"""Question parsers."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from exam_study_guide.parsers.base import Parser, Question
from exam_study_guide.parsers.calculation import CalculationNoteParser
from exam_study_guide.parsers.multiple_choice import MultipleChoiceParser
from exam_study_guide.parsers.short_answer import ShortAnswerParser
from exam_study_guide.parsers.true_false import TrueFalseParser

DEFAULT_PARSERS: tuple[Parser, ...] = (
    MultipleChoiceParser(),
    TrueFalseParser(),
    ShortAnswerParser(),
    CalculationNoteParser(),
)


def get_parser(filename: str, parsers: Iterable[Parser] | None = None) -> Parser | None:
    """Return the first parser that claims it can parse the given filename."""
    for parser in parsers or DEFAULT_PARSERS:
        if parser.can_parse(filename):
            return parser
    return None


def parse_file(path: Path, parsers: Iterable[Parser] | None = None) -> List[Question]:
    """Parse a single text file into questions."""
    parser = get_parser(path.name, parsers)
    if parser is None:
        return []
    text = path.read_text(encoding="utf-8", errors="ignore")
    return parser.parse(text, path.stem)


def parse_files(
    paths: Iterable[Path], parsers: Iterable[Parser] | None = None
) -> List[Question]:
    """Parse multiple text files into a single list of questions."""
    questions: List[Question] = []
    for path in paths:
        questions.extend(parse_file(path, parsers))
    return questions


__all__ = [
    "Parser",
    "Question",
    "MultipleChoiceParser",
    "TrueFalseParser",
    "ShortAnswerParser",
    "CalculationNoteParser",
    "DEFAULT_PARSERS",
    "get_parser",
    "parse_file",
    "parse_files",
]
