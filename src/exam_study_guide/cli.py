"""Typer CLI for the exam study guide generator."""
from __future__ import annotations

from pathlib import Path
from typing import List

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from exam_study_guide.config import SubjectConfig
from exam_study_guide.extractors import extract_file
from exam_study_guide.generators import generate_review_points, generate_study_guide
from exam_study_guide.matcher import (
    MatchReview,
    apply_review_corrections,
    build_match_review,
    load_manual_assignments,
    save_manual_assignments,
)
from exam_study_guide.parsers import parse_files

app = typer.Typer(
    help="Generate exam study guides from an outline and question banks.",
    rich_markup_mode="rich",
)
console = Console()


def _discover_files(input_dir: Path, extensions: tuple[str, ...]) -> List[Path]:
    files = []
    for ext in extensions:
        files.extend(input_dir.glob(f"*{ext}"))
        files.extend(input_dir.glob(f"*{ext.upper()}"))
    return sorted(set(files))


@app.command()
def extract(
    input_dir: Path = typer.Argument(..., help="Directory with question bank files"),
    output_dir: Path = typer.Argument(..., help="Directory to save extracted text files"),
    formats: List[str] = typer.Option(
        [".docx", ".doc", ".pdf", ".txt"],
        "--formats",
        help="File extensions to process",
    ),
) -> None:
    """Extract text from question bank files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    files = _discover_files(input_dir, tuple(formats))
    if not files:
        console.print(f"[yellow]No files found in {input_dir} with extensions {formats}[/]")
        raise typer.Exit(1)

    for path in files:
        try:
            text = extract_file(path)
            out_path = output_dir / f"{path.stem}.txt"
            out_path.write_text(text, encoding="utf-8")
            console.print(f"[green]Extracted[/] {path.name} -> {out_path.name}")
        except Exception as e:
            console.print(f"[red]Failed[/] {path.name}: {e}")


@app.command()
def match(
    config: Path = typer.Option(..., "--config", "-c", help="Subject outline YAML file"),
    questions_dir: Path = typer.Option(
        ..., "--questions-dir", "-q", help="Directory with extracted .txt question files"
    ),
    review_file: Path = typer.Option(
        "match_review.json", "--review-file", "-r", help="Path to write review JSON"
    ),
    threshold: float = typer.Option(1.5, "--threshold", "-t", help="Minimum score to auto-match"),
    manual_file: Path | None = typer.Option(
        None, "--manual-file", "-m", help="Optional manual assignments YAML"
    ),
) -> None:
    """Match questions to outline points and produce a review file."""
    cfg = SubjectConfig.from_yaml(config)
    txt_files = list(questions_dir.glob("*.txt"))
    if not txt_files:
        console.print(f"[red]No .txt files found in {questions_dir}[/]")
        raise typer.Exit(1)

    questions = parse_files(txt_files)
    manual = load_manual_assignments(cfg.manual_assignments, manual_file)
    review = build_match_review(questions, cfg, manual, threshold=threshold)
    review.save(review_file)

    total_matched = sum(len(items) for items in review.matches.values())
    console.print(
        f"[green]Matched {total_matched} questions, {len(review.unmatched)} unmatched.[/]"
    )
    console.print(f"Review file written to [cyan]{review_file}[/]")


@app.command()
def review(
    review_file: Path = typer.Option(..., "--review-file", "-r", help="Path to review JSON"),
    manual_file: Path = typer.Option(
        "manual_assignments.yaml", "--manual-file", "-m", help="Where to save corrections"
    ),
) -> None:
    """Interactively review and correct auto-matched questions."""
    match_review = MatchReview.load(review_file)

    if match_review.unmatched:
        console.print(
            f"\n[bold]Reviewing {len(match_review.unmatched)} unmatched questions...[/]\n"
        )
        for item in match_review.unmatched:
            table = Table(title=f"{item['qid']} ({item['qtype']})")
            table.add_column("Field", style="cyan")
            table.add_column("Value")
            table.add_row("Stem", item["stem"])
            if item["top_suggestions"]:
                suggestions = "\n".join(
                    f"{i+1}. {s['point']} (score {s['score']})"
                    for i, s in enumerate(item["top_suggestions"])
                )
                table.add_row("Suggestions", suggestions)
            console.print(table)

            choices = {
                "1": f"Accept: {item['suggested_point']}" if item["suggested_point"] else None,
                "2": "Assign to a different point",
                "3": "Skip this question",
            }
            for k, v in choices.items():
                if v:
                    console.print(f"  {k}. {v}")

            choice = Prompt.ask(
                "Choice",
                choices=[k for k, v in choices.items() if v],
                default="3",
            )

            if choice == "1" and item["suggested_point"]:
                item["user_assigned"] = item["suggested_point"]
            elif choice == "2":
                point_title = Prompt.ask("Enter exact point title")
                item["user_assigned"] = point_title
            else:
                item["user_assigned"] = "__SKIP__"

    # Optionally review matched items
    review_matched = Prompt.ask(
        "Review already-matched questions too?", choices=["y", "n"], default="n"
    )
    if review_matched == "y":
        for title, items in match_review.matches.items():
            for item in items:
                if item.get("user_confirmed"):
                    continue
                console.print(
                    f"\n[bold]{item['qid']}[/] matched to [green]{title}[/] (score {item['score']})"
                )
                choices = {
                    "1": "Keep",
                    "2": "Move to another point",
                    "3": "Skip",
                }
                for k, v in choices.items():
                    console.print(f"  {k}. {v}")
                choice = Prompt.ask("Choice", choices=list(choices.keys()), default="1")
                if choice == "2":
                    item["user_moved_to"] = Prompt.ask("Enter exact point title")
                elif choice == "3":
                    item["user_moved_to"] = "__SKIP__"

    match_review.save(review_file)
    new_assignments, _ = apply_review_corrections(match_review)
    if new_assignments:
        save_manual_assignments(new_assignments, manual_file)
        console.print(
            f"[green]Saved {len(new_assignments)} corrections to {manual_file}[/]"
        )
    console.print(f"[green]Updated {review_file}[/]")


@app.command()
def generate(
    config: Path = typer.Option(..., "--config", "-c", help="Subject outline YAML file"),
    review_file: Path = typer.Option(..., "--review-file", "-r", help="Reviewed match JSON"),
    output: Path = typer.Option(..., "--output", "-o", help="Output Word document path"),
    questions_dir: Path = typer.Option(
        ..., "--questions-dir", "-q", help="Directory with extracted .txt question files"
    ),
) -> None:
    """Generate final study guide Word document."""
    cfg = SubjectConfig.from_yaml(config)
    match_review = MatchReview.load(review_file)
    questions = parse_files(list(questions_dir.glob("*.txt")))
    generate_study_guide(cfg, questions, match_review, output)
    console.print(f"[green]Generated study guide:[/] {output}")


@app.command()
def generate_review(
    config: Path = typer.Option(..., "--config", "-c", help="Subject outline YAML file"),
    output: Path = typer.Option(..., "--output", "-o", help="Output Word document path"),
) -> None:
    """Generate review points + real-life examples Word document."""
    cfg = SubjectConfig.from_yaml(config)
    generate_review_points(cfg, output)
    console.print(f"[green]Generated review points:[/] {output}")


@app.command()
def full(
    config: Path = typer.Option(..., "--config", "-c", help="Subject outline YAML file"),
    input_dir: Path = typer.Option(..., "--input-dir", "-i", help="Question bank files directory"),
    output_dir: Path = typer.Option(..., "--output-dir", "-o", help="Output directory"),
    threshold: float = typer.Option(1.5, "--threshold", "-t", help="Minimum auto-match score"),
    skip_review: bool = typer.Option(
        False, "--skip-review", help="Skip interactive review (not recommended)"
    ),
    manual_file: Path | None = typer.Option(
        None, "--manual-file", "-m", help="Optional manual assignments YAML"
    ),
) -> None:
    """Run full pipeline: extract → match → (review) → generate."""
    output_dir.mkdir(parents=True, exist_ok=True)
    extracted_dir = output_dir / "extracted"
    review_file = output_dir / "match_review.json"
    study_guide_path = output_dir / "study_guide.docx"
    review_points_path = output_dir / "review_points.docx"

    console.print("[bold]Step 1/4:[/] Extracting question banks...")
    extract(input_dir, extracted_dir)

    console.print("\n[bold]Step 2/4:[/] Matching questions to outline...")
    match(config, extracted_dir, review_file, threshold, manual_file)

    if not skip_review:
        console.print("\n[bold]Step 3/4:[/] Review matches...")
        do_review = Prompt.ask(
            "Launch interactive review now?", choices=["y", "n"], default="y"
        )
        if do_review == "y":
            review(review_file, output_dir / "manual_assignments.yaml")

    console.print("\n[bold]Step 4/4:[/] Generating documents...")
    generate(config, review_file, study_guide_path, extracted_dir)
    generate_review(config, review_points_path)

    console.print("\n[bold green]Done![/]")
    console.print(f"  Study guide: {study_guide_path}")
    console.print(f"  Review points: {review_points_path}")
    console.print(f"  Review file: {review_file}")


if __name__ == "__main__":
    app()
