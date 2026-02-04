#!/usr/bin/env python3
"""Phase-Level Validation System.

This module provides validation at the phase level (Phase 0-4) rather than
individual steps. It aggregates step-level validations and provides
comprehensive phase completion reports.

Design Principles:
- Additive-Only: Built on top of workflow_validator.py
- Independent: Can be used standalone or with validated_executor.py
- Non-invasive: Can be added/removed without affecting existing workflow
- Fail-Fast: Provides clear pass/fail at phase level

Usage:
    validator = PhaseValidator(working_dir)
    report = validator.validate_phase_verbose(3)  # Validate Phase 3
    if not report.all_passed:
        print(report.summary())
"""

from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json

# Import our independent validators
from workflow_validator import (
    WorkflowValidator,
    DependencyValidator,
    REQUIRED_OUTPUTS,
    ValidationResult
)


# ============================================================================
# Phase Definitions
# ============================================================================

PHASE_NAMES = {
    0: "Phase 0: Initialization",
    1: "Phase 1: Literature Review",
    2: "Phase 2: Research Design",
    3: "Phase 3: Thesis Writing",
    4: "Phase 4: Publication Strategy"
}

# Define critical steps for each phase (steps with required outputs)
PHASE_CRITICAL_STEPS = {
    0: [1, 7],                              # Init + Checklist
    1: [19, 22, 75, 88],                    # Literature review critical outputs
    2: [108],                               # Research design paradigm statement
    3: [111, 115, 117, 119, 121, 123, 129, 130],  # All thesis chapters + final
    4: [136, 138, 139]                      # Publication strategy + manuscript
}

# Define dependencies between phases
PHASE_DEPENDENCIES = {
    1: [0],         # Literature review requires initialization
    2: [0, 1],      # Research design requires init + literature
    3: [0, 1, 2],   # Writing requires init + literature + design
    4: [0, 1, 2, 3] # Publication requires all previous phases
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class StepValidation:
    """Validation result for a single step."""
    step: int
    success: bool
    missing_files: List[str]
    message: str


@dataclass
class PhaseValidationReport:
    """Comprehensive validation report for a phase."""
    phase: int
    phase_name: str
    timestamp: datetime
    all_passed: bool
    total_steps: int
    passed_steps: int
    failed_steps: int
    completion_rate: float
    step_validations: Dict[int, StepValidation] = field(default_factory=dict)
    failed_steps_list: List[int] = field(default_factory=list)
    missing_dependencies: List[int] = field(default_factory=list)

    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "✅ PASSED" if self.all_passed else "❌ FAILED"

        summary = f"""
{'='*70}
{status}: {self.phase_name}
{'='*70}

Completion: {self.passed_steps}/{self.total_steps} steps ({self.completion_rate:.1f}%)
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
"""

        if not self.all_passed:
            summary += f"\n❌ {len(self.failed_steps_list)} step(s) failed:\n"
            for step in self.failed_steps_list:
                validation = self.step_validations[step]
                summary += f"\n  Step {step}:\n"
                for file in validation.missing_files:
                    summary += f"    - Missing: {file}\n"

        if self.missing_dependencies:
            summary += f"\n⚠️  Missing prerequisite phases: {self.missing_dependencies}\n"

        summary += f"\n{'='*70}\n"
        return summary

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "phase": self.phase,
            "phase_name": self.phase_name,
            "timestamp": self.timestamp.isoformat(),
            "all_passed": self.all_passed,
            "total_steps": self.total_steps,
            "passed_steps": self.passed_steps,
            "failed_steps": self.failed_steps,
            "completion_rate": self.completion_rate,
            "failed_steps_list": self.failed_steps_list,
            "missing_dependencies": self.missing_dependencies,
            "step_validations": {
                step: {
                    "success": val.success,
                    "missing_files": val.missing_files,
                    "message": val.message
                }
                for step, val in self.step_validations.items()
            }
        }


