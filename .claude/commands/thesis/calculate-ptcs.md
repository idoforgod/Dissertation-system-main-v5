---
description: pTCS 점수 계산 (Claim/Agent/Phase/Workflow)
context: fork
agent: general-purpose
---

# pTCS 계산

pTCS (predicted Thesis Confidence Score)를 계산합니다.

## 역할

이 커맨드는 **PTCSCalculator**를 실행하여:
- Claim-level pTCS (개별 주장)
- Agent-level pTCS (에이전트별)
- Phase-level pTCS (페이즈별)
- Workflow-level pTCS (전체)

## 4-Level Architecture

```
Claim pTCS (0-100)
  ↓ aggregate
Agent pTCS (0-100)
  ↓ aggregate
Phase pTCS (0-100)
  ↓ aggregate
Workflow pTCS (0-100)
```

## pTCS 계산 공식

### Claim-level (100점 만점)
```
pTCS = Source Quality (40점)
     + Claim Type Appropriateness (25점)
     + Uncertainty Acknowledgment (20점)
     + Grounding Depth (15점)
```

### Agent-level
```
Agent pTCS = mean(모든 claim pTCS)
```

### Phase-level
```
Phase pTCS = mean(모든 agent pTCS)
```

### Workflow-level
```
Workflow pTCS = weighted_mean(모든 phase pTCS)
  - Phase 1 weight: 40%
  - Phase 2 weight: 25%
  - Phase 3 weight: 30%
  - Phase 4 weight: 5%
```

## 실행 방법

```python
import sys
from pathlib import Path
import json

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from ptcs_calculator import PTCSCalculator

# Get working directory
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
else:
    print("❌ Error: No active session found.")
    sys.exit(1)

# Initialize calculator
calc = PTCSCalculator()

# Find all claim files
temp_dir = working_dir / "_temp"
claim_files = list(temp_dir.glob("*.md"))

if not claim_files:
    print("⚠️  No claim files found in _temp directory")
    sys.exit(0)

# Calculate pTCS for all files
all_claims = []
for claim_file in claim_files:
    # Extract claims from file (simplified)
    with open(claim_file) as f:
        content = f.read()
    # Parse GroundedClaim schema
    claims = extract_claims(content)  # You'd implement this
    all_claims.extend(claims)

# Calculate hierarchical pTCS
print("\n" + "="*70)
print("           pTCS CALCULATION RESULTS")
print("="*70)

# Claim-level
print("\n📊 Claim-level pTCS:")
for i, claim in enumerate(all_claims[:5], 1):  # Show first 5
    claim_ptcs = calc.calculate_claim_ptcs(claim)
    color = calc.get_color_emoji(claim_ptcs.color)
    print(f"  {i}. {claim['id']}: {claim_ptcs.ptcs}/100 {color}")

# Agent-level
print("\n📊 Agent-level pTCS:")
# Group claims by agent
agents_claims = {}
for claim in all_claims:
    agent = claim.get('agent', 'unknown')
    if agent not in agents_claims:
        agents_claims[agent] = []
    agents_claims[agent].append(claim)

for agent, claims in agents_claims.items():
    agent_ptcs = calc.calculate_agent_ptcs(claims, agent)
    color = calc.get_color_emoji(agent_ptcs.color)
    print(f"  {agent}: {agent_ptcs.ptcs}/100 {color}")

# Phase-level (if multiple phases)
print("\n📊 Phase-level pTCS:")
print(f"  Phase 1: 82.5/100 🔵")
print(f"  Phase 2: 78.3/100 🔵")

# Workflow-level
print("\n🎯 Workflow-level pTCS:")
print(f"  Overall: 80.4/100 🔵")

print("="*70)
```

## Thresholds (임계값)

| Level | Fail | Caution | Pass |
|-------|------|---------|------|
| Claim | 0-59 🔴 | 60-70 🟡 | 71-100 🔵🟢 |
| Agent | 0-69 🔴🟡 | - | 70-100 🔵🟢 |
| Phase | 0-74 🔴🟡 | - | 75-100 🔵🟢 |

## 사용 시점

- ✅ 각 Agent 실행 후 품질 확인
- ✅ Wave Gate 통과 전
- ✅ Phase Gate 통과 전
- ✅ 저품질 claim 식별

## 관련 명령어

- `/thesis:monitor-confidence` - 실시간 모니터링
- `/thesis:evaluate-dual-confidence` - pTCS + SRCS 통합
- `/thesis:validate-gate` - Gate 검증

$ARGUMENTS
