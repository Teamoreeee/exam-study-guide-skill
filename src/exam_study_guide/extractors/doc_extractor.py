"""DOC extractor with cross-platform fallback chain."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from exam_study_guide.extractors.base import Extractor, ExtractionError


class DocExtractor(Extractor):
    """Extract text from legacy .doc files.

    Tries multiple methods in priority order:
      1. python-textract (cross-platform wrapper)
      2. antiword CLI (Linux/macOS)
      3. catdoc CLI (Linux/macOS)
      4. Microsoft Word COM automation (Windows)
      5. olefile raw stream extraction (last resort)
    """

    extensions = (".doc",)

    def extract(self, path: Path) -> str:
        errors = []
        for method in (
            self._try_textract,
            self._try_antiword,
            self._try_catdoc,
            self._try_word_com,
            self._try_olefile,
        ):
            try:
                return method(path)
            except Exception as e:  # noqa: BLE001
                errors.append(f"{method.__name__}: {e}")
        raise ExtractionError(
            f"All extraction methods failed for {path}:\n" + "\n".join(errors)
        )

    def _try_textract(self, path: Path) -> str:
        try:
            import textract
        except ImportError as e:
            raise RuntimeError("textract not installed") from e
        text = textract.process(str(path))
        return text.decode("utf-8", errors="ignore")

    def _try_antiword(self, path: Path) -> str:
        if not shutil.which("antiword"):
            raise RuntimeError("antiword not found in PATH")
        result = subprocess.run(
            ["antiword", str(path)],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="ignore",
        )
        return result.stdout

    def _try_catdoc(self, path: Path) -> str:
        if not shutil.which("catdoc"):
            raise RuntimeError("catdoc not found in PATH")
        result = subprocess.run(
            ["catdoc", "-d", "utf-8", str(path)],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
            errors="ignore",
        )
        return result.stdout

    def _try_word_com(self, path: Path) -> str:
        try:
            import win32com.client
        except ImportError as e:
            raise RuntimeError("pywin32 not installed") from e

        word = win32com.client.Dispatch("Word.Application")
        word.Visible = False
        try:
            doc = word.Documents.Open(str(path.resolve()))
            text = doc.Content.Text
            doc.Close(False)
            return text
        finally:
            word.Quit()

    def _try_olefile(self, path: Path) -> str:
        """Last-resort raw text extraction from OLE WordDocument stream.

        This is lossy but does not require external tools.
        """
        try:
            import olefile
        except ImportError as e:
            raise RuntimeError("olefile not installed") from e

        ole = olefile.OleFileIO(str(path))
        try:
            if not ole.exists("WordDocument"):
                raise RuntimeError("No WordDocument stream found")
            data = ole.openstream("WordDocument").read()
            # Extract printable ASCII/Chinese characters heuristically.
            text = re.sub(rb"[^\x20-\x7e\x80-\xff]+", b" ", data).decode(
                "utf-8", errors="ignore"
            )
            return " ".join(text.split())
        finally:
            ole.close()
