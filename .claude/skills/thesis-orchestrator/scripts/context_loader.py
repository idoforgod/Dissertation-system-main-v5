#!/usr/bin/env python3
"""Context loader for all agents - ensures path consistency across workflow.

This module provides centralized path management to prevent the duplicate
directory issue. All agents should use this module to determine output paths.

Usage:
    from context_loader import load_context

    # In each agent
    context = load_context()
    output_path = context.get_output_path("phase1", "wave1-literature-search.yaml")
    save_results(output_path, results)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from workflow_constants import PHASE_DIRS


class WorkflowContext:
    """Central workflow context manager for path consistency."""

    def __init__(self, session_path: Path):
        """Initialize context from session.json.

        Args:
            session_path: Path to session.json file
        """
        self.session_path = session_path
        self.session = self._load_session()
        self.working_dir = self._resolve_working_dir()
        self._validate_structure()

    def _load_session(self) -> dict:
        """Load session.json."""
        if not self.session_path.exists():
            raise FileNotFoundError(f"session.json not found: {self.session_path}")

        with open(self.session_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _resolve_working_dir(self) -> Path:
        """Resolve working directory from session.json.

        Priority:
        1. session["paths"]["absolute_path"] (v2.1.0+)
        2. session["working_dir"] (v2.1.0+)
        3. Fallback: session_path parent directory
        """
        # Try new paths section (v2.1.0+)
        if "paths" in self.session:
            paths = self.session["paths"]
            if "absolute_path" in paths:
                return Path(paths["absolute_path"])

        # Try working_dir field (v2.1.0+)
        if "working_dir" in self.session:
            # working_dir is just the directory name
            # Need to combine with base_dir
            if "paths" in self.session and "base_dir" in self.session["paths"]:
                base = Path(self.session["paths"]["base_dir"])
                return base / self.session["working_dir"]

        # Fallback: use session_path location (backward compatible)
        return self.session_path.parent.parent

    def _validate_structure(self):
        """Validate that working directory has expected structure."""
        if not self.working_dir.exists():
            raise RuntimeError(
                f"Working directory does not exist: {self.working_dir}\n"
                "This may indicate a path consistency issue."
            )

        # Check for required directories (derived from PHASE_DIRS single source)
        required_dirs = list(PHASE_DIRS.values())

        missing = []
        for dir_name in required_dirs:
            if not (self.working_dir / dir_name).exists():
                missing.append(dir_name)

        if missing:
            print(f"⚠️  Warning: Missing directories: {', '.join(missing)}")
            print(f"   Creating missing directories...")
            for dir_name in missing:
                (self.working_dir / dir_name).mkdir(parents=True, exist_ok=True)

    def get_output_path(self, phase: str, filename: str) -> Path:
        """Get output path for a specific phase and filename.

        Args:
            phase: Phase name (phase0, phase1, phase2, phase3, phase4)
            filename: Output filename

        Returns:
            Full path to output file

        Examples:
            >>> context.get_output_path("phase1", "wave1-search.yaml")
            Path('thesis-output/ai-free-will-study-2026-01-20/01-literature/wave1-search.yaml')
        """
        phase_dirs = PHASE_DIRS

        if phase not in phase_dirs:
            raise ValueError(f"Invalid phase: {phase}. Must be one of {list(phase_dirs.keys())}")

        phase_dir = phase_dirs[phase]
        output_path = self.working_dir / phase_dir / filename

        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        return output_path

    def update_session(self, updates: dict) -> None:
        """Update session.json with new data.

        Args:
            updates: Dictionary of updates to merge into session

        Examples:
            >>> context.update_session({
            ...     "workflow": {"current_step": 20, "last_agent": "literature-searcher"}
            ... })
        """
        # Deep merge updates
        self._deep_merge(self.session, updates)

        # Update timestamp
        self.session["updated_at"] = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Save to file
        self.save_session()

    def _deep_merge(self, target: dict, source: dict) -> None:
        """Deep merge source into target."""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value

    def save_session(self) -> None:
        """Save current session state to session.json."""
        with open(self.session_path, 'w', encoding='utf-8') as f:
            json.dump(self.session, f, ensure_ascii=False, indent=2)

    def validate_paths(self) -> tuple[bool, list[str]]:
        """Validate all paths for consistency.

        Returns:
            Tuple of (is_valid, list of error messages)
        """
        errors = []

        # Check working directory
        if not self.working_dir.exists():
            errors.append(f"Working directory missing: {self.working_dir}")

        # Check session.json
        if not self.session_path.exists():
            errors.append(f"session.json missing: {self.session_path}")

        # Check path consistency
        if "paths" in self.session:
            paths = self.session["paths"]
            expected_dir = Path(paths.get("absolute_path", ""))
            if expected_dir != self.working_dir:
                errors.append(
                    f"Path mismatch: session says '{expected_dir}', "
                    f"but using '{self.working_dir}'"
                )

        # Check required directories (derived from PHASE_DIRS single source)
        required_dirs = list(PHASE_DIRS.values())
        for dir_name in required_dirs:
            dir_path = self.working_dir / dir_name
            if not dir_path.exists():
                errors.append(f"Required directory missing: {dir_name}")

        return len(errors) == 0, errors

    def get_phase_info(self) -> dict:
        """Get current phase information.

        Returns:
            Dictionary with current phase, step, and progress
        """
        workflow = self.session.get("workflow", {})
        return {
            "phase": workflow.get("current_phase", "phase0"),
            "step": workflow.get("current_step", 0),
            "total_steps": workflow.get("total_steps", 150),
            "progress": workflow.get("current_step", 0) / workflow.get("total_steps", 150) * 100,
            "last_agent": workflow.get("last_agent"),
        }

    def __repr__(self) -> str:
        phase_info = self.get_phase_info()
        return (
            f"WorkflowContext("
            f"working_dir='{self.working_dir.name}', "
            f"phase='{phase_info['phase']}', "
            f"step={phase_info['step']}/{phase_info['total_steps']}"
            f")"
        )


def load_context(session_path: Optional[Path] = None) -> WorkflowContext:
    """Load workflow context (entry point for all agents).

    Args:
        session_path: Path to session.json (optional, will auto-detect if not provided)

    Returns:
        WorkflowContext instance

    Raises:
        FileNotFoundError: If session.json cannot be found
        RuntimeError: If path validation fails

    Examples:
        >>> # Auto-detect session.json
        >>> context = load_context()

        >>> # Explicit path
        >>> context = load_context(Path("thesis-output/my-research-2026-01-20/00-session/session.json"))
    """
    if session_path is None:
        session_path = find_session_file()

    context = WorkflowContext(session_path)

    # Validate paths
    is_valid, errors = context.validate_paths()
    if not is_valid:
        error_msg = "Path validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        raise RuntimeError(error_msg)

    return context


def find_session_file(start_dir: Optional[Path] = None) -> Path:
    """Auto-detect session.json file location.

    Search priority:
    1. Environment variable: THESIS_SESSION_PATH
    2. .current-working-dir.txt marker file
    3. Current directory
    4. thesis-output/* (most recent)

    Args:
        start_dir: Starting directory for search (default: current directory)

    Returns:
        Path to session.json

    Raises:
        FileNotFoundError: If session.json cannot be found
    """
    if start_dir is None:
        start_dir = Path.cwd()

    # 1. Check environment variable
    if "THESIS_SESSION_PATH" in os.environ:
        env_path = Path(os.environ["THESIS_SESSION_PATH"])
        if env_path.exists():
            return env_path

    # 2. Check .current-working-dir.txt marker
    marker_file = start_dir / "thesis-output" / ".current-working-dir.txt"
    if marker_file.exists():
        working_dir_name = marker_file.read_text().strip()
        session_file = start_dir / "thesis-output" / working_dir_name / "00-session" / "session.json"
        if session_file.exists():
            return session_file

    # 3. Check current directory
    if (start_dir / "00-session" / "session.json").exists():
        return start_dir / "00-session" / "session.json"

    # 4. Search thesis-output/* (most recent)
    thesis_output = start_dir / "thesis-output"
    if thesis_output.exists():
        dirs_with_session = []

        for item in thesis_output.iterdir():
            if item.is_dir():
                session_file = item / "00-session" / "session.json"
                if session_file.exists():
                    dirs_with_session.append((item, session_file.stat().st_mtime))

        if dirs_with_session:
            # Sort by modification time, most recent first
            dirs_with_session.sort(key=lambda x: x[1], reverse=True)
            most_recent_dir = dirs_with_session[0][0]
            return most_recent_dir / "00-session" / "session.json"

    # Not found
    raise FileNotFoundError(
        "session.json not found. Searched:\n"
        f"  1. Environment variable: THESIS_SESSION_PATH\n"
        f"  2. Marker file: {marker_file}\n"
        f"  3. Current directory: {start_dir / '00-session' / 'session.json'}\n"
        f"  4. thesis-output subdirectories\n"
        "\n"
        "Please ensure you have initialized a workflow with init_session.py"
    )


if __name__ == "__main__":
    # Test/demo
    try:
        context = load_context()
        print(f"✅ Loaded context: {context}")
        print(f"📁 Working directory: {context.working_dir}")

        phase_info = context.get_phase_info()
        print(f"📊 Progress: {phase_info['progress']:.1f}% ({phase_info['step']}/{phase_info['total_steps']})")

        # Test path generation
        test_path = context.get_output_path("phase1", "test.yaml")
        print(f"🔗 Example output path: {test_path}")

        # Validate
        is_valid, errors = context.validate_paths()
        if is_valid:
            print("✅ All paths validated successfully")
        else:
            print("❌ Path validation errors:")
            for error in errors:
                print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error: {e}")
