"""
db/mongo.py
-----------
All MongoDB operations for VYNERA AI.
Collections: users, conversations, memories, feedback, goals, journals
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from config import settings

logger = logging.getLogger(__name__)

# ─── Client singleton ─────────────────────────────────────────────────────────

_client: Optional[AsyncIOMotorClient] = None
_db: Optional[AsyncIOMotorDatabase] = None


def get_db() -> AsyncIOMotorDatabase:
    return _db


async def connect_db() -> None:
    global _client, _db
    _client = AsyncIOMotorClient(settings.mongo_uri)
    _db = _client[settings.mongo_db_name]
    # Create indexes
    await _db.users.create_index("email", unique=True)
    await _db.users.create_index("username", unique=True)
    await _db.conversations.create_index("user_id")
    await _db.memories.create_index("user_id")
    await _db.feedback.create_index("user_id")
    await _db.goals.create_index("user_id")
    await _db.journals.create_index("user_id")
    logger.info("MongoDB connected and indexes created.")


async def close_db() -> None:
    if _client:
        _client.close()


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _serialize(doc: dict) -> dict:
    """Convert ObjectId to string for JSON serialisation."""
    if doc is None:
        return {}
    out = {}
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            out[k] = str(v)
        elif isinstance(v, list):
            out[k] = [_serialize(i) if isinstance(i, dict) else (str(i) if isinstance(i, ObjectId) else i) for i in v]
        elif isinstance(v, dict):
            out[k] = _serialize(v)
        else:
            out[k] = v
    return out


# ─── USERS ────────────────────────────────────────────────────────────────────

async def create_user(data: dict) -> str:
    data["created_at"] = _now()
    result = await _db.users.insert_one(data)
    return str(result.inserted_id)


async def get_user_by_email(email: str) -> Optional[dict]:
    doc = await _db.users.find_one({"email": email.lower()})
    return _serialize(doc) if doc else None


async def get_user_by_username(username: str) -> Optional[dict]:
    doc = await _db.users.find_one({"username": username.lower()})
    return _serialize(doc) if doc else None


async def get_user_by_id(user_id: str) -> Optional[dict]:
    doc = await _db.users.find_one({"_id": ObjectId(user_id)})
    return _serialize(doc) if doc else None


async def get_user_by_identifier(identifier: str) -> Optional[dict]:
    """Accept either email or username."""
    doc = await _db.users.find_one({
        "$or": [
            {"email": identifier.lower()},
            {"username": identifier.lower()}
        ]
    })
    return _serialize(doc) if doc else None


async def update_user(user_id: str, data: dict) -> bool:
    data["updated_at"] = _now()
    result = await _db.users.update_one(
        {"_id": ObjectId(user_id)}, {"$set": data}
    )
    return result.modified_count > 0


async def delete_user_data(user_id: str) -> None:
    """Permanently delete all data for a user."""
    oid = ObjectId(user_id)
    uid = user_id
    await _db.users.delete_one({"_id": oid})
    for col in ("conversations", "memories", "feedback", "goals", "journals"):
        await _db[col].delete_many({"user_id": uid})


# ─── CONVERSATIONS ────────────────────────────────────────────────────────────

async def create_conversation(user_id: str, title: str = "New Conversation") -> str:
    doc = {
        "user_id": user_id,
        "title": title,
        "topic": None,
        "messages": [],
        "mood_scores": [],
        "support_flow": None,   # {"topic": "breakup", "step": 0} when in a structured flow
        "created_at": _now(),
        "updated_at": _now(),
    }
    result = await _db.conversations.insert_one(doc)
    return str(result.inserted_id)


async def get_conversation(conv_id: str) -> Optional[dict]:
    doc = await _db.conversations.find_one({"_id": ObjectId(conv_id)})
    return _serialize(doc) if doc else None


async def set_support_flow(conv_id: str, flow: Optional[dict]) -> None:
    """Set or clear the active structured-support-flow state for a conversation."""
    await _db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"support_flow": flow, "updated_at": _now()}}
    )


async def get_user_conversations(user_id: str, search: str = "", limit: int = 200) -> list[dict]:
    query: dict[str, Any] = {"user_id": user_id}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"topic": {"$regex": search, "$options": "i"}},
        ]
    cursor = _db.conversations.find(query).sort("updated_at", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize(d) for d in docs]


async def append_message(conv_id: str, message: dict, mood_score: Optional[float] = None) -> None:
    message["timestamp"] = _now()
    update: dict[str, Any] = {
        "$push": {"messages": message},
        "$set": {"updated_at": _now()},
    }
    if mood_score is not None:
        update["$push"]["mood_scores"] = mood_score  # type: ignore[index]
    await _db.conversations.update_one({"_id": ObjectId(conv_id)}, update)


async def set_conversation_title(conv_id: str, title: str) -> None:
    await _db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"title": title, "updated_at": _now()}}
    )


async def set_conversation_topic(conv_id: str, topic: str) -> None:
    await _db.conversations.update_one(
        {"_id": ObjectId(conv_id)},
        {"$set": {"topic": topic, "updated_at": _now()}}
    )


async def get_recent_mood_scores(user_id: str, n: int = 14) -> list[dict]:
    """Return mood_scores + created_at from last n conversations."""
    cursor = _db.conversations.find(
        {"user_id": user_id, "mood_scores": {"$exists": True, "$ne": []}},
        {"mood_scores": 1, "created_at": 1}
    ).sort("created_at", -1).limit(n)
    docs = await cursor.to_list(length=n)
    return [_serialize(d) for d in reversed(docs)]


# ─── MEMORIES ─────────────────────────────────────────────────────────────────

async def upsert_memory(user_id: str, key: str, value: str) -> None:
    await _db.memories.update_one(
        {"user_id": user_id, "key": key},
        {"$set": {"value": value, "updated_at": _now()}, "$setOnInsert": {"created_at": _now()}},
        upsert=True,
    )


async def get_all_memories(user_id: str) -> list[dict]:
    cursor = _db.memories.find({"user_id": user_id}).sort("updated_at", -1)
    docs = await cursor.to_list(length=500)
    return [_serialize(d) for d in docs]


async def get_recent_memories(user_id: str, n: int = 5) -> list[dict]:
    cursor = _db.memories.find({"user_id": user_id}).sort("updated_at", -1).limit(n)
    docs = await cursor.to_list(length=n)
    return [_serialize(d) for d in docs]


async def delete_memory(user_id: str, memory_id: str) -> bool:
    result = await _db.memories.delete_one({"_id": ObjectId(memory_id), "user_id": user_id})
    return result.deleted_count > 0


# ─── FEEDBACK ─────────────────────────────────────────────────────────────────

async def save_feedback(user_id: str, conv_id: str, user_msg: str, bot_msg: str, rating: int) -> None:
    """rating: 1 = thumbs up, -1 = thumbs down"""
    doc = {
        "user_id": user_id,
        "conv_id": conv_id,
        "user_message": user_msg,
        "bot_response": bot_msg,
        "rating": rating,
        "processed": False,
        "created_at": _now(),
    }
    await _db.feedback.insert_one(doc)


async def get_unprocessed_positive_feedback(limit: int = 500) -> list[dict]:
    cursor = _db.feedback.find({"rating": 1, "processed": False}).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize(d) for d in docs]


async def count_unprocessed_feedback() -> int:
    return await _db.feedback.count_documents({"processed": False})


async def mark_feedback_processed(ids: list[str]) -> None:
    oids = [ObjectId(i) for i in ids]
    await _db.feedback.update_many({"_id": {"$in": oids}}, {"$set": {"processed": True}})


# ─── GOALS ────────────────────────────────────────────────────────────────────

async def create_goal(user_id: str, title: str, steps: list[str], deadline: Optional[str] = None) -> str:
    doc = {
        "user_id": user_id,
        "title": title,
        "steps": [{"text": s, "done": False} for s in steps],
        "progress": 0,
        "status": "active",
        "deadline": deadline,
        "created_at": _now(),
        "updated_at": _now(),
    }
    result = await _db.goals.insert_one(doc)
    return str(result.inserted_id)


async def get_user_goals(user_id: str, status: Optional[str] = None) -> list[dict]:
    query: dict[str, Any] = {"user_id": user_id}
    if status:
        query["status"] = status
    cursor = _db.goals.find(query).sort("created_at", -1)
    docs = await cursor.to_list(length=200)
    return [_serialize(d) for d in docs]


async def update_goal_step(user_id: str, goal_id: str, step_index: int, done: bool) -> Optional[dict]:
    goal = await _db.goals.find_one({"_id": ObjectId(goal_id), "user_id": user_id})
    if not goal:
        return None
    steps = goal.get("steps", [])
    if 0 <= step_index < len(steps):
        steps[step_index]["done"] = done
    total = len(steps)
    completed = sum(1 for s in steps if s.get("done"))
    progress = int((completed / total) * 100) if total > 0 else 0
    status = "completed" if progress == 100 else "active"
    await _db.goals.update_one(
        {"_id": ObjectId(goal_id)},
        {"$set": {"steps": steps, "progress": progress, "status": status, "updated_at": _now()}}
    )
    return _serialize({**goal, "steps": steps, "progress": progress, "status": status})


async def delete_goal(user_id: str, goal_id: str) -> bool:
    result = await _db.goals.delete_one({"_id": ObjectId(goal_id), "user_id": user_id})
    return result.deleted_count > 0


# ─── JOURNALS ─────────────────────────────────────────────────────────────────

async def save_journal(user_id: str, content: str, emotion: str, intensity: float, patterns: list[str]) -> str:
    doc = {
        "user_id": user_id,
        "content": content,
        "emotion": emotion,
        "intensity": intensity,
        "patterns": patterns,
        "created_at": _now(),
    }
    result = await _db.journals.insert_one(doc)
    return str(result.inserted_id)


async def get_user_journals(user_id: str, limit: int = 100) -> list[dict]:
    cursor = _db.journals.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_serialize(d) for d in docs]


# ─── EXPORT ───────────────────────────────────────────────────────────────────

async def export_all_user_data(user_id: str) -> dict:
    user = await get_user_by_id(user_id)
    if user:
        user.pop("hashed_password", None)
    conversations = await get_user_conversations(user_id, limit=10000)
    memories = await get_all_memories(user_id)
    goals = await get_user_goals(user_id)
    journals = await get_user_journals(user_id, limit=10000)
    return {
        "profile": user,
        "conversations": conversations,
        "memories": memories,
        "goals": goals,
        "journals": journals,
        "exported_at": _now().isoformat(),
    }