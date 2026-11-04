"""
prepare_data.py
---------------
VYNERA AI — Local Dataset Preparation Script.

Reads ALL datasets from your local files (no internet needed).
Run this on your laptop, then upload data/train.jsonl + data/val.jsonl to Kaggle.

YOUR FOLDER STRUCTURE (from screenshot):
  data/
  ├── counsel/train.json
  ├── dailydialog/train/dialogues.json  (+ train.json, validation.json)
  ├── Emotional-Support-Conversation-main/ESConv.json
  ├── EmpatheticDialogues/train.json  (+ train.csv, validation.json, test.json)
  ├── mental_health_chat_dataset/train/data-00000-of-00001.arrow
  └── train.jsonl / val.jsonl  (output — written here)

HOW TO USE:
  1. Set DATA_ROOT below to the full path of your data/ folder
  2. Run:  python prepare_data.py
  3. Upload data/train.jsonl and data/val.jsonl to Kaggle
"""

from __future__ import annotations

import csv
import json
import re
import logging
import random
import struct
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# 👇  SET THIS to the path of your data/ folder
# ─────────────────────────────────────────────────────────────────────────────
DATA_ROOT = Path("./data")

# Windows example:
# DATA_ROOT = Path(r"D:\myprojects\Companion\VYNERA AI\data")
# ─────────────────────────────────────────────────────────────────────────────

OUTPUT_FILE = DATA_ROOT / "train.jsonl"
VAL_FILE    = DATA_ROOT / "val.jsonl"


# ── Helpers ───────────────────────────────────────────────────────────────────

# ── Topic filter — reject service/task/hospitality conversations ────────────────
# VYNERA is an emotional companion. It has no business learning from hotel
# check-in dialogues, customer service calls, restaurant orders, ticket
# bookings, or flight reservations. These pairs dilute the model's emotional
# intelligence and introduce irrelevant vocabulary.

_SERVICE_PATTERNS = re.compile(
    r"(minibar|check.?in|check.?out|reservation|booking|checkout|hotel|"
    r"front desk|room service|housekeeping|concierge|receptionist|"
    r"ticket|flight|airline|boarding pass|passport|visa|luggage|baggage|"
    r"restaurant|menu|waiter|waitress|order|dish|cuisine|chef|"
    r"promotion|discount|package|deal|offer|subscription|membership|"
    r"refund|invoice|payment|billing|charge|credit card|"
    r"delivery|shipment|tracking|parcel|courier|"
    r"sir|ma.?am|madam)",
    re.I,
)

_EMOTIONAL_SIGNALS = re.compile(
    r"(feel|feeling|felt|sad|happy|anxious|worried|lonely|miss|"
    r"angry|upset|hurt|depressed|excited|scared|nervous|tired|"
    r"stressed|overwhelmed|lost|confused|hopeful|love|hate|"
    r"friend|family|relationship|breakup|boyfriend|girlfriend|"
    r"myself|yourself|i am|i'm|you are|you're|we can|let me|"
    r"hey|yeah|ugh|honestly|lol|omg|okay|alright|sorry|thank)",
    re.I,
)


def is_service_dialogue(inp: str, out: str) -> bool:
    """
    Return True only if the pair is clearly service/task-oriented dialogue.
    We are intentionally permissive here — it is better to keep a borderline
    pair than to accidentally discard all valid emotional pairs.
    A pair is rejected ONLY if it contains explicit service keywords.
    """
    combined = inp + " " + out
    # Hard reject: explicit service/hospitality vocabulary
    if _SERVICE_PATTERNS.search(combined):
        return True
    # Hard reject: looks like a very short transactional exchange with no
    # personal pronoun or emotional word at all (e.g. "Keep the change!" / "Thanks.")
    # Only applies to very short pairs to avoid over-filtering
    combined_lower = combined.lower()
    has_personal = any(w in combined_lower for w in (
        "i ", "i'm", "i've", "i'd", "i'll", "you ", "your ", "we ", "my ",
        "me ", "feel", "felt", "sad", "happy", "help", "need", "want", "sorry",
        "thank", "okay", "yeah", "hi", "hey", "hello",
    ))
    if not has_personal and len(combined) < 120:
        return True
    return False


