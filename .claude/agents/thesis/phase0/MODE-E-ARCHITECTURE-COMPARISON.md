# Mode E 아키텍처 비교: AS-IS vs TO-BE

**작성일**: 2026-01-28
**목적**: 현재 구조와 최적화된 구조를 시각적으로 비교

---

## 1. 전체 아키텍처 비교

### AS-IS (현재 구조)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Command                              │
│               /thesis:start paper-upload                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              paper-research-designer                         │
│              (Monolithic Agent - Opus)                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Stage 1: Deep Paper Analysis            [10-15분]     │ │
│  └────────────────────────────────────────────────────────┘ │
│                     │                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Stage 2: Strategic Gap Identification   [8-12분]      │ │
│  └────────────────────────────────────────────────────────┘ │
│                     │                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Stage 3: Novel Hypothesis Generation    [15-20분]     │ │
│  └────────────────────────────────────────────────────────┘ │
│                     │                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Stage 4: Research Design Proposal       [20-30분]     │ │
│  └────────────────────────────────────────────────────────┘ │
│                     │                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Stage 5: Feasibility & Ethics           [5-8분]       │ │
│  └────────────────────────────────────────────────────────┘ │
│                     │                                        │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Stage 6: Final Integration              [5-10분]      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└─────────────────────┬────────────────────────────────────────┘
                      │
                      ▼
              [HITL-1 Checkpoint]
                      │
                      ▼
                  Phase 1 진입
```

**문제점**:
- ❌ 단일 거대 agent (600+ 줄)
- ❌ 순차 실행만 가능 (병렬 불가)
- ❌ 오류 시 전체 재시작 필요
- ❌ Stage별 독립 실행 불가
- ❌ 재사용성 낮음
- ❌ 모든 stage에 Opus 사용 (비용 높음)

---

### TO-BE (최적화된 구조)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Commands                             │
│  /thesis:start paper-upload  (전체 워크플로우)              │
│  /thesis:analyze-paper       (Stage 1만)                    │
│  /thesis:identify-gaps       (Stage 2만)                    │
│  /thesis:generate-hypotheses (Stage 3만)                    │
│  ...                                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         paper-research-orchestrator                          │
│         (Master Agent - Sonnet - Lightweight)                │
│                                                              │
│  • Workflow coordination                                    │
│  • Subagent delegation                                      │
│  • Error handling & retry                                   │
│  • Progress logging                                         │
│  • HITL checkpoint management                               │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
   [Hook: pre-stage]       [Parallel Execution]
        │                         │
        │           ┌─────────────┼─────────────┐
        │           │             │             │
        ▼           ▼             ▼             ▼
┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────┐
│ Stage 1   │ │ Stage 2   │ │ Stage 3   │ │ Stage 4   │
│  paper-   │→│   gap-    │→│hypothesis-│→│  design-  │
│ analyzer  │ │identifier │ │ generator │ │ proposer  │
│  (Opus)   │ │  (Opus)   │ │  (Opus)   │ │  (Opus)   │
│ [10-15분] │ │ [8-12분]  │ │ [15-20분] │ │ [20-30분] │
└─────┬─────┘ └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
      │             │             │             │
      │             │             │             │
      ▼             ▼             ▼             ▼
   [Hook: post-stage - GRA, pTCS validation]
      │             │             │             │
      │             │             │             │
      ▼             ▼             ▼             ▼
┌───────────┐ ┌───────────────────────────────────┐
│ Stage 5   │ │         Stage 6                   │
│feasibility│→│     proposal-integrator           │
│ assessor  │ │         (Opus)                    │
│ (Sonnet)  │ │       [5-10분]                    │
│ [5-8분]   │ │                                   │
└─────┬─────┘ └─────┬─────────────────────────────┘
      │             │
      └─────────────┴──────────────┐
                                   ▼
                       [Hook: hitl-checkpoint]
                                   │
                                   ▼
                            [HITL-1 Checkpoint]
                                   │
                                   ▼
                              Phase 1 진입
```

