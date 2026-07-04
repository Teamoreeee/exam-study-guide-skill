"""True/false question parser."""
from __future__ import annotations

import re
from typing import List

from exam_study_guide.parsers.base import Question


class TrueFalseParser:
    """Parse true/false statements marked with √ or ×."""

    qtype = "判断"
    filename_patterns = ("判断", "truefalse", "true_false")

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return any(p.lower() in lower for p in self.filename_patterns)

    def parse(self, text: str, source: str) -> List[Question]:
        questions: List[Question] = []
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            m = re.match(r"[（(]\s*([√×])\s*[）)]\s*(.*)", line)
            if not m:
                continue
            ans = m.group(1)
            stmt = m.group(2).strip()
            if len(stmt) < 3:
                continue
            questions.append(
                Question(
                    qid=f"{source}-{len(questions) + 1}",
                    qtype=self.qtype,
                    stem=stmt,
                    answer=ans,
                    source=source,
                    raw=line,
                )
            )
        return questions
