# Mode E (논문 기반 연구 설계) 최적화 설계

**작성일**: 2026-01-28
**목적**: paper-research-designer agent를 Master-Subagent 아키텍처로 리팩토링하여 효율성과 유지보수성을 향상

---

## 1. 현재 구조 분석

### 1.1 Current Architecture (AS-IS)

```yaml
current_structure:
  agents:
    - name: paper-research-designer
      type: monolithic
      model: opus
      stages: 6
      duration: 60-90분
      complexity: HIGH

  commands:
    - name: start-paper-upload
      agent: paper-research-designer

  subagents: 0
  skills: 0 (scientific-skills 의존)
  hooks: 0
```

**문제점**:
- ❌ 하나의 거대한 agent가 모든 책임 (Single Responsibility Principle 위반)
- ❌ Stage별 독립 실행 불가 (예: Gap 분석만 재실행)
- ❌ 오류 발생 시 전체 재시작 필요
- ❌ 병렬 실행 불가능 (일부 stage는 병렬 가능)
- ❌ 재사용성 낮음 (다른 모드에서 stage 활용 불가)

---

## 2. 최적화 설계 (TO-BE)

### 2.1 Target Architecture

```yaml
optimized_structure:
  master_agent: 1
    - name: paper-research-orchestrator
      role: Workflow coordination & stage delegation
      model: sonnet (lightweight)

  subagents: 6
    - paper-analyzer (Stage 1)
    - gap-identifier (Stage 2)
    - hypothesis-generator (Stage 3)
    - design-proposer (Stage 4)
    - feasibility-assessor (Stage 5)
    - proposal-integrator (Stage 6)

  skills: 4
    - paper-analysis (논문 분석 공통 로직)
    - hypothesis-development (가설 생성 로직)
    - research-design-templates (연구 설계 템플릿)
    - validation-checks (품질 검증)

  commands: 8
    - start-paper-upload (전체 워크플로우)
    - analyze-paper (Stage 1만)
    - identify-gaps (Stage 2만)
    - generate-hypotheses (Stage 3만)
    - propose-design (Stage 4만)
    - assess-feasibility (Stage 5만)
    - integrate-proposal (Stage 6만)
    - review-proposal (HITL-1)

  hooks: 3
    - pre-stage (Stage 시작 전 검증)
    - post-stage (Stage 완료 후 검증)
    - hitl-checkpoint (사용자 승인 대기)
```

---

## 3. 세부 설계

### 3.1 Master Agent: paper-research-orchestrator

**파일**: `.claude/agents/thesis/phase0/paper-research-orchestrator.md`

```yaml
name: paper-research-orchestrator
description: 논문 기반 연구 설계 워크플로우 총괄 오케스트레이터
tools: Task(*), Read(*), Write(*), Bash(*)
model: sonnet
```

**책임 (Responsibilities)**:
1. 워크플로우 순서 제어 (Stage 1 → 2 → 3 → 4 → 5 → 6)
2. Subagent 호출 및 결과 수집
3. Stage 간 데이터 전달 (Stage N 출력 → Stage N+1 입력)
4. 오류 처리 및 재시도 로직
5. HITL 체크포인트 관리
6. 진행 상황 로깅

**Pseudocode**:
```python
def orchestrate_paper_research(paper_path):
    # Initialize session
    session = init_session(mode="paper-upload", paper_path=paper_path)

    # Stage 1: Deep Analysis
    analysis = Task(subagent="paper-analyzer", input=paper_path)
    if not validate_output(analysis):
        retry_or_fail()

    # Stage 2: Gap Identification
    gaps = Task(subagent="gap-identifier", input=analysis)

    # Stage 3: Hypothesis Generation
    hypotheses = Task(subagent="hypothesis-generator", input=gaps)

    # Stage 4: Design Proposal
    design = Task(subagent="design-proposer", input=hypotheses)

    # Stage 5: Feasibility Assessment
    feasibility = Task(subagent="feasibility-assessor", input=design)

    # Stage 6: Integration
    proposal = Task(subagent="proposal-integrator", inputs=[
        analysis, gaps, hypotheses, design, feasibility
    ])

    # HITL-1 Checkpoint
    user_approval = hitl_checkpoint(proposal)

    # Proceed to Phase 1 if approved
    if user_approval:
        trigger_phase_1(hypotheses=user_selected_hypotheses)
```

