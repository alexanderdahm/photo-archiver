from pathlib import Path

import yaml

from media_archiver.month_normalizer import normalize_month_folder


def test_month_folder_cases():
    cases_path = Path(__file__).resolve().parent / "fixtures" / "month_folder_cases.yaml"
    payload = yaml.safe_load(cases_path.read_text(encoding="utf-8"))

    for case in payload["cases"]:
        assert normalize_month_folder(case["input"]) == case["expected"]
