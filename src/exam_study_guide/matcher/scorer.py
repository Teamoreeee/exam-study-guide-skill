"""Keyword-based question-to-outline scoring."""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

from exam_study_guide.config import KeywordSet, OutlinePoint, SubjectConfig
from exam_study_guide.parsers.base import Question


def compute_idf(all_questions: List[Question], keywords: List[str]) -> Dict[str, float]:
    """Compute smoothed IDF for each keyword across all questions."""
    doc_freq: Dict[str, int] = {kw: 0 for kw in keywords}
    for q in all_questions:
        full = q.stem + " " + " ".join(q.options)
        for kw in keywords:
            if kw in full:
                doc_freq[kw] += 1
    idf: Dict[str, float] = {}
    N = len(all_questions) or 1
    for kw, df in doc_freq.items():
        idf[kw] = math.log((N + 1) / (df + 0.5))
    return idf


def score_question(q: Question, point: OutlinePoint, idf: Dict[str, float]) -> float:
    """Score a single question against a single outline point."""
    full = q.stem + " " + " ".join(q.options)
    score = 0.0
    primary_hits = 0

    for kw, w in point.keywords.primary.items():
        if kw in full:
            score += w * idf.get(kw, 1.0)
            primary_hits += 1

    if primary_hits == 0:
        return 0.0

    for kw, w in point.keywords.secondary.items():
        if kw in full:
            score += w * idf.get(kw, 1.0)

    for kw, w in point.keywords.negative.items():
        if kw in full:
            score -= w * idf.get(kw, 1.0)

    score += primary_hits * 0.5
    return max(score, 0.0)


def collect_keywords(config: SubjectConfig) -> List[str]:
    """Collect all keywords used in the subject config."""
    keywords: set[str] = set()
    for ch in config.chapters:
        for p in ch.points:
            keywords.update(p.keywords.primary.keys())
            keywords.update(p.keywords.secondary.keys())
            keywords.update(p.keywords.negative.keys())
    return list(keywords)


def find_best_point(
    q: Question, config: SubjectConfig, idf: Dict[str, float]
) -> Tuple[str, float] | None:
    """Return the best-matching point title and score for a question."""
    best_title = ""
    best_score = 0.0
    for ch in config.chapters:
        for p in ch.points:
            s = score_question(q, p, idf)
            if s > best_score:
                best_score = s
                best_title = p.title
    if best_title and best_score >= 1.0:
        return best_title, best_score
    return None


def top_suggestions(
    q: Question, config: SubjectConfig, idf: Dict[str, float], top_n: int = 3
) -> List[Tuple[str, float]]:
    """Return the top N matching point titles and scores for a question."""
    scored: List[Tuple[str, float]] = []
    for ch in config.chapters:
        for p in ch.points:
            s = score_question(q, p, idf)
            if s > 0:
                scored.append((p.title, s))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_n]
