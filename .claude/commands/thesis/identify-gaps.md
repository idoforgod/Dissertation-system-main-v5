---
name: identify-gaps
description: Stage 2 - 연구 갭 식별. 논문 분석 결과를 바탕으로 5가지 유형의 연구 갭을 식별하고 우선순위를 매깁니다.
agent: gap-identifier
allowed-tools:
  - Read(*)
  - Write(*)
  - Task(*)
model: opus
---

# /thesis:identify-gaps

**Stage 2**: 연구 갭 식별 및 우선순위화

선행연구 분석 결과를 바탕으로 새로운 연구 기회를 식별합니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:identify-gaps --analysis-file stage1-paper-analysis.md
```

### 고급 옵션

```bash
# 특정 갭 유형만 식별
/thesis:identify-gaps --analysis-file <파일> --gap-types "theoretical,methodological"

# 우선순위 매트릭스 포함
/thesis:identify-gaps --analysis-file <파일> --prioritize true

# 출력 경로 지정
/thesis:identify-gaps --analysis-file <파일> --output stage2-gap-analysis.md
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--analysis-file` | Yes | - | Stage 1 분석 결과 파일 경로 |
| `--gap-types` | No | `all` | 식별할 갭 유형: `theoretical`, `methodological`, `contextual`, `practical`, `integration` (쉼표 구분) |
| `--prioritize` | No | `true` | 우선순위 매트릭스 생성 여부 |
| `--min-score` | No | `3.0` | 최소 우선순위 점수 (1-5) |
| `--output` | No | `stage2-gap-analysis.md` | 출력 파일 경로 |

---

## 출력 구조

```
stage2-gap-analysis.md
├─ 1. Identified Gaps
│  ├─ Theoretical Gaps (이론적 갭)
│  ├─ Methodological Gaps (방법론적 갭)
│  ├─ Contextual Gaps (맥락적 갭)
│  ├─ Practical Gaps (실무적 갭)
│  └─ Integration Gaps (통합 갭)
├─ 2. Gap Prioritization Matrix
│  ├─ Importance (학술적/실무적 중요도)
│  ├─ Feasibility (연구 실행 가능성)
│  └─ Novelty (참신성/기여도)
├─ 3. Top 3 Research Opportunities
│  ├─ Opportunity #1 (가장 높은 우선순위)
│  ├─ Opportunity #2
│  └─ Opportunity #3
└─ 4. Rationale & Evidence
   └─ Each gap supported by analysis
```

---

## 5가지 갭 유형

### 1. Theoretical Gap (이론적 갭)
- 기존 이론의 한계
- 이론 간 불일치
- 새로운 이론적 렌즈 필요

### 2. Methodological Gap (방법론적 갭)
- 측정 도구의 한계
- 연구 설계 개선 필요
- 새로운 분석 기법 적용

### 3. Contextual Gap (맥락적 갭)
- 다른 산업/국가/문화
- 다른 시간대 (종단 연구)
- 다른 수준 (개인/팀/조직)

### 4. Practical Gap (실무적 갭)
- 실무 적용 가능성
- 실행 전략 부족
- 실증적 검증 필요

### 5. Integration Gap (통합 갭)
- 여러 이론 통합
- 다학제적 접근
- 혼합연구 방법론

---

## 예시

### Example 1: 표준 갭 식별

```bash
/thesis:identify-gaps --analysis-file stage1-paper-analysis.md
```

**출력**:
```markdown
# Research Gap Analysis

## 1. Identified Gaps

### Theoretical Gaps
**Gap 1.1**: Boundary Conditions Unexplored
- **Description**: The paper assumes transformational leadership universally
  increases innovation, but does not consider when it might be less effective.
- **Evidence**: Authors acknowledge (p. 23): "Future research should examine
  moderating factors..."
- **Opportunity**: Test organizational climate as boundary condition
- **Priority Score**: 4.5/5.0

**Gap 1.2**: Dark Side Not Considered
- **Description**: Only positive effects examined. Potential negative outcomes
  (pressure, burnout) ignored.
- **Evidence**: Unacknowledged limitation
- **Opportunity**: Investigate curvilinear relationship
- **Priority Score**: 3.8/5.0

[... 계속 ...]

## 2. Gap Prioritization Matrix

| Gap ID | Type | Importance | Feasibility | Novelty | Total | Rank |
|--------|------|------------|-------------|---------|-------|------|
| 1.1 | Theoretical | 5 | 4 | 4 | 4.3 | 1 |
| 2.1 | Methodological | 4 | 5 | 3 | 4.0 | 2 |
| 3.1 | Contextual | 4 | 4 | 4 | 4.0 | 3 |
| 1.2 | Theoretical | 4 | 3 | 5 | 4.0 | 4 |
| ... | ... | ... | ... | ... | ... | ... |

## 3. Top 3 Research Opportunities

### 🥇 Opportunity #1: Organizational Climate as Moderator
- **Gap Type**: Theoretical (Boundary Condition)
- **Priority Score**: 4.5/5.0
- **Rationale**: High importance (extends theory), high feasibility (data available),
  moderate novelty (some prior work in related areas)
- **Potential RQ**: "How does organizational climate moderate the relationship
  between transformational leadership and innovation?"

[... 계속 ...]
```

---

## 우선순위 계산 공식

```
Priority Score = (Importance × 0.4) + (Feasibility × 0.3) + (Novelty × 0.3)

where:
- Importance (1-5): 학술적/실무적 중요도
- Feasibility (1-5): 데이터 수집 가능성, 시간/예산
- Novelty (1-5): 기존 연구와 차별성
```

---

## 다음 단계

```bash
# Stage 3로 진행 (가설 생성)
/thesis:generate-hypotheses --gap-file stage2-gap-analysis.md

# 또는 전체 워크플로우 재개
/thesis:run-paper-upload --resume-from stage3
```

---

## 관련 커맨드

- `/thesis:analyze-paper` - Stage 1 실행
- `/thesis:generate-hypotheses` - Stage 3 실행
- `/thesis:status` - 진행 상태 확인

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**에이전트**: gap-identifier (Opus)
