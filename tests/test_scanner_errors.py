from pathlib import Path

from media_archiver.scanner import scan_directories


def test_scanner_handles_stat_error(monkeypatch, tmp_path: Path):
    test_file = tmp_path / "broken.jpg"
    test_file.write_text("x", encoding="utf-8")

    original_stat = Path.stat

    def broken_stat(self):
        if self == test_file:
            raise OSError("stat failed")
        return original_stat(self)

    monkeypatch.setattr(Path, "stat", broken_stat)

    result = scan_directories([tmp_path])

    assert len(result.supported) == 0
    assert len(result.ignored) == 1

    ignored = result.ignored[0]
    assert ignored.absolute_path == test_file.resolve()
    assert ignored.reason == "stat_failed"
