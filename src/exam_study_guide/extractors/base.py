"""Document extractors."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Extractor(Protocol):
    """Protocol for file-to-text extractors."""

    extensions: tuple[str, ...]

    def can_extract(self, path: Path) -> bool:
        """Return True if this extractor handles the given file."""
        return path.suffix.lower() in self.extensions

    def extract(self, path: Path) -> str:
        """Extract plain text from the file."""
        ...


class ExtractionError(Exception):
    """Raised when all extraction methods fail."""

    pass
