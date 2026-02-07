from pathlib import Path
from unittest.mock import patch

import yaml

from media_archiver.executor import execute_decision
from media_archiver.sorter import SortDecision


def test_executor_respects_apply():
    decision = SortDecision(
        source=Path("D:/Photos/_unsorted/IMG_0001.jpg"),
        target_dir=Path("D:/Photos/2021/08_August"),
        target_path=Path("D:/Photos/2021/08_August/IMG_0001.jpg"),
        action="copy",
        reason=None,
    )

    assert execute_decision(decision=decision, apply=False) is False


def test_executor_executes_copy_and_move_from_fixtures():
    cases_path = Path(__file__).resolve().parent / "fixtures" / "sort_execution_cases.yaml"
    payload = yaml.safe_load(cases_path.read_text(encoding="utf-8"))

    for case in payload["cases"]:
        expected_performed = case["expected"]["performed"]
        if case["expected"]["action"] == "skip":
            continue

        decision = SortDecision(
            source=Path(case["input"]["source_path"]),
            target_dir=Path(case["expected"]["target_dir"]),
            target_path=Path(case["expected"]["target_path"]),
            action=case["expected"]["action"],
            reason=None,
        )

        with (
            patch.object(Path, "mkdir", lambda *args, **kwargs: None),
            patch("shutil.copy2", lambda *args, **kwargs: None),
            patch("shutil.move", lambda *args, **kwargs: None),
        ):
            performed = execute_decision(
                decision=decision,
                apply=not case["config"]["dry_run"],
            )

        assert performed == expected_performed


def test_executor_handles_io_errors():
    decision = SortDecision(
        source=Path("D:/Photos/_unsorted/IMG_0001.jpg"),
        target_dir=Path("D:/Photos/2021/08_August"),
        target_path=Path("D:/Photos/2021/08_August/IMG_0001.jpg"),
        action="copy",
        reason=None,
    )

    with (
        patch.object(Path, "mkdir", lambda *args, **kwargs: None),
        patch("shutil.copy2", side_effect=OSError("disk full")),
    ):
        assert execute_decision(decision=decision, apply=True) is False
