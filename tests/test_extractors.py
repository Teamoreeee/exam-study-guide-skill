"""Tests for document extractors."""
from pathlib import Path

import pytest

from exam_study_guide.extractors import get_extractor
from exam_study_guide.extractors.base import ExtractionError


def test_get_extractor(tmp_path: Path):
    docx = tmp_path / "test.docx"
    docx.write_text("", encoding="utf-8")
    extractor = get_extractor(docx)
    assert extractor.extensions == (".docx",)

    pdf = tmp_path / "test.pdf"
    pdf.write_text("", encoding="utf-8")
    extractor = get_extractor(pdf)
    assert extractor.extensions == (".pdf",)


def test_get_extractor_unknown_extension(tmp_path: Path):
    unknown = tmp_path / "test.xyz"
    unknown.write_text("", encoding="utf-8")
    with pytest.raises(ExtractionError):
        get_extractor(unknown)
