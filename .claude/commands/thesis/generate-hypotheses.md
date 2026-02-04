---
name: generate-hypotheses
description: Stage 3 - 가설 생성 및 평가. 식별된 연구 갭을 바탕으로 검증 가능한 가설을 개발하고 CTOSF 기준으로 평가합니다.
agent: hypothesis-generator
allowed-tools:
  - Read(*)
  - Write(*)
  - Task(*)
model: opus
---

# /thesis:generate-hypotheses

**Stage 3**: 가설 개발 및 품질 평가

연구 갭을 바탕으로 체계적 가설을 생성하고 CTOSF 기준으로 평가합니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:generate-hypotheses --gap-file stage2-gap-analysis.md
```

### 고급 옵션

```bash
# 가설 개수 지정
/thesis:generate-hypotheses --gap-file <파일> --num-hypotheses 5

# 가설 유형 지정
/thesis:generate-hypotheses --gap-file <파일> --types "direct,mediation,moderation"

# 최소 품질 기준
/thesis:generate-hypotheses --gap-file <파일> --min-quality 3.5

# 출력 경로
/thesis:generate-hypotheses --gap-file <파일> --output stage3-hypotheses.md
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--gap-file` | Yes | - | Stage 2 갭 분석 파일 경로 |
| `--num-hypotheses` | No | `3-8` | 생성할 가설 개수 (우선순위 높은 갭 기반) |
| `--types` | No | `all` | 가설 유형: `direct`, `mediation`, `moderation`, `complex` (쉼표 구분) |
| `--min-quality` | No | `3.0` | 최소 CTOSF 점수 (1-5) |
| `--include-alternatives` | No | `true` | 대안 가설 포함 여부 |
| `--output` | No | `stage3-hypotheses.md` | 출력 파일 경로 |

---

## 출력 구조

```
stage3-hypotheses.md
├─ 1. Hypotheses Overview
│  ├─ Total hypotheses: 5
│  ├─ Average CTOSF: 4.2/5.0
│  └─ Distribution by type
├─ 2. Main Hypotheses
│  ├─ H1: Direct Effect
│  ├─ H2: Direct Effect
│  ├─ H3: Mediation
│  ├─ H4: Moderation
│  └─ H5: Complex Model
├─ 3. Hypothesis Details (각 가설마다)
│  ├─ Formal Statement
│  ├─ Variables (IV, DV, M, Z)
│  ├─ Theoretical Rationale
│  ├─ Empirical Evidence
│  ├─ CTOSF Evaluation
│  │  ├─ Clarity: 5/5
│  │  ├─ Testability: 4/5
│  │  ├─ Originality: 4/5
│  │  ├─ Significance: 5/5
│  │  └─ Feasibility: 4/5
│  └─ Operationalization Plan
├─ 4. Conceptual Model
│  └─ Visual diagram of variable relationships
└─ 5. Alternative Hypotheses
   └─ Competing explanations
```

---

## CTOSF 평가 기준

### C - Clarity (명확성)
- 변수가 명확히 정의되었는가?
- 관계의 방향이 명시되었는가?
- 모호한 용어가 없는가?

### T - Testability (검증가능성)
- 변수가 측정 가능한가?
- 분석 방법이 존재하는가?
- 데이터 수집이 가능한가?

### O - Originality (독창성)
- 새로운 변수/관계인가?
- 새로운 맥락인가?
- 이론적 확장인가?

### S - Significance (중요성)
- 이론적 기여가 있는가?
- 실무적 시사점이 있는가?
- 학술지 게재 가능성이 있는가?

### F - Feasibility (실행가능성)
- 자원이 확보 가능한가?
- 시간이 적절한가?
- 윤리적 문제가 없는가?

---

## 가설 유형

### Direct Effect (직접 효과)
```
H: X → Y
Example: "Transformational leadership will positively affect employee creativity"
```

### Mediation (매개)
```
H: X → M → Y
Example: "Intrinsic motivation will mediate the relationship between
transformational leadership and employee creativity"
```

### Moderation (조절)
```
H: X × Z → Y
Example: "Organizational climate will moderate the relationship between
transformational leadership and creativity, such that the relationship
is stronger in innovative climates"
```

### Complex Model (복합 모델)
```
H: X → M → Y, moderated by Z
Example: Moderated mediation, mediated moderation, serial mediation
```

---

## 예시

### Example 1: 표준 가설 생성

```bash
/thesis:generate-hypotheses --gap-file stage2-gap-analysis.md
```

**출력**:
```markdown
# Research Hypotheses

