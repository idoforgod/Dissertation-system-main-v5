#!/usr/bin/env python3
"""Single Source of Truth for all workflow constants.

Every module that needs TOTAL_STEPS, PHASES, AGENT_STEP_MAP, PHASE_DIRS,
or TRANSLATION_TRIGGERS must import from this file. No other file should
define these values independently.

Usage:
    from workflow_constants import TOTAL_STEPS, PHASES, PHASE_DIRS
"""

# ---------------------------------------------------------------------------
# Total number of steps in the workflow
# ---------------------------------------------------------------------------
TOTAL_STEPS = 150

# ---------------------------------------------------------------------------
# Phase definitions: (phase_name, start_step, end_step)
# ---------------------------------------------------------------------------
PHASES = [
    ("phase0", 1, 18),
    ("phase1-wave1", 19, 34),
    ("phase1-wave2", 35, 50),
    ("phase1-wave3", 51, 66),
    ("phase1-wave4", 67, 74),
    ("phase1-wave5", 75, 82),
    ("hitl-2", 83, 88),
    ("phase2", 89, 108),
    ("phase3", 109, 132),
    ("phase4", 133, 146),
    ("completion", 147, 150),
]

# ---------------------------------------------------------------------------
# Phase → directory mapping (used by context_loader, performance_collector)
# ---------------------------------------------------------------------------
PHASE_DIRS = {
    "phase0": "00-session",
    "phase1": "01-literature",
    "phase2": "02-research-design",
    "phase3": "03-thesis",
    "phase4": "04-publication",
}

# Extended mapping including wave-level keys (used by performance_collector)
PHASE_DIRS_EXTENDED = {
    "phase0": "00-session",
    "phase1-wave1": "01-literature",
    "phase1-wave2": "01-literature",
    "phase1-wave3": "01-literature",
    "phase1-wave4": "01-literature",
    "phase1-wave5": "01-literature",
    "phase2-quantitative": "02-research-design",
    "phase2-qualitative": "02-research-design",
    "phase2-mixed": "02-research-design",
    "phase2-philosophical": "02-research-design",
    "phase3": "03-thesis",
    "phase4": "04-publication",
}

# ---------------------------------------------------------------------------
# Agent → step mapping (used by Hook for automatic checklist/session sync)
# ---------------------------------------------------------------------------
AGENT_STEP_MAP = {
    # Phase 0
    'topic-explorer': 9,

    # Phase 1 Wave 1
    'literature-searcher': 23,
    'seminal-works-analyst': 27,
    'trend-analyst': 31,
    'methodology-scanner': 33,

    # Phase 1 Wave 2
    'theoretical-framework-analyst': 38,
    'empirical-evidence-analyst': 42,
    'gap-identifier': 46,
    'variable-relationship-analyst': 49,

    # Phase 1 Wave 3
    'critical-reviewer': 54,
    'methodology-critic': 58,
    'limitation-analyst': 62,
    'future-direction-analyst': 65,

    # Phase 1 Wave 4
    'synthesis-agent': 70,
    'conceptual-model-builder': 73,

    # Phase 1 Wave 5
    'plagiarism-checker': 77,
    'unified-srcs-evaluator': 80,
    'research-synthesizer': 82,

    # Phase 2
    'hypothesis-developer': 95,
    'research-model-developer': 96,
    'sampling-designer': 97,
    'statistical-planner': 98,
    'paradigm-consultant': 99,
    'participant-selector': 100,
    'qualitative-data-designer': 101,
    'qualitative-analysis-planner': 102,
    'mixed-methods-designer': 103,
    'integration-strategist': 104,
    'philosophical-method-designer': 95,
    'source-text-selector': 96,
    'argument-construction-designer': 97,
    'philosophical-analysis-planner': 98,

    # Phase 3
    'thesis-architect': 113,
    'thesis-writer': None,  # Multiple steps (115, 117, 119, 121, 123)
    'thesis-reviewer': 125,

    # Phase 4
    'publication-strategist': 136,
    'manuscript-formatter': 142,

    # Simulation
    'simulation-controller': 150,
    'alphago-evaluator': 151,
    'autopilot-manager': 152,
    'thesis-writer-quick-rlm': None,  # Multiple chapters
}

# ---------------------------------------------------------------------------
# Wave/Phase boundaries that trigger auto-translation
# ---------------------------------------------------------------------------
TRANSLATION_TRIGGERS = {
    33: 'wave1',   # After methodology-scanner
    49: 'wave2',   # After variable-relationship-analyst
    65: 'wave3',   # After future-direction-analyst
    73: 'wave4',   # After conceptual-model-builder
    82: 'wave5',   # After research-synthesizer (Phase 1 complete)
    108: 'phase2',  # After Phase 2 completion
    132: 'phase3',  # After Phase 3 completion
    146: 'phase4',  # After Phase 4 completion
}


def get_phase_for_step(step: int) -> str:
    """Get the phase name for a given step number.

    Args:
        step: Step number (1-150)

    Returns:
        Phase name string

    Raises:
        ValueError: If step is out of range
    """
    if step < 1 or step > TOTAL_STEPS:
        raise ValueError(f"Step must be between 1 and {TOTAL_STEPS}, got {step}")

    for phase_name, start, end in PHASES:
        if start <= step <= end:
            return phase_name

    return "unknown"


def get_phase_dir(phase: str) -> str:
    """Get the directory name for a phase.

    Args:
        phase: Phase key (e.g. 'phase1', 'phase2')

    Returns:
        Directory name (e.g. '01-literature')

    Raises:
        ValueError: If phase is not recognized
    """
    if phase in PHASE_DIRS:
        return PHASE_DIRS[phase]
    if phase in PHASE_DIRS_EXTENDED:
        return PHASE_DIRS_EXTENDED[phase]
    raise ValueError(f"Unknown phase: {phase}. Valid: {list(PHASE_DIRS.keys())}")


# ---------------------------------------------------------------------------
# HITL checkpoint → step mapping (used by autopilot for auto-approval)
# ---------------------------------------------------------------------------
HITL_STEPS = {
    'HITL-0': 8,    # Phase 0: Initial setup approval
    'HITL-1': 18,   # Phase 0: Research question finalization
    'HITL-2': 83,   # Phase 1: Literature review approval
    'HITL-3': 89,   # Phase 2: Research type confirmation
    'HITL-4': 108,  # Phase 2: Research design approval
    'HITL-5': 109,  # Phase 3: Thesis format selection
    'HITL-6': 114,  # Phase 3: Outline approval
    'HITL-7': 125,  # Phase 3: Draft review
    'HITL-8': 146,  # Phase 4: Final approval
}

# ---------------------------------------------------------------------------
# Autopilot default settings (written to session.json when activated)
# ---------------------------------------------------------------------------
AUTOPILOT_DEFAULTS = {
    'enabled': False,
    'mode': 'full',        # full | semi | review-only
    'hitl_mode': 'auto-approve',  # auto-approve | manual | review-only
    'started_at': None,
    'target': 'completion',  # completion | phase0 | phase1 | phase2 | phase3 | phase4
    'paused': False,
    'pause_reason': None,
}
