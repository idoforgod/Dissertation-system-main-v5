# Mode E: Paper-Based Research Design Workflow

선행연구 논문을 업로드하여 박사급 연구 설계를 제안받는 워크플로우입니다.

## 개요

- **핵심 철학**: 단순한 논문 요약자가 아닌, **박사급 연구 보조 AI system**
- **입력**: 선행연구 논문 파일 (PDF, DOCX, TXT)
- **출력**: 통합 연구 제안서 (40-60 pages)
  - 논문 심층 분석
  - 전략적 갭 식별
  - 새로운 가설 도출 (6-15개)
  - 상세한 연구 설계 제안
  - 실행가능성 및 윤리 평가
- **소요 시간**: 60-90분
- **Agent**: @paper-research-designer (Opus)

---

## Workflow Stages

### Stage 0: Initialization

```bash
# 세션 초기화
/thesis:init

# 사용자 선택
[입력 모드]
● Mode E: 선행연구 논문 업로드 (NEW)

[논문 파일 업로드]
> user-resource/uploaded-papers/[논문파일].pdf
```

**Output**:
```
thesis-output/[논문제목-2026-01-28]/
├── 00-session/
│   ├── session.json (mode: paper-upload)
│   └── todo-checklist.md
└── 00-paper-based-design/
    └── uploaded-paper.pdf
```

---

### Stage 1: Deep Paper Analysis (10-15분)

**Agent**: @paper-research-designer

**Analysis Framework**:
1. **Research Context**
   - 핵심 연구질문
   - 이론적 프레임워크
   - 연구 패러다임

2. **Methodology Evaluation**
   - 연구 설계 유형
   - 표본 특성
   - 자료수집 방법
   - 분석 기법
   - 타당도 평가

3. **Findings Synthesis**
   - 핵심 발견사항
   - 효과 크기
   - 통계적 유의성

4. **Critical Evaluation**
   - 이론적 기여도
   - 방법론적 강점/약점
   - 명시된/미명시된 한계점

**Scientific Skills 사용**:
- `scientific-skills:peer-review`
- `scientific-skills:scientific-critical-thinking`
- `scientific-skills:literature-review`

**Output**: `paper-deep-analysis.md` (5-7 pages)

---

### Stage 2: Strategic Gap Identification (8-12분)

**Gap Types**:

1. **Theoretical Gaps (이론적 갭)**
   - 기존 이론이 설명하지 못하는 현상
   - 상충하는 이론적 예측
   - 새로운 맥락에서 이론 검증 필요

2. **Methodological Gaps (방법론적 갭)**
   - 더 엄밀한 연구 설계 필요
   - 다른 측정 도구/분석 기법 적용
   - 질적/양적 연구 보완

3. **Contextual Gaps (맥락적 갭)**
   - 다른 국가/문화/산업에서 검증
   - 다른 시간대/시기 확인
   - 다른 조직 유형/규모 적용

4. **Practical Gaps (실무적 갭)**
   - 실무 적용 가능한 방안
   - 정책/전략 수립 근거
   - 실무자 필요 지식

5. **Integration Gaps (통합적 갭)**
   - 다른 이론/분야 통합
   - 학제간 연구 기회
   - 혼합연구 방법론 적용

**Scientific Skills 사용**:
- `scientific-skills:hypothesis-generation`
- `scientific-skills:research-lookup`
- `scientific-skills:scientific-brainstorming`

**Output**: `strategic-gap-analysis.md` (3-5 gaps with detailed justification)

---

### Stage 3: Novel Hypothesis Generation (15-20분)

**각 갭당 2-3개의 새로운 가설 도출**

**Hypothesis Structure**:
```yaml
hypothesis_id: "H1"
hypothesis_statement:
  english: "Clear, testable hypothesis"
  korean: "명확하고 검증 가능한 가설"
theoretical_rationale: [이론적 근거 1, 2, 3]
originality_claim:
  what_is_new: "기존 연구와 차별점"
  why_important: "학술적/실무적 중요성"
testability:
  variables:
    independent: "독립변수"
    dependent: "종속변수"
    moderators: ["조절변수"]
    mediators: ["매개변수"]
  operationalization: [측정 방법]
feasibility_assessment:
  data_availability: 4/5
  ethical_considerations: "윤리적 고려사항"
```

