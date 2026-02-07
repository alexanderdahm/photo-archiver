"""Reporting utilities for processed photos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
from typing import Iterable, List

from media_archiver.sorter import SortDecision


@dataclass(frozen=True)
class ReportEntry:
    source_path: str
    target_path: str
    action: str
    performed: bool
    reason: str | None


@dataclass(frozen=True)
class ReportSummary:
    timestamp: str
    dry_run: bool
    move_files: bool
    total_files: int
    copied: int
    moved: int
    skipped: int
    errors: int


@dataclass(frozen=True)
class Report:
    summary: ReportSummary
    entries: List[ReportEntry]
    errors: List[str]


@dataclass(frozen=True)
class ReportConfig:
    dry_run: bool
    move_files: bool


@dataclass(frozen=True)
class ExecutionResult:
    decision: SortDecision
    performed: bool
    error: str | None = None


def build_report(
    *,
    results: Iterable[ExecutionResult],
    config: ReportConfig,
    timestamp: str,
) -> Report:
    entries: list[ReportEntry] = []
    # errors only count execution/runtime errors, not skips
    errors: list[str] = []

    for item in results:
        reason = item.decision.reason
        if item.error:
            reason = item.error
            errors.append(item.error)

        entries.append(
            ReportEntry(
                source_path=str(item.decision.source),
                target_path=str(item.decision.target_path),
                action=item.decision.action,
                performed=item.performed,
                reason=reason,
            )
        )

    entries.sort(
        key=lambda entry: (
            Path(entry.target_path).parent,
            Path(entry.target_path).name,
            entry.source_path,
        )
    )

    copied = sum(1 for e in entries if e.action == "copy" and e.performed)
    moved = sum(1 for e in entries if e.action == "move" and e.performed)
    skipped = sum(1 for e in entries if e.action == "skip")

    summary = ReportSummary(
        timestamp=timestamp,
        dry_run=config.dry_run,
        move_files=config.move_files,
        total_files=len(entries),
        copied=copied,
        moved=moved,
        skipped=skipped,
        errors=len(errors),
    )

    return Report(summary=summary, entries=entries, errors=errors)


def _report_to_dict(report: Report) -> dict:
    return {
        "summary": {
            "timestamp": report.summary.timestamp,
            "dry_run": report.summary.dry_run,
            "move_files": report.summary.move_files,
            "total_files": report.summary.total_files,
            "copied": report.summary.copied,
            "moved": report.summary.moved,
            "skipped": report.summary.skipped,
            "errors": report.summary.errors,
        },
        "entries": [
            {
                "source_path": entry.source_path,
                "target_path": entry.target_path,
                "action": entry.action,
                "performed": entry.performed,
                "reason": entry.reason,
            }
            for entry in report.entries
        ],
        "errors": list(report.errors),
    }


def to_json(report: Report) -> str:
    return json.dumps(_report_to_dict(report), indent=2, ensure_ascii=False, sort_keys=True)


def to_markdown(report: Report) -> str:
    summary = report.summary
    lines: list[str] = ["# Report", "", "## Summary", ""]
    lines.extend(
        [
            f"- Timestamp: {summary.timestamp}",
            f"- Dry-run: {summary.dry_run}",
            f"- Move files: {summary.move_files}",
            f"- Total files: {summary.total_files}",
            f"- Files copied: {summary.copied}",
            f"- Files moved: {summary.moved}",
            f"- Files skipped: {summary.skipped}",
            f"- Errors: {summary.errors}",
            "",
            "## Detailed Actions",
            "",
        ]
    )

    for entry in report.entries:
        reason = entry.reason or ""
        lines.extend(
            [
                f"- Source: {entry.source_path}",
                f"  Target: {entry.target_path}",
                f"  Action: {entry.action}",
                f"  Performed: {entry.performed}",
                f"  Reason: {reason}",
            ]
        )

    lines.extend(["", "## Errors", ""])
    if report.errors:
        lines.extend([f"- {error}" for error in report.errors])
    else:
        lines.append("- None")

    return "\n".join(lines)


def _ensure_unique_path(base_path: Path) -> Path:
    if not base_path.exists():
        return base_path

    stem = base_path.stem
    suffix = base_path.suffix
    index = 1
    while True:
        candidate = base_path.with_name(f"{stem}_{index:02d}{suffix}")
        if not candidate.exists():
            return candidate
        index += 1


def write_reports(
    *,
    report: Report,
    output_dir: Path,
    prefix: str = "report",
) -> tuple[Path, Path]:
    # timestamp must be externally provided (no time generation here)
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = f"{report.summary.timestamp}_{prefix}"
    markdown_path = _ensure_unique_path(output_dir / f"{base_name}.md")
    json_path = _ensure_unique_path(output_dir / f"{base_name}.json")

    markdown_path.write_text(to_markdown(report), encoding="utf-8")
    json_path.write_text(to_json(report), encoding="utf-8")

    return markdown_path, json_path
