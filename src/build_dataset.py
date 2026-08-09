"""Assemble training data from any LabelSource.

Scanner-agnostic: each Example carries which scanner renders its input, so the
system prompt, block rendering and text-field set all derive from the tool.
Guards before admission: contamination (heldout.json: held-out stems, denied
stems, eval-only hosts), field containment (labels must be present in the
input), schema validity (upstream).

Provenance: the exact prompt text used per scanner is snapshotted into the
output, so a trained artifact records the prompt it was trained against.

  uv run --no-sync python ../mulita-extractor-training/src/build_dataset.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import containment, tokens  # noqa: E402
from sources import SOURCES  # noqa: E402

from mulitaminer.evaluation.fields import field_plans  # noqa: E402
from mulitaminer.extraction import render_block  # noqa: E402
from mulitaminer.scanner_engine import get_scanner  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO.parent / "MulitaMiner2"
CONTAINMENT_MIN = 0.80


def text_fields(scanner: str) -> list[str]:
    profile = get_scanner(scanner)
    overrides = dict(profile.field_metric_overrides)
    return [p.name for p in field_plans(profile.record_type)
            if overrides.get(p.name, p.metric) == "text"]


def eval_identity(repo: Path) -> tuple[set[str], set[str]]:
    """Denied stems + eval-only hosts from heldout.json (see its comment)."""
    cfg = json.loads((repo / "heldout.json").read_text(encoding="utf-8"))
    stems = {s.lower() for stems in cfg["heldout"].values() for s in stems}
    stems |= {s.lower() for s in cfg["denied_stems"]}
    return stems, set(cfg["eval_only_hosts"])


def assemble(sources, out_dir: Path, val_frac: float, cmin: float) -> None:
    deny_stems, deny_hosts = eval_identity(REPO)
    tf_cache: dict[str, list[str]] = {}
    prompts: dict[str, str] = {}
    examples: list[dict] = []
    dropped: Counter = Counter()
    denied: Counter = Counter()
    fill: Counter = Counter()

    for source in sources:
        for ex in source.examples():
            if Path(ex.source_id).stem.lower() in deny_stems:
                denied["stem"] += 1
                continue
            if ex.block.host in deny_hosts:
                denied["host"] += 1
                continue

            fields = tf_cache.setdefault(ex.scanner, text_fields(ex.scanner))
            block_tokens = tokens(ex.block.text)
            bad = next(
                (f for f in fields if ex.target.get(f)
                 and containment(tokens(ex.target[f]), block_tokens) < cmin),
                None,
            )
            if bad:
                dropped[bad] += 1
                continue

            for field, value in ex.target.items():
                if value not in (None, [], {}, ""):
                    fill[field] += 1
            prompt = prompts.setdefault(ex.scanner, get_scanner(ex.scanner).prompt())
            examples.append({
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": render_block(ex.block)},
                    {"role": "assistant",
                     "content": json.dumps({"items": [ex.target]}, ensure_ascii=False)},
                ],
                "_source": ex.source_id,
                "_scanner": ex.scanner,
            })

    _write(out_dir, examples, val_frac, dropped, denied, fill, prompts, deny_stems, deny_hosts)


def _write(out_dir, examples, val_frac, dropped, denied, fill, prompts, deny_stems, deny_hosts):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prompts").mkdir(exist_ok=True)
    prompt_hashes = {}
    for scanner, text in prompts.items():
        (out_dir / "prompts" / f"{scanner}.txt").write_text(text, encoding="utf-8")
        prompt_hashes[scanner] = hashlib.sha256(text.encode()).hexdigest()[:12]

    def bucket(ex: dict) -> float:
        h = hashlib.sha256(json.dumps(ex["messages"], sort_keys=True).encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    train = [ex for ex in examples if bucket(ex) >= val_frac]
    val = [ex for ex in examples if bucket(ex) < val_frac]
    for name, rows in (("train", train), ("val", val)):
        with (out_dir / f"{name}.jsonl").open("w", encoding="utf-8") as fh:
            for ex in rows:
                fh.write(json.dumps({"messages": ex["messages"]}, ensure_ascii=False) + "\n")

    per_scanner = Counter(ex["_scanner"] for ex in examples)
    report = [
        "# Training dataset report", "",
        f"- examples admitted: {len(examples)} (train {len(train)}, val {len(val)})",
        f"- per scanner: {dict(per_scanner)}",
        f"- dropped (field not contained): {sum(dropped.values())}"
        + (f" {dict(dropped)}" if dropped else ""),
        f"- source reports: {len({ex['_source'] for ex in examples})}",
        f"- contamination guard: {len(deny_stems)} stems, {len(deny_hosts)} eval-only hosts; "
        f"denied examples: {dict(denied) or 0}",
        f"- prompt snapshots: {prompt_hashes}",
        "", "## Field fill rate", "",
        *[f"- {f}: {n} ({n / max(len(examples), 1):.0%})" for f, n in fill.most_common()],
    ]
    (out_dir / "dataset_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[1:9]))
    print(f"\nWrote {out_dir}/train.jsonl, val.jsonl, prompts/, dataset_report.md")


def default_sources() -> dict:
    return {
        "openvas-csv": lambda: SOURCES["openvas-csv"](
            REPO / "data" / "pdfs", REPO / "data" / "vulnnet_scans_openvas.csv"),
        "qualys-csv": lambda: SOURCES["qualys-csv"](TOOL / "resources" / "qualys"),
        "nessus-html": lambda: SOURCES["nessus-html"](TOOL / "resources" / "nessus"),
        "zap-xml": lambda: SOURCES["zap-xml"](TOOL / "resources" / "zap"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", default="all",
                        help="'all' or comma list of: " + ",".join(sorted(SOURCES)))
    parser.add_argument("--out", type=Path, default=REPO / "data" / "dataset")
    parser.add_argument("--val-frac", type=float, default=0.1)
    args = parser.parse_args()

    factories = default_sources()
    names = sorted(factories) if args.sources == "all" else args.sources.split(",")
    assemble([factories[n]() for n in names], args.out, args.val_frac, CONTAINMENT_MIN)


if __name__ == "__main__":
    main()
