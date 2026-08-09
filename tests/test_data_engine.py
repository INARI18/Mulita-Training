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
    from mulitaminer.models import extraction_model_for
    from mulitaminer.scanner_engine import get_scanner

    src = OpenVASCsvSource.__new__(OpenVASCsvSource)  # no I/O; only _target used
    src._model = extraction_model_for(get_scanner("openvas").record_type)
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


def test_target_requires_severity_column():
    # the record no longer restricts severity literals (prioritization audits
    # labels), but the CSV column itself is still mandatory
    row = _row().drop("Severity")
    with pytest.raises(KeyError):
        _source()._target(row, _Block(0, "NVT: x"))


def test_norm_key_immune_to_artifacts():
    assert norm_key("Apache 2.4 mod_proxy") == norm_key("Apache 2.4 mod￾_proxy")


# --- qualys ------------------------------------------------------------------


def _qualys_row(**over) -> pd.Series:
    base = {
        "IP": "172.30.1.1", "QID": "38021", "Title": "Remote Execution Service Open",
        "Severity": "4", "Port": "512", "Protocol": "tcp",
        "CVE ID": "CVE-1999-0618, CVE-2000-0001", "Vendor Reference": "MS08-001",
        "Bugtraq ID": "-", "Threat": "The rexec service was detected.",
        "Impact": "Access may be gained.", "Solution": "Disable the service.",
        "Category": "General remote services",
    }
    base.update(over)
    return pd.Series(base)


def _qualys_source():
    from mulitaminer.models import extraction_model_for
    from mulitaminer.scanner_engine import get_scanner
    from sources.qualys import QualysCsvSource

    src = QualysCsvSource.__new__(QualysCsvSource)
    src._model = extraction_model_for(get_scanner("qualys").record_type)
    return src


def test_qualys_target_mapping():
    t = _qualys_source()._target(_qualys_row(), _Block(7, "QID: 38021"))
    assert t["block_id"] == 7 and t["plugin"] == 38021
    assert t["severity"] == "HIGH"  # digit 4 -> HIGH per prompt contract
    assert t["references"] == ["CVE-1999-0618", "CVE-2000-0001"]  # CVE column only
    assert t["port"] == 512 and t["protocol"] == "tcp"
    assert t["category"] == "General remote services"


def test_qualys_blank_port_and_refs():
    t = _qualys_source()._target(
        _qualys_row(Port="", Protocol="", **{"CVE ID": "-"}), _Block(0, "QID: 38021"))
    assert t["port"] is None and t["protocol"] is None and t["references"] == []


# --- zap ---------------------------------------------------------------------


def test_zap_parse_export(tmp_path):
    from sources.zap.xml_source import parse_export

    xml = """<?xml version="1.0"?>
    <OWASPZAPReport><site name="http://h" host="h" port="80" ssl="false"><alerts>
    <alertitem>
      <pluginid>10202</pluginid><name>Absence of Anti-CSRF Tokens</name>
      <riskdesc>Medium (Low)</riskdesc>
      <desc>&lt;p&gt;First para.&lt;/p&gt;&lt;p&gt;Second para.&lt;/p&gt;</desc>
      <solution>&lt;p&gt;Fix it.&lt;/p&gt;</solution>
      <reference>&lt;p&gt;https://a.example/x&lt;/p&gt;</reference>
      <cweid>352</cweid><wascid>-1</wascid>
      <instances><instance>
        <uri>http://h:80</uri><method>GET</method><param>q</param>
        <attack>'(</attack><evidence>HTTP/1.1 500</evidence><otherinfo>extra</otherinfo>
      </instance></instances>
    </alertitem></alerts></site></OWASPZAPReport>"""
    p = tmp_path / "r.xml"
    p.write_text(xml, encoding="utf-8")
    (e,) = parse_export(p)
    assert e["Name"] == "Absence of Anti-CSRF Tokens"
    assert e["description"] == ["First para.", "Second para."]
    assert e["severity"] == "Medium"  # ZAP's own wording, first riskdesc word
    assert e["references"] == ["https://a.example/x", "CWE 352"]  # wascid -1 dropped
    inst = e["instances"][0]
    assert inst["instance"] == "http://h:80" and inst["request_method"] == "GET"
    assert inst["input_name"] == "q" and inst["payload"] == "'("
    assert inst["proof"] == "HTTP/1.1 500" and inst["output"] == "extra"


# --- nessus ------------------------------------------------------------------


def test_nessus_severity_and_paragraphs():
    from sources.nessus.html_source import _paragraphs, _text

    assert _text("a &amp; b<br/>c") == "a & b\nc"
    assert _paragraphs("<p>One.</p>\n\n<p>Two.</p>") == ["One.", "Two."]


def test_containment_detects_absent_text():
    block = tokens("the server runs php 5.5.9 and is end of life")
    assert containment(tokens("php 5.5.9 end of life"), block) == 1.0
    assert containment(tokens("completely unrelated invented sentence"), block) < 0.5
    assert containment(tokens(""), block) == 1.0  # empty field vacuously fine
