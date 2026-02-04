# Mode F: Proposal-Based Research Workflow

연구 프로포절을 업로드하여 기존 계획을 추출하고, 체계적 연구를 수행하는 워크플로우입니다.

## 개요

- **핵심 철학**: 사용자의 기존 연구 계획을 **존중하면서 보강**하는 시스템
- **입력**: 연구 프로포절 파일 (PDF, DOCX, MD, TXT)
- **출력**: 추출된 연구 계획 → 문헌검토로 검증 → 연구 수행
- **Agent**: @proposal-analyzer (Opus)

### Mode E vs Mode F

| 항목 | Mode E (Paper Upload) | Mode F (Proposal Upload) |
|------|----------------------|--------------------------|
| 입력물 | 선행연구 논문 (남의 논문) | 연구 프로포절 (나의 계획서) |
| 에이전트 | @paper-research-designer | @proposal-analyzer |
| 분석 목적 | 비판적 분석 → 새 가설 도출 | 구조 파싱 → 계획 추출 |
| 출력물 | 새로운 연구 제안서 (40-60p) | 추출된 연구 계획 + 완성도 평가 |
| HITL | review-proposal (새 제안 검토) | review-extracted-plan (추출 확인) |
| Phase 1 관계 | 새로운 관점으로 문헌검토 | 기존 계획 검증을 위한 문헌검토 |
| 특수 정책 | 없음 | Flag-and-Follow (모순 감지) |

---

## Workflow Stages

### Stage 0: Initialization

```bash
# 세션 초기화
python3 .claude/skills/thesis-orchestrator/scripts/init_session.py \
  --mode proposal \
  --proposal-path "user-resource/proposals/my-proposal.pdf" \
  --base-dir thesis-output \
  "My Research Proposal Title"
```

**Output**:
```
thesis-output/[프로포절제목-날짜]/
├── 00-session/
│   ├── session.json (mode: proposal)
│   └── todo-checklist.md
└── 00-proposal-analysis/
    └── my-proposal.pdf
```

---

### Stage 1: Proposal Analysis

**Agent**: @proposal-analyzer

프로포절 문서를 파싱하여 구조화된 연구 계획을 추출합니다.

**추출 항목**:
1. 연구질문 (research_questions)
2. 가설 (hypotheses) - 있는 경우
3. 방법론 (methodology_type, subtype)
4. 이론적 프레임워크 (theoretical_framework)
5. 변수 (independent, dependent, mediating, moderating)
6. 표본 계획 (proposed_sample)
7. 분석 전략 (proposed_analysis)
8. 완성도 평가 (completeness_score 0-100, gap_report)

**Output**: `00-proposal-analysis/proposal-analysis.md`

---

### Stage 2: HITL - Extracted Plan Review

**Command**: `/thesis:review-extracted-plan`

사용자가 추출된 계획의 정확성을 확인합니다.

**선택지**:
- APPROVE: 추출된 계획대로 진행
- MODIFY: 특정 항목 수정
- SUPPLEMENT: 누락 항목 보완
- REJECT: 다른 모드로 변경

**승인 시**:
- session.json에 추출된 계획 사전 설정
- research_questions, hypotheses, type, methodology 등 자동 입력
- Phase 1로 자동 진입

---

### Stage 3: Phase 1 with Flag-and-Follow

문헌검토(Phase 1)는 기존 워크플로우와 동일하게 진행되지만,
**Flag-and-Follow 정책**이 추가 적용됩니다.

#### Flag-and-Follow 정책

문헌검토 결과와 프로포절 계획 간 모순이 발견되면:

1. **Flag (표시)**: 모순 내용을 명시적으로 안내
2. **Follow (추적)**: HITL-2에서 사용자에게 선택지 제시

**확인 사항**:
- 프로포절의 연구질문이 문헌에 의해 지지되는지
- 프로포절의 방법론이 선행연구 패턴과 정합하는지
- 프로포절의 이론적 프레임워크가 최신 문헌과 부합하는지

**모순 발견 시 선택지**:
1. 프로포절 유지 (근거 제시 필요)
2. 문헌검토 결과 반영 수정
3. 절충안 도출

---

## session.json 스키마 확장

Mode F에서 추가되는 필드:

```json
{
  "version": "2.3.0",
  "research": {
    "mode": "proposal",
    "topic": "...",
    "research_questions": ["RQ1", "RQ2"],
    "hypotheses": ["H1", "H2"],
    "type": "quantitative",
    "entry_path": null
  },
  "proposal_metadata": {
    "original_path": "/path/to/proposal.pdf",
    "uploaded_at": "2026-01-31T...",
    "analysis_status": "pending|analyzed|approved",
    "completeness_score": 85,
    "extracted_plan": {
      "methodology": { "type": "...", "subtype": "..." },
      "theoretical_framework": "...",
      "variables": { "independent": [], "dependent": [], "mediating": [], "moderating": [] },
      "proposed_sample": "...",
      "proposed_analysis": "..."
    }
  }
}
```

---

## Phase 2-4 통합

Phase 1 이후의 워크플로우는 기존과 동일합니다.
단, 프로포절에서 추출된 사전 설정값이 자동으로 반영됩니다:

- **HITL-3 (연구유형 설정)**: 프로포절에서 추출된 유형이 기본값으로 제시
- **Phase 2 (연구설계)**: 프로포절의 방법론/변수가 초기값으로 사용
- **Phase 3 (논문작성)**: 프로포절의 이론적 프레임워크가 서론에 반영

이 사전 설정값들은 사용자가 HITL에서 언제든 변경할 수 있습니다.

---

**버전**: 1.0.0
**작성일**: 2026-01-31
