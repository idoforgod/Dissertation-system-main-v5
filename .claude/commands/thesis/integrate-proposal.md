---
name: integrate-proposal
description: Stage 6 - 제안서 통합. 모든 Stage 결과를 40-60페이지 연구 제안서로 통합하고 품질 검증을 수행합니다.
agent: proposal-integrator
allowed-tools:
  - Read(*)
  - Write(*)
  - Task(*)
model: opus
---

# /thesis:integrate-proposal

**Stage 6**: 종합 연구 제안서 통합

모든 Stage 결과를 학술적 연구 제안서로 통합합니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:integrate-proposal --feasibility-file stage5-feasibility-assessment.md
```

### 고급 옵션

```bash
# 모든 Stage 파일 명시적 지정
/thesis:integrate-proposal \
  --analysis-file stage1-paper-analysis.md \
  --gap-file stage2-gap-analysis.md \
  --hypotheses-file stage3-hypotheses.md \
  --design-file stage4-research-design.md \
  --feasibility-file stage5-feasibility-assessment.md

# 출력 형식 지정
/thesis:integrate-proposal --feasibility-file <파일> --format "markdown,pdf"

# 페이지 목표
/thesis:integrate-proposal --feasibility-file <파일> --target-pages 50

# 출력 경로
/thesis:integrate-proposal --feasibility-file <파일> --output final-research-proposal.md
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--feasibility-file` | Yes* | - | Stage 5 타당성 평가 파일 (또는 모든 파일 명시) |
| `--analysis-file` | No | `stage1-*.md` | Stage 1 논문 분석 파일 |
| `--gap-file` | No | `stage2-*.md` | Stage 2 갭 분석 파일 |
| `--hypotheses-file` | No | `stage3-*.md` | Stage 3 가설 파일 |
| `--design-file` | No | `stage4-*.md` | Stage 4 연구 설계 파일 |
| `--format` | No | `markdown` | 출력 형식: `markdown`, `pdf`, `docx` (쉼표 구분) |
| `--target-pages` | No | `50` | 목표 페이지 수 (40-60 권장) |
| `--include-validation` | No | `true` | GRA + pTCS 검증 포함 여부 |
| `--output` | No | `final-research-proposal.md` | 출력 파일 경로 |

---

## 출력 구조 (APA 7th Format)

```
final-research-proposal.md (40-60 pages)
├─ Title Page
├─ Abstract (250-300 words)
├─ Table of Contents
├─ 1. Introduction (8-10 pages)
│  ├─ 1.1 Background
│  ├─ 1.2 Problem Statement
│  ├─ 1.3 Research Questions
│  ├─ 1.4 Significance of the Study
│  └─ 1.5 Outline of the Proposal
├─ 2. Literature Review (12-15 pages)
│  ├─ 2.1 Theoretical Framework
│  ├─ 2.2 Empirical Evidence
│  ├─ 2.3 Research Gaps
│  └─ 2.4 Conceptual Model
├─ 3. Hypotheses (5-6 pages)
│  ├─ 3.1 Hypothesis Development
│  ├─ 3.2 Theoretical Rationale
│  └─ 3.3 Conceptual Model
├─ 4. Research Methodology (12-15 pages)
│  ├─ 4.1 Research Design
│  ├─ 4.2 Sampling Strategy
│  ├─ 4.3 Measurement Instruments
│  ├─ 4.4 Data Collection Procedures
│  ├─ 4.5 Data Analysis Plan
│  └─ 4.6 Ethical Considerations
├─ 5. Expected Results and Contributions (4-5 pages)
│  ├─ 5.1 Expected Findings
│  ├─ 5.2 Theoretical Contributions
│  ├─ 5.3 Practical Implications
│  └─ 5.4 Limitations
├─ 6. Timeline and Budget (3-4 pages)
│  ├─ 6.1 Research Timeline (Gantt Chart)
│  ├─ 6.2 Budget Breakdown
│  └─ 6.3 Resource Requirements
├─ References (APA 7th)
├─ Appendices
│  ├─ Appendix A: Survey Instrument
│  ├─ Appendix B: Interview Protocol
│  ├─ Appendix C: IRB Materials
│  └─ Appendix D: Statistical Power Analysis
└─ Quality Validation Report
   ├─ GRA Compliance: 98.5%
   ├─ pTCS Average: 0.72
   └─ Overall Quality: 4.1/5.0
