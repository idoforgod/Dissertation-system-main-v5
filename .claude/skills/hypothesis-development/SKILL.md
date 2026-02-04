---
name: hypothesis-development
description: 연구 가설 개발을 위한 체계적 프레임워크. 가설 템플릿, 품질 평가 기준, 이론적 정당화 가이드를 제공합니다.
---

# Hypothesis Development Skill

**목적**: 과학적 가설 개발을 위한 템플릿 및 평가 도구

이 Skill은 hypothesis-generator agent 및 연구 설계 작업에서 사용됩니다.

---

## 주요 기능

### 1. 가설 템플릿 (Hypothesis Templates)

#### Template 1: Direct Effect (직접 효과)

```yaml
direct_effect_template:
  hypothesis_statement:
    english: "[IV] will positively/negatively affect [DV]"
    korean: "[IV]는 [DV]를 증가/감소시킬 것이다"

  structure:
    independent_variable: ""
    dependent_variable: ""
    direction: "positive | negative"
    relationship_type: "causal | correlational"

  example:
    IV: "Transformational leadership"
    DV: "Employee creativity"
    H: "Transformational leadership will positively affect employee creativity"
```

#### Template 2: Mediation (매개)

```yaml
mediation_template:
  hypothesis_statement:
    english: "[Mediator] will mediate the relationship between [IV] and [DV]"
    korean: "[M]은 [IV]와 [DV]의 관계를 매개할 것이다"

  structure:
    independent_variable: ""
    mediator: ""
    dependent_variable: ""
    paths:
      path_a: "IV → M"
      path_b: "M → DV"
      indirect_effect: "a × b"

  example:
    IV: "Transformational leadership"
    M: "Intrinsic motivation"
    DV: "Employee creativity"
    H: "Intrinsic motivation will mediate the relationship between transformational leadership and employee creativity"
```

#### Template 3: Moderation (조절)

```yaml
moderation_template:
  hypothesis_statement:
    english: "[Moderator] will moderate the relationship between [IV] and [DV], such that the relationship is stronger when [Moderator] is high"
    korean: "[Z]는 [IV]와 [DV]의 관계를 조절할 것이며, [Z]가 높을 때 관계가 더 강할 것이다"

  structure:
    independent_variable: ""
    moderator: ""
    dependent_variable: ""
    interaction_direction: "amplify | dampen"

  example:
    IV: "Transformational leadership"
    Z: "Organizational climate"
    DV: "Employee creativity"
    H: "Organizational climate will moderate the TL-creativity relationship, such that the relationship is stronger in innovative climates"
```

---

### 2. 품질 평가 기준 (Quality Criteria)

**CTOSF Framework**:

```yaml
quality_criteria:
  C_larity:
    description: "명확하고 구체적한가?"
    checklist:
      - "변수가 명확히 정의되었는가?"
      - "관계의 방향이 명시되었는가?"
      - "모호한 용어가 없는가?"
    scoring: 0-5

  T_estability:
    description: "실증적으로 검증 가능한가?"
    checklist:
      - "변수가 측정 가능한가?"
      - "분석 방법이 존재하는가?"
      - "데이터 수집이 가능한가?"
    scoring: 0-5

  O_riginality:
    description: "기존 연구와 차별화되는가?"
    checklist:
      - "새로운 변수/관계인가?"
      - "새로운 맥락인가?"
      - "이론적 확장인가?"
    scoring: 0-5

  S_ignificance:
    description: "학술적/실무적으로 중요한가?"
    checklist:
      - "이론적 기여가 있는가?"
      - "실무적 시사점이 있는가?"
      - "학술지 게재 가능성이 있는가?"
    scoring: 0-5

  F_easibility:
    description: "현실적으로 수행 가능한가?"
    checklist:
      - "자원이 확보 가능한가?"
      - "시간이 적절한가?"
      - "윤리적 문제가 없는가?"
    scoring: 0-5

total_score: "평균 (C+T+O+S+F) / 5"
quality_rating:
  excellent: "≥ 4.0"
  good: "3.0-3.9"
  acceptable: "2.0-2.9"
  poor: "< 2.0"
```

---

### 3. 가설 평가 함수 (Evaluation Functions)

```python
def evaluate_hypothesis(hypothesis):
    """
    Evaluate hypothesis quality using CTOSF criteria

    Returns:
        dict: Scores for each criterion and overall rating
    """
    scores = {
        "clarity": assess_clarity(hypothesis),
        "testability": assess_testability(hypothesis),
        "originality": assess_originality(hypothesis),
        "significance": assess_significance(hypothesis),
        "feasibility": assess_feasibility(hypothesis)
    }

    total = sum(scores.values()) / len(scores)

    return {
        "scores": scores,
        "total": total,
        "rating": get_rating(total)
    }

def get_rating(score):
    if score >= 4.0:
        return "excellent"
    elif score >= 3.0:
        return "good"
    elif score >= 2.0:
        return "acceptable"
    else:
        return "poor"
```

---

### 4. 이론적 정당화 가이드 (Theoretical Justification Guide)

```yaml
justification_framework:
  step_1_identify_theory:
    question: "어떤 이론이 이 가설을 지지하는가?"
    examples:
      - "Social Exchange Theory"
      - "Self-Determination Theory"
      - "Transformational Leadership Theory"

  step_2_explain_mechanism:
    question: "이론적으로 왜 X가 Y에 영향을 미치는가?"
    template: "According to [Theory], [IV] affects [DV] because [mechanism]"

  step_3_cite_evidence:
    question: "이전 연구가 이를 지지하는가?"
    template: "Previous research (Citation) found that [evidence]"

  step_4_identify_novelty:
    question: "이 가설이 기존 연구와 어떻게 다른가?"
    options:
      - "New variable"
      - "New relationship"
      - "New context"
      - "Theory integration"
```

