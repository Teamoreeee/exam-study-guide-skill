"""Load and persist manual question-to-point assignments."""
from __future__ import annotations

from pathlib import Path
from typing import Dict

import yaml

DEFAULT_MANUAL_ASSIGN_FILE = Path("manual_assignments.yaml")


def load_manual_assignments(
    config_assignments: Dict[str, str] | None = None,
    path: Path | None = None,
) -> Dict[str, str]:
    """Load manual assignments from config and optional YAML file.

    Config assignments take precedence over file assignments.
    """
    assignments: Dict[str, str] = {}
    if path and path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict):
            assignments.update(data)
    if config_assignments:
        assignments.update(config_assignments)
    return assignments


def save_manual_assignments(assignments: Dict[str, str], path: Path | None = None) -> None:
    """Save manual assignments to a YAML file."""
    target = path or DEFAULT_MANUAL_ASSIGN_FILE
    with open(target, "w", encoding="utf-8") as f:
        yaml.dump(assignments, f, allow_unicode=True, sort_keys=True, width=120)
