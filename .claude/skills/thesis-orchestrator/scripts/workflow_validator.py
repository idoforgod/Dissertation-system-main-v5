#!/usr/bin/env python3
"""Workflow Output Validation System.

This module provides validation for thesis workflow outputs.
It is completely independent and does not modify existing code.

Design Principles:
- Additive-Only: Does not modify existing files or functions
- Independent: Does not import from existing workflow scripts
- Non-invasive: Can be added/removed without affecting existing workflow
- Fail-Fast: Raises errors immediately when validation fails
"""

from pathlib import Path
from typing import List, Dict, Tuple, Optional
import re
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# Required Outputs Definition
# ============================================================================

# Define required outputs for each critical step
# Format: step_number -> [glob_pattern, ...]
REQUIRED_OUTPUTS: Dict[int, List[str]] = {
    # Phase 0: Initialization
    1: ["00-session/session.json"],
    7: ["00-session/todo-checklist.md"],

    # Phase 1: Literature Review (critical files only)
    19: ["01-literature/wave1-literature-search.yaml"],
    22: ["01-literature/wave1-seminal-works.yaml"],
    75: ["01-literature/wave5-srcs-evaluation.yaml"],
    88: ["00-session/research-synthesis.md"],

    # Phase 2: Research Design
    108: ["02-research-design/paradigm-statement.md"],

    # Phase 3: Writing (CRITICAL - all chapters required)
    111: ["03-thesis/thesis-outline.md"],
    115: ["03-thesis/chapter1-*.md"],           # ⭐ Chapter 1 required
    117: ["03-thesis/chapter2-*.md"],           # ⭐ Chapter 2 required
    119: ["03-thesis/chapter3-*.md"],           # ⭐ Chapter 3 required
    121: ["03-thesis/chapter4-*.md"],           # ⭐ Chapter 4 required
    123: ["03-thesis/chapter5-*.md"],           # ⭐ Chapter 5 required
    129: ["03-thesis/thesis-final.md"],         # ⭐ Final integrated thesis
    130: ["03-thesis/references.md"],           # ⭐ References

    # Phase 4: Publication
    136: ["04-publication/publication-strategy.md"],
    138: ["04-publication/manuscript-formatted.md"],
    139: ["04-publication/abstract-english.md"],
}


# ============================================================================
# Step Dependencies Definition
# ============================================================================

