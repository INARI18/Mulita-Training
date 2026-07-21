"""Assemble training data from any LabelSource.

Scanner-agnostic: each Example carries which scanner renders its input, so the
system prompt, block rendering and text-field set all derive from the tool.
Guards before admission: contamination (eval baselines never enter), field
containment (labels must be present in the input), schema validity (upstream).

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
    record_type = get_scanner(scanner).record_type
    return [p.name for p in field_plans(record_type) if p.metric == "text"]


def baseline_identity(resources: Path) -> tuple[set[str], set[str]]:
    stems = {p.stem.lower() for p in resources.rglob("*.pdf")}
    hosts: set[str] = set()
    import pandas as pd

    for xlsx in resources.rglob("*.xlsx"):
        try:
            df = pd.read_excel(xlsx)
        except Exception:
            continue
        for col in ("host", "Host", "IP"):
            if col in df.columns:
                hosts |= {str(h).strip() for h in df[col].dropna()}
    return stems, hosts


def assemble(sources, out_dir: Path, val_frac: float, cmin: float) -> None:
    deny_stems, deny_hosts = baseline_identity(TOOL / "resources")
    tf_cache: dict[str, list[str]] = {}
    prompts: dict[str, str] = {}
    examples: list[dict] = []
    dropped: Counter = Counter()
    fill: Counter = Counter()

    for source in sources:
        for ex in source.examples():
            if Path(ex.source_id).stem.lower() in deny_stems or ex.block.host in deny_hosts:
                raise SystemExit(
                    f"CONTAMINATION: {ex.source_id} (host {ex.block.host}) "
                    f"overlaps an evaluation baseline."
                )

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
            })

    _write(out_dir, examples, val_frac, dropped, fill, prompts, deny_stems, deny_hosts)


def _write(out_dir, examples, val_frac, dropped, fill, prompts, deny_stems, deny_hosts):
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

    report = [
        "# Training dataset report", "",
        f"- examples admitted: {len(examples)} (train {len(train)}, val {len(val)})",
        f"- dropped (field not contained): {sum(dropped.values())}"
        + (f" {dict(dropped)}" if dropped else ""),
        f"- source reports: {len({ex['_source'] for ex in examples})}",
        f"- contamination guard: {len(deny_stems)} baseline stems, "
        f"{len(deny_hosts)} baseline hosts denied",
        f"- prompt snapshots: {prompt_hashes}",
        "", "## Field fill rate", "",
        *[f"- {f}: {n} ({n / max(len(examples), 1):.0%})" for f, n in fill.most_common()],
    ]
    (out_dir / "dataset_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report[1:9]))
    print(f"\nWrote {out_dir}/train.jsonl, val.jsonl, prompts/, dataset_report.md")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="openvas-csv", choices=sorted(SOURCES))
    parser.add_argument("--pdfs", type=Path, default=REPO / "data" / "pdfs")
    parser.add_argument("--csv", type=Path, default=REPO / "data" / "vulnnet_scans_openvas.csv")
    parser.add_argument("--out", type=Path, default=REPO / "data" / "dataset")
    parser.add_argument("--val-frac", type=float, default=0.1)
    args = parser.parse_args()

    source = SOURCES[args.source](args.pdfs, args.csv)
    assemble([source], args.out, args.val_frac, CONTAINMENT_MIN)


if __name__ == "__main__":
    main()
