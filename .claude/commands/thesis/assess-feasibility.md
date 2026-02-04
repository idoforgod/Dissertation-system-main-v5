---
name: assess-feasibility
description: Stage 5 - 타당성 평가. 제안된 연구 설계의 실행 가능성을 자원, 시간, 윤리, 위험 측면에서 평가합니다.
agent: feasibility-assessor
allowed-tools:
  - Read(*)
  - Write(*)
model: sonnet
---

# /thesis:assess-feasibility

**Stage 5**: 연구 타당성 평가

제안된 연구 설계의 실행 가능성을 다각도로 평가합니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:assess-feasibility --design-file stage4-research-design.md
```

### 고급 옵션

```bash
# 평가 기준 가중치 조정
/thesis:assess-feasibility --design-file <파일> --weights "resource:0.3,time:0.3,ethics:0.2,risk:0.2"

# 최소 타당성 점수
/thesis:assess-feasibility --design-file <파일> --min-score 3.0

# 출력 경로
/thesis:assess-feasibility --design-file <파일> --output stage5-feasibility-assessment.md
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--design-file` | Yes | - | Stage 4 연구 설계 파일 경로 |
| `--weights` | No | `equal` | 평가 기준별 가중치 (resource, time, ethics, risk) |
| `--min-score` | No | `3.0` | 최소 타당성 점수 (1-5) |
| `--risk-tolerance` | No | `medium` | 위험 감수 수준: `low`, `medium`, `high` |
| `--output` | No | `stage5-feasibility-assessment.md` | 출력 파일 경로 |

---

## 출력 구조

```
stage5-feasibility-assessment.md
├─ 1. Feasibility Overview
│  ├─ Overall Feasibility Score
│  ├─ Rating (HIGH/MEDIUM/LOW)
│  └─ Go/No-Go Recommendation
├─ 2. Resource Assessment
│  ├─ Financial Resources (4.0/5.0)
│  ├─ Human Resources (3.5/5.0)
│  ├─ Technical Resources (4.5/5.0)
│  └─ Institutional Support (4.0/5.0)
├─ 3. Timeline Assessment
│  ├─ Realistic Timeline (4.0/5.0)
│  ├─ Critical Path Analysis
│  └─ Buffer Time Allocation
├─ 4. Ethical Assessment
│  ├─ IRB Approval Likelihood (5.0/5.0)
│  ├─ Participant Protection (5.0/5.0)
│  ├─ Data Privacy (5.0/5.0)
│  └─ Potential Harms (minimal)
├─ 5. Risk Assessment
│  ├─ Data Collection Risks (2.5/5.0 severity)
│  ├─ Analysis Risks (2.0/5.0)
│  ├─ Timeline Risks (3.0/5.0)
│  └─ Mitigation Strategies
└─ 6. Recommendations
   ├─ Critical Actions
   ├─ Contingency Plans
   └─ Go/Modify/No-Go Decision
```

---

## 평가 기준 (4개 차원)

### 1. Resource Feasibility (자원)
- **Financial**: 예산 충분성, 자금 확보 가능성
- **Human**: 연구팀 역량, 시간 투입 가능성
- **Technical**: 소프트웨어, 도구, 장비
- **Institutional**: 기관 지원, 네트워크 접근

### 2. Timeline Feasibility (시간)
- **Realistic**: 각 단계별 시간 배분 적절성
- **Critical Path**: 병목 구간 식별
- **Buffer**: 예비 시간 확보 여부

### 3. Ethical Feasibility (윤리)
- **IRB Approval**: 승인 가능성
- **Participant Protection**: 참여자 보호
- **Data Privacy**: 개인정보 보호
- **Conflicts of Interest**: 이해 충돌 여부

### 4. Risk Assessment (위험)
- **Data Collection**: 응답률, 접근성
- **Analysis**: 분석 복잡도, 실패 가능성
- **External**: 외부 요인 (경제, 정치 등)

---

## 평가 점수 해석

| Score | Rating | Interpretation | Recommendation |
|-------|--------|----------------|----------------|
| 4.0-5.0 | HIGH | 높은 실행 가능성 | ✅ GO - 진행 |
| 3.0-3.9 | MEDIUM | 중간 실행 가능성 | ⚠️ MODIFY - 수정 후 진행 |
| 2.0-2.9 | LOW | 낮은 실행 가능성 | 🔄 REDESIGN - 재설계 필요 |
| <2.0 | VERY LOW | 실행 불가능 | ❌ NO-GO - 중단 |

---

## 예시

### Example 1: 표준 타당성 평가

```bash
/thesis:assess-feasibility --design-file stage4-research-design.md
```

**출력**:
```markdown
# Feasibility Assessment Report

