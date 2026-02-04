---
name: research-design-templates
description: 양적/질적/혼합연구 설계를 위한 템플릿 모음. 연구 설계 유형별 구조화된 템플릿과 체크리스트를 제공합니다.
---

# Research Design Templates Skill

**목적**: 체계적인 연구 설계를 위한 템플릿 및 가이드

이 Skill은 design-proposer agent 및 연구 설계 작업에서 사용됩니다.

---

## 주요 기능

### 1. 양적연구 템플릿 (Quantitative Research Templates)

#### Template 1: Experimental Design (실험 설계)

```yaml
experimental_design_template:
  research_type: "Experimental"

  design_structure:
    type: "Between-subjects | Within-subjects | Mixed"
    independent_variables:
      - name: ""
        levels: []
        manipulation: ""
    dependent_variables:
      - name: ""
        measurement: ""
        scale: ""
    control_variables: []

  participants:
    target_population: ""
    sampling_method: "Random assignment"
    sample_size:
      power_analysis:
        effect_size: "Cohen's d = 0.5 (medium)"
        alpha: 0.05
        power: 0.80
        required_n: ""
    inclusion_criteria: []
    exclusion_criteria: []

  procedure:
    randomization: "Random assignment to conditions"
    manipulation_check: ""
    experimental_task: ""
    duration: ""

  data_collection:
    instruments: []
    timing: ""
    setting: "Lab | Field | Online"

  analysis_plan:
    primary_analysis: "ANOVA | ANCOVA | Regression"
    post_hoc_tests: []
    assumptions_tests:
      - "Normality (Shapiro-Wilk)"
      - "Homogeneity of variance (Levene's test)"
      - "Independence"
    software: "SPSS | R | Python"

  validity_threats:
    internal_validity: []
    external_validity: []
    construct_validity: []
    statistical_conclusion_validity: []

  ethical_considerations:
    informed_consent: true
    deception: false
    debriefing: true
    irb_approval: "Required"
```

#### Template 2: Survey Design (서베이 설계)

```yaml
survey_design_template:
  research_type: "Cross-sectional Survey | Longitudinal Survey"

  survey_structure:
    constructs:
      - name: ""
        definition: ""
        dimensions: []
    measurement_model:
      type: "Reflective | Formative"
      scales: []

  sampling:
    population: ""
    sampling_frame: ""
    sampling_method: "Probability | Non-probability"
    sample_size:
      target_n: ""
      expected_response_rate: "30-40%"
      minimum_n: ""
      rationale: "SEM requires 200+ | Regression requires 15*predictors"

  questionnaire_design:
    sections:
      - name: "Demographics"
        items: []
      - name: "Main Constructs"
        items: []
    scale_type: "Likert 5-point | Likert 7-point"
    reverse_coded_items: []

  data_collection:
    method: "Online (Qualtrics) | Paper-based | Mixed"
    pilot_test:
      n: "30-50"
      purpose: "Test clarity, reliability"
    main_survey:
      duration: "2-4 weeks"
      reminders: "2 reminders at Week 1, 2"

  quality_checks:
    attention_checks: []
    response_time_filter: ""
    straight_lining_detection: true

  analysis_plan:
    preliminary_analysis:
      - "Missing data analysis (Little's MCAR test)"
      - "Outlier detection (Mahalanobis distance)"
      - "Common method bias (Harman's single factor test)"
    measurement_model:
      - "CFA (Confirmatory Factor Analysis)"
      - "Reliability: Cronbach's α, CR"
      - "Validity: AVE, discriminant validity"
    structural_model:
      - "Path analysis | SEM"
      - "Mediation analysis (Hayes PROCESS)"
      - "Moderation analysis (Interaction terms)"
    software: "AMOS | MPlus | lavaan (R)"

  reporting_standards:
    follow: "APA 7th | JARS-Quant"
    include:
      - "Response rate"
      - "Sample characteristics table"
      - "Measurement model fit indices"
      - "Correlation matrix with α on diagonal"
```

