---
description: 선행연구 논문을 업로드하여 새로운 연구 설계를 제안받습니다 (Mode E)
allowed-tools: Bash(*), Write(*), Read(*), Task(*)
agent: paper-research-orchestrator
context: fork
---

# 선행연구 논문 기반 연구 설계 시작

업로드된 논문을 박사급 수준으로 분석하여 새로운 연구 가설과 실험 설계를 제안합니다.

## 실행 프로세스

### Step 1: 논문 업로드 확인

사용자가 논문 파일을 업로드했는지 확인합니다.

**지원 파일 형식**:
- PDF (.pdf)
- Word 문서 (.docx, .doc)
- 텍스트 파일 (.txt)
- Markdown (.md)

**파일 위치 옵션**:
1. 사용자가 Claude Code에 직접 첨부
2. `user-resource/uploaded-papers/` 폴더에 저장
3. 파일 경로를 직접 제공

### Step 2: 세션 초기화

```bash
# 세션 디렉토리 생성
python3 .claude/skills/thesis-orchestrator/scripts/init_session.py \
  --mode paper-upload \
  --paper-path "$PAPER_PATH" \
  --base-dir thesis-output

# 생성되는 구조:
# thesis-output/[논문제목-날짜]/
# ├── 00-session/
# │   ├── session.json (mode: paper-upload)
# │   └── todo-checklist.md
# ├── 00-paper-based-design/
# │   └── uploaded-paper.pdf (사용자 업로드 파일)
# └── user-resource/ (optional)
```

### Step 3: @paper-research-orchestrator 실행

Master Orchestrator가 6개의 전문 subagent를 순차적으로 조율합니다:

```yaml
execution_stages:
  stage_1_deep_analysis:
    description: "논문 심층 분석"
    duration: "10-15분"
    output: "paper-deep-analysis.md (5-7 pages)"
    tasks:
      - "연구 맥락 파악 (연구질문, 이론적 프레임워크)"
      - "방법론 평가 (설계, 표본, 분석기법)"
      - "연구 결과 종합 (핵심 발견, 효과 크기)"
      - "비판적 평가 (강점, 약점, 한계점)"

  stage_2_gap_identification:
    description: "전략적 갭 식별"
    duration: "8-12분"
    output: "strategic-gap-analysis.md (3-5 gaps)"
    gap_types:
      - "이론적 갭 (Theoretical gaps)"
      - "방법론적 갭 (Methodological gaps)"
      - "맥락적 갭 (Contextual gaps)"
      - "실무적 갭 (Practical gaps)"
      - "통합적 갭 (Integration gaps)"

  stage_3_hypothesis_generation:
    description: "새로운 가설 도출"
    duration: "15-20분"
    output: "novel-hypotheses.md (6-15 hypotheses)"
    quality_criteria:
      - "명확성 (Clarity)"
      - "검증가능성 (Testability)"
      - "독창성 (Originality)"
      - "중요성 (Significance)"
      - "실행가능성 (Feasibility)"

  stage_4_research_design:
    description: "연구 설계 제안"
    duration: "20-30분"
    output: "research-design-proposal.md (20-30 pages)"
    includes:
      - "양적연구 설계 (if applicable)"
      - "질적연구 설계 (if applicable)"
      - "혼합연구 설계 (if applicable)"
      - "표본 설계"
      - "측정 도구"
      - "분석 계획"

  stage_5_feasibility:
    description: "실행가능성 및 윤리 평가"
    duration: "5-8분"
    output: "feasibility-ethics-report.md"
    includes:
      - "자원 요구사항 (예산, 인력, 시간)"
      - "윤리적 고려사항 (IRB, 동의서)"
      - "데이터 관리 계획"

  stage_6_integration:
    description: "통합 연구 제안서 생성"
    duration: "5-10분"
    output: "integrated-research-proposal.md (40-60 pages)"
    export: "integrated-research-proposal.docx (Word)"
```