**개선점**:
- ✅ Master-Subagent 패턴 (각 100-150줄)
- ✅ 병렬 실행 가능 (일부 stage)
- ✅ Stage별 독립 재실행
- ✅ 오류 격리 및 재시도
- ✅ 높은 재사용성
- ✅ 모델 최적화 (Orchestrator: Sonnet, 복잡한 stage: Opus)

---

## 2. Skills 아키텍처

### AS-IS (현재)

```
┌─────────────────────────────────────────────────────────────┐
│         paper-research-designer                              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Hard-coded Logic (600+ lines)                         │ │
│  │                                                         │ │
│  │  • Paper analysis logic                                │ │
│  │  • Gap identification logic                            │ │
│  │  • Hypothesis generation logic                         │ │
│  │  • Design proposal logic                               │ │
│  │  • Feasibility assessment logic                        │ │
│  │  • Integration logic                                   │ │
│  │                                                         │ │
│  │  ❌ 재사용 불가                                         │ │
│  │  ❌ 다른 agent에서 활용 불가                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  External Dependency:                                        │
│  • scientific-skills:* (only)                                │
└─────────────────────────────────────────────────────────────┘
```

---

### TO-BE (최적화)

```
┌─────────────────────────────────────────────────────────────┐
│                 Reusable Skills Layer                        │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ paper-analysis   │  │ hypothesis-      │                │
│  │                  │  │   development    │                │
│  │ • PDF parsing    │  │ • Templates      │                │
│  │ • Section detect │  │ • Quality checks │                │
│  │ • Auto translate │  │ • Rationale gen  │                │
│  └──────────────────┘  └──────────────────┘                │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ research-design- │  │ validation-      │                │
│  │   templates      │  │   checks         │                │
│  │                  │  │                  │                │
│  │ • Quant designs  │  │ • GRA compliance │                │
│  │ • Qual designs   │  │ • Hallucination  │                │
│  │ • Mixed designs  │  │ • pTCS scoring   │                │
│  └──────────────────┘  └──────────────────┘                │
└────────────┬────────────────────────────────────────────────┘
             │
             │ (Skills used by)
             │
    ┌────────┴────────┬────────────┬────────────┐
    ▼                 ▼            ▼            ▼
┌─────────┐  ┌─────────────┐  ┌─────────┐  ┌─────────┐
│ paper-  │  │    gap-     │  │hypothesis│ │ design- │
│analyzer │  │ identifier  │  │generator │ │proposer │
└─────────┘  └─────────────┘  └─────────┘  └─────────┘
                      ...

✅ 재사용 가능 (다른 Phase/Mode에서도 사용)
✅ 유지보수 용이 (Skills만 업데이트)
✅ 테스트 독립적
```

---

## 3. 데이터 흐름 비교

### AS-IS (Monolithic)

```
User Input (paper.pdf)
        │
        ▼
┌───────────────────┐
│ paper-research-   │
│    designer       │
│                   │
│  [Internal State] │←─┐ (모든 데이터가 agent 내부에)
│  • paper_text     │  │
│  • analysis       │  │
│  • gaps           │  │
│  • hypotheses     │  │
│  • design         │  │
│  • feasibility    │  │
│  • proposal       │──┘
│                   │
└─────────┬─────────┘
          │
          ▼
   Output Files (6개)

❌ 데이터 흐름 불투명
❌ 중간 상태 검증 어려움
❌ Stage 간 의존성 명확하지 않음
```

---

### TO-BE (Explicit Data Flow)