---

## 템플릿 파일 (Template Files)

### causal-hypothesis.yaml

**파일**: `templates/causal-hypothesis.yaml`

```yaml
causal_hypothesis:
  type: "direct_effect"

  hypothesis_statement:
    english: "[IV] will [positively/negatively] affect [DV]"
    korean: "[IV]는 [DV]를 [증가/감소]시킬 것이다"

  variables:
    independent_variable:
      name: ""
      measurement: ""
      source: ""

    dependent_variable:
      name: ""
      measurement: ""
      source: ""

    control_variables: []

  theoretical_rationale:
    theory_1:
      name: ""
      citation: ""
      explanation: ""

    theory_2:
      name: ""
      citation: ""
      explanation: ""

  empirical_evidence:
    - citation: ""
      finding: ""
      relevance: ""

  originality_claim:
    what_is_new: ""
    why_important: ""
    expected_contribution: ""

  operationalization:
    IV:
      scale: ""
      items: 0
      reliability: ""

    DV:
      scale: ""
      items: 0
      reliability: ""

  feasibility:
    data_availability: 0  # 1-5 scale
    ethical_considerations: ""
    resource_requirements: ""
    estimated_timeline: ""

  expected_results:
    if_supported: ""
    if_not_supported: ""
```

---

### mediation-hypothesis.yaml

**파일**: `templates/mediation-hypothesis.yaml`

```yaml
mediation_hypothesis:
  type: "mediation"

  hypothesis_statement:
    english: "[Mediator] will mediate the relationship between [IV] and [DV]"
    korean: "[M]은 [IV]와 [DV]의 관계를 매개할 것이다"

  mediation_model:
    paths:
      path_a:
        from: "IV"
        to: "Mediator"
        theoretical_basis: ""

      path_b:
        from: "Mediator"
        to: "DV"
        theoretical_basis: ""

      indirect_effect:
        formula: "a × b"
        expected_sign: "positive | negative"

  why_mediation:
    rationale: ""
    mechanism_explanation: ""

  variables:
    independent_variable: {}
    mediator: {}
    dependent_variable: {}
    controls: []

  theoretical_rationale:
    path_a_theory: {}
    path_b_theory: {}
    mediation_rationale: ""

  analysis_plan:
    method: "Hayes PROCESS Model 4"
    bootstrap_samples: 5000
    confidence_interval: 95

  feasibility: {}
```

---

### moderation-hypothesis.yaml

**파일**: `templates/moderation-hypothesis.yaml`

```yaml
moderation_hypothesis:
  type: "moderation"

  hypothesis_statement:
    english: "[Moderator] will moderate the relationship between [IV] and [DV], such that the relationship is stronger/weaker when [Moderator] is high/low"
    korean: "[Z]는 [IV]와 [DV]의 관계를 조절할 것이며, [Z]가 높을/낮을 때 관계가 더 강할/약할 것이다"

  moderation_model:
    interaction_term: "IV × Moderator"
    expected_pattern: "amplify | dampen | reverse"

  theoretical_rationale:
    boundary_condition_theory: ""
    when_high: ""
    when_low: ""

  variables:
    independent_variable: {}
    moderator: {}
    dependent_variable: {}
    interaction_term: {}
    controls: []

  analysis_plan:
    method: "Hierarchical multiple regression"
    steps:
      step_1: "Controls"
      step_2: "Main effects (IV, Moderator)"
      step_3: "Interaction (IV × Moderator)"
    probing: "Simple slope analysis at +1 SD, Mean, -1 SD"

  expected_results:
    simple_slope_high: ""
    simple_slope_low: ""
    interaction_plot: "Description of expected pattern"

  feasibility: {}
```

---

## 사용 예시 (Usage Examples)

### Example 1: 가설 생성 및 평가

```python
from skills.hypothesis_development import load_template, evaluate_hypothesis

# 1. 템플릿 로드
template = load_template("causal-hypothesis.yaml")

# 2. 가설 작성
hypothesis = template.copy()
hypothesis['variables']['independent_variable']['name'] = "Transformational Leadership"
hypothesis['variables']['dependent_variable']['name'] = "Employee Creativity"
hypothesis['hypothesis_statement']['english'] = "Transformational leadership will positively affect employee creativity"

# 3. 품질 평가
evaluation = evaluate_hypothesis(hypothesis)

print(f"Clarity: {evaluation['scores']['clarity']}")
print(f"Testability: {evaluation['scores']['testability']}")
print(f"Overall: {evaluation['total']} ({evaluation['rating']})")
```

### Example 2: 배치 평가

```python
# 여러 가설을 평가하고 우선순위화
hypotheses = [H1, H2, H3, H4, H5]

evaluations = []
for h in hypotheses:
    eval_result = evaluate_hypothesis(h)
    evaluations.append({
        "hypothesis": h['hypothesis_statement']['english'],
        "score": eval_result['total'],
        "rating": eval_result['rating']
    })

# 점수순 정렬
evaluations.sort(key=lambda x: x['score'], reverse=True)

# Top 3 추천
print("Top 3 Recommended Hypotheses:")
for i, e in enumerate(evaluations[:3], 1):
    print(f"{i}. {e['hypothesis']} (Score: {e['score']:.2f})")
```

---

## 사용하는 Agents

이 Skill을 사용하는 agents:
- `hypothesis-generator` (Stage 3)
- `gap-identifier` (Stage 2)
- `research-model-developer` (Phase 2)

---

## 버전 히스토리

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-28 | Initial release |

---

**작성자**: Claude Code
**상태**: ✅ Ready for use
