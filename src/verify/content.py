"""Field-content containment check: is every CSV field's text present in the
paired PDF block?

Training labels must be contained in the model's input. For each paired
finding (host + normalized NVT name, from the 1:1 verification), this
measures per-field token containment: the fraction of the CSV field's tokens
that appear in the PDF block's text. A field with low containment would
teach the model to generate text absent from its input, which is exactly
the "ensinar errado" failure mode to avoid.

Run from the MulitaMiner2 repo:
  uv run --no-sync python ../mulita-extractor-training/src/content_check.py
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from mulitaminer.pdf_reader import extract_pdf  # noqa: E402
from mulitaminer.scanner_engine import get_scanner  # noqa: E402

from common import norm_key as key_name, tokens  # noqa: E402

HERE = Path(__file__).resolve().parents[2]
NVT_RE = re.compile(r"^NVT:\s*(.*)$")

# CSV column -> short report label.
FIELDS = {
    "Summary": "summary",
    "Impact": "impact",
    "Solution": "solution",
    "Vulnerability Insight": "insight",
    "Specific Result": "detection_result",
    "Vulnerability Detection Method": "detection_method",
    "Product Detection Result": "product_detection",
    "Affected Software/OS": "affected",
    "CVEs": "cves",
    "BIDs": "bids",
    "Other References": "other_refs",
    "CERTs": "certs",
}


def containment(field_tokens: Counter, block_tokens: Counter) -> float | None:
    """None for an empty field (excluded from stats), else the hit fraction."""
    total = sum(field_tokens.values())
    return sum((field_tokens & block_tokens).values()) / total if total else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=HERE / "data" / "vulnnet_scans_openvas.csv")
    parser.add_argument("--pdfs", type=Path, default=HERE / "data" / "pdfs")
    parser.add_argument("--out", type=Path, default=HERE / "data" / "content_report.md")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df["key"] = df["NVT Name"].map(key_name)
    profile = get_scanner("openvas")

    # scores[label] -> list of (ratio, pdf, name) ; absent[label] -> count of empty fields
    scores: dict[str, list] = defaultdict(list)
    n_pairs = 0

    for pdf_path in sorted(args.pdfs.glob("*.pdf")):
        doc = extract_pdf(pdf_path)
        blocks = profile.segment(doc.text)
        by_key: dict[str, list] = defaultdict(list)
        host = None
        for block in blocks:
            host = block.host or host
            for line in block.text.splitlines():
                m = NVT_RE.match(line.strip())
                if m:
                    by_key[key_name(m.group(1))].append(block)
                    break
        if host is None:
            continue
        rows = df[df["IP"] == host]
        for _, row in rows.iterrows():
            candidates = by_key.get(row["key"]) or [
                b for k, blks in by_key.items() if k.startswith(row["key"][:40]) for b in blks
            ]
            if not candidates:
                continue
            # Duplicate names on a host: pick the block whose text best
            # contains this row's Specific Result (port-specific content).
            if len(candidates) > 1:
                sr = tokens(row.get("Specific Result"))
                candidates = sorted(
                    candidates,
                    key=lambda b: -(containment(sr, tokens(b.text)) or 0.0),
                )
            block_tokens = tokens(candidates[0].text)
            n_pairs += 1
            for column, label in FIELDS.items():
                ratio = containment(tokens(row.get(column)), block_tokens)
                if ratio is not None:
                    scores[label].append((ratio, pdf_path.name, str(row["NVT Name"])[:60]))

    lines = ["# CSV field containment in PDF blocks", "", f"Paired findings: {n_pairs}", ""]
    lines.append("| field | n filled | mean | >=0.90 | >=0.99 | min |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    print(f"paired findings: {n_pairs}")
    for label in FIELDS.values():
        vals = scores.get(label)
        if not vals:
            lines.append(f"| {label} | 0 | - | - | - | - |")
            continue
        ratios = [v[0] for v in vals]
        mean = sum(ratios) / len(ratios)
        p90 = sum(r >= 0.90 for r in ratios) / len(ratios)
        p99 = sum(r >= 0.99 for r in ratios) / len(ratios)
        lines.append(
            f"| {label} | {len(ratios)} | {mean:.3f} | {p90:.1%} | {p99:.1%} | {min(ratios):.3f} |"
        )
        print(f"{label:<18} n={len(ratios):<5} mean={mean:.3f} >=0.90:{p90:.1%} min={min(ratios):.3f}")

    lines += ["", "## Worst cases per field (up to 3)", ""]
    for label, vals in scores.items():
        for ratio, pdf, name in sorted(vals)[:3]:
            if ratio < 0.90:
                lines.append(f"- {label} {ratio:.2f} `{pdf}` {name}")

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nFull report: {args.out}")


if __name__ == "__main__":
    main()
