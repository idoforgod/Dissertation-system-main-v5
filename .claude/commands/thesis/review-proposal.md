---
name: review-proposal
description: HITL Checkpoint - 연구 제안서 검토. 사용자가 최종 제안서를 검토하고 승인/수정/거부 결정을 내립니다.
---

# /thesis:review-proposal

**HITL Gate 1**: 연구 제안서 검토 및 승인

Mode E의 최종 Human-in-the-Loop 체크포인트입니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:review-proposal --proposal-file final-research-proposal.md
```

### 고급 옵션

```bash
# 검증 리포트 포함
/thesis:review-proposal --proposal-file <파일> --show-validation true

# 비교 모드 (이전 버전과 비교)
/thesis:review-proposal --proposal-file <파일> --compare-with proposal-v1.md

# 출력 형식
/thesis:review-proposal --proposal-file <파일> --format "markdown,pdf"
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--proposal-file` | Yes | - | 최종 제안서 파일 경로 |
| `--show-validation` | No | `true` | 품질 검증 리포트 표시 여부 |
| `--compare-with` | No | - | 이전 버전 파일 경로 (변경사항 비교) |
| `--format` | No | `markdown` | 출력 형식: `markdown`, `pdf`, `docx` |
| `--checklist` | No | `true` | 검토 체크리스트 표시 |

---

## 검토 프로세스

### Step 1: 제안서 요약 표시

```
┌─────────────────────────────────────────────────────────────┐
│  📄 Research Proposal Review                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Title: The Moderating Role of Organizational Climate...    │
│  Pages: 52                                                   │
│  Hypotheses: 2 (H1: Direct, H2: Moderation)                 │
│  Research Type: Quantitative - Survey                        │
│  Sample Size: n=122 (350 surveys)                           │
│  Timeline: 20 months                                         │
│  Budget: $19,030                                             │
│                                                              │
│  Quality Metrics:                                            │
│  ├─ GRA Compliance: 98.5% ✅                                │
│  ├─ pTCS Average: 0.72 ✅                                   │
│  ├─ Citation Format: 3 errors ⚠️                            │
│  ├─ Reference Completeness: 2 missing ⚠️                    │
│  └─ Overall Quality: 4.1/5.0 ✅                             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 2: 검토 체크리스트 제공

사용자가 검토해야 할 핵심 사항:

```yaml
review_checklist:
  content_quality:
    - [ ] Research question is clear and significant
    - [ ] Hypotheses are well-justified
    - [ ] Literature review is comprehensive (50+ citations)
    - [ ] Methodology is rigorous and appropriate
    - [ ] Expected contributions are clearly stated

  technical_quality:
    - [ ] All claims are properly cited (GRA ≥95%)
    - [ ] Evidence quality is high (pTCS ≥0.6)
    - [ ] Citations follow APA 7th format
    - [ ] Reference list is complete
    - [ ] Statistical analysis plan is sound

  feasibility:
    - [ ] Sample size is achievable (power analysis based)
    - [ ] Timeline is realistic (20 months)
    - [ ] Budget is reasonable ($19,030)
    - [ ] IRB approval is likely
    - [ ] Resources are available

  alignment:
    - [ ] Addresses research gap identified in Stage 2
    - [ ] Builds on paper analyzed in Stage 1
    - [ ] Hypotheses match conceptual model
    - [ ] Methodology aligns with hypotheses
    - [ ] Timeline matches budget

  overall:
    - [ ] Proposal is ready for committee review
    - [ ] Proposal is ready for grant application
    - [ ] Proposal is ready for IRB submission
```

---

### Step 3: 품질 이슈 표시

자동 검증에서 발견된 문제점:

```
⚠️  Quality Issues Found (5 total)

Critical (0):
  [None]

High Priority (2):
  1. Citation Format Error (L123)
     Found: "(Bass 1985)"
     Fix: "(Bass, 1985)" [missing comma]

  2. Citation Format Error (L456)
     Found: "Smith and Johnson"
     Fix: "Smith & Johnson" [use ampersand in parenthetical]

Medium Priority (2):
  3. Missing Reference: Woodman et al. (1993)
     Cited in: L234, L567
     Action: Add to reference list

  4. Missing Reference: Schafer & Graham (2002)
     Cited in: L890
     Action: Add to reference list

Low Priority (1):
  5. Citation Format Error (L789)
     Found: Reference missing period
     Fix: Add period at end

Recommended Action:
  ✅ FIX - Address 5 issues before approval (estimated 10-15 minutes)
```

---

### Step 4: 사용자 결정 요청

