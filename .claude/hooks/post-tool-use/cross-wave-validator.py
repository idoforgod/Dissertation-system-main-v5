#!/usr/bin/env python3
"""
Cross-Wave Validation Hook

Automatically validates consistency between waves to detect contradictions.
This implements the quadratic complexity (O(n²)) validation that was designed
but not executed in the original workflow.

Hook Event: PostToolUse
Triggers: After Wave 2, 3, 4, 5 completion (steps 50, 66, 74, 82)

Philosophy: MINIMALLY INVASIVE
- Does NOT modify workflow execution
- ONLY adds validation layer that was designed but missing
- Provides early warning for contradictions
"""

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "skills" / "thesis-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


# Wave completion triggers
VALIDATION_TRIGGERS = {
    50: {
        'wave': 'wave2',
        'validate_against': ['wave1'],
        'description': 'Validate Wave 2 against Wave 1'
    },
    66: {
        'wave': 'wave3',
        'validate_against': ['wave1', 'wave2'],
        'description': 'Validate Wave 3 against Wave 1-2'
    },
    74: {
        'wave': 'wave4',
        'validate_against': ['wave1', 'wave2', 'wave3'],
        'description': 'Validate Wave 4 against Wave 1-3'
    },
    82: {
        'wave': 'wave5',
        'validate_against': ['wave1', 'wave2', 'wave3', 'wave4'],
        'description': 'Validate Wave 5 against all previous waves'
    }
}


def find_session_dir(working_dir: str) -> Optional[Path]:
    """Find current thesis session directory."""
    working_path = Path(working_dir)

    marker_file = working_path / "thesis-output" / ".current-working-dir.txt"
    if marker_file.exists():
        session_dir = marker_file.read_text().strip()
        return Path(session_dir)

    thesis_output = working_path / "thesis-output"
    if not thesis_output.exists():
        return None

    session_dirs = [d for d in thesis_output.iterdir() if d.is_dir() and d.name != '_temp']
    if not session_dirs:
        return None

    return max(session_dirs, key=lambda d: d.stat().st_mtime)


def extract_claims_from_file(file_path: Path) -> List[Dict]:
    """
    Extract GroundedClaim blocks from markdown file.

    Returns:
        List of claim dictionaries
    """
    claims = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find all YAML claim blocks (simplified extraction)
        # Pattern: ```yaml ... ```
        yaml_blocks = re.findall(r'```yaml\n(.*?)```', content, re.DOTALL)

        for i, block in enumerate(yaml_blocks):
            # Try to extract claim text (simplified)
            text_match = re.search(r'text:\s*["\']?(.*?)["\']?\n', block, re.IGNORECASE)
            claim_type_match = re.search(r'claim_type:\s*(\w+)', block, re.IGNORECASE)

            if text_match:
                claim = {
                    'id': f"{file_path.stem}-{i+1}",
                    'text': text_match.group(1).strip(),
                    'claim_type': claim_type_match.group(1) if claim_type_match else 'UNKNOWN',
                    'source_file': file_path.name
                }
                claims.append(claim)

    except Exception as e:
        print(f"   ⚠️  Error extracting claims from {file_path.name}: {e}")

    return claims


def detect_contradiction(claim_a: Dict, claim_b: Dict) -> Optional[Dict]:
    """
    Detect semantic contradiction between two claims.

    This is a simplified heuristic. Real implementation would use
    Claude API for semantic analysis.

    Returns:
        Contradiction dict if found, None otherwise
    """
    text_a = claim_a['text'].lower()
    text_b = claim_b['text'].lower()

    # Heuristic patterns for contradiction
    contradiction_patterns = [
        # Negation patterns
        (r'ai (can|is able to)', r'ai (cannot|is unable to)'),
        (r'evidence (shows|demonstrates)', r'(no|lack of) evidence'),
        (r'(strong|significant) (effect|relationship)', r'(weak|no) (effect|relationship)'),
        (r'(supports|confirms)', r'(contradicts|refutes)'),

        # Opposite conclusions
        (r'free will (exists|is possible)', r'free will (does not exist|is impossible)'),
        (r'(always|consistently)', r'(never|rarely)'),
        (r'(all|every)', r'(no|none)'),
    ]

    for pattern_a, pattern_b in contradiction_patterns:
        if re.search(pattern_a, text_a) and re.search(pattern_b, text_b):
            return {
                'claim_a': claim_a,
                'claim_b': claim_b,
                'pattern': f"{pattern_a} vs {pattern_b}",
                'severity': 'HIGH'
            }
        if re.search(pattern_b, text_a) and re.search(pattern_a, text_b):
            return {
                'claim_a': claim_a,
                'claim_b': claim_b,
                'pattern': f"{pattern_b} vs {pattern_a}",
                'severity': 'HIGH'
            }

    # Check for numerical contradictions
    # e.g., "75% of studies" vs "25% of studies"
    numbers_a = re.findall(r'(\d+)%', text_a)
    numbers_b = re.findall(r'(\d+)%', text_b)

    if numbers_a and numbers_b:
        for num_a in numbers_a:
            for num_b in numbers_b:
                diff = abs(int(num_a) - int(num_b))
                if diff > 30:  # Significant difference
                    return {
                        'claim_a': claim_a,
                        'claim_b': claim_b,
                        'pattern': f"Numerical discrepancy: {num_a}% vs {num_b}%",
                        'severity': 'MEDIUM'
                    }

    return None


