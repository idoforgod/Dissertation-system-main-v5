# Dual Confidence System - Quick Guide

**5분 안에 시작하기**

---

## 🎯 이것은 무엇인가?

**pTCS (predicted Thesis Confidence Score)**: AlphaFold의 pIDDT처럼 **자체 신뢰도를 예측**하는 시스템

**핵심 개념**:
- 📊 **실시간**: 모든 claim/agent 생성 즉시 pTCS 계산
- 🔒 **강한 기준**: pTCS < threshold → 자동 재작업
- 🔄 **자동 반복**: 기준 충족까지 작업 반복
- 🎨 **시각화**: 🔴🟡🔵🟢 컬러 코딩

---

## 🚀 30초 Quickstart

```bash
# 1. pTCS 계산 테스트
python3 .claude/skills/thesis-orchestrator/scripts/ptcs_calculator.py --test

# 2. pTCS Enforcement 테스트
python3 .claude/skills/thesis-orchestrator/scripts/ptcs_enforcer.py --test

# 3. 실시간 모니터 테스트
python3 .claude/skills/thesis-orchestrator/scripts/confidence_monitor.py --test
```

---

## 📖 기본 사용법

### 1. Claim-level pTCS 계산

```python
from ptcs_calculator import PTCSCalculator

calc = PTCSCalculator()

# Calculate pTCS for a claim
claim = {
    'id': 'LIT-001',
    'text': 'AI systems lack consciousness',
    'claim_type': 'THEORETICAL',
    'sources': [
        {'type': 'PRIMARY', 'doi': '10.1234/test', 'verified': True}
    ],
    'confidence': 80,
    'uncertainty': 'Philosophical debate ongoing'
}

result = calc.calculate_claim_ptcs(claim)
print(f"pTCS: {result.ptcs}/100 {calc.get_color_emoji(result.color)}")
# Output: pTCS: 78.5/100 🔵
```

### 2. Agent 실행 with pTCS Enforcement

```python
from ptcs_enforcer import PTCSEnforcer

enforcer = PTCSEnforcer(max_retries=3)

# Execute agent with enforcement (retry-until-pass)
result = enforcer.enforce_agent_execution(
    agent_name="literature-searcher",
    agent_function=your_agent_function,
    threshold=70
)

# If pTCS < 70: Automatically retries (up to 3 times)
# If pTCS ≥ 70: Proceeds to next agent
```

### 3. Wave/Phase Gate Validation

```python
from gate_controller import GateController

controller = GateController(working_dir=your_project_dir)

# Validate Wave Gate 1
decision = controller.validate_wave_gate(
    gate_number=1,
    wave_ptcs=82,
    wave_srcs=78,
    auto_retry=True  # Automatically retry if failed
)

# Result: PASS/FAIL/MANUAL_REVIEW
```

### 4. Real-time Monitoring

```python
from confidence_monitor import ConfidenceMonitor

monitor = ConfidenceMonitor(
    project_name="your-project",
    working_dir=your_project_dir
)

# Track agent execution
agent_ptcs = calc.calculate_agent_ptcs(claims, "agent-name")
monitor.track_agent(agent_ptcs)

# Generate dashboard
dashboard = monitor.generate_dashboard()
print(dashboard)
```

---

## 🎨 Color Coding (AlphaFold 스타일)

```
pTCS Score:
  0-60:   🔴 Red    → Immediate review required
  61-70:  🟡 Yellow → Review recommended
  71-85:  🔵 Cyan   → Good confidence
  86-100: 🟢 Green  → High confidence
```

---

## 📏 Thresholds (임계값)

```yaml
Claim-level:
  FAIL: 0-59 (red)
  CAUTION: 60-70 (yellow)
  PASS: 71-100 (cyan/green)

Agent-level:
  FAIL: 0-69 → Retry required
  PASS: 70-100 → Proceed

Wave/Phase-level:
  FAIL: 0-74 → Rework required
  PASS: 75-100 → Gate passed
```

---

## 🔄 Dual Confidence (pTCS + SRCS)

**가중치**:
```python
overall_confidence = pTCS * 0.60 + SRCS * 0.40
```

**Decision Matrix** (pTCS is STRONGER):

| pTCS | SRCS | Decision |
|------|------|----------|
| ≥75 | ≥75 | ✅ PASS |
| ≥75 | <75 | ⚠️ MANUAL_REVIEW |
| <75 | ≥75 | ❌ FAIL (pTCS 우선) |
| <75 | <75 | ❌ FAIL |

---

## 🚪 Gate System

**9 Gates Total**:
```
Wave Gates (Phase 1):
  Gate 1: Wave 1 (문헌탐색 4개 에이전트)
  Gate 2: Wave 2 (이론/실증 4개 에이전트)
  Gate 3: Wave 3 (비판적 검토 4개 에이전트)
  Gate 4: Wave 4 (종합 2개 에이전트)

Phase Gates:
  Phase 0: Initialization
  Phase 1: Literature Review
  Phase 2: Research Design
  Phase 3: Thesis Writing
  Phase 4: Publication Strategy
```

**Auto-Retry**:
- Wave gates: 최대 3회 재시도
- Phase gates: 최대 2회 재시도

---

## 📊 Dashboard Example

