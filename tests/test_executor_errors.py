import shutil
from pathlib import Path

from media_archiver.executor import execute_decision
from media_archiver.sorter import SortDecision


def test_executor_copy_io_error_is_handled(monkeypatch, tmp_path: Path):
    source = tmp_path / "source.jpg"
    target_dir = tmp_path / "target"
    target = target_dir / "target.jpg"

    source.write_text("x", encoding="utf-8")

    decision = SortDecision(
        source=source,
        target_dir=target_dir,
        target_path=target,
        action="copy",
        reason=None,
    )

    def broken_copy(*args, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(shutil, "copy2", broken_copy)

    performed = execute_decision(
        decision=decision,
        apply=True,
    )

    assert performed is False
    assert not target.exists()
