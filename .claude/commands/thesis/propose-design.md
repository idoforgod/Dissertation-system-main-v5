---
name: propose-design
description: Stage 4 - 연구 설계 제안. 가설에 기반하여 양적/질적/혼합연구 설계를 수립하고 상세한 방법론을 제시합니다.
agent: design-proposer
allowed-tools:
  - Read(*)
  - Write(*)
  - Task(*)
model: opus
---

# /thesis:propose-design

**Stage 4**: 종합 연구 설계 제안

가설을 검증하기 위한 상세한 연구 방법론을 설계합니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:propose-design --hypotheses-file stage3-hypotheses.md
```

### 고급 옵션

```bash
# 연구 유형 지정
/thesis:propose-design --hypotheses-file <파일> --research-type quantitative

# 표본 크기 지정
/thesis:propose-design --hypotheses-file <파일> --target-n 300

# 예산 제한
/thesis:propose-design --hypotheses-file <파일> --budget-limit 30000

# 출력 경로
/thesis:propose-design --hypotheses-file <파일> --output stage4-research-design.md
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--hypotheses-file` | Yes | - | Stage 3 가설 파일 경로 |
| `--research-type` | No | `auto` | 연구 유형: `quantitative`, `qualitative`, `mixed`, `auto` |
| `--target-n` | No | `auto` | 목표 표본 크기 (power analysis 기반) |
| `--budget-limit` | No | `none` | 예산 제한 (USD) |
| `--timeline` | No | `18 months` | 연구 기간 |
| `--include-pilot` | No | `true` | 파일럿 연구 포함 여부 |
| `--output` | No | `stage4-research-design.md` | 출력 파일 경로 |

---

## 출력 구조

```
stage4-research-design.md
├─ 1. Research Design Overview
│  ├─ Research Type
│  ├─ Research Questions
│  ├─ Hypotheses
│  └─ Conceptual Model
├─ 2. Sampling Strategy
│  ├─ Population & Sampling Frame
│  ├─ Sampling Method
│  ├─ Sample Size Calculation
│  ├─ Inclusion/Exclusion Criteria
│  └─ Recruitment Plan
├─ 3. Measurement Instruments
│  ├─ Variable Operationalization
│  ├─ Scales & Items
│  ├─ Reliability & Validity
│  └─ Pilot Testing
├─ 4. Data Collection Procedures
│  ├─ Data Collection Method
│  ├─ Timeline
│  ├─ Quality Checks
│  └─ Ethical Considerations
├─ 5. Data Analysis Plan
│  ├─ Preliminary Analysis
│  ├─ Measurement Model (CFA)
│  ├─ Structural Model (SEM/Regression)
│  ├─ Hypothesis Testing
│  └─ Software & Tools
├─ 6. Budget & Resources
│  ├─ Personnel
│  ├─ Data Collection Costs
│  ├─ Software & Tools
│  └─ Total Budget
└─ 7. Timeline & Milestones
   └─ Gantt chart (18 months)
```

---

## 연구 유형별 설계

### Quantitative (양적연구)
- Survey design (설문)
- Experimental design (실험)
- Power analysis & sample size
- Statistical analysis plan

### Qualitative (질적연구)
- Interview protocol (인터뷰)
- Observation plan (관찰)
- Coding strategy (코딩)
- Saturation criteria

### Mixed Methods (혼합연구)
- Explanatory sequential (QUANT → qual)
- Exploratory sequential (qual → QUANT)
- Convergent parallel (QUANT + QUAL)
- Integration strategy

---

## 예시

### Example 1: 양적연구 설계

```bash
/thesis:propose-design --hypotheses-file stage3-hypotheses.md --research-type quantitative
```

**출력**:
```markdown
# Research Design Proposal

## 1. Research Design Overview

### Research Type
**Quantitative - Cross-Sectional Survey Design**

### Research Questions
1. Does transformational leadership positively affect employee creativity?
2. Does intrinsic motivation mediate this relationship?
3. Does organizational climate moderate this relationship?

### Conceptual Model
```
[Visual diagram here]
```

## 2. Sampling Strategy

### Population & Sampling Frame
- **Target Population**: Full-time employees in technology companies
- **Sampling Frame**: LinkedIn, industry associations
- **Geographic Scope**: United States

### Sampling Method
- **Type**: Stratified random sampling
- **Strata**: Company size (Small <50, Medium 50-500, Large >500)
- **Rationale**: Ensure representation across company sizes

### Sample Size Calculation

**Power Analysis**:
- **Effect size**: Medium (f² = 0.15)
- **Alpha**: 0.05
- **Power**: 0.80
- **Number of predictors**: 5
- **Required n**: 92 per analysis

**Attrition adjustment**:
- **Expected response rate**: 35%
- **Target survey distribution**: 350
- **Expected completed surveys**: 122
- **Final target n**: 350 invitations

