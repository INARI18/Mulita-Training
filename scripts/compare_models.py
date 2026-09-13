"""Aggregate held-out evaluations into one comparison table.

    python3 scripts/compare_models.py output_heldout/qwen2.5-1.5b \
        output_heldout/mulita-qwen2.5-1.5b-v4 output_heldout/deepseek

Every mean is printed with the share of pairs the model filled, because the
mean is taken only over pairs it answered: a model that skips the hard
findings scores higher on fewer of them. Restricts itself to the reports all
models share, and uses the newest run per report.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

FIELDS = ["description", "solution", "insight", "impact", "detection_result",
          "references", "severity", "instances", "plugin"]


def newest_runs(root: Path) -> dict[str, Path]:
    """Report stem -> its latest evaluation.json (dirs are timestamp-prefixed)."""
    found: dict[str, Path] = {}
    suffix = "_" + root.name
    for path in root.glob("*/*/evaluation.json"):
        # <timestamp>_<report stem>_<model key>
        stem = path.parent.name.split("_", 1)[1]
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
        if stem not in found or path.parent.name > found[stem].parent.name:
            found[stem] = path
    return found


def main(roots: list[Path]) -> None:
    runs = {r.name: newest_runs(r) for r in roots}
    shared = set.intersection(*(set(v) for v in runs.values()))
    for name, got in runs.items():
        if extra := set(got) - shared:
            print(f"note: {name} has {len(extra)} report(s) the others lack, excluded")
    print(f"\n{len(shared)} reports common to {len(roots)} models\n")

    stats: dict = defaultdict(dict)
    recall: dict = {}
    for name, got in runs.items():
        num, den, fill_n, fill_d = defaultdict(float), defaultdict(float), \
            defaultdict(float), defaultdict(float)
        matched = total = 0
        for stem in shared:
            data = json.loads(got[stem].read_text(encoding="utf-8"))
            matched += data["coverage"]["matched"]
            total += data["coverage"]["baseline_count"]
            for field, metrics in data["fields"].items():
                for metric, s in metrics.items():
                    if not isinstance(s, dict):
                        continue
                    if s.get("measured_mean") is not None:
                        num[field, metric] += s["measured_mean"] * (s.get("n_measured") or 0)
                        den[field, metric] += s.get("n_measured") or 0
                    if s.get("fill_rate_extraction") is not None:
                        fill_n[field] += s["fill_rate_extraction"] * (s.get("n") or 0)
                        fill_d[field] += s.get("n") or 0
        recall[name] = matched / total if total else None
        for key, d in den.items():
            if d:
                stats[key][name] = (num[key] / d, fill_n[key[0]] / fill_d[key[0]]
                                    if fill_d[key[0]] else None)

    names = [r.name for r in roots]
    width = max(len(n) for n in names) + 8
    print(f"{'field':<20}{'metric':<12}" + "".join(n.ljust(width) for n in names))
    print(f"{'-' * 20}{'-' * 12}" + "".join("-" * width for _ in names))
    for field in FIELDS:
        for metric in ("token_f1", "set_f1", "structural", "exact"):
            if (field, metric) not in stats:
                continue
            cells = []
            for name in names:
                got = stats[field, metric].get(name)
                cells.append("-".ljust(width) if not got else
                             f"{got[0]:.3f} ({got[1]:.2f})".ljust(width))
            print(f"{field:<20}{metric:<12}" + "".join(cells))
            break
    print(f"\n{'RECALL':<32}" + "".join(
        (f"{recall[n]:.3f}" if recall[n] is not None else "-").ljust(width) for n in names))
    print("\nmean (fill rate). The mean covers only the pairs a model answered.")


if __name__ == "__main__":
    main([Path(a) for a in sys.argv[1:]])
