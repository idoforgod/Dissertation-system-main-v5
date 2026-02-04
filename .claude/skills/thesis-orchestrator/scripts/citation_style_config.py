"""Citation Style Configuration Module.

Defines citation style rules, display names, and format specifications
for the doctoral research workflow.

Used by:
- init_session.py (session creation)
- thesis-writer-rlm.md (RLM writing prompts)
- run_writing_validated.py (writing pipeline)
- manage_references.py (citation extraction)
- validation-checks/SKILL.md (format validation)

IMPORTANT: This is the SINGLE SOURCE OF TRUTH for citation style definitions.
All other files should import from this module to prevent format inconsistencies.
"""

# Machine-readable style keys
VALID_CITATION_STYLES = {"apa7", "chicago17", "mla9", "harvard", "ieee"}

# Default style (backward compatible)
DEFAULT_CITATION_STYLE = "apa7"

# Display names for LLM prompts
CITATION_DISPLAY_NAMES = {
    "apa7": "APA 7th Edition",
    "chicago17": "Chicago Manual of Style 17th Edition",
    "mla9": "MLA 9th Edition",
    "harvard": "Harvard Referencing",
    "ieee": "IEEE Citation Style",
}

# Note type: endnotes vs footnotes
CITATION_NOTE_TYPES = {
    "apa7": "endnotes",
    "chicago17": "footnotes",
    "mla9": "endnotes",
    "harvard": "endnotes",
    "ieee": "endnotes",
}

# In-text citation format
CITATION_IN_TEXT_FORMATS = {
    "apa7": "author_year_parenthetical",       # (Author, 2024)
    "chicago17": "footnote_superscript",        # ^1
    "mla9": "author_page_parenthetical",        # (Author 42)
    "harvard": "author_year_parenthetical",     # (Author 2024)
    "ieee": "numbered_bracket",                 # [1]
}

# In-text citation examples (for LLM prompt context)
CITATION_IN_TEXT_EXAMPLES = {
    "apa7": "(Smith, 2024) or Smith (2024)",
    "chicago17": "^1 (superscript footnote number)",
    "mla9": "(Smith 42) or Smith (42)",
    "harvard": "(Smith 2024) or Smith (2024)",
    "ieee": "[1] or [1, 2] or [1]-[3]",
}

# Bibliography section title (English)
CITATION_BIBLIOGRAPHY_TITLES = {
    "apa7": "References",
    "chicago17": "Bibliography",
    "mla9": "Works Cited",
    "harvard": "Reference List",
    "ieee": "References",
}

# Bibliography section title (Korean)
CITATION_BIBLIOGRAPHY_TITLES_KO = {
    "apa7": "참고문헌",
    "chicago17": "참고문헌",
    "mla9": "인용 문헌",
    "harvard": "참고문헌 목록",
    "ieee": "참고문헌",
}

# Multiple authors connector
CITATION_AUTHOR_CONNECTORS = {
    "apa7": "&",          # Smith & Jones (2024)
    "chicago17": "and",   # Smith and Jones
    "mla9": "and",        # Smith and Jones
    "harvard": "&",       # Smith & Jones (2024)
    "ieee": "and",        # Smith and Jones
}

# Et al. threshold (number of authors before using et al.)
CITATION_ET_AL_THRESHOLD = {
    "apa7": 3,       # 3+ authors → et al. on first citation
    "chicago17": 4,  # 4+ authors → et al.
    "mla9": 3,       # 3+ authors → et al.
    "harvard": 3,    # 3+ authors → et al.
    "ieee": 3,       # 3+ authors → et al.
}


def get_citation_config(style_key: str) -> dict:
    """Generate citation_config object for session.json.

    Args:
        style_key: Machine-readable style key (e.g., "apa7", "chicago17")

    Returns:
        Dictionary with citation configuration

    Raises:
        ValueError: If style_key is not valid
    """
    if style_key not in VALID_CITATION_STYLES:
        raise ValueError(
            f"Invalid citation style: '{style_key}'. "
            f"Valid styles: {sorted(VALID_CITATION_STYLES)}"
        )

    return {
        "style_key": style_key,
        "display_name": CITATION_DISPLAY_NAMES[style_key],
        "note_type": CITATION_NOTE_TYPES[style_key],
        "in_text_format": CITATION_IN_TEXT_FORMATS[style_key],
        "in_text_example": CITATION_IN_TEXT_EXAMPLES[style_key],
        "bibliography_title": CITATION_BIBLIOGRAPHY_TITLES[style_key],
        "bibliography_title_ko": CITATION_BIBLIOGRAPHY_TITLES_KO[style_key],
    }


def get_display_name(style_key: str) -> str:
    """Get human-readable display name for a citation style.

    Args:
        style_key: Machine-readable style key

    Returns:
        Display name string. Returns style_key itself if not found.
    """
    return CITATION_DISPLAY_NAMES.get(style_key, style_key)
