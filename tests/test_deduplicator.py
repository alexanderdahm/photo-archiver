from datetime import datetime
from pathlib import Path

from photo_tool.deduplicator import find_duplicates
from photo_tool.scanner import FileInfo


def _make_file_info(path: Path) -> FileInfo:
    stat = path.stat()
    return FileInfo(
        absolute_path=path,
        name=path.name,
        extension=path.suffix.lower(),
        size_bytes=stat.st_size,
        modified_timestamp=stat.st_mtime,
    )


def test_find_duplicates_groups_and_selects_original(tmp_path: Path):
    file_a = tmp_path / "a.jpg"
    file_b = tmp_path / "b.jpg"
    file_c = tmp_path / "c.jpg"
    file_d = tmp_path / "d.jpg"

    file_a.write_bytes(b"same")
    file_b.write_bytes(b"same")
    file_c.write_bytes(b"same")
    file_d.write_bytes(b"different")

    files = [_make_file_info(file_a), _make_file_info(file_b), _make_file_info(file_c), _make_file_info(file_d)]

    resolved_datetimes = {
        file_a: datetime(2020, 1, 1, 0, 0, 1),
        file_b: datetime(2019, 12, 31, 23, 59, 59),
        file_c: datetime(2020, 1, 2, 0, 0, 0),
        file_d: datetime(2020, 1, 3, 0, 0, 0),
    }

    groups = find_duplicates(files=files, resolved_datetimes=resolved_datetimes)

    assert len(groups) == 1
    group = groups[0]
    assert group.original == file_b
    assert set(group.duplicates) == {file_a, file_c}


def test_find_duplicates_ignores_unique(tmp_path: Path):
    file_a = tmp_path / "a.jpg"
    file_b = tmp_path / "b.jpg"

    file_a.write_bytes(b"one")
    file_b.write_bytes(b"two")

    files = [_make_file_info(file_a), _make_file_info(file_b)]

    resolved_datetimes = {
        file_a: datetime(2020, 1, 1, 0, 0, 0),
        file_b: datetime(2020, 1, 2, 0, 0, 0),
    }

    groups = find_duplicates(files=files, resolved_datetimes=resolved_datetimes)

    assert groups == []


def test_find_duplicates_handles_hash_errors(tmp_path: Path, monkeypatch):
    file_a = tmp_path / "a.jpg"
    file_b = tmp_path / "b.jpg"

    file_a.write_bytes(b"same")
    file_b.write_bytes(b"same")

    files = [_make_file_info(file_a), _make_file_info(file_b)]
    resolved_datetimes = {
        file_a: datetime(2020, 1, 1, 0, 0, 0),
        file_b: datetime(2020, 1, 2, 0, 0, 0),
    }

    def fake_hash(_path):
        return None

    monkeypatch.setattr("photo_tool.deduplicator._hash_file", fake_hash)

    groups = find_duplicates(files=files, resolved_datetimes=resolved_datetimes)
    assert groups == []