---

### 2. 질적연구 템플릿 (Qualitative Research Templates)

#### Template 1: Phenomenological Study (현상학적 연구)

```yaml
phenomenological_study_template:
  research_type: "Phenomenology"
  philosophical_approach: "Descriptive | Interpretive (Hermeneutic)"

  research_question:
    focus: "Lived experience of [phenomenon]"
    example: "What is the lived experience of remote workers during COVID-19?"

  participants:
    sampling: "Purposive sampling"
    criteria:
      - "Direct experience with phenomenon"
      - "Able to articulate experience"
      - "Willing to participate"
    target_n: "10-15 (saturation)"

  data_collection:
    method: "In-depth interviews"
    interview_protocol:
      opening: "Tell me about your experience with..."
      main_questions: []
      probes: ["Can you tell me more?", "What did that mean to you?"]
    duration: "60-90 minutes"
    recording: "Audio + Transcription"

  data_analysis:
    approach: "Colaizzi | Van Kaam | Moustakas"
    steps:
      - "Read transcripts multiple times"
      - "Extract significant statements"
      - "Formulate meanings"
      - "Cluster themes"
      - "Write textural description"
      - "Write structural description"
      - "Synthesize essence"
    software: "NVivo | Atlas.ti | Manual"

  trustworthiness:
    credibility:
      - "Member checking"
      - "Triangulation (multiple interviews)"
    transferability:
      - "Thick description"
      - "Rich quotes"
    dependability:
      - "Audit trail"
      - "Reflexive journal"
    confirmability:
      - "Bracketing (epoché)"
      - "Peer debriefing"

  ethical_considerations:
    confidentiality: "Pseudonyms, de-identification"
    emotional_safety: "Sensitive topics, debriefing"
    power_dynamics: "Voluntary participation"
```

#### Template 2: Grounded Theory (근거이론)

```yaml
grounded_theory_template:
  research_type: "Grounded Theory"
  approach: "Glaserian | Straussian | Constructivist (Charmaz)"

  research_question:
    focus: "Process | Social phenomenon"
    example: "How do organizations adapt to digital transformation?"

  sampling:
    initial_sampling: "Purposive sampling"
    theoretical_sampling: "Emerging concepts guide next participants"
    saturation: "When no new codes emerge"
    target_n: "20-30"

  data_collection:
    methods:
      - "Interviews (semi-structured)"
      - "Observations"
      - "Documents"
    concurrent_analysis: "Analyze while collecting"

  coding_process:
    open_coding:
      description: "Line-by-line coding, identify concepts"
      output: "100+ initial codes"
    axial_coding:
      description: "Link categories, identify relationships"
      paradigm_model: "Conditions → Actions/Interactions → Consequences"
    selective_coding:
      description: "Identify core category, integrate theory"
      output: "Theoretical model"

  constant_comparison:
    compare_within: "Within same interview"
    compare_across: "Across different interviews"
    compare_to_literature: "After theory emerges"

  memo_writing:
    types:
      - "Code memos (define codes)"
      - "Theoretical memos (emerging theory)"
      - "Operational memos (research decisions)"
    frequency: "Throughout analysis"

  theory_development:
    core_category: ""
    theoretical_propositions: []
    visual_model: "Process diagram"

  quality_criteria:
    fit: "Theory fits data"
    work: "Theory explains process"
    relevance: "Theory matters to field"
    modifiability: "Theory can evolve"
```

#### Template 3: Case Study (사례연구)

