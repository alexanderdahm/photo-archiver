from dataclasses import dataclass
from pathlib import Path
import yaml


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class PathsConfig:
    archive_root: Path
    unsorted: Path
    report_output: Path


@dataclass(frozen=True)
class BehaviorConfig:
    dry_run: bool
    move_files: bool
    normalize_month_folders: bool


@dataclass(frozen=True)
class NamingConfig:
    month_format: str
    filename_format: str
    preserve_original_filename: bool


@dataclass(frozen=True)
class DuplicateConfig:
    detect: bool
    mode: str


@dataclass(frozen=True)
class ReportingConfig:
    markdown: bool
    json: bool
    verbose: bool


@dataclass(frozen=True)
class AppConfig:
    paths: PathsConfig
    behavior: BehaviorConfig
    naming: NamingConfig
    duplicates: DuplicateConfig
    reporting: ReportingConfig


def _require(mapping: dict, key: str):
    if not isinstance(mapping, dict):
        raise ConfigError("Invalid config structure: expected mapping")
    if key not in mapping:
        raise ConfigError(f"Missing required config key: {key}")
    return mapping[key]


def _optional(mapping: dict, key: str, default):
    if not isinstance(mapping, dict):
        raise ConfigError("Invalid config structure: expected mapping")
    return mapping.get(key, default)


def load_config(path: Path) -> AppConfig:
    if not path.exists():
        raise ConfigError(f"Config file does not exist: {path}")

    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ConfigError("Invalid config structure: root must be a mapping")

    try:
        paths = PathsConfig(
            archive_root=Path(_require(raw["paths"], "archive_root")),
            unsorted=Path(_require(raw["paths"], "unsorted")),
            report_output=Path(_require(raw["paths"], "report_output")),
        )

        behavior = BehaviorConfig(
            dry_run=bool(_require(raw["behavior"], "dry_run")),
            move_files=bool(_require(raw["behavior"], "move_files")),
            normalize_month_folders=bool(
                _require(raw["behavior"], "normalize_month_folders")
            ),
        )

        naming = NamingConfig(
            month_format=_require(raw["naming"], "month_format"),
            filename_format=_require(raw["naming"], "filename_format"),
            preserve_original_filename=bool(
                _optional(raw["naming"], "preserve_original_filename", False)
            ),
        )

        duplicates = DuplicateConfig(
            detect=bool(_require(raw["duplicates"], "detect")),
            mode=_require(raw["duplicates"], "mode"),
        )

        reporting = ReportingConfig(
            markdown=bool(_require(raw["reporting"], "markdown")),
            json=bool(_require(raw["reporting"], "json")),
            verbose=bool(_require(raw["reporting"], "verbose")),
        )

    except KeyError as exc:
        raise ConfigError(f"Invalid config structure: {exc}") from exc

    return AppConfig(
        paths=paths,
        behavior=behavior,
        naming=naming,
        duplicates=duplicates,
        reporting=reporting,
    )
