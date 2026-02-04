---
description: pTCS + SRCS 통합 신뢰도 평가
context: fork
agent: general-purpose
---

# Dual Confidence 평가

pTCS + SRCS 통합 신뢰도를 평가합니다.

## 역할

이 커맨드는 **DualConfidenceCalculator**를 실행하여:
- pTCS (60%) + SRCS (40%) 가중 평균
- 통합 의사결정 (PASS/FAIL/MANUAL_REVIEW)
- pTCS 우선 기준 적용 (강한 기준)

## Dual Confidence 공식

```python
combined_score = pTCS * 0.60 + SRCS * 0.40
```

## Decision Matrix (pTCS 우선)

| pTCS | SRCS | Decision |
|------|------|----------|
| ≥75 | ≥75 | ✅ PASS |
| ≥75 | <75 | ⚠️ MANUAL_REVIEW |
| <75 | ≥75 | ❌ FAIL (pTCS 우선) |
| <75 | <75 | ❌ FAIL |

**핵심 원칙**: pTCS < threshold → 자동 FAIL (SRCS와 무관)

## 실행 방법

```python
import sys
from pathlib import Path
import json

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from dual_confidence_system import DualConfidenceCalculator

# Get working directory
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
else:
    print("❌ Error: No active session found.")
    sys.exit(1)

# Get phase from arguments (default: current phase)
phase = int("$ARGUMENTS") if "$ARGUMENTS" else session.get("current_phase", 1)

# Calculate pTCS and SRCS for the phase
# (This would use actual calculators in real implementation)
phase_ptcs = 82.0  # Placeholder
phase_srcs = 78.0  # Placeholder

# Initialize calculator
calc = DualConfidenceCalculator()

# Calculate combined score
result = calc.calculate_combined_score(phase_ptcs, phase_srcs)

# Display results
print("\n" + "="*70)
print("           DUAL CONFIDENCE EVALUATION")
print("="*70)

print(f"\n📊 Individual Scores:")
print(f"  pTCS (60% weight): {result.ptcs}/100")
print(f"  SRCS (40% weight): {result.srcs}/100")

print(f"\n🎯 Combined Score:")
print(f"  Overall: {result.combined}/100")

print(f"\n📋 Decision: {result.decision}")
if result.decision == "PASS":
    print("  ✅ Both criteria met")
elif result.decision == "FAIL":
    print("  ❌ pTCS below threshold (강한 기준)")
elif result.decision == "MANUAL_REVIEW":
    print("  ⚠️  pTCS passed but SRCS needs review")

print(f"\n💬 Reasoning:")
print(f"  {result.reasoning}")

print("="*70)

# Save result
result_file = working_dir / f"dual-confidence-phase{phase}.json"
with open(result_file, 'w') as f:
    json.dump(result.to_dict(), f, indent=2)

print(f"\n💾 Result saved to: {result_file}")

# Exit code based on decision
if result.decision == "PASS":
    sys.exit(0)
elif result.decision == "MANUAL_REVIEW":
    sys.exit(2)  # Special code for manual review
else:
    sys.exit(1)
```

## 출력 예시

### Case 1: PASS (Both meet threshold)
```
══════════════════════════════════════════════════════════════════════
           DUAL CONFIDENCE EVALUATION
══════════════════════════════════════════════════════════════════════

📊 Individual Scores:
  pTCS (60% weight): 82.0/100
  SRCS (40% weight): 78.0/100

🎯 Combined Score:
  Overall: 80.4/100

📋 Decision: PASS
  ✅ Both criteria met

💬 Reasoning:
  Both pTCS (82.0) and SRCS (78.0) meet thresholds. Combined score: 80.4
══════════════════════════════════════════════════════════════════════
```

### Case 2: FAIL (pTCS below threshold)
```
══════════════════════════════════════════════════════════════════════
           DUAL CONFIDENCE EVALUATION
══════════════════════════════════════════════════════════════════════

📊 Individual Scores:
  pTCS (60% weight): 68.0/100
  SRCS (40% weight): 80.0/100

🎯 Combined Score:
  Overall: 72.8/100

📋 Decision: FAIL
  ❌ pTCS below threshold (강한 기준)

💬 Reasoning:
  pTCS (68.0) below threshold (70). pTCS is the stronger criterion -
  automatic FAIL.
══════════════════════════════════════════════════════════════════════
```

### Case 3: MANUAL_REVIEW (pTCS pass, SRCS fail)
```
══════════════════════════════════════════════════════════════════════
           DUAL CONFIDENCE EVALUATION
══════════════════════════════════════════════════════════════════════

📊 Individual Scores:
  pTCS (60% weight): 78.0/100
  SRCS (40% weight): 72.0/100

🎯 Combined Score:
  Overall: 75.6/100

📋 Decision: MANUAL_REVIEW
  ⚠️  pTCS passed but SRCS needs review

💬 Reasoning:
  pTCS (78.0) passed but SRCS (72.0) below threshold (75). Manual
  review recommended to investigate deep quality issues detected by SRCS.
══════════════════════════════════════════════════════════════════════
```

## 사용 시점

- ✅ Wave Gate 검증 전
- ✅ Phase Gate 검증 전
- ✅ 최종 품질 확인

## 관련 명령어

- `/thesis:calculate-ptcs` - pTCS 계산
- `/thesis:evaluate-srcs` - SRCS 평가
- `/thesis:validate-gate` - Gate 검증

$ARGUMENTS
