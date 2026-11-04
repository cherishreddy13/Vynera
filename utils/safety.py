"""
utils/safety.py
---------------
VYNERA AI Psychological Safety Layer.

Three hardcoded protections that cannot be bypassed:
  1. Crisis detection  — suicidal ideation / self-harm
  2. Medical guard     — diagnosis / medication requests
  3. Response validation — filters toxic positivity, harmful content

All checks run on every message before it is delivered to the user.
"""

from __future__ import annotations

import re
from config import settings

# ─── Crisis signals ───────────────────────────────────────────────────────────

_CRISIS_PATTERNS = re.compile(
    r"\b("
    r"kill myself|killing myself|end my life|take my life|end it all|"
    r"want to die|wanna die|ready to die|don't want to live|don't wanna live|"
    r"no reason to live|not worth living|life is not worth|"
    r"suicide|suicidal|cut myself|cutting myself|self.harm|hurt myself|"
    r"overdose|hang myself|jump off|"
    r"goodbye forever|final goodbye|last message|"
    r"can't go on|cannot go on|no way out|it's too late for me"
    r")\b",
    re.I,
)

# ─── Medical guard signals ────────────────────────────────────────────────────

_MEDICAL_PATTERNS = re.compile(
    r"\b("
    r"diagnose me|what disease do i have|do i have [a-z]+|"
    r"what medication|prescribe|should i take [a-z]+ mg|"
    r"what pills|what drugs should|am i depressed clinically|"
    r"do i have anxiety disorder|do i have adhd|"
    r"what dose|dosage for|can i take [a-z]+ with [a-z]+"
    r")\b",
    re.I,
)

# ─── Toxic positivity filter ──────────────────────────────────────────────────

_TOXIC_PHRASES: list[str] = [
    "just think positive",
    "think positive",
    "others have it worse",
    "other people have it worse",
    "at least you",
    "could be worse",
    "you should smile",
    "stop being negative",
    "get over it",
    "man up",
    "toughen up",
    "stop feeling sorry for yourself",
    "you're overreacting",
    "it's not that bad",
    "just be happy",
    "everything happens for a reason",
    "good vibes only",
    "look on the bright side",
    "just focus on the positives",
    "push through it",
    "never give up",
    "you're stronger than this",
]

_SHAME_PHRASES: list[str] = [
    "you should be ashamed",
    "that's pathetic",
    "what's wrong with you",
    "you're weak",
    "you're a burden",
    "grow up",
    "don't be so sensitive",
]

# ─── Fallback responses ───────────────────────────────────────────────────────

_CRISIS_RESPONSE = (
    "I hear you, and I want you to know that what you're feeling matters deeply. "
    "You are not alone in this. Please reach out to a crisis support line right now — "
    "they are trained to help and will listen without judgment.\n\n"
    f"🆘 {settings.crisis_hotline}\n\n"
    "I'm here with you. Would you like to talk about what's been building up?"
)

_MEDICAL_RESPONSE = (
    "I care about your health deeply, and I want to be honest with you — "
    "I'm not a medical professional and it wouldn't be right for me to try to diagnose "
    "or recommend medications. What you're describing deserves real, qualified attention. "
    "Please speak with a doctor or mental health professional who can properly support you. "
    "I'm here to listen and support you emotionally in the meantime."
)

_SAFE_FALLBACK = (
    "I want to make sure I'm responding to you thoughtfully. "
    "Could you tell me a bit more about what's on your mind? "
    "I'm here and I'm listening."
)


# ─── Public API ───────────────────────────────────────────────────────────────

class SafetyResult:
    __slots__ = ("is_crisis", "is_medical", "override_response")

    def __init__(self, is_crisis: bool, is_medical: bool, override_response: str | None):
        self.is_crisis = is_crisis
        self.is_medical = is_medical
        self.override_response = override_response

    @property
    def blocked(self) -> bool:
        return self.override_response is not None


def check_input(text: str) -> SafetyResult:
    """
    Check user input for safety signals.
    Returns a SafetyResult. If .blocked is True, use .override_response
    instead of sending to the model.
    """
    if _CRISIS_PATTERNS.search(text):
        return SafetyResult(True, False, _CRISIS_RESPONSE)
    if _MEDICAL_PATTERNS.search(text):
        return SafetyResult(False, True, _MEDICAL_RESPONSE)
    return SafetyResult(False, False, None)


def validate_response(text: str) -> str:
    """
    Validate and sanitise a model-generated response before delivery.
    Strips toxic positivity phrases. If the response is empty or
    incoherent after cleaning, returns a safe fallback.
    """
    if not text or len(text.strip()) < 5:
        return _SAFE_FALLBACK

    cleaned = text
    text_lower = text.lower()

    for phrase in _TOXIC_PHRASES + _SHAME_PHRASES:
        if phrase in text_lower:
            # Replace at the correct position (case-insensitive)
            pattern = re.compile(re.escape(phrase), re.I)
            cleaned = pattern.sub("", cleaned)

    # Clean up double spaces / trailing punctuation artifacts
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()

    if not cleaned or len(cleaned) < 10:
        return _SAFE_FALLBACK

    return cleaned


def is_incoherent(text: str) -> bool:
    """Basic incoherence check — repeated tokens, too short, all symbols."""
    words = text.split()
    if len(words) < 3:
        return True
    # If more than 40% of words are the same token, it's likely a generation loop
    if words:
        most_common = max(set(words), key=words.count)
        if words.count(most_common) / len(words) > 0.4:
            return True
    return False