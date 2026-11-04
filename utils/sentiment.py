"""
utils/sentiment.py
------------------
Emotion detection for VYNERA AI.

Detects: happiness, sadness, anxiety, anger (+ neutral)
Returns emotion label, intensity (0–1), and valence score (-1 to +1).

Uses a lightweight rule-based approach as the fast path and falls back to
the fine-tuned DialoGPT classifier when the model is loaded.
This keeps the chat WebSocket latency low.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# ─── Keyword banks ────────────────────────────────────────────────────────────

_BANKS: dict[str, list[str]] = {
    "happiness": [
        "happy", "joy", "joyful", "excited", "great", "amazing", "wonderful",
        "fantastic", "love", "loved", "grateful", "thankful", "blessed",
        "elated", "thrilled", "delighted", "content", "glad", "smile",
        "laugh", "laughing", "awesome", "brilliant", "proud", "hopeful",
        "positive", "optimistic", "cheerful", "celebrate", "celebrating",
    ],
    "sadness": [
        "sad", "sadness", "depressed", "depression", "unhappy", "miserable",
        "crying", "cry", "tears", "grief", "grieving", "lost", "lonely",
        "alone", "hopeless", "empty", "numb", "heartbroken", "hurt",
        "disappointed", "miss", "missing", "low", "down", "broken",
        "worthless", "useless", "failure", "give up", "giving up",
    ],
    "anxiety": [
        "anxious", "anxiety", "worried", "worry", "scared", "fear", "afraid",
        "nervous", "nervous", "panic", "panicking", "stress", "stressed",
        "overwhelmed", "terrified", "dread", "dreading", "apprehensive",
        "uneasy", "restless", "tense", "tension", "catastrophe", "disaster",
        "can't breathe", "can't sleep", "sleepless", "overthinking",
    ],
    "anger": [
        "angry", "anger", "furious", "rage", "mad", "frustrated",
        "frustration", "irritated", "annoyed", "hate", "hateful",
        "disgusted", "resentful", "bitter", "betrayed", "unfair",
        "bullshit", "pissed", "livid", "enraged", "hostile", "fed up",
    ],
}

# Valence by emotion
_VALENCE: dict[str, float] = {
    "happiness": 1.0,
    "sadness": -0.8,
    "anxiety": -0.6,
    "anger": -0.7,
    "neutral": 0.0,
}

# Intensifiers
_INTENSIFIERS = re.compile(
    r"\b(very|extremely|so|incredibly|absolutely|totally|deeply|utterly|"
    r"completely|really|terribly|awfully|beyond|insanely)\b",
    re.I,
)
_DIMINISHERS = re.compile(
    r"\b(a bit|slightly|kind of|sort of|a little|somewhat|maybe|perhaps)\b",
    re.I,
)


@dataclass
class EmotionResult:
    emotion: str
    intensity: float        # 0.0 – 1.0
    valence: float          # -1.0 – +1.0
    label: str              # "mildly", "moderately", "strongly"


def _intensity_label(intensity: float) -> str:
    if intensity >= 0.7:
        return "strongly"
    if intensity >= 0.4:
        return "moderately"
    return "mildly"


def detect_emotion(text: str) -> EmotionResult:
    """Fast rule-based emotion detection."""
    text_lower = text.lower()
    words = re.findall(r"\b\w+\b", text_lower)
    word_set = set(words)

    scores: dict[str, int] = {e: 0 for e in _BANKS}
    for emotion, keywords in _BANKS.items():
        for kw in keywords:
            # multi-word keywords
            if " " in kw:
                if kw in text_lower:
                    scores[emotion] += 2
            elif kw in word_set:
                scores[emotion] += 1

    best_emotion = max(scores, key=lambda e: scores[e])
    best_score = scores[best_emotion]

    if best_score == 0:
        return EmotionResult(
            emotion="neutral",
            intensity=0.1,
            valence=0.0,
            label="mildly",
        )

    # Base intensity: clamp keyword hits to 0–1 range
    base = min(best_score / 5.0, 1.0)

    # Adjust for intensifiers / diminishers
    intensifier_count = len(_INTENSIFIERS.findall(text_lower))
    diminisher_count = len(_DIMINISHERS.findall(text_lower))
    intensity = base + 0.1 * intensifier_count - 0.1 * diminisher_count
    intensity = max(0.05, min(1.0, intensity))

    valence = _VALENCE[best_emotion]
    # Scale valence by intensity
    scaled_valence = valence * intensity

    return EmotionResult(
        emotion=best_emotion,
        intensity=round(intensity, 3),
        valence=round(scaled_valence, 3),
        label=_intensity_label(intensity),
    )


def emotion_to_dict(result: EmotionResult) -> dict:
    return {
        "emotion": result.emotion,
        "intensity": result.intensity,
        "valence": result.valence,
        "label": result.label,
    }