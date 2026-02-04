#!/usr/bin/env python3
"""
Thesis Workflow Automation Hook

Automatically handles post-processing after each agent completion:
1. Update checklist progress (checklist_manager.py)
2. Update session state (session.json)
3. Trigger Korean translation when phase/wave completes
4. Log completion for audit trail

Hook Event: PostToolUse
Triggers: After Task tool completion with thesis-related subagents

Philosophy: MINIMALLY INVASIVE
- Does NOT modify existing workflow commands
- Does NOT create new execution paths
- ONLY adds automation that was designed but not implemented
- Preserves 100% of original workflow philosophy
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "skills" / "thesis-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Import thesis orchestrator modules
try:
    from checklist_manager import update_step_status, get_progress, get_current_step
    from context_loader import load_context, find_session_file
    from workflow_constants import AGENT_STEP_MAP, TRANSLATION_TRIGGERS, PHASE_DIRS, get_phase_for_step
except ImportError:
    print("⚠️  Warning: Could not import thesis-orchestrator scripts")
    # Graceful degradation - hook won't crash if imports fail


def find_session_dir(working_dir: str) -> Optional[Path]:
    """
    Find the current thesis session directory via context_loader.

    Delegates to context_loader.find_session_file() for consistent path
    resolution across the entire workflow.

    Args:
        working_dir: Current working directory

    Returns:
        Path to session directory or None
    """
    try:
        session_file = find_session_file(Path(working_dir))
        # session.json is at {session_dir}/00-session/session.json
        return session_file.parent.parent
    except FileNotFoundError:
        return None


def update_checklist(session_dir: Path, step: int) -> bool:
    """
    Update checklist for completed step.

    Args:
        session_dir: Path to session directory
        step: Step number (1-150)

    Returns:
        True if successful, False otherwise
    """
    try:
        checklist_path = session_dir / "00-session" / "todo-checklist.md"

        if not checklist_path.exists():
            print(f"⚠️  Checklist not found: {checklist_path}")
            return False

        # Mark step as completed
        update_step_status(checklist_path, step, "completed")

        # Get updated progress
        progress = get_progress(checklist_path)

        print(f"✅ Checklist updated: Step {step} completed")
        print(f"   Progress: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)")

        return True

    except Exception as e:
        print(f"⚠️  Failed to update checklist: {e}")
        return False


def update_session_state(session_dir: Path, step: int, agent_name: str) -> bool:
    """
    Update session.json with current progress via context_loader.

    Uses context_loader.load_context() for consistent session access
    with path validation and deep merge.

    Args:
        session_dir: Path to session directory
        step: Step number (1-150)
        agent_name: Name of completed agent

    Returns:
        True if successful, False otherwise
    """
    try:
        session_path = session_dir / "00-session" / "session.json"

        if not session_path.exists():
            print(f"⚠️  Session file not found: {session_path}")
            return False

        # Load context via centralized loader (validates paths)
        context = load_context(session_path)

        # Determine current phase using centralized phase definitions
        if step <= 150:
            phase_detail = get_phase_for_step(step)
            # Normalize to coarse-grained phase for session tracking
            if phase_detail.startswith('phase1-'):
                coarse_phase = 'phase1'
            elif phase_detail == 'hitl-2':
                coarse_phase = 'phase2'  # HITL-2 grouped with Phase 2
            else:
                coarse_phase = phase_detail  # phase0, phase2, phase3, phase4, completion
        else:
            # Steps beyond 150 (simulation agents: 151, 152)
            coarse_phase = 'simulation'

        # Deep-merge update via context_loader (also sets updated_at)
        context.update_session({
            'workflow': {
                'current_step': step,
                'last_agent': agent_name,
                'last_checkpoint': datetime.now(timezone.utc).isoformat(),
                'current_phase': coarse_phase,
            }
        })

        print(f"✅ Session updated: {coarse_phase} - Step {step}")

        return True

    except Exception as e:
        print(f"⚠️  Failed to update session: {e}")
        return False


def trigger_auto_translation(session_dir: Path, trigger_name: str) -> bool:
    """
    Trigger automatic Korean translation for completed wave/phase.

    Args:
        session_dir: Path to session directory
        trigger_name: Name of translation trigger (wave1, wave2, phase2, etc.)

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"🌐 Auto-translation triggered: {trigger_name}")

        # Determine which directory to translate (using centralized PHASE_DIRS)
        translation_targets = {
            'wave1': session_dir / PHASE_DIRS['phase1'],
            'wave2': session_dir / PHASE_DIRS['phase1'],
            'wave3': session_dir / PHASE_DIRS['phase1'],
            'wave4': session_dir / PHASE_DIRS['phase1'],
            'wave5': session_dir / PHASE_DIRS['phase1'],
            'phase2': session_dir / PHASE_DIRS['phase2'],
            'phase3': session_dir / PHASE_DIRS['phase3'],
            'phase4': session_dir / PHASE_DIRS['phase4'],
        }

        target_dir = translation_targets.get(trigger_name)
        if not target_dir or not target_dir.exists():
            print(f"⚠️  Translation target not found: {target_dir}")
            return False

        # Find all untranslated .md files
        md_files = list(target_dir.glob('*.md'))
        untranslated = [f for f in md_files if not f.name.endswith('-ko.md')]

        if not untranslated:
            print(f"   No files to translate")
            return True

        print(f"   Found {len(untranslated)} file(s) to translate")

        # Call translate_to_korean.py script
        translate_script = SCRIPT_DIR / "translate_to_korean.py"

        if not translate_script.exists():
            print(f"⚠️  Translation script not found: {translate_script}")
            return False

        # Execute translation (placeholder - actual execution would use subprocess)
        # For now, log the intent
        log_dir = session_dir / "00-session"
        log_file = log_dir / "auto-translation.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().isoformat()
            f.write(f"\n[{timestamp}] {trigger_name}: {len(untranslated)} files queued for translation\n")
            for file in untranslated:
                f.write(f"  - {file.name}\n")

        print(f"   ✅ Translation queued (see auto-translation.log)")
        print(f"   💡 Run: /thesis:translate {target_dir}")

        return True

    except Exception as e:
        print(f"⚠️  Failed to trigger translation: {e}")
        return False


