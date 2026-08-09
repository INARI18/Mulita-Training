"""Build eval baselines for the held-out OpenVAS reports from the campaign CSV.

Reuses OpenVASCsvSource (the same gold mapping training uses) on the held-out
PDFs only, writing data/heldout/openvas/<stem>.xlsx + a copy of the PDF, ready
for `mulitaminer evaluate`. Machine-derived: replaces nothing in resources/.

  uv run --no-sync python ../mulita-extractor-training/src/make_heldout_baselines.py
"""
from __future__ import annotations

import json
import shutil
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402

from sources import OpenVASCsvSource  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

COLUMNS = ["Name", "description", "solution", "impact", "references", "severity",
           "host", "port", "protocol", "source", "cvss", "insight", "detection_result",
           "detection_method", "product_detection_result", "log_method"]


def cell(value):
    if isinstance(value, (list, dict)):
        return str(value) if value else ""
    return value


def main() -> None:
    cfg = json.loads((REPO / "heldout.json").read_text(encoding="utf-8"))
    stems = set(cfg["heldout"]["openvas"])
    out_dir = REPO / "data" / "heldout" / "openvas"
    out_dir.mkdir(parents=True, exist_ok=True)

    source = OpenVASCsvSource(REPO / "data" / "pdfs", REPO / "data" / "vulnnet_scans_openvas.csv")
    rows: dict[str, list[dict]] = defaultdict(list)
    for ex in source.examples():
        stem = Path(ex.source_id).stem
        if stem not in stems:
            continue
        row = {c: cell(ex.target.get(c)) for c in COLUMNS}
        row["host"] = ex.block.host
        row["source"] = "OPENVAS"
        rows[stem].append(row)

    for stem in sorted(stems):
        if not rows[stem]:
            raise SystemExit(f"{stem}: no examples produced; check the CSV/PDF pair")
        pd.DataFrame(rows[stem], columns=COLUMNS).to_excel(out_dir / f"{stem}.xlsx", index=False)
        shutil.copy2(REPO / "data" / "pdfs" / f"{stem}.pdf", out_dir / f"{stem}.pdf")
        print(f"{stem}: {len(rows[stem])} findings -> {out_dir / (stem + '.xlsx')}")


if __name__ == "__main__":
    main()