---

### 3.2 Subagents (6개)

#### Subagent 1: paper-analyzer

**파일**: `.claude/agents/thesis/phase0/subagents/paper-analyzer.md`

```yaml
name: paper-analyzer
description: 선행연구 논문 심층 분석 전문가 (Stage 1)
tools: Read(*), Write(*), WebSearch(*), Skill(scientific-skills:peer-review)
model: opus
```

**입력**:
- `paper_path`: 업로드된 논문 경로

**출력**:
- `paper-deep-analysis.md` (5-7 pages)

**분석 프레임워크**:
```yaml
analysis_framework:
  1_research_context:
    - research_question
    - theoretical_framework
    - research_paradigm

  2_methodology_evaluation:
    - research_design
    - sample_characteristics
    - data_collection
    - analysis_techniques
    - validity_assessment

  3_findings_synthesis:
    - main_findings
    - effect_sizes
    - statistical_significance
    - practical_significance

  4_critical_evaluation:
    - theoretical_contribution
    - methodological_strengths
    - methodological_weaknesses
    - author_acknowledged_limitations
    - unacknowledged_limitations
```

**Skills 활용**:
- `scientific-skills:peer-review` - 체계적 논문 평가
- `scientific-skills:scientific-critical-thinking` - 비판적 사고

---

#### Subagent 2: gap-identifier

**파일**: `.claude/agents/thesis/phase0/subagents/gap-identifier.md`

```yaml
name: gap-identifier
description: 전략적 연구 갭 식별 전문가 (Stage 2)
tools: Read(*), Write(*), WebSearch(*), Skill(hypothesis-generation)
model: opus
```

**입력**:
- `paper-deep-analysis.md` (Stage 1 출력)

**출력**:
- `strategic-gap-analysis.md` (3-5 gaps)

**갭 유형**:
```yaml
gap_types:
  theoretical_gaps:
    questions:
      - "기존 이론이 설명하지 못하는 현상은?"
      - "서로 상충하는 이론적 예측은?"

  methodological_gaps:
    questions:
      - "더 엄밀한 연구 설계로 재검증 가능한가?"
      - "다른 측정 도구 적용 시 다른 결과?"

  contextual_gaps:
    questions:
      - "다른 국가/문화/산업에서의 재현성은?"

  practical_gaps:
    questions:
      - "실무 적용 가능한 구체적 방안은?"

  integration_gaps:
    questions:
      - "다른 이론/분야와 통합 가능한가?"
```

---

#### Subagent 3: hypothesis-generator

**파일**: `.claude/agents/thesis/phase0/subagents/hypothesis-generator.md`

```yaml
name: hypothesis-generator
description: 새로운 연구 가설 도출 전문가 (Stage 3)
tools: Read(*), Write(*), Skill(hypothesis-development)
model: opus
```

**입력**:
- `strategic-gap-analysis.md` (Stage 2 출력)

**출력**:
- `novel-hypotheses.md` (6-15 hypotheses)

**가설 구조**:
```yaml
hypothesis_structure:
  hypothesis_id: "H1"
  hypothesis_statement:
    english: "Clear, testable hypothesis"
    korean: "명확하고 검증 가능한 가설"

  theoretical_rationale:
    - reason_1
    - reason_2

  originality_claim:
    what_is_new: "기존 연구와 차별점"
    why_important: "학술적/실무적 중요성"

  testability:
    variables:
      independent: "IV"
      dependent: "DV"
      moderators: []
      mediators: []
      controls: []

    operationalization: [...]

  feasibility_assessment:
    data_availability: 4/5
    ethical_considerations: "IRB 필요"
    resource_requirements: "중간"
```