def log_completion(session_dir: Path, agent_name: str, step: int) -> None:
    """
    Log agent completion for audit trail.

    Args:
        session_dir: Path to session directory
        agent_name: Name of completed agent
        step: Step number
    """
    try:
        log_dir = session_dir / "00-session"
        log_file = log_dir / "workflow-execution.log"

        timestamp = datetime.now().isoformat()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] Step {step}: @{agent_name} completed\n")

    except Exception:
        pass  # Silent failure for logging


def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PostToolUse hook for thesis workflow automation.

    This hook runs AFTER each Task tool completion and performs:
    1. Checklist update
    2. Session state update
    3. Auto-translation trigger (at wave/phase boundaries)
    4. Audit logging

    IMPORTANT: This hook does NOT modify workflow execution.
    It ONLY adds post-processing automation.

    Args:
        context: Hook context with 'tool_name', 'tool_input', 'tool_output', 'working_directory'

    Returns:
        Unmodified context (this hook only has side effects)
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    tool_output = context.get('tool_output', {})
    working_dir = context.get('working_directory', os.getcwd())

    # Only process Task tool completions
    if tool_name != 'Task':
        return context

    # Only process thesis-related subagents
    subagent_type = tool_input.get('subagent_type', '')
    if not subagent_type:
        return context

    # Normalize agent name (remove common suffixes like -rlm, -validated)
    normalized_agent = subagent_type
    for suffix in ['-rlm', '-validated', '-parallel']:
        if normalized_agent.endswith(suffix):
            normalized_agent = normalized_agent[:-len(suffix)]
            break

    # Check if this is a thesis workflow agent
    if normalized_agent not in AGENT_STEP_MAP:
        return context

    # Find session directory
    session_dir = find_session_dir(working_dir)
    if not session_dir:
        print(f"⚠️  Could not find thesis session directory")
        return context

    print(f"\n{'='*60}")
    print(f"📋 Post-Processing: @{subagent_type}")
    print(f"{'='*60}")

    # Get step number for this agent
    step = AGENT_STEP_MAP[normalized_agent]

    # Special handling for thesis-writer (multiple chapters)
    if step is None and subagent_type == 'thesis-writer':
        # Try to infer from prompt
        prompt = tool_input.get('prompt', '').lower()
        if 'chapter 1' in prompt or 'ch.1' in prompt:
            step = 115
        elif 'chapter 2' in prompt or 'ch.2' in prompt:
            step = 117
        elif 'chapter 3' in prompt or 'ch.3' in prompt:
            step = 119
        elif 'chapter 4' in prompt or 'ch.4' in prompt:
            step = 121
        elif 'chapter 5' in prompt or 'ch.5' in prompt:
            step = 123
        else:
            step = 115  # Default to first chapter

    # Special handling for thesis-writer-quick-rlm (multiple chapters)
    if step is None and subagent_type == 'thesis-writer-quick-rlm':
        # Infer chapter from prompt
        prompt = tool_input.get('prompt', '').lower()
        if 'chapter 1' in prompt:
            step = 115
        elif 'chapter 2' in prompt:
            step = 117
        elif 'chapter 3' in prompt:
            step = 119
        elif 'chapter 4' in prompt:
            step = 121
        elif 'chapter 5' in prompt:
            step = 123
        else:
            step = 115

    # 1. Update checklist
    update_checklist(session_dir, step)

    # 2. Update session state
    update_session_state(session_dir, step, subagent_type)

    # 3. Log completion
    log_completion(session_dir, subagent_type, step)

    # 4. Check for translation trigger
    if step in TRANSLATION_TRIGGERS:
        trigger_name = TRANSLATION_TRIGGERS[step]
        trigger_auto_translation(session_dir, trigger_name)

    # 5. Special handling for simulation agents
    if normalized_agent == 'simulation-controller':
        print("💡 Simulation complete! Next steps:")
        print("   - Review simulation results")
        print("   - Upgrade to Full mode: run Full simulation")
        print("   - Continue workflow: proceed to next phase")

    elif normalized_agent == 'alphago-evaluator':
        print("🎯 AlphaGo evaluation complete!")
        print("   - Check recommended option")
        print("   - Run Full simulation on best option")

    elif normalized_agent == 'autopilot-manager':
        print("🤖 Autopilot execution complete!")
        print("   - Review all phases")
        print("   - Check final pTCS/SRCS scores")

    print(f"{'='*60}\n")

    # Return unmodified context (hook only has side effects)
    return context


if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'literature-searcher',
            'prompt': 'Search for relevant literature...'
        },
        'tool_output': {
            'success': True
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"Context returned: {result == test_context}")
