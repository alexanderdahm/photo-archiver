from pathlib import Path

from photo_tool.datetime_resolver import resolve_datetime


def test_datetime_resolution_returns_value(tmp_path: Path):
    sample = tmp_path / "image.jpg"
    sample.write_text("x", encoding="utf-8")

    result = resolve_datetime(sample)

    assert result is not None