```yaml
decision_options:
  - option: "APPROVE ✅"
    description: "Proposal is excellent. Proceed to next phase."
    next_action: "Exit Mode E, return to main workflow"
    condition: "All quality checks passed, user satisfied"

  - option: "APPROVE with Minor Edits ✏️"
    description: "Approve but fix quality issues first (auto-fix available)"
    next_action: "Auto-fix citations → Re-validate → Exit Mode E"
    condition: "Quality issues are minor (formatting only)"

  - option: "REVISE - Stage 6 Only 🔄"
    description: "Re-integrate proposal (Stage 6) with user feedback"
    next_action: "Re-run proposal-integrator with modifications"
    condition: "Integration issues (e.g., missing sections, organization)"

  - option: "REVISE - Stage 4-6 🔄🔄"
    description: "Revise research design (Stage 4) and re-integrate"
    next_action: "Re-run design-proposer → feasibility-assessor → proposal-integrator"
    condition: "Methodology issues (e.g., wrong design, inadequate sample)"

  - option: "REVISE - Stage 3-6 🔄🔄🔄"
    description: "Revise hypotheses (Stage 3) and downstream stages"
    next_action: "Re-run hypothesis-generator → design → feasibility → integration"
    condition: "Hypothesis issues (e.g., not testable, poor CTOSF scores)"

  - option: "REVISE - All Stages 🔄🔄🔄🔄"
    description: "Major revision needed, restart from Stage 1"
    next_action: "Re-run entire Mode E workflow"
    condition: "Fundamental issues (e.g., wrong paper, misidentified gaps)"

  - option: "REJECT ❌"
    description: "Proposal is not acceptable. Exit Mode E."
    next_action: "Exit Mode E without saving, return to main workflow"
    condition: "Proposal does not meet minimum standards"
```

---

## 자동 수정 기능

Minor quality issues can be auto-fixed:

```bash
# Auto-fix citation format errors
/thesis:review-proposal --proposal-file <파일> --auto-fix citations

# Auto-fix missing references
/thesis:review-proposal --proposal-file <파일> --auto-fix references

# Auto-fix all
/thesis:review-proposal --proposal-file <파일> --auto-fix all
```

**Auto-fixable issues**:
- Citation format errors (comma, ampersand, period)
- Missing references (auto-search and add from CrossRef/DOI)
- Spacing/formatting inconsistencies

**Not auto-fixable**:
- Logical errors (wrong hypotheses)
- Content gaps (missing sections)
- Methodological flaws

---

## 예시

### Example 1: Approval with Minor Edits

```bash
/thesis:review-proposal --proposal-file final-research-proposal.md
```

**Output**:
```
📄 Research Proposal Review
─────────────────────────────────────────────────────────────

Title: The Moderating Role of Organizational Climate in the
       Transformational Leadership-Innovation Relationship

Quality Metrics:
  ✅ GRA Compliance: 98.5% (threshold: 95%)
  ✅ pTCS Average: 0.72 (threshold: 0.6)
  ⚠️  Citation Format: 3 errors
  ⚠️  Reference Completeness: 2 missing
  ✅ Overall Quality: 4.1/5.0

⚠️  Quality Issues: 5 found (2 High, 2 Medium, 1 Low)

─────────────────────────────────────────────────────────────

Please review the proposal and select an option:

  1. ✅ APPROVE - Excellent, proceed to next phase
  2. ✏️  APPROVE with Minor Edits - Fix quality issues first
  3. 🔄 REVISE Stage 6 - Re-integrate with feedback
  4. 🔄🔄 REVISE Stages 4-6 - Revise methodology
  5. 🔄🔄🔄 REVISE Stages 3-6 - Revise hypotheses
  6. 🔄🔄🔄🔄 REVISE All Stages - Major revision
  7. ❌ REJECT - Not acceptable

Your choice: 2

─────────────────────────────────────────────────────────────

You selected: APPROVE with Minor Edits ✏️

Auto-fixing quality issues...
  ✅ Fixed citation format error (L123): (Bass, 1985)
  ✅ Fixed citation format error (L456): Smith & Johnson
  ✅ Added missing reference: Woodman et al. (1993)
  ✅ Added missing reference: Schafer & Graham (2002)
  ✅ Fixed citation format error (L789): Added period

Re-validating...
  ✅ GRA Compliance: 100% (was 98.5%)
  ✅ pTCS Average: 0.72 (unchanged)
  ✅ Citation Format: 0 errors (was 3)
  ✅ Reference Completeness: 0 missing (was 2)
  ✅ Overall Quality: 4.3/5.0 (was 4.1)

✅ All quality checks passed!

Saving final proposal:
  📄 final-research-proposal-approved.md (52 pages)
  📊 validation-report-final.json
  📋 review-checklist-completed.md

─────────────────────────────────────────────────────────────

🎉 Mode E Complete!

Next Steps:
  1. Review final proposal: final-research-proposal-approved.md
  2. Return to main workflow: /thesis:status
  3. Optional: Export to PDF/DOCX for committee review

Total Mode E Duration: 105 minutes (1 hour 45 minutes)
  Stage 1 (Paper Analysis): 15 min
  Stage 2 (Gap Identification): 10 min
  Stage 3 (Hypothesis Generation): 18 min
  Stage 4 (Research Design): 28 min
  Stage 5 (Feasibility Assessment): 8 min
  Stage 6 (Proposal Integration): 20 min
  HITL Review + Auto-fix: 6 min

Workflow saved to: thesis-output/mode-e-session-20260128.json
```

