"""Unit tests for the training data engine (references, mapping, assembly)."""
import pandas as pd
import pytest

from common import containment, norm_key, tokens
from sources.openvas.references import build_references
from sources.openvas import OpenVASCsvSource


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


class _Block:
    def __init__(self, id, text):
        self.id = id
        self.text = text


def _source() -> OpenVASCsvSource:
    from mulitaminer.models import OpenVASRecord, extraction_model_for

    src = OpenVASCsvSource.__new__(OpenVASCsvSource)  # no I/O; only _target used
    src._model = extraction_model_for(OpenVASRecord)
    return src


def test_target_shape_and_types():
    block = _Block(3, "High (CVSS: 10.0)\nNVT: PHP End of Life\nReferences\ncve: CVE-2016-5770\n")
    t = _source()._target(_row(), block)
    assert t["block_id"] == 3
    assert t["Name"].startswith("PHP End of Life")
    assert t["description"] == ["The PHP version has reached end of life.",
                                "Second paragraph here."]
    assert t["cvss"] == 10.0 and t["severity"] == "CRITICAL"
    assert t["port"] == 80 and t["protocol"] == "tcp"
    assert t["insight"] == []  # blank cell -> empty list
    assert t["references"] == ["CVE-2016-5770"]  # from the block, not the row
    assert t["plugin"] is None and t["plugin_details"] == {} and t["instances"] == []


def test_target_rejects_bad_severity():
    with pytest.raises(Exception):
        _source()._target(_row(Severity="Bogus"), _Block(0, "NVT: x"))


def test_norm_key_immune_to_artifacts():
    assert norm_key("Apache 2.4 mod_proxy") == norm_key("Apache 2.4 mod￾_proxy")


def test_containment_detects_absent_text():
    block = tokens("the server runs php 5.5.9 and is end of life")
    assert containment(tokens("php 5.5.9 end of life"), block) == 1.0
    assert containment(tokens("completely unrelated invented sentence"), block) < 0.5
    assert containment(tokens(""), block) == 1.0  # empty field vacuously fine
