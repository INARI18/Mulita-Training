"""OpenVAS label source: vulnnet CSV export as teacher-free gold labels.

The CSV is the same data the PDF renders (verified 1:1 by verify/pairing and
>=0.99 field containment by verify/content). Each PDF block is the model
input; its matched CSV row is the target, validated through the tool's own
extraction contract so a bad row raises instead of becoming a bad label.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path
from typing import Iterator

import pandas as pd

from mulitaminer.models import extraction_model_for
from mulitaminer.pdf_reader import extract_pdf
from mulitaminer.scanner_engine import get_scanner

from common import blank, norm_key, paragraphs
from sources.base import Example
from sources.openvas.references import build_references

_NVT_RE = re.compile(r"^NVT:\s*(.*)$")
_TEXT_FIELDS = {
    "Summary": "description",
    "Solution": "solution",
    "Impact": "impact",
    "Vulnerability Insight": "insight",
    "Specific Result": "detection_result",
    "Vulnerability Detection Method": "detection_method",
    "Product Detection Result": "product_detection_result",
}


def _port(value) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _protocol(value) -> str | None:
    p = str(value).strip().lower()
    return p if p in ("tcp", "udp") else None


class OpenVASCsvSource:
    name = "openvas-csv"
    scanner = "openvas"

    def __init__(self, pdfs_dir: Path, csv_path: Path):
        self.pdfs_dir = Path(pdfs_dir)
        self.csv_path = Path(csv_path)
        self._model = extraction_model_for(get_scanner(self.scanner).record_type)

    def _target(self, row: pd.Series, block) -> dict:
        data: dict = {"block_id": block.id, "Name": str(row["NVT Name"]).strip()}
        for column, field in _TEXT_FIELDS.items():
            data[field] = paragraphs(row.get(column))
        data["references"] = build_references(block.text)
        data["log_method"] = []
        data["cvss"] = None if blank(row.get("CVSS")) else float(row["CVSS"])
        data["severity"] = str(row["Severity"]).strip().upper()
        data["port"] = _port(row.get("Port"))
        data["protocol"] = _protocol(row.get("Port Protocol"))
        return self._model.model_validate(data).model_dump(by_alias=True)

    def examples(self) -> Iterator[Example]:
        df = pd.read_csv(self.csv_path)
        df["_key"] = df["NVT Name"].map(norm_key)
        profile = get_scanner(self.scanner)

        for pdf in sorted(self.pdfs_dir.glob("*.pdf")):
            blocks = profile.segment(extract_pdf(pdf).text)
            index: dict[str, list] = defaultdict(list)
            for block in blocks:
                for line in block.text.splitlines():
                    m = _NVT_RE.match(line.strip())
                    if m:
                        index[norm_key(m.group(1))].append(block)
                        break
            host = next((b.host for b in blocks if b.host), None)
            rows = df[df["IP"] == host] if host else df.iloc[0:0]

            used: dict[int, int] = defaultdict(int)
            for _, row in rows.iterrows():
                candidates = index.get(row["_key"]) or []
                if not candidates:
                    continue
                if len(candidates) > 1:
                    sr = norm_key(row.get("Specific Result"))
                    candidates = sorted(
                        candidates,
                        key=lambda b: (used[b.id], -_overlap(sr, b.text)),
                    )
                block = candidates[0]
                used[block.id] += 1
                yield Example(self.scanner, block, self._target(row, block), pdf.name)


def _overlap(needle_key: str, haystack_text: str) -> int:
    hay = norm_key(haystack_text)
    parts = [needle_key[i:i + 12] for i in range(0, len(needle_key), 12)]
    return sum(1 for p in parts if p in hay)