# Define dependencies between steps
# Format: step_number -> [prerequisite_step_numbers, ...]
STEP_DEPENDENCIES: Dict[int, List[int]] = {
    # Phase 3 dependencies (critical)
    117: [115],                    # Ch.2 requires Ch.1
    119: [115, 117],              # Ch.3 requires Ch.1, Ch.2
    121: [115, 117, 119],         # Ch.4 requires Ch.1, Ch.2, Ch.3
    123: [115, 117, 119, 121],    # Ch.5 requires Ch.1-4
    129: [115, 117, 119, 121, 123],  # Final thesis requires all chapters
    130: [129],                   # References requires final thesis

    # Phase 4 dependencies
    138: [129, 130],             # Manuscript formatting requires thesis + refs
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ValidationResult:
    """Result of validation."""
    success: bool
    step: int
    missing_files: List[str]
    timestamp: datetime
    message: str

    def __str__(self) -> str:
        if self.success:
            return f"✅ Step {self.step} validation passed"
        else:
            return (
                f"❌ Step {self.step} validation failed\n"
                f"Missing files:\n" +
                "\n".join(f"  - {f}" for f in self.missing_files)
            )


# ============================================================================
# Main Validator Class
# ============================================================================

class WorkflowValidator:
    """Validates workflow outputs against required files.

    This validator is completely independent and does not modify
    or depend on existing workflow code.

    Usage:
        validator = WorkflowValidator(working_dir)
        success, missing = validator.validate_step(115)
        if not success:
            print(f"Missing: {missing}")
    """

    def __init__(self, working_dir: Path):
        """Initialize validator.

        Args:
            working_dir: Absolute path to workflow working directory
                        (e.g., thesis-output/AI-free-will-impossibility-2026-01-20)
        """
        self.working_dir = Path(working_dir)
        if not self.working_dir.exists():
            raise ValueError(f"Working directory does not exist: {working_dir}")

    def validate_step(self, step: int) -> Tuple[bool, List[str]]:
        """Validate required outputs for a specific step.

        Args:
            step: Step number (1-150)

        Returns:
            (success, missing_files)
            - success: True if all required files exist
            - missing_files: List of missing file patterns
        """
        required = REQUIRED_OUTPUTS.get(step, [])
        missing = []

        for pattern in required:
            # Check if pattern matches any files
            matches = list(self.working_dir.glob(pattern))
            if not matches:
                missing.append(pattern)

        success = len(missing) == 0
        return success, missing

    def validate_step_verbose(self, step: int) -> ValidationResult:
        """Validate step with detailed result object.

        Args:
            step: Step number (1-150)

        Returns:
            ValidationResult object with detailed information
        """
        success, missing = self.validate_step(step)

        if success:
            message = f"Step {step} validation passed - all required files exist"
        else:
            message = (
                f"Step {step} validation failed - {len(missing)} file(s) missing"
            )

        return ValidationResult(
            success=success,
            step=step,
            missing_files=missing,
            timestamp=datetime.now(),
            message=message
        )

    def enforce_step(self, step: int):
        """Enforce validation - raise error if files are missing.

        This is the strict validation mode that raises ValidationError
        on failure, following the Fail-Fast principle.

        Args:
            step: Step number (1-150)

        Raises:
            ValidationError: If required files are missing
        """
        success, missing = self.validate_step(step)
        if not success:
            raise ValidationError(
                f"Step {step} validation failed. Missing files:\n" +
                "\n".join(f"  - {f}" for f in missing)
            )

    def validate_phase(self, phase: int) -> Dict[int, List[str]]:
        """Validate all steps in a phase.

        Args:
            phase: Phase number (0-4)

        Returns:
            Dictionary mapping step_number -> missing_files
            Only includes steps that failed validation
        """
        phase_steps = self._get_phase_steps(phase)
        failures = {}

        for step in phase_steps:
            success, missing = self.validate_step(step)
            if not success:
                failures[step] = missing

        return failures

    def validate_critical_steps(self) -> Dict[int, List[str]]:
        """Validate all critical steps (those with required outputs).

        Returns:
            Dictionary mapping step_number -> missing_files
            Only includes steps that failed validation
        """
        failures = {}

        for step in REQUIRED_OUTPUTS.keys():
            success, missing = self.validate_step(step)
            if not success:
                failures[step] = missing

        return failures

    def get_completion_rate(self) -> Dict[str, any]:
        """Calculate workflow completion rate based on required outputs.

        Returns:
            Dictionary with completion statistics
        """
        total_steps = len(REQUIRED_OUTPUTS)
        completed_steps = 0

        for step in REQUIRED_OUTPUTS.keys():
            success, _ = self.validate_step(step)
            if success:
                completed_steps += 1

        return {
            "total_required_steps": total_steps,
            "completed_steps": completed_steps,
            "completion_rate": completed_steps / total_steps * 100,
            "missing_steps": total_steps - completed_steps
        }

    def _get_phase_steps(self, phase: int) -> List[int]:
        """Get step numbers for a phase.

        Args:
            phase: Phase number (0-4)

        Returns:
            List of step numbers in that phase
        """
        phase_ranges = {
            0: range(1, 19),      # 1-18
            1: range(19, 89),     # 19-88
            2: range(89, 109),    # 89-108
            3: range(109, 133),   # 109-132
            4: range(133, 151)    # 133-150
        }

        steps = list(phase_ranges.get(phase, []))
        # Only return steps that have required outputs defined
        return [s for s in steps if s in REQUIRED_OUTPUTS]


# ============================================================================
# Dependency Validator
# ============================================================================

class DependencyValidator:
    """Validates step dependencies.

    Ensures that prerequisite steps are completed before
    dependent steps are executed.
    """

    def __init__(self, working_dir: Path):
        """Initialize dependency validator.

        Args:
            working_dir: Absolute path to workflow working directory
        """
        self.working_dir = Path(working_dir)
        self.output_validator = WorkflowValidator(working_dir)

    def validate_dependencies(self, step: int) -> Tuple[bool, List[int]]:
        """Validate that all dependencies for a step are met.

        Args:
            step: Step number to validate

        Returns:
            (success, missing_dependencies)
            - success: True if all dependencies are satisfied
            - missing_dependencies: List of prerequisite steps not completed
        """
        dependencies = STEP_DEPENDENCIES.get(step, [])
        missing = []

        for dep_step in dependencies:
            success, _ = self.output_validator.validate_step(dep_step)
            if not success:
                missing.append(dep_step)

        return len(missing) == 0, missing

    def enforce_dependencies(self, step: int):
        """Enforce dependencies - raise error if not met.

        Args:
            step: Step number to validate

        Raises:
            DependencyError: If dependencies are not satisfied
        """
        success, missing = self.validate_dependencies(step)
        if not success:
            raise DependencyError(
                f"Step {step} cannot execute. Missing dependencies:\n" +
                "\n".join(f"  - Step {s}" for s in missing)
            )


# ============================================================================
# Custom Exceptions
# ============================================================================

class ValidationError(Exception):
    """Raised when workflow validation fails."""
    pass


class DependencyError(Exception):
    """Raised when step dependencies are not satisfied."""
    pass


# ============================================================================
# CLI Interface (for manual testing)
# ============================================================================

def main():
    """CLI interface for manual validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate thesis workflow outputs")
    parser.add_argument("working_dir", type=Path, help="Path to working directory")
    parser.add_argument("--step", type=int, help="Validate specific step")
    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3, 4],
                       help="Validate entire phase")
    parser.add_argument("--all", action="store_true",
                       help="Validate all critical steps")
    parser.add_argument("--stats", action="store_true",
                       help="Show completion statistics")

    args = parser.parse_args()

    validator = WorkflowValidator(args.working_dir)

    if args.step:
        result = validator.validate_step_verbose(args.step)
        print(result)
        return 0 if result.success else 1

    elif args.phase is not None:
        failures = validator.validate_phase(args.phase)
        if failures:
            print(f"❌ Phase {args.phase} validation failed:")
            for step, missing in failures.items():
                print(f"\n  Step {step}:")
                for file in missing:
                    print(f"    - {file}")
            return 1
        else:
            print(f"✅ Phase {args.phase} validation passed")
            return 0

    elif args.all:
        failures = validator.validate_critical_steps()
        if failures:
            print(f"❌ Validation failed for {len(failures)} step(s):")
            for step, missing in failures.items():
                print(f"\n  Step {step}:")
                for file in missing:
                    print(f"    - {file}")
            return 1
        else:
            print("✅ All critical steps validated")
            return 0

    elif args.stats:
        stats = validator.get_completion_rate()
        print(f"Completion Rate: {stats['completion_rate']:.1f}%")
        print(f"Completed: {stats['completed_steps']}/{stats['total_required_steps']}")
        print(f"Missing: {stats['missing_steps']}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
