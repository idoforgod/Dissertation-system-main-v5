#!/usr/bin/env python3
"""Path utilities for consistent directory naming across the workflow.

This module provides utilities to ensure consistent path handling,
preventing the duplicate directory issue caused by Korean/English naming conflicts.
"""

import re
import unicodedata
from pathlib import Path


# Korean to English keyword mapping for academic research
KOREAN_TO_ENGLISH = {
    # Research terms
    "연구": "study",
    "논문": "thesis",
    "박사": "doctoral",
    "석사": "masters",
    "학위": "degree",

    # AI/Tech terms
    "인공지능": "ai",
    "AI": "ai",
    "기계학습": "machine-learning",
    "딥러닝": "deep-learning",
    "신경망": "neural-network",

    # Philosophy terms
    "자유의지": "free-will",
    "의식": "consciousness",
    "의도": "intentionality",
    "윤리": "ethics",
    "도덕": "morality",
    "철학": "philosophy",

    # Neuroscience terms
    "뇌": "brain",
    "신경": "neural",
    "뇌과학": "neuroscience",
    "뇌신경공학": "neural-engineering",

    # Psychology terms
    "심리학": "psychology",
    "인지": "cognition",
    "행동": "behavior",

    # Theology terms
    "신학": "theology",
    "종교": "religion",
    "칼빈": "calvin",
    "어거스틴": "augustine",

    # General terms
    "불가능": "impossibility",
    "가능": "possibility",
    "가능성": "possibility",
    "분석": "analysis",
    "이론": "theory",
    "모델": "model",
    "프레임워크": "framework",
    "접근": "approach",
    "관점": "perspective",
    "방법": "method",
    "방법론": "methodology",

    # Disciplines
    "컴퓨터": "computer",
    "과학": "science",
    "공학": "engineering",
    "사회": "social",
    "자연": "natural",
    "인문": "humanities",

    # Common words
    "대한": "on",
    "에": "in",
    "의": "of",
    "를": "",
    "을": "",
    "가": "",
    "이": "",
    "는": "",
    "은": "",
    "와": "and",
    "과": "and",
}


def slugify(text: str, max_length: int = 50) -> str:
    """Convert Korean/special characters to English slug.

    This function ensures consistent directory naming by converting
    Korean research titles to English slugs.

    Args:
        text: Original text (may contain Korean, special chars)
        max_length: Maximum length of the slug

    Returns:
        ASCII-safe slug suitable for directory names

    Examples:
        >>> slugify("인공지능이 자유의지를 가질 수 없다는 연구")
        'ai-free-will-impossibility-study'

        >>> slugify("박사논문 - 심리학 접근")
        'doctoral-thesis-psychology-approach'

        >>> slugify("AI Ethics in the 21st Century")
        'ai-ethics-in-the-21st-century'
    """
    # Convert to lowercase
    slug = text.lower()

    # Replace Korean keywords with English
    for korean, english in KOREAN_TO_ENGLISH.items():
        slug = slug.replace(korean.lower(), english)

    # Normalize unicode (handles accented characters)
    slug = unicodedata.normalize('NFKD', slug)

    # Remove non-ASCII characters
    slug = slug.encode('ascii', 'ignore').decode('ascii')

    # Replace special characters and spaces with hyphens
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)

    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)

    # Strip leading/trailing hyphens
    slug = slug.strip('-')

    # Truncate to max length
    if len(slug) > max_length:
        # Try to cut at word boundary
        slug = slug[:max_length]
        last_hyphen = slug.rfind('-')
        if last_hyphen > max_length * 0.7:  # If hyphen in last 30%
            slug = slug[:last_hyphen]

    return slug


def generate_working_dir_name(topic: str, date_str: str) -> str:
    """Generate working directory name from topic and date.

    Args:
        topic: Research topic (may contain Korean)
        date_str: Date string (YYYY-MM-DD)

    Returns:
        Directory name in format: {slug}-{date}

    Examples:
        >>> generate_working_dir_name("인공지능 연구", "2026-01-20")
        'ai-study-2026-01-20'
    """
    slug = slugify(topic)
    return f"{slug}-{date_str}"


def validate_path_consistency(session_path: Path, expected_dir_name: str) -> tuple[bool, str]:
    """Validate that session.json path matches expected directory name.

    Args:
        session_path: Path to session.json
        expected_dir_name: Expected directory name

    Returns:
        Tuple of (is_valid, error_message)
    """
    actual_dir = session_path.parent.parent
    actual_dir_name = actual_dir.name

    if actual_dir_name != expected_dir_name:
        return False, f"Path mismatch: expected '{expected_dir_name}', got '{actual_dir_name}'"

    return True, ""


def find_working_directory(base_dir: Path, topic_slug: str) -> Path | None:
    """Find working directory by topic slug.

    Args:
        base_dir: Base directory (thesis-output)
        topic_slug: Topic slug from session.json

    Returns:
        Path to working directory, or None if not found
    """
    # Pattern: {slug}-YYYY-MM-DD
    pattern = f"{topic_slug}-*"

    matches = list(base_dir.glob(pattern))
    if not matches:
        return None

    # Return most recent if multiple matches
    if len(matches) > 1:
        matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)

    return matches[0]


def get_working_dir_from_session() -> Path:
    """Get working directory from active session.

    Returns:
        Path to working directory

    Raises:
        FileNotFoundError: If no active session found
        KeyError: If session file is missing required fields
    """
    import json

    session_file = Path("thesis-output") / "session.json"

    if not session_file.exists():
        raise FileNotFoundError(
            "No active session found. Run /thesis:init first to create a session."
        )

    with open(session_file, 'r', encoding='utf-8') as f:
        session = json.load(f)

    if "working_dir" not in session:
        raise KeyError("Session file is missing 'working_dir' field")

    working_dir = Path(session["working_dir"])

    if not working_dir.exists():
        raise FileNotFoundError(
            f"Working directory does not exist: {working_dir}"
        )

    return working_dir


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "인공지능이 자유의지를 가질 수 없다는 연구 - 심리학, 뇌신경공학, AI/컴퓨터과학, 철학, 신학(칼빈·어거스틴) 접근",
        "박사논문 연구",
        "AI Ethics and Morality",
        "기계학습 모델의 윤리적 판단 가능성",
    ]

    print("Slugify Test Cases:")
    print("=" * 80)
    for text in test_cases:
        slug = slugify(text)
        print(f"Original: {text}")
        print(f"Slug:     {slug}")
        print(f"Length:   {len(slug)}")
        print("-" * 80)
