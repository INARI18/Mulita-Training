"""Label sources: each yields Examples the assembler renders into training data.
Add a source by implementing LabelSource and registering it in SOURCES."""
from sources.base import Example, LabelSource
from sources.nessus import NessusHtmlSource
from sources.openvas import OpenVASCsvSource
from sources.qualys import QualysCsvSource
from sources.zap import ZapXmlSource

SOURCES = {
    "openvas-csv": OpenVASCsvSource,
    "qualys-csv": QualysCsvSource,
    "nessus-html": NessusHtmlSource,
    "zap-xml": ZapXmlSource,
}

__all__ = ["Example", "LabelSource", "SOURCES", "OpenVASCsvSource",
           "QualysCsvSource", "NessusHtmlSource", "ZapXmlSource"]
