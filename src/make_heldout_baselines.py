"""Build eval baselines for every held-out report from the scanners' own exports.

Reuses the training LabelSources (the same gold mapping training uses) on the
held-out reports only, applying the same input-faithfulness trim as training
(paragraphs the PDF never renders are removed, so the ruler never demands text
the input does not show). Output: data/heldout/<scanner>/<stem>.xlsx + a copy
of the PDF, ready for `mulitaminer evaluate`. resources/ is never touched.

  uv run --no-sync python ../mulita-extractor-training/src/make_heldout_baselines.py
"""
from __future__ import annotations

import json
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from build_dataset import CONTAINMENT_MIN, default_sources, text_fields, trim_target  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO.parent / "MulitaMiner2"

BASE = ["Name", "description", "solution", "impact", "references", "severity",
        "host", "port", "protocol", "source"]
COLUMNS = {
    "openvas": BASE + ["cvss", "insight", "detection_result", "detection_method",
                       "product_detection_result", "log_method"],
    "qualys": BASE + ["category", "plugin"],
    "nessus": BASE + ["cvss", "insight", "detection_result", "plugin", "plugin_details"],
    "zap": BASE + ["plugin", "instances"],
}
SOURCE_FOR = {"openvas": "openvas-csv", "qualys": "qualys-csv",
              "nessus": "nessus-html", "zap": "zap-xml"}
STAMP = {"openvas": "OPENVAS", "qualys": "QUALYS", "nessus": "NESSUS", "zap": "ZAP"}


def cell(value):
    if isinstance(value, dict):
        return json.dumps(value) if value else ""
    if isinstance(value, list):
        return str(value) if value else ""
    return value


def main() -> None:
    cfg = json.loads((REPO / "heldout.json").read_text(encoding="utf-8"))
    factories = default_sources()

    for scanner, stems in cfg["heldout"].items():
        stems = set(stems)
        out_dir = REPO / "data" / "heldout" / scanner
        out_dir.mkdir(parents=True, exist_ok=True)
        fields = text_fields(scanner)
        trimmed: Counter = Counter()

        rows: dict[str, list[dict]] = defaultdict(list)
        pdf_dirs: dict[str, Path] = {}
        for ex in factories[SOURCE_FOR[scanner]]().examples():
            stem = Path(ex.source_id).stem
            if stem not in stems:
                continue
            if trim_target(ex.target, ex.block.text, fields, CONTAINMENT_MIN, trimmed):
                continue
            row = {c: cell(ex.target.get(c)) for c in COLUMNS[scanner]}
            row["host"] = ex.block.host
            row["source"] = STAMP[scanner]
            rows[stem].append(row)
            pdf_dirs[stem] = (REPO / "data" / "pdfs" if scanner == "openvas"
                              else TOOL / "resources" / scanner)

        for stem in sorted(stems):
            if not rows[stem]:
                raise SystemExit(f"{stem}: no examples produced; check the export/PDF pair")
            pd.DataFrame(rows[stem], columns=COLUMNS[scanner]).to_excel(
                out_dir / f"{stem}.xlsx", index=False)
            shutil.copy2(pdf_dirs[stem] / f"{stem}.pdf", out_dir / f"{stem}.pdf")
            print(f"{stem}: {len(rows[stem])} findings -> {out_dir / (stem + '.xlsx')}")
        if trimmed:
            print(f"  {scanner} trimmed paragraphs: {dict(trimmed)}")


if __name__ == "__main__":
    main()
