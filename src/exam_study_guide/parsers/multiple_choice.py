"""Multiple-choice question parser."""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from exam_study_guide.parsers.base import Question, _extract_answer, _split_options


class MultipleChoiceParser:
    """Parse numbered multiple-choice questions.

    Supports question numbers like "1、", "2.", "3．" followed by stem and A/B/C/D options.
    """

    qtype = "选择"
    filename_patterns = ("选择", "choice", "multiple", "500题")

    def can_parse(self, filename: str) -> bool:
        lower = filename.lower()
        return any(p.lower() in lower for p in self.filename_patterns)

    def parse(self, text: str, source: str) -> List[Question]:
        questions: List[Question] = []
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove common page/footers but keep content
        text = re.sub(r"\n?--- Page \d+ ---\n?", "\n", text)
        text = re.sub(r"内部资料\s*—\d+—\s*请勿外传", "", text)
        text = re.sub(r"\n+", "\n", text)

        blocks = re.split(r"\n(?=\d+\s*[、．.])", text)
        for blk in blocks:
            blk = blk.strip()
            if not blk:
                continue
            m = re.match(r"(\d+)\s*[、．.]\s*(.*)", blk, re.DOTALL)
            if not m:
                continue
            qid = m.group(1)
            body = m.group(2).strip()
            ans, body = _extract_answer(body)
            stem, opts = _split_options(body)
            if len(stem) < 3:
                continue
            questions.append(
                Question(
                    qid=f"{source}-{qid}",
                    qtype=self.qtype,
                    stem=stem,
                    options=opts,
                    answer=ans,
                    source=source,
                    raw=blk,
                )
            )
        return questions