## 1. Feasibility Overview

### Overall Feasibility Score: **3.75/5.0**
### Rating: **HIGH** ✅
### Recommendation: **GO** - Proceed with minor adjustments

---

## 2. Resource Assessment

### Financial Resources: **4.0/5.0** ✅
- **Budget Requirement**: $19,030
- **Funding Status**: Partial funding secured ($15,000)
- **Gap**: $4,030
- **Assessment**: Likely obtainable through department grant
- **Recommendation**: Apply for graduate research grant ($5,000 typical)

### Human Resources: **3.5/5.0** ⚠️
- **Principal Investigator**: PhD student (adequate)
- **Research Assistant**: Budgeted 200 hours
- **Statistical Consultant**: Available via university
- **Concern**: PI time management (coursework + research)
- **Recommendation**: Create detailed weekly schedule, block 15 hrs/week for research

### Technical Resources: **4.5/5.0** ✅
- **Survey Platform**: Qualtrics (university license available)
- **Statistical Software**: AMOS & SPSS (university license)
- **Computing**: Personal laptop sufficient
- **Assessment**: All technical needs met

### Institutional Support: **4.0/5.0** ✅
- **Advisor Support**: Strong (advisor experienced in this method)
- **IRB**: Standard process, 4-6 week turnaround
- **Library Access**: Full access to journals
- **Assessment**: Good institutional support

**Resource Feasibility Score: 4.0/5.0** ✅

---

## 3. Timeline Assessment

### Realistic Timeline: **4.0/5.0** ✅

| Phase | Proposed | Realistic | Buffer | Feasible? |
|-------|----------|-----------|--------|-----------|
| IRB Approval | 2 months | 2-3 months | +1 month | ✅ Yes |
| Pilot Study | 1 month | 1 month | sufficient | ✅ Yes |
| Main Data Collection | 2 months | 2-3 months | +1 month | ✅ Yes |
| Data Analysis | 3 months | 3-4 months | +1 month | ✅ Yes |
| Writing | 4 months | 4-5 months | +1 month | ✅ Yes |

**Total**: 18 months proposed → 20-22 months realistic (with buffers)

### Critical Path Analysis
**Longest path**: IRB → Pilot → Main Study → Analysis → Writing
- **Critical milestones**: IRB approval (must start early), Data collection (peak semester for participants)
- **Risk**: IRB delays could cascade

### Recommendation
- Submit IRB 1 month earlier than planned
- Add 2-month buffer at end
- Total timeline: 20 months (realistic)

**Timeline Feasibility Score: 4.0/5.0** ✅

---

## 4. Ethical Assessment

### IRB Approval Likelihood: **5.0/5.0** ✅
- **Risk Level**: Minimal risk (anonymous survey)
- **Vulnerable Populations**: None
- **Deception**: None
- **Assessment**: Standard expedited review, high approval likelihood

### Participant Protection: **5.0/5.0** ✅
- **Informed Consent**: Clear online consent form
- **Anonymity**: IP addresses not collected
- **Right to Withdraw**: Stated clearly
- **Assessment**: Excellent protection measures

### Data Privacy: **5.0/5.0** ✅
- **Storage**: Encrypted Qualtrics server
- **Access**: Password-protected, PI only
- **Retention**: 5 years (per policy)
- **Compliance**: GDPR/CCPA compliant

### Potential Harms: **Minimal**
- No physical harm
- No psychological distress expected
- No sensitive topics (e.g., trauma, illegal activity)

**Ethical Feasibility Score: 5.0/5.0** ✅

---

## 5. Risk Assessment

### Data Collection Risks: **Severity 2.5/5.0** (MEDIUM)

