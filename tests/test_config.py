"""Tests for configuration loading."""
from pathlib import Path

import pytest
import yaml

from exam_study_guide.config import SubjectConfig


def test_load_computer_networks_config(tmp_path: Path):
    data = {
        "subject": "Test Subject",
        "description": "Test description",
        "chapters": [
            {
                "title": "Chapter 1",
                "points": [
                    {
                        "title": "Point A",
                        "keywords": {"primary": {"foo": 2.0}, "secondary": {}, "negative": {}},
                        "guidance": "Study this.",
                        "examples": ["Example 1"],
                    }
                ],
            }
        ],
    }
    path = tmp_path / "test.yaml"
    path.write_text(yaml.dump(data), encoding="utf-8")

    cfg = SubjectConfig.from_yaml(path)
    assert cfg.subject == "Test Subject"
    assert len(cfg.chapters) == 1
    assert cfg.chapters[0].points[0].title == "Point A"
    assert cfg.chapters[0].points[0].keywords.primary["foo"] == 2.0
    assert cfg.get_point_by_title("Point A") is not None
    assert cfg.get_point_by_title("Missing") is None
