---
description: SRCS 4축 평가 (Citation, Grounding, Uncertainty, Verifiability)
context: fork
agent: general-purpose
---

# SRCS 평가

SRCS (Structured Research Claim Score) 4축 평가를 수행합니다.

## 역할

이 커맨드는 **SRCS 4축 종합 평가**를 실행합니다:
- CS (Citation Score): 출처 품질
- GS (Grounding Score): 근거 품질
- US (Uncertainty Score): 불확실성 표현
- VS (Verifiability Score): 검증가능성

## 전제 조건

- 평가할 문헌검토 또는 논문 파일 존재
- GroundedClaim 스키마 준수 파일

## 실행 방법

```python
import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from cross_validator import extract_claims_from_file
from srcs_evaluator import (
    evaluate_all_claims,
    generate_summary,
    generate_quality_report,
    DEFAULT_THRESHOLD,
)

# Get working directory from session.json
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
else:
    print("❌ Error: No active session found. Run /thesis:init first.")
    sys.exit(1)

# Find all GroundedClaim files in literature directory
lit_dir = working_dir / "01-literature"
claim_files = sorted(lit_dir.glob("wave*.md")) if lit_dir.exists() else []

if not claim_files:
    # Fallback to _temp directory
    temp_dir = working_dir / "_temp"
    claim_files = list(temp_dir.glob("*.md"))

if not claim_files:
    print("❌ Error: No claim files found")
    sys.exit(1)

# Extract claims from all files
all_claims = []
for claim_file in claim_files:
    claims = extract_claims_from_file(str(claim_file))
    all_claims.extend(claims)

# Evaluate all claims (returns a dict with overall_scores, evaluated_claims, etc.)
result = evaluate_all_claims(all_claims)

# Extract overall scores from result dict
overall_scores = result.get("overall_scores", {})
cs_avg = overall_scores.get("cs", 0)
gs_avg = overall_scores.get("gs", 0)
us_avg = overall_scores.get("us", 0)
vs_avg = overall_scores.get("vs", 0)
overall = overall_scores.get("total", 0)
grade = result.get("grade", "F")

# Print results
print("\n" + "="*70)
print("           SRCS EVALUATION RESULTS")
print("="*70)
print(f"\nTotal Claims Evaluated: {result.get('total_claims', 0)}")
print(f"\n📊 SRCS Scores:")
print(f"  CS (Citation):      {cs_avg:.1f}/100")
print(f"  GS (Grounding):     {gs_avg:.1f}/100")
print(f"  US (Uncertainty):   {us_avg:.1f}/100")
print(f"  VS (Verifiability): {vs_avg:.1f}/100")
print(f"\n🎯 Overall SRCS:      {overall:.1f}/100")
print(f"   Grade:             {grade}")
print(f"   Pass Rate:         {result.get('pass_rate', 0)}%")

# Threshold check
threshold = DEFAULT_THRESHOLD
if overall >= threshold:
    print(f"\n✅ PASSED: SRCS ({overall:.1f}) meets threshold ({threshold})")
else:
    print(f"\n❌ FAILED: SRCS ({overall:.1f}) below threshold ({threshold})")

# Save JSON summary report
report_file = working_dir / "srcs-evaluation-report.json"
generate_summary(result, report_file)

# Save markdown quality report
report_md = working_dir / "quality-report.md"
generate_quality_report(result, report_md)

print(f"\n📄 JSON report: {report_file}")
print(f"📄 Quality report: {report_md}")
print("="*70)
```

## 출력

```
thesis-output/[project]/
├── srcs-evaluation-report.json
└── quality-report.md
```

## SRCS 등급 기준

| Grade | Score Range | Description |
|-------|-------------|-------------|
| A+ | 90-100 | Outstanding |
| A | 85-89 | Excellent |
| B+ | 80-84 | Very Good |
| B | 75-79 | Good (Pass) |
| C | 70-74 | Acceptable (Caution) |
| D | 60-69 | Poor (Fail) |
| F | 0-59 | Unacceptable (Fail) |

**Threshold: 75점 이상 필수**

## 관련 명령어

- `/thesis:validate-phase` - Phase 검증
- `/thesis:check-plagiarism` - 표절 검사
- `/thesis:run-literature-review` - 문헌검토 실행

$ARGUMENTS