**총 소요 시간**: 약 60-90분

### Step 4: HITL-1 체크포인트 (사용자 검토)

사용자에게 다음을 제시하고 선택을 요청합니다:

```
┌─────────────────────────────────────────────────────────────┐
│  📋 연구 제안서 검토 (HITL-1)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ 완료: 통합 연구 제안서 생성                              │
│                                                              │
│  📊 제안된 내용:                                             │
│  ├─ 원본 논문 분석: [paper-deep-analysis.md]                │
│  ├─ 식별된 갭: 5개 (이론 2, 방법론 1, 맥락 2)                │
│  ├─ 제안된 가설: 12개 (우선순위별 정렬)                     │
│  └─ 연구 설계 제안: 양적(실험연구), 질적(사례연구), 혼합     │
│                                                              │
│  🎯 다음 단계: 가설 및 연구 설계 선택                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**사용자 선택 옵션**:

```yaml
selection_options:
  1_hypothesis_selection:
    question: "제안된 가설 중 어떤 것을 채택하시겠습니까?"
    options:
      - "Top 3 추천 가설 선택 (권장)"
      - "특정 가설 선택 (1-3개)"
      - "가설 수정 요청"
      - "새로운 가설 추가 요청"

  2_research_type_selection:
    question: "어떤 연구 유형으로 진행하시겠습니까?"
    options:
      - "양적연구 (Quantitative)"
      - "질적연구 (Qualitative)"
      - "혼합연구 (Mixed Methods)"
      - "아직 미정 (문헌검토 후 결정)"

  3_next_phase_decision:
    question: "다음 단계를 선택하세요"
    options:
      - "승인 - Phase 1 (Literature Review) 진행 (권장)"
      - "수정 요청 - 특정 부분 보완"
      - "다른 논문으로 재시작"
      - "수동 연구질문 입력 (Mode B로 전환)"
```

**Command**:
```bash
/thesis:approve-topic  # 가설 및 연구유형 승인 후 다음 단계
```

### Step 5: Phase 1 (Literature Review) 자동 진입

사용자 승인 후, 선택된 가설을 바탕으로 심층 문헌검토가 자동으로 시작됩니다:

```
승인된 가설 → Phase 1 (15개 전문 에이전트 순차 실행)
  ↓
Wave 1: @literature-searcher → @seminal-works-analyst → @trend-analyst → @methodology-scanner
  ↓
Wave 2: @theoretical-framework-analyst → @empirical-evidence-analyst → @gap-identifier → @variable-relationship-analyst
  ↓
Wave 3: @critical-reviewer → @methodology-critic → @limitation-analyst → @future-direction-analyst
  ↓
Wave 4: @synthesis-agent → @conceptual-model-builder
  ↓
Wave 5: @plagiarism-checker → @unified-srcs-evaluator → @research-synthesizer
  ↓
HITL-2: 문헌검토 결과 승인
```

---

## 사용 예시

### Example 1: 기본 사용

```bash
# 1. 논문 파일을 user-resource/에 업로드
mkdir -p user-resource/uploaded-papers
cp ~/Downloads/transformational-leadership-2023.pdf user-resource/uploaded-papers/

# 2. 워크플로우 시작
/thesis:start paper-upload --paper-path user-resource/uploaded-papers/transformational-leadership-2023.pdf

# 3. 자동 실행 (60-90분 소요)
# - Stage 1-6 순차 실행
# - 통합 제안서 생성

# 4. HITL-1 체크포인트
# [사용자 선택]
# - 가설 3개 선택
# - 양적연구 선택
# - 승인

# 5. Phase 1 자동 진입
```

### Example 2: 다중 논문 분석 (고급)

```bash
# 여러 논문을 동시에 분석하여 종합적 연구 제안
/thesis:start multi-paper-upload \
  --papers "paper1.pdf,paper2.pdf,paper3.pdf"

