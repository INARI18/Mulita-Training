"""Map each CSV export row to a schema-valid extraction label for its PDF block.

The OpenVAS CSV export is the same data the PDF renders, in clean structured
columns (verified 1:1 by verify_pairing.py and >=0.99 field containment by
content_check.py). That makes it a teacher-free gold label source: the block
text is the model INPUT, the mapped CSV row is the TARGET.

`iter_labeled_blocks` yields (pdf_path, block, target_dict) where target_dict
is exactly the object the tool's LLM contract expects for one block
(`extraction_model_for(OpenVASRecord)`): block_id + LLM-produced fields.
Every target is validated through that model, so a malformed row raises
rather than producing a bad label.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterator

import pandas as pd

from mulitaminer.models import OpenVASRecord, extraction_model_for
from mulitaminer.pdf_reader import extract_pdf
from mulitaminer.scanner_engine import get_scanner

from references_from_pdf import build_references

HERE = Path(__file__).resolve().parent.parent
_NVT_RE = re.compile(r"^NVT:\s*(.*)$")

# CSV column -> schema list[str] text field. Each cell is split into paragraphs.
_TEXT_FIELDS = {
    "Summary": "description",
    "Solution": "solution",
    "Impact": "impact",
    "Vulnerability Insight": "insight",
    "Specific Result": "detection_result",
    "Vulnerability Detection Method": "detection_method",
    "Product Detection Result": "product_detection_result",
}


def norm_key(name) -> str:
    """Alphanumeric squeeze; immune to PDF wrapping/ligature artifacts."""
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def _blank(value) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value)) or \
        str(value).strip() in ("", "nan")


def _paragraphs(value) -> list[str]:
    """Split a CSV text cell into paragraphs (blank-line separated), collapsing
    the hard-wrapped continuation lines within each paragraph to single spaces."""
    if _blank(value):
        return []
    out: list[str] = []
    for para in re.split(r"\n\s*\n", str(value).strip()):
        collapsed = re.sub(r"\s+", " ", para.strip())
        if collapsed:
            out.append(collapsed)
    return out


def _port(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _protocol(value) -> str | None:
    p = str(value).strip().lower()
    return p if p in ("tcp", "udp") else None


def row_to_target(row: pd.Series, block_text: str, block_id: int) -> dict:
    """Build and validate the LLM-target object for one finding."""
    data: dict = {"block_id": block_id, "Name": str(row["NVT Name"]).strip()}
    for column, field in _TEXT_FIELDS.items():
        data[field] = _paragraphs(row.get(column))
    data["references"] = build_references(block_text)
    data["log_method"] = []
    data["plugin"] = None
    data["plugin_details"] = {}
    data["instances"] = []
    data["cvss"] = None if _blank(row.get("CVSS")) else float(row["CVSS"])
    data["severity"] = str(row["Severity"]).strip().upper()
    data["port"] = _port(row.get("Port"))
    data["protocol"] = _protocol(row.get("Port Protocol"))

    # Validate against the exact contract the tool expects for one block.
    model = extraction_model_for(OpenVASRecord)
    return model.model_validate(data).model_dump(by_alias=True)


def _block_index(blocks) -> dict[str, list]:
    """Map normalized NVT name -> blocks carrying it (duplicates possible)."""
    index: dict[str, list] = defaultdict(list)
    for block in blocks:
        for line in block.text.splitlines():
            m = _NVT_RE.match(line.strip())
            if m:
                index[norm_key(m.group(1))].append(block)
                break
    return index


def iter_labeled_blocks(
    pdfs_dir: Path, csv_path: Path
) -> Iterator[tuple[Path, object, dict]]:
    """Yield (pdf_path, block, target_dict) for every CSV row matched to a block."""
    df = pd.read_csv(csv_path)
    df["_key"] = df["NVT Name"].map(norm_key)
    profile = get_scanner("openvas")

    for pdf_path in sorted(pdfs_dir.glob("*.pdf")):
        doc = extract_pdf(pdf_path)
        blocks = profile.segment(doc.text)
        index = _block_index(blocks)
        host = next((b.host for b in blocks if b.host), None)
        rows = df[df["IP"] == host] if host else df.iloc[0:0]

        used: dict[int, int] = defaultdict(int)  # block id -> times consumed
        for _, row in rows.iterrows():
            candidates = index.get(row["_key"]) or []
            if not candidates:
                continue
            # Duplicate names on one host: pick by best Specific Result overlap,
            # then round-robin so each block instance is used once.
            if len(candidates) > 1:
                sr = norm_key(row.get("Specific Result"))
                candidates = sorted(
                    candidates,
                    key=lambda b: (used[b.id], -_overlap(sr, b.text)),
                )
            block = candidates[0]
            used[block.id] += 1
            yield pdf_path, block, row_to_target(row, block.text, block.id)


def _overlap(needle_key: str, haystack_text: str) -> int:
    hay = norm_key(haystack_text)
    return sum(1 for chunk in _chunks(needle_key) if chunk in hay)


def _chunks(text: str, size: int = 12) -> list[str]:
    return [text[i:i + size] for i in range(0, len(text), size)] if text else []