---

### Example 2: Revision Required (Stage 4-6)

```
Your choice: 4 (REVISE Stages 4-6)

─────────────────────────────────────────────────────────────

Please specify revision requirements:

What needs to change in the research design?
> Change from survey to experimental design. Need to test causality.

Additional notes (optional):
> Consider lab experiment with random assignment. Sample size will be smaller.

─────────────────────────────────────────────────────────────

Revision Plan:
  🔄 Stage 4: Re-run design-proposer
     Input: stage3-hypotheses.md (unchanged)
     Change: Research type = experimental
     Output: stage4-research-design-v2.md

  🔄 Stage 5: Re-run feasibility-assessor
     Input: stage4-research-design-v2.md
     Output: stage5-feasibility-assessment-v2.md

  🔄 Stage 6: Re-run proposal-integrator
     Input: All stages (Stage 4-5 revised)
     Output: final-research-proposal-v2.md

Estimated Time: 50-70 minutes

Proceed with revision? (y/n): y

─────────────────────────────────────────────────────────────

🔄 Starting Stage 4 Revision...
  Agent: design-proposer
  Mode: Experimental design
  [... progress ...]

[... continues until new proposal ready for review ...]
```

---

## 검토 후 액션

### If APPROVED:
```bash
# 1. Export to multiple formats
/thesis:export --input final-research-proposal-approved.md --format "pdf,docx"

# 2. Generate presentation slides
/thesis:create-slides --proposal final-research-proposal-approved.md

# 3. Return to main workflow
/thesis:status
```

### If REVISED:
```bash
# Re-review after revision
/thesis:review-proposal --proposal-file final-research-proposal-v2.md

# Compare versions
/thesis:review-proposal --proposal-file final-research-proposal-v2.md \
  --compare-with final-research-proposal-v1.md
```

---

## 변경사항 비교 (Compare Mode)

```bash
/thesis:review-proposal --proposal-file proposal-v2.md --compare-with proposal-v1.md
```

**Output**:
```diff
Changes from v1 to v2:

## 4. Research Methodology

### 4.1 Research Design

- This study employs a **cross-sectional survey design**
+ This study employs a **laboratory experimental design** with random assignment

### 4.2 Sampling Strategy

- **Target Population**: Full-time employees in technology companies
- **Sampling Method**: Stratified random sampling
- **Sample Size**: n=122
+ **Target Population**: Undergraduate students (proxy for employees)
+ **Sampling Method**: Random assignment to conditions
+ **Sample Size**: n=120 (60 per condition)

[... continues ...]

Summary of Changes:
  - Research design: Survey → Experiment
  - Sample: Employees → Students
  - Sample size: 122 → 120
  - Timeline: 20 months → 12 months
  - Budget: $19,030 → $8,500

Quality Impact:
  - Internal validity: Improved (causal inference)
  - External validity: Decreased (student sample)
  - Feasibility: Improved (faster, cheaper)
```

---

## 체크리스트 출력

```bash
/thesis:review-proposal --proposal-file <파일> --checklist-only
```

**Output**: `review-checklist-completed.md`

```markdown
# Research Proposal Review Checklist

**Proposal**: final-research-proposal.md
**Date**: 2026-01-28
**Reviewer**: [Your Name]

## Content Quality

- [x] Research question is clear and significant
- [x] Hypotheses are well-justified (CTOSF avg: 4.4/5.0)
- [x] Literature review is comprehensive (58 citations)
- [x] Methodology is rigorous and appropriate
- [x] Expected contributions are clearly stated

## Technical Quality

- [x] All claims are properly cited (GRA: 100%)
- [x] Evidence quality is high (pTCS: 0.72)
- [x] Citations follow APA 7th format (0 errors)
- [x] Reference list is complete (0 missing)
- [x] Statistical analysis plan is sound

## Feasibility

- [x] Sample size is achievable (n=122, power=0.80)
- [x] Timeline is realistic (20 months with buffer)
- [x] Budget is reasonable ($19,030)
- [x] IRB approval is likely (minimal risk)
- [x] Resources are available

## Alignment

- [x] Addresses research gap (boundary conditions)
- [x] Builds on Smith & Johnson (2023) paper
- [x] Hypotheses match conceptual model
- [x] Methodology aligns with hypotheses
- [x] Timeline matches budget

## Overall Assessment

- [x] Proposal is ready for committee review
- [x] Proposal is ready for grant application
- [x] Proposal is ready for IRB submission

**Decision**: ✅ APPROVED with Minor Edits
**Quality Score**: 4.3/5.0
**Recommendation**: Excellent proposal. Proceed to next phase.

**Signature**: ___________________
**Date**: 2026-01-28
```

---

## 관련 커맨드

- `/thesis:integrate-proposal` - Stage 6 실행
- `/thesis:export` - PDF/DOCX 변환
- `/thesis:status` - 전체 워크플로우 상태
- `/thesis:start` - 새로운 연구 시작

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**Human-in-the-Loop Checkpoint**: Gate 1 (Mode E 완료)