```

---

## 자동 품질 검증 (Quality Validation)

통합 과정에서 자동으로 실행됩니다:

### 1. GRA (GroundedClaim) Compliance
- **기준**: 95% 이상 인용 필요
- **검사**: 모든 주장에 출처 확인
- **결과**: 98.5% (✅ PASS)

### 2. pTCS (Probabilistic Truth-Claim Score)
- **기준**: 평균 0.6 이상
- **검사**: 각 주장의 증거 품질 평가
- **결과**: 0.72 (✅ PASS)

### 3. Citation Format
- **기준**: APA 7th Edition 100% 준수
- **검사**: 인용 형식 자동 검사
- **결과**: 3 errors found (⚠️ FIX)

### 4. Reference Completeness
- **기준**: 본문 인용 = 참고문헌 100% 일치
- **검사**: 누락된 참고문헌 확인
- **결과**: 2 missing references (⚠️ FIX)

---

## 예시

### Example 1: 표준 제안서 통합

```bash
/thesis:integrate-proposal --feasibility-file stage5-feasibility-assessment.md
```

**Process**:
```
🔄 Reading Stage 1-5 outputs...
  ✅ stage1-paper-analysis.md (20 pages)
  ✅ stage2-gap-analysis.md (10 pages)
  ✅ stage3-hypotheses.md (12 pages)
  ✅ stage4-research-design.md (25 pages)
  ✅ stage5-feasibility-assessment.md (8 pages)

📝 Synthesizing Introduction...
  ├─ Background from Stage 1
  ├─ Problem from Stage 2
  └─ Research Questions from Stage 3

📚 Integrating Literature Review...
  ├─ Theoretical framework (Stage 1)
  ├─ Empirical evidence (Stage 1)
  ├─ Research gaps (Stage 2)
  └─ Conceptual model (Stage 3)

🔬 Compiling Methodology...
  ├─ Research design (Stage 4)
  ├─ Sampling (Stage 4)
  ├─ Instruments (Stage 4)
  └─ Analysis plan (Stage 4)

💰 Adding Timeline & Budget...
  └─ From Stage 4 + Stage 5

✅ Quality Validation Running...
  ├─ GRA Compliance: 98.5% ✅
  ├─ pTCS Average: 0.72 ✅
  ├─ Citation Format: 3 errors ⚠️
  └─ Reference Completeness: 2 missing ⚠️

📄 Final Proposal Generated:
  └─ final-research-proposal.md (52 pages)

⚠️  Quality Issues Found:
  1. Fix 3 APA citation format errors (see validation-report.md:L45-52)
  2. Add 2 missing references to reference list (see validation-report.md:L60-65)

📊 Next Step:
  Run /thesis:review-proposal to address quality issues
```

**Output Structure**:
```markdown
# Research Proposal: The Moderating Role of Organizational Climate in the Transformational Leadership-Innovation Relationship

## Abstract

This study investigates how organizational climate moderates the relationship
between transformational leadership and employee creativity. Building on
transformational leadership theory (Bass, 1985) and interactionist perspectives
(Woodman et al., 1993), we propose that the positive effect of transformational
leadership on employee creativity is stronger in innovative organizational
climates...

[250 words]

**Keywords**: transformational leadership, employee creativity, organizational
climate, moderation, innovation

---

## 1. Introduction

### 1.1 Background

Innovation has become a critical competitive advantage for organizations
operating in dynamic environments (Amabile, 1996; Anderson et al., 2014).
Employee creativity, defined as the generation of novel and useful ideas
(Zhou & George, 2001), serves as the foundation for organizational innovation
(Mumford & Gustafson, 1988). Among various antecedents of employee creativity,
transformational leadership has emerged as a significant predictor (Rosing et al.,
2011; Shin & Zhou, 2003).

Transformational leadership, characterized by idealized influence, inspirational
motivation, intellectual stimulation, and individualized consideration (Bass, 1985),
has been shown to enhance employee creativity through multiple mechanisms...

[... 8-10 pages total ...]

### 1.4 Significance of the Study

This research makes several important contributions:

**Theoretical Contributions**:
1. Extends transformational leadership theory by identifying organizational
   climate as a critical boundary condition
2. Integrates leadership and climate literatures to explain innovation processes
3. Addresses unacknowledged limitation in Smith & Johnson (2023) regarding
   universal applicability of transformational leadership effects

**Practical Implications**:
1. Informs leadership development programs by highlighting contextual factors
2. Guides organizational climate interventions to maximize leadership effectiveness
3. Provides actionable insights for managers seeking to enhance team creativity

**Methodological Contributions**:
1. Employs rigorous survey design with validated instruments (MLQ, TCDS)
2. Uses advanced statistical techniques (moderated regression, simple slopes)
3. Includes pilot study to ensure measurement quality

