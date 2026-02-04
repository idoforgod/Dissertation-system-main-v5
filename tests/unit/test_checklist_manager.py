"""Unit tests for checklist_manager.py - Checklist management module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))


class TestChecklistParsing:
    """Tests for checklist parsing functionality."""

    def test_parse_checklist_returns_list(self, temp_thesis_output: Path):
        """Test that parse_checklist returns a list of items."""
        from checklist_manager import parse_checklist, create_checklist

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        items = parse_checklist(checklist_path)

        assert isinstance(items, list)
        assert len(items) == 150

    def test_parse_checklist_item_structure(self, temp_thesis_output: Path):
        """Test that each checklist item has required fields."""
        from checklist_manager import parse_checklist, create_checklist

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        items = parse_checklist(checklist_path)

        for item in items:
            assert "step" in item
            assert "task" in item
            assert "status" in item
            assert item["status"] in ("pending", "in_progress", "completed")

    def test_parse_checklist_initial_status(self, temp_thesis_output: Path):
        """Test that initial checklist has all items as pending."""
        from checklist_manager import parse_checklist, create_checklist

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        items = parse_checklist(checklist_path)

        for item in items:
            assert item["status"] == "pending"


class TestChecklistUpdate:
    """Tests for checklist update functionality."""

    def test_update_step_status_to_completed(self, temp_thesis_output: Path):
        """Test updating a step to completed status."""
        from checklist_manager import (
            parse_checklist,
            create_checklist,
            update_step_status,
        )

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        update_step_status(checklist_path, step=1, status="completed")
        items = parse_checklist(checklist_path)

        step1 = next(item for item in items if item["step"] == 1)
        assert step1["status"] == "completed"

    def test_update_step_status_to_in_progress(self, temp_thesis_output: Path):
        """Test updating a step to in_progress status."""
        from checklist_manager import (
            parse_checklist,
            create_checklist,
            update_step_status,
        )

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        update_step_status(checklist_path, step=2, status="in_progress")
        items = parse_checklist(checklist_path)

        step2 = next(item for item in items if item["step"] == 2)
        assert step2["status"] == "in_progress"

    def test_update_preserves_other_steps(self, temp_thesis_output: Path):
        """Test that updating one step doesn't affect others."""
        from checklist_manager import (
            parse_checklist,
            create_checklist,
            update_step_status,
        )

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        update_step_status(checklist_path, step=1, status="completed")
        items = parse_checklist(checklist_path)

        step2 = next(item for item in items if item["step"] == 2)
        assert step2["status"] == "pending"

    def test_update_invalid_step_raises_error(self, temp_thesis_output: Path):
        """Test that updating invalid step raises ValueError."""
        from checklist_manager import create_checklist, update_step_status

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        with pytest.raises(ValueError):
            update_step_status(checklist_path, step=999, status="completed")

    def test_update_invalid_status_raises_error(self, temp_thesis_output: Path):
        """Test that invalid status raises ValueError."""
        from checklist_manager import create_checklist, update_step_status

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        with pytest.raises(ValueError):
            update_step_status(checklist_path, step=1, status="invalid")


class TestChecklistProgress:
    """Tests for progress tracking functionality."""

    def test_get_progress_initial(self, temp_thesis_output: Path):
        """Test initial progress is 0%."""
        from checklist_manager import create_checklist, get_progress

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        progress = get_progress(checklist_path)

        assert progress["completed"] == 0
        assert progress["in_progress"] == 0
        assert progress["pending"] == 150
        assert progress["percentage"] == 0.0

    def test_get_progress_after_updates(self, temp_thesis_output: Path):
        """Test progress tracking after status updates."""
        from checklist_manager import (
            create_checklist,
            update_step_status,
            get_progress,
        )

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        update_step_status(checklist_path, step=1, status="completed")
        update_step_status(checklist_path, step=2, status="in_progress")

        progress = get_progress(checklist_path)

        assert progress["completed"] == 1
        assert progress["in_progress"] == 1
        assert progress["pending"] == 148
        assert progress["percentage"] == pytest.approx(0.67, rel=0.1)

    def test_get_current_step(self, temp_thesis_output: Path):
        """Test getting current step in progress."""
        from checklist_manager import (
            create_checklist,
            update_step_status,
            get_current_step,
        )

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        update_step_status(checklist_path, step=1, status="completed")
        update_step_status(checklist_path, step=2, status="in_progress")

        current = get_current_step(checklist_path)

        assert current["step"] == 2
        assert current["status"] == "in_progress"


class TestChecklistPhase:
    """Tests for phase-related functionality."""

    def test_get_phase_for_step(self, temp_thesis_output: Path):
        """Test getting phase name for a given step."""
        from checklist_manager import get_phase_for_step

        assert get_phase_for_step(1) == "phase0"
        assert get_phase_for_step(8) == "phase0"
        assert get_phase_for_step(19) == "phase1-wave1"
        assert get_phase_for_step(35) == "phase1-wave2"
        assert get_phase_for_step(89) == "phase2"
        assert get_phase_for_step(109) == "phase3"
        assert get_phase_for_step(133) == "phase4"

    def test_get_steps_for_phase(self, temp_thesis_output: Path):
        """Test getting step range for a phase."""
        from checklist_manager import get_steps_for_phase

        phase0_steps = get_steps_for_phase("phase0")
        assert phase0_steps["start"] == 1
        assert phase0_steps["end"] == 18

    def test_get_phase_progress(self, temp_thesis_output: Path):
        """Test getting progress for a specific phase."""
        from checklist_manager import (
            create_checklist,
            update_step_status,
            get_phase_progress,
        )

        create_checklist(temp_thesis_output)
        checklist_path = temp_thesis_output / "todo-checklist.md"

        # Complete first 3 steps of phase0
        for step in [1, 2, 3]:
            update_step_status(checklist_path, step=step, status="completed")

        progress = get_phase_progress(checklist_path, "phase0")

        assert progress["completed"] == 3
        assert progress["total"] == 18