**품질 기준**:
- ✅ 명확성 (Clarity)
- ✅ 검증가능성 (Testability)
- ✅ 독창성 (Originality)
- ✅ 중요성 (Significance)
- ✅ 실행가능성 (Feasibility)

---

#### Subagent 4: design-proposer

**파일**: `.claude/agents/thesis/phase0/subagents/design-proposer.md`

```yaml
name: design-proposer
description: 상세 연구 설계 제안 전문가 (Stage 4)
tools: Read(*), Write(*), Skill(research-design-templates)
model: opus
```

**입력**:
- `novel-hypotheses.md` (Stage 3 출력)

**출력**:
- `research-design-proposal.md` (20-30 pages)

**설계 유형**:
```yaml
design_types:
  quantitative:
    - experimental
    - quasi-experimental
    - survey
    - secondary_data_analysis

  qualitative:
    - phenomenology
    - grounded_theory
    - case_study
    - ethnography

  mixed_methods:
    - convergent
    - explanatory_sequential
    - exploratory_sequential
    - embedded
```

**Skills 활용**:
- `research-design-templates:quantitative` - 양적연구 템플릿
- `research-design-templates:qualitative` - 질적연구 템플릿
- `research-design-templates:mixed` - 혼합연구 템플릿

---

#### Subagent 5: feasibility-assessor

**파일**: `.claude/agents/thesis/phase0/subagents/feasibility-assessor.md`

```yaml
name: feasibility-assessor
description: 실행가능성 및 윤리 평가 전문가 (Stage 5)
tools: Read(*), Write(*), Bash(*)
model: sonnet
```

**입력**:
- `research-design-proposal.md` (Stage 4 출력)

**출력**:
- `feasibility-ethics-report.md`

**평가 영역**:
```yaml
assessment_areas:
  resource_requirements:
    financial: "예산 추정"
    human_resources: "필요 인력"
    time_requirements: "소요 시간"

  ethical_considerations:
    irb_requirements: "IRB 승인 필요 여부"
    informed_consent: "동의서 설계"
    confidentiality: "익명성 보장 방안"
    potential_risks: "잠재적 위험 및 완화 방안"

  data_management_plan:
    storage: "저장 방법"
    retention_period: "보관 기간"
    disposal_method: "폐기 방법"
```

---

#### Subagent 6: proposal-integrator

**파일**: `.claude/agents/thesis/phase0/subagents/proposal-integrator.md`

```yaml
name: proposal-integrator
description: 통합 연구 제안서 생성 전문가 (Stage 6)
tools: Read(*), Write(*), Skill(validation-checks)
model: opus
```

**입력**:
- `paper-deep-analysis.md` (Stage 1)
- `strategic-gap-analysis.md` (Stage 2)
- `novel-hypotheses.md` (Stage 3)
- `research-design-proposal.md` (Stage 4)
- `feasibility-ethics-report.md` (Stage 5)

**출력**:
- `integrated-research-proposal.md` (40-60 pages)
- `integrated-research-proposal.docx` (Word export)

**통합 구조**:
```markdown
# Novel Research Proposal Based on [Original Paper Title]

## Executive Summary (1 page)
- Original paper summary
- Identified gaps
- Proposed hypotheses (top 3-5)
- Recommended research design

## Part 1: Original Paper Analysis (5-7 pages)
[Stage 1 content]

## Part 2: Strategic Gap Analysis (3-5 pages)
[Stage 2 content]

## Part 3: Novel Hypotheses (8-12 pages)
[Stage 3 content]

## Part 4: Research Design Proposal (20-30 pages)
[Stage 4 content]

## Part 5: Feasibility & Ethics (5-8 pages)
[Stage 5 content]

## Part 6: Expected Contributions (2-3 pages)
- Theoretical contributions
- Methodological contributions
- Practical implications

## References (APA 7th)
- Original paper + 30-50 additional references
```

**Skills 활용**:
- `validation-checks:gra-compliance` - GRA 준수 검증
- `validation-checks:hallucination-firewall` - 환각 방지 검증
- `validation-checks:ptcs-score` - 신뢰도 점수 계산

---

### 3.3 Skills (4개)