```yaml
case_study_template:
  research_type: "Case Study"
  design: "Single-case | Multiple-case"
  purpose: "Exploratory | Descriptive | Explanatory"

  case_selection:
    unit_of_analysis: "Individual | Organization | Project | Event"
    rationale:
      - "Critical case"
      - "Unique case"
      - "Revelatory case"
      - "Typical case"
    boundaries:
      temporal: "Time period"
      spatial: "Location"
      contextual: "Specific context"

  data_sources:
    triangulation:
      - source: "Interviews"
        n: ""
      - source: "Documents"
        types: []
      - source: "Observations"
        setting: ""
      - source: "Archival records"
        types: []

  data_collection_protocol:
    questions_by_source: []
    procedures: ""
    case_study_database: "Organized repository"

  analysis_strategy:
    approach: "Pattern matching | Explanation building | Time-series"
    within_case_analysis:
      - "Chronology"
      - "Themes"
      - "Patterns"
    cross_case_analysis:
      - "Variable-oriented"
      - "Case-oriented"
    rival_explanations: []

  reporting:
    structure: "Linear | Comparative | Chronological | Suspense"
    narrative_style: "Descriptive | Analytical"
    case_description:
      - "Context"
      - "Key events"
      - "Outcomes"
    theoretical_propositions: []

  quality_assurance:
    construct_validity:
      - "Multiple sources"
      - "Chain of evidence"
      - "Key informant review"
    internal_validity:
      - "Pattern matching"
      - "Rival explanations"
    external_validity:
      - "Replication logic"
      - "Analytical generalization"
    reliability:
      - "Case study protocol"
      - "Case study database"
```

---

### 3. 혼합연구 템플릿 (Mixed Methods Templates)

#### Template 1: Explanatory Sequential Design (설명적 순차 설계)

```yaml
explanatory_sequential_template:
  research_type: "Mixed Methods - Explanatory Sequential"
  notation: "QUANT → qual"

  rationale:
    purpose: "Quantitative results need explanation or elaboration"
    example: "Survey finds unexpected relationship → interviews explain why"

  phase_1_quantitative:
    design: "Survey | Experiment"
    sample_size: "Large (200+)"
    analysis: "Statistical analysis"
    output: "Significant findings needing explanation"

  connecting_phase:
    participant_selection:
      strategy: "Extreme case | Maximum variation | Typical case"
      criteria: "Based on Phase 1 results"
      n: "15-30"
    interview_protocol:
      based_on: "Phase 1 findings"
      focus: "Explain unexpected/significant results"

  phase_2_qualitative:
    design: "Interviews | Focus groups"
    purpose: "Explain Phase 1 results"
    analysis: "Thematic analysis"
    output: "Rich explanations"

  integration:
    where: "Interpretation stage"
    how:
      - "Compare/contrast findings"
      - "Qual explains Quant"
      - "Develop joint display"
    joint_display_example:
      columns: ["Quant Finding", "Qual Theme", "Interpretation"]

  reporting:
    structure:
      - "Phase 1 Results (Quant)"
      - "Phase 2 Results (Qual)"
      - "Integration Discussion"
    visual: "Two-phase flowchart"

  validity:
    integration_quality:
      - "Clear connection between phases"
      - "Qual adequately explains Quant"
      - "Contradictions addressed"
```

#### Template 2: Exploratory Sequential Design (탐색적 순차 설계)

```yaml
exploratory_sequential_template:
  research_type: "Mixed Methods - Exploratory Sequential"
  notation: "qual → QUANT"

  rationale:
    purpose: "Need to explore before measuring"
    example: "Interviews identify new constructs → survey tests them"

  phase_1_qualitative:
    design: "Interviews | Focus groups | Grounded theory"
    sample_size: "15-30"
    analysis: "Thematic analysis | Grounded theory"
    output: "Themes, constructs, or variables"

  instrument_development:
    based_on: "Phase 1 themes"
    process:
      - "Generate items from quotes"
      - "Expert review"
      - "Cognitive interviews"
      - "Pilot test"
    output: "New survey instrument"

  phase_2_quantitative:
    design: "Survey with new instrument"
    sample_size: "Large (300+)"
    analysis: "EFA, CFA, SEM"
    purpose: "Test/generalize Phase 1 findings"

  integration:
    where: "Instrument development + interpretation"
    how:
      - "Qual informs Quant instrument"
      - "Quant generalizes Qual findings"
      - "Joint display showing emergence to testing"

  reporting:
    structure:
      - "Phase 1 Results (Qual) + Instrument Development"
      - "Phase 2 Results (Quant)"
      - "Integration Discussion"
    emphasize: "How Qual led to Quant"
```