```
User Input (paper.pdf)
        │
        ▼
[paper-research-orchestrator]
        │
        ▼
┌───────────────────┐
│   paper-analyzer  │
└─────────┬─────────┘
          │
          ▼
  paper-deep-analysis.md ←── ✅ Explicit output
          │
          ▼
┌───────────────────┐
│  gap-identifier   │
└─────────┬─────────┘
          │
          ▼
strategic-gap-analysis.md ←── ✅ Explicit output
          │
          ▼
┌───────────────────┐
│hypothesis-generator│
└─────────┬─────────┘
          │
          ▼
   novel-hypotheses.md ←── ✅ Explicit output
          │
          ▼
┌───────────────────┐
│  design-proposer  │
└─────────┬─────────┘
          │
          ▼
research-design-proposal.md ←── ✅ Explicit output
          │
          ▼
┌───────────────────┐
│feasibility-assessor│
└─────────┬─────────┘
          │
          ▼
feasibility-ethics-report.md ←── ✅ Explicit output
          │
          ▼
┌───────────────────────────┐
│   proposal-integrator     │
└─────────┬─────────────────┘
          │
          ▼
integrated-research-proposal.md ←── ✅ Final output

✅ 데이터 흐름 명확
✅ 각 Stage 출력 독립 검증 가능
✅ Stage 간 의존성 명시적
✅ 중간 결과물 재사용 가능
```

---

## 4. 오류 처리 비교

### AS-IS (Fragile)

```
Start
  │
  ▼
Stage 1 ──[Error]──┐
  │                 │
  ▼                 │
Stage 2 ──[Error]──┤
  │                 │
  ▼                 │
Stage 3 ──[Error]──┤
  │                 │
  ▼                 │
Stage 4 ──[Error]──┤
  │                 │
  ▼                 │
Stage 5 ──[Error]──┤
  │                 │
  ▼                 │
Stage 6 ──[Error]──┤
  │                 │
  ▼                 ▼
Success        ❌ FAIL
                   │
                   ▼
         전체 재시작 필요
         (60-90분 손실)
```

---

### TO-BE (Resilient)

```
Start
  │
  ▼
Stage 1 ──[Error]──► Retry (최대 2회) ──[Still Fail]──┐
  │                                                    │
  │ [Success]                                         │
  ▼                                                    │
Stage 2 ──[Error]──► Retry (최대 2회) ──[Still Fail]──┤
  │                                                    │
  │ [Success]                                         │
  ▼                                                    │
Stage 3 ──[Error]──► Retry (최대 2회) ──[Still Fail]──┤
  │                                                    │
  │ [Success]                                         │
  ▼                                                    │
Stage 4 ──[Error]──► Retry (최대 2회) ──[Still Fail]──┤
  │                                                    │
  │ [Success]                                         │
  ▼                                                    │
Stage 5 ──[Error]──► Retry (최대 2회) ──[Still Fail]──┤
  │                                                    │
  │ [Success]                                         │
  ▼                                                    │
Stage 6 ──[Error]──► Retry (최대 2회) ──[Still Fail]──┤
  │                                                    │
  │ [Success]                                         │
  ▼                                                    │
Success                                               │
                                                      │
                                                      ▼
                                          Partial Success
                                                      │
                                                      ▼
                                    User Decision:
                                    • Fix & Resume from failed stage
                                    • Skip failed stage
                                    • Abort
                                                      │
                                                      ▼
                                    Resume:
                                    /thesis:generate-hypotheses
                                    (특정 stage만 재실행, 5-20분)

✅ 오류 격리
✅ Stage별 재시도
✅ Partial success 가능
✅ 특정 stage만 재실행 (시간 절약)
```

---

## 5. 사용자 경험 비교

### AS-IS (Inflexible)

```
사용자 → /thesis:start paper-upload → [60-90분 대기] → 결과 또는 실패

❌ 전체 완료 또는 전체 실패 (All or Nothing)
❌ 중간 수정 불가
❌ Stage별 결과 확인 어려움
❌ 오류 시 전체 재시작 필요
```

---

### TO-BE (Flexible)

```
사용자 옵션 1: 전체 워크플로우
  /thesis:start paper-upload → [60-90분 대기] → 결과

사용자 옵션 2: Stage별 실행
  /thesis:analyze-paper         → [10-15분] → 분석 결과 확인
    ↓ (만족)
  /thesis:identify-gaps         → [8-12분]  → 갭 결과 확인
    ↓ (만족)
  /thesis:generate-hypotheses   → [15-20분] → 가설 확인
    ↓ (수정 필요)
  /thesis:generate-hypotheses   → [15-20분] → 수정된 가설 확인
    ↓ (만족)
  /thesis:propose-design        → [20-30분] → 설계 확인
    ↓ ...

사용자 옵션 3: 중간부터 재개
  [Stage 1-3 완료됨]
    ↓
  /thesis:propose-design --input novel-hypotheses.md
    ↓
  [Stage 4-6 진행]

✅ 유연한 실행 모드
✅ Stage별 결과 확인 및 수정
✅ 중간부터 재개 가능
✅ 점진적 개선 가능
```

---

## 6. 성능 및 비용 비교

### AS-IS

```yaml
performance:
  total_time: "60-90분 (순차 실행)"
  retry_time: "60-90분 (전체 재시작)"
  parallel_execution: "불가능"

cost:
  model: "Opus for all stages"
  tokens: "~500K tokens"
  estimated_cost: "$15-20 per run"

flexibility:
  stage_rerun: "불가능 (전체 재시작 필요)"
  partial_results: "불가능"
```

---

### TO-BE

```yaml
performance:
  total_time: "45-70분 (병렬 최적화)"
    - Stage 4A, 4B, 4C 병렬 실행 가능
    - Orchestrator overhead 최소화
  retry_time: "5-30분 (특정 stage만)"
  parallel_execution: "가능 (일부 stage)"

cost:
  model: "Opus for complex stages, Sonnet for orchestrator"
  tokens: "~350K tokens (30% 감소)"
    - Orchestrator: Sonnet (lightweight)
    - Stage 5: Sonnet (simple assessment)
  estimated_cost: "$10-13 per run (35% 절감)"

flexibility:
  stage_rerun: "가능 (개별 실행)"
  partial_results: "가능 (Stage별 출력)"

scalability:
  additional_stages: "쉬움 (새 subagent 추가)"
  modifications: "격리됨 (특정 subagent만 수정)"
```

---

## 7. 코드 복잡도 비교

### AS-IS (Monolithic)

```yaml
code_complexity:
  paper-research-designer.md:
    lines: 614
    stages: 6 (all in one file)
    responsibilities: "All"
    maintainability: "LOW"
    testability: "LOW"

  start-paper-upload.md:
    lines: 351
    agent: "paper-research-designer"
```

**Total Lines**: ~965 lines (2개 파일)

---

### TO-BE (Modular)

```yaml
code_complexity:
  paper-research-orchestrator.md:
    lines: ~150
    responsibilities: "Workflow coordination only"
    maintainability: "HIGH"
    testability: "HIGH"

  subagents/ (6 files):
    paper-analyzer.md: ~120 lines
    gap-identifier.md: ~100 lines
    hypothesis-generator.md: ~130 lines
    design-proposer.md: ~150 lines
    feasibility-assessor.md: ~80 lines
    proposal-integrator.md: ~100 lines
    total: ~680 lines

  skills/ (4 files):
    paper-analysis/SKILL.md: ~80 lines
    hypothesis-development/SKILL.md: ~70 lines
    research-design-templates/SKILL.md: ~100 lines
    validation-checks/SKILL.md: ~60 lines
    total: ~310 lines

  commands/ (8 files):
    start-paper-upload.md: ~100 lines
    analyze-paper.md: ~40 lines
    identify-gaps.md: ~40 lines
    generate-hypotheses.md: ~40 lines
    propose-design.md: ~40 lines
    assess-feasibility.md: ~40 lines
    integrate-proposal.md: ~40 lines
    review-proposal.md: ~50 lines
    total: ~390 lines

  hooks/ (3 files):
    pre-stage.sh: ~30 lines
    post-stage.sh: ~40 lines
    hitl-checkpoint.sh: ~30 lines
    total: ~100 lines
```

**Total Lines**: ~1,630 lines (21개 파일)

**하지만**:
- ✅ 각 파일이 작고 집중됨 (100-150 lines)
- ✅ 단일 책임 원칙 준수
- ✅ 독립 테스트 가능
- ✅ 재사용성 높음
- ✅ 유지보수 용이