**Quality Criteria**:
- ✅ 명확성 (Clarity)
- ✅ 검증가능성 (Testability)
- ✅ 독창성 (Originality)
- ✅ 중요성 (Significance)
- ✅ 실행가능성 (Feasibility)

**Scientific Skills 사용**:
- `scientific-skills:hypothesis-generation`
- `scientific-skills:scientific-writing`

**Output**: `novel-hypotheses.md` (6-15 hypotheses)

---

### Stage 4: Research Design Proposal (20-30분)

**각 가설에 대한 상세 연구 설계**

#### 4A. Quantitative Design
- 연구 유형: Experimental | Quasi-Experimental | Survey
- 실험 설계 (if applicable)
- 표본 전략
  - 표본크기 계산 (검정력 분석)
  - 표본추출 방법
- 측정 도구
  - 검증된 척도 인용
  - 신뢰도/타당도
- 자료수집 절차
- 통계분석 계획
  - 가설별 통계기법
  - 전제조건 확인
  - 강건성 검정

#### 4B. Qualitative Design
- 연구 유형: Phenomenology | Grounded Theory | Case Study
- 철학적 패러다임
- 참여자 선정
  - 의도적 표본추출
  - 포화 기준
- 자료수집 방법
  - 반구조화 인터뷰
  - 관찰
  - 문서 분석
- 분석 전략
  - 주제분석 (Thematic Analysis)
  - 코딩 절차
  - 신뢰성 확보 전략

#### 4C. Mixed Methods Design
- 설계 유형: Convergent | Explanatory Sequential | Exploratory Sequential
- 통합 전략
- Joint Display
- Meta-inferences

**Scientific Skills 사용**:
- `scientific-skills:statistical-analysis`
- `scientific-skills:research-lookup`
- `scientific-skills:peer-review`

**Output**: `research-design-proposal.md` (20-30 pages)

---

### Stage 5: Feasibility & Ethics Assessment (5-8분)

**Feasibility Assessment**:
- 자원 요구사항 (예산, 인력, 시간)
- 예상 소요 기간 (9-11개월)

**Ethical Considerations**:
- IRB 승인 요구사항
- 동의서 확보
- 기밀성 보장
- 잠재적 위험 및 완화 방안

**Data Management Plan**:
- 저장 방법
- 보유 기간
- 폐기 방법

**Output**: `feasibility-ethics-report.md` (5-8 pages)

---

### Stage 6: Final Deliverable Package (5-10분)

**통합 연구 제안서 생성**:

```markdown
# Novel Research Proposal Based on [Original Paper]

## Executive Summary (1 page)
## Part 1: Original Paper Analysis (5-7 pages)
## Part 2: Strategic Gap Analysis (3-5 pages)
## Part 3: Novel Hypotheses (8-12 pages)
## Part 4: Research Design Proposal (20-30 pages)
## Part 5: Feasibility & Ethics (5-8 pages)
## Part 6: Expected Contributions (2-3 pages)
## References (APA 7th)
```

**Output**:
```
00-paper-based-design/
├── uploaded-paper.pdf (원본)
├── paper-deep-analysis.md
├── paper-deep-analysis-ko.md (Korean)
├── strategic-gap-analysis.md
├── strategic-gap-analysis-ko.md
├── novel-hypotheses.md
├── novel-hypotheses-ko.md
├── research-design-proposal.md
├── research-design-proposal-ko.md
├── feasibility-ethics-report.md
├── feasibility-ethics-report-ko.md
├── integrated-research-proposal.md (Master)
├── integrated-research-proposal-ko.md
└── integrated-research-proposal.docx (Word)
```

---

### Stage 7: HITL-1 Checkpoint (사용자 검토)

**사용자에게 제시**:
- 제안된 가설 목록 (6-15개, 우선순위별 정렬)
- 연구 설계 옵션 (양적/질적/혼합)
- 예상 기여도 분석

**사용자 선택**:
```yaml
1_hypothesis_selection:
  - "Top 3 추천 가설 선택 (권장)"
  - "특정 가설 선택 (1-3개)"
  - "가설 수정 요청"

2_research_type_selection:
  - "양적연구 (Quantitative)"
  - "질적연구 (Qualitative)"
  - "혼합연구 (Mixed Methods)"
  - "아직 미정 (문헌검토 후 결정)"

3_next_phase_decision:
  - "승인 - Phase 1 (Literature Review) 진행 (권장)"
  - "수정 요청 - 특정 부분 보완"
  - "다른 논문으로 재시작"
```

