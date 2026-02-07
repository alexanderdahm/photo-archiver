from pathlib import Path

from media_archiver.cli import main


def test_cli_apply_cleans_empty_unsorted_dirs(tmp_path: Path):
    archive = tmp_path / "archive"
    unsorted = tmp_path / "unsorted"
    reports = tmp_path / "reports"
    archive.mkdir()
    unsorted.mkdir()
    reports.mkdir()

    nested = unsorted / "camera"
    nested.mkdir()

    source = nested / "IMG-20210914_203344.jpg"
    source.write_text("x", encoding="utf-8")

    config = tmp_path / "config.yaml"
    config.write_text(
        f"""
paths:
  archive_root: "{archive.as_posix()}"
  unsorted: "{unsorted.as_posix()}"
  report_output: "{reports.as_posix()}"

behavior:
  dry_run: false
  move_files: true
  normalize_month_folders: true

naming:
  month_format: "MM_Month"
  filename_format: "YYYY-MM-DD_HH-mm-ss"
  preserve_original_filename: false

duplicates:
  detect: true
  mode: "report-only"

reporting:
  markdown: false
  json: false
  verbose: false
""",
        encoding="utf-8",
    )

    exit_code = main(["--config", str(config)])
    assert exit_code == 0

    assert not nested.exists()
    assert not source.exists()
    assert any(archive.rglob("*.jpg"))
