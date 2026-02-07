"""Filename generation and deterministic collision handling."""

from datetime import datetime
from pathlib import Path
from typing import Iterable

from media_archiver.models import DateTimeSource


def _format_base_name(
    *,
    original_name: str,
    resolved_datetime: datetime,
    source: DateTimeSource,
) -> str:
    extension = Path(original_name).suffix.lower()
    if not extension:
        extension = ""
    timestamp = resolved_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    return f"{timestamp}{extension}"


def _apply_collision_suffix(base_name: str, existing: Iterable[str]) -> str:
    existing_set = {name.strip().lower() for name in existing}
    if base_name.lower() not in existing_set:
        return base_name

    stem = Path(base_name).stem
    suffix = Path(base_name).suffix

    index = 1
    while True:
        candidate = f"{stem}_{index:02d}{suffix}"
        if candidate.lower() not in existing_set:
            return candidate
        index += 1


def ensure_unique_name(*, original_name: str, existing_names: Iterable[str]) -> str:
    return _apply_collision_suffix(original_name, existing_names)


def generate_filename(
    *,
    original_name: str,
    resolved_datetime: datetime,
    source: DateTimeSource,
    existing_names: Iterable[str],
) -> str:
    base = _format_base_name(
        original_name=original_name,
        resolved_datetime=resolved_datetime,
        source=source,
    )
    return _apply_collision_suffix(base, existing_names)
