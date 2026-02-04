"""Unit tests for init_session.py - Session initialization module."""

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))


class TestSessionInitialization:
    """Tests for session initialization functionality."""

    def test_create_session_returns_valid_structure(self, temp_dir: Path):
        """Test that create_session returns a valid session structure."""
        from init_session import create_session

        session = create_session(
            topic="AI와 조직혁신 연구",
            mode="topic",
            output_dir=temp_dir
        )

        assert "version" in session
        assert session["version"] == "2.3.0"
        assert "research" in session
        assert session["research"]["topic"] == "AI와 조직혁신 연구"
        assert session["research"]["mode"] == "topic"
        assert "workflow" in session
        assert "options" in session
        assert "quality" in session
        assert "context_snapshots" in session

    def test_create_session_with_different_modes(self, temp_dir: Path):
        """Test session creation with different input modes."""
        from init_session import create_session

        modes = ["topic", "question", "review", "learning", "paper-upload", "proposal"]
        for mode in modes:
            session = create_session(
                topic=f"Test topic for {mode}",
                mode=mode,
                output_dir=temp_dir
            )
            assert session["research"]["mode"] == mode

    def test_create_session_sets_timestamps(self, temp_dir: Path):
        """Test that session has valid timestamps."""
        from init_session import create_session

        session = create_session(
            topic="Test topic",
            mode="topic",
            output_dir=temp_dir
        )

        assert "created_at" in session
        assert "updated_at" in session
        # Verify ISO format
        datetime.fromisoformat(session["created_at"].replace("Z", "+00:00"))
        datetime.fromisoformat(session["updated_at"].replace("Z", "+00:00"))

    def test_create_session_initializes_workflow_state(self, temp_dir: Path):
        """Test that workflow state is properly initialized."""
        from init_session import create_session

        session = create_session(
            topic="Test topic",
            mode="topic",
            output_dir=temp_dir
        )

        workflow = session["workflow"]
        assert workflow["current_phase"] == "phase0"
        assert workflow["current_step"] == 1
        assert workflow["total_steps"] == 150
        assert workflow["last_checkpoint"] is None
        assert workflow["last_agent"] is None

    def test_create_session_proposal_mode_with_metadata(self, temp_dir: Path):
        """Test that proposal mode creates proposal_metadata."""
        from init_session import create_session

        session = create_session(
            topic="My Research Proposal",
            mode="proposal",
            output_dir=temp_dir,
            paper_path="/tmp/test-proposal.pdf",
        )

        assert session["research"]["mode"] == "proposal"
        assert "proposal_metadata" in session
        assert session["proposal_metadata"]["original_path"] == "/tmp/test-proposal.pdf"
        assert session["proposal_metadata"]["analysis_status"] == "pending"
        assert session["proposal_metadata"]["completeness_score"] is None
        assert session["proposal_metadata"]["extracted_plan"] is None

    def test_create_session_with_entry_path(self, temp_dir: Path):
        """Test that entry_path is stored in session."""
        from init_session import create_session

        session = create_session(
            topic="Custom Input Topic",
            mode="topic",
            output_dir=temp_dir,
            entry_path="custom",
        )

        assert session["research"]["entry_path"] == "custom"

    def test_create_session_with_custom_preferences(self, temp_dir: Path):
        """Test that custom_preferences are stored when entry_path is custom."""
        from init_session import create_session

        prefs = {
            "methodology_preference": "quantitative",
            "theoretical_framework": "TAM",
            "constraints": ["time_limited"],
        }

        session = create_session(
            topic="Custom Input Topic",
            mode="topic",
            output_dir=temp_dir,
            entry_path="custom",
            custom_preferences=prefs,
        )

        assert session["research"]["entry_path"] == "custom"
        assert session["research"]["custom_preferences"] == prefs

    def test_create_session_without_entry_path_has_no_field(self, temp_dir: Path):
        """Test that entry_path is not set when not provided."""
        from init_session import create_session

        session = create_session(
            topic="Normal Topic",
            mode="topic",
            output_dir=temp_dir,
        )

        assert "entry_path" not in session["research"]

    def test_save_session_creates_file(self, temp_thesis_output: Path):
        """Test that save_session creates a JSON file."""
        from init_session import create_session, save_session

        session = create_session(
            topic="Test topic",
            mode="topic",
            output_dir=temp_thesis_output.parent.parent
        )

        session_path = temp_thesis_output / "session.json"
        save_session(session, session_path)

        assert session_path.exists()

        with open(session_path) as f:
            loaded = json.load(f)

        assert loaded["research"]["topic"] == "Test topic"

    def test_save_session_preserves_korean_characters(self, temp_thesis_output: Path):
        """Test that Korean characters are preserved in session file."""
        from init_session import create_session, save_session

        korean_topic = "인공지능 기반 조직혁신 연구"
        session = create_session(
            topic=korean_topic,
            mode="topic",
            output_dir=temp_thesis_output.parent.parent
        )

        session_path = temp_thesis_output / "session.json"
        save_session(session, session_path)

        with open(session_path, encoding="utf-8") as f:
            loaded = json.load(f)

        assert loaded["research"]["topic"] == korean_topic


