"""Qualys label source: the scan's own CSV export as gold labels.

The CSV carries the same finding data the PDF renders (Threat/Impact/Solution
sections, QID, category). Pairing: block "QID: <n>" line + report host against
the CSV (IP, QID) rows; ties broken by Results-text overlap.
"""
from __future__ import annotations

import csv
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

_QID_RE = re.compile(r"^QID:\s*(\d+)", re.M)
# prompt contract: leading digit 5..1 -> label
_SEVERITY = {"5": "CRITICAL", "4": "HIGH", "3": "MEDIUM", "2": "LOW", "1": "INFO"}
# eval-baseline mapping: CVE ID column only (the xlsx referee ignores Vendor
# Reference and Bugtraq ID; the prompt mentions BIDs, a known inconsistency)
_REF_COLUMNS = ("CVE ID",)


def _read_export(path: Path) -> pd.DataFrame:
    """The export opens with account/scan preamble; the real table starts at
    the 'IP,...,QID,...' header row."""
    with path.open(encoding="utf-8-sig", errors="replace") as fh:
        for i, row in enumerate(csv.reader(fh)):
            if row and row[0] == "IP" and "QID" in row:
                return pd.read_csv(path, skiprows=i, encoding="utf-8-sig",
                                   encoding_errors="replace", dtype=str)
    raise ValueError(f"{path.name}: no IP/QID header row found")


def _references(row: pd.Series) -> list[str]:
    refs: list[str] = []
    for col in _REF_COLUMNS:
        if blank(row.get(col)):
            continue
        for part in str(row[col]).split(","):
            part = part.strip()
            if part and part != "-" and part not in refs:
                refs.append(part)
    return refs


class QualysCsvSource:
    name = "qualys-csv"
    scanner = "qualys"

    def __init__(self, resources_dir: Path):
        self.resources_dir = Path(resources_dir)
        self._model = extraction_model_for(get_scanner(self.scanner).record_type)

    def _target(self, row: pd.Series, block) -> dict:
        data = {
            "block_id": block.id,
            "Name": str(row["Title"]).strip(),
            "description": paragraphs(row.get("Threat")),
            "impact": paragraphs(row.get("Impact")),
            "solution": paragraphs(row.get("Solution")),
            "references": _references(row),
            "severity": _SEVERITY[str(row["Severity"]).strip()],
            "port": None if blank(row.get("Port")) else int(float(row["Port"])),
            "protocol": None if blank(row.get("Protocol")) else str(row["Protocol"]).strip().lower(),
            "category": None if blank(row.get("Category")) else str(row["Category"]).strip(),
            "plugin": int(row["QID"]),
        }
        return self._model.model_validate(data).model_dump(by_alias=True)

    def examples(self) -> Iterator[Example]:
        profile = get_scanner(self.scanner)
        for pdf in sorted(self.resources_dir.glob("*.pdf")):
            export = pdf.with_suffix(".csv")
            if not export.exists():
                continue
            df = _read_export(export)
            blocks = profile.segment(extract_pdf(pdf).text)

            index: dict[tuple[str, str], list] = defaultdict(list)
            for block in blocks:
                m = _QID_RE.search(block.text)
                if m and block.host:
                    index[(block.host, m.group(1))].append(block)

            used: dict[int, int] = defaultdict(int)
            for _, row in df.iterrows():
                candidates = index.get((str(row["IP"]).strip(), str(row["QID"]).strip())) or []
                if not candidates:
                    continue
                if len(candidates) > 1:
                    results = norm_key(row.get("Results"))
                    candidates = sorted(
                        candidates, key=lambda b: (used[b.id], -_overlap(results, b.text)))
                block = candidates[0]
                used[block.id] += 1
                yield Example(self.scanner, block, self._target(row, block), pdf.name)


def _overlap(needle_key: str, haystack_text: str) -> int:
    hay = norm_key(haystack_text)
    parts = [needle_key[i:i + 12] for i in range(0, len(needle_key), 12)]
    return sum(1 for p in parts if p in hay)
