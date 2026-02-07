import argparse
import sys
from pathlib import Path

from photo_tool.config import load_config, ConfigError


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="photo-tool",
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


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config(Path(args.config))
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    # Phase 1 ends here: no filesystem operations allowed
    # Future phases will be invoked from here

    if args.apply and config.behavior.dry_run:
        print(
            "Warning: --apply provided but config is set to dry_run=true",
            file=sys.stderr,
        )

    print("Configuration loaded successfully.")
    print(f"Dry-run mode: {config.behavior.dry_run and not args.apply}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
