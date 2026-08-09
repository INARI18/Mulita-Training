"""ZAP label source: the scan's own XML report as gold labels.

Alert fields are HTML fragments (<p>-separated); references gain the CWE/WASC
ids as entries, matching the tool's ZAP prompt contract. Pairing: block first
line "<Risk> <alert name>" against alertitems by normalized name.
"""
from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterator
from xml.etree import ElementTree

from mulitaminer.models import extraction_model_for
from mulitaminer.pdf_reader import extract_pdf
from mulitaminer.scanner_engine import get_scanner

from common import norm_key
from sources.base import Example

_RISK_WORDS = ("High", "Medium", "Low", "Informational")


def _paragraphs(fragment: str | None) -> list[str]:
    if not fragment:
        return []
    s = re.sub(r"</p>\s*<p>", "\n\n", fragment)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", s) if p.strip()]


def _references(item: ElementTree.Element) -> list[str]:
    refs = _paragraphs(item.findtext("reference"))
    for tag, label in (("cweid", "CWE"), ("wascid", "WASC")):
        value = (item.findtext(tag) or "").strip()
        if value and value != "-1":  # -1 = ZAP's "no id"
            refs.append(f"{label} {value}")
    return refs


def _instances(item: ElementTree.Element) -> list[dict]:
    out = []
    for inst in item.iter("instance"):
        out.append({
            "instance": (inst.findtext("uri") or "").strip(),
            "input_type": "",
            "input_name": (inst.findtext("param") or "").strip(),
            "payload": (inst.findtext("attack") or "").strip(),
            "proof": (inst.findtext("evidence") or "").strip(),
            "output": (inst.findtext("otherinfo") or "").strip(),
            "request_method": (inst.findtext("method") or "").strip(),
            "http_status_code": None,
            "http_protocol": "",
            "response_content_type": "",
        })
    return out


def parse_export(path: Path) -> list[dict]:
    """One dict per alertitem, in document order."""
    entries = []
    for item in ElementTree.parse(path).getroot().iter("alertitem"):
        entries.append({
            "Name": (item.findtext("name") or "").strip(),
            "description": _paragraphs(item.findtext("desc")),
            "solution": _paragraphs(item.findtext("solution")),
            "impact": [],
            "references": _references(item),
            "severity": (item.findtext("riskdesc") or "").split()[0],
            "port": None,
            "protocol": None,
            "plugin": int(item.findtext("pluginid")),
            "instances": _instances(item),
        })
    return entries


class ZapXmlSource:
    name = "zap-xml"
    scanner = "zap"

    def __init__(self, resources_dir: Path):
        self.resources_dir = Path(resources_dir)
        self._model = extraction_model_for(get_scanner(self.scanner).record_type)

    def _target(self, entry: dict, block) -> dict:
        return self._model.model_validate({**entry, "block_id": block.id}).model_dump(by_alias=True)

    def examples(self) -> Iterator[Example]:
        profile = get_scanner(self.scanner)
        for pdf in sorted(self.resources_dir.glob("*.pdf")):
            export = pdf.with_suffix(".xml")
            if not export.exists():
                continue
            entries = parse_export(export)
            blocks = profile.segment(extract_pdf(pdf).text)

            index: dict[str, list] = defaultdict(list)
            for block in blocks:
                first = block.text.strip().splitlines()[0]
                for word in _RISK_WORDS:
                    if first.startswith(word + " "):
                        first = first[len(word) + 1:]
                        break
                index[norm_key(first)].append(block)

            used: dict[int, int] = defaultdict(int)
            for entry in entries:
                candidates = index.get(norm_key(entry["Name"])) or []
                if not candidates:
                    continue
                candidates = sorted(candidates, key=lambda b: used[b.id])
                block = candidates[0]
                used[block.id] += 1
                yield Example(self.scanner, block, self._target(entry, block), pdf.name)
