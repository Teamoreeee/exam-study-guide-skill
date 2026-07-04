"""Configuration models and YAML loader."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel, Field, field_validator


class KeywordSet(BaseModel):
    """Weighted keywords for matching questions to outline points."""

    primary: Dict[str, float] = Field(default_factory=dict)
    secondary: Dict[str, float] = Field(default_factory=dict)
    negative: Dict[str, float] = Field(default_factory=dict)


class OutlinePoint(BaseModel):
    """A single point within an outline chapter."""

    title: str
    keywords: KeywordSet = Field(default_factory=KeywordSet)
    guidance: str = ""
    examples: List[str] = Field(default_factory=list)


class Chapter(BaseModel):
    """A chapter containing outline points."""

    title: str
    points: List[OutlinePoint]


class SubjectConfig(BaseModel):
    """Top-level configuration for a subject / exam."""

    subject: str
    description: str = ""
    chapters: List[Chapter]
    manual_assignments: Dict[str, str] = Field(default_factory=dict)

    @field_validator("manual_assignments", mode="before")
    @classmethod
    def _ensure_manual_assignments(cls, v):
        return v or {}

    @classmethod
    def from_yaml(cls, path: Path) -> "SubjectConfig":
        """Load and validate a YAML configuration file."""
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid YAML config: expected mapping, got {type(data).__name__}")
        return cls.model_validate(data)

    def get_point_by_title(self, title: str) -> OutlinePoint | None:
        """Find an outline point by its exact title."""
        for chapter in self.chapters:
            for point in chapter.points:
                if point.title == title:
                    return point
        return None

    def all_point_titles(self) -> List[str]:
        """Return all point titles in order."""
        return [
            point.title
            for chapter in self.chapters
            for point in chapter.points
        ]
