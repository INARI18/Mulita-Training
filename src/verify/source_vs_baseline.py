"""Cross-check a label source against the eval xlsx derived from the same export.

The resources/ xlsx baselines encode the export->record mapping already used by
evaluation; a new LabelSource must reproduce it. For every report that has an
xlsx, pair source targets to xlsx rows and report per-field agreement
(normalized-text equality), printing sample mismatches.

  uv run --no-sync python ../mulita-extractor-training/src/verify/source_vs_baseline.py qualys-csv
"""
from __future__ import annotations

import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from common import blank, norm_key  # noqa: E402
from build_dataset import default_sources  # noqa: E402

TOOL = Path(__file__).resolve().parents[2].parent / "MulitaMiner2"
SKIP = {"block_id", "source", "host"}  # not produced or pipeline-owned


def norm(value) -> str:
    if isinstance(value, str) and value[:1] in "[{":
        try:  # stringified list/dict cells: compare content, not repr escapes
            value = __import__("ast").literal_eval(value)
        except (ValueError, SyntaxError):
            try:
                value = __import__("json").loads(value)
            except ValueError:
                pass
    if isinstance(value, list):
        return norm_key(" ".join(str(v) for v in value))
    if isinstance(value, dict):
        return norm_key(" ".join(f"{k} {v}" for k, v in sorted(value.items()) if v))
    if blank(value):
        return ""
    if isinstance(value, float) and value == int(value):
        value = int(value)  # xlsx floats: 21.0 == 21
    return norm_key(value)


def main() -> None:
    name = sys.argv[1]
    source = default_sources()[name]()
    by_report: dict[str, list] = defaultdict(list)
    for ex in source.examples():
        by_report[Path(ex.source_id).stem].append(ex.target)

    for stem, targets in sorted(by_report.items()):
        xlsx = next(TOOL.glob(f"resources/*/{stem}.xlsx"), None)
        if xlsx is None:
            print(f"{stem}: no xlsx, skipped")
            continue
        df = pd.read_excel(xlsx)
        key = "plugin" if "plugin" in df.columns else "Name"
        rows = defaultdict(list)
        for _, r in df.iterrows():
            rows[norm(r[key])].append(r)

        agree: Counter = Counter()
        seen: Counter = Counter()
        samples: list[str] = []
        matched = 0
        for t in targets:
            pool = rows.get(norm(t.get(key) or t.get("Name")))
            if not pool:
                continue
            row = pool.pop(0)
            matched += 1
            for field, value in t.items():
                if field in SKIP or field not in df.columns:
                    continue
                seen[field] += 1
                if norm(value) == norm(row[field]):
                    agree[field] += 1
                elif len(samples) < 8:
                    samples.append(f"  [{field}] {stem}#{t['block_id']}\n"
                                   f"    src: {str(value)[:110]}\n"
                                   f"    xls: {str(row[field])[:110]}")

        print(f"{stem}: {matched}/{len(targets)} matched vs {len(df)} xlsx rows")
        for field in sorted(seen):
            pct = agree[field] / seen[field]
            flag = "" if pct >= 0.98 else "  <-- CHECK"
            print(f"  {field}: {agree[field]}/{seen[field]} ({pct:.0%}){flag}")
        if samples:
            print("\n".join(samples))


if __name__ == "__main__":
    main()
