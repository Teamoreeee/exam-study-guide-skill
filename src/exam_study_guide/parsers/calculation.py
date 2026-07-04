"""Calculation-note parser."""
from __future__ import annotations

from typing import List

from exam_study_guide.parsers.base import Question


class CalculationNoteParser:
    """Parse calculation review notes, one note per line."""

    qtype = "计算要点"
    filename_patterns = ("计算", "calculation", "compute")

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return any(p.lower() in lower for p in self.filename_patterns)

    def parse(self, text: str, source: str) -> List[Question]:
        questions: List[Question] = []
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        for line in text.split("\n"):
            line = line.strip()
            if not line or line.startswith("《"):
                continue
            if len(line) < 4:
                continue
            # Skip overly generic guide sentences
            if any(k in line for k in ["复习", "重点", "以下面列出", "重点关注", "教材中有关"]):
                continue
            questions.append(
                Question(
                    qid=f"{source}-{len(questions) + 1}",
                    qtype=self.qtype,
                    stem=line,
                    source=source,
                    raw=line,
                )
            )
        return questions
