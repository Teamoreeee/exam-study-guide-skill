"""Human review workflow for question-to-outline matching."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

from exam_study_guide.config import SubjectConfig
from exam_study_guide.matcher.scorer import (
    collect_keywords,
    compute_idf,
    find_best_point,
    score_question,
    top_suggestions,
)
from exam_study_guide.parsers.base import Question


@dataclass
class MatchReview:
    """Container for match review data before serialization."""

    subject: str
    generated_at: str
    unmatched: List[Dict] = field(default_factory=list)
    matches: Dict[str, List[Dict]] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        return {
            "subject": self.subject,
            "generated_at": self.generated_at,
            "unmatched_questions": self.unmatched,
            "point_matches": self.matches,
        }

    def save(self, path: Path) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path: Path) -> "MatchReview":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            subject=data.get("subject", ""),
            generated_at=data.get("generated_at", ""),
            unmatched=data.get("unmatched_questions", []),
            matches=data.get("point_matches", {}),
        )


def build_match_review(
    questions: List[Question],
    config: SubjectConfig,
    manual_assignments: Dict[str, str],
    threshold: float = 1.5,
) -> MatchReview:
    """Automatically match questions to points and produce a review object."""
    keywords = collect_keywords(config)
    idf = compute_idf(questions, keywords)

    review = MatchReview(
        subject=config.subject,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )

    point_index = {p.title: [] for ch in config.chapters for p in ch.points}

    for q in questions:
        # Manual assignment wins
        if q.qid in manual_assignments:
            assigned_title = manual_assignments[q.qid]
            if assigned_title in point_index:
                point_index[assigned_title].append(
                    {"qid": q.qid, "score": 999.0, "user_confirmed": True}
                )
                continue

        best = find_best_point(q, config, idf)
        if best:
            title, score = best
            if score >= threshold:
                point_index[title].append(
                    {"qid": q.qid, "score": round(score, 2), "user_confirmed": False}
                )
                continue

        # Unmatched: include top suggestions for human review
        suggestions = top_suggestions(q, config, idf, top_n=3)
        review.unmatched.append(
            {
                "qid": q.qid,
                "qtype": q.qtype,
                "stem": q.stem[:300],
                "suggested_point": suggestions[0][0] if suggestions else None,
                "suggested_score": round(suggestions[0][1], 2) if suggestions else 0.0,
                "top_suggestions": [
                    {"point": t, "score": round(s, 2)} for t, s in suggestions
                ],
                "user_assigned": None,
            }
        )

    # Sort matches by score descending and store
    for title, items in point_index.items():
        items.sort(key=lambda x: x["score"], reverse=True)
        review.matches[title] = items

    return review


def apply_review_corrections(review: MatchReview) -> Tuple[Dict[str, str], List[str]]:
    """Return (manual_assignments, skipped_qids) based on user corrections."""
    assignments: Dict[str, str] = {}
    skipped: List[str] = []

    for item in review.unmatched:
        qid = item["qid"]
        assigned = item.get("user_assigned")
        if assigned == "__SKIP__":
            skipped.append(qid)
        elif assigned:
            assignments[qid] = assigned

    for title, items in review.matches.items():
        for item in items:
            moved = item.get("user_moved_to")
            if moved == "__SKIP__":
                skipped.append(item["qid"])
            elif moved:
                assignments[item["qid"]] = moved

    return assignments, skipped