## 1. Hypotheses Overview
- **Total Hypotheses**: 5
- **Average CTOSF Score**: 4.2/5.0
- **Distribution**:
  - Direct Effect: 2
  - Mediation: 2
  - Moderation: 1

## 2. Main Hypotheses

### H1: Direct Effect (TL → Creativity)
**Statement**: "Transformational leadership will positively affect employee creativity."

**CTOSF Evaluation**:
- Clarity: ⭐⭐⭐⭐⭐ (5/5) - Variables clearly defined
- Testability: ⭐⭐⭐⭐⭐ (5/5) - Validated scales available
- Originality: ⭐⭐⭐ (3/5) - Replication in new context
- Significance: ⭐⭐⭐⭐ (4/5) - Important relationship
- Feasibility: ⭐⭐⭐⭐⭐ (5/5) - Survey data easily collected
- **Total: 4.4/5.0** ✅ PASS

**Theoretical Rationale**:
According to Transformational Leadership Theory (Bass, 1985), leaders
who inspire and intellectually stimulate employees enhance their creative
problem-solving abilities...

[... 계속 ...]

### H3: Mediation (TL → IM → Creativity)
**Statement**: "Intrinsic motivation will mediate the relationship between
transformational leadership and employee creativity."

**Variables**:
- IV: Transformational Leadership (MLQ-20)
- Mediator: Intrinsic Motivation (WPI-6)
- DV: Employee Creativity (TCDS-10)

**Mediation Model**:
```
Path a: TL → IM (β = ?)
Path b: IM → Creativity (β = ?)
Indirect effect: a × b
```

**CTOSF Evaluation**:
- Clarity: ⭐⭐⭐⭐⭐ (5/5)
- Testability: ⭐⭐⭐⭐ (4/5) - Requires PROCESS Model 4
- Originality: ⭐⭐⭐⭐ (4/5) - New mediator
- Significance: ⭐⭐⭐⭐⭐ (5/5) - Explains mechanism
- Feasibility: ⭐⭐⭐⭐ (4/5) - Additional scale needed
- **Total: 4.4/5.0** ✅ PASS

[... 계속 ...]

## 4. Conceptual Model

```
                  Organizational Climate (Z)
                            ↓ (moderates)
Transformational    →    Employee
Leadership (X)           Creativity (Y)
      ↓
   Intrinsic
  Motivation (M)
```

## 5. Alternative Hypotheses

### Alternative H1
**Statement**: "The relationship between transformational leadership and
creativity is curvilinear (inverted U-shape)."

**Rationale**: Too much inspirational motivation may create pressure...
```

---

## 품질 기준

가설은 다음 기준을 만족해야 합니다:

| Criterion | Minimum | Target | Excellent |
|-----------|---------|--------|-----------|
| CTOSF Total | 3.0 | 4.0 | 4.5 |
| Clarity | 4.0 | 5.0 | 5.0 |
| Testability | 3.0 | 4.0 | 5.0 |

**자동 필터링**: `--min-quality 3.5` 미만 가설은 제외됩니다.

---

## 다음 단계

```bash
# Stage 4로 진행 (연구 설계)
/thesis:propose-design --hypotheses-file stage3-hypotheses.md

# 또는 전체 워크플로우 재개
/thesis:run-paper-upload --resume-from stage4
```

---

## 관련 커맨드

- `/thesis:identify-gaps` - Stage 2 실행
- `/thesis:propose-design` - Stage 4 실행
- `/thesis:status` - 진행 상태 확인

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**에이전트**: hypothesis-generator (Opus)
