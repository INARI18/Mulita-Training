"""1:1 pairing verification: each vulnnet PDF vs the OpenVAS CSV export.

The user's rule: nothing enters the dataset unless the PDF and the CSV agree
exactly, per host, with nothing extra or missing on either side. This script
produces that verdict per PDF, plus a QoD analysis (the OpenVAS PDF report
applies a QoD >= 70 filter by default, while CSV exports carry every row, so
a raw mismatch may be fully explained by QoD).

Verdicts per PDF:
  PERFECT            PDF findings == all CSV rows for that host/scan
  PERFECT_QOD70      PDF findings == CSV rows with QoD >= 70
  MISMATCH           anything else (details listed)
  NO_HOST / NO_BLOCKS  PDF unusable for pairing (listed)

Run from the MulitaMiner2 repo (uses its environment):
  uv run --no-sync python ../mulita-extractor-training/src/verify_pairing.py
"""
from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

import pandas as pd

from mulitaminer.pdf_reader import extract_pdf
from mulitaminer.scanner_engine import get_scanner

HERE = Path(__file__).resolve().parent.parent

# NVT name inside an OpenVAS block: the "NVT:" line, possibly wrapped onto
# following lines until a known section header starts.
NVT_RE = re.compile(r"^NVT:\s*(.*)$")
SECTION_RE = re.compile(
    r"^(Summary|Impact|Solution|Vulnerability Detection Result|"
    r"Vulnerability Insight|Vulnerability Detection Method|"
    r"Product Detection Result|Log Method|References|Affected Software|"
    r"OID|CVSS|Quality of Detection)\b",
    re.IGNORECASE,
)

# Report-furniture lines that can follow a (wrapped) NVT name: the per-host
# results index ("2 results per host 10") and bare page/count lines.
FURNITURE_RE = re.compile(r"^\d+\s+results?\b|^\d+\s*$", re.IGNORECASE)


def norm_name(name: str) -> str:
    """Alphanumeric squeeze: the comparison key.

    PDF text carries rendering artifacts the CSV does not (broken ligatures
    like ￾ inside words, hyphens lost/kept at line wraps, quote style).
    Dropping everything but [a-z0-9] makes the key immune to all of them
    while staying plenty distinctive for these long NVT titles.
    """
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def pdf_findings(pdf_path: Path, profile) -> tuple[str | None, Counter]:
    """-> (host, Counter of normalized NVT names)."""
    doc = extract_pdf(pdf_path)
    blocks = profile.segment(doc.text)
    names: list[str] = []
    hosts = set()
    for block in blocks:
        if block.host:
            hosts.add(block.host)
        lines = block.text.splitlines()
        for i, line in enumerate(lines):
            m = NVT_RE.match(line.strip())
            if not m:
                continue
            name = m.group(1).strip()
            # Wrapped title: keep appending lines until a section header.
            for cont in lines[i + 1:]:
                cont = cont.strip()
                if not cont or SECTION_RE.match(cont) or FURNITURE_RE.match(cont):
                    break
                name += " " + cont
            names.append(norm_name(name))
            break
    host = hosts.pop() if len(hosts) == 1 else (None if not hosts else sorted(hosts)[0])
    return host, Counter(names)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", type=Path, default=HERE / "data" / "vulnnet_scans_openvas.csv")
    parser.add_argument("--pdfs", type=Path, default=HERE / "data" / "pdfs")
    parser.add_argument("--out", type=Path, default=HERE / "data" / "pairing_report.md")
    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df["name_norm"] = df["NVT Name"].map(norm_name)
    profile = get_scanner("openvas")

    lines = ["# PDF vs CSV pairing report", ""]
    verdicts: Counter = Counter()
    matched_hosts: set[str] = set()

    for pdf_path in sorted(args.pdfs.glob("*.pdf")):
        host, pdf_counts = pdf_findings(pdf_path, profile)
        n_pdf = sum(pdf_counts.values())
        if n_pdf == 0:
            verdicts["NO_BLOCKS"] += 1
            lines.append(f"- `{pdf_path.name}`: **NO_BLOCKS**")
            continue
        if host is None:
            verdicts["NO_HOST"] += 1
            lines.append(f"- `{pdf_path.name}`: **NO_HOST** ({n_pdf} findings)")
            continue

        rows = df[df["IP"] == host]
        matched_hosts.add(host)
        csv_all = Counter(rows["name_norm"])
        csv_q70 = Counter(rows[rows["QoD"] >= 70]["name_norm"])

        if pdf_counts == csv_all:
            verdicts["PERFECT"] += 1
            lines.append(f"- `{pdf_path.name}` ({host}): **PERFECT** ({n_pdf})")
            continue
        if pdf_counts == csv_q70:
            verdicts["PERFECT_QOD70"] += 1
            lines.append(
                f"- `{pdf_path.name}` ({host}): **PERFECT_QOD70** "
                f"({n_pdf} == QoD>=70 rows; CSV total {sum(csv_all.values())})"
            )
            continue

        verdicts["MISMATCH"] += 1
        # Diff against whichever CSV view is closer (full export vs QoD>=70),
        # so the report shows the true discrepancies, not the QoD tail.
        def _delta(ref: Counter) -> int:
            return sum((ref - pdf_counts).values()) + sum((pdf_counts - ref).values())

        ref_name, ref = min(
            (("csv_all", csv_all), ("csv_q70", csv_q70)), key=lambda t: _delta(t[1])
        )
        missing = ref - pdf_counts
        extra = pdf_counts - ref
        lines.append(
            f"- `{pdf_path.name}` ({host}): **MISMATCH vs {ref_name}** pdf={n_pdf} "
            f"csv_all={sum(csv_all.values())} csv_q70={sum(csv_q70.values())} "
            f"(diff {_delta(ref)})"
        )
        for name, count in sorted(missing.items()):
            lines.append(f"    - missing in PDF ({count}x): {name[:90]}")
        for name, count in sorted(extra.items()):
            lines.append(f"    - extra in PDF ({count}x): {name[:90]}")

    csv_hosts = set(df["IP"].unique())
    unpaired_csv = sorted(csv_hosts - matched_hosts)
    summary = [
        "",
        "## Summary",
        "",
        *[f"- {k}: {v}" for k, v in sorted(verdicts.items())],
        f"- CSV hosts never claimed by any PDF: {len(unpaired_csv)}"
        + (f" ({', '.join(unpaired_csv[:10])}{'...' if len(unpaired_csv) > 10 else ''})"
           if unpaired_csv else ""),
    ]
    lines += summary

    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(summary[2:]))
    print(f"\nFull report: {args.out}")


if __name__ == "__main__":
    main()