#### Template 3: Convergent Parallel Design (수렴적 병렬 설계)

```yaml
convergent_parallel_template:
  research_type: "Mixed Methods - Convergent Parallel"
  notation: "QUANT + QUAL"

  rationale:
    purpose: "Compare, validate, or corroborate findings"
    example: "Collect survey and interview data simultaneously to triangulate"

  quantitative_strand:
    design: "Survey"
    sample: "n = 200+"
    timing: "Concurrent with qualitative"

  qualitative_strand:
    design: "Interviews"
    sample: "n = 20-30"
    timing: "Concurrent with quantitative"

  sampling:
    approach: "Same population, different samples | Same participants"
    rationale: ""

  integration:
    where: "Analysis and interpretation"
    strategies:
      - "Data transformation (qual → counts)"
      - "Side-by-side comparison"
      - "Joint display matrix"
    joint_display_example:
      format: "Theme + Stat + Meta-inference"

  handling_discrepancies:
    if_convergent: "Findings reinforce each other"
    if_divergent:
      - "Explore why they differ"
      - "Consider contextual factors"
      - "May lead to new insights"

  reporting:
    structure:
      - "Quant Results"
      - "Qual Results"
      - "Integration (Joint Display)"
      - "Meta-inferences"
    emphasize: "Convergence and divergence"
```

---

## 템플릿 선택 가이드 (Template Selection Guide)

### Decision Tree

```yaml
template_selection:
  step_1_paradigm:
    question: "연구의 근본적 목적은?"
    options:
      test_hypothesis: → Quantitative
      explore_phenomenon: → Qualitative
      both: → Mixed Methods

  step_2_quantitative:
    question: "관계의 성격은?"
    options:
      causal: → Experimental Design
      correlational: → Survey Design

  step_3_qualitative:
    question: "연구 초점은?"
    options:
      lived_experience: → Phenomenology
      social_process: → Grounded Theory
      bounded_system: → Case Study

  step_4_mixed:
    question: "통합 시점은?"
    options:
      need_explanation: → Explanatory Sequential (QUANT → qual)
      need_exploration: → Exploratory Sequential (qual → QUANT)
      need_triangulation: → Convergent Parallel (QUANT + QUAL)
```

---

## 표본설계 가이드 (Sampling Design Guide)

### Power Analysis Calculator (양적연구)

```python
def calculate_sample_size(effect_size="medium", alpha=0.05, power=0.80, test_type="t-test"):
    """
    Calculate required sample size for statistical power

    Args:
        effect_size: "small" (0.2) | "medium" (0.5) | "large" (0.8)
        alpha: Type I error rate (default 0.05)
        power: Statistical power (default 0.80)
        test_type: "t-test" | "ANOVA" | "regression" | "correlation"

    Returns:
        dict: Required sample size and parameters
    """

    effect_sizes = {
        "small": 0.2,
        "medium": 0.5,
        "large": 0.8
    }

    d = effect_sizes[effect_size]

    if test_type == "t-test":
        # Cohen's formula for independent t-test
        n_per_group = 16 * (1/d**2)
        total_n = n_per_group * 2

    elif test_type == "ANOVA":
        # f = 0.25 (medium), k groups
        k = 3  # default 3 groups
        n_per_group = 52  # approximate
        total_n = n_per_group * k

    elif test_type == "regression":
        # Multiple regression
        predictors = 5  # default
        total_n = 15 * predictors  # rule of thumb

    return {
        "test_type": test_type,
        "effect_size": f"{effect_size} (d={d})",
        "alpha": alpha,
        "power": power,
        "required_n": int(total_n),
        "recommendation": f"Collect at least {int(total_n * 1.2)} to account for 20% dropout"
    }
```

