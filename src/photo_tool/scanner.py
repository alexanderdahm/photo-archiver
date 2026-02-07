"""Read-only filesystem scanning utilities."""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


SUPPORTED_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".heic"})
SUPPORTED_VIDEO_EXTENSIONS = frozenset({".mp4", ".mov", ".avi"})
SUPPORTED_EXTENSIONS = SUPPORTED_IMAGE_EXTENSIONS | SUPPORTED_VIDEO_EXTENSIONS


@dataclass(frozen=True)
class FileInfo:
    absolute_path: Path
    name: str
    extension: str
    size_bytes: int
    modified_timestamp: float


@dataclass(frozen=True)
class IgnoredFile:
    absolute_path: Path
    extension: str
    reason: str


@dataclass(frozen=True)
class ScanResult:
    supported: List[FileInfo]
    ignored: List[IgnoredFile]


def _iter_files(directories: Iterable[Path]) -> List[Path]:
    files: list[Path] = []
    for directory in sorted(directories, key=lambda d: str(d)):
        for candidate in directory.rglob("*"):
            if candidate.is_file():
                files.append(candidate)
    return sorted(files, key=lambda p: str(p))


def _collect_file_info(path: Path) -> FileInfo | None:
    try:
        stat_result = path.stat()
    except OSError:
        return None
    return FileInfo(
        absolute_path=path.resolve(strict=False),
        name=path.name,
        extension=path.suffix.lower(),
        size_bytes=stat_result.st_size,
        modified_timestamp=stat_result.st_mtime,
    )


def scan_directories(directories: Iterable[Path]) -> ScanResult:
    supported: list[FileInfo] = []
    ignored: list[IgnoredFile] = []

    directory_list = sorted(directories, key=lambda d: str(d))
    for directory in directory_list:
        if not directory.exists():
            ignored.append(
                IgnoredFile(
                    absolute_path=directory.resolve(strict=False),
                    extension="",
                    reason="directory_not_found",
                )
            )

    for path in _iter_files(directory_list):
        extension = path.suffix.lower()
        if extension in SUPPORTED_EXTENSIONS:
            info = _collect_file_info(path)
            if info is None:
                ignored.append(
                    IgnoredFile(
                        absolute_path=path.resolve(strict=False),
                        extension=extension,
                        reason="stat_failed",
                    )
                )
            else:
                supported.append(info)
        else:
            ignored.append(
                IgnoredFile(
                    absolute_path=path.resolve(strict=False),
                    extension=extension,
                    reason="unsupported_extension",
                )
            )

    return ScanResult(supported=supported, ignored=ignored)
