"""Document extraction utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

from exam_study_guide.extractors.base import Extractor, ExtractionError
from exam_study_guide.extractors.doc_extractor import DocExtractor
from exam_study_guide.extractors.docx_extractor import DocxExtractor
from exam_study_guide.extractors.pdf_extractor import PdfExtractor
from exam_study_guide.extractors.txt_extractor import TxtExtractor

DEFAULT_EXTRACTORS: tuple[Extractor, ...] = (
    DocxExtractor(),
    DocExtractor(),
    PdfExtractor(),
    TxtExtractor(),
)


def get_extractor(path: Path, extractors: Iterable[Extractor] | None = None) -> Extractor:
    """Return the first extractor that can handle the given file."""
    for extractor in extractors or DEFAULT_EXTRACTORS:
        if extractor.can_extract(path):
            return extractor
    raise ExtractionError(f"No extractor available for {path.suffix}")


def extract_file(path: Path, extractors: Iterable[Extractor] | None = None) -> str:
    """Extract text from a single file."""
    extractor = get_extractor(path, extractors)
    return extractor.extract(path)


__all__ = [
    "Extractor",
    "ExtractionError",
    "DocExtractor",
    "DocxExtractor",
    "PdfExtractor",
    "TxtExtractor",
    "DEFAULT_EXTRACTORS",
    "get_extractor",
    "extract_file",
]
