#!/usr/bin/env python3
"""Test script for run_writing_validated.py

This creates a mock session and tests the validation flow.
"""

import sys
from pathlib import Path
import json
import shutil
import tempfile

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from phase_validator import PhaseValidator


def create_test_session():
    """Create a test session with working directory."""
    # Create temporary test directory
    test_dir = Path("test-thesis-output")
    test_dir.mkdir(exist_ok=True)

    # Create working directory
    working_dir = test_dir / "test-ai-study-2026-01-20"
    working_dir.mkdir(exist_ok=True)

    # Create session.json
    session_file = test_dir / "session.json"
    session_data = {
        "working_dir": str(working_dir.absolute()),
        "topic": "Test AI Study",
        "research_type": "empirical",
        "thesis_format": "traditional-5-chapter",
        "created_at": "2026-01-20T10:00:00",
        "options": {
            "citation_style": "apa7",
            "citation_config": {
                "style_key": "apa7",
                "display_name": "APA 7th Edition",
                "note_type": "endnotes",
                "in_text_format": "author_year_parenthetical",
                "in_text_example": "(Smith, 2024) or Smith (2024)",
                "bibliography_title": "References",
                "bibliography_title_ko": "참고문헌"
            },
            "thesis_format": "traditional_5chapter"
        }
    }

    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2)

    # Create Phase 0 outputs
    session_dir = working_dir / "00-session"
    session_dir.mkdir(exist_ok=True)

    (session_dir / "session.json").write_text(
        json.dumps(session_data, indent=2),
        encoding='utf-8'
    )

    (session_dir / "todo-checklist.md").write_text(
        "# TODO Checklist\n\n- [x] Phase 0 complete\n",
        encoding='utf-8'
    )

    # Create Phase 1 outputs (minimal)
    lit_dir = working_dir / "01-literature"
    lit_dir.mkdir(exist_ok=True)

    (lit_dir / "wave1-literature-search.yaml").write_text(
        "# Literature Search Results\n",
        encoding='utf-8'
    )

    (lit_dir / "wave1-seminal-works.yaml").write_text(
        "# Seminal Works\n",
        encoding='utf-8'
    )

    (lit_dir / "wave5-srcs-evaluation.yaml").write_text(
        "# SRCS Evaluation\n",
        encoding='utf-8'
    )

    (session_dir / "research-synthesis.md").write_text(
        "# Research Synthesis\n\nTest synthesis.\n",
        encoding='utf-8'
    )

    # Create Phase 2 outputs
    design_dir = working_dir / "02-research-design"
    design_dir.mkdir(exist_ok=True)

    (design_dir / "paradigm-statement.md").write_text(
        "# Research Paradigm\n\nTest paradigm.\n",
        encoding='utf-8'
    )

    # Create temp directory with research design
    temp_dir = working_dir / "_temp"
    temp_dir.mkdir(exist_ok=True)

    (temp_dir / "research-design-final.md").write_text(
        "# Research Design\n\nTest design.\n",
        encoding='utf-8'
    )

    print(f"✅ Test session created at: {working_dir}")
    print(f"   Session file: {session_file}")

    return working_dir


def validate_test_session(working_dir: Path):
    """Validate that prerequisites are satisfied."""
    print("\nValidating test session prerequisites...")

    validator = PhaseValidator(working_dir)

    for phase in [0, 1, 2]:
        report = validator.validate_phase_verbose(phase)
        if report.all_passed:
            print(f"✅ Phase {phase} validated")
        else:
            print(f"❌ Phase {phase} validation failed:")
            print(report.summary())
            return False

    print("\n✅ All prerequisites satisfied for Phase 3\n")
    return True


def cleanup_test_session():
    """Clean up test directory."""
    test_dir = Path("test-thesis-output")
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print(f"🗑️  Cleaned up test directory: {test_dir}")


def main():
    """Run test."""
    print("="*70)
    print("Testing run_writing_validated.py")
    print("="*70 + "\n")

    # Create test session
    working_dir = create_test_session()

    # Validate prerequisites
    if not validate_test_session(working_dir):
        print("\n❌ Test failed: Prerequisites not satisfied")
        cleanup_test_session()
        return 1

    print("="*70)
    print("Test Setup Complete")
    print("="*70)
    print(f"\nWorking directory: {working_dir}")
    print("\nTo test the validated writing pipeline:")
    print(f"1. cd {working_dir.parent}")
    print(f"2. python3 {SCRIPT_DIR}/run_writing_validated.py")
    print("\nOr run: /thesis:run-writing-validated")
    print("\n" + "="*70)

    # Don't cleanup - leave for manual testing
    print("\nNote: Test directory left for manual testing.")
    print("      Run this script with --cleanup to remove it.")

    if "--cleanup" in sys.argv:
        cleanup_test_session()

    return 0


if __name__ == "__main__":
    sys.exit(main())
