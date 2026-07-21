"""Shared text helpers for the data engine (normalization, containment)."""
from __future__ import annotations

import math
import re
from collections import Counter

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_ARTIFACTS = ("￾", "﻿")  # broken ligatures / BOM from PDF text


def norm_key(name) -> str:
    """Alphanumeric squeeze; immune to PDF wrapping, ligatures, punctuation."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def blank(value) -> bool:
    return (value is None or (isinstance(value, float) and math.isnan(value))
            or str(value).strip() in ("", "nan"))


def tokens(value) -> Counter:
    if blank(value):
        return Counter()
    if isinstance(value, (list, tuple)):
        value = " ".join(str(v) for v in value)
    text = str(value)
    for a in _ARTIFACTS:
        text = text.replace(a, "")
    return Counter(_TOKEN_RE.findall(text.lower()))


def containment(field_tokens: Counter, block_tokens: Counter) -> float:
    """Fraction of a field's tokens present in the block; empty field -> 1.0."""
    total = sum(field_tokens.values())
    return sum((field_tokens & block_tokens).values()) / total if total else 1.0


def paragraphs(value) -> list[str]:
    """Blank-line-separated paragraphs, wrapping collapsed to single spaces."""
    if blank(value):
        return []
    return [p for para in re.split(r"\n\s*\n", str(value).strip())
            if (p := re.sub(r"\s+", " ", para.strip()))]
