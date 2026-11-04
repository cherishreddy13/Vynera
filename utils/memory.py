"""
utils/memory.py
---------------
Extracts factual information from user messages and stores them
as key-value memory entries in MongoDB.

Patterns extracted:
  name, age, occupation, location, pet (dog/cat), relationship,
  health condition, hobby, goal mention, language, school/college
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class MemoryFact:
    key: str
    value: str


# ─── Pattern definitions ──────────────────────────────────────────────────────

_PATTERNS: list[tuple[str, re.Pattern, int]] = [
    # (key_name, compiled_regex, group_index_for_value)

    # Name: "my name is X" / "I'm X" / "call me X"
    ("name", re.compile(
        r"(?:my name is|i(?:'m| am) called|call me|i go by)\s+([A-Za-z][A-Za-z\s\-']{1,30})",
        re.I), 1),

    # Age: "I am 25 years old" / "I'm 25"
    ("age", re.compile(
        r"i(?:'m| am)\s+(\d{1,3})\s*(?:years?\s*old)?", re.I), 1),

    # Occupation
    ("occupation", re.compile(
        r"(?:i(?:'m| am) a|i work as(?: a)?|my job is|my profession is)\s+([A-Za-z][A-Za-z\s]{2,40})",
        re.I), 1),

    # Location: "I live in X" / "I'm from X"
    ("location", re.compile(
        r"(?:i live in|i(?:'m| am) from|i(?:'m| am) based in|i(?:'m| am) in)\s+([A-Za-z][A-Za-z\s,]{2,50})",
        re.I), 1),

    # Dog name
    ("pet_dog", re.compile(
        r"(?:my dog(?:'s| is)? name(?:d)? is|my dog is called|i have a dog (?:named|called))\s+([A-Za-z][A-Za-z\s\-]{1,20})",
        re.I), 1),

    # Cat name
    ("pet_cat", re.compile(
        r"(?:my cat(?:'s| is)? name(?:d)? is|my cat is called|i have a cat (?:named|called))\s+([A-Za-z][A-Za-z\s\-]{1,20})",
        re.I), 1),

    # Partner/spouse
    ("partner", re.compile(
        r"my (?:wife|husband|partner|boyfriend|girlfriend)(?:'s name is| is called| is)\s+([A-Za-z][A-Za-z\s\-]{1,30})",
        re.I), 1),

    # Hobby
    ("hobby", re.compile(
        r"(?:i love|i enjoy|i like|my hobby is|i(?:'m| am) into)\s+([A-Za-z][A-Za-z\s]{3,40})",
        re.I), 1),

    # Health condition
    ("health_condition", re.compile(
        r"(?:i have|i was diagnosed with|i suffer from|i struggle with)\s+((?:depression|anxiety|adhd|bipolar|ocd|ptsd|diabetes|asthma|[A-Za-z\s]{4,40}))",
        re.I), 1),

    # School / college
    ("school", re.compile(
        r"(?:i(?:'m| am) (?:studying|a student) at|i (?:go to|attend)|my college is|my school is)\s+([A-Za-z][A-Za-z\s\-,]{3,60})",
        re.I), 1),

    # Language
    ("language", re.compile(
        r"(?:i speak|my (?:native|first|primary) language is|i(?:'m| am) (?:fluent in|learning))\s+([A-Za-z][A-Za-z\s]{2,30})",
        re.I), 1),
]

# Clean up extracted values
_CLEAN_ENDINGS = re.compile(r"[.,!?;:\s]+$")


def _clean(value: str) -> str:
    return _CLEAN_ENDINGS.sub("", value.strip())


def extract_facts(text: str) -> list[MemoryFact]:
    """
    Extract all recognisable facts from a single user message.
    Returns a (potentially empty) list of MemoryFact objects.
    """
    facts: list[MemoryFact] = []
    for key, pattern, group in _PATTERNS:
        match = pattern.search(text)
        if match:
            value = _clean(match.group(group))
            if value and len(value) >= 2:
                facts.append(MemoryFact(key=key, value=value))
    return facts


def format_memory_for_prompt(memories: list[dict]) -> str:
    """
    Convert stored memory dicts to a compact string for the system prompt.
    E.g.: "name: Arjun | occupation: nurse | location: Bangalore"
    """
    if not memories:
        return ""
    parts = [f"{m['key']}: {m['value']}" for m in memories]
    return " | ".join(parts)