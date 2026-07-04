"""Tests for question parsers."""
from exam_study_guide.parsers.calculation import CalculationNoteParser
from exam_study_guide.parsers.multiple_choice import MultipleChoiceParser
from exam_study_guide.parsers.short_answer import ShortAnswerParser
from exam_study_guide.parsers.true_false import TrueFalseParser


def test_multiple_choice_parser():
    text = """1、Internet 中发送邮件协议是（ B ）
A、FTP B、SMTP
C、HTTP D、POP
2、TCP 协议是一种 服务的协议。C
A、无连接
B、主机-网络层
C、面向连接
D、应用层"""
    parser = MultipleChoiceParser()
    questions = parser.parse(text, "选择资料")
    assert len(questions) == 2
    assert questions[0].answer == "B"
    assert questions[1].answer == "C"
    assert "SMTP" in questions[0].options[1]


def test_true_false_parser():
    text = "（ √ ）TCP协议起源于ARPANET。\n（ × ）FTP协议的默认端口是80。"
    parser = TrueFalseParser()
    questions = parser.parse(text, "判断题")
    assert len(questions) == 2
    assert questions[0].answer == "√"
    assert questions[1].answer == "×"


def test_short_answer_parser():
    text = "1.数字签名的原理是什么？\n2.简述TCP三次握手过程。"
    parser = ShortAnswerParser()
    questions = parser.parse(text, "简答题")
    assert len(questions) == 2
    assert "数字签名" in questions[0].stem


def test_calculation_parser():
    text = "复习要点\n1.CRC冗余检测 （P76）\n2.数据报分片 （P137）"
    parser = CalculationNoteParser()
    questions = parser.parse(text, "计算题")
    assert len(questions) == 2
    assert "CRC" in questions[0].stem