def clean_pair(p: dict) -> dict | None:
    inp = str(p.get("input",  "") or "").strip()
    out = str(p.get("output", "") or "").strip()
    if not inp or not out:
        return None
    if len(inp) < 5 or len(out) < 10:
        return None
    if len(inp) > 2000 or len(out) > 2000:
        return None
    # Safety net: reject pairs where a loader bug stringified a dict/list
    if inp.startswith(("{", "[")) or out.startswith(("{", "[")):
        return None
    if "'utterance'" in inp or "'utterance'" in out or "'speaker'" in inp or "'speaker'" in out:
        return None
    # Reject service/hospitality/task-oriented dialogue
    if is_service_dialogue(inp, out):
        return None
    return {"input": inp, "output": out}


def load_json_file(path: Path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def load_jsonl_file(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    return rows


def load_csv_file(path: Path) -> list[dict]:
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


# ── 1. EmpatheticDialogues — local JSON/CSV ───────────────────────────────────

def load_empathetic_dialogues() -> list[dict]:
    """
    Reads from:
      data/EmpatheticDialogues/train.json  (+ validation.json, test.json)

    ACTUAL format (confirmed from debug):
      Each row is one utterance with keys:
        context   — emotion label (e.g. "sentimental")
        utterance — the RESPONSE (bot turn)
        emotion   — often empty string
        prompt    — the USER message that prompted this response

    So each row is directly one pair:
        input  = prompt    (what the user said)
        output = utterance (what the empathetic responder said)
    """
    base = DATA_ROOT / "EmpatheticDialogues"
    if not base.exists():
        logger.warning("  ❌ EmpatheticDialogues folder not found: %s", base)
        return []

    all_rows: list[dict] = []

    # Load JSON splits
    for fname in ("train.json", "validation.json", "test.json"):
        fp = base / fname
        if fp.exists():
            try:
                raw = load_json_file(fp)
                if isinstance(raw, list):
                    all_rows.extend(raw)
                    logger.info("    Loaded %d rows from %s", len(raw), fp.name)
            except Exception as exc:
                logger.warning("    Could not load %s: %s", fp.name, exc)

    # Fallback to CSV
    if not all_rows:
        for fname in ("train.csv", "validation.csv", "test.csv"):
            fp = base / fname
            if fp.exists():
                try:
                    rows = load_csv_file(fp)
                    all_rows.extend(rows)
                    logger.info("    Loaded %d rows from %s (csv)", len(rows), fp.name)
                except Exception as exc:
                    logger.warning("    Could not load %s: %s", fp.name, exc)

    if not all_rows:
        logger.warning("  ❌ EmpatheticDialogues: no data found in %s", base)
        return []

    pairs = []
    for row in all_rows:
        if not isinstance(row, dict):
            continue
        # prompt = user turn, utterance = empathetic response
        user_msg = str(row.get("prompt") or "").replace("_comma_", ",").strip()
        bot_msg  = str(row.get("utterance") or "").replace("_comma_", ",").strip()

        if user_msg and bot_msg and len(user_msg) > 5 and len(bot_msg) > 10:
            pairs.append({"input": user_msg, "output": bot_msg})

    logger.info("  ✅ EmpatheticDialogues (local): %d pairs", len(pairs))
    return pairs


# ── 2. Counsel_Chat — local JSON ─────────────────────────────────────────────

def load_counsel_chat() -> list[dict]:
    """
    Reads from:
      data/counsel/train.json

    Tries multiple field name patterns:
      questionText / answerText
      question / answer
      input / output
      prompt / completion
    """
    fp = DATA_ROOT / "counsel" / "train.json"
    if not fp.exists():
        # also try top-level
        fp2 = DATA_ROOT / "counsel.json"
        if fp2.exists():
            fp = fp2
        else:
            logger.warning("  ❌ Counsel_Chat not found: %s", fp)
            return []

    try:
        raw = load_json_file(fp)
        rows = raw if isinstance(raw, list) else []

        FIELD_PAIRS = [
            ("questionText", "answerText"),
            ("question",     "answer"),
            ("input",        "output"),
            ("prompt",       "completion"),
            ("human",        "assistant"),
        ]

        pairs = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            q, a = "", ""
            for qk, ak in FIELD_PAIRS:
                q = str(row.get(qk) or "").strip()
                a = str(row.get(ak) or "").strip()
                if q and a:
                    break
            if q and a and len(q) > 10 and len(a) > 20:
                pairs.append({"input": q, "output": a})

        logger.info("  ✅ Counsel_Chat (local): %d pairs", len(pairs))
        return pairs
    except Exception as exc:
        logger.warning("  ❌ Counsel_Chat failed: %s", exc)
        return []


# ── 3. ESConv — local ESConv.json ─────────────────────────────────────────────

def load_esconv() -> list[dict]:
    """
    Reads from:
      data/Emotional-Support-Conversation-main/ESConv.json

    ESConv.json format — a list of conversation objects:
    [
      {
        "dialog": [
          {"speaker": "usr", "text": "I feel..."},
          {"speaker": "sys", "text": "I hear you..."},
          ...
        ]
      },
      ...
    ]
    """
    candidates = [
        DATA_ROOT / "Emotional-Support-Conversation-main" / "ESConv.json",
        DATA_ROOT / "Emotional-Support-Conversation-main" / "FailedESConv.json",
        DATA_ROOT / "ESConv.json",
    ]

    fp = None
    for c in candidates:
        if c.exists():
            fp = c
            break

    if fp is None:
        logger.warning("  ❌ ESConv.json not found in %s", DATA_ROOT / "Emotional-Support-Conversation-main")
        return []

    try:
        raw = load_json_file(fp)

        # ESConv.json can be a list OR a dict with a key like "train"
        if isinstance(raw, dict):
            conversations = []
            for v in raw.values():
                if isinstance(v, list):
                    conversations.extend(v)
        elif isinstance(raw, list):
            conversations = raw
        else:
            logger.warning("  ❌ ESConv.json unexpected format: %s", type(raw))
            return []

        pairs = []
        for conv in conversations:
            if not isinstance(conv, dict):
                continue

            dialog = conv.get("dialog", conv.get("dialogue", []))

            # dialog might itself be a JSON string
            if isinstance(dialog, str):
                try:
                    dialog = json.loads(dialog)
                except Exception:
                    continue

            if not isinstance(dialog, list) or len(dialog) < 2:
                continue

            for i in range(len(dialog) - 1):
                cur  = dialog[i]
                nxt  = dialog[i + 1]

                if isinstance(cur, dict) and isinstance(nxt, dict):
                    spk_cur  = str(cur.get("speaker", cur.get("role", ""))).lower()
                    spk_next = str(nxt.get("speaker", nxt.get("role", ""))).lower()
                    txt_cur  = str(cur.get("text",  cur.get("content", ""))).strip()
                    txt_next = str(nxt.get("text",  nxt.get("content", ""))).strip()

                    # accept usr→sys or user→assistant or seeker→supporter
                    is_user_turn = spk_cur in ("usr", "user", "seeker", "human")
                    is_sys_turn  = spk_next in ("sys", "system", "supporter", "assistant", "bot")

                    if is_user_turn and is_sys_turn and txt_cur and txt_next and len(txt_next) > 10:
                        pairs.append({"input": txt_cur, "output": txt_next})

                elif isinstance(cur, str) and isinstance(nxt, str):
                    # Plain alternating strings: even=user, odd=sys
                    if i % 2 == 0 and cur.strip() and nxt.strip():
                        pairs.append({"input": cur.strip(), "output": nxt.strip()})

        logger.info("  ✅ ESConv (local): %d pairs from %d conversations", len(pairs), len(conversations))
        return pairs

    except Exception as exc:
        logger.warning("  ❌ ESConv failed: %s", exc)
        return []


# ── 4. DailyDialog — local JSON ──────────────────────────────────────────────

def _extract_utterance_text(u) -> str:
    """
    Normalize a single dialogue turn to plain text.
    Turns may be:
      - a plain string                       -> use as-is
      - a dict like {"speaker": ..., "utterance"/"text": "..."} -> extract the text field
    Anything else (or empty/missing text) returns "".
    """
    if isinstance(u, str):
        return u.strip()
    if isinstance(u, dict):
        for key in ("utterance", "text", "content", "message"):
            val = u.get(key)
            if isinstance(val, str) and val.strip():
                return val.strip()
        return ""
    return ""


def load_daily_dialog() -> list[dict]:
    """
    Reads from:
      data/dailydialog/train/dialogues.json   ← preferred
      data/dailydialog/train/train.json
      data/dailydialog/train.json
      data/dailydialog/validation.json

    dialogues.json format:
      list of dialogues, each dialogue = list of utterance strings,
      OR list of utterance dicts like {"speaker": "user", "utterance": "..."}
      (e.g. MultiWOZ-style), OR list of {"dialog": [...]} objects.
    """
    base = DATA_ROOT / "dailydialog"
    if not base.exists():
        logger.warning("  ❌ dailydialog folder not found: %s", base)
        return []

    # Only load these specific files — no rglob (avoids duplicate counting)
    # Priority: train/dialogues.json is the canonical DailyDialog file
    STRICT_CANDIDATES = [
        base / "train" / "dialogues.json",   # canonical dialogues file
        base / "validation.json",             # validation split
        base / "test.json",                   # test split (optional)
    ]
    # Fallback: if above don't exist, try train.json at root
    if not any(f.exists() for f in STRICT_CANDIDATES):
        STRICT_CANDIDATES = [base / "train.json", base / "validation.json"]

    all_dialogues: list[list[str]] = []
    loaded_files: set[str] = set()

    for fp in STRICT_CANDIDATES:
        if not fp.exists() or str(fp) in loaded_files:
            continue
        loaded_files.add(str(fp))
        try:
            raw = load_json_file(fp)
            before = len(all_dialogues)

            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, list):
                        dlg = [_extract_utterance_text(u) for u in item]
                        dlg = [u for u in dlg if u]
                        if len(dlg) >= 2:
                            all_dialogues.append(dlg)
                    elif isinstance(item, dict):
                        for key in ("dialog", "dialogue", "utterances", "turns", "conversation"):
                            turns = item.get(key)
                            if turns and isinstance(turns, list):
                                dlg = [_extract_utterance_text(u) for u in turns]
                                dlg = [u for u in dlg if u]
                                if len(dlg) >= 2:
                                    all_dialogues.append(dlg)
                                break
            elif isinstance(raw, dict):
                for v in raw.values():
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, list):
                                dlg = [_extract_utterance_text(u) for u in item]
                                dlg = [u for u in dlg if u]
                                if len(dlg) >= 2:
                                    all_dialogues.append(dlg)

            added = len(all_dialogues) - before
            logger.info("    %d dialogues from %s", added, fp.name)
        except Exception as exc:
            logger.warning("    Skipping %s: %s", fp.name, exc)

    # Deduplicate dialogues
    seen_dlg: set[str] = set()
    unique_dlg = []
    for dlg in all_dialogues:
        key = dlg[0][:80]
        if key not in seen_dlg:
            seen_dlg.add(key)
            unique_dlg.append(dlg)

    pairs = []
    for dlg in unique_dlg:
        for i in range(0, len(dlg) - 1, 2):
            u = dlg[i]
            b = dlg[i + 1] if i + 1 < len(dlg) else ""
            if u and b and len(u) > 5 and len(b) > 5:
                pairs.append({"input": u, "output": b})

    logger.info("  ✅ DailyDialog (local): %d pairs from %d dialogues", len(pairs), len(unique_dlg))
    return pairs


