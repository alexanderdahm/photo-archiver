from pathlib import Path
import pytest

from photo_tool.config import load_config, ConfigError


def test_load_valid_config(tmp_path: Path):
    config_file = tmp_path / "config.yaml"
    config_file.write_text(
        """
paths:
  archive_root: "D:/Photos"
  unsorted: "D:/Photos/_unsorted"
  report_output: "D:/Photos/_reports"

behavior:
  dry_run: true
  move_files: false
  normalize_month_folders: true

naming:
  month_format: "MM_MonthName"
  filename_format: "YYYY-MM-DD_HH-mm-ss_source"

duplicates:
  detect: true
  mode: "report-only"

reporting:
  markdown: true
  json: true
  verbose: true
""",
        encoding="utf-8",
    )

    config = load_config(config_file)

    assert config.behavior.dry_run is True
    assert config.paths.archive_root.name == "Photos"


def test_missing_config_file():
    with pytest.raises(ConfigError):
        load_config(Path("does_not_exist.yaml"))


def test_invalid_root_structure(tmp_path: Path):
  config_file = tmp_path / "config.yaml"
  config_file.write_text("", encoding="utf-8")

  with pytest.raises(ConfigError):
    load_config(config_file)


def test_missing_required_key(tmp_path: Path):
  config_file = tmp_path / "config.yaml"
  config_file.write_text(
    """
paths:
  unsorted: "D:/Photos/_unsorted"
  report_output: "D:/Photos/_reports"
""",
    encoding="utf-8",
  )

  with pytest.raises(ConfigError):
    load_config(config_file)
