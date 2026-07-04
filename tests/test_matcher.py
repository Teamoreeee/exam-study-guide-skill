"""Tests for the matcher/scorer."""
from exam_study_guide.config import KeywordSet, OutlinePoint
from exam_study_guide.matcher.scorer import compute_idf, score_question
from exam_study_guide.parsers.base import Question


def test_score_question():
    point = OutlinePoint(
        title="Test Point",
        keywords=KeywordSet(
            primary={"TCP": 2.0},
            secondary={"协议": 1.0},
            negative={"UDP": 1.0},
        ),
        guidance="Test guidance",
    )
    q = Question(qid="q1", qtype="选择", stem="TCP协议是什么？", options=[])
    idf = compute_idf([q], ["TCP", "协议", "UDP"])
    score = score_question(q, point, idf)
    assert score > 0


def test_no_primary_keyword_zero_score():
    point = OutlinePoint(
        title="Test Point",
        keywords=KeywordSet(primary={"IP": 2.0}, secondary={"协议": 1.0}),
        guidance="Test guidance",
    )
    q = Question(qid="q2", qtype="选择", stem="TCP协议是什么？", options=[])
    idf = compute_idf([q], ["IP", "协议"])
    score = score_question(q, point, idf)
    assert score == 0.0
