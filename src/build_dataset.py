"""Assemble the training dataset from the labeled blocks.

Each example is one PDF block (model INPUT, rendered exactly as the tool sends
it) paired with its CSV-derived label (TARGET). Three guards run before an
example is admitted:

1. Contamination guard: the tool's evaluation baselines (hosts and report
   stems under MulitaMiner2/resources/) may never enter training. The vulnnet
   hosts are disjoint from them, so this is a sanity gate that aborts loudly
   if that ever stops being true.
2. Containment gate: every non-empty label field's tokens must be present in
   the block text above a threshold. A field that fails would teach the model
   to emit text absent from its input (hallucination) — the example is
   dropped and counted.
3. Schema validity: guaranteed upstream by row_to_target (validated through
   extraction_model_for).

Output: train.jsonl / val.jsonl in chat format
({"messages":[system, user, assistant]}) plus dataset_report.md.

Run from the MulitaMiner2 repo (uses its environment and prompt):
  uv run --no-sync python ../mulita-extractor-training/src/build_dataset.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from mulitaminer.extraction import render_block
from mulitaminer.scanner_engine import get_scanner

from label_from_csv import iter_labeled_blocks, norm_key

HERE = Path(__file__).resolve().parent.parent
TOOL = HERE.parent / "MulitaMiner2"

TOKEN_RE = re.compile(r"[a-z0-9]+")
CONTAINMENT_MIN = 0.80  # per-field token containment floor for admission

# Fields whose text must be contained in the block (references excluded: it is
# built FROM the block by construction; structured fields are not text).
_CONTAINED_FIELDS = ("description", "solution", "impact", "insight",
                     "detection_result", "detection_method",
                     "product_detection_result")


def _tokens(value) -> Counter:
    if isinstance(value, list):
        value = " ".join(str(v) for v in value)
    cleaned = str(value).replace("￾", "").replace("﻿", "")
    return Counter(TOKEN_RE.findall(cleaned.lower()))


def _containment(field_tokens: Counter, block_tokens: Counter) -> float:
    total = sum(field_tokens.values())
    if total == 0:
        return 1.0
    return sum((field_tokens & block_tokens).values()) / total


def _baseline_identity(resources: Path) -> tuple[set[str], set[str]]:
    """Report stems and baseline hosts that must never appear in training."""
    stems = {p.stem.lower() for p in resources.rglob("*.pdf")}
    hosts: set[str] = set()
    try:
        import pandas as pd

        for xlsx in resources.rglob("*.xlsx"):
            df = pd.read_excel(xlsx)
            for col in ("host", "Host", "IP"):
                if col in df.columns:
                    hosts |= {str(h).strip() for h in df[col].dropna()}
    except Exception:
        pass
    return stems, hosts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdfs", type=Path, default=HERE / "data" / "pdfs")
    parser.add_argument("--csv", type=Path, default=HERE / "data" / "vulnnet_scans_openvas.csv")
    parser.add_argument("--out", type=Path, default=HERE / "data" / "dataset")
    parser.add_argument("--val-frac", type=float, default=0.1)
    args = parser.parse_args()

    profile = get_scanner("openvas")
    system_prompt = profile.prompt()
    deny_stems, deny_hosts = _baseline_identity(TOOL / "resources")

    args.out.mkdir(parents=True, exist_ok=True)
    examples: list[dict] = []
    dropped: Counter = Counter()
    field_fill: Counter = Counter()

    for pdf_path, block, target in iter_labeled_blocks(args.pdfs, args.csv):
        if pdf_path.stem.lower() in deny_stems or (block.host in deny_hosts):
            raise SystemExit(
                f"CONTAMINATION: {pdf_path.name} (host {block.host}) overlaps an "
                f"evaluation baseline. Training must never see it."
            )

        block_tokens = _tokens(block.text)
        bad_field = None
        for field in _CONTAINED_FIELDS:
            if target.get(field) and _containment(_tokens(target[field]), block_tokens) < CONTAINMENT_MIN:
                bad_field = field
                break
        if bad_field:
            dropped[bad_field] += 1
            continue

        for field, value in target.items():
            if value not in (None, [], {}, ""):
                field_fill[field] += 1

        user = render_block(block)
        assistant = json.dumps({"items": [target]}, ensure_ascii=False)
        examples.append({
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant},
            ],
            "_source": pdf_path.name,
        })

    # Deterministic split by a hash of the source+content (no run-to-run drift).
    def _bucket(ex: dict) -> float:
        h = hashlib.sha256(json.dumps(ex["messages"], sort_keys=True).encode()).hexdigest()
        return int(h[:8], 16) / 0xFFFFFFFF

    train, val = [], []
    for ex in examples:
        (val if _bucket(ex) < args.val_frac else train).append(ex)

    for name, rows in (("train", train), ("val", val)):
        with (args.out / f"{name}.jsonl").open("w", encoding="utf-8") as fh:
            for ex in rows:
                fh.write(json.dumps({"messages": ex["messages"]}, ensure_ascii=False) + "\n")

    report = [
        "# Training dataset report", "",
        f"- examples admitted: {len(examples)} (train {len(train)}, val {len(val)})",
        f"- dropped (field not contained in block): {sum(dropped.values())} "
        + (f"({dict(dropped)})" if dropped else ""),
        f"- source reports: {len({ex['_source'] for ex in examples})}",
        f"- contamination guard: {len(deny_stems)} baseline stems, "
        f"{len(deny_hosts)} baseline hosts denied",
        "", "## Field fill rate (of admitted examples)", "",
    ]
    for field, n in field_fill.most_common():
        report.append(f"- {field}: {n} ({n / len(examples):.0%})")
    (args.out / "dataset_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    print("\n".join(report[1:8]))
    print(f"\nWrote {args.out}/train.jsonl, val.jsonl, dataset_report.md")


if __name__ == "__main__":
    main()
