"""Short-answer question parser."""
from __future__ import annotations

import re
from typing import List

from exam_study_guide.parsers.base import Question


class ShortAnswerParser:
    """Parse numbered short-answer questions."""

    qtype = "简答"
    filename_patterns = ("简答", "shortanswer", "short_answer")

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return any(p.lower() in lower for p in self.filename_patterns)

    def parse(self, text: str, source: str) -> List[Question]:
        questions: List[Question] = []
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        blocks = re.split(r"\n(?=\d+\s*[\.．])", text)
        for blk in blocks:
            blk = blk.strip()
            if not blk:
                continue
            m = re.match(r"(\d+)\s*[\.．]\s*(.*)", blk, re.DOTALL)
            if not m:
                continue
            qid = m.group(1)
            stem = re.sub(r"\s+", " ", m.group(2).strip())
            if len(stem) < 3:
                continue
            questions.append(
                Question(
                    qid=f"{source}-{qid}",
                    qtype=self.qtype,
                    stem=stem,
                    source=source,
                    raw=blk,
                )
            )
        return questions
