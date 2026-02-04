# pTCS Specification: predicted Thesis Confidence Score

**Version**: 1.0
**Date**: 2026-01-20
**Inspired by**: AlphaFold pIDDT (predicted local Distance Difference Test)

---

## Overview

pTCS (predicted Thesis Confidence Score)는 논문 워크플로우의 실시간 신뢰도 평가 시스템입니다.

**핵심 개념**:
- AlphaFold의 pIDDT처럼 **자체 신뢰도 예측**
- 0-100점 척도 (AlphaFold와 동일)
- 실시간 자동 계산 (각 agent 실행 직후)
- 4-Level 계층 구조 (Claim → Agent → Phase → Workflow)

---

## Design Philosophy

### 1. Real-time Prediction (실시간 예측)

```
AlphaFold: Structure prediction + pIDDT (동시 계산)
     ↓
pTCS: Claim generation + pTCS (동시 계산)
```

**원칙**:
- 모든 claim 생성 시 즉시 pTCS 계산
- 사후 평가가 아닌 예측
- 조기 경보 시스템

### 2. Self-Confidence (자체 신뢰 평가)

```
AlphaFold: "이 residue 예측이 얼마나 정확한가?" (자체 판단)
     ↓
pTCS: "이 claim이 얼마나 신뢰할 만한가?" (자체 판단)
```

**원칙**:
- 외부 검증 전 자체 평가
- 모델 자체가 불확실성 인식
- Hallucination 자동 감지

### 3. Multi-Level Granularity (다층 세밀도)

```
AlphaFold:
  Residue-level → Domain-level → Chain-level → Structure-level

pTCS:
  Claim-level → Agent-level → Phase-level → Workflow-level
```

**원칙**:
- 미시적 평가 (각 주장)부터 거시적 평가 (전체 논문)까지
- 계층별 독립적 임계값
- 상위 레벨은 하위 레벨 집계

---

## 4-Level Architecture

### Level 1: Claim-level pTCS (Micro)

**대상**: 각 GroundedClaim

**척도**: 0-100점

**계산 공식**:
```python
claim_pTCS = (
    source_quality * 0.40 +           # 40%
    claim_type_appropriateness * 0.25 + # 25%
    uncertainty_acknowledgment * 0.20 + # 20%
    grounding_depth * 0.15            # 15%
)
```

**Component 1: Source Quality (40%)**

```
Breakdown (total 50 points, scaled to 40):
  - DOI present: 20 points
  - Primary source count: 10 points each (max 20 points)
  - Verified status: 10 points

Score = (sum / 50) * 40
```

**Component 2: Claim Type Appropriateness (25%)**

```
Base scores (0-100, scaled to 25):
  - FACTUAL: 100 if has_source, else 0
  - EMPIRICAL: 100 if has_data, else 0
  - THEORETICAL: 100 if has_framework, else 50
  - METHODOLOGICAL: 100 if has_method, else 60
  - INTERPRETIVE: 70 (base)
  - SPECULATIVE: 40 (base)

Score = (base_score / 100) * 25
```

**Component 3: Uncertainty Acknowledgment (20%)**

```
Breakdown (total 100 points, scaled to 20):
  - Has uncertainty field: 50 points
  - Confidence level (0-100): 50 points

Score = (sum / 100) * 20
```

**Component 4: Grounding Depth (15%)**

```
Based on source count (max 4 sources = 100 points):
  - 1 source: 25 points
  - 2 sources: 50 points
  - 3 sources: 75 points
  - 4+ sources: 100 points

Score = (min(count * 25, 100) / 100) * 15
```

**Color Coding**:
```
0-60:   🔴 Red    (low confidence)
61-70:  🟡 Yellow (medium confidence)
71-85:  🔵 Cyan   (good confidence)
86-100: 🟢 Green  (high confidence)
```

---

### Level 2: Agent-level pTCS (Meso)

**대상**: 각 Agent 출력 파일

**척도**: 0-100점

**계산 공식**:
```python
agent_pTCS = (
    avg_claim_pTCS * 0.50 +                # 50%
    coverage_completeness * 0.25 +         # 25%
    cross_reference_consistency * 0.15 +   # 15%
    hallucination_firewall_pass * 0.10     # 10%
)
```

**Component 1: Average Claim pTCS (50%)**

```
avg_claim_pTCS = mean([claim.pTCS for claim in all_claims])

Score = (avg_claim_pTCS / 100) * 50
```

**Component 2: Coverage Completeness (25%)**

```
coverage = (present_sections / required_sections) * 100

Score = (coverage / 100) * 25
```

**Component 3: Cross-Reference Consistency (15%)**