### Saturation Calculator (질적연구)

```python
def estimate_saturation_point(research_design):
    """
    Estimate sample size for qualitative saturation

    Args:
        research_design: "phenomenology" | "grounded_theory" | "case_study"

    Returns:
        dict: Recommended sample size range
    """

    guidelines = {
        "phenomenology": {
            "min": 10,
            "typical": 15,
            "max": 20,
            "rationale": "Homogeneous experience group"
        },
        "grounded_theory": {
            "min": 20,
            "typical": 30,
            "max": 40,
            "rationale": "Theoretical saturation, diverse perspectives"
        },
        "case_study": {
            "min": 1,
            "typical": 3,
            "max": 5,
            "rationale": "In-depth understanding, replication logic"
        },
        "interviews_general": {
            "min": 12,
            "typical": 20,
            "max": 30,
            "rationale": "Guest et al. (2006) saturation study"
        }
    }

    return guidelines.get(research_design, guidelines["interviews_general"])
```

---

## 측정도구 선택 가이드 (Measurement Instruments)

### Validated Scales Database

```yaml
validated_scales:
  organizational_behavior:
    - construct: "Transformational Leadership"
      scale: "MLQ (Multifactor Leadership Questionnaire)"
      items: 20
      reliability: "α = 0.89-0.92"
      citation: "Bass & Avolio (1995)"

    - construct: "Job Satisfaction"
      scale: "MSQ (Minnesota Satisfaction Questionnaire)"
      items: 20 (short form)
      reliability: "α = 0.87"
      citation: "Weiss et al. (1967)"

    - construct: "Organizational Commitment"
      scale: "OCQ (Organizational Commitment Questionnaire)"
      items: 15
      reliability: "α = 0.90"
      citation: "Mowday, Steers, & Porter (1979)"

  psychology:
    - construct: "Self-Efficacy"
      scale: "GSE (General Self-Efficacy Scale)"
      items: 10
      reliability: "α = 0.76-0.90"
      citation: "Schwarzer & Jerusalem (1995)"

    - construct: "Depression"
      scale: "BDI-II (Beck Depression Inventory)"
      items: 21
      reliability: "α = 0.92"
      citation: "Beck et al. (1996)"
```

---

## 사용 예시 (Usage Examples)

### Example 1: 양적연구 설계 생성

```python
from skills.research_design_templates import load_template

# 1. 템플릿 로드
survey_template = load_template("survey-design.yaml")

# 2. 연구에 맞게 커스터마이즈
study_design = survey_template.copy()
study_design['constructs'] = [
    {"name": "Leadership", "scale": "MLQ"},
    {"name": "Creativity", "scale": "TCDS"}
]
study_design['sampling']['target_n'] = calculate_sample_size(
    effect_size="medium",
    test_type="regression"
)

# 3. 출력
write_design("research-design.md", study_design)
```

### Example 2: 혼합연구 설계 생성

```python
# 1. 혼합연구 전략 선택
if need_explanation_of_quant_results:
    template = load_template("explanatory-sequential.yaml")
elif need_to_develop_instrument:
    template = load_template("exploratory-sequential.yaml")
else:
    template = load_template("convergent-parallel.yaml")

# 2. 각 Phase 설계
design = template.copy()
design['phase_1_quantitative'] = {...}
design['phase_2_qualitative'] = {...}
design['integration_strategy'] = {...}
```

---

## 사용하는 Agents

이 Skill을 사용하는 agents:
- `design-proposer` (Stage 4) - 주요 사용자
- `research-model-developer` (Phase 2)
- `mixed-methods-designer` (Phase 2 - legacy)

---

## 버전 히스토리

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-28 | Initial release |

---

**작성자**: Claude Code
**상태**: ✅ Ready for use
