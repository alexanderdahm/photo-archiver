from datetime import datetime
from pathlib import Path

import yaml

from media_archiver.sorter import build_sort_decision


def test_sort_execution_cases():
    cases_path = Path(__file__).resolve().parent / "fixtures" / "sort_execution_cases.yaml"
    payload = yaml.safe_load(cases_path.read_text(encoding="utf-8"))

    archive_root = Path("D:/Photos")

    for case in payload["cases"]:
        resolved_datetime = datetime.fromisoformat(case["input"]["resolved_datetime"])
        if "target_dir" in case["expected"]:
            month_folder = Path(case["expected"]["target_dir"]).name
        else:
            month_folder = f"{resolved_datetime.month:02d}_Unknown"
        decision = build_sort_decision(
            archive_root=archive_root,
            source_path=Path(case["input"]["source_path"]),
            resolved_datetime=resolved_datetime,
            month_folder=month_folder,
            canonical_name=case["input"]["canonical_name"],
            move_files=case["config"]["move_files"],
            target_exists=case["input"].get("target_exists", False),
        )

        if "target_dir" in case["expected"]:
            assert decision.target_dir.as_posix() == case["expected"]["target_dir"]
        if "target_path" in case["expected"]:
            assert decision.target_path.as_posix() == case["expected"]["target_path"]
        assert decision.action == case["expected"]["action"]
        assert decision.reason == case["expected"].get("reason")
