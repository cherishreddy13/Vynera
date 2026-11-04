from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import (
    Depends, FastAPI, HTTPException, Query,
    WebSocket, WebSocketDisconnect, status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from config import settings
from db.mongo import (
    connect_db, close_db,
    create_user, get_user_by_identifier, get_user_by_email,
    get_user_by_username, get_user_by_id, update_user, delete_user_data,
    create_conversation, get_conversation, get_user_conversations,
    append_message, set_conversation_title, set_conversation_topic,
    get_recent_mood_scores,
    upsert_memory, get_all_memories, get_recent_memories, delete_memory,
    save_feedback,
    create_goal, get_user_goals, update_goal_step, delete_goal,
    save_journal, get_user_journals,
    export_all_user_data,
)
from model.core import (
    load_model, generate_response, build_system_prompt, is_model_loaded,
    is_summary_request, build_summary_response,
)
from model.support_flow import (
    detect_topic, get_flow_response, wants_to_continue_topic, wants_to_exit_topic,
    check_direct_request,
)
from db.mongo import set_support_flow
from model.self_learn import run_nightly_learning
from utils.sentiment import detect_emotion, emotion_to_dict
from utils.memory import extract_facts, format_memory_for_prompt
from utils.safety import check_input, validate_response, is_incoherent

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ─── Scheduler ────────────────────────────────────────────────────────────────

scheduler = AsyncIOScheduler()

# ─── Lifespan (replaces deprecated on_event) ──────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    try:
        load_model()
    except Exception as exc:
        logger.warning("Model load failed (server still runs): %s", exc)
    scheduler.add_job(
        run_nightly_learning,
        "cron",
        hour=settings.self_learn_hour,
        minute=0,
        id="nightly_learn",
    )
    scheduler.start()
    logger.info("VYNERA AI started. Model loaded: %s", is_model_loaded())
    yield
    scheduler.shutdown(wait=False)
    await close_db()

# ─── App init ─────────────────────────────────────────────────────────────────

app = FastAPI(title="VYNERA AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Mount static files only if the directory exists (prevents startup crash)
import os as _os
if _os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Auth helpers ─────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_jwt(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.jwt_expire_days)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_jwt(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")


async def get_current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token.")
    token = auth[7:]
    user_id = decode_jwt(token)
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")
    return user


async def get_user_from_ws_token(token: str) -> Optional[dict]:
    try:
        user_id = decode_jwt(token)
        return await get_user_by_id(user_id)
    except Exception:
        return None


# ─── Pydantic models ──────────────────────────────────────────────────────────

class SignupRequest(BaseModel):
    name: str
    age: int
    email: str
    username: str
    password: str
    parent_phone: Optional[str] = None
    questionnaire: Optional[dict] = None
    personality: str = "encouraging"


class LoginRequest(BaseModel):
    identifier: str   # email or username
    password: str


class ProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    email: Optional[str] = None
    username: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class PersonalityRequest(BaseModel):
    personality: str


class FeedbackRequest(BaseModel):
    conv_id: str
    user_message: str
    bot_response: str
    rating: int   # 1 or -1


class GoalCreateRequest(BaseModel):
    title: str
    steps: list[str]
    deadline: Optional[str] = None


# ─── AUTH ROUTES ──────────────────────────────────────────────────────────────

@app.post("/api/auth/signup")
async def signup(body: SignupRequest):
    # Check uniqueness
    if await get_user_by_email(body.email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    if await get_user_by_username(body.username):
        raise HTTPException(status_code=400, detail="Username already taken.")

    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")

    if body.age < 18 and not body.parent_phone:
        raise HTTPException(status_code=400, detail="Parent or guardian phone required for users under 18.")

    user_data = {
        "name": body.name.strip(),
        "age": body.age,
        "email": body.email.lower().strip(),
        "username": body.username.lower().strip(),
        "hashed_password": hash_password(body.password),
        "personality": body.personality,
        "questionnaire": body.questionnaire or {},
        "parent_phone": body.parent_phone,
    }

    user_id = await create_user(user_data)
    token = create_jwt(user_id)
    user = await get_user_by_id(user_id)
    user.pop("hashed_password", None)
    return {"token": token, "user": user}


@app.post("/api/auth/login")
async def login(body: LoginRequest):
    user = await get_user_by_identifier(body.identifier)
    if not user or not verify_password(body.password, user.get("hashed_password", "")):
        raise HTTPException(status_code=401, detail="Invalid credentials.")
    token = create_jwt(user["_id"])
    user.pop("hashed_password", None)
    return {"token": token, "user": user}


@app.get("/api/auth/me")
@app.get("/api/me")   # alias kept for compatibility
async def me(current_user: dict = Depends(get_current_user)):
    current_user.pop("hashed_password", None)
    return current_user


# ─── USER ROUTES ──────────────────────────────────────────────────────────────

@app.put("/api/user/profile")
async def update_profile(body: ProfileUpdateRequest, current_user: dict = Depends(get_current_user)):
    update_data: dict = {}
    if body.name is not None:
        update_data["name"] = body.name.strip()
    if body.age is not None:
        update_data["age"] = body.age
    if body.email is not None:
        existing = await get_user_by_email(body.email)
        if existing and existing["_id"] != current_user["_id"]:
            raise HTTPException(status_code=400, detail="Email already in use.")
        update_data["email"] = body.email.lower().strip()
    if body.username is not None:
        existing = await get_user_by_username(body.username)
        if existing and existing["_id"] != current_user["_id"]:
            raise HTTPException(status_code=400, detail="Username already taken.")
        update_data["username"] = body.username.lower().strip()

    if update_data:
        await update_user(current_user["_id"], update_data)
    return {"message": "Profile updated."}


@app.put("/api/user/password")
async def change_password(body: PasswordChangeRequest, current_user: dict = Depends(get_current_user)):
    user = await get_user_by_id(current_user["_id"])
    if not verify_password(body.current_password, user.get("hashed_password", "")):
        raise HTTPException(status_code=400, detail="Current password is incorrect.")
    if len(body.new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters.")
    await update_user(current_user["_id"], {"hashed_password": hash_password(body.new_password)})
    return {"message": "Password updated."}


@app.put("/api/user/personality")
async def update_personality(body: PersonalityRequest, current_user: dict = Depends(get_current_user)):
    valid = {"encouraging", "analytical", "playful", "wise"}
    if body.personality.lower() not in valid:
        raise HTTPException(status_code=400, detail=f"Personality must be one of: {', '.join(valid)}")
    await update_user(current_user["_id"], {"personality": body.personality.lower()})
    return {"message": "Personality updated."}


@app.delete("/api/user/account")
async def delete_account(current_user: dict = Depends(get_current_user)):
    await delete_user_data(current_user["_id"])
    return {"message": "Account permanently deleted."}


# ─── CONVERSATION ROUTES ──────────────────────────────────────────────────────

@app.get("/api/conversations")
async def list_conversations(
    search: str = Query(""),
    current_user: dict = Depends(get_current_user)
):
    convs = await get_user_conversations(current_user["_id"], search=search)
    return convs


@app.post("/api/conversations")
async def new_conversation(current_user: dict = Depends(get_current_user)):
    conv_id = await create_conversation(current_user["_id"])
    return {"conv_id": conv_id}


@app.get("/api/conversations/{conv_id}")
async def get_conv(conv_id: str, current_user: dict = Depends(get_current_user)):
    conv = await get_conversation(conv_id)
    if not conv or conv["user_id"] != current_user["_id"]:
        raise HTTPException(status_code=404, detail="Conversation not found.")
    return conv


# ─── MEMORY ROUTES ────────────────────────────────────────────────────────────

@app.get("/api/memories")
async def list_memories(current_user: dict = Depends(get_current_user)):
    return await get_all_memories(current_user["_id"])


@app.delete("/api/memories/{memory_id}")
async def remove_memory(memory_id: str, current_user: dict = Depends(get_current_user)):
    deleted = await delete_memory(current_user["_id"], memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found.")
    return {"message": "Memory deleted."}


# ─── FEEDBACK ROUTE ───────────────────────────────────────────────────────────

@app.post("/api/feedback")
async def submit_feedback(body: FeedbackRequest, current_user: dict = Depends(get_current_user)):
    if body.rating not in (1, -1):
        raise HTTPException(status_code=400, detail="Rating must be 1 or -1.")
    await save_feedback(
        user_id=current_user["_id"],
        conv_id=body.conv_id,
        user_msg=body.user_message,
        bot_msg=body.bot_response,
        rating=body.rating,
    )
    return {"message": "Feedback recorded."}


# ─── GOAL ROUTES ──────────────────────────────────────────────────────────────

@app.get("/api/goals")
async def list_goals(
    status: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    return await get_user_goals(current_user["_id"], status=status)


@app.post("/api/goals")
async def create_new_goal(body: GoalCreateRequest, current_user: dict = Depends(get_current_user)):
    if not body.steps:
        raise HTTPException(status_code=400, detail="At least one step is required.")
    goal_id = await create_goal(current_user["_id"], body.title, body.steps, body.deadline)
    return {"goal_id": goal_id, "message": "Goal created."}


@app.put("/api/goals/{goal_id}/step/{step_index}")
async def toggle_goal_step(
    goal_id: str, step_index: int,
    done: bool = Query(...),
    current_user: dict = Depends(get_current_user)
):
    result = await update_goal_step(current_user["_id"], goal_id, step_index, done)
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return result


@app.delete("/api/goals/{goal_id}")
async def remove_goal(goal_id: str, current_user: dict = Depends(get_current_user)):
    deleted = await delete_goal(current_user["_id"], goal_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Goal not found.")
    return {"message": "Goal deleted."}


# ─── JOURNAL ROUTES ───────────────────────────────────────────────────────────

@app.get("/api/journals")
async def list_journals(current_user: dict = Depends(get_current_user)):
    return await get_user_journals(current_user["_id"])


# ─── DASHBOARD ROUTES ─────────────────────────────────────────────────────────

@app.get("/api/dashboard/stats")
async def dashboard_stats(current_user: dict = Depends(get_current_user)):
    uid = current_user["_id"]
    convs = await get_user_conversations(uid, limit=10000)
    goals = await get_user_goals(uid)
    memories = await get_all_memories(uid)
    active_goals = [g for g in goals if g.get("status") == "active"]
    completed_goals = [g for g in goals if g.get("status") == "completed"]
    return {
        "chat_sessions": len(convs),
        "active_goals": len(active_goals),
        "completed_goals": len(completed_goals),
        "facts_remembered": len(memories),
    }


@app.get("/api/dashboard/mood")
async def dashboard_mood(current_user: dict = Depends(get_current_user)):
    mood_data = await get_recent_mood_scores(current_user["_id"], n=14)
    return mood_data


# ─── EXPORT ROUTE ─────────────────────────────────────────────────────────────

@app.get("/api/export")
async def export_data(current_user: dict = Depends(get_current_user)):
    data = await export_all_user_data(current_user["_id"])
    json_str = json.dumps(data, indent=2, default=str)

    def iter_content():
        yield json_str

    return StreamingResponse(
        iter_content(),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="vynera_export_{current_user["_id"]}.json"'}
    )


# ─── WEBSOCKET — MAIN CHAT ────────────────────────────────────────────────────

@app.websocket("/ws/chat/{conv_id}")
async def websocket_chat(websocket: WebSocket, conv_id: str, token: str = Query(...)):
    await websocket.accept()

    # Authenticate
    user = await get_user_from_ws_token(token)
    if not user:
        await websocket.send_json({"type": "error", "message": "Authentication failed."})
        await websocket.close(code=4001)
        return

    # Verify conversation belongs to user
    conv = await get_conversation(conv_id)
    if not conv or conv["user_id"] != user["_id"]:
        await websocket.send_json({"type": "error", "message": "Conversation not found."})
        await websocket.close(code=4004)
        return

    user_id = user["_id"]
    personality = user.get("personality", "encouraging")
    user_name = user.get("name", "")

    logger.info("WS connected: user=%s conv=%s", user_id, conv_id)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            user_message = data.get("message", "").strip()
            mode = data.get("mode", "chat")   # chat | journal | goals | reason

            if not user_message:
                continue

            # 1. Safety check
            safety = check_input(user_message)
            if safety.blocked:
                await websocket.send_json({
                    "type": "response",
                    "message": safety.override_response,
                    "emotion": {"emotion": "sadness" if safety.is_crisis else "neutral",
                                "intensity": 0.9, "valence": -0.8, "label": "strongly"},
                    "is_crisis": safety.is_crisis,
                    "is_medical": safety.is_medical,
                })
                # Still store the exchange
                await append_message(conv_id, {"role": "user", "content": user_message})
                await append_message(conv_id, {"role": "assistant", "content": safety.override_response})
                continue

            # 2. Emotion detection
            emotion_result = detect_emotion(user_message)
            emotion_dict = emotion_to_dict(emotion_result)

            # 3. Memory extraction
            facts = extract_facts(user_message)
            for fact in facts:
                await upsert_memory(user_id, fact.key, fact.value)

            memories = await get_recent_memories(user_id, n=10)
            memory_string = format_memory_for_prompt(memories)

            # 4. Build conversation history from DB
            fresh_conv = await get_conversation(conv_id)
            history = fresh_conv.get("messages", [])[-20:]  # last 20 turns
            # Append current user message to history for generation
            history.append({"role": "user", "content": user_message})

            # 5. Build system prompt
            system_prompt = build_system_prompt(
                personality=personality,
                emotion=emotion_result.emotion,
                mode=mode,
                memory_string=memory_string,
                user_name=user_name,
            )

            # 6. Send typing indicator
            await websocket.send_json({"type": "typing", "value": True})

            # 7. Generate response
            # Summary requests ("what have I told you", "summarize this") are answered
            # directly from stored memories/topics — DialoGPT cannot reliably summarize.
            active_flow = fresh_conv.get("support_flow")

            # Direct requests ("give me motivation", "i need your help",
            # "i don't have a plan") are answered by VYNERA itself — checked
            # with high priority so DialoGPT never gets the chance to deflect
            # to "talk to a friend / therapist / counselor" instead.
            direct_response = check_direct_request(user_message)

            if is_summary_request(user_message):
                all_memories = await get_all_memories(user_id)
                recent_convs = await get_user_conversations(user_id, limit=10)
                recent_topics = [c.get("topic") for c in recent_convs if c.get("topic")]
                bot_response = build_summary_response(all_memories, recent_topics)
                # Summary doesn't change the active flow state — leave it as-is

            elif direct_response:
                bot_response = direct_response
                # Direct requests don't advance/clear the active flow —
                # the user can return to it afterwards

            elif active_flow:
                # ── Continue or exit an active structured support flow ──
                topic = active_flow.get("topic")
                step  = active_flow.get("step", 0)

                if wants_to_exit_topic(user_message):
                    # User wants to move on — clear flow and fall through to
                    # normal generation for this turn
                    await set_support_flow(conv_id, None)
                    bot_response = generate_response(history, system_prompt)
                elif wants_to_continue_topic(user_message):
                    # Advance to the next step in the flow
                    next_step = step + 1
                    bot_response, is_final = get_flow_response(topic, next_step)
                    if is_final:
                        await set_support_flow(conv_id, None)
                    else:
                        await set_support_flow(conv_id, {"topic": topic, "step": next_step})
                else:
                    # Ambiguous — treat as continuing but don't advance the step,
                    # so the same depth of response is offered again differently
                    bot_response, is_final = get_flow_response(topic, step)
                    if is_final:
                        await set_support_flow(conv_id, None)

            else:
                # ── No active flow — check if this message starts a new one ──
                new_topic = detect_topic(user_message)
                if new_topic:
                    bot_response, is_final = get_flow_response(new_topic, 0)
                    if not is_final:
                        await set_support_flow(conv_id, {"topic": new_topic, "step": 0})
                else:
                    bot_response = generate_response(history, system_prompt)

            # 8. Validate response
            if is_incoherent(bot_response):
                from model.core import _get_fallback
                bot_response = _get_fallback(user_message, emotion_result.emotion)
            else:
                bot_response = validate_response(bot_response)

            # 9. Store messages
            await append_message(conv_id,
                                  {"role": "user", "content": user_message},
                                  mood_score=emotion_result.valence)
            await append_message(conv_id,
                                  {"role": "assistant", "content": bot_response})

            # 10. Journal mode: detect patterns + save journal entry
            journal_patterns: list[str] = []
            if mode == "journal":
                journal_patterns = _detect_cognitive_patterns(user_message)
                await save_journal(
                    user_id=user_id,
                    content=user_message,
                    emotion=emotion_result.emotion,
                    intensity=emotion_result.intensity,
                    patterns=journal_patterns,
                )

            # 11. Goals mode: auto-detect goal creation language
            if mode == "goals":
                await _try_extract_goal(user_id, user_message)

            # 12. Auto-title conversation after first user message
            if len(fresh_conv.get("messages", [])) == 0:
                title = user_message[:50] + ("…" if len(user_message) > 50 else "")
                await set_conversation_title(conv_id, title)
                await set_conversation_topic(conv_id, emotion_result.emotion)

            # 13. Send response
            await websocket.send_json({
                "type": "response",
                "message": bot_response,
                "emotion": emotion_dict,
                "journal_patterns": journal_patterns,
                "new_memories": [{"key": f.key, "value": f.value} for f in facts],
            })

    except WebSocketDisconnect:
        logger.info("WS disconnected: user=%s conv=%s", user_id, conv_id)
    except Exception as exc:
        logger.error("WS error: %s", exc)
        try:
            await websocket.send_json({"type": "error", "message": "An internal error occurred."})
        except Exception:
            pass


# ─── Cognitive pattern detection (journal mode) ───────────────────────────────

_PATTERN_REGEXES = {
    "absolute_thinking": [
        r"\b(always|never|everyone|nobody|nothing|everything|all|completely|totally)\b",
    ],
    "catastrophising": [
        r"\b(disaster|catastrophe|terrible|awful|horrible|worst|ruined|destroyed)\b",
    ],
    "self_blame": [
        r"\b(my fault|i failed|i ruined|blame myself|i'm the problem|i caused)\b",
    ],
    "should_statements": [
        r"\b(should|shouldn't|must|mustn't|have to|ought to|need to)\b",
    ],
}

import re as _re

def _detect_cognitive_patterns(text: str) -> list[str]:
    text_lower = text.lower()
    detected = []
    for pattern_name, regexes in _PATTERN_REGEXES.items():
        for regex in regexes:
            if _re.search(regex, text_lower):
                detected.append(pattern_name)
                break
    return detected


# ─── Goal extraction from natural language ────────────────────────────────────

_GOAL_TRIGGER = _re.compile(
    r"\b(i want to|i need to|my goal is|i plan to|i(?:'m| am) going to|i will|i'd like to)\s+(.{5,80})",
    _re.I,
)

async def _try_extract_goal(user_id: str, text: str) -> None:
    match = _GOAL_TRIGGER.search(text)
    if match:
        goal_title = match.group(2).strip().rstrip(".,!?")
        await create_goal(
            user_id=user_id,
            title=goal_title[:100],
            steps=["Define first step", "Work toward it", "Reflect and adjust"],
        )


# ─── LOGOUT ROUTE ────────────────────────────────────────────────────────────

@app.get("/api/auth/logout")
async def logout():
    # JWT is stateless — client deletes the token. This endpoint exists for convenience.
    return {"message": "Logged out. Delete your token client-side."}


# ─── HTML PAGE ROUTES ─────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    return templates.TemplateResponse("profile.html", {"request": request})


@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level="info",
    )