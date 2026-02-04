---
description: Phase 2 연구설계 파이프라인 실행. 선택된 연구 유형에 따라 적절한 에이전트들을 자동으로 실행합니다.
context: fork
agent: general-purpose
---

# Phase 2: 연구설계 파이프라인 실행

## 개요

이 커맨드는 **Phase 2 (Research Design) 파이프라인**을 실행하여 연구 유형(양적/질적/혼합)에 맞는 연구설계를 자동으로 생성합니다.

## 전제 조건

✅ **필수 완료 사항**:
1. Phase 1 (Literature Review) 완료
2. HITL-2 (문헌검토 승인) 완료
3. HITL-3 (`/thesis:set-research-type`) 연구 유형 선택 완료

## 실행 방법

```bash
python3 .claude/skills/thesis-orchestrator/scripts/run_research_design.py
```

또는 Claude를 통해:
```
Please run the research design pipeline for my thesis.
```

## 연구 유형별 실행 경로

### 1️⃣ 양적연구 (Quantitative) 경로

**에이전트 순서**:
```
Agent 1: @hypothesis-developer
  └─ Output: 20-hypotheses.md
  └─ Role: 연구질문을 검증 가능한 가설로 변환

Agent 2: @research-model-developer
  └─ Output: 21-research-model-final.md
  └─ Role: 연구모델 및 변수 조작화

Agent 3: @sampling-designer
  └─ Output: 22-sampling-design.md
  └─ Role: 표본설계 및 표본크기 결정

Agent 4: @statistical-planner
  └─ Output: 23-statistical-analysis-plan.md
  └─ Role: 통계분석 계획 수립
```

**생성되는 내용**:
- 귀무가설/대립가설 체계
- 연구모델 다이어그램
- 표본추출 전략
- 통계분석 방법 (회귀분석, 매개효과, 조절효과 등)

### 2️⃣ 질적연구 (Qualitative) 경로

**에이전트 순서**:
```
Agent 1: @paradigm-consultant
  └─ Output: 20-research-paradigm.md
  └─ Role: 연구 패러다임 및 인식론적 입장 정립

Agent 2: @participant-selector
  └─ Output: 21-participant-selection.md
  └─ Role: 참여자 선정 전략 및 기준

Agent 3: @qualitative-data-designer
  └─ Output: 22-data-collection-protocol.md
  └─ Role: 자료수집 프로토콜 (인터뷰, 관찰 등)

Agent 4: @qualitative-analysis-planner
  └─ Output: 23-qualitative-analysis-plan.md
  └─ Role: 질적 분석 방법 (코딩, 주제분석 등)
```

**생성되는 내용**:
- 존재론/인식론적 입장
- 참여자 선정 기준 및 포화 전략
- 인터뷰 가이드/관찰 프로토콜
- 질적 분석 방법 (근거이론, 현상학 등)

### 3️⃣ 혼합연구 (Mixed Methods) 경로

**에이전트 순서**:
```
Core Agents:
  Agent 1: @mixed-methods-designer
    └─ Output: 20-mixed-methods-design.md
    └─ Role: 혼합연구 설계 (수렴적/순차적/내재적)

  Agent 2: @integration-strategist
    └─ Output: 21-integration-strategy.md
    └─ Role: 양적-질적 통합 전략

Then executes:
  → Quantitative path (4 agents)
  → Qualitative path (4 agents)
```

**생성되는 내용**:
- 혼합연구 설계 유형 선택 및 근거
- 양적-질적 통합 지점 및 방법
- 양적 컴포넌트 전체
- 질적 컴포넌트 전체

## 출력 구조

```
thesis-output/[your-project]/
└── _temp/
    ├── 20-[first-component].md        # 첫 번째 설계 요소
    ├── 21-[second-component].md       # 두 번째 설계 요소
    ├── 22-[third-component].md        # 세 번째 설계 요소
    ├── 23-[fourth-component].md       # 네 번째 설계 요소
    └── research-design-final.md       # 최종 종합 문서 ⭐
```

**파일명 예시**:

| 연구 유형 | 파일명 |
|-----------|--------|
| Quantitative | `20-hypotheses.md`, `21-research-model-final.md`, `22-sampling-design.md`, `23-statistical-analysis-plan.md` |
| Qualitative | `20-research-paradigm.md`, `21-participant-selection.md`, `22-data-collection-protocol.md`, `23-qualitative-analysis-plan.md` |
| Mixed | 위 두 가지 + `20-mixed-methods-design.md`, `21-integration-strategy.md` |

## 품질 보증

### 자동 품질 검증

각 에이전트 출력은 다음을 포함합니다:

✅ **GRA (Grounded Research Architecture) Compliance**
```yaml
claims:
  - id: "AGENT-001"
    text: "[주장 내용]"
    claim_type: THEORETICAL|EMPIRICAL|METHODOLOGICAL
    sources:
      - type: PRIMARY|SECONDARY
        reference: "[출처]"
        verified: true
    confidence: [0-100]
    uncertainty: "[불확실성 명시]"
```

✅ **품질 체크리스트**
- [ ] 문헌 근거 충분성
- [ ] 방법론적 타당성
- [ ] 실행 가능성
- [ ] 윤리적 고려사항

✅ **SRCS (Scholarly Rigor Confidence Score) 평가**
- Citation Quality
- Reasoning Depth
- Counterargument Engagement
- Scope Awareness

## 실행 예시

```bash
$ cd /path/to/Dissertation-system-main-v3
$ python3 .claude/skills/thesis-orchestrator/scripts/run_research_design.py

Loading thesis workflow context...
✅ Context loaded

📋 Research Type: QUANTITATIVE

================================================================================
PHASE 2 - QUANTITATIVE RESEARCH DESIGN PATH
================================================================================

================================================================================
QUANTITATIVE AGENT 1/4: Hypothesis Development
Agent: @hypothesis-developer
================================================================================

📋 Research Topic: [Your topic]

🎯 Research Questions:
   1. RQ1: [Question 1]
   2. RQ2: [Question 2]

✅ Agent 1 Complete: hypothesis-developer
📄 Output: /path/to/_temp/20-hypotheses.md

[... continues for all 4 agents ...]

================================================================================
PHASE 2 RESEARCH DESIGN COMPLETE ✅
================================================================================

📊 Summary:
   - Research Type: Quantitative
   - All research design agents executed successfully
   - Synthesis document created

📁 Outputs:
   - .../thesis-output/[project]/_temp/20-hypotheses.md
   - .../thesis-output/[project]/_temp/21-research-model-final.md
   - .../thesis-output/[project]/_temp/22-sampling-design.md
   - .../thesis-output/[project]/_temp/23-statistical-analysis-plan.md
   - .../thesis-output/[project]/_temp/research-design-final.md

🎯 Next Step: HITL-4 - Research Design Approval
   Use command: /thesis:approve-design
```

## 완료 후 다음 단계

### HITL-4: 연구설계 승인

```
/thesis:approve-design
```

**검토 사항**:
1. ✅ 연구설계가 연구질문에 적합한가?
2. ✅ 방법론적 타당성이 충분한가?
3. ✅ 실행 가능성이 있는가?
4. ✅ 윤리적 문제는 없는가?

**승인 후**: Phase 3 (Thesis Writing) 진행 가능

## 문제 해결

### 오류: "Research type not set"
```bash
# 해결: 먼저 연구 유형을 설정하세요
/thesis:set-research-type
```

### 오류: "Phase 1 not complete"
```bash
# 해결: Phase 1 먼저 완료하세요
python3 .claude/skills/thesis-orchestrator/scripts/run_literature_review.py
```

### session.json 확인
```bash
# 현재 상태 확인
cat thesis-output/[your-project]/00-session/session.json | grep -A 5 "research"
```

## 기술 세부사항

### 스크립트 구조

```python
# Main execution flow
1. load_context() - 세션 정보 로드
2. get_research_type() - 연구 유형 확인
3. [run_quantitative_path() | run_qualitative_path() | run_mixed_methods_path()]
4. create_research_design_final() - 최종 종합
5. Update session.json - 상태 업데이트
```

### 에이전트 실행 패턴

각 에이전트는:
1. 이전 단계 출력 읽기 (context)
2. 에이전트별 분석 수행
3. GRA-compliant 마크다운 생성
4. session.json 업데이트
5. 다음 에이전트로 컨텍스트 전달

### 의존성

```python
from context_loader import load_context
# context.session - 세션 정보
# context.working_dir - 작업 디렉토리
# context.get_output_path() - 출력 경로 헬퍼
# context.update_session() - 세션 업데이트
```

## 참고 자료

### Agent 정의 위치
- Quantitative: `.claude/agents/thesis/phase2-design/quantitative/`
- Qualitative: `.claude/agents/thesis/phase2-design/qualitative/`
- Mixed: `.claude/agents/thesis/phase2-design/mixed/`

### 관련 커맨드
- `/thesis:set-research-type` - 연구 유형 설정 (HITL-3)
- `/thesis:approve-design` - 연구설계 승인 (HITL-4)
- `/thesis:progress` - 진행상황 확인
- `/thesis:status` - 워크플로우 상태 확인

---

**Created**: 2026-01-30
**Version**: 1.0.0
**Dependencies**: Phase 1 complete, Research type selected
**Next Phase**: Phase 3 (Thesis Writing)
