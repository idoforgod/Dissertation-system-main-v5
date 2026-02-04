#!/usr/bin/env python3
"""Bridge script: reorganize _temp/ outputs into numbered directory structure.

At runtime, agents write outputs to thesis-output/_temp/ (flat structure).
The SOT (session.json + context_loader) expects files in numbered directories
(01-literature/, 02-research-design/, etc.).

This script bridges the gap by copying files from _temp/ to the correct
numbered directory, keeping the originals in _temp/ for agent reference.

Usage:
    # Auto-detect session, reorganize all pending files
    python reorganize_outputs.py

    # Specify session directory explicitly
    python reorganize_outputs.py /path/to/thesis-output/my-study-2026-01-20

    # Reorganize only a specific phase
    python reorganize_outputs.py --phase phase1
"""

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Ensure scripts directory is on path
sys.path.insert(0, str(Path(__file__).parent))

from context_loader import load_context, find_session_file
from workflow_constants import PHASE_DIRS


# Rule-based mapping: file number prefix → target phase directory
# Note: 00-* files (e.g., 00-topic-exploration.md) are Phase 0 agent outputs
# but belong in 01-literature/ (consumed by Phase 1 pipeline), NOT 00-session/
# (which is reserved for management files like session.json, checklist).
FILE_NUMBER_RANGES = [
    (0, 0, "phase1"),      # 00-* → 01-literature/ (Phase 0 outputs feed Phase 1)
    (1, 17, "phase1"),     # 01-17-* → 01-literature/
    (20, 29, "phase2"),    # 20-29-* → 02-research-design/
]

# Named pattern mapping for files without number prefixes
NAMED_PATTERNS = {
    "phase3": [
        "thesis-outline",
        "chapter-",
        "thesis-review",
    ],
    "phase4": [
        "journal-recommendation",
        "manuscript-",
        "submission-",
        "cover-letter",
        "title-page",
    ],
    "phase1": [
        "cross-validation",
        "srcs-",
        "quality-report",
        "research-synthesis",
    ],
}


def get_target_phase(filename: str) -> Optional[str]:
    """Determine target phase directory for a given filename.

    Uses two strategies:
    1. Number prefix: files like 01-literature-search.md → phase based on number range
    2. Named patterns: files like thesis-outline.md → phase3

    Args:
        filename: The filename (not full path)

    Returns:
        Phase key (e.g. 'phase1') or None if unknown
    """
    # Strategy 1: Number prefix
    match = re.match(r'^(\d{2})-', filename)
    if match:
        num = int(match.group(1))
        for low, high, phase in FILE_NUMBER_RANGES:
            if low <= num <= high:
                return phase

    # Strategy 2: Named patterns
    lower_name = filename.lower()
    for phase, patterns in NAMED_PATTERNS.items():
        for pattern in patterns:
            if lower_name.startswith(pattern):
                return phase

    return None


def reorganize(session_dir: Path, dry_run: bool = False,
               phase_filter: Optional[str] = None) -> dict:
    """Reorganize _temp/ files into numbered directory structure.

    Args:
        session_dir: Path to the session directory (e.g., thesis-output/my-study/)
        dry_run: If True, only report what would be done
        phase_filter: Optional phase to filter (e.g., 'phase1')

    Returns:
        Summary dict with counts
    """
    temp_dir = session_dir / "_temp"

    if not temp_dir.exists():
        print(f"No _temp/ directory found at: {temp_dir}")
        return {"moved": 0, "skipped": 0, "unknown": 0}

    summary = {"moved": 0, "skipped": 0, "unknown": 0, "files": []}

    for file_path in sorted(temp_dir.iterdir()):
        if file_path.is_dir():
            continue

        filename = file_path.name
        target_phase = get_target_phase(filename)

        if target_phase is None:
            summary["unknown"] += 1
            if not dry_run:
                print(f"  ? {filename} (unknown target, skipping)")
            continue

        if phase_filter and target_phase != phase_filter:
            continue

        target_dir_name = PHASE_DIRS.get(target_phase)
        if not target_dir_name:
            summary["unknown"] += 1
            continue

        target_path = session_dir / target_dir_name / filename

        # Skip if already exists and is identical
        if target_path.exists() and target_path.stat().st_size == file_path.stat().st_size:
            summary["skipped"] += 1
            if not dry_run:
                print(f"  = {filename} (already in {target_dir_name}/)")
            continue

        if dry_run:
            print(f"  → {filename} → {target_dir_name}/{filename}")
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, target_path)
            print(f"  ✅ {filename} → {target_dir_name}/{filename}")

        summary["moved"] += 1
        summary["files"].append({"src": str(filename), "dst": f"{target_dir_name}/{filename}"})

    return summary


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Reorganize _temp/ outputs into numbered directories")
    parser.add_argument("session_dir", nargs="?", help="Session directory path (auto-detected if omitted)")
    parser.add_argument("--phase", help="Only reorganize files for this phase (e.g., phase1)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    # Resolve session directory
    if args.session_dir:
        session_dir = Path(args.session_dir)
    else:
        try:
            context = load_context()
            session_dir = context.working_dir
        except (FileNotFoundError, RuntimeError) as e:
            print(f"Could not auto-detect session: {e}")
            sys.exit(1)

    print(f"Session: {session_dir.name}")
    if args.dry_run:
        print("(DRY RUN - no files will be changed)\n")
    else:
        print()

    summary = reorganize(session_dir, dry_run=args.dry_run, phase_filter=args.phase)

    print(f"\nSummary: {summary['moved']} moved, {summary['skipped']} already synced, {summary['unknown']} unknown")

    # Log the reorganization
    if not args.dry_run and summary["moved"] > 0:
        log_file = session_dir / "00-session" / "reorganize.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            timestamp = datetime.now().isoformat()
            f.write(f"\n[{timestamp}] Reorganized {summary['moved']} files\n")
            for item in summary["files"]:
                f.write(f"  {item['src']} → {item['dst']}\n")


if __name__ == "__main__":
    main()
