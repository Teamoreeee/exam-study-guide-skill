"""PDF extractor using pdfplumber."""
from __future__ import annotations

from pathlib import Path

from exam_study_guide.extractors.base import Extractor, ExtractionError


class PdfExtractor(Extractor):
    """Extract text from .pdf files using pdfplumber."""

    extensions = (".pdf",)

    def extract(self, path: Path) -> str:
        try:
            import pdfplumber
        except ImportError as e:
            raise ExtractionError("pdfplumber not installed") from e

        try:
            parts = []
            with pdfplumber.open(str(path)) as pdf:
                for i, page in enumerate(pdf.pages, 1):
                    text = page.extract_text()
                    if text:
                        parts.append(f"\n--- Page {i} ---\n{text}")
            return "\n".join(parts)
        except Exception as e:
            raise ExtractionError(f"pdfplumber failed for {path}: {e}") from e
