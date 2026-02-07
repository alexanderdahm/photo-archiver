from pathlib import Path

import yaml

from media_archiver.datetime_resolver import resolve_datetime


def test_datetime_resolution_cases():
    cases_path = Path(__file__).resolve().parent / "fixtures" / "datetime_cases.yaml"
    payload = yaml.safe_load(cases_path.read_text(encoding="utf-8"))

    for case in payload["cases"]:
        result = resolve_datetime(
            filename=case["filename"],
            exif_datetime=case["exif_datetime"],
            fs_modified=case["fs_modified"],
        )

        assert result.datetime.isoformat() == case["expected"]["datetime"]
        assert result.source.value == case["expected"]["source"]
        assert result.confidence.value == case["expected"]["confidence"]


def test_exif_fallback_format_parses():
    result = resolve_datetime(
        filename="IMG-20170526-WA0009.jpg",
        exif_datetime="2017:05:26 14:32:10",
        fs_modified="2017-05-26T15:00:00",
    )

    assert result.datetime.isoformat() == "2017-05-26T14:32:10"
    assert result.source.value == "exif"
    assert result.confidence.value == "high"


def test_missing_fs_modified_raises():
    try:
        resolve_datetime(
            filename="image_final.jpg",
            exif_datetime=None,
            fs_modified=None,
        )
    except ValueError as exc:
        assert "Filesystem modified time" in str(exc)
    else:
        raise AssertionError("Expected ValueError for missing fs_modified")
