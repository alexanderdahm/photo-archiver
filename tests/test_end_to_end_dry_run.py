from datetime import datetime
from pathlib import Path

from media_archiver.datetime_resolver import resolve_datetime
from media_archiver.executor import execute_decision
from media_archiver.month_normalizer import normalize_month_folder
from media_archiver.renamer import generate_filename
from media_archiver.reporter import ExecutionResult, ReportConfig, build_report, write_reports
from media_archiver.sorter import build_sort_decision
from media_archiver.models import DateTimeSource


_MONTH_NAME_BY_NUMBER = {
    1: "Januar",
    2: "Februar",
    3: "Maerz",
    4: "April",
    5: "Mai",
    6: "Juni",
    7: "Juli",
    8: "August",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Dezember",
}


def test_end_to_end_dry_run(tmp_path: Path):
    archive = tmp_path / "archive"
    unsorted = tmp_path / "unsorted"
    reports = tmp_path / "reports"
    archive.mkdir()
    unsorted.mkdir()

    source_path = unsorted / "IMG-20210914_203344.jpg"
    source_path.write_text("x", encoding="utf-8")

    fs_modified = datetime.fromtimestamp(source_path.stat().st_mtime)
    resolution = resolve_datetime(
        filename=source_path.name,
        exif_datetime=None,
        fs_modified=fs_modified,
    )

    canonical_name = generate_filename(
        original_name=source_path.name,
        resolved_datetime=resolution.datetime,
        source=resolution.source,
        existing_names=[],
    )

    # simulate month folder name as produced by Phase 4
    month_folder = normalize_month_folder("August")
    assert month_folder is not None

    decision = build_sort_decision(
        archive_root=archive,
        source_path=source_path,
        resolved_datetime=resolution.datetime,
        month_folder=month_folder,
        canonical_name=canonical_name,
        move_files=False,
        target_exists=False,
    )

    performed = execute_decision(decision=decision, apply=False)

    result = ExecutionResult(decision=decision, performed=performed)
    report = build_report(
        results=[result],
        config=ReportConfig(dry_run=True, move_files=False),
        timestamp="2025-01-01T00-00-00",
    )

    markdown_path, json_path = write_reports(
        report=report,
        output_dir=reports,
        prefix="dry_run",
    )

    assert source_path.exists()
    assert not (archive / month_folder / canonical_name).exists()
    assert markdown_path.exists()
    assert json_path.exists()

    json_text = json_path.read_text(encoding="utf-8")
    assert "\"source_path\"" in json_text
    assert "\"target_path\"" in json_text
    assert "\"action\": \"copy\"" in json_text
    assert "\"performed\": false" in json_text