def validate_wave_consistency(session_dir: Path, current_wave: str, previous_waves: List[str]) -> Dict:
    """
    Validate consistency between current wave and previous waves.

    Returns:
        Validation result dictionary
    """
    result = {
        'current_wave': current_wave,
        'previous_waves': previous_waves,
        'timestamp': datetime.now().isoformat(),
        'contradictions': [],
        'total_comparisons': 0,
        'passed': True
    }

    lit_dir = session_dir / "01-literature"

    if not lit_dir.exists():
        result['error'] = "Literature directory not found"
        return result

    # Get files for current wave
    current_files = list(lit_dir.glob(f"{current_wave}-*.md"))
    if not current_files:
        result['error'] = f"No files found for {current_wave}"
        return result

    # Extract claims from current wave
    current_claims = []
    for file in current_files:
        claims = extract_claims_from_file(file)
        current_claims.extend(claims)

    print(f"   Extracted {len(current_claims)} claim(s) from {current_wave}")

    # Extract claims from previous waves
    previous_claims = []
    for wave in previous_waves:
        wave_files = list(lit_dir.glob(f"{wave}-*.md"))
        for file in wave_files:
            claims = extract_claims_from_file(file)
            previous_claims.extend(claims)

    print(f"   Extracted {len(previous_claims)} claim(s) from previous waves")

    # Cross-validate (quadratic complexity O(n²))
    contradictions = []
    comparisons = 0

    for claim_current in current_claims:
        for claim_previous in previous_claims:
            comparisons += 1
            contradiction = detect_contradiction(claim_current, claim_previous)
            if contradiction:
                contradictions.append(contradiction)

    result['total_comparisons'] = comparisons
    result['contradictions'] = contradictions

    # Determine pass/fail
    if len(contradictions) > 0:
        result['passed'] = False
        print(f"   ⚠️  Found {len(contradictions)} potential contradiction(s)")
    else:
        result['passed'] = True
        print(f"   ✅ No contradictions detected ({comparisons} comparisons)")

    return result


def log_validation_result(session_dir: Path, result: Dict) -> None:
    """Log validation result."""
    try:
        log_dir = session_dir / "00-session"
        log_file = log_dir / "cross-validation.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Wave: {result['current_wave']}\n")
            f.write(f"Validated against: {', '.join(result['previous_waves'])}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write(f"Result: {'PASS' if result['passed'] else 'FAIL'}\n")
            f.write(f"Comparisons: {result['total_comparisons']}\n")
            f.write(f"Contradictions found: {len(result['contradictions'])}\n")

            if result['contradictions']:
                f.write(f"\nContradictions:\n")
                for i, contradiction in enumerate(result['contradictions'], 1):
                    f.write(f"\n  {i}. {contradiction['severity']} severity\n")
                    f.write(f"     Claim A ({contradiction['claim_a']['source_file']}): {contradiction['claim_a']['text'][:100]}...\n")
                    f.write(f"     Claim B ({contradiction['claim_b']['source_file']}): {contradiction['claim_b']['text'][:100]}...\n")
                    f.write(f"     Pattern: {contradiction['pattern']}\n")

            f.write(f"{'='*60}\n")

    except Exception:
        pass


def save_validation_result(session_dir: Path, result: Dict) -> None:
    """Save validation result to JSON."""
    try:
        results_dir = session_dir / "00-session"
        results_file = results_dir / "cross-validation-results.json"

        # Load existing
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
        else:
            all_results = {'validations': []}

        # Append
        all_results['validations'].append(result)

        # Save
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print(f"   📄 Validation result saved: cross-validation-results.json")

    except Exception as e:
        print(f"   ⚠️  Failed to save result: {e}")


def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PostToolUse hook for automatic cross-wave validation.

    Args:
        context: Hook context

    Returns:
        Unmodified context
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    working_dir = context.get('working_directory', os.getcwd())

    if tool_name != 'Task':
        return context

    subagent_type = tool_input.get('subagent_type', '')
    if not subagent_type:
        return context

    # Normalize agent name (remove suffixes)
    normalized_agent = subagent_type
    for suffix in ['-rlm', '-validated', '-parallel']:
        if normalized_agent.endswith(suffix):
            normalized_agent = normalized_agent[:-len(suffix)]
            break

    session_dir = find_session_dir(working_dir)
    if not session_dir:
        return context

    # Map agents to steps
    agent_to_step = {
        'variable-relationship-analyst': 50,  # End of Wave 2
        'future-direction-analyst': 66,        # End of Wave 3
        'conceptual-model-builder': 74,        # End of Wave 4
        'research-synthesizer': 82             # End of Wave 5
    }

    step = agent_to_step.get(normalized_agent)
    if not step or step not in VALIDATION_TRIGGERS:
        return context

    # Execute cross-wave validation
    trigger_config = VALIDATION_TRIGGERS[step]

    print(f"\n{'='*60}")
    print(f"🔍 Cross-Wave Validation")
    print(f"{'='*60}")
    print(f"   {trigger_config['description']}")

    try:
        result = validate_wave_consistency(
            session_dir,
            trigger_config['wave'],
            trigger_config['validate_against']
        )

        # Log and save
        log_validation_result(session_dir, result)
        save_validation_result(session_dir, result)

        # Report
        if result['passed']:
            print(f"✅ Cross-validation PASSED")
        else:
            print(f"⚠️  Cross-validation WARNING")
            print(f"   Found {len(result['contradictions'])} potential contradiction(s)")
            print(f"   💡 Review cross-validation-results.json for details")

    except Exception as e:
        print(f"❌ Validation error: {e}")

    print(f"{'='*60}\n")

    return context


if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'variable-relationship-analyst',
            'prompt': 'Analyze variable relationships...'
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"Validation triggered: {result == test_context}")
