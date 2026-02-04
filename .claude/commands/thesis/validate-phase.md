---
tags: [thesis, validation, quality-assurance]
description: Validate a specific phase of the thesis workflow
context: fork
agent: general-purpose
---

# Validate Phase

특정 페이즈의 검증을 수행합니다.

## Usage

```bash
/thesis:validate-phase [phase-number]
```

**Arguments:**
- `phase-number`: 검증할 페이즈 번호 (0-4)
  - 0: Initialization
  - 1: Literature Review
  - 2: Research Design
  - 3: Thesis Writing
  - 4: Publication Strategy

## What This Command Does

이 명령어는 Phase Validator를 사용하여 지정된 페이즈의 모든 critical steps를 검증합니다:

1. **파일 존재 여부 확인**: 각 스텝의 필수 출력 파일이 존재하는지 검증
2. **의존성 검증**: 이전 페이즈가 완료되었는지 확인
3. **상세 보고서 생성**: 통과/실패 상태와 누락된 파일 목록 제공

## Example Output

```
======================================================================
✅ PASSED: Phase 3: Thesis Writing
======================================================================

Completion: 8/8 steps (100.0%)
Timestamp: 2026-01-20 14:30:00

======================================================================
```

또는 실패 시:

```
======================================================================
❌ FAILED: Phase 3: Thesis Writing
======================================================================

Completion: 6/8 steps (75.0%)
Timestamp: 2026-01-20 14:30:00

❌ 2 step(s) failed:

  Step 117:
    - Missing: 03-thesis/chapter2-*.md

  Step 119:
    - Missing: 03-thesis/chapter3-*.md

======================================================================
```

## Implementation

```python
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from phase_validator import PhaseValidator

# Get phase number from arguments
phase = int("$ARGUMENTS")

# Get working directory from session.json
import json
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
else:
    print("❌ Error: No active session found. Run /thesis:init first.")
    sys.exit(1)

# Validate phase
validator = PhaseValidator(working_dir)
report = validator.validate_phase_verbose(phase)

# Print report
print(report.summary())

# Save report to file
report_file = working_dir / "validation-reports" / f"phase-{phase}-validation.json"
report_file.parent.mkdir(parents=True, exist_ok=True)
with open(report_file, 'w') as f:
    import json
    json.dump(report.to_dict(), f, indent=2)

print(f"\n📄 Report saved to: {report_file}")

# Exit with appropriate code
sys.exit(0 if report.all_passed else 1)
```

## When to Use

- ✅ **After completing a phase**: Verify all required outputs were generated
- ✅ **Before starting next phase**: Ensure prerequisites are met
- ✅ **During debugging**: Identify which files are missing
- ✅ **Quality assurance**: Regular validation checks

## Notes

- This command is **non-destructive** - it only reads files
- Does not modify any existing workflow files
- Can be run at any time without affecting ongoing work
- Complements existing workflow without replacing it

## Related Commands

- `/thesis:validate-all` - Validate all phases at once
- `/thesis:progress` - Show overall progress
- `/thesis:status` - Show current workflow status

$ARGUMENTS
