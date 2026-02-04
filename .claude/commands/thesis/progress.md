---
tags: [thesis, progress, monitoring]
description: Show thesis workflow progress summary
---

# Progress

논문 워크플로우의 진행 상황을 간단히 보여줍니다.

## Usage

```bash
/thesis:progress
```

## What This Command Does

이 명령어는 현재 워크플로우의 진행 상황을 한눈에 보여줍니다:

1. **전체 완료율**: Critical steps 기준 완료 퍼센트
2. **페이즈별 상태**: 각 페이즈의 통과/실패 상태
3. **완료된 스텝 수**: 총 critical steps 대비 완료된 수

## Example Output

```
Workflow Progress: 78.5%
Completed: 11/14 critical steps

  ✅ Phase 0: Initialization
  ✅ Phase 1: Literature Review
  ✅ Phase 2: Research Design
  ❌ Phase 3: Thesis Writing
  ❌ Phase 4: Publication Strategy
```

## Implementation

```python
import sys
from pathlib import Path
import json

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from phase_validator import PhaseValidator

# Get working directory from session.json
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
else:
    print("❌ Error: No active session found. Run /thesis:init first.")
    sys.exit(1)

# Get progress summary
validator = PhaseValidator(working_dir)
progress = validator.get_progress_summary()

# Print summary
print(f"\nWorkflow Progress: {progress['completion_rate']:.1f}%")
print(f"Completed: {progress['completed_steps']}/{progress['total_critical_steps']} critical steps\n")

for phase, info in progress['phases_summary'].items():
    status = "✅" if info['passed'] else "❌"
    print(f"  {status} {info['name']}")

print()
```

## When to Use

- ✅ **Quick status check**: See progress at a glance
- ✅ **Daily standup**: Report current status
- ✅ **Before meetings**: Know where you are in the workflow
- ✅ **After work session**: See what was accomplished
- ✅ **Planning next steps**: Identify what needs to be done

## Difference from /thesis:status

| Command | Purpose | Detail Level |
|---------|---------|--------------|
| `/thesis:progress` | Quick validation-based progress | High-level, file existence |
| `/thesis:status` | Workflow execution status | Detailed, step-by-step tracking |

**Use `/thesis:progress`** when you want to know if all required files exist.

**Use `/thesis:status`** when you want to see the workflow execution state.

## Notes

- This command is **non-destructive** - only reads files
- Very fast - just checks file existence
- Does not require workflow to be running
- Provides instant feedback on completion status

## Related Commands

- `/thesis:validate-all` - Comprehensive validation with details
- `/thesis:validate-phase [N]` - Validate specific phase
- `/thesis:status` - Show workflow execution status

$ARGUMENTS