---

## 2. Literature Review

### 2.1 Theoretical Framework

#### 2.1.1 Transformational Leadership Theory

Transformational leadership, originally conceptualized by Burns (1978) and
later refined by Bass (1985), represents a leadership approach that motivates
followers to transcend self-interest for the collective good...

[Detailed theoretical exposition with 15-20 citations]

#### 2.1.2 Organizational Climate Theory

Organizational climate refers to shared perceptions of organizational practices,
procedures, and behaviors that are rewarded and supported (Schneider et al., 2013)...

[... continues for 12-15 pages ...]

### 2.3 Research Gaps

Despite extensive research on transformational leadership and creativity, three
critical gaps remain:

**Gap 1: Boundary Conditions Unexplored** (Priority Score: 4.5/5.0)

Existing research assumes transformational leadership universally enhances
creativity (Rosing et al., 2011; Shin & Zhou, 2003). However, as Smith and
Johnson (2023, p. 23) acknowledge, "Future research should examine moderating
factors that may enhance or diminish the transformational leadership-creativity
relationship." This gap represents a significant theoretical limitation, as
contingency perspectives suggest leadership effectiveness depends on contextual
factors (Fiedler, 1967; Vroom & Yetton, 1973)...

[Each gap detailed with evidence from Stage 1-2]

---

## 3. Hypotheses

### 3.1 Hypothesis Development

Based on the identified research gaps, we propose the following hypotheses:

**H1**: Transformational leadership will positively affect employee creativity.

**Rationale**: Transformational leaders inspire employees to think creatively
through intellectual stimulation, provide autonomy through individualized
consideration, and create psychological safety through idealized influence
(Bass, 1985; Shin & Zhou, 2003). Meta-analytic evidence (Rosing et al., 2011)
supports this relationship (ρ = 0.32)...

**H2**: Organizational climate will moderate the relationship between
transformational leadership and employee creativity, such that the positive
relationship is stronger in innovative climates.

**Rationale**: According to interactionist perspectives (Woodman et al., 1993),
creativity emerges from the interaction between individual, group, and
organizational factors. An innovative climate, characterized by support for
experimentation and tolerance for failure (Anderson & West, 1998), amplifies
transformational leadership effects by...

[Each hypothesis with theoretical + empirical support, 5-6 pages total]

### 3.3 Conceptual Model

```
                  Organizational Climate (Z)
                            ↓ (moderates)
Transformational    →    Employee
Leadership (X)           Creativity (Y)

H1: β₁ > 0
H2: β₃ > 0 (interaction term X×Z)
```

Figure 1. Conceptual model showing the moderating effect of organizational
climate on the transformational leadership-creativity relationship.

---

## 4. Research Methodology

### 4.1 Research Design

This study employs a **cross-sectional survey design** to test the proposed
hypotheses. The quantitative approach is appropriate because: (1) hypotheses
specify directional relationships that require statistical testing, (2) validated
measurement instruments exist for all constructs, and (3) the research aims to
generalize findings to a broader population (Creswell & Creswell, 2018)...

[... methodology section from Stage 4, 12-15 pages ...]

### 4.5 Data Analysis Plan

#### 4.5.1 Preliminary Analysis

**Missing Data**: Little's MCAR test will be conducted. If data are missing
completely at random (p > .05) and missing rate is below 5%, multiple imputation
using the expectation-maximization algorithm will be employed (Schafer & Graham, 2002).

**Outliers**: Multivariate outliers will be identified using Mahalanobis distance
(χ², p < .001). Cases exceeding critical values will be examined and removed if
data entry errors are confirmed (Tabachnick & Fidell, 2019).

[... detailed analysis plan ...]

#### 4.5.3 Hypothesis Testing

**H1 (Direct Effect)**:
- **Method**: Hierarchical multiple regression
- **Model**: Y = β₀ + β₁X + β₂(controls) + ε
- **Criterion**: β₁ significant at p < .05, two-tailed

**H2 (Moderation)**:
- **Method**: Hayes (2018) PROCESS Model 1
- **Model**: Y = β₀ + β₁X + β₂Z + β₃(X×Z) + β₄(controls) + ε
- **Criterion**: β₃ significant at p < .05
- **Probing**: Simple slopes at Z = M ± 1 SD
- **Visualization**: Interaction plot

---

## 5. Expected Results and Contributions

### 5.1 Expected Findings

Based on theory and prior evidence, we expect:

