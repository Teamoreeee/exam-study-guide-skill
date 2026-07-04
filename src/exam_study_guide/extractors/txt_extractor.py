"""TXT extractor (passthrough)."""
from __future__ import annotations

from pathlib import Path

from exam_study_guide.extractors.base import Extractor, ExtractionError


class TxtExtractor(Extractor):
    """Read .txt files directly."""

    extensions = (".txt",)

    def extract(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            raise ExtractionError(f"Failed to read {path}: {e}") from e
