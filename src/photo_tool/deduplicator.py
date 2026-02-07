"""Duplicate detection and classification (read-only)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from photo_tool.scanner import FileInfo


@dataclass(frozen=True)
class DuplicateGroup:
    content_hash: str
    original: Path
    duplicates: List[Path]


def _hash_file(path: Path) -> str | None:
    try:
        hasher = sha256()
        with path.open("rb") as handle:
            while True:
                chunk = handle.read(1024 * 1024)
                if not chunk:
                    break
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        return None


def _select_original(
    candidates: List[Path],
    resolved_datetimes: Dict[Path, datetime],
) -> Tuple[Path, List[Path]]:
    def sort_key(path: Path) -> tuple[datetime, str]:
        return (resolved_datetimes.get(path, datetime.max), str(path))

    ordered = sorted(candidates, key=sort_key)
    return ordered[0], ordered[1:]


def find_duplicates(
    *,
    files: Iterable[FileInfo],
    resolved_datetimes: Dict[Path, datetime],
) -> List[DuplicateGroup]:
    size_groups: dict[int, list[FileInfo]] = {}
    for info in files:
        size_groups.setdefault(info.size_bytes, []).append(info)

    duplicates: list[DuplicateGroup] = []

    for size, group in size_groups.items():
        if len(group) < 2:
            continue

        hash_groups: dict[str, list[Path]] = {}
        for info in sorted(group, key=lambda item: str(item.absolute_path)):
            content_hash = _hash_file(info.absolute_path)
            if content_hash is None:
                continue
            hash_groups.setdefault(content_hash, []).append(info.absolute_path)

        for content_hash, paths in hash_groups.items():
            if len(paths) < 2:
                continue

            original, dupes = _select_original(paths, resolved_datetimes)
            duplicates.append(
                DuplicateGroup(
                    content_hash=content_hash,
                    original=original,
                    duplicates=dupes,
                )
            )

    duplicates.sort(key=lambda group: (group.content_hash, str(group.original)))
    return duplicates