#### Skill 1: paper-analysis

**파일**: `.claude/skills/paper-analysis/SKILL.md`

```yaml
name: paper-analysis
description: 학술 논문 분석을 위한 공통 로직 및 도구
tools: Read(*), WebSearch(*), Bash(*)
```

**기능**:
- PDF 파싱 (텍스트 추출)
- 섹션 자동 인식 (Abstract, Introduction, Methods, Results, Discussion)
- 인용 추출 (References 섹션)
- 표/그림 메타데이터 추출
- 언어 감지 및 자동 번역 (한국어 ↔ 영어)

**스크립트**:
```python
# .claude/skills/paper-analysis/scripts/parse_pdf.py
def parse_pdf(pdf_path):
    """PDF 논문을 구조화된 JSON으로 변환"""
    return {
        "title": str,
        "authors": List[str],
        "abstract": str,
        "sections": Dict[str, str],
        "references": List[str],
        "figures": List[str],
        "tables": List[str]
    }
```

---

#### Skill 2: hypothesis-development

**파일**: `.claude/skills/hypothesis-development/SKILL.md`

```yaml
name: hypothesis-development
description: 연구 가설 개발을 위한 체계적 프레임워크
tools: Read(*), Write(*), WebSearch(*)
```

**기능**:
- 가설 템플릿 제공 (인과관계, 상관관계, 조절/매개 효과)
- 가설 품질 자동 평가 (5개 기준)
- 이론적 근거 자동 검색 (WebSearch)
- 변수 조작적 정의 가이드

**템플릿**:
```yaml
hypothesis_templates:
  causal:
    template: "[IV] increases/decreases [DV]"
    example: "Transformational leadership increases employee creativity"

  moderation:
    template: "[Moderator] moderates the relationship between [IV] and [DV]"
    example: "Psychological safety moderates the relationship between leadership and creativity"

  mediation:
    template: "[Mediator] mediates the relationship between [IV] and [DV]"
    example: "Trust mediates the relationship between leadership and performance"
```

---

#### Skill 3: research-design-templates

**파일**: `.claude/skills/research-design-templates/SKILL.md`

```yaml
name: research-design-templates
description: 양적/질적/혼합연구 설계 템플릿
tools: Read(*), Write(*)
```

**템플릿 종류**:
- `quantitative_experimental.yaml` - 실험연구 설계
- `quantitative_survey.yaml` - 조사연구 설계
- `qualitative_case_study.yaml` - 사례연구 설계
- `qualitative_grounded_theory.yaml` - 근거이론 설계
- `mixed_convergent.yaml` - 수렴 혼합연구 설계

**예시 (조사연구)**:
```yaml
quantitative_survey_template:
  research_type: "Cross-sectional Survey"

  sampling_strategy:
    population: "[Define target population]"
    sampling_method: "Random | Convenience | Stratified"
    sample_size_calculation:
      expected_effect_size: 0.3
      alpha_level: 0.05
      power: 0.80
      calculated_n: 82

  measurement_instruments:
    - variable: "[Variable name]"
      scale: "[Scale name & citation]"
      items: "[Number of items]"
      reliability: "Cronbach's α = 0.XX"

  data_collection_procedure:
    - step: 1
      action: "[Action description]"
      timeline: "[Week X-Y]"

  statistical_analysis_plan:
    preliminary_analysis:
      - "Descriptive statistics"
      - "Normality tests"
    main_analysis:
      - hypothesis: "H1"
        technique: "Multiple Regression"
```

---

#### Skill 4: validation-checks

**파일**: `.claude/skills/validation-checks/SKILL.md`

```yaml
name: validation-checks
description: 출력물 품질 검증 자동화
tools: Read(*), Bash(*)
```