# ── 5. MentalHealth — HuggingFace Arrow file ─────────────────────────────────

def load_mental_health() -> list[dict]:
    """
    Reads from:
      data/mental_health_chat_dataset/train/data-00000-of-00001.arrow

    Magic bytes ffffffff confirm this is HuggingFace datasets format (not plain Arrow IPC).
    Must be read with datasets.Dataset.from_file(), NOT pyarrow.ipc.
    """
    base = DATA_ROOT / "mental_health_chat_dataset"
    if not base.exists():
        logger.warning("  ❌ mental_health_chat_dataset folder not found: %s", base)
        return []

    # ── Try HuggingFace datasets reader (correct for ffffffff magic) ──
    arrow_files = list(base.rglob("*.arrow"))
    if arrow_files:
        try:
            from datasets import Dataset  # type: ignore
            pairs = []
            for arrow_path in arrow_files:
                try:
                    ds = Dataset.from_file(str(arrow_path))
                    col_names = ds.column_names
                    logger.info("    Arrow columns: %s", col_names)

                    # Field name priority — questionText/answerText confirmed in this dataset
                    FIELD_PAIRS = [
                        ("questionText", "answerText"),   # confirmed: mental_health_chat_dataset
                        ("Context",      "Response"),
                        ("context",      "response"),
                        ("question",     "answer"),
                        ("Question",     "Answer"),
                        ("input",        "output"),
                        ("user",         "bot"),
                        ("prompt",       "completion"),
                        ("human",        "assistant"),
                        ("Patient",      "Doctor"),
                        ("patient",      "doctor"),
                        ("text",         "label"),
                    ]

                    q_col, a_col = None, None
                    for qk, ak in FIELD_PAIRS:
                        if qk in col_names and ak in col_names:
                            q_col, a_col = qk, ak
                            logger.info("    Using fields: %s → %s", q_col, a_col)
                            break

                    # Last resort: skip unknown layouts (avoid garbage like questionID→questionTitle)
                    if not q_col:
                        logger.warning("    Could not find valid Q/A columns in %s. Columns: %s", arrow_path.name, col_names)
                        continue

                    if not q_col:
                        logger.warning("    Could not identify Q/A columns in %s", arrow_path.name)
                        continue

                    for row in ds:
                        q = str(row.get(q_col) or "").strip()
                        a = str(row.get(a_col) or "").strip()
                        if q and a and len(q) > 10 and len(a) > 20:
                            pairs.append({"input": q, "output": a})

                    logger.info("    %d pairs from %s", len(pairs), arrow_path.name)

                except Exception as exc:
                    logger.warning("    datasets.Dataset.from_file failed for %s: %s", arrow_path.name, exc)

            if pairs:
                logger.info("  ✅ MentalHealth (HF arrow): %d pairs", len(pairs))
                return pairs

        except ImportError:
            logger.warning("    datasets library not installed — run: pip install datasets")

    # ── Fallback: any .json / .jsonl inside the folder ──
    FIELD_PAIRS = [
        ("Context", "Response"), ("context", "response"),
        ("question", "answer"),  ("Question", "Answer"),
        ("input", "output"),     ("user", "bot"),
        ("prompt", "completion"),("human", "assistant"),
        ("Patient", "Doctor"),   ("patient", "doctor"),
    ]
    pairs = []
    for fp in sorted(base.rglob("*.jsonl")) + sorted(base.rglob("*.json")):
        if fp.name in ("dataset_info.json", "state.json", "dataset_dict.json"):
            continue
        try:
            rows = load_jsonl_file(fp) if fp.suffix == ".jsonl" else load_json_file(fp)
            if isinstance(rows, dict):
                rows = list(rows.values())[0] if rows else []
            for row in rows:
                if not isinstance(row, dict):
                    continue
                q, a = "", ""
                for qk, ak in FIELD_PAIRS:
                    q = str(row.get(qk) or "").strip()
                    a = str(row.get(ak) or "").strip()
                    if q and a:
                        break
                if q and a and len(q) > 10 and len(a) > 20:
                    pairs.append({"input": q, "output": a})
        except Exception:
            pass

    if pairs:
        logger.info("  ✅ MentalHealth (json fallback): %d pairs", len(pairs))
    else:
        logger.warning("  ❌ MentalHealth: 0 pairs — run: pip install datasets")
    return pairs