class TestOutputDirectoryCreation:
    """Tests for output directory structure creation."""

    def test_create_output_structure_creates_directories(self, temp_dir: Path):
        """Test that all required directories are created."""
        from init_session import create_output_structure

        output_dir = create_output_structure(
            base_dir=temp_dir,
            research_title="테스트 연구"
        )

        assert output_dir.exists()
        assert (output_dir / "00-session").exists()
        assert (output_dir / "01-literature").exists()
        assert (output_dir / "02-research-design").exists()
        assert (output_dir / "03-thesis").exists()
        assert (output_dir / "04-publication").exists()

    def test_create_output_structure_uses_date_suffix(self, temp_dir: Path):
        """Test that output directory includes date suffix."""
        from init_session import create_output_structure

        output_dir = create_output_structure(
            base_dir=temp_dir,
            research_title="테스트 연구"
        )

        today = datetime.now().strftime("%Y-%m-%d")
        assert today in output_dir.name

    def test_create_output_structure_sanitizes_title(self, temp_dir: Path):
        """Test that special characters in title are sanitized."""
        from init_session import create_output_structure

        output_dir = create_output_structure(
            base_dir=temp_dir,
            research_title="AI/ML: 조직혁신? 연구!"
        )

        # Should not contain problematic characters
        assert "/" not in output_dir.name
        assert ":" not in output_dir.name
        assert "?" not in output_dir.name


class TestSessionValidation:
    """Tests for session validation."""

    def test_validate_session_accepts_valid_session(self, sample_session: dict):
        """Test that valid session passes validation."""
        from init_session import validate_session

        is_valid, errors = validate_session(sample_session)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_session_rejects_missing_version(self, sample_session: dict):
        """Test that session without version is rejected."""
        from init_session import validate_session

        del sample_session["version"]
        is_valid, errors = validate_session(sample_session)

        assert is_valid is False
        assert any("version" in e.lower() for e in errors)

    def test_validate_session_accepts_proposal_mode(self, sample_session: dict):
        """Test that proposal mode passes validation."""
        from init_session import validate_session

        sample_session["research"]["mode"] = "proposal"
        is_valid, errors = validate_session(sample_session)

        assert is_valid is True

    def test_validate_session_rejects_invalid_mode(self, sample_session: dict):
        """Test that session with invalid mode is rejected."""
        from init_session import validate_session

        sample_session["research"]["mode"] = "invalid_mode"
        is_valid, errors = validate_session(sample_session)

        assert is_valid is False
        assert any("mode" in e.lower() for e in errors)

    def test_validate_session_rejects_negative_step(self, sample_session: dict):
        """Test that session with negative step is rejected."""
        from init_session import validate_session

        sample_session["workflow"]["current_step"] = -1
        is_valid, errors = validate_session(sample_session)

        assert is_valid is False


class TestInitializeWorkflow:
    """Tests for complete workflow initialization."""

    def test_initialize_workflow_creates_all_files(self, temp_dir: Path):
        """Test that initialize_workflow creates all required files."""
        from init_session import initialize_workflow

        output_dir = initialize_workflow(
            topic="AI 연구",
            mode="topic",
            base_dir=temp_dir / "thesis-output"
        )

        assert (output_dir / "00-session" / "session.json").exists()
        assert (output_dir / "00-session" / "todo-checklist.md").exists()
        assert (output_dir / "00-session").exists()

    def test_initialize_workflow_returns_output_directory(self, temp_dir: Path):
        """Test that initialize_workflow returns the output directory path."""
        from init_session import initialize_workflow

        output_dir = initialize_workflow(
            topic="AI 연구",
            mode="topic",
            base_dir=temp_dir / "thesis-output"
        )

        assert isinstance(output_dir, Path)
        assert output_dir.exists()