```
consistency = (1 - (conflicting_claims / total_claims)) * 100

Score = (consistency / 100) * 15
```

**Component 4: Hallucination Firewall Pass Rate (10%)**

```
Red flags: ["모든 연구가 일치", "100%", "예외 없이", ...]

pass_rate = (total_claims - flagged_claims) / total_claims

Score = pass_rate * 10
```

**Color Coding**: Same as Claim-level

---

### Level 3: Phase-level pTCS (Macro)

**대상**: 각 Phase (0-4)

**척도**: 0-100점

**계산 공식**:
```python
phase_pTCS = (
    avg_agent_pTCS * 0.60 +          # 60%
    outputs_completeness * 0.25 +    # 25%
    dependency_satisfaction * 0.15   # 15%
)
```

**Component 1: Average Agent pTCS (60%)**

```
avg_agent_pTCS = mean([agent.pTCS for agent in phase_agents])

Score = (avg_agent_pTCS / 100) * 60
```

**Component 2: Outputs Completeness (25%)**

```
completeness = (present_files / required_files) * 100

Score = (completeness / 100) * 25
```

**Component 3: Dependency Satisfaction (15%)**

```
satisfaction = (satisfied_dependencies / total_dependencies) * 100

Score = (satisfaction / 100) * 15
```

**Color Coding**: Same as Claim-level

---

### Level 4: Workflow-level pTCS (Global)

**대상**: 전체 논문 워크플로우

**척도**: 0-100점

**계산 공식**:
```python
workflow_pTCS = (
    phase_weighted_avg * 0.70 +      # 70%
    cross_phase_consistency * 0.20 + # 20%
    overall_SRCS * 0.10              # 10%
)
```

**Component 1: Phase-weighted Average (70%)**

```
phase_weights = {
    0: 0.05,  # Initialization: 5%
    1: 0.30,  # Literature Review: 30%
    2: 0.20,  # Research Design: 20%
    3: 0.35,  # Thesis Writing: 35%
    4: 0.10   # Publication: 10%
}

phase_weighted_avg = sum([
    phase_pTCS[i] * phase_weights[i] for i in range(5)
])

Score = phase_weighted_avg * 0.70
```

**Component 2: Cross-Phase Consistency (20%)**

```
consistency = (1 - (cross_phase_conflicts / total_cross_refs)) * 100

Score = (consistency / 100) * 20
```

**Component 3: Overall SRCS (10%)**

```
Score = (overall_SRCS / 100) * 10
```

**Color Coding**: Same as Claim-level

---

## Thresholds (임계값)

### pTCS Thresholds (강한 기준)

사용자 지시: **pTCS를 강한 기준으로 사용**

```yaml
Claim-level:
  FAIL: 0-59 (red) → Immediate review required
  CAUTION: 60-70 (yellow) → Review recommended
  PASS: 71-100 (cyan/green) → Acceptable

Agent-level:
  FAIL: 0-69 → Retry required
  CAUTION: 70-74 → Review recommended
  PASS: 75-100 → Proceed to next

Phase-level:
  FAIL: 0-74 → Rework required
  PASS: 75-100 → Phase complete

Workflow-level:
  FAIL: 0-74 → Overall rework
  PASS: 75-100 → Thesis ready
```

**핵심 원칙**:
- **pTCS < threshold → Automatic retry until pass**
- **No manual override** (강제 반복)
- **Fail-fast** (즉시 중단)

---

## Automatic Calculation Timing

### When pTCS is Calculated

```
@post_agent_execution
├─> Claim-level pTCS: ALL claims
├─> Agent-level pTCS: Agent output
└─> Alert if pTCS < 70

@wave_completion (Phase 1 only)
└─> No pTCS calculation (wait for SRCS)

@phase_completion
├─> Phase-level pTCS: Phase summary
└─> Alert if pTCS < 75

@workflow_completion
└─> Workflow-level pTCS: Final report
```

---

## Integration with SRCS

### pTCS (60%) + SRCS (40%) = Dual Confidence

```python
overall_confidence = (
    workflow_pTCS * 0.60 +
    overall_SRCS * 0.40
)
```

**Why 60-40 split?**:
- pTCS: Real-time, all agents (broad coverage)
- SRCS: Gated, critical points (deep quality)
- pTCS has wider coverage → higher weight

**Dual Decision Matrix**:

| pTCS | SRCS | Decision |
|------|------|----------|
| ≥75 | ≥75 | PASS |
| ≥75 | <75 | MANUAL_REVIEW (SRCS detected deep issues) |
| <75 | ≥75 | FAIL (pTCS is stronger criterion) |
| <75 | <75 | FAIL |

**핵심**: pTCS가 SRCS보다 **우선**합니다 (강한 기준).

