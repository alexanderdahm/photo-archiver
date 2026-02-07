"""Resolve a datetime for a photo from various sources."""

from datetime import datetime
import re
from typing import Any

from media_archiver.models import ConfidenceLevel, DateTimeResolution, DateTimeSource


_PATTERN_WHATSAPP = re.compile(r"^IMG-(\d{8})-WA\d+", re.IGNORECASE)
_PATTERN_UNDERSCORE = re.compile(r"^(?:IMG|VID)_(\d{8})_(\d{6})", re.IGNORECASE)
# Matches any YYYY-MM-DD occurrence in filename
_PATTERN_DASHED = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

_EXIF_FALLBACK_FORMATS = ["%Y:%m:%d %H:%M:%S"]


def _coerce_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.replace(tzinfo=None)
        return value
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            parsed = None

        if parsed is not None:
            if parsed.tzinfo is not None:
                return parsed.replace(tzinfo=None)
            return parsed

        for fmt in _EXIF_FALLBACK_FORMATS:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue
    return None


def _parse_from_filename(filename: str) -> datetime | None:
    match = _PATTERN_WHATSAPP.search(filename)
    if match:
        return datetime.strptime(match.group(1), "%Y%m%d")

    match = _PATTERN_UNDERSCORE.search(filename)
    if match:
        return datetime.strptime(match.group(1) + match.group(2), "%Y%m%d%H%M%S")

    match = _PATTERN_DASHED.search(filename)
    if match:
        return datetime.strptime(match.group(0), "%Y-%m-%d")

    return None


def resolve_datetime(
    *,
    filename: str,
    exif_datetime: str | datetime | None,
    fs_modified: str | datetime,
) -> DateTimeResolution:
    exif_value = _coerce_datetime(exif_datetime)
    if exif_value is not None:
        return DateTimeResolution(
            datetime=exif_value,
            source=DateTimeSource.EXIF,
            confidence=ConfidenceLevel.HIGH,
        )

    filename_value = _parse_from_filename(filename)
    if filename_value is not None:
        return DateTimeResolution(
            datetime=filename_value,
            source=DateTimeSource.FILENAME,
            confidence=ConfidenceLevel.MEDIUM,
        )

    fs_value = _coerce_datetime(fs_modified)
    if fs_value is None:
        raise ValueError("Filesystem modified time must be provided")

    return DateTimeResolution(
        datetime=fs_value,
        source=DateTimeSource.FILESYSTEM,
        confidence=ConfidenceLevel.LOW,
    )
