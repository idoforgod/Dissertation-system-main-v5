---
description: 연구 프로포절을 업로드하여 계획을 추출하고 실행합니다 (Mode F)
allowed-tools: Bash(*), Write(*), Read(*), Task(*)
agent: proposal-analyzer
context: fork
---

# 연구 프로포절 기반 워크플로우 시작

업로드된 프로포절 문서를 분석하여 연구 계획을 추출하고, 기존 계획을 기반으로 체계적 연구를 수행합니다.

## 실행 프로세스

### Step 1: 프로포절 파일 업로드 확인

사용자가 프로포절 파일을 업로드했는지 확인합니다.

**지원 파일 형식**:
- PDF (.pdf)
- Word 문서 (.docx, .doc)
- 텍스트 파일 (.txt)
- Markdown (.md)

**파일 위치 옵션**:
1. 사용자가 Claude Code에 직접 첨부
2. `user-resource/proposals/` 폴더에 저장
3. 파일 경로를 직접 제공

### Step 2: 세션 초기화

```bash
# 세션 디렉토리 생성
python3 .claude/skills/thesis-orchestrator/scripts/init_session.py \
  --mode proposal \
  --proposal-path "$PROPOSAL_PATH" \
  --base-dir thesis-output \
  "[프로포절 제목]"

# 생성되는 구조:
# thesis-output/[프로포절제목-날짜]/
# ├── 00-session/
# │   ├── session.json (mode: proposal)
# │   └── todo-checklist.md
# ├── 00-proposal-analysis/
# │   └── [원본 프로포절 파일]
# └── 01-literature/ (이후 Phase 1 결과물)
```

### Step 3: @proposal-analyzer 실행

프로포절 문서를 파싱하여 구조화된 연구 계획을 추출합니다:

```yaml
analysis_items:
  1_research_questions:
    description: "프로포절에 명시된 연구질문 추출"
    output: "research_questions[]"

  2_hypotheses:
    description: "프로포절에 명시된 가설 추출 (있는 경우)"
    output: "hypotheses[]"

  3_methodology:
    description: "방법론 계획 추출"
    output: "methodology_type, methodology_subtype, methodology_details"

  4_theoretical_framework:
    description: "이론적 프레임워크 추출"
    output: "theoretical_framework"

  5_variables:
    description: "변수 추출 (독립/종속/매개/조절)"
    output: "variables{independent, dependent, mediating, moderating}"

  6_proposed_sample:
    description: "표본 계획 추출"
    output: "proposed_sample"

  7_proposed_analysis:
    description: "분석 전략 추출"
    output: "proposed_analysis"

  8_completeness_assessment:
    description: "완성도 평가 및 누락 항목 리포트"
    output: "completeness_score (0-100), gap_report[]"
```

**출력 파일**: `00-proposal-analysis/proposal-analysis.md`

### Step 4: HITL → /thesis:review-extracted-plan

추출된 계획을 사용자에게 제시하고 확인을 요청합니다:

```
┌─────────────────────────────────────────────────────────────┐
│  📋 프로포절 분석 완료 (HITL)                                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ✅ 완료: 연구 계획 추출                                     │
│                                                              │
│  📊 추출된 내용:                                             │
│  ├─ 연구질문: [N]개 식별                                    │
│  ├─ 가설: [N]개 식별 (또는 "미포함")                        │
│  ├─ 방법론: [유형] ([세부유형])                              │
│  ├─ 이론적 프레임워크: [이름]                               │
│  ├─ 변수: 독립[N], 종속[N], 매개[N], 조절[N]               │
│  └─ 완성도: [점수]/100                                      │
│                                                              │
│  ⚠️  누락 항목: [리스트]                                     │
│                                                              │
│  🎯 다음 단계: 추출 계획 확인 후 Phase 1 진입               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Command**:
```bash
/thesis:review-extracted-plan
```

### Step 5: Phase 1 (Literature Review) 자동 진입

사용자 승인 후, 추출된 계획을 바탕으로 문헌검토가 시작됩니다:

```
승인된 계획 → Phase 1 (15개 전문 에이전트 순차 실행)
  ↓
Wave 1-5 (기존 워크플로우와 동일)
  ↓
HITL-2: 문헌검토 결과 승인
  ↓
⚠️  Flag-and-Follow: 프로포절 계획과 문헌검토 결과 간 모순 확인
```

---

## Mode E vs Mode F 비교

| 항목 | Mode E (Paper Upload) | Mode F (Proposal Upload) |
|------|----------------------|--------------------------|
| 입력 | 남의 논문 (선행연구) | 나의 프로포절 (연구계획서) |
| 목적 | 새로운 가설 도출 | 기존 계획 추출 및 실행 |
| 분석 | 비판적 분석 → 갭 식별 → 가설 생성 | 구조 파싱 → 계획 추출 → 완성도 평가 |
| HITL | 새로운 제안 검토 (review-proposal) | 추출된 계획 확인 (review-extracted-plan) |
| 후속 | Phase 1부터 새로 시작 | Phase 1에서 기존 계획 검증 |
| Flag | 없음 | Flag-and-Follow (모순 감지) |

---

## Quality Assurance

### GRA Compliance
- 프로포절 원문 인용: 페이지/섹션 번호와 함께 인용
- 추출 항목: 원문 대비 정확도 검증
- 누락 항목: 명시적 안내

### pTCS Target
- Claim-level: 70+ (추출 정확도)
- Agent-level: 75+ (전체 분석 신뢰도)

---

## Troubleshooting

| 문제 | 해결 방법 |
|------|----------|
| 프로포절 파일을 찾을 수 없음 | `user-resource/proposals/` 경로 확인 또는 파일 경로 직접 제공 |
| 프로포절이 너무 짧음 (<5 pages) | 초안(draft) 모드로 분석, 누락 항목 상세 리포트 |
| 연구질문이 명확하지 않음 | 추출 불가 항목은 HITL에서 사용자 직접 입력 요청 |
| 영어 프로포절 | 정상 지원 (한국어/영어 모두 가능) |

---

## Integration with Main Workflow

이 커맨드는 **Phase 0의 Mode F**로 작동하며, 이후 워크플로우는 기존과 동일합니다:

```
Mode F (Proposal Upload)
  ↓
HITL (추출된 계획 확인) → /thesis:review-extracted-plan
  ↓
Phase 1 (Literature Review) + Flag-and-Follow
  ↓
HITL-2 (문헌검토 승인)
  ↓
Phase 2-4 (기존과 동일, 사전 설정값 반영)
```

---

$ARGUMENTS
