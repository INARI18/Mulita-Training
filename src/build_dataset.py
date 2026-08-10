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

from mulitaminer.chunking import pack  # noqa: E402
from mulitaminer.evaluation.fields import field_plans  # noqa: E402
from mulitaminer.extraction import render_chunk  # noqa: E402
from mulitaminer.scanner_engine import get_scanner  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO.parent / "MulitaMiner2"
CONTAINMENT_MIN = 0.80
# mirrors production packing: profile.max_vulns_per_chunk blocks under the
# serving profiles' max_output_tokens budget
TRAIN_TOKEN_BUDGET = 8000


def text_fields(scanner: str) -> list[str]:
    profile = get_scanner(scanner)
    overrides = dict(profile.field_metric_overrides)
    return [p.name for p in field_plans(profile.record_type)
            if overrides.get(p.name, p.metric) == "text"]


def trim_target(target: dict, block_text: str, fields, cmin: float, trimmed: Counter) -> str | None:
    """Keep only label content present in the input block. List fields lose the
    non-contained paragraphs (exports can carry text the PDF never renders);
    a non-contained scalar field rejects the example (returns the field name)."""
    block_tokens = tokens(block_text)
    for f in fields:
        value = target.get(f)
        if not value:
            continue
        if isinstance(value, list):
            kept = [p for p in value if containment(tokens(p), block_tokens) >= cmin]
            if len(kept) != len(value):
                trimmed[f] += len(value) - len(kept)
                target[f] = kept
        elif containment(tokens(value), block_tokens) < cmin:
            return f
    return None


def eval_identity(repo: Path) -> tuple[set[str], set[str]]:
    """Denied stems + eval-only hosts from heldout.json (see its comment)."""
    cfg = json.loads((repo / "heldout.json").read_text(encoding="utf-8"))
    stems = {s.lower() for stems in cfg["heldout"].values() for s in stems}
    stems |= {s.lower() for s in cfg["denied_stems"]}
    return stems, set(cfg["eval_only_hosts"])


def assemble(sources, out_dir: Path, val_frac: float, cmin: float,
             shape: str = "chunked") -> None:
    deny_stems, deny_hosts = eval_identity(REPO)
    tf_cache: dict[str, list[str]] = {}
    prompts: dict[str, str] = {}
    examples: list[dict] = []
    dropped: Counter = Counter()
    denied: Counter = Counter()
    trimmed: Counter = Counter()
    fill: Counter = Counter()

    by_report: dict[tuple[str, str], dict[int, object]] = {}
    for source in sources:
        for ex in source.examples():
            if Path(ex.source_id).stem.lower() in deny_stems:
                denied["stem"] += 1
                continue
            if ex.block.host in deny_hosts:
                denied["host"] += 1
                continue

            fields = tf_cache.setdefault(ex.scanner, text_fields(ex.scanner))
            bad = trim_target(ex.target, ex.block.text, fields, cmin, trimmed)
            if bad:
                dropped[bad] += 1
                continue

            for field, value in ex.target.items():
                if value not in (None, [], {}, ""):
                    fill[field] += 1
            # first gold wins on duplicate block matches within a report
            by_report.setdefault((ex.scanner, ex.source_id), {}).setdefault(ex.block.id, ex)

    # shapes: "chunked" = production packing (N blocks -> N items, the tool's
    # own chunker); "single" = one block per call (items of length 1);
    # "mixed" = both, interleaved by the trainer's shuffle
    n_records = 0

    def emit(scanner, source_id, prompt, blocks, targets):
        examples.append({
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": render_chunk(blocks)},
                {"role": "assistant",
                 "content": json.dumps({"items": targets}, ensure_ascii=False)},
            ],
            "_source": source_id,
            "_scanner": scanner,
        })

    for (scanner, source_id), by_id in by_report.items():
        prompt = prompts.setdefault(scanner, get_scanner(scanner).prompt())
        ordered = [by_id[i] for i in sorted(by_id)]
        n_records += len(ordered)
        if shape in ("single", "mixed"):
            for e in ordered:
                emit(scanner, source_id, prompt, [e.block], [e.target])
        if shape in ("chunked", "mixed"):
            chunks, _ = pack(
                [e.block for e in ordered],
                max_blocks_per_chunk=get_scanner(scanner).max_vulns_per_chunk,
                token_budget=TRAIN_TOKEN_BUDGET,
            )
            for chunk in chunks:
                emit(scanner, source_id, prompt, chunk.blocks,
                     [by_id[b.id].target for b in chunk.blocks])

    _write(out_dir, examples, val_frac, dropped, denied, trimmed, fill, prompts,
           deny_stems, deny_hosts, n_records)


def _write(out_dir, examples, val_frac, dropped, denied, trimmed, fill, prompts,
           deny_stems, deny_hosts, n_records):
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
        f"- examples admitted: {len(examples)} chunks / {n_records} records "
        f"(train {len(train)}, val {len(val)} chunks)",
        f"- per scanner (chunks): {dict(per_scanner)}",
        f"- dropped (scalar field not contained): {sum(dropped.values())}"
        + (f" {dict(dropped)}" if dropped else ""),
        f"- trimmed paragraphs (not rendered in the PDF): {sum(trimmed.values())}"
        + (f" {dict(trimmed)}" if trimmed else ""),
        f"- source reports: {len({ex['_source'] for ex in examples})}",
        f"- contamination guard: {len(deny_stems)} stems, {len(deny_hosts)} eval-only hosts; "
        f"denied examples: {dict(denied) or 0}",
        f"- prompt snapshots: {prompt_hashes}",
        "", "## Field fill rate", "",
        *[f"- {f}: {n} ({n / max(n_records, 1):.0%})" for f, n in fill.most_common()],
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
    parser.add_argument("--shape", default="chunked", choices=["single", "chunked", "mixed"])
    parser.add_argument("--out", type=Path, default=REPO / "data" / "dataset")
    parser.add_argument("--val-frac", type=float, default=0.1)
    args = parser.parse_args()

    factories = default_sources()
    names = sorted(factories) if args.sources == "all" else args.sources.split(",")
    assemble([factories[n]() for n in names], args.out, args.val_frac,
             CONTAINMENT_MIN, args.shape)


if __name__ == "__main__":
    main()