@dataclass
class WorkflowValidationReport:
    """Complete validation report for entire workflow (all phases)."""
    timestamp: datetime
    working_dir: Path
    all_phases_passed: bool
    total_phases: int
    passed_phases: int
    failed_phases: int
    overall_completion_rate: float
    phase_reports: Dict[int, PhaseValidationReport] = field(default_factory=dict)

    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "✅ ALL PASSED" if self.all_phases_passed else "❌ SOME FAILED"

        summary = f"""
{'#'*70}
{status}: COMPLETE WORKFLOW VALIDATION
{'#'*70}

Working Directory: {self.working_dir}
Timestamp: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Phase Summary:
  Passed: {self.passed_phases}/{self.total_phases} phases
  Overall Completion: {self.overall_completion_rate:.1f}%

"""

        for phase in range(5):
            report = self.phase_reports.get(phase)
            if report:
                status_icon = "✅" if report.all_passed else "❌"
                summary += f"  {status_icon} {report.phase_name}: {report.completion_rate:.1f}% complete\n"

        summary += f"\n{'#'*70}\n"
        return summary

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "working_dir": str(self.working_dir),
            "all_phases_passed": self.all_phases_passed,
            "total_phases": self.total_phases,
            "passed_phases": self.passed_phases,
            "failed_phases": self.failed_phases,
            "overall_completion_rate": self.overall_completion_rate,
            "phase_reports": {
                phase: report.to_dict()
                for phase, report in self.phase_reports.items()
            }
        }


# ============================================================================
# Main Phase Validator Class
# ============================================================================