**Risk 1: Low Response Rate**
- **Probability**: Medium (35% expected)
- **Impact**: High (underpowered study)
- **Mitigation**:
  - Over-sample (350 invitations for 122 needed)
  - Offer $10 gift cards
  - Send 3 reminders
  - Leverage industry associations
- **Residual Risk**: Low

**Risk 2: Sample Bias**
- **Probability**: Medium (self-selection)
- **Impact**: Medium (external validity)
- **Mitigation**:
  - Stratified sampling
  - Compare early vs. late responders
  - Report response rate and limitations
- **Residual Risk**: Low

### Analysis Risks: **Severity 2.0/5.0** (LOW)

**Risk 3: Poor Model Fit**
- **Probability**: Low (validated scales)
- **Impact**: Medium (need model revision)
- **Mitigation**:
  - Pilot test (n=50)
  - Check reliability before main study
  - Have backup scales identified
- **Residual Risk**: Very Low

**Risk 4: Non-Significant Results**
- **Probability**: Medium (exploratory study)
- **Impact**: Medium (publication challenge)
- **Mitigation**:
  - Power analysis ensures 80% power
  - Alternative hypotheses prepared
  - Frame as contribution even if null
- **Residual Risk**: Low

### Timeline Risks: **Severity 3.0/5.0** (MEDIUM)

**Risk 5: IRB Delays**
- **Probability**: Medium (peak season)
- **Impact**: High (cascades to all phases)
- **Mitigation**:
  - Submit early (Month 0 instead of Month 1)
  - Prepare thorough application
  - Advisor pre-review
- **Residual Risk**: Medium

### External Risks: **Severity 1.5/5.0** (LOW)
- Economic downturn: Low probability, medium impact
- Organizational changes: Low probability, low impact

**Overall Risk Score: 2.3/5.0** (LOW) ✅

---

## 6. Recommendations

### Critical Actions (Must Do)
1. ✅ **Submit IRB 1 month early** (by end of Month 0)
2. ✅ **Secure $4,030 funding gap** (apply for grant by Month 1)
3. ✅ **Create research schedule** (15 hrs/week blocked)
4. ✅ **Pilot test by Month 3** (n=50, check reliability)

### Contingency Plans
- **If response rate <30%**: Extend data collection by 2 weeks, increase incentives to $15
- **If IRB delayed >8 weeks**: Adjust timeline, push back data collection to next semester
- **If funding not secured**: Reduce incentives to $5, increase target n to compensate for lower response

### Go/Modify/No-Go Decision

**Decision: GO ✅**
- Overall feasibility: 3.75/5.0 (HIGH)
- All dimensions ≥3.5
- Risks are manageable
- Minor adjustments needed (timeline buffer, early IRB)

**Recommended Adjustments**:
1. Add 2-month buffer → 20 months total
2. Submit IRB 1 month early
3. Secure funding gap before Month 2
```

---

## 자동 평가 로직

```python
def calculate_feasibility_score(resource, timeline, ethics, risk):
    """
    Calculate overall feasibility score

    Args:
        resource: Resource feasibility (1-5)
        timeline: Timeline feasibility (1-5)
        ethics: Ethical feasibility (1-5)
        risk: Risk severity (1-5, lower is better)

    Returns:
        float: Overall feasibility score
    """
    # Invert risk (higher risk = lower feasibility)
    risk_feasibility = 6 - risk

    # Weighted average
    weights = {
        "resource": 0.3,
        "timeline": 0.3,
        "ethics": 0.2,
        "risk": 0.2
    }

    overall = (
        resource * weights["resource"] +
        timeline * weights["timeline"] +
        ethics * weights["ethics"] +
        risk_feasibility * weights["risk"]
    )

    return round(overall, 2)
```

---

## 다음 단계

```bash
# Stage 6으로 진행 (제안서 통합)
/thesis:integrate-proposal --feasibility-file stage5-feasibility-assessment.md

# 또는 전체 워크플로우 재개
/thesis:run-paper-upload --resume-from stage6
```

---

## 관련 커맨드

- `/thesis:propose-design` - Stage 4 실행
- `/thesis:integrate-proposal` - Stage 6 실행
- `/thesis:status` - 진행 상태 확인

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**에이전트**: feasibility-assessor (Sonnet)