**검증 항목**:
```yaml
validation_checks:
  gra_compliance:
    description: "GroundedClaim 스키마 준수 검증"
    checks:
      - "모든 주장에 인용 있는가?"
      - "페이지 번호 포함되었는가?"
      - "문헌 목록에 모든 인용 포함되었는가?"

  hallucination_firewall:
    description: "환각 방지 패턴 검증"
    blocked_patterns:
      - "완벽하다"
      - "모든 연구자가 동의"
      - "100% 확실"
    required_patterns:
      - "연구에 따르면 (Citation)"
      - "효과 크기 (r=XX, p<.YY)"

  ptcs_score:
    description: "pTCS 신뢰도 점수 계산"
    thresholds:
      claim_level: 70
      agent_level: 75
```

**스크립트**:
```python
# .claude/skills/validation-checks/scripts/check_gra.py
def check_gra_compliance(md_file):
    """GRA 준수 여부 자동 검증"""
    violations = []

    # Check: 모든 주장에 인용 있는가?
    claims = extract_claims(md_file)
    for claim in claims:
        if not has_citation(claim):
            violations.append(f"No citation: {claim}")

    return {
        "is_compliant": len(violations) == 0,
        "violations": violations,
        "score": calculate_compliance_score(violations)
    }
```

---

### 3.4 Commands (8개)

#### Command 1: start-paper-upload (전체 워크플로우)

**파일**: `.claude/commands/thesis/start-paper-upload.md`

```yaml
description: 선행연구 논문 기반 연구 설계 전체 워크플로우 실행
allowed-tools: Task(paper-research-orchestrator)
agent: paper-research-orchestrator
```

**실행 흐름**:
```
start-paper-upload
  ↓
@paper-research-orchestrator
  ↓
├─ @paper-analyzer (Stage 1) [10-15분]
├─ @gap-identifier (Stage 2) [8-12분]
├─ @hypothesis-generator (Stage 3) [15-20분]
├─ @design-proposer (Stage 4) [20-30분]
├─ @feasibility-assessor (Stage 5) [5-8분]
└─ @proposal-integrator (Stage 6) [5-10분]
  ↓
HITL-1 체크포인트
```

---

#### Command 2-7: 개별 Stage 실행

각 stage를 독립적으로 실행할 수 있는 커맨드:

```yaml
commands:
  - name: analyze-paper
    description: "Stage 1만 실행 (논문 심층 분석)"
    agent: paper-analyzer

  - name: identify-gaps
    description: "Stage 2만 실행 (연구 갭 식별)"
    agent: gap-identifier

  - name: generate-hypotheses
    description: "Stage 3만 실행 (가설 도출)"
    agent: hypothesis-generator

  - name: propose-design
    description: "Stage 4만 실행 (연구 설계)"
    agent: design-proposer

  - name: assess-feasibility
    description: "Stage 5만 실행 (실행가능성 평가)"
    agent: feasibility-assessor

  - name: integrate-proposal
    description: "Stage 6만 실행 (통합 제안서)"
    agent: proposal-integrator
```

**사용 사례**:
```bash
# Gap 분석만 재실행
/thesis:identify-gaps --input paper-deep-analysis.md

# 가설만 재생성 (다른 접근 시도)
/thesis:generate-hypotheses --input strategic-gap-analysis.md --approach alternative
```

---

#### Command 8: review-proposal (HITL-1)

**파일**: `.claude/commands/thesis/review-proposal.md`

```yaml
description: 통합 연구 제안서 검토 및 승인 (HITL-1)
allowed-tools: Read(*), AskUserQuestion(*)
```

**검토 항목**:
```yaml
review_checklist:
  1_paper_analysis:
    question: "원본 논문 분석이 정확한가?"
    options: ["승인", "수정 필요", "재분석 요청"]

  2_gaps_identified:
    question: "식별된 갭이 타당한가?"
    options: ["승인", "갭 추가 요청", "갭 제거 요청"]

  3_hypotheses:
    question: "제안된 가설 중 몇 개를 선택하시겠습니까?"
    options: ["Top 3 추천", "수동 선택 (1-3개)", "가설 수정 요청"]

  4_research_design:
    question: "연구 설계 유형을 선택하세요"
    options: ["양적", "질적", "혼합", "문헌검토 후 결정"]

  5_next_step:
    question: "다음 단계를 선택하세요"
    options: ["승인 - Phase 1 진행", "수정 요청", "다른 논문 분석"]
```

