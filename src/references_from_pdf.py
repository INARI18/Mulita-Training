"""Build the `references` label from a PDF block, one reference per element.

The vulnnet OpenVAS reports render the References section one item per line,
each prefixed by a category label:

    References
    cve: CVE-2016-5770
    cve: CVE-2016-5771
    url: http://www.php.net/ChangeLog-5.php
    cert-bund: CB-K16/2012

The training label must follow the tool's extraction contract (one reference
per element, category label stripped, no label-only empties) AND be literally
present in the block text the model is trained on. Parsing the block's own
References section satisfies both by construction.
"""
from __future__ import annotations

import re

# "References" header (some reports title it "References:" or "Reference").
_HEADER_RE = re.compile(r"^references?:?\s*$", re.IGNORECASE)
# A labeled reference line: "<label>: <value>". Label is a short lowercase
# token possibly hyphenated (cve, url, bid, cert-bund, dfn-cert, other, ...).
_LABELED_RE = re.compile(r"^([a-z][a-z-]{1,15}):\s*(.+)$", re.IGNORECASE)
# A bare URL line with no label prefix.
_URL_RE = re.compile(r"^(https?://\S+)$", re.IGNORECASE)
# A label with no value ("other:", "cve:") — an empty reference entry.
_LABEL_ONLY_RE = re.compile(r"^[a-z][a-z-]{1,15}:\s*$", re.IGNORECASE)
# Section headers that end the References block if one follows it.
_SECTION_RE = re.compile(
    r"^(summary|impact|solution|affected|vulnerability|product|log|references?"
    r"|oid|cvss|quality of detection)\b",
    re.IGNORECASE,
)


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
        # URL first: a bare URL's scheme ("https") would otherwise be parsed
        # as a category label, mangling the value.
        if _URL_RE.match(line):
            refs.append(line)
            continue
        m = _LABELED_RE.match(line)
        if m:
            value = m.group(2).strip()
            if value and value != "-":
                refs.append(value)
            continue
        # A label with no value ("other:", "cve:") is an empty entry: skip it,
        # don't end the section.
        if _LABEL_ONLY_RE.match(line):
            continue
        # A new section header (or any other unlabeled prose) ends the
        # references region; blocks are finding-scoped, so References trails.
        break

    seen: set[str] = set()
    unique: list[str] = []
    for r in refs:
        if r not in seen:
            seen.add(r)
            unique.append(r)
    return unique
