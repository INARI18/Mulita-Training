"""Build the `references` label from a PDF block, one reference per element.

OpenVAS renders References one item per line ("cve: CVE-2016-5770",
"url: http://...", "cert-bund: CB-K16/2012"). Parsing the block's own section
yields atomic references that follow the extraction contract (label stripped,
no empties) and are present in the input by construction.
"""
from __future__ import annotations

import re

_HEADER_RE = re.compile(r"^references?:?\s*$", re.IGNORECASE)
_LABELED_RE = re.compile(r"^([a-z][a-z-]{1,15}):\s*(.+)$", re.IGNORECASE)
_URL_RE = re.compile(r"^(https?://\S+)$", re.IGNORECASE)
_LABEL_ONLY_RE = re.compile(r"^[a-z][a-z-]{1,15}:\s*$", re.IGNORECASE)


def build_references(block_text: str) -> list[str]:
    """Return atomic references from the block's References section.

    Each list element is a single reference with its category label stripped
    ("cve: CVE-2016-5770" -> "CVE-2016-5770"). Label-only lines and empties
    are dropped. Order is preserved; duplicates are removed keeping first.
    """
    lines = block_text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if _HEADER_RE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return []

    refs: list[str] = []
    for raw in lines[start:]:
        line = raw.strip()
        if not line:
            continue
        # URL first: a bare URL's "https" scheme would match as a label.
        if _URL_RE.match(line):
            refs.append(line)
            continue
        m = _LABELED_RE.match(line)
        if m:
            value = m.group(2).strip()
            if value and value != "-":
                refs.append(value)
            continue
        if _LABEL_ONLY_RE.match(line):  # empty entry, skip
            continue
        break  # section header / prose ends the trailing References region

    seen: set[str] = set()
    unique: list[str] = []
    for r in refs:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique
