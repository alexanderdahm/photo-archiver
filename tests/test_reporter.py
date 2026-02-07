from datetime import datetime
from pathlib import Path

from media_archiver.reporter import (
    ExecutionResult,
    ReportConfig,
    build_report,
    _ensure_unique_path,
    to_json,
    to_markdown,
)
from media_archiver.sorter import SortDecision


def _make_decision(source: str, target: str, action: str, reason: str | None):
    return SortDecision(
        source=Path(source),
        target_dir=Path(target).parent,
        target_path=Path(target),
        action=action,
        reason=reason,
    )


def test_report_summary_counts_and_ordering():
    results = [
        ExecutionResult(
            decision=_make_decision(
                "D:/Photos/_unsorted/B.jpg",
                "D:/Photos/2021/08_August/B.jpg",
                "copy",
                None,
            ),
            performed=False,
        ),
        ExecutionResult(
            decision=_make_decision(
                "D:/Photos/_unsorted/A.jpg",
                "D:/Photos/2019/12_Dezember/A.jpg",
                "move",
                None,
            ),
            performed=True,
        ),
        ExecutionResult(
            decision=_make_decision(
                "D:/Photos/_unsorted/C.jpg",
                "D:/Photos/2020/01_Januar/C.jpg",
                "skip",
                "target_exists",
            ),
            performed=False,
            error="target already exists",
        ),
    ]

    report = build_report(
        results=results,
        config=ReportConfig(dry_run=False, move_files=True),
        timestamp="2025-01-01T00-00-00",
    )

    assert report.summary.total_files == 3
    assert report.summary.copied == 0
    assert report.summary.moved == 1
    assert report.summary.skipped == 1
    assert report.summary.errors == 1

    assert Path(report.entries[0].target_path).as_posix().endswith("12_Dezember/A.jpg")
    assert Path(report.entries[1].target_path).as_posix().endswith("01_Januar/C.jpg")
    assert Path(report.entries[2].target_path).as_posix().endswith("08_August/B.jpg")


def test_markdown_and_json_are_deterministic():
    decision = _make_decision(
        "D:/Photos/_unsorted/A.jpg",
        "D:/Photos/2019/12_Dezember/A.jpg",
        "copy",
        None,
    )
    result = ExecutionResult(decision=decision, performed=True)

    report = build_report(
        results=[result],
        config=ReportConfig(dry_run=True, move_files=False),
        timestamp="2025-01-01T00-00-00",
    )

    markdown = to_markdown(report)
    json_output = to_json(report)

    assert "Timestamp: 2025-01-01T00-00-00" in markdown
    assert "Dry-run: True" in markdown
    assert "\"dry_run\": true" in json_output
    assert "\"action\": \"copy\"" in json_output


def test_dry_run_vs_apply_reports_only_differ_in_performed():
    decision = _make_decision(
        "D:/Photos/_unsorted/A.jpg",
        "D:/Photos/2019/12_Dezember/A.jpg",
        "copy",
        None,
    )

    report_dry = build_report(
        results=[ExecutionResult(decision=decision, performed=False)],
        config=ReportConfig(dry_run=True, move_files=False),
        timestamp="2025-01-01T00-00-00",
    )

    report_apply = build_report(
        results=[ExecutionResult(decision=decision, performed=True)],
        config=ReportConfig(dry_run=False, move_files=False),
        timestamp="2025-01-01T00-00-00",
    )

    assert report_dry.entries[0].source_path == report_apply.entries[0].source_path
    assert report_dry.entries[0].target_path == report_apply.entries[0].target_path
    assert report_dry.entries[0].action == report_apply.entries[0].action
    assert report_dry.entries[0].reason == report_apply.entries[0].reason
    assert report_dry.entries[0].performed is False
    assert report_apply.entries[0].performed is True


def test_ensure_unique_path(tmp_path: Path):
    base = tmp_path / "report.json"
    base.write_text("one", encoding="utf-8")
    first = _ensure_unique_path(base)
    first.write_text("two", encoding="utf-8")

    second = _ensure_unique_path(base)

    assert first.name == "report_01.json"
    assert second.name == "report_02.json"


def test_ensure_unique_path_when_unused(tmp_path: Path):
    base = tmp_path / "report.json"
    result = _ensure_unique_path(base)
    assert result == base
