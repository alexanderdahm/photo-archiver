"""
Phase 6: Sorting orchestration (decision logic only).

Determines target paths and actions without performing filesystem writes.
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Literal


Action = Literal["copy", "move", "skip"]


@dataclass(frozen=True)
class SortDecision:
    source: Path
    target_dir: Path
    target_path: Path
    action: Action
    reason: str | None = None


def determine_target_dir(
    *,
    archive_root: Path,
    resolved_datetime: datetime,
    month_folder: str,
) -> Path:
    year = f"{resolved_datetime.year:04d}"
    return archive_root / year / month_folder


def decide_action(
    *,
    source: Path,
    target_path: Path,
    move_files: bool,
    target_exists: bool,
) -> SortDecision:
    if target_exists:
        return SortDecision(
            source=source,
            target_dir=target_path.parent,
            target_path=target_path,
            action="skip",
            reason="target_exists",
        )

    action: Action = "move" if move_files else "copy"
    return SortDecision(
        source=source,
        target_dir=target_path.parent,
        target_path=target_path,
        action=action,
        reason=None,
    )


def build_sort_decision(
    *,
    archive_root: Path,
    source_path: Path,
    resolved_datetime: datetime,
    month_folder: str,
    canonical_name: str,
    move_files: bool,
    target_exists: bool,
) -> SortDecision:
    target_dir = determine_target_dir(
        archive_root=archive_root,
        resolved_datetime=resolved_datetime,
        month_folder=month_folder,
    )
    target_path = target_dir / canonical_name
    return decide_action(
        source=source_path,
        target_path=target_path,
        move_files=move_files,
        target_exists=target_exists,
    )