---

### 3.5 Hooks (3개)

#### Hook 1: pre-stage

**파일**: `.claude/hooks/thesis/pre-stage.sh`

```bash
#!/bin/bash
# Stage 시작 전 자동 검증

STAGE=$1
INPUT_FILE=$2

echo "[pre-stage] Stage $STAGE 시작 전 검증..."

# 입력 파일 존재 확인
if [ ! -f "$INPUT_FILE" ]; then
    echo "❌ 입력 파일 없음: $INPUT_FILE"
    exit 1
fi

# 입력 파일 최소 크기 확인 (빈 파일 방지)
FILE_SIZE=$(wc -c < "$INPUT_FILE")
if [ "$FILE_SIZE" -lt 100 ]; then
    echo "⚠️  입력 파일이 너무 작음 (< 100 bytes)"
    exit 1
fi

echo "✅ 입력 검증 통과"
```

**등록**:
```json
{
  "hooks": {
    "tool-use:Task": {
      "pre": [
        {
          "command": ".claude/hooks/thesis/pre-stage.sh $SUBAGENT_NAME $INPUT_FILE",
          "block_on_error": true
        }
      ]
    }
  }
}
```

---

#### Hook 2: post-stage

**파일**: `.claude/hooks/thesis/post-stage.sh`

```bash
#!/bin/bash
# Stage 완료 후 자동 검증

STAGE=$1
OUTPUT_FILE=$2

echo "[post-stage] Stage $STAGE 완료 후 검증..."

# 출력 파일 존재 확인
if [ ! -f "$OUTPUT_FILE" ]; then
    echo "❌ 출력 파일 생성되지 않음: $OUTPUT_FILE"
    exit 1
fi

# GRA Compliance 검증
python3 .claude/skills/validation-checks/scripts/check_gra.py "$OUTPUT_FILE"
if [ $? -ne 0 ]; then
    echo "⚠️  GRA 준수 위반 발견"
    exit 1
fi

# pTCS 점수 계산
PTCS_SCORE=$(python3 .claude/skills/validation-checks/scripts/calculate_ptcs.py "$OUTPUT_FILE")
echo "📊 pTCS Score: $PTCS_SCORE"

if [ "$PTCS_SCORE" -lt 70 ]; then
    echo "⚠️  pTCS 점수가 기준(70) 미만"
    exit 1
fi

echo "✅ 출력 검증 통과"
```

---

#### Hook 3: hitl-checkpoint

**파일**: `.claude/hooks/thesis/hitl-checkpoint.sh`

```bash
#!/bin/bash
# HITL 체크포인트 알림

CHECKPOINT=$1
OUTPUT_DIR=$2

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  🚦 HITL Checkpoint: $CHECKPOINT                         ║"
echo "╠═══════════════════════════════════════════════════════════╣"
echo "║                                                           ║"
echo "║  📁 검토 파일: $OUTPUT_DIR                               ║"
echo "║                                                           ║"
echo "║  다음 중 하나를 선택하세요:                              ║"
echo "║  1. /thesis:review-proposal  (제안서 검토 및 승인)       ║"
echo "║  2. /thesis:revise-stage     (특정 Stage 재실행)         ║"
echo "║  3. /thesis:abort            (워크플로우 중단)            ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# 사용자 입력 대기 (blocking)
# 이 hook은 사용자가 명시적으로 승인할 때까지 대기
```

---

## 4. 구현 계획

### 4.1 Phase 1: Subagents 생성 (1일)

```bash
# 6개 subagent 파일 생성
.claude/agents/thesis/phase0/subagents/
├── paper-analyzer.md
├── gap-identifier.md
├── hypothesis-generator.md
├── design-proposer.md
├── feasibility-assessor.md
└── proposal-integrator.md
```

**각 subagent 구조**:
```yaml
---
name: [subagent-name]
description: [1줄 설명]
tools: Read(*), Write(*), WebSearch(*), Skill(*)
model: opus | sonnet
---

# [Subagent Name]

## 역할 및 책임
...

## 입력
...

## 출력
...

## 실행 프로세스
...

## 품질 기준
...
```