**Command**: `/thesis:approve-topic`

---

### Stage 8: Phase 1 자동 진입

승인된 가설을 바탕으로 심층 문헌검토 자동 시작:

```
승인된 가설
  ↓
Phase 1: Literature Review (15개 에이전트 순차 실행)
  ↓
Wave 1-5 실행
  ↓
HITL-2: 문헌검토 결과 승인
  ↓
Phase 2: Research Design
  ↓
Phase 3: Writing
  ↓
Phase 4: Publication
```

---

## Quality Assurance

### GRA Compliance
- 모든 분석은 GroundedClaim 스키마 준수
- 원본 논문 주장: 페이지 번호와 함께 인용
- 새로운 가설: 이론적 근거는 문헌 뒷받침
- 측정 도구: 검증된 척도 인용

### Hallucination Firewall
- ❌ "이 논문은 완벽하다" → ✅ "강점 X, 한계 Y"
- ❌ "모든 연구자가 동의" → ✅ "다수 연구 지지 (Smith, 2020)"

### pTCS Target
- Claim-level: 70+
- Agent-level: 75+

---

## Advanced Features

### 1. Multi-Paper Analysis
```bash
/thesis:start multi-paper-upload --papers "paper1.pdf,paper2.pdf,paper3.pdf"
```
여러 논문 비교 분석 → 통합 연구 제안

### 2. Replication Study
```bash
/thesis:start replication-design --paper-path "original-study.pdf"
```
원본 논문의 개선된 재현 연구 설계

### 3. Extension Study
```bash
/thesis:start extension-design --paper-path "base-study.pdf"
```
새로운 맥락/변수 추가한 확장 연구

---

## Example Use Case

**Input**: 논문 업로드
> Doe, J. (2023). The impact of transformational leadership on employee creativity. *Journal of Management*, 49(2), 123-145.

**Stage 1 Output (요약)**:
> 변혁적 리더십과 직원 창의성의 정적 상관(r=0.42, p<.001) 발견. 그러나 횡단면 설계로 인과관계 추론 제한.

**Stage 2 Output (갭 3개)**:
- Gap 1: 횡단면 → 종단 설계 필요
- Gap 2: 심리적 안전감 매개 역할 미검증
- Gap 3: 미국 기업만 대상 → 한국 기업 검증 필요

**Stage 3 Output (가설 3개)**:
- H1: 변혁적 리더십은 시간에 따라 창의성 증가 (종단)
- H2: 심리적 안전감 매개 역할
- H3: 한국 기업에서도 정적 관계 (맥락)

**Stage 4 Output (설계)**:
- 3-wave 종단 조사 (6개월 간격)
- 한국 중소기업 300명
- LGCM + Mediation Analysis

**HITL-1**:
> H1, H2 선택 → 혼합연구 (종단조사 + 인터뷰) → 승인

**Phase 1 진입**:
> 심층 문헌검토 자동 시작...

---

## Command Reference

```bash
# 기본 사용
/thesis:start paper-upload --paper-path user-resource/papers/smith-2023.pdf

# 고급 옵션
/thesis:start paper-upload \
  --paper-path "path/to/paper.pdf" \
  --analysis-depth "comprehensive" \
  --focus-area "methodology" \
  --hypothesis-count 10 \
  --preferred-design "quantitative"

# 다중 논문 분석
/thesis:start multi-paper-upload --papers "p1.pdf,p2.pdf,p3.pdf"

# 재현 연구
/thesis:start replication-design --paper-path "original.pdf"

# 확장 연구
/thesis:start extension-design --paper-path "base.pdf"
```

---

## Integration with Main Workflow

```
Mode E (Paper Upload)
  ↓ @paper-research-designer (60-90분)
HITL-1 (가설 선택)
  ↓
Phase 1 (Literature Review)
  ↓
HITL-2 (문헌검토 승인)
  ↓
Phase 2 (Research Design)
  ↓
HITL-3/4 (연구설계 승인)
  ↓
Phase 3 (Writing)
  ↓
HITL-5/6/7 (논문 작성)
  ↓
Phase 4 (Publication)
  ↓
HITL-8 (최종 완료)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-28 | Mode E initial release - Paper-based research design workflow |
