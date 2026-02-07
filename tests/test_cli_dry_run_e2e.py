from pathlib import Path

from media_archiver.cli import main


def test_cli_dry_run_creates_full_report(tmp_path: Path):
    archive = tmp_path / "archive"
    unsorted = tmp_path / "unsorted"
    reports = tmp_path / "reports"
    archive.mkdir()
    unsorted.mkdir()
    reports.mkdir()

    source = unsorted / "IMG-20210914_203344.jpg"
    source.write_text("x", encoding="utf-8")
    second = unsorted / "IMG-20210914_203344(1).jpg"
    second.write_text("x", encoding="utf-8")

    config = tmp_path / "config.yaml"
    config.write_text(
        f"""
paths:
  archive_root: "{archive.as_posix()}"
  unsorted: "{unsorted.as_posix()}"
  report_output: "{reports.as_posix()}"

behavior:
  dry_run: true
  move_files: false
  normalize_month_folders: true

naming:
  month_format: "MM_Month"
  filename_format: "YYYY-MM-DD_HH-mm-ss"
  preserve_original_filename: false

duplicates:
  detect: true
  mode: "report-only"

reporting:
  markdown: true
  json: true
  verbose: false
""",
        encoding="utf-8",
    )

    exit_code = main(["--config", str(config)])
    assert exit_code == 0

    assert source.exists()
    assert not any(archive.rglob("*"))

    md_reports = list(reports.glob("*.md"))
    json_reports = list(reports.glob("*.json"))
    assert len(md_reports) == 1
    assert len(json_reports) == 1

    text = json_reports[0].read_text(encoding="utf-8")
    assert '"action": "copy"' in text
    assert '"performed": false' in text
    assert "_01" in text
