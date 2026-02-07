"""Deduplication helpers."""

from pathlib import Path


def find_duplicates(photos):
    """Placeholder: dedupe by file size and name."""
    seen = {}
    for p in photos:
        key = (p.stat().st_size, p.name)
        seen.setdefault(key, []).append(p)
    return [group for group in seen.values() if len(group) > 1]