1. **H1 Supported**: Positive main effect of transformational leadership
   (β ≈ 0.30-0.40, based on Rosing et al., 2011 meta-analysis)

2. **H2 Supported**: Significant interaction term (β₃ > 0), with simple slopes
   showing:
   - High innovative climate: β = 0.45-0.50 (strong positive)
   - Low innovative climate: β = 0.15-0.20 (weak positive)

[... continues for 4-5 pages ...]

---

## 6. Timeline and Budget

### 6.1 Research Timeline

| Phase | Duration | Start | End | Milestones |
|-------|----------|-------|-----|------------|
| **Phase 1: Preparation** | 2 months | Month 1 | Month 2 | IRB submission (Week 2), Survey finalization (Week 6) |
| **Phase 2: Pilot Study** | 1 month | Month 3 | Month 3 | Pilot data (n=50), Reliability check |
| **Phase 3: Main Data Collection** | 2 months | Month 4 | Month 5 | 350 surveys distributed, 122 completed |
| **Phase 4: Data Analysis** | 3 months | Month 6 | Month 8 | CFA, regression, PROCESS |
| **Phase 5: Writing** | 4 months | Month 9 | Month 12 | Draft chapters 1-5 |
| **Phase 6: Revision** | 3 months | Month 13 | Month 15 | Committee feedback incorporated |
| **Phase 7: Submission** | 1 month | Month 16 | Month 16 | Submit to target journal |
| **Phase 8: Publication** | 4 months | Month 17 | Month 20 | Address reviews, publication |

**Total Duration**: 20 months (including 2-month buffer)

[Gantt chart visualization]

### 6.2 Budget Breakdown

[From Stage 4 + 5]

---

## References

[APA 7th format, alphabetically ordered]

Anderson, N., Potočnik, K., & Zhou, J. (2014). Innovation and creativity in
    organizations: A state-of-the-science review, prospective commentary, and
    guiding framework. *Journal of Management*, *40*(5), 1297-1333.
    https://doi.org/10.1177/0149206314527128

Bass, B. M. (1985). *Leadership and performance beyond expectations*. Free Press.

[... 50-60 references total ...]

---

## Appendix A: Survey Instrument

[Complete survey with all items]

## Appendix B: IRB Materials

[Informed consent, debriefing]

## Appendix C: Statistical Power Analysis

[Detailed power analysis calculations]

---

## Quality Validation Report

**GRA Compliance**: 98.5% (✅ PASS, threshold: 95%)
- Total claims: 134
- Cited claims: 132
- Uncited claims: 2 (see L234, L567)

**pTCS Average**: 0.72 (✅ PASS, threshold: 0.6)
- High confidence (≥0.8): 45 claims (33.6%)
- Moderate confidence (0.6-0.8): 68 claims (50.7%)
- Low confidence (<0.6): 21 claims (15.7%)

**Citation Format**: 3 errors (⚠️ FIX)
- L123: Missing comma before year "(Bass 1985)" → "(Bass, 1985)"
- L456: Wrong ampersand "Smith and Johnson" → "Smith & Johnson"
- L789: Missing period at end of reference

**Reference Completeness**: 2 missing (⚠️ FIX)
- "Woodman et al. (1993)" cited but not in references
- "Schafer & Graham (2002)" cited but not in references

**Overall Quality Score**: 4.1/5.0 (✅ HIGH)

**Recommendation**: Fix minor citation issues before HITL review
```

---

## 자동 통합 프로세스

1. **Content Synthesis** (60-90분)
   - Stage 1-5 파일 읽기
   - 중복 제거, 일관성 확보
   - APA 형식 적용

2. **Structure Organization** (20-30분)
   - 장별 구조 생성
   - 목차 자동 생성
   - 페이지 번호 할당

3. **Quality Validation** (10-15분)
   - GRA 검증
   - pTCS 계산
   - 인용 형식 검사
   - 참고문헌 일치 확인

4. **Report Generation** (10분)
   - Markdown 생성
   - 검증 리포트 첨부
   - 수정 사항 리스트 출력

**Total Time**: 100-150분

---

## 다음 단계

```bash
# HITL 검토로 진행
/thesis:review-proposal --proposal-file final-research-proposal.md

# 품질 문제 수정 후 재검증
/thesis:integrate-proposal --revalidate
```

---

## 관련 커맨드

- `/thesis:assess-feasibility` - Stage 5 실행
- `/thesis:review-proposal` - HITL 검토 (Gate 1)
- `/thesis:status` - 진행 상태 확인

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**에이전트**: proposal-integrator (Opus)