**LOC가 증가했지만 복잡도는 감소**:
- Cyclomatic Complexity: HIGH → LOW
- Coupling: HIGH → LOW
- Cohesion: LOW → HIGH

---

## 8. 테스트 전략 비교

### AS-IS

```
테스트 가능성:

┌─────────────────────────────────────┐
│  paper-research-designer            │
│                                     │
│  ❌ 전체 통합 테스트만 가능         │
│  ❌ 단위 테스트 불가능              │
│  ❌ Mock 입력 사용 어려움           │
│  ❌ 60-90분 소요 (매 테스트마다)   │
└─────────────────────────────────────┘

테스트 커버리지: ~30% (통합 테스트만)
```

---

### TO-BE

```
테스트 가능성:

┌─────────────────────────────────────┐
│  Unit Tests (각 Subagent)           │
│                                     │
│  ✅ paper-analyzer                  │
│     Mock PDF → analysis.md          │
│     Time: 5분                       │
│                                     │
│  ✅ gap-identifier                  │
│     Mock analysis.md → gaps.md      │
│     Time: 3분                       │
│                                     │
│  ✅ hypothesis-generator            │
│     Mock gaps.md → hypotheses.md    │
│     Time: 5분                       │
│                                     │
│  ... (나머지 subagents)             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  Integration Tests (Orchestrator)   │
│                                     │
│  ✅ Mock subagent outputs           │
│  ✅ Workflow coordination           │
│  ✅ Error handling                  │
│     Time: 2분                       │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│  E2E Tests (전체 워크플로우)        │
│                                     │
│  ✅ 실제 논문 입력                  │
│  ✅ 전체 Stage 1-6 실행             │
│     Time: 60분                      │
└─────────────────────────────────────┘

테스트 커버리지: ~85% (단위 + 통합 + E2E)
```

---

## 9. 확장성 비교

### AS-IS

```
새로운 Stage 추가 시:

┌─────────────────────────────────────────────┐
│  paper-research-designer.md 수정            │
│                                             │
│  1. Stage 7 로직 추가 (100+ lines)          │
│  2. 기존 Stage 1-6과 통합                   │
│  3. 데이터 흐름 조정                        │
│  4. 오류 처리 추가                          │
│  5. 전체 파일 600 → 700+ lines              │
│                                             │
│  ❌ 기존 코드 수정 필요                     │
│  ❌ 회귀 테스트 필요 (전체 60-90분)         │
│  ❌ 리스크 높음 (기존 기능 영향)            │
└─────────────────────────────────────────────┘

Estimated Time: 1-2일
Risk Level: HIGH
```

---

### TO-BE

```
새로운 Stage 추가 시:

┌─────────────────────────────────────────────┐
│  새 Subagent 생성                           │
│                                             │
│  1. stage-7-subagent.md 생성 (100 lines)    │
│  2. Orchestrator에 stage 7 추가 (5 lines)   │
│  3. 새 커맨드 생성 (선택 사항)              │
│                                             │
│  ✅ 기존 코드 수정 최소화                   │
│  ✅ 독립 테스트 (5-10분)                    │
│  ✅ 리스크 낮음 (기존 기능 독립)            │
└─────────────────────────────────────────────┘

Estimated Time: 0.5-1일
Risk Level: LOW
```

---

## 10. 의존성 그래프

### AS-IS (Tightly Coupled)

