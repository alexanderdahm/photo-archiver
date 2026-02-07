from datetime import datetime
from pathlib import Path

import yaml

from media_archiver.models import DateTimeSource
from media_archiver.renamer import ensure_unique_name, generate_filename


def _parse_base_filename(base: str) -> datetime:
    stem = Path(base).stem
    parts = stem.split("_")
    date_part = parts[0]
    time_part = parts[1]
    resolved_datetime = datetime.strptime(
        f"{date_part}_{time_part}", "%Y-%m-%d_%H-%M-%S"
    )
    return resolved_datetime


def test_generate_filename_with_collisions():
    cases_path = Path(__file__).resolve().parent / "fixtures" / "rename_collision_cases.yaml"
    payload = yaml.safe_load(cases_path.read_text(encoding="utf-8"))

    for case in payload["cases"]:
        resolved_datetime = _parse_base_filename(case["base"])
        result = generate_filename(
            original_name=case["base"],
            resolved_datetime=resolved_datetime,
            source=DateTimeSource.EXIF,
            existing_names=case["existing"],
        )
        assert result == case["expected"]


def test_generate_filename_uses_source_and_extension():
    result = generate_filename(
        original_name="IMG_20230801_101530.HEIC",
        resolved_datetime=datetime(2023, 8, 1, 10, 15, 30),
        source=DateTimeSource.FILENAME,
        existing_names=[],
    )

    assert result == "2023-08-01_10-15-30.heic"


def test_ensure_unique_name_keeps_original_and_handles_collisions():
    result = ensure_unique_name(
        original_name="IMG_0001.JPG",
        existing_names=["IMG_0001.JPG"],
    )

    assert result == "IMG_0001_01.JPG"