# ── 6. VYNERA custom pairs ────────────────────────────────────────────────────

CUSTOM_PAIRS: list[dict] = [
    {"input": "I feel like nobody cares about me.",
     "output": "That feeling of being unseen is one of the loneliest things a person can carry. What you're feeling is real, and it matters. Can you tell me what's been making you feel this way lately?"},
    {"input": "I'm so stressed with work, I don't know how to cope.",
     "output": "When stress piles up like that, it can feel like there's no room to breathe. Before anything else — how are you right now, in this moment? Let's start there."},
    {"input": "I've been feeling really anxious about the future.",
     "output": "Anxiety about the future makes complete sense — the future is uncertain. I'm here. Tell me what's weighing on you the most right now."},
    {"input": "I had a panic attack today and I'm scared.",
     "output": "I'm really glad you're talking to me. Panic attacks are frightening — your body responds as if there's danger even when you're safe. You're okay right now. Can you tell me what happened before it started?"},
    {"input": "My relationship ended and I don't know who I am without them.",
     "output": "Losing a relationship can feel like losing a part of yourself. That grief is completely valid. You don't need to know who you are right now — you just need to feel what you're feeling. I'm here with you."},
    {"input": "I've been isolating myself and avoiding everyone.",
     "output": "Withdrawing when things are heavy is something many people do — it can feel safer. What's been making connection feel too hard lately?"},
    {"input": "I feel like a failure.",
     "output": "That word — failure — can feel so total and permanent when you're in this kind of pain. I want to understand what's happened that's brought you to this feeling. Will you tell me?"},
    {"input": "I can't sleep at night because my mind won't stop.",
     "output": "That racing-mind feeling at night is exhausting on a level that goes beyond just being tired. What does your mind keep returning to when you're trying to rest?"},
    {"input": "I'm grateful today. Things are going well.",
     "output": "That's genuinely wonderful to hear. What's been going well? I want to celebrate this with you."},
    {"input": "I set a new goal for myself this week.",
     "output": "That's such a meaningful thing — deciding on something you want to move toward. Tell me about it. What's the goal, and what made now the right time to set it?"},
    {"input": "I don't know what to do with my life.",
     "output": "Being honest about not knowing is a brave starting point — it means you're not pretending. What feels most unclear to you right now: direction, purpose, or something else?"},
    {"input": "I've been comparing myself to others a lot.",
     "output": "Comparison is one of the quieter ways we can be hard on ourselves. What is it you keep measuring yourself against?"},
    {"input": "I'm angry and I don't know why.",
     "output": "Anger without a clear cause can be frustrating in itself. Often it's carrying something underneath — stress, hurt, a sense of unfairness. What's been happening in your life recently?"},
    {"input": "I feel empty inside.",
     "output": "Emptiness is one of the harder feelings to sit with because it doesn't have the edges that grief or anger do. How long have you been feeling this way?"},
    {"input": "I'm really excited about something new happening in my life!",
     "output": "I can feel that excitement through your words! Tell me everything — what's happening? I want to hear all of it."},
    {"input": "I keep overthinking everything and it's exhausting.",
     "output": "Overthinking is one of the most draining things to live with — your mind working against you when you just want to rest. What kinds of thoughts keep looping for you?"},
    {"input": "I feel like I'm not good enough.",
     "output": "That feeling of not being enough is one of the most painful things to carry quietly. Where do you think it comes from — is it something that's been building, or did something specific happen?"},
    {"input": "I've been having really dark thoughts lately.",
     "output": "I'm glad you felt safe enough to share that with me. Dark thoughts can feel very isolating. Can you tell me a bit more about what those thoughts have been like?"},
    {"input": "I just want someone to listen to me.",
     "output": "I'm here. I'm listening. You have my full attention — tell me whatever you need to say."},
    {"input": "I feel overwhelmed and don't know where to start.",
     "output": "When everything piles up, even knowing where to begin can feel impossible. Let's slow down together. What feels most pressing to you right now?"},
    {"input": "I have been feeling really low lately.",
     "output": "I'm glad you're here and telling me. Low can mean so many things — heavy, hollow, tired, disconnected. Which of those feels closest to what you're carrying right now?"},
    {"input": "Nobody ever takes me seriously.",
     "output": "That's such a painful thing to feel, especially over time. Is this something that's been happening in a specific part of your life — work, relationships, family — or does it feel like it's everywhere?"},
    {"input": "I feel like I'm falling behind everyone else my age.",
     "output": "That comparison — measuring your life against some invisible timeline — can be crushing. What does 'falling behind' look like to you specifically? What are you measuring?"},
    {"input": "I think I might be burning out.",
     "output": "Burnout sneaks up slowly and then hits all at once. What's been draining you most — is it the volume of what's on your plate, or something about the work itself that's stopped feeling meaningful?"},
    {"input": "I don't feel motivated to do anything anymore.",
     "output": "That flatness — where nothing pulls you forward — is one of the harder things to sit with. How long has it been feeling like this?"},
]


