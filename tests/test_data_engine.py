"""Unit tests for the training data engine (references, mapping, assembly)."""
import pandas as pd
import pytest

from references_from_pdf import build_references
from label_from_csv import norm_key, row_to_target
from build_dataset import _containment, _tokens


# --- references_from_pdf -----------------------------------------------------


def test_references_strips_labels_and_keeps_urls():
    block = (
        "Some Finding\n"
        "References\n"
        "cve: CVE-2016-5770\n"
        "cve: CVE-2016-5771\n"
        "url: http://www.php.net/ChangeLog-5.php\n"
        "cert-bund: CB-K16/2012\n"
    )
    assert build_references(block) == [
        "CVE-2016-5770", "CVE-2016-5771",
        "http://www.php.net/ChangeLog-5.php", "CB-K16/2012",
    ]


def test_references_bare_url_and_dedup():
    block = "References\nhttps://a.example/x\nurl: https://a.example/x\n"
    assert build_references(block) == ["https://a.example/x"]


def test_references_skips_empty_and_stops_at_section():
    block = "References\ncve: -\nother:\nurl: https://ok.example/1\nSummary\ntext\n"
    assert build_references(block) == ["https://ok.example/1"]


def test_references_absent_header():
    assert build_references("Just a finding with no refs section") == []


# --- label_from_csv ----------------------------------------------------------


def _row(**over) -> pd.Series:
    base = {
        "NVT Name": "PHP End of Life (EOL) Detection - Linux",
        "Summary": "The PHP version has reached end of life.\n\nSecond paragraph here.",
        "Solution": "Update PHP to a supported version.",
        "Impact": "An EOL version receives no security updates.",
        "Vulnerability Insight": "",
        "Specific Result": "Installed version: 5.5.9",
        "Vulnerability Detection Method": "Checks the installed version.",
        "Product Detection Result": "cpe:/a:php:php:5.5.9",
        "CVSS": 10.0,
        "Severity": "Critical",
        "Port": 80,
        "Port Protocol": "tcp",
    }
    base.update(over)
    return pd.Series(base)


def test_row_to_target_shape_and_types():
    block = "High (CVSS: 10.0)\nNVT: PHP End of Life\nReferences\ncve: CVE-2016-5770\n"
    t = row_to_target(_row(), block, block_id=3)
    assert t["block_id"] == 3
    assert t["Name"].startswith("PHP End of Life")
    assert t["description"] == ["The PHP version has reached end of life.",
                                "Second paragraph here."]
    assert t["cvss"] == 10.0 and t["severity"] == "CRITICAL"
    assert t["port"] == 80 and t["protocol"] == "tcp"
    assert t["insight"] == []  # blank cell -> empty list
    assert t["references"] == ["CVE-2016-5770"]  # from the block, not the row
    assert t["plugin"] is None and t["plugin_details"] == {} and t["instances"] == []


def test_row_to_target_rejects_bad_severity():
    with pytest.raises(Exception):
        row_to_target(_row(Severity="Bogus"), "NVT: x", 0)


def test_norm_key_immune_to_artifacts():
    # broken ligature + hyphen wrap collapse to the same key
    assert norm_key("Apache 2.4 mod_proxy") == norm_key("Apache 2.4 mod￾_proxy")


# --- build_dataset guards ----------------------------------------------------


def test_containment_detects_absent_text():
    block = _tokens("the server runs php 5.5.9 and is end of life")
    assert _containment(_tokens("php 5.5.9 end of life"), block) == 1.0
    assert _containment(_tokens("completely unrelated invented sentence"), block) < 0.5
    assert _containment(_tokens(""), block) == 1.0  # empty field is vacuously fine
