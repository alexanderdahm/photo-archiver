"""
Phase 6: Filesystem executor.

Performs copy/move operations based on SortDecision.
"""

import shutil
from pathlib import Path

from media_archiver.sorter import SortDecision


def execute_decision(
    *,
    decision: SortDecision,
    apply: bool,
) -> bool:
    """
    Returns True if an operation was performed, False otherwise.
    """
    if decision.action == "skip":
        return False

    if not apply:
        return False

    try:
        decision.target_dir.mkdir(parents=True, exist_ok=True)

        if decision.action == "copy":
            shutil.copy2(decision.source, decision.target_path)
            return True

        if decision.action == "move":
            shutil.move(decision.source, decision.target_path)
            return True
    except OSError:
        return False

    return False
