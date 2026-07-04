"""DOCX extractor using pandoc."""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from exam_study_guide.extractors.base import Extractor, ExtractionError


class DocxExtractor(Extractor):
    """Extract text from .docx files using pandoc."""

    extensions = (".docx",)

    def extract(self, path: Path) -> str:
        if not shutil.which("pandoc"):
            raise ExtractionError("pandoc not found in PATH; install it to extract .docx files")
        try:
            result = subprocess.run(
                ["pandoc", "-s", str(path), "-t", "plain"],
                capture_output=True,
                text=True,
                check=True,
                encoding="utf-8",
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise ExtractionError(f"pandoc failed for {path}: {e.stderr}") from e