### Inclusion Criteria
- Full-time employment (≥35 hours/week)
- At least 6 months tenure
- Direct supervisor for leadership rating
- Age 18+

### Exclusion Criteria
- Part-time workers
- Contractors/freelancers
- C-suite executives

### Recruitment Plan
1. **Week 1-2**: Partner with industry associations
2. **Week 3-4**: Distribute survey via email + LinkedIn
3. **Week 5**: First reminder
4. **Week 6**: Second reminder
5. **Week 7**: Final reminder + close survey

## 3. Measurement Instruments

### Transformational Leadership
- **Scale**: MLQ-5X (20 items)
- **Source**: Bass & Avolio (1995)
- **Sample item**: "My supervisor articulates a compelling vision of the future"
- **Response scale**: 5-point Likert (1=Not at all, 5=Frequently)
- **Reliability**: α = 0.89-0.92 in prior research
- **Dimensions**: Idealized influence, Inspirational motivation, Intellectual stimulation, Individualized consideration

### Employee Creativity
- **Scale**: TCDS (10 items)
- **Source**: Tierney, Farmer, & Graen (1999)
- **Sample item**: "I come up with creative solutions to problems"
- **Response scale**: 5-point Likert
- **Reliability**: α = 0.87 in prior research

[... 계속 ...]

## 5. Data Analysis Plan

### Preliminary Analysis
1. **Missing data**: Little's MCAR test, multiple imputation if <5%
2. **Outliers**: Mahalanobis distance (χ², p<.001)
3. **Normality**: Skewness/kurtosis (|2|), Q-Q plots
4. **Common method bias**: Harman's single factor test (<50% variance)

### Measurement Model (CFA)
- **Software**: AMOS 28
- **Estimator**: Maximum likelihood
- **Fit indices**:
  - χ²/df < 3
  - CFI > 0.90
  - TLI > 0.90
  - RMSEA < 0.08
  - SRMR < 0.08
- **Reliability**: Cronbach's α > 0.70, CR > 0.70
- **Validity**: AVE > 0.50, √AVE > inter-construct correlations

### Structural Model (Path Analysis)
- **H1-H2 (Direct effects)**: Path coefficients, p-values
- **H3 (Mediation)**: Hayes PROCESS Model 4, bootstrap 5000, 95% CI
- **H4 (Moderation)**: Hayes PROCESS Model 1, simple slopes at ±1 SD

### Hypothesis Testing
- **Significance level**: α = 0.05 (two-tailed)
- **Effect size**: Report β, R²
- **Confidence intervals**: 95% CI for all effects

## 6. Budget & Resources

| Category | Item | Cost (USD) |
|----------|------|------------|
| **Personnel** | Research assistant (200 hours × $25) | $5,000 |
| | Data collection support | $2,000 |
| **Data Collection** | Qualtrics subscription (1 year) | $1,500 |
| | Participant incentives (350 × $10) | $3,500 |
| **Software** | AMOS license (1 year) | $1,600 |
| | SPSS license | $1,200 |
| **Other** | IRB application | $500 |
| | Conference travel (dissemination) | $2,000 |
| | Contingency (10%) | $1,730 |
| **Total** | | **$19,030** |

## 7. Timeline & Milestones

| Phase | Duration | Milestones |
|-------|----------|------------|
| **Phase 1: Preparation** | Months 1-2 | IRB approval, finalize survey |
| **Phase 2: Pilot Study** | Month 3 | n=50, test reliability |
| **Phase 3: Main Data Collection** | Months 4-5 | n=350 targeted |
| **Phase 4: Data Analysis** | Months 6-8 | CFA, SEM, hypothesis testing |
| **Phase 5: Writing** | Months 9-12 | Draft manuscript |
| **Phase 6: Revision** | Months 13-15 | Incorporate feedback |
| **Phase 7: Submission** | Month 16 | Submit to journal |
| **Phase 8: Revision & Publication** | Months 17-18 | Address reviews |

**Total Duration**: 18 months
```

---

## 자동 결정 로직

`--research-type auto` 사용 시:

1. **가설 유형 분석**
   - Direct effect/mediation/moderation → Quantitative
   - Process/experience 질문 → Qualitative
   - Both → Mixed Methods

2. **표본 크기 계산**
   - Regression: 15 × predictors
   - SEM: 200+
   - Qualitative: 15-30

3. **예산 산정**
   - Quant survey: $15,000-25,000
   - Qual interviews: $10,000-20,000
   - Mixed: $30,000-50,000

---

## 다음 단계

```bash
# Stage 5로 진행 (타당성 평가)
/thesis:assess-feasibility --design-file stage4-research-design.md

# 또는 전체 워크플로우 재개
/thesis:run-paper-upload --resume-from stage5
```

---

## 관련 커맨드

- `/thesis:generate-hypotheses` - Stage 3 실행
- `/thesis:assess-feasibility` - Stage 5 실행
- `/thesis:status` - 진행 상태 확인

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**에이전트**: design-proposer (Opus)
