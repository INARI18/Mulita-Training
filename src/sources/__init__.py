"""Label sources: each yields Examples the assembler renders into training data.
Add a source by implementing LabelSource and registering it in SOURCES."""
from sources.base import Example, LabelSource
from sources.openvas import OpenVASCsvSource

SOURCES = {"openvas-csv": OpenVASCsvSource}

__all__ = ["Example", "LabelSource", "SOURCES", "OpenVASCsvSource"]