# 논문 간 비교 분석 → 통합 연구 제안
```

### Example 3: 재현 연구 제안

```bash
# 원본 논문의 재현 연구 설계
/thesis:start replication-design \
  --paper-path user-resource/original-study.pdf

# 원본 방법론 재검토 → 개선된 재현 연구 설계
```

---

## 출력 파일 구조

```
thesis-output/[논문제목-2026-01-28]/
├── 00-session/
│   ├── session.json
│   └── todo-checklist.md
├── 00-paper-based-design/
│   ├── uploaded-paper.pdf (원본)
│   ├── paper-deep-analysis.md (Stage 1)
│   ├── paper-deep-analysis-ko.md (한국어 번역)
│   ├── strategic-gap-analysis.md (Stage 2)
│   ├── strategic-gap-analysis-ko.md
│   ├── novel-hypotheses.md (Stage 3)
│   ├── novel-hypotheses-ko.md
│   ├── research-design-proposal.md (Stage 4)
│   ├── research-design-proposal-ko.md
│   ├── feasibility-ethics-report.md (Stage 5)
│   ├── feasibility-ethics-report-ko.md
│   ├── integrated-research-proposal.md (Stage 6 - Master)
│   ├── integrated-research-proposal-ko.md
│   └── integrated-research-proposal.docx (Word export)
└── (이후 Phase 1-4 결과물...)
```

---

## Quality Assurance

### GRA Compliance
모든 분석 및 제안은 GroundedClaim 스키마를 준수합니다:
- 원본 논문의 주장: 페이지 번호와 함께 인용
- 새로운 가설: 이론적 근거는 문헌으로 뒷받침
- 측정 도구: 검증된 척도 인용
- 분석 방법: 방법론 문헌 참조

### Hallucination Firewall
- ❌ "이 논문은 완벽하다" → ✅ "이 논문의 강점은 X이나, Y의 한계가 있다"
- ❌ "모든 연구자가 동의" → ✅ "다수의 연구가 지지 (Smith, 2020; Lee, 2021)"

### pTCS Target
- Claim-level: 70+ (각 제안의 신뢰도)
- Agent-level: 75+ (전체 분석의 신뢰도)

---

## Troubleshooting

| 문제 | 해결 방법 |
|------|----------|
| 논문 파일을 찾을 수 없음 | `user-resource/uploaded-papers/` 경로 확인 또는 파일 경로 직접 제공 |
| 논문이 너무 짧음 (<10 pages) | Warning 확인 후 계속 진행 여부 결정 |
| 학술 논문이 아님 | Warning 확인 후 계속 진행 여부 결정 |
| 방법론 섹션 누락 | 부분 분석 결과로 진행 |
| 한국어 논문 | 자동 번역 후 분석 진행 |

---

## Advanced Options

### 고급 옵션 플래그

```bash
/thesis:start paper-upload \
  --paper-path "path/to/paper.pdf" \
  --analysis-depth "comprehensive"  # standard | comprehensive | quick
  --focus-area "methodology"        # all | methodology | theory | context
  --hypothesis-count 10             # 생성할 가설 개수 (기본: 6-15)
  --preferred-design "quantitative" # quantitative | qualitative | mixed | auto
```

---

## 다음 단계

1. **가설 승인 후**: `/thesis:approve-topic` → Phase 1 진입
2. **수정 요청**: 특정 부분 재분석 요청
3. **다른 논문 분석**: `/thesis:start paper-upload --paper-path <new-paper>`

---

## Integration with Main Workflow

이 커맨드는 **Phase 0의 Mode E**로 작동하며, 이후 워크플로우는 기존과 동일합니다:

```
Mode E (Paper Upload)
  ↓
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
HITL-5/6/7 (논문 작성 검토)
  ↓
Phase 4 (Publication)
  ↓
HITL-8 (최종 완료)
```

---

$ARGUMENTS