---

### 4.2 Phase 2: Skills 추출 (1일)

```bash
# 4개 skill 디렉토리 생성
.claude/skills/
├── paper-analysis/
│   ├── SKILL.md
│   ├── scripts/
│   │   └── parse_pdf.py
│   └── templates/
│       └── analysis-template.yaml
├── hypothesis-development/
│   ├── SKILL.md
│   └── templates/
│       ├── causal-hypothesis.yaml
│       ├── moderation-hypothesis.yaml
│       └── mediation-hypothesis.yaml
├── research-design-templates/
│   ├── SKILL.md
│   └── templates/
│       ├── quantitative_experimental.yaml
│       ├── quantitative_survey.yaml
│       ├── qualitative_case_study.yaml
│       └── mixed_convergent.yaml
└── validation-checks/
    ├── SKILL.md
    └── scripts/
        ├── check_gra.py
        ├── check_hallucination.py
        └── calculate_ptcs.py
```

---

### 4.3 Phase 3: Master Orchestrator 생성 (1일)

```bash
# Master agent 생성
.claude/agents/thesis/phase0/paper-research-orchestrator.md
```

**핵심 로직**:
```python
def orchestrate():
    # 1. Session 초기화
    session = init_session()

    # 2. Stage 1-6 순차 실행
    results = {}
    for stage in STAGES:
        try:
            result = execute_stage(stage, results)
            results[stage] = result

            # Post-stage validation
            validate_output(result)

        except StageError as e:
            handle_error(stage, e)

    # 3. HITL Checkpoint
    hitl_checkpoint(results)

    # 4. User approval
    approval = wait_for_approval()

    # 5. Proceed to Phase 1
    if approval:
        trigger_phase_1(approval.selected_hypotheses)
```

---

### 4.4 Phase 4: Commands 업데이트 (0.5일)

```bash
# 8개 command 생성/업데이트
.claude/commands/thesis/
├── start-paper-upload.md (업데이트)
├── analyze-paper.md (신규)
├── identify-gaps.md (신규)
├── generate-hypotheses.md (신규)
├── propose-design.md (신규)
├── assess-feasibility.md (신규)
├── integrate-proposal.md (신규)
└── review-proposal.md (신규)
```

---

### 4.5 Phase 5: Hooks 설정 (0.5일)

```bash
# 3개 hook 스크립트 생성
.claude/hooks/thesis/
├── pre-stage.sh
├── post-stage.sh
└── hitl-checkpoint.sh

# .claude.json 업데이트
{
  "hooks": {
    "tool-use:Task": {
      "pre": [".claude/hooks/thesis/pre-stage.sh"],
      "post": [".claude/hooks/thesis/post-stage.sh"]
    },
    "hitl": [".claude/hooks/thesis/hitl-checkpoint.sh"]
  }
}
```

---

### 4.6 Phase 6: 테스트 및 검증 (1일)

```bash
# 샘플 논문으로 전체 워크플로우 테스트
/thesis:start paper-upload --paper-path test/sample-paper.pdf

# 개별 Stage 테스트
/thesis:analyze-paper --input test/sample-paper.pdf
/thesis:identify-gaps --input test/analysis-output.md

# Hook 동작 확인
# - pre-stage: 입력 검증
# - post-stage: GRA, pTCS 검증
# - hitl-checkpoint: 사용자 대기
```

---

## 5. 예상 효과

### 5.1 성능 향상

```yaml
performance_improvements:
  parallel_execution:
    before: "Stage 1 → 2 → 3 → 4 → 5 → 6 (순차)"
    after: "일부 stage 병렬 실행 가능 (예: Stage 4A, 4B, 4C 동시)"
    time_saved: "20-30%"

  retry_efficiency:
    before: "오류 시 전체 재시작 (60-90분)"
    after: "특정 stage만 재실행 (5-30분)"

  model_optimization:
    before: "모든 stage에 opus 사용"
    after: "orchestrator = sonnet, 복잡한 stage만 opus"
    cost_saved: "30-40%"
```

