"""Question-to-outline matching utilities."""
from exam_study_guide.matcher.manual_assign import (
    load_manual_assignments,
    save_manual_assignments,
)
from exam_study_guide.matcher.review_workflow import (
    MatchReview,
    apply_review_corrections,
    build_match_review,
)
from exam_study_guide.matcher.scorer import (
    collect_keywords,
    compute_idf,
    find_best_point,
    score_question,
    top_suggestions,
)

__all__ = [
    "collect_keywords",
    "compute_idf",
    "find_best_point",
    "score_question",
    "top_suggestions",
    "load_manual_assignments",
    "save_manual_assignments",
    "MatchReview",
    "build_match_review",
    "apply_review_corrections",
]
