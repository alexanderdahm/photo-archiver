"""Data models used by media_archiver."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path


class DateTimeSource(str, Enum):
    EXIF = "exif"
    FILENAME = "filename"
    FILESYSTEM = "filesystem"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass(frozen=True)
class DateTimeResolution:
    datetime: datetime
    source: DateTimeSource
    confidence: ConfidenceLevel


