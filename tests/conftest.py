"""Pytest configuration and fixtures for thesis workflow tests."""

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest
import yaml


# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "skills" / "thesis-orchestrator" / "scripts"
FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test outputs."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_thesis_output(temp_dir: Path) -> Path:
    """Create a temporary thesis-output directory structure."""
    output_dir = temp_dir / "thesis-output" / "test-research-2026-01-18"
    output_dir.mkdir(parents=True)
    (output_dir / "_temp").mkdir()
    return output_dir


@pytest.fixture
def sample_session() -> dict:
    """Return a sample session.json structure."""
    return {
        "version": "2.3.0",
        "created_at": "2026-01-18T10:00:00Z",
        "updated_at": "2026-01-18T10:00:00Z",
        "working_dir": "ai-organizational-innovation-2026-01-18",
        "research": {
            "topic": "AI와 조직혁신의 상관관계 연구",
            "mode": "topic",
            "type": None,
            "discipline": None,
            "research_questions": [],
            "hypotheses": []
        },
        "workflow": {
            "current_phase": "phase0",
            "current_step": 1,
            "total_steps": 150,
            "last_checkpoint": None,
            "last_agent": None
        },
        "paths": {
            "output_dir": "thesis-output/ai-organizational-innovation-2026-01-18",
            "absolute_path": "/tmp/thesis-output/ai-organizational-innovation-2026-01-18",
        },
        "options": {
            "literature_depth": "comprehensive",
            "theoretical_framework": "existing",
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
            "language": "korean",
            "thesis_format": "traditional_5chapter"
        },
        "quality": {
            "srcs_scores": [],
            "gra_validations": [],
            "plagiarism_checks": []
        },
        "context_snapshots": []
    }


@pytest.fixture
def sample_claims() -> list[dict]:
    """Return sample GroundedClaim data for testing."""
    return [
        {
            "id": "LIT-001",
            "text": "조직 몰입과 직무 성과 간에는 정적 상관관계가 있다",
            "claim_type": "EMPIRICAL",
            "sources": [
                {
                    "type": "PRIMARY",
                    "reference": "Meyer & Allen (1991), Journal of Applied Psychology",
                    "doi": "10.1037/0021-9010.76.6.733",
                    "verified": True
                }
            ],
            "confidence": 92,
            "uncertainty": "개인 수준 분석에 한정"
        },
        {
            "id": "LIT-002",
            "text": "변혁적 리더십은 조직 혁신에 긍정적 영향을 미친다",
            "claim_type": "EMPIRICAL",
            "sources": [
                {
                    "type": "PRIMARY",
                    "reference": "Bass & Avolio (1994), Improving Organizational Effectiveness",
                    "doi": "10.4135/9781452204932",
                    "verified": True
                }
            ],
            "confidence": 88,
            "uncertainty": "문화적 맥락에 따른 차이 존재"
        }
    ]


@pytest.fixture
def sample_checklist_items() -> list[dict]:
    """Return sample checklist items."""
    return [
        {"step": 1, "phase": "phase0", "task": "세션 초기화", "status": "completed"},
        {"step": 2, "phase": "phase0", "task": "연구유형 선택", "status": "in_progress"},
        {"step": 3, "phase": "phase0", "task": "학문분야 선택", "status": "pending"},
    ]


@pytest.fixture
def hallucination_patterns() -> list[dict]:
    """Return hallucination detection patterns (aligned with gra_validator.py)."""
    return [
        {"level": "BLOCK", "patterns": ["모든 연구가 일치", "항상", "절대로", "완벽하게", "전혀 없", "모두 동의"]},
        {"level": "REQUIRE_SOURCE", "patterns": [r"p\s*[<>=]\s*\.\d+", r"효과크기\s*[dr]\s*="]},
        {"level": "SOFTEN", "patterns": ["100%", "예외 없이", "확실히", "명백히", "분명히", "틀림없이"]},
        {"level": "VERIFY", "patterns": ["일반적으로", "대부분", "많은 연구"]},
    ]


def load_fixture(filename: str) -> dict | list:
    """Load a fixture file (JSON or YAML)."""
    filepath = FIXTURES_DIR / filename
    if filepath.suffix == ".json":
        with open(filepath) as f:
            return json.load(f)
    elif filepath.suffix in (".yaml", ".yml"):
        with open(filepath) as f:
            return yaml.safe_load(f)
    raise ValueError(f"Unsupported fixture format: {filepath.suffix}")


def write_fixture(filepath: Path, data: dict | list) -> None:
    """Write data to a fixture file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if filepath.suffix == ".json":
        with open(filepath, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    elif filepath.suffix in (".yaml", ".yml"):
        with open(filepath, "w") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