```
┌─────────────────────────────────────┐
│   paper-research-designer           │
│                                     │
│   ┌─────┐                           │
│   │Stage│◄──────────────────┐       │
│   │  1  │                   │       │
│   └──┬──┘                   │       │
│      │                      │       │
│      ▼                      │       │
│   ┌─────┐                  │       │
│   │Stage│◄─────────────┐   │       │
│   │  2  │              │   │       │
│   └──┬──┘              │   │       │
│      │                 │   │       │
│      ▼                 │   │       │
│   ┌─────┐              │   │       │
│   │Stage│◄────────┐    │   │       │
│   │  3  │         │    │   │       │
│   └──┬──┘         │    │   │       │
│      │            │    │   │       │
│      ▼            │    │   │       │
│   ┌─────┐         │    │   │       │
│   │Stage│◄────┐   │    │   │       │
│   │  4  │     │   │    │   │       │
│   └──┬──┘     │   │    │   │       │
│      │        │   │    │   │       │
│      ▼        │   │    │   │       │
│   ┌─────┐     │   │    │   │       │
│   │Stage│◄─┐  │   │    │   │       │
│   │  5  │  │  │   │    │   │       │
│   └──┬──┘  │  │   │    │   │       │
│      │     │  │   │    │   │       │
│      ▼     │  │   │    │   │       │
│   ┌─────┐  │  │   │    │   │       │
│   │Stage│  │  │   │    │   │       │
│   │  6  ├──┴──┴───┴────┴───┘       │
│   └─────┘                           │
│                                     │
│  ❌ 높은 결합도 (Tight Coupling)    │
│  ❌ 순환 의존성 가능성              │
│  ❌ 변경 영향 범위 큼               │
└─────────────────────────────────────┘
```

---

### TO-BE (Loosely Coupled)

```
┌─────────────────────────────────────┐
│   paper-research-orchestrator       │
│   (Coordinator Only)                │
└────┬────────────────────────────────┘
     │
     ├──► paper-analyzer
     │      │
     │      └──► Skill: paper-analysis
     │      └──► Skill: validation-checks
     │
     ├──► gap-identifier
     │      │
     │      └──► Skill: validation-checks
     │
     ├──► hypothesis-generator
     │      │
     │      └──► Skill: hypothesis-development
     │      └──► Skill: validation-checks
     │
     ├──► design-proposer
     │      │
     │      └──► Skill: research-design-templates
     │      └──► Skill: validation-checks
     │
     ├──► feasibility-assessor
     │      │
     │      └──► Skill: validation-checks
     │
     └──► proposal-integrator
            │
            └──► Skill: validation-checks

✅ 낮은 결합도 (Loose Coupling)
✅ 단방향 의존성만 (Orchestrator → Subagent → Skills)
✅ 변경 영향 범위 작음
✅ 독립적인 개발 및 테스트 가능
```

---

## 요약

| 측면 | AS-IS | TO-BE | 개선도 |
|------|-------|-------|--------|
| **아키텍처** | Monolithic (1개 agent) | Master-Subagent (1+6) | ⭐⭐⭐⭐⭐ |
| **실행 시간** | 60-90분 (순차) | 45-70분 (병렬 최적화) | ⭐⭐⭐ |
| **재시도 시간** | 60-90분 (전체) | 5-30분 (특정 stage) | ⭐⭐⭐⭐⭐ |
| **비용** | $15-20 (Opus only) | $10-13 (Mixed models) | ⭐⭐⭐⭐ |
| **유연성** | 낮음 (All or Nothing) | 높음 (Stage별 실행) | ⭐⭐⭐⭐⭐ |
| **재사용성** | 낮음 (Monolithic) | 높음 (Skills + Subagents) | ⭐⭐⭐⭐⭐ |
| **테스트 가능성** | 낮음 (통합 테스트만) | 높음 (단위 + 통합 + E2E) | ⭐⭐⭐⭐⭐ |
| **유지보수성** | 낮음 (614 lines) | 높음 (~150 lines/file) | ⭐⭐⭐⭐⭐ |
| **확장성** | 낮음 (기존 코드 수정) | 높음 (새 subagent 추가) | ⭐⭐⭐⭐⭐ |
| **오류 처리** | 취약 (전체 실패) | 견고 (격리 + 재시도) | ⭐⭐⭐⭐⭐ |

---

**결론**: TO-BE 아키텍처는 모든 측면에서 AS-IS 대비 현저히 개선되었으며, 특히 **유연성**, **재사용성**, **유지보수성**, **확장성** 측면에서 획기적인 향상을 보임.

---

**작성자**: Claude Code
**검토자**: [사용자 이름]
**승인 상태**: ⬜ 검토 대기
