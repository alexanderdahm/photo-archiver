from pathlib import Path
from unittest.mock import patch

from photo_tool.scanner import scan_directories


class _FakeStat:
    def __init__(self, size: int, mtime: float):
        self.st_size = size
        self.st_mtime = mtime


def test_scan_directories_filters_and_reports():
    dirs = [Path("C:/Photos/B"), Path("C:/Photos/A")]

    files_a = [
        Path("C:/Photos/A/2.txt"),
        Path("C:/Photos/A/1.jpg"),
    ]
    files_b = [
        Path("C:/Photos/B/3.mp4"),
        Path("C:/Photos/B/4.doc"),
    ]

    def fake_rglob(self, pattern):
        if str(self).endswith("A"):
            return files_a
        return files_b

    def fake_is_file(self):
        return True

    def fake_stat(self):
        return _FakeStat(size=123, mtime=456.0)

    with (
        patch.object(Path, "rglob", fake_rglob),
        patch.object(Path, "stat", fake_stat),
        patch.object(Path, "is_file", fake_is_file),
        patch.object(Path, "exists", lambda self: True),
    ):
        result = scan_directories(dirs)

    supported_names = [item.name for item in result.supported]
    ignored_names = [item.absolute_path.name for item in result.ignored]

    assert supported_names == ["1.jpg", "3.mp4"]
    assert ignored_names == ["2.txt", "4.doc"]


def test_scan_directories_is_deterministic():
    dirs = [Path("C:/Photos/B"), Path("C:/Photos/A")]
    files_a = [Path("C:/Photos/A/a.jpg")]
    files_b = [Path("C:/Photos/B/z.png"), Path("C:/Photos/B/b.jpeg")]

    def fake_rglob(self, pattern):
        if str(self).endswith("A"):
            return list(reversed(files_a))
        return list(reversed(files_b))

    def fake_is_file(self):
        return True

    def fake_stat(self):
        return _FakeStat(size=1, mtime=2.0)

    with (
        patch.object(Path, "rglob", fake_rglob),
        patch.object(Path, "stat", fake_stat),
        patch.object(Path, "is_file", fake_is_file),
        patch.object(Path, "exists", lambda self: True),
    ):
        result = scan_directories(dirs)

    ordered = [item.name for item in result.supported]
    assert ordered == ["a.jpg", "b.jpeg", "z.png"]


def test_scan_ignores_directories_and_stat_failures():
    dirs = [Path("C:/Photos/A")]
    candidates = [
        Path("C:/Photos/A/dir"),
        Path("C:/Photos/A/ok.jpg"),
        Path("C:/Photos/A/broken.jpg"),
    ]

    def fake_rglob(self, pattern):
        return candidates

    def fake_is_file(self):
        return self.name != "dir"

    def fake_stat(self):
        if self.name == "broken.jpg":
            raise OSError("stat failed")
        return _FakeStat(size=10, mtime=20.0)

    with (
        patch.object(Path, "rglob", fake_rglob),
        patch.object(Path, "is_file", fake_is_file),
        patch.object(Path, "stat", fake_stat),
        patch.object(Path, "exists", lambda self: True),
    ):
        result = scan_directories(dirs)

    supported = [item.name for item in result.supported]
    ignored = [item.absolute_path.name for item in result.ignored]

    assert supported == ["ok.jpg"]
    assert "broken.jpg" in ignored
    assert "dir" not in ignored


def test_scan_reports_missing_directories():
    dirs = [Path("C:/Photos/Missing")]

    with (
        patch.object(Path, "exists", lambda self: False),
        patch.object(Path, "rglob", lambda self, pattern: []),
    ):
        result = scan_directories(dirs)

    assert len(result.supported) == 0
    assert len(result.ignored) == 1
    assert result.ignored[0].reason == "directory_not_found"
