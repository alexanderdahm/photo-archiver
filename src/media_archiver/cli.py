import argparse
from collections import defaultdict
from datetime import datetime
import sys
from pathlib import Path

from media_archiver.config import load_config, ConfigError, AppConfig
from media_archiver.datetime_resolver import resolve_datetime
from media_archiver.executor import execute_decision
from media_archiver.month_normalizer import normalize_month_folder
from media_archiver.renamer import ensure_unique_name, generate_filename
from media_archiver.reporter import ExecutionResult, ReportConfig, build_report, write_reports
from media_archiver.scanner import scan_directories
from media_archiver.sorter import SortDecision, build_sort_decision


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="media-archiver",
        description="Deterministic photo and video archive organizer",
    )

    parser.add_argument(
        "--config",
        required=True,
        help="Path to configuration YAML file",
    )

    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply changes to filesystem (default is dry-run)",
    )

    return parser.parse_args(argv)


_MONTH_NAMES = {
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


def _month_name_from_datetime(value: datetime) -> str:
    return _MONTH_NAMES[value.month]


def _current_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")


def _cleanup_empty_dirs(root: Path, candidates: set[Path]) -> None:
    for directory in sorted(candidates, key=lambda p: len(p.parts), reverse=True):
        if directory == root:
            continue
        try:
            if directory.exists() and directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
        except OSError:
            continue


def run_pipeline(config: AppConfig, apply: bool) -> tuple[Path | None, Path | None]:
    scan_result = scan_directories([config.paths.unsorted])

    planned_names: dict[Path, set[str]] = defaultdict(set)
    execution_results: list[ExecutionResult] = []

    current_time = datetime.now()

    cleanup_candidates: set[Path] = set()

    for info in scan_result.supported:
        resolution = resolve_datetime(
            filename=info.name,
            exif_datetime=None,
            fs_modified=datetime.fromtimestamp(info.modified_timestamp),
        )

        month_folder = normalize_month_folder(
            _month_name_from_datetime(resolution.datetime)
        )
        if month_folder is None:
            continue

        target_dir = config.paths.archive_root / f"{resolution.datetime.year:04d}" / month_folder
        existing_names = planned_names[target_dir]

        if config.naming.preserve_original_filename:
            canonical_name = ensure_unique_name(
                original_name=info.name,
                existing_names=existing_names,
            )
        else:
            canonical_name = generate_filename(
                original_name=info.name,
                resolved_datetime=resolution.datetime,
                source=resolution.source,
                existing_names=existing_names,
            )

        planned_names[target_dir].add(canonical_name)
        target_path = target_dir / canonical_name

        if resolution.datetime > current_time:
            decision = SortDecision(
                source=info.absolute_path,
                target_dir=target_dir,
                target_path=target_path,
                action="skip",
                reason="future_date",
            )
        else:
            target_exists = target_path.exists()
            decision = build_sort_decision(
                archive_root=config.paths.archive_root,
                source_path=info.absolute_path,
                resolved_datetime=resolution.datetime,
                month_folder=month_folder,
                canonical_name=canonical_name,
                move_files=config.behavior.move_files,
                target_exists=target_exists,
            )

        performed = execute_decision(
            decision=decision,
            apply=apply,
        )

        if performed and decision.action == "move":
            cleanup_candidates.add(decision.source.parent)

        execution_results.append(
            ExecutionResult(decision=decision, performed=performed)
        )

    report = build_report(
        results=execution_results,
        config=ReportConfig(
            dry_run=not apply,
            move_files=config.behavior.move_files,
        ),
        timestamp=_current_timestamp(),
    )

    if apply and cleanup_candidates:
        _cleanup_empty_dirs(config.paths.unsorted, cleanup_candidates)

    if config.reporting.markdown or config.reporting.json:
        return write_reports(
            report=report,
            output_dir=config.paths.report_output,
            prefix="dry_run" if not apply else "apply",
        )

    return None, None


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config(Path(args.config))
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    if args.apply and config.behavior.dry_run:
        print(
            "WARNING: --apply was provided, but config.behavior.dry_run is true. "
            "No filesystem changes will be performed.",
            file=sys.stderr,
        )
    apply = (args.apply or not config.behavior.dry_run) and not config.behavior.dry_run
    mode_label = "apply" if apply else "dry-run"
    print(f"Starting media-archiver ({mode_label})")

    markdown_path, json_path = run_pipeline(config, apply)

    if markdown_path and json_path:
        print(f"Report written to: {markdown_path}")
        print(f"Report written to: {json_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