# ── Merge, clean, deduplicate, split ─────────────────────────────────────────

def main() -> None:
    logger.info("Starting VYNERA data preparation...")
    logger.info("Data root: %s", DATA_ROOT.resolve())

    all_pairs: list[dict] = []

    # ── Cap formal/clinical-tone sources ──
    # EmpatheticDialogues and Counsel-Chat are written in a formal/therapist
    # register ("That's such a meaningful thing...", "I want to validate...").
    # At full size they dominate the dataset and the model learns to sound
    # like a counselor. Capping them lets the casual custom pairs set the
    # dominant tone while still keeping useful emotional-range examples.
    random.seed(42)

    # ── V6 REBALANCE ──
    # V5 (EmpatheticDialogues capped at 30k, ESConv uncapped at 14,328,
    # custom_v2 at 25x) gave val_loss 2.79 - much worse than V3's 1.03
    # (EmpatheticDialogues near-uncapped at ~70k, NO ESConv, NO custom_v2).
    #
    # ESConv pairs come from long multi-turn therapy-style conversations -
    # high entropy, hard to predict, and prone to the model fabricating
    # personal backstory ("We were engaged for 5 years...") when it tries
    # to imitate that long-form style.
    #
    # EmpatheticDialogues pairs are short situation/response Q&A - much
    # easier to predict (lower loss) while still being emotionally relevant.
    #
    # V6: raise EmpatheticDialogues back toward V3 levels, cap ESConv hard,
    # keep custom_v2 for tone but at a more moderate weight.

    empathetic = load_empathetic_dialogues()
    random.shuffle(empathetic)
    EMPATHETIC_CAP = 70000   # V3 had ~70k+ and got val_loss 1.03
    if len(empathetic) > EMPATHETIC_CAP:
        logger.info("Capping EmpatheticDialogues: %d -> %d", len(empathetic), EMPATHETIC_CAP)
        empathetic = empathetic[:EMPATHETIC_CAP]
    all_pairs.extend(empathetic)

    counsel = load_counsel_chat()
    random.shuffle(counsel)
    COUNSEL_CAP = 3000
    if len(counsel) > COUNSEL_CAP:
        logger.info("Capping Counsel-Chat: %d -> %d", len(counsel), COUNSEL_CAP)
        counsel = counsel[:COUNSEL_CAP]
    all_pairs.extend(counsel)

    # ESConv heavily capped - it's the main source of high-entropy long-form
    # responses that drag up loss and cause the model to fabricate backstory
    esconv = load_esconv()
    random.shuffle(esconv)
    ESCONV_CAP = 4000   # was 14,328 (uncapped) in V5
    if len(esconv) > ESCONV_CAP:
        logger.info("Capping ESConv: %d -> %d", len(esconv), ESCONV_CAP)
        esconv = esconv[:ESCONV_CAP]
    all_pairs.extend(esconv)

    # DailyDialog stays removed - confirmed bad in V4 (49% of raw data,
    # short generic exchanges, val_loss 2.88)
    # all_pairs.extend(load_daily_dialog())

    all_pairs.extend(load_mental_health())

    # ── Custom pairs V2 (casual best-friend tone) ──
    # Reduced from 25x to 12x - with EmpatheticDialogues back to ~70k,
    # 12x keeps custom pairs at a meaningful ~1-2% without overwhelming
    # the much larger base dataset
    from data.custom_pairs_v2 import CUSTOM_PAIRS_V2
    for _ in range(12):
        all_pairs.extend(CUSTOM_PAIRS_V2)

    # Old custom pairs - kept at 3x
    for _ in range(3):
        all_pairs.extend(CUSTOM_PAIRS)

    logger.info("Total raw pairs (before dedup/clean): %d", len(all_pairs))

    # Clean — validate format, length, reject service dialogue
    cleaned = [c for p in all_pairs if (c := clean_pair(p)) is not None]
    logger.info("After cleaning: %d", len(cleaned))

    # Deduplicate ONLY the base dataset (not custom pairs).
    # Custom pairs are intentionally repeated for weighting — deduplicating them
    # collapses 15 repeats back to 1, completely defeating the purpose.
    # Strategy: dedup base pairs first, then add all custom pairs after.

    # Split into custom vs base
    custom_inputs = set()
    for p in CUSTOM_PAIRS_V2:
        custom_inputs.add(p["input"][:100].lower())
    for p in CUSTOM_PAIRS:
        custom_inputs.add(p["input"][:100].lower())

    base_pairs   = [p for p in cleaned if p["input"][:100].lower() not in custom_inputs]
    custom_clean = [p for p in cleaned if p["input"][:100].lower() in custom_inputs]

    # Dedup only the base pairs
    seen:    set[str]   = set()
    deduped_base: list[dict] = []
    for p in base_pairs:
        key = p["input"][:100].lower()
        if key not in seen:
            seen.add(key)
            deduped_base.append(p)

    logger.info("Base pairs after dedup: %d", len(deduped_base))
    logger.info("Custom pairs (weighted, kept as-is): %d", len(custom_clean))

    # Combine: deduped base + all weighted custom pairs
    deduped = deduped_base + custom_clean
    logger.info("Total after dedup: %d", len(deduped))

    if len(deduped) < 100:
        logger.error("Too few pairs (%d). Check your dataset paths.", len(deduped))
        return

    # Shuffle + 95/5 split
    random.seed(42)
    random.shuffle(deduped)
    split       = int(len(deduped) * 0.95)
    train_pairs = deduped[:split]
    val_pairs   = deduped[split:]

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for p in train_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    with open(VAL_FILE, "w", encoding="utf-8") as f:
        for p in val_pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")

    logger.info("✅ train.jsonl → %d pairs  (%s)", len(train_pairs), OUTPUT_FILE)
    logger.info("✅ val.jsonl   → %d pairs  (%s)", len(val_pairs),   VAL_FILE)
    logger.info("")
    logger.info("── Breakdown ──")
    logger.info("  Base pairs (deduped):     %d", len(deduped_base))
    logger.info("  Custom pairs (weighted):  %d  (%.1f%% of total)",
                 len(custom_clean), 100 * len(custom_clean) / len(deduped))
    logger.info("")
    logger.info("Next step: upload train.jsonl and val.jsonl to Kaggle → Add Data → Upload Dataset")


if __name__ == "__main__":
    main()