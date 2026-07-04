"""Question data model and parser protocol."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Protocol


@dataclass
class Question:
    """A parsed question from any source."""

    qid: str
    qtype: str  # 选择 / 判断 / 简答 / 计算要点
    stem: str
    options: List[str] = field(default_factory=list)
    answer: str = ""
    source: str = ""
    raw: str = ""


class Parser(Protocol):
    """Protocol for question parsers."""

    qtype: str

    def can_parse(self, filename: str) -> bool:
        """Return True if this parser handles the given filename."""
        ...

    def parse(self, text: str, source: str) -> List[Question]:
        """Parse text into a list of questions."""
        ...


def _extract_answer(body: str) -> tuple[str, str]:
    """Extract an answer marker from a question body.

    Supports:
      - （A） / (A) / [A]
      - ___A___
      - 答案：A / 答案为A / 答案是A
      - ...为：c / ...为:c (bare letter before options)
    """
    patterns = [
        r"[（(]\s*([a-dA-D])\s*[）)]",
        r"_{1,3}\s*([a-dA-D])\s*_{1,3}",
        r"[\[〔]\s*([a-dA-D])\s*[\]〕]",
        r"答案[是为:]\s*([a-dA-D])",
        r"[：:]\s*([a-dA-D])\s*\n",
        # Bare answer letter at end of stem line, immediately before first option
        r"(?<=[一-龥。！？\.\s])([a-dA-D])\s*\n\s*[A-Da-d][\.．。,、]",
    ]
    for pat in patterns:
        m = __import__("re").search(pat, body)
        if m:
            ans = m.group(1).upper()
            body = body.replace(m.group(0), " ")
            return ans, body
    return "", body


def _split_options(body: str) -> tuple[str, List[str]]:
    """Split a question body into stem and A/B/C/D options."""
    import re

    opt_parts = re.split(r"(?=[A-Da-d][\.．。,、\s])", body)
    opt_dict: dict[str, str] = {}
    for p in opt_parts[1:]:
        p = p.strip()
        if len(p) < 2:
            continue
        label = p[0].upper()
        if label not in "ABCD":
            continue
        content = p[1:].lstrip(".．。,、").strip()
        opt_dict[label] = content
    opts = [f"{lab}. {opt_dict[lab]}" for lab in "ABCD" if lab in opt_dict]
    stem = re.sub(r"\s+", " ", opt_parts[0].strip())
    return stem, opts