```
══════════════════════════════════════════════════════════════════════
           THESIS CONFIDENCE MONITOR (pTCS + SRCS)
══════════════════════════════════════════════════════════════════════

Project: AI-free-will-impossibility
Current Phase: 1
Current Agent: literature-searcher
Agent pTCS: 82/100 🔵

──────────────────────────────────────────────────────────────────────
📊 Real-time pTCS Status (Predictive)
──────────────────────────────────────────────────────────────────────
Total Claims: 45
  🔴 Low (0-60):       3 (  6.7%)
  🟡 Medium (61-70):   8 ( 17.8%)
  🔵 Good (71-85):    20 ( 44.4%)
  🟢 High (86-100):   14 ( 31.1%)

Agent Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20.0%
Completed: 8/41 agents

──────────────────────────────────────────────────────────────────────
🎯 SRCS Gate Status (Evaluative)
──────────────────────────────────────────────────────────────────────
Wave Gates:
  Gate 1: ✅ PASSED (pTCS: 82.0, SRCS: 78.0)
  Gate 2: ⏳ IN PROGRESS
  Gate 3: ⏭️  PENDING

──────────────────────────────────────────────────────────────────────
⚠️  Active Alerts
──────────────────────────────────────────────────────────────────────
1. ⚠️ Warning: Claim LIT-012 has low confidence (pTCS: 58)
2. ⚠️ Warning: Agent trend-analyst needs review (pTCS: 68)
──────────────────────────────────────────────────────────────────────
```

---

## 🛠️ 파일 구조

```
.claude/skills/thesis-orchestrator/scripts/
├── ptcs_calculator.py         # pTCS 계산 엔진
├── ptcs_enforcer.py           # 강제 반복 로직
├── dual_confidence_system.py  # pTCS + SRCS 통합
├── gate_controller.py         # Gate 자동 제어
└── confidence_monitor.py      # 실시간 모니터

.claude/skills/thesis-orchestrator/
├── DUAL-CONFIDENCE-IMPLEMENTATION-REPORT.md  # 전체 보고서
├── DUAL-CONFIDENCE-QUICK-GUIDE.md           # 이 파일
└── references/ptcs-specification.md         # 전체 사양서
```

---

## ⚡ 일반적인 워크플로우

```python
# 1. Initialize
from ptcs_calculator import PTCSCalculator
from ptcs_enforcer import PTCSEnforcer
from gate_controller import GateController
from confidence_monitor import ConfidenceMonitor

calc = PTCSCalculator()
enforcer = PTCSEnforcer(max_retries=3)
controller = GateController(working_dir=project_dir)
monitor = ConfidenceMonitor(project_name="your-project", working_dir=project_dir)

# 2. Execute agents with enforcement
for agent_name, agent_func in agents:
    result = enforcer.enforce_agent_execution(
        agent_name=agent_name,
        agent_function=agent_func,
        threshold=70
    )

    # Track for monitoring
    claims = extract_claims(result)
    agent_ptcs = calc.calculate_agent_ptcs(claims, agent_name)
    monitor.track_agent(agent_ptcs)

# 3. Validate gates
decision = controller.validate_wave_gate(
    gate_number=1,
    wave_ptcs=calculate_wave_ptcs(),
    wave_srcs=calculate_wave_srcs(),
    auto_retry=True
)

# 4. Monitor progress
dashboard = monitor.generate_dashboard()
print(dashboard)
```

---

## 💡 주요 원칙

1. **pTCS는 강한 기준**
   - pTCS < threshold → 자동 실패 (SRCS와 무관)
   - SRCS는 보완적 역할 (deep quality check)

2. **자동 반복 (Retry-until-pass)**
   - 기준 미달 → 자동 재시도
   - 수동 override 없음

3. **실시간 모니터링**
   - 모든 claim/agent 즉시 pTCS 계산
   - 문제 조기 발견 (fail-fast)

4. **시각적 피드백**
   - 🔴🟡🔵🟢 컬러 코딩
   - Progress bars
   - Alert system

---

## 🔍 Troubleshooting

### Q: pTCS 점수가 낮게 나옵니다

**A**: 다음을 확인하세요:
1. Sources에 DOI가 있는가? (+20점)
2. Primary source를 사용하는가? (+10점/개)
3. Uncertainty를 명시했는가? (+10점)
4. Claim type이 적절한가?

### Q: Agent가 계속 재시도됩니다

**A**: pTCS < 70이 원인입니다:
1. 낮은 pTCS claim 개선
2. Source 품질 향상 (DOI, primary sources)
3. Uncertainty 명시
4. Claim type 재검토

### Q: Gate가 실패합니다

**A**: pTCS와 SRCS를 모두 확인:
1. pTCS < 75? → pTCS 개선 우선 (강한 기준)
2. SRCS < 75? → 출처 품질, 근거 강화
3. Dashboard에서 낮은 confidence claim 확인

---

## 📚 추가 자료

- **전체 보고서**: `DUAL-CONFIDENCE-IMPLEMENTATION-REPORT.md`
- **전체 사양서**: `references/ptcs-specification.md`
- **SRCS 사양**: `references/srcs-evaluation.md`

---

**5분이면 시작할 수 있습니다!**

```bash
# Right now:
cd .claude/skills/thesis-orchestrator
python3 scripts/ptcs_calculator.py --test
python3 scripts/confidence_monitor.py --test
```