---

### 5.2 유지보수성

```yaml
maintainability_improvements:
  separation_of_concerns:
    - "각 subagent는 단일 책임만 가짐"
    - "Stage 로직 변경 시 해당 subagent만 수정"

  reusability:
    - "gap-identifier는 다른 모드에서도 활용 가능"
    - "hypothesis-generator는 Mode A, B, C에서도 사용"

  testability:
    - "각 subagent를 독립적으로 테스트 가능"
    - "Mock 입력으로 단위 테스트 용이"
```

---

### 5.3 사용자 경험

```yaml
ux_improvements:
  flexibility:
    - "전체 워크플로우 또는 개별 stage 실행 선택 가능"
    - "특정 stage만 수정하고 재실행"

  transparency:
    - "각 stage 진행 상황 실시간 확인"
    - "Hook으로 자동 검증 결과 즉시 피드백"

  control:
    - "HITL checkpoint에서 세밀한 제어"
    - "Stage별 결과물 개별 검토 가능"
```

---

## 6. 마이그레이션 가이드

### 6.1 기존 사용자를 위한 호환성

```yaml
backward_compatibility:
  old_command:
    command: "/thesis:start paper-upload --paper-path paper.pdf"
    behavior: "기존과 동일하게 전체 워크플로우 실행"
    internal: "내부적으로 @paper-research-orchestrator 호출"

  new_features:
    - "개별 stage 실행 가능 (선택 사항)"
    - "자동 검증 hook 활성화 (선택 사항)"
    - "병렬 실행 (자동 최적화)"
```

---

### 6.2 기존 출력물 호환성

```yaml
output_compatibility:
  file_structure:
    old: "thesis-output/.../00-paper-based-design/*.md"
    new: "동일 (변경 없음)"

  file_names:
    old: "paper-deep-analysis.md, strategic-gap-analysis.md, ..."
    new: "동일 (변경 없음)"

  file_format:
    old: "Markdown + YAML frontmatter"
    new: "동일 (변경 없음)"
```

---

## 7. 구현 우선순위

### High Priority (즉시 구현)
1. ✅ Master Orchestrator 생성
2. ✅ 6개 Subagents 생성
3. ✅ `start-paper-upload` 커맨드 업데이트

### Medium Priority (1주 내)
4. ⬜ 4개 Skills 추출 및 생성
5. ⬜ 개별 Stage 커맨드 생성 (7개)
6. ⬜ 기본 Hooks 설정 (pre/post-stage)

### Low Priority (2주 내)
7. ⬜ 고급 기능 (병렬 실행, 재시도 로직)
8. ⬜ 성능 최적화 (모델 선택, 캐싱)
9. ⬜ 종합 테스트 및 문서화

---

## 8. 다음 단계

### 즉시 시작
```bash
# 1. Master orchestrator 생성
claude code edit .claude/agents/thesis/phase0/paper-research-orchestrator.md

# 2. 첫 번째 subagent 생성
claude code edit .claude/agents/thesis/phase0/subagents/paper-analyzer.md

# 3. 커맨드 업데이트
claude code edit .claude/commands/thesis/start-paper-upload.md
```

---

## 9. 질문 및 검토사항

### 검토 필요
1. **병렬 실행**: Stage 4 (양적/질적/혼합 설계)를 병렬 실행할까요?
2. **모델 선택**: 모든 subagent에 opus를 사용할까요, 아니면 일부는 sonnet?
3. **Skill 의존성**: scientific-skills를 계속 사용할까요, 아니면 독립적으로?

### 사용자 피드백 필요
- 개별 stage 실행 기능이 유용할까요?
- Hook 자동 검증이 너무 엄격하지 않을까요?
- 다른 필요한 기능이 있을까요?

---

**작성자**: Claude Code (paper-research-orchestrator 설계)
**검토자**: [사용자 이름]
**승인 상태**: ⬜ 검토 대기 | ⬜ 수정 필요 | ⬜ 승인 완료
