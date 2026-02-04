---
tags: [thesis, validation, quality-assurance]
description: Validate the entire thesis workflow (all phases)
context: fork
agent: general-purpose
---

# Validate All Phases

전체 워크플로우의 모든 페이즈를 한 번에 검증합니다.

## Usage

```bash
/thesis:validate-all
```

## What This Command Does

이 명령어는 Phase Validator를 사용하여 전체 워크플로우 (Phase 0-4)를 검증합니다:

1. **모든 페이즈 검증**: Phase 0부터 Phase 4까지 순차적으로 검증
2. **통합 보고서 생성**: 전체 완료율과 페이즈별 상태 제공
3. **상세 실패 정보**: 실패한 페이즈의 누락 파일 목록 표시
4. **JSON 보고서 저장**: 상세 검증 결과를 파일로 저장

## Example Output

성공 시:

```
######################################################################
✅ ALL PASSED: COMPLETE WORKFLOW VALIDATION
######################################################################

Working Directory: thesis-output/AI-free-will-impossibility-2026-01-20
Timestamp: 2026-01-20 14:30:00

Phase Summary:
  Passed: 5/5 phases
  Overall Completion: 100.0%

  ✅ Phase 0: Initialization: 100.0% complete
  ✅ Phase 1: Literature Review: 100.0% complete
  ✅ Phase 2: Research Design: 100.0% complete
  ✅ Phase 3: Thesis Writing: 100.0% complete
  ✅ Phase 4: Publication Strategy: 100.0% complete

######################################################################
```

실패 시:

```
######################################################################
❌ SOME FAILED: COMPLETE WORKFLOW VALIDATION
######################################################################

Working Directory: thesis-output/AI-free-will-impossibility-2026-01-20
Timestamp: 2026-01-20 14:30:00

Phase Summary:
  Passed: 3/5 phases
  Overall Completion: 78.5%

  ✅ Phase 0: Initialization: 100.0% complete
  ✅ Phase 1: Literature Review: 100.0% complete
  ✅ Phase 2: Research Design: 100.0% complete
  ❌ Phase 3: Thesis Writing: 75.0% complete
  ❌ Phase 4: Publication Strategy: 33.3% complete

######################################################################

======================================================================
❌ FAILED: Phase 3: Thesis Writing
======================================================================

Completion: 6/8 steps (75.0%)

❌ 2 step(s) failed:

  Step 117:
    - Missing: 03-thesis/chapter2-*.md

  Step 119:
    - Missing: 03-thesis/chapter3-*.md

======================================================================

======================================================================
❌ FAILED: Phase 4: Publication Strategy
======================================================================

Completion: 1/3 steps (33.3%)

❌ 2 step(s) failed:

  Step 138:
    - Missing: 04-publication/manuscript-formatted.md

  Step 139:
    - Missing: 04-publication/abstract-english.md

======================================================================
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

# Validate all phases
validator = PhaseValidator(working_dir)
report = validator.validate_all_phases()

# Print summary
print(report.summary())

# Print detailed reports for failed phases
for phase, phase_report in sorted(report.phase_reports.items()):
    if not phase_report.all_passed:
        print(phase_report.summary())

# Save comprehensive report
report_file = working_dir / "validation-reports" / "complete-workflow-validation.json"
validator.save_report(report, report_file)

# Exit with appropriate code
sys.exit(0 if report.all_phases_passed else 1)
```

## When to Use

- ✅ **Before final submission**: Comprehensive quality check
- ✅ **After major work**: Verify nothing was missed
- ✅ **Regular checkpoints**: Weekly validation during long projects
- ✅ **Debugging workflow issues**: Identify systemic problems
- ✅ **Quality assurance**: Ensure all deliverables are present

## Output Files

검증 결과는 다음 위치에 저장됩니다:

```
thesis-output/[your-project]/validation-reports/
└── complete-workflow-validation.json
```

이 JSON 파일은 다음 정보를 포함합니다:
- 전체 완료율
- 페이즈별 상세 결과
- 각 스텝의 검증 상태
- 누락된 파일 목록
- 타임스탬프

## Notes

- This command is **non-destructive** - only reads files
- Does not modify any existing workflow files
- Can be run at any time without affecting ongoing work
- Provides comprehensive quality assurance without replacing existing workflow

## Related Commands

- `/thesis:validate-phase [N]` - Validate specific phase only
- `/thesis:progress` - Show progress summary
- `/thesis:status` - Show current workflow status

$ARGUMENTS
