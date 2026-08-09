"""Nessus label source: the "Vulnerabilities by Host" HTML export as gold labels.

Same parse as the tool's historical tools/nessus_html_to_baseline.py (regex over
the fixed export markup; no HTML-parser dependency). Field semantics follow the
baseline mapping: Synopsis -> description, Description -> insight, plugin
output -> detection_result. Pairing: block "<plugin> - <name>" heading + report
host against the parsed (host, plugin) entries.
"""
from __future__ import annotations

import html
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterator

from mulitaminer.models import extraction_model_for
from mulitaminer.pdf_reader import extract_pdf
from mulitaminer.scanner_engine import get_scanner

from common import norm_key
from sources.base import Example

_HOST_RE = re.compile(r'<div xmlns="" id="id\d+" style="font-size: 22px[^>]*>([0-9.]+)<')
_HEAD_RE = re.compile(r"onclick=\"toggleSection\('id\d+-container'\);\"[^>]*>(\d+) - ([^<]+)<")
_PORT_RE = re.compile(r"<h2>([^<]+)</h2>")
_OUTPUT_RE = re.compile(r"font-family: monospace;[^\"]*\">(.*?)<div class=\"clear\">", re.S)
_BLOCK_HEAD_RE = re.compile(r"^\s*(\d+) - ", re.M)


def _text(fragment: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", fragment)
    s = re.sub(r"<[^>]+>", "", s)
    return html.unescape(s).strip()


def _paragraphs(fragment: str) -> list[str]:
    body = _text(fragment)
    return [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]


def _field(segment: str, label: str) -> str | None:
    m = re.search(
        re.escape(label) + r'<div class="clear"></div>\s*</div>\s*'
        r'<div[^>]*>(.*?)<div class="clear">', segment, re.S)
    return m.group(1) if m else None


def _table_rows(segment: str, label: str) -> list[str]:
    m = re.search(
        re.escape(label) + r'<div class="clear"></div>\s*</div>\s*'
        r'<div[^>]*class="table-wrapper see-also">(.*?)</table>', segment, re.S)
    if not m:
        return []
    out = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", m.group(1), re.S):
        cells = [c for c in (_text(td) for td in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)) if c]
        if cells:
            out.append(" ".join(cells))
    return out


def parse_export(path: Path) -> list[dict]:
    """One dict per finding, keyed for pairing by host + plugin."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    body = raw[raw.find('id="id1"'):]

    hosts = [(m.start(), m.group(1)) for m in _HOST_RE.finditer(body)]
    bounds = [m.start() for m in _HEAD_RE.finditer(body)] + [len(body)]

    def owner(pos: int) -> str:
        cur = ""
        for start, ip in hosts:
            if start >= pos:
                break
            cur = ip
        return cur

    entries = []
    for i in range(len(bounds) - 1):
        seg = body[bounds[i]:bounds[i + 1]]
        head = _HEAD_RE.search(seg)
        plugin_id, name = int(head.group(1)), head.group(2).strip()

        proto, port = None, None
        if p := _PORT_RE.search(seg):
            parts = p.group(1).split("/")
            proto = parts[0].strip().lower() or None
            port = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else None

        cvss = []
        for label in ("CVSS v2.0 Base Score", "CVSS v2.0 Temporal Score",
                      "CVSS v3.0 Base Score", "CVSS v3.0 Temporal Score"):
            if v := _field(seg, label):
                cvss.append(f"{label} {_text(v)}")

        details: dict = {"plugin_id": plugin_id}
        if info := _field(seg, "Plugin Information"):
            keys = {"published": "publication_date", "modified": "modification_date"}
            for part in _text(info).split(","):
                if ":" in part:
                    k, v = part.split(":", 1)
                    if key := keys.get(k.strip().lower()):
                        details[key] = v.strip()

        out_block = _OUTPUT_RE.search(seg)
        risk = _field(seg, "Risk Factor")

        entries.append({
            "host": owner(bounds[i]),
            "plugin": plugin_id,
            "Name": name,
            "description": _paragraphs(_field(seg, "Synopsis") or ""),
            "solution": _paragraphs(_field(seg, "Solution") or ""),
            "references": _table_rows(seg, "See Also") + _table_rows(seg, "References"),
            "severity": _text(risk).upper() if risk else "NONE",
            "port": port,
            "protocol": proto,
            "cvss": cvss,
            "insight": _paragraphs(_field(seg, "Description") or ""),
            "detection_result": _paragraphs(out_block.group(1)) if out_block else [],
            "plugin_details": details,
        })
    return entries


class NessusHtmlSource:
    name = "nessus-html"
    scanner = "nessus"

    def __init__(self, resources_dir: Path):
        self.resources_dir = Path(resources_dir)
        self._model = extraction_model_for(get_scanner(self.scanner).record_type)

    def _target(self, entry: dict, block) -> dict:
        data = {k: v for k, v in entry.items() if k != "host"}
        data["block_id"] = block.id
        data["impact"] = []
        return self._model.model_validate(data).model_dump(by_alias=True)

    def examples(self) -> Iterator[Example]:
        profile = get_scanner(self.scanner)
        for pdf in sorted(self.resources_dir.glob("*.pdf")):
            export = pdf.with_suffix(".html")
            if not export.exists():
                continue
            entries = parse_export(export)
            blocks = profile.segment(extract_pdf(pdf).text)

            index: dict[tuple[str, int], list] = defaultdict(list)
            for block in blocks:
                m = _BLOCK_HEAD_RE.match(block.text)
                if m and block.host:
                    index[(block.host, int(m.group(1)))].append(block)

            used: dict[int, int] = defaultdict(int)
            for entry in entries:
                candidates = index.get((entry["host"], entry["plugin"])) or []
                if not candidates:
                    continue
                if len(candidates) > 1:
                    result = norm_key(" ".join(entry["detection_result"]) or entry.get("port"))
                    candidates = sorted(
                        candidates, key=lambda b: (used[b.id], -_overlap(result, b.text)))
                block = candidates[0]
                used[block.id] += 1
                yield Example(self.scanner, block, self._target(entry, block), pdf.name)


def _overlap(needle_key: str, haystack_text: str) -> int:
    hay = norm_key(haystack_text)
    parts = [needle_key[i:i + 12] for i in range(0, len(needle_key), 12)]
    return sum(1 for p in parts if p in hay)