---

## Metadata Format

### Claim-level pTCS Metadata

```yaml
claim:
  id: "LIT-001"
  text: "AI systems lack subjective experience"
  claim_type: THEORETICAL
  sources: [...]
  confidence: 85
  uncertainty: "Limited empirical evidence"

  # pTCS metadata (auto-generated)
  pTCS:
    score: 78.5
    breakdown:
      source_quality: 32.0
      claim_type_appropriate: 12.5
      uncertainty_acknowledgment: 18.5
      grounding_depth: 15.5
    color: cyan
    confidence_level: good
    timestamp: "2026-01-20T15:30:00"
```

### Agent-level pTCS Metadata

```yaml
agent_output:
  agent_name: "literature-searcher"

  # pTCS metadata
  pTCS:
    score: 82.0
    breakdown:
      avg_claim_ptcs: 41.0
      coverage_completeness: 25.0
      cross_reference_consistency: 15.0
      hallucination_firewall_pass: 10.0
    statistics:
      total_claims: 45
      low_confidence: 3
      medium_confidence: 8
      good_confidence: 20
      high_confidence: 14
    color: cyan
    confidence_level: good
    timestamp: "2026-01-20T15:35:00"
```

---

## Example Calculation

### Claim Example

**Input**:
```yaml
claim:
  id: "TEST-001"
  text: "AI systems cannot possess subjective experience"
  claim_type: THEORETICAL
  sources:
    - type: PRIMARY
      doi: "10.1234/test"
      verified: true
    - type: SECONDARY
      verified: false
  confidence: 85
  uncertainty: "Limited empirical evidence for consciousness theories"
```

**Calculation**:
```
Source Quality (40%):
  - DOI present: 20 points
  - Primary count (1): 10 points
  - Verified: 10 points
  Total: 40 points → (40/50)*40 = 32.0

Claim Type (25%):
  - THEORETICAL with framework: 50 points
  Total: 50 points → (50/100)*25 = 12.5

Uncertainty (20%):
  - Has uncertainty: 50 points
  - Confidence 85: 42.5 points
  Total: 92.5 points → (92.5/100)*20 = 18.5

Grounding Depth (15%):
  - 2 sources: 50 points
  Total: 50 points → (50/100)*15 = 7.5

pTCS = 32.0 + 12.5 + 18.5 + 7.5 = 70.5
Color: Cyan (71-85 range에 근접)
Confidence: good
```

**Output**: pTCS 70.5/100 🔵 (good)

---

## Comparison: AlphaFold pIDDT vs pTCS

| Aspect | AlphaFold pIDDT | pTCS |
|--------|-----------------|------|
| **Domain** | Protein structure | Thesis research |
| **Scale** | 0-100 | 0-100 |
| **Granularity** | Per residue | Per claim |
| **Calculation** | Real-time with prediction | Real-time with generation |
| **Purpose** | Structure confidence | Research confidence |
| **Color map** | Red-Yellow-Blue | Red-Yellow-Cyan-Green |
| **Threshold** | 70 (reliable structure) | 75 (reliable claim) |
| **Levels** | 4 (residue→structure) | 4 (claim→workflow) |

**Common Philosophy**:
- Self-assessment during prediction
- Multi-level granularity
- Automatic calculation
- Visual confidence indication

---

## Usage Example

```python
from ptcs_calculator import PTCSCalculator

# Initialize calculator
calc = PTCSCalculator()

# Calculate claim-level pTCS
claim = {
    'id': 'LIT-001',
    'text': 'AI systems lack consciousness',
    'claim_type': 'THEORETICAL',
    'sources': [...],
    'confidence': 80,
    'uncertainty': 'Philosophical debate ongoing'
}

result = calc.calculate_claim_ptcs(claim)
print(f"pTCS: {result.ptcs}/100 {calc.get_color_emoji(result.color)}")

# Check threshold
if result.ptcs < 70:
    print("⚠️ Below threshold - review required")
```

---

## Implementation Status

✅ **Phase 1 Complete**: pTCS Calculator
- ✅ Claim-level pTCS calculation
- ✅ Agent-level pTCS calculation
- ✅ Phase-level pTCS calculation
- ✅ Workflow-level pTCS calculation
- ✅ Color coding system
- ✅ Test suite

⏳ **Phase 2 Pending**: pTCS Enforcement
⏳ **Phase 3 Pending**: SRCS Integration
⏳ **Phase 4 Pending**: Dual Gate Controller
⏳ **Phase 5 Pending**: Real-time Monitor

---

**Specification Version**: 1.0
**Last Updated**: 2026-01-20
**Next Review**: After Phase 2 completion