class PhaseValidator:
    """Validates workflow at the phase level.

    This validator provides higher-level validation than WorkflowValidator,
    aggregating step validations into phase-level reports.

    Usage:
        validator = PhaseValidator(working_dir)
        report = validator.validate_phase_verbose(3)
        if not report.all_passed:
            print(report.summary())
    """

    def __init__(self, working_dir: Path):
        """Initialize phase validator.

        Args:
            working_dir: Absolute path to workflow working directory
        """
        self.working_dir = Path(working_dir)
        if not self.working_dir.exists():
            raise ValueError(f"Working directory does not exist: {working_dir}")

        # Initialize underlying validators
        self.step_validator = WorkflowValidator(working_dir)
        self.dependency_validator = DependencyValidator(working_dir)

    def validate_phase(self, phase: int) -> Tuple[bool, Dict[int, List[str]]]:
        """Validate all critical steps in a phase.

        Args:
            phase: Phase number (0-4)

        Returns:
            (all_passed, failures)
            - all_passed: True if all steps passed
            - failures: Dictionary mapping step -> missing_files
        """
        critical_steps = PHASE_CRITICAL_STEPS.get(phase, [])
        failures = {}

        for step in critical_steps:
            success, missing = self.step_validator.validate_step(step)
            if not success:
                failures[step] = missing

        all_passed = len(failures) == 0
        return all_passed, failures

    def validate_phase_verbose(self, phase: int) -> PhaseValidationReport:
        """Validate phase with detailed report.

        Args:
            phase: Phase number (0-4)

        Returns:
            PhaseValidationReport with comprehensive validation information
        """
        phase_name = PHASE_NAMES.get(phase, f"Phase {phase}")
        critical_steps = PHASE_CRITICAL_STEPS.get(phase, [])

        step_validations = {}
        failed_steps_list = []
        passed_count = 0

        # Validate each critical step
        for step in critical_steps:
            success, missing = self.step_validator.validate_step(step)

            if success:
                message = f"Step {step} passed"
                passed_count += 1
            else:
                message = f"Step {step} failed - {len(missing)} file(s) missing"
                failed_steps_list.append(step)

            step_validations[step] = StepValidation(
                step=step,
                success=success,
                missing_files=missing,
                message=message
            )

        # Check phase dependencies
        missing_dependencies = self._check_phase_dependencies(phase)

        # Calculate completion rate
        total_steps = len(critical_steps)
        completion_rate = (passed_count / total_steps * 100) if total_steps > 0 else 0

        # Create report
        all_passed = (len(failed_steps_list) == 0 and len(missing_dependencies) == 0)

        return PhaseValidationReport(
            phase=phase,
            phase_name=phase_name,
            timestamp=datetime.now(),
            all_passed=all_passed,
            total_steps=total_steps,
            passed_steps=passed_count,
            failed_steps=len(failed_steps_list),
            completion_rate=completion_rate,
            step_validations=step_validations,
            failed_steps_list=failed_steps_list,
            missing_dependencies=missing_dependencies
        )

    def validate_all_phases(self) -> WorkflowValidationReport:
        """Validate all phases and generate complete workflow report.

        Returns:
            WorkflowValidationReport with all phases
        """
        phase_reports = {}
        passed_phases = 0
        total_completion = 0

        for phase in range(5):
            report = self.validate_phase_verbose(phase)
            phase_reports[phase] = report

            if report.all_passed:
                passed_phases += 1

            total_completion += report.completion_rate

        overall_completion_rate = total_completion / 5 if len(phase_reports) > 0 else 0
        all_phases_passed = (passed_phases == 5)

        return WorkflowValidationReport(
            timestamp=datetime.now(),
            working_dir=self.working_dir,
            all_phases_passed=all_phases_passed,
            total_phases=5,
            passed_phases=passed_phases,
            failed_phases=5 - passed_phases,
            overall_completion_rate=overall_completion_rate,
            phase_reports=phase_reports
        )

    def enforce_phase(self, phase: int):
        """Enforce phase validation - raise error if not complete.

        Args:
            phase: Phase number (0-4)

        Raises:
            PhaseValidationError: If phase validation fails
        """
        report = self.validate_phase_verbose(phase)
        if not report.all_passed:
            raise PhaseValidationError(
                f"Phase {phase} validation failed:\n{report.summary()}"
            )

    def _check_phase_dependencies(self, phase: int) -> List[int]:
        """Check if prerequisite phases are complete.

        Args:
            phase: Phase number to check

        Returns:
            List of missing prerequisite phase numbers
        """
        dependencies = PHASE_DEPENDENCIES.get(phase, [])
        missing = []

        for dep_phase in dependencies:
            all_passed, failures = self.validate_phase(dep_phase)
            if not all_passed:
                missing.append(dep_phase)

        return missing

    def get_progress_summary(self) -> Dict[str, any]:
        """Get simple progress summary across all phases.

        Returns:
            Dictionary with progress statistics
        """
        total_critical_steps = sum(len(steps) for steps in PHASE_CRITICAL_STEPS.values())
        completed_steps = 0

        for phase, steps in PHASE_CRITICAL_STEPS.items():
            for step in steps:
                success, _ = self.step_validator.validate_step(step)
                if success:
                    completed_steps += 1

        return {
            "total_critical_steps": total_critical_steps,
            "completed_steps": completed_steps,
            "completion_rate": completed_steps / total_critical_steps * 100,
            "phases_summary": {
                phase: {
                    "name": PHASE_NAMES[phase],
                    "passed": self.validate_phase(phase)[0]
                }
                for phase in range(5)
            }
        }

    def save_report(self, report: WorkflowValidationReport, output_path: Path):
        """Save validation report to JSON file.

        Args:
            report: WorkflowValidationReport to save
            output_path: Path to output JSON file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        print(f"✅ Report saved to: {output_path}")


# ============================================================================
# Custom Exceptions
# ============================================================================

class PhaseValidationError(Exception):
    """Raised when phase validation fails."""
    pass


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for phase validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate thesis workflow phases")
    parser.add_argument("working_dir", type=Path, help="Path to working directory")
    parser.add_argument("--phase", type=int, choices=[0, 1, 2, 3, 4],
                       help="Validate specific phase")
    parser.add_argument("--all", action="store_true",
                       help="Validate all phases")
    parser.add_argument("--progress", action="store_true",
                       help="Show progress summary")
    parser.add_argument("--output", type=Path,
                       help="Save report to JSON file")
    parser.add_argument("--enforce", action="store_true",
                       help="Fail-fast mode: exit with error if validation fails")

    args = parser.parse_args()

    validator = PhaseValidator(args.working_dir)

    if args.phase is not None:
        # Validate specific phase
        report = validator.validate_phase_verbose(args.phase)
        print(report.summary())

        if args.output:
            # Save single phase report
            output_data = {
                "phase_report": report.to_dict()
            }
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"✅ Report saved to: {args.output}")

        if args.enforce and not report.all_passed:
            return 1

        return 0 if report.all_passed else 1

    elif args.all:
        # Validate all phases
        report = validator.validate_all_phases()
        print(report.summary())

        # Print detailed phase summaries
        for phase, phase_report in sorted(report.phase_reports.items()):
            if not phase_report.all_passed:
                print(phase_report.summary())

        if args.output:
            validator.save_report(report, args.output)

        if args.enforce and not report.all_phases_passed:
            return 1

        return 0 if report.all_phases_passed else 1

    elif args.progress:
        # Show progress summary
        progress = validator.get_progress_summary()
        print(f"\nWorkflow Progress: {progress['completion_rate']:.1f}%")
        print(f"Completed: {progress['completed_steps']}/{progress['total_critical_steps']} critical steps\n")

        for phase, info in progress['phases_summary'].items():
            status = "✅" if info['passed'] else "❌"
            print(f"  {status} {info['name']}")

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
