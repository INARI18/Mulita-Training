"""The seam between label sources and the assembler."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Protocol, runtime_checkable

from mulitaminer.models import Block


@dataclass
class Example:
    scanner: str      # scanner profile that renders the input block
    block: Block      # model input
    target: dict      # LLM-target object (block_id + fields), schema-validated
    source_id: str    # provenance (e.g. report filename)


@runtime_checkable
class LabelSource(Protocol):
    name: str

    def examples(self) -> Iterator[Example]: ...
