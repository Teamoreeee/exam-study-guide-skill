# Exam Study Guide Generator Skill

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A cross-platform CLI tool and [Claude Code](https://claude.ai/code) skill that turns an exam outline + a set of question banks into a polished Word study guide.

**What it does**

1. **Extracts** text from question-bank files: `.docx`, `.doc`, `.pdf`, `.txt`.
2. **Parses** questions (multiple-choice, true/false, short-answer, calculation notes).
3. **Matches** each question to the most relevant point in your exam outline using IDF-weighted keyword scoring.
4. **Reviews** matches with you (optional but recommended) so you can fix wrong assignments.
5. **Generates** two Word documents:
   - **Study Guide** — outline points + matched questions + answers + explanations.
   - **Review Points** — concise study notes with real-life examples for each concept.

**Why this exists**

Manually matching hundreds of exam questions to an outline is tedious and error-prone. This skill automates the bulk of the work while keeping you in the loop for final quality control.

---

## Quick start

### 1. Install

```bash
git clone https://github.com/YOUR_USERNAME/exam-study-guide-skill.git
cd exam-study-guide-skill
pip install -e .
```

Optional platform extras:

```bash
# Windows (for best .doc extraction)
pip install -e ".[windows]"

# Linux / macOS
pip install -e ".[linux]"   # or [macos]
```

System dependencies:

- **pandoc** is required for `.docx` extraction.
- For `.doc` on Linux/macOS: install `antiword` or `catdoc`.
- For `.doc` on Windows: Microsoft Word + the `windows` extra gives the highest quality.

### 2. Prepare your files

Put your question-bank files in a folder, e.g. `question_banks/`:

```
question_banks/
├── 选择题.docx
├── 判断题.doc
├── 简答题.doc
├── 计算题.doc
└── 500题.pdf
```

Copy `config/computer_networks.yaml` to `config/my_subject.yaml` and edit it for your subject.

### 3. Run the full pipeline

```bash
exam-study-guide full \
  --config config/computer_networks.yaml \
  --input-dir question_banks \
  --output-dir output
```

This produces:

```
output/
├── study_guide.docx
├── review_points.docx
└── match_review.json
```

Open `match_review.json` to inspect or correct matches before sharing the final docs.

---

## Step-by-step commands

### Extract text only

```bash
exam-study-guide extract question_banks extracted
```

### Match questions to outline

```bash
exam-study-guide match \
  --config config/computer_networks.yaml \
  --questions-dir extracted \
  --review-file match_review.json
```

### Review matches interactively

```bash
exam-study-guide review --review-file match_review.json
```

### Generate study guide

```bash
exam-study-guide generate \
  --config config/computer_networks.yaml \
  --review-file match_review.json \
  --output output/study_guide.docx
```

### Generate review-points document

```bash
exam-study-guide generate-review \
  --config config/computer_networks.yaml \
  --output output/review_points.docx
```

---

## Configuration

The outline is defined in a YAML file. See `config/computer_networks.yaml` for a complete example.

```yaml
subject: "计算机网络"
description: "计算机网络期末考试复习指南"

chapters:
  - title: "第一章 计算机网络概述"
    points:
      - title: "三种交换方式：电路交换、报文交换、分组交换"
        keywords:
          primary:
            电路交换: 2.0
            报文交换: 2.0
            分组交换: 2.0
          secondary:
            交换方式: 1.0
            存储转发: 1.0
          negative:
            TCP: 1.0
            UDP: 1.0
        guidance: "..."
        examples:
          - "打电话就是电路交换..."
          - "拆成多个包裹发快递就是分组交换..."

manual_assignments:
  "简答题-2": "信道容量：香农公式与奈氏准则"
```

Key concepts:

- **`primary` keywords**: a question must hit at least one to be considered for this point.
- **`secondary` keywords**: boost the score.
- **`negative` keywords**: penalize the score (keeps unrelated questions out).
- **`examples`**: real-life analogies shown in the review-points document.
- **`manual_assignments`**: force specific question IDs to specific points.

---

## Using as a Claude Code skill

1. Clone or copy this repo into your project's `.claude/skills/` folder, **or** register the `claude-skill.yaml` manifest.
2. Restart Claude Code.
3. Invoke with:

```
/study-guide full --config config/computer_networks.yaml --input-dir question_banks --output-dir output
```

---

## Project structure

```
exam-study-guide-skill/
├── claude-skill.yaml              # Claude Code skill manifest
├── pyproject.toml                 # Package metadata
├── config/
│   └── computer_networks.yaml     # Example subject outline
├── src/exam_study_guide/
│   ├── cli.py                     # Typer CLI
│   ├── config.py                  # Pydantic config loader
│   ├── extractors/                # Cross-platform doc extractors
│   ├── parsers/                   # Question parsers
│   ├── matcher/                   # Keyword scoring + review workflow
│   └── generators/                # Word doc generators
└── tests/
```

---

## Development

Install dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

Format and lint:

```bash
black src tests
ruff check src tests
mypy src
```

---

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

Built with [python-docx](https://python-docx.readthedocs.io/), [pdfplumber](https://github.com/jsvine/pdfplumber), [Typer](https://typer.tiangolo.com/), and [Pydantic](https://docs.pydantic.dev/).
