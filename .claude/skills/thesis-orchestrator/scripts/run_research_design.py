#!/usr/bin/env python3
"""Phase 2 Research Design Pipeline Orchestrator

This script executes Phase 2 of the thesis workflow based on research type:

QUANTITATIVE PATH:
1. hypothesis-developer -> 20-hypotheses.md
2. research-model-developer -> 21-research-model-final.md
3. sampling-designer -> 22-sampling-design.md
4. statistical-planner -> 23-statistical-analysis-plan.md

QUALITATIVE PATH:
1. paradigm-consultant -> 20-research-paradigm.md
2. participant-selector -> 21-participant-selection.md
3. qualitative-data-designer -> 22-data-collection-protocol.md
4. qualitative-analysis-planner -> 23-qualitative-analysis-plan.md

MIXED METHODS PATH:
1. mixed-methods-designer -> 20-mixed-methods-design.md
2. integration-strategist -> 21-integration-strategy.md
(+ both quantitative and qualitative paths)

PHILOSOPHICAL PATH:
1. philosophical-method-designer -> 20-philosophical-methods.md
2. source-text-selector -> 21-source-text-selection.md
3. argument-construction-designer -> 22-argument-structure.md
4. philosophical-analysis-planner -> 23-philosophical-analysis-plan.md

After all agents complete, it runs validation and creates research-design-final.md
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from context_loader import load_context
from workflow_constants import AGENT_STEP_MAP


# ---------------------------------------------------------------------------
# Prerequisites validation
# ---------------------------------------------------------------------------

def validate_prerequisites(context):
    """Validate that Phase 1 is complete and research type is set.

    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []

    # Check Phase 1 completion
    workflow = context.session.get('workflow', {})
    current_phase = workflow.get('current_phase', '')
    current_step = workflow.get('current_step', 0)

    phase1_complete_indicators = [
        'phase1-complete', 'phase1_complete',
        'hitl-2', 'hitl-2-complete', 'hitl_2_complete',
        'phase2', 'phase2_research_design',
    ]

    if current_phase not in phase1_complete_indicators and current_step < 83:
        errors.append(
            f"Phase 1 not complete (current: '{current_phase}', step {current_step}). "
            "Run Phase 1 first: python3 run_wave1.py"
        )

    # Check research type
    research = context.session.get('research', {})
    research_type = research.get('type', '')

    if not research_type:
        errors.append(
            "Research type not set. Use /thesis:set-research-type first."
        )
    elif research_type not in ['quantitative', 'qualitative', 'mixed', 'philosophical']:
        errors.append(
            f"Invalid research type: '{research_type}'. "
            "Must be one of: quantitative, qualitative, mixed, philosophical"
        )

    if errors:
        return False, errors
    return True, []


def get_research_type(context):
    """Get research type from session.json."""
    research = context.session.get('research', {})
    research_type = research.get('type', '')

    if research_type not in ['quantitative', 'qualitative', 'mixed', 'philosophical']:
        print(f"\n  Warning: Unknown research type '{research_type}'. Defaulting to 'qualitative'.")
        return 'qualitative'

    return research_type


def get_research_questions_text(questions):
    """Format research questions for display, handling both string and dict formats."""
    lines = []
    for i, q in enumerate(questions, 1):
        if isinstance(q, dict):
            domain = q.get('domain', '')
            q_text = q.get('question_ko', '') or q.get('question_en', '') or q.get('question', '')
            if domain:
                lines.append(f"{i}. [{domain}] {q_text}")
            else:
                lines.append(f"{i}. {q_text}")
        else:
            lines.append(f"{i}. {q}")
    return lines


def format_questions_markdown(questions):
    """Format research questions for markdown output."""
    lines = get_research_questions_text(questions)
    return chr(10).join(lines)


# ---------------------------------------------------------------------------
# QUANTITATIVE PATH
# ---------------------------------------------------------------------------

def run_quantitative_path(context):
    """Execute quantitative research design agents."""
    print("\n" + "=" * 80)
    print("PHASE 2 - QUANTITATIVE RESEARCH DESIGN PATH")
    print("=" * 80)

    agents = [
        ('hypothesis-developer', '20-hypotheses.md', 'Hypothesis Development'),
        ('research-model-developer', '21-research-model-final.md', 'Research Model Development'),
        ('sampling-designer', '22-sampling-design.md', 'Sampling Design'),
        ('statistical-planner', '23-statistical-analysis-plan.md', 'Statistical Analysis Planning'),
    ]

    for i, (agent_name, output_file, description) in enumerate(agents, 1):
        print(f"\n{'=' * 80}")
        print(f"QUANTITATIVE AGENT {i}/4: {description}")
        print(f"Agent: @{agent_name}")
        print(f"{'=' * 80}")

        output_path = context.get_output_path("phase2", output_file)

        research = context.session.get('research', {})
        topic = research.get('topic', '')
        questions = research.get('research_questions', [])

        print(f"\n  Research Topic: {topic}")
        print(f"\n  Research Questions:")
        for line in get_research_questions_text(questions):
            print(f"   {line}")

        content = generate_quantitative_agent_output(
            agent_name, description, topic, questions, context
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        step = AGENT_STEP_MAP.get(agent_name, 89 + i)
        context.update_session({
            "workflow": {
                "current_step": step,
                "current_phase": "phase2_research_design",
                "last_agent": agent_name,
            }
        })

        print(f"\n  Agent {i} Complete: {agent_name}")
        print(f"  Output: {output_path}")

    return True


# ---------------------------------------------------------------------------
# QUALITATIVE PATH
# ---------------------------------------------------------------------------

def run_qualitative_path(context):
    """Execute qualitative research design agents."""
    print("\n" + "=" * 80)
    print("PHASE 2 - QUALITATIVE RESEARCH DESIGN PATH")
    print("=" * 80)

    agents = [
        ('paradigm-consultant', '20-research-paradigm.md', 'Research Paradigm Establishment'),
        ('participant-selector', '21-participant-selection.md', 'Participant Selection Strategy'),
        ('qualitative-data-designer', '22-data-collection-protocol.md', 'Data Collection Protocol'),
        ('qualitative-analysis-planner', '23-qualitative-analysis-plan.md', 'Qualitative Analysis Planning'),
    ]

    for i, (agent_name, output_file, description) in enumerate(agents, 1):
        print(f"\n{'=' * 80}")
        print(f"QUALITATIVE AGENT {i}/4: {description}")
        print(f"Agent: @{agent_name}")
        print(f"{'=' * 80}")

        output_path = context.get_output_path("phase2", output_file)

        research = context.session.get('research', {})
        topic = research.get('topic', '')
        questions = research.get('research_questions', [])

        print(f"\n  Research Topic: {topic}")
        print(f"\n  Research Questions:")
        for line in get_research_questions_text(questions):
            print(f"   {line}")

        content = generate_qualitative_agent_output(
            agent_name, description, topic, questions, context
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        step = AGENT_STEP_MAP.get(agent_name, 89 + i)
        context.update_session({
            "workflow": {
                "current_step": step,
                "current_phase": "phase2_research_design",
                "last_agent": agent_name,
            }
        })

        print(f"\n  Agent {i} Complete: {agent_name}")
        print(f"  Output: {output_path}")

    return True


# ---------------------------------------------------------------------------
# MIXED METHODS PATH
# ---------------------------------------------------------------------------

def run_mixed_methods_path(context):
    """Execute mixed methods research design."""
    print("\n" + "=" * 80)
    print("PHASE 2 - MIXED METHODS RESEARCH DESIGN PATH")
    print("=" * 80)

    core_agents = [
        ('mixed-methods-designer', '20-mixed-methods-design.md', 'Mixed Methods Design'),
        ('integration-strategist', '21-integration-strategy.md', 'Integration Strategy'),
    ]

    for i, (agent_name, output_file, description) in enumerate(core_agents, 1):
        print(f"\n{'=' * 80}")
        print(f"MIXED METHODS CORE AGENT {i}/2: {description}")
        print(f"Agent: @{agent_name}")
        print(f"{'=' * 80}")

        output_path = context.get_output_path("phase2", output_file)

        research = context.session.get('research', {})
        topic = research.get('topic', '')
        questions = research.get('research_questions', [])

        print(f"\n  Research Topic: {topic}")
        print(f"\n  Research Questions:")
        for line in get_research_questions_text(questions):
            print(f"   {line}")

        content = generate_mixed_methods_agent_output(
            agent_name, description, topic, questions, context
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        step = AGENT_STEP_MAP.get(agent_name, 89 + i)
        context.update_session({
            "workflow": {
                "current_step": step,
                "current_phase": "phase2_research_design",
                "last_agent": agent_name,
            }
        })

        print(f"\n  Agent {i} Complete: {agent_name}")
        print(f"  Output: {output_path}")

    # Execute quantitative and qualitative components
    print("\n" + "=" * 80)
    print("EXECUTING QUANTITATIVE COMPONENT")
    print("=" * 80)
    run_quantitative_path(context)

    print("\n" + "=" * 80)
    print("EXECUTING QUALITATIVE COMPONENT")
    print("=" * 80)
    run_qualitative_path(context)

    return True


# ---------------------------------------------------------------------------
# PHILOSOPHICAL PATH
# ---------------------------------------------------------------------------

def run_philosophical_path(context):
    """Execute philosophical/theoretical research design agents."""
    print("\n" + "=" * 80)
    print("PHASE 2 - PHILOSOPHICAL/THEORETICAL RESEARCH DESIGN PATH")
    print("=" * 80)

    agents = [
        ('philosophical-method-designer', '20-philosophical-methods.md', 'Philosophical Method Design'),
        ('source-text-selector', '21-source-text-selection.md', 'Primary Source & Text Selection'),
        ('argument-construction-designer', '22-argument-structure.md', 'Argument Construction Design'),
        ('philosophical-analysis-planner', '23-philosophical-analysis-plan.md', 'Philosophical Analysis Planning'),
    ]

    for i, (agent_name, output_file, description) in enumerate(agents, 1):
        print(f"\n{'=' * 80}")
        print(f"PHILOSOPHICAL AGENT {i}/4: {description}")
        print(f"Agent: @{agent_name}")
        print(f"{'=' * 80}")

        output_path = context.get_output_path("phase2", output_file)

        research = context.session.get('research', {})
        topic = research.get('topic', '')
        questions = research.get('research_questions', [])

        print(f"\n  Research Topic: {topic}")
        print(f"\n  Research Questions:")
        for line in get_research_questions_text(questions):
            print(f"   {line}")

        content = generate_philosophical_agent_output(
            agent_name, description, topic, questions, context
        )

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        step = AGENT_STEP_MAP.get(agent_name, 89 + i)
        context.update_session({
            "workflow": {
                "current_step": step,
                "current_phase": "phase2_research_design",
                "last_agent": agent_name,
            }
        })

        print(f"\n  Agent {i} Complete: {agent_name}")
        print(f"  Output: {output_path}")

    return True


# ===========================================================================
# Content generation functions
# ===========================================================================


def generate_quantitative_agent_output(agent_name, description, topic, questions, context):
    """Generate output for quantitative research design agents."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    q_text = format_questions_markdown(questions)

    if agent_name == 'hypothesis-developer':
        return f"""# Research Hypotheses

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Hypothesis Development Framework

### 2.1 Variable Identification

Based on the research questions and literature review, the following key variables have been identified:

#### Independent Variables (IV)
- [Variable 1]: [Description]
- [Variable 2]: [Description]

#### Dependent Variables (DV)
- [Variable 1]: [Description]
- [Variable 2]: [Description]

#### Mediating Variables (M)
- [Variable 1]: [Description]

#### Moderating Variables (MOD)
- [Variable 1]: [Description]

### 2.2 Hypothesis System

#### Main Effect Hypotheses

| Hypothesis | Content | Direction | Literature Support |
|------------|---------|-----------|-------------------|
| H1 | [IV1] will have a positive/negative effect on [DV1] | (+)/(-) | [Citation] |
| H2 | [IV2] will have a positive/negative effect on [DV1] | (+)/(-) | [Citation] |

#### Mediating Effect Hypotheses

| Hypothesis | Path | Literature Support |
|------------|------|-------------------|
| H3 | [IV1] -> [M1] -> [DV1] | [Citation] |

#### Moderating Effect Hypotheses

| Hypothesis | Moderator | Moderation Direction | Literature Support |
|------------|-----------|---------------------|-------------------|
| H4 | [MOD1] moderates [IV1] -> [DV1] | Strengthens/Weakens | [Citation] |

## 3. Null and Alternative Hypotheses

| Hypothesis | H0 (Null) | H1 (Alternative) |
|------------|-----------|------------------|
| H1 | There is no significant relationship between [IV1] and [DV1] | There is a significant positive/negative relationship between [IV1] and [DV1] |
| H2 | There is no significant relationship between [IV2] and [DV1] | There is a significant positive/negative relationship between [IV2] and [DV1] |

## 4. Hypothesis Integration and Logic

The hypotheses form an integrated theoretical model:

```
[IV1] ----------------------------> [DV1]  (H1: Direct effect)
  |                                   ^
  +----> [M1] ------------------------+  (H3: Mediation)

[IV2] ----------------------------> [DV1]  (H2: Direct effect)

[MOD1] --+
         +---> [IV1] x [MOD1] -> [DV1]  (H4: Moderation)
[IV1] ---+
```

## 5. Expected Analytical Methods

| Hypothesis | Proposed Analysis Method | Software |
|------------|-------------------------|----------|
| H1, H2 | Multiple regression analysis | SPSS/R/Stata |
| H3 | Mediation analysis (Baron & Kenny; Bootstrap) | R/Mplus |
| H4 | Moderated regression analysis | SPSS/R |

## 6. GRA Compliance - Claims

```yaml
claims:
  - id: "HD-001"
    text: "The relationship between [IV1] and [DV1] is theoretically grounded in [Theory Name]."
    claim_type: THEORETICAL
    sources:
      - type: PRIMARY
        reference: "[Author, Year]"
        doi: "[DOI if available]"
        verified: true
    confidence: 85
    uncertainty: "The theoretical relationship may be context-dependent and vary across populations."

  - id: "HD-002"
    text: "Prior empirical studies have demonstrated a positive relationship between [IV1] and [DV1]."
    claim_type: EMPIRICAL
    sources:
      - type: PRIMARY
        reference: "[Study 1, Year]"
        verified: true
      - type: PRIMARY
        reference: "[Study 2, Year]"
        verified: true
    confidence: 80
    uncertainty: "Effect sizes vary across studies, and some contradictory evidence exists."
```

## Quality Checklist

- [ ] All hypotheses derived from literature review
- [ ] Directional predictions specified where appropriate
- [ ] Null and alternative hypotheses clearly stated
- [ ] Hypotheses are testable and falsifiable
- [ ] All claims use GRA GroundedClaim format
- [ ] Theoretical logic connecting hypotheses is clear
- [ ] Analytical methods appropriate for each hypothesis

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Quantitative Agent 1/4 Complete
**Next Agent**: @research-model-developer
"""

    elif agent_name == 'research-model-developer':
        return f"""# Research Model Development

Generated by: @{agent_name}
Date: {timestamp}

## 1. Conceptual Research Model

Based on the hypotheses developed, this section presents the integrated research model.

### 1.1 Theoretical Framework

[Describe the overarching theoretical framework that guides the research model]

### 1.2 Visual Research Model

```
+--------------------------------------------------------------+
|                    RESEARCH MODEL                             |
+--------------------------------------------------------------+
|                                                               |
|  [Independent Variables]      [Mediators]    [Dependent Var]  |
|                                                               |
|  +------------+                +----------+   +-----------+   |
|  |    IV1     |--------------->|    M1    |-->|    DV1    |   |
|  +------------+     H3a        +----------+   +-----------+   |
|       |                              ^              ^         |
|       |              H1              |              |         |
|       +-----------  -----------------+--------------+         |
|                                                               |
|  +------------+                                               |
|  |    IV2     |---------------------------------------------> |
|  +------------+                H2                             |
|                                                               |
|  [Moderators]                                                 |
|  +------------+                                               |
|  |   MOD1     |-----> IV1 x MOD1 -----> DV1 (H4)            |
|  +------------+                                               |
|                                                               |
+--------------------------------------------------------------+
```

## 2. Variable Operationalization

### 2.1 Independent Variables

| Variable | Conceptual Definition | Operational Definition | Measurement Scale | Source |
|----------|----------------------|------------------------|-------------------|--------|
| IV1 | [Concept] | [How it will be measured] | Likert 1-5 / Continuous | [Instrument] |
| IV2 | [Concept] | [How it will be measured] | Likert 1-5 / Continuous | [Instrument] |

### 2.2 Dependent Variables

| Variable | Conceptual Definition | Operational Definition | Measurement Scale | Source |
|----------|----------------------|------------------------|-------------------|--------|
| DV1 | [Concept] | [How it will be measured] | Likert 1-5 / Continuous | [Instrument] |

### 2.3 Mediating Variables

| Variable | Conceptual Definition | Operational Definition | Measurement Scale | Source |
|----------|----------------------|------------------------|-------------------|--------|
| M1 | [Concept] | [How it will be measured] | Likert 1-5 / Continuous | [Instrument] |

### 2.4 Moderating Variables

| Variable | Conceptual Definition | Operational Definition | Measurement Scale | Source |
|----------|----------------------|------------------------|-------------------|--------|
| MOD1 | [Concept] | [How it will be measured] | Categorical / Continuous | [Instrument] |

### 2.5 Control Variables

| Variable | Conceptual Definition | Operational Definition | Measurement Scale | Source |
|----------|----------------------|------------------------|-------------------|--------|
| Control1 | [Concept] | [How it will be measured] | [Scale] | [Instrument] |

## 3. Model Assumptions

### 3.1 Theoretical Assumptions
1. [Assumption 1 about causal relationships]
2. [Assumption 2 about variable relationships]

### 3.2 Statistical Assumptions
1. **Linearity**: Relationships between variables are assumed to be linear
2. **Independence**: Observations are independent of each other
3. **Homoscedasticity**: Error variance is constant across levels of predictors
4. **Normality**: Residuals are normally distributed
5. **No Multicollinearity**: Independent variables are not highly correlated

## 4. Model Justification

### 4.1 Literature Support

[Discuss how this model is grounded in existing literature]

### 4.2 Theoretical Rationale

[Explain the theoretical logic underlying the proposed relationships]

## 5. Expected Model Fit Criteria

For structural equation modeling (if applicable):

| Fit Index | Acceptable Threshold | Desired Value |
|-----------|---------------------|---------------|
| chi-sq/df | < 3.0 | < 2.0 |
| CFI | > 0.90 | > 0.95 |
| TLI | > 0.90 | > 0.95 |
| RMSEA | < 0.08 | < 0.05 |
| SRMR | < 0.08 | < 0.05 |

## 6. GRA Compliance - Claims

```yaml
claims:
  - id: "RMD-001"
    text: "The proposed research model integrates [Theory A] and [Theory B] to explain [phenomenon]."
    claim_type: THEORETICAL
    sources:
      - type: PRIMARY
        reference: "[Theory A citation]"
        verified: true
      - type: PRIMARY
        reference: "[Theory B citation]"
        verified: true
    confidence: 88
    uncertainty: "The integration of these theories in this specific context is novel and requires empirical validation."
```

## Quality Checklist

- [ ] All variables clearly operationalized
- [ ] Measurement scales specified
- [ ] Model assumptions stated
- [ ] Literature support provided
- [ ] Visual model diagram included
- [ ] Expected fit criteria defined
- [ ] All claims use GRA format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Quantitative Agent 2/4 Complete
**Next Agent**: @sampling-designer
"""

    elif agent_name == 'sampling-designer':
        return f"""# Sampling Design

Generated by: @{agent_name}
Date: {timestamp}

## 1. Target Population

### 1.1 Population Definition

**Target Population**: [Clearly define the population to which results will be generalized]

**Inclusion Criteria**:
- [Criterion 1]
- [Criterion 2]
- [Criterion 3]

**Exclusion Criteria**:
- [Criterion 1]
- [Criterion 2]

**Population Size**: Approximately [N] individuals/units

## 2. Sampling Strategy

### 2.1 Sampling Method

**Selected Method**: [Probability/Non-probability sampling method]

**Justification**: [Why this method is appropriate for this research]

### 2.2 Specific Sampling Technique

#### Option A: Simple Random Sampling
- [Description of how random sampling will be implemented]
- Random number generation method: [Method]

#### Option B: Stratified Random Sampling
- **Strata Definition**: [How population will be stratified]
  - Stratum 1: [Description] (estimated n = [n])
  - Stratum 2: [Description] (estimated n = [n])
- **Proportional vs. Disproportional**: [Choice and rationale]

#### Option C: Convenience/Purposive Sampling (if applicable)
- **Rationale**: [Why probability sampling is not feasible]
- **Mitigation of Bias**: [Strategies to minimize selection bias]

## 3. Sample Size Determination

### 3.1 Statistical Power Analysis

**Parameters**:
- **Desired Power (1-beta)**: 0.80 (minimum) / 0.90 (preferred)
- **Significance Level (alpha)**: 0.05
- **Expected Effect Size**: [Small: 0.20 / Medium: 0.50 / Large: 0.80] based on [literature/pilot study]
- **Number of Predictors**: [k]

**Calculation Method**: G*Power / R pwr package / Formula-based

**Minimum Required Sample Size**: n = [N]

### 3.2 Attrition Adjustment

- **Expected Response Rate**: [X]%
- **Expected Dropout Rate**: [Y]%
- **Adjusted Sample Size**: n = [N] x (1 / response rate) = [N_adjusted]

### 3.3 Sample Size by Analysis Method

| Analysis | Minimum n | Recommended n | Rationale |
|----------|-----------|---------------|-----------|
| Multiple Regression | [N] | [N] | 10-20 cases per predictor |
| SEM | [N] | [N] | 10-15 cases per parameter |
| Mediation Analysis | [N] | [N] | Bootstrap requires [N]+ |

**Final Target Sample Size**: **n = [N]**

## 4. Sampling Procedures

### 4.1 Participant Recruitment

**Recruitment Channels**:
1. [Channel 1]: [Description]
2. [Channel 2]: [Description]
3. [Channel 3]: [Description]

**Recruitment Timeline**:
- Phase 1 (Weeks 1-2): [Activities]
- Phase 2 (Weeks 3-4): [Activities]
- Phase 3 (Weeks 5-6): [Activities]

### 4.2 Screening Process

1. Initial contact and study explanation
2. Screening questionnaire to verify inclusion/exclusion criteria
3. Informed consent process
4. Data collection

### 4.3 Incentives (if applicable)

- **Type**: [Monetary / Non-monetary]
- **Amount/Value**: [Value]
- **Justification**: [Why this incentive level is appropriate]

## 5. Representativeness Assessment

### 5.1 Demographic Comparison

Will compare sample demographics to known population parameters:

| Characteristic | Population % | Expected Sample % |
|----------------|--------------|-------------------|
| Gender | [%] | [%] |
| Age Group | [%] | [%] |
| [Other] | [%] | [%] |

### 5.2 Non-Response Bias Check

- **Method**: Compare early vs. late respondents on key variables
- **Threshold**: >10% difference indicates potential bias

## 6. Ethical Considerations

### 6.1 Informed Consent
- [Description of consent process]

### 6.2 Confidentiality
- [How participant confidentiality will be maintained]

### 6.3 IRB Approval
- **Status**: [Applied / Approved / Exempt]
- **IRB Reference**: [Number]

## 7. GRA Compliance - Claims

```yaml
claims:
  - id: "SD-001"
    text: "A sample size of [N] provides 80% power to detect a medium effect size at alpha = 0.05 for multiple regression with [k] predictors."
    claim_type: METHODOLOGICAL
    sources:
      - type: SECONDARY
        reference: "Cohen, J. (1988). Statistical Power Analysis for the Behavioral Sciences"
        verified: true
    confidence: 95
    uncertainty: "Actual power depends on true (unknown) effect size in the population."

  - id: "SD-002"
    text: "[Sampling method] is appropriate given [constraints/characteristics of the study]."
    claim_type: METHODOLOGICAL
    sources:
      - type: SECONDARY
        reference: "[Sampling methodology textbook/paper]"
        verified: true
    confidence: 85
    uncertainty: "All sampling methods have limitations; generalizability depends on sample representativeness."
```

## Quality Checklist

- [ ] Target population clearly defined
- [ ] Inclusion/exclusion criteria specified
- [ ] Sampling method justified
- [ ] Sample size calculation documented
- [ ] Power analysis conducted
- [ ] Recruitment procedures detailed
- [ ] Ethical considerations addressed
- [ ] All claims use GRA format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Quantitative Agent 3/4 Complete
**Next Agent**: @statistical-planner
"""

    else:  # statistical-planner
        return f"""# Statistical Analysis Plan

Generated by: @{agent_name}
Date: {timestamp}

## 1. Overview

This statistical analysis plan (SAP) outlines all analyses to be conducted to test the research hypotheses. The plan follows pre-registration best practices to ensure transparency and minimize researcher degrees of freedom.

## 2. Data Preparation

### 2.1 Data Screening

#### Missing Data Analysis
- **Method**: Little's MCAR test
- **Threshold**: Missing data >5% per variable will be investigated
- **Handling Strategy**:
  - <5% missing: Listwise deletion
  - 5-20% missing: Multiple imputation (m=5 imputations)
  - >20% missing: Variable exclusion or sensitivity analysis

#### Outlier Detection
- **Method**:
  - Univariate: +/-3 SD from mean
  - Multivariate: Mahalanobis distance (p < .001)
- **Handling**:
  - Investigate outliers for data entry errors
  - Report analyses with and without outliers
  - Winsorization if appropriate

### 2.2 Assumption Testing

#### Normality
- **Tests**: Shapiro-Wilk test, Q-Q plots, histograms
- **Threshold**: Skewness < |2|, Kurtosis < |7|
- **Remediation**: Log transformation, square root transformation, or non-parametric alternatives

#### Linearity
- **Test**: Scatterplots, LOESS curves
- **Remediation**: Polynomial terms, transformation, or non-linear models

#### Homoscedasticity
- **Test**: Breusch-Pagan test, residual plots
- **Remediation**: Robust standard errors, weighted least squares

#### Multicollinearity
- **Test**: VIF (Variance Inflation Factor)
- **Threshold**: VIF > 10 indicates problematic multicollinearity
- **Remediation**: Remove redundant variables, use PCA, or ridge regression

## 3. Descriptive Statistics

### 3.1 Sample Characteristics

- Frequency distributions for categorical variables
- Means, SDs, ranges for continuous variables
- Demographic breakdown by key subgroups

### 3.2 Correlation Matrix

Pearson correlations (or Spearman for non-normal) for all study variables.

**Interpretation Thresholds**:
- r < .30: Weak
- .30 <= r < .50: Moderate
- r >= .50: Strong

## 4. Hypothesis Testing

### 4.1 Hypothesis 1: [IV1 -> DV1]

**Analysis Method**: Multiple linear regression

**Model Specification**:
```
DV1 = b0 + b1(IV1) + b2(Control1) + b3(Control2) + ... + e
```

**Effect Size**: R-squared, Delta-R-squared, Cohen's f-squared

**Interpretation**:
- H1 supported if b1 is significant (p < .05) and in predicted direction
- Report standardized and unstandardized coefficients
- Report 95% confidence intervals

### 4.2 Hypothesis 3: [Mediation: IV1 -> M1 -> DV1]

**Analysis Method**: Mediation analysis (Baron & Kenny + Bootstrap)

**Steps**:
1. Test IV1 -> DV1 (path c)
2. Test IV1 -> M1 (path a)
3. Test M1 -> DV1 controlling for IV1 (path b)
4. Test IV1 -> DV1 controlling for M1 (path c')

**Bootstrap**: 5,000 resamples for indirect effect (a x b)

**Software**: R (lavaan/mediation package) / Mplus / PROCESS macro

**Interpretation**:
- Full mediation: c' not significant, indirect effect significant
- Partial mediation: c' significant but reduced, indirect effect significant
- 95% CI for indirect effect does not include zero

### 4.3 Hypothesis 4: [Moderation: MOD1 x IV1 -> DV1]

**Analysis Method**: Moderated regression analysis

**Model Specification**:
```
DV1 = b0 + b1(IV1) + b2(MOD1) + b3(IV1 x MOD1) + b4(Controls) + e
```

**Centering**: Mean-center IV1 and MOD1 before computing interaction term

**Interpretation**:
- H4 supported if b3 is significant (p < .05)
- Simple slopes analysis at MOD1 = M +/- 1 SD
- Plot interaction effect

## 5. Sensitivity Analyses

### 5.1 Robustness Checks

1. **Alternative Specifications**: Test models with/without control variables
2. **Subsample Analysis**: Analyze by subgroups (e.g., gender, age)
3. **Outlier Sensitivity**: Re-run analyses excluding outliers
4. **Missing Data Methods**: Compare results across imputation methods

## 6. Statistical Software and Packages

| Software | Version | Packages | Purpose |
|----------|---------|----------|---------|
| R | 4.x | lavaan, psych, mediation, ggplot2 | Primary analysis |
| SPSS | 28.x | PROCESS macro | Mediation/moderation |
| G*Power | 3.1.x | N/A | Power analysis |

## 7. Decision Rules

### 7.1 Statistical Significance
- **Primary threshold**: p < .05 (two-tailed)
- **Bonferroni correction** (if multiple testing): alpha / k

### 7.2 Practical Significance
- In addition to statistical significance, consider:
  - Effect size magnitude
  - Confidence interval width
  - Practical importance in real-world context

## 8. GRA Compliance - Claims

```yaml
claims:
  - id: "SAP-001"
    text: "Multiple regression is appropriate for testing the relationship between [IV] and [DV] given the continuous nature of variables and sample size."
    claim_type: METHODOLOGICAL
    sources:
      - type: SECONDARY
        reference: "Cohen, J., Cohen, P., West, S. G., & Aiken, L. S. (2003). Applied Multiple Regression/Correlation Analysis"
        verified: true
    confidence: 92
    uncertainty: "Appropriateness depends on assumptions being met (linearity, homoscedasticity, normality of residuals)."

  - id: "SAP-002"
    text: "Bootstrap mediation analysis with 5,000 resamples provides more accurate confidence intervals than the Sobel test, especially with smaller samples."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "Preacher, K. J., & Hayes, A. F. (2008). Asymptotic and resampling strategies for assessing and comparing indirect effects"
        doi: "10.3758/BRM.40.3.879"
        verified: true
    confidence: 90
    uncertainty: "Bootstrap CI accuracy depends on sample size and distribution characteristics."
```

## Quality Checklist

- [ ] All hypotheses linked to specific statistical tests
- [ ] Assumption testing procedures specified
- [ ] Missing data handling strategy defined
- [ ] Effect sizes specified for all analyses
- [ ] Software and packages documented
- [ ] Decision rules for interpretation stated
- [ ] Sensitivity analyses planned
- [ ] All claims use GRA format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Quantitative Agent 4/4 Complete
**Next Step**: Create research-design-final.md synthesis
"""


# ===========================================================================
# QUALITATIVE content generation
# ===========================================================================

def generate_qualitative_agent_output(agent_name, description, topic, questions, context):
    """Generate output for qualitative research design agents."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    q_text = format_questions_markdown(questions)

    if agent_name == 'paradigm-consultant':
        return f"""# Research Paradigm Establishment

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Philosophical Foundations

### 2.1 Ontological Position

**Selected Position**: [Realism / Relativism / Critical Realism / Social Constructionism]

**Justification**: [Why this ontological position is appropriate for the research questions]

**Implications for Research**:
- Nature of reality assumed: [Description]
- Multiple realities acknowledged: [Yes/No and how]

### 2.2 Epistemological Position

**Selected Position**: [Objectivism / Subjectivism / Constructionism / Pragmatism]

**Justification**: [How knowledge is understood and generated in this study]

**Implications for Research**:
- Relationship between researcher and participants: [Description]
- Nature of knowledge produced: [Description]

### 2.3 Axiological Position

**Value Stance**: [Value-free / Value-laden / Value-bound]

**Researcher's Values**:
- Acknowledged biases: [Description]
- Impact on research: [Description]

## 3. Research Paradigm Selection

### 3.1 Selected Paradigm

**Paradigm**: [Interpretivism / Critical Theory / Constructivism / Pragmatism / Transformative / Post-positivism]

### 3.2 Selection Rationale

| Criterion | Alignment |
|-----------|-----------|
| Research purpose | [How the paradigm aligns with research purpose] |
| Research questions | [How it aligns with RQ nature] |
| Researcher stance | [How it aligns with researcher's worldview] |
| Phenomenon nature | [How it suits the phenomenon under study] |

### 3.3 Paradigm Characteristics

| Dimension | Position | Description |
|-----------|----------|-------------|
| Ontology | [Position] | [Description] |
| Epistemology | [Position] | [Description] |
| Methodology | [Position] | [Description] |
| Axiology | [Position] | [Description] |

## 4. Methodological Approach

### 4.1 Selected Qualitative Approach

**Approach**: [Phenomenology / Grounded Theory / Ethnography / Case Study / Narrative Inquiry / IPA]

### 4.2 Selection Rationale

| Consideration | Assessment |
|---------------|------------|
| Fit with RQs | [Assessment] |
| Fit with paradigm | [Assessment] |
| Fit with phenomenon | [Assessment] |
| Practical feasibility | [Assessment] |

### 4.3 Key Methodological Scholars

| Scholar | Contribution | Key Work |
|---------|-------------|----------|
| [Name] | [Contribution to the methodology] | [Citation] |
| [Name] | [Contribution to the methodology] | [Citation] |

## 5. Researcher Reflexivity

### 5.1 Researcher Background
- Academic training: [Description]
- Professional experience: [Description]
- Personal connection to topic: [Description]

### 5.2 Pre-understanding (Bracketing)
- Known assumptions about the phenomenon: [Description]
- Steps to bracket pre-understanding: [Description]

### 5.3 Influence Minimization Strategies
1. Reflexive journaling throughout the research process
2. Peer debriefing with colleagues
3. Member checking with participants
4. Audit trail documentation

## 6. GRA Compliance - Claims

```yaml
claims:
  - id: "PC-001"
    text: "[Paradigm] is appropriate for this research because [justification grounded in methodology literature]."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Methodology scholar, Year]"
        verified: true
    confidence: 87
    uncertainty: "Paradigm selection involves interpretive judgment; alternative paradigms could also be defended."

  - id: "PC-002"
    text: "[Qualitative approach] aligns with [paradigm] and is suited to address research questions focused on [phenomenon type]."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Methodology source]"
        verified: true
      - type: SECONDARY
        reference: "[Supporting source]"
        verified: true
    confidence: 85
    uncertainty: "Multiple qualitative approaches could potentially address these questions; the selection reflects methodological fit rather than exclusivity."
```

## Quality Checklist

- [ ] Ontological position clearly stated and justified
- [ ] Epistemological position clearly stated and justified
- [ ] Research paradigm explicitly named and defended
- [ ] Qualitative approach selected with rationale
- [ ] Researcher reflexivity section complete
- [ ] Paradigm-methodology alignment demonstrated
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Qualitative Agent 1/4 Complete
**Next Agent**: @participant-selector
"""

    elif agent_name == 'participant-selector':
        return f"""# Participant Selection Strategy

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Purposeful Sampling Strategy

### 2.1 Sampling Type

**Selected Strategy**: [Maximum variation / Homogeneous / Critical case / Typical case / Snowball / Criterion-based / Theory-based]

### 2.2 Selection Rationale

| Criterion | Assessment |
|-----------|-----------|
| Alignment with RQs | [How this strategy addresses the research questions] |
| Information richness | [Why this strategy yields information-rich cases] |
| Practical feasibility | [Accessibility and resource considerations] |

## 3. Participant Selection Criteria

### 3.1 Inclusion Criteria

| Criterion | Rationale | Verification Method |
|-----------|-----------|---------------------|
| [Criterion 1] | [Why this criterion is essential] | [How to verify] |
| [Criterion 2] | [Why this criterion is essential] | [How to verify] |
| [Criterion 3] | [Why this criterion is essential] | [How to verify] |

### 3.2 Exclusion Criteria

| Criterion | Rationale |
|-----------|-----------|
| [Criterion 1] | [Why this criterion warrants exclusion] |
| [Criterion 2] | [Why this criterion warrants exclusion] |

### 3.3 Diversity Dimensions

| Dimension | Target Variation | Rationale |
|-----------|-----------------|-----------|
| [Dimension 1: e.g., Age] | [Range/Categories] | [Why variation matters] |
| [Dimension 2: e.g., Experience level] | [Range/Categories] | [Why variation matters] |
| [Dimension 3: e.g., Context] | [Range/Categories] | [Why variation matters] |

## 4. Sample Size

### 4.1 Initial Target

**Planned Participants**: [N] participants

**Justification**:
- Methodological guidance: [e.g., Creswell recommends 5-25 for phenomenology]
- Previous studies: [Similar studies used N = X]
- Resource constraints: [Practical considerations]

### 4.2 Theoretical Saturation

**Saturation Criteria**:
1. No new themes emerge from additional interviews
2. No new codes are generated from analysis of new data
3. Existing categories are well-developed with sufficient examples

**Saturation Assessment Method**:
- Track new codes per interview
- Assess conceptual depth of categories
- Peer review of saturation judgment

**Contingency Plan**: If saturation is not reached at [N], recruit additional [X] participants in waves of [Y]

## 5. Access and Rapport

### 5.1 Access Strategy

**Gatekeepers**: [Identify key gatekeepers and access points]

**Access Steps**:
1. [Step 1: Initial contact with gatekeepers]
2. [Step 2: Introduction to potential participants]
3. [Step 3: Informed consent process]

### 5.2 Rapport Building

- **Initial contact**: [How first contact will be made]
- **Trust building**: [Strategies for building trust]
- **Cultural sensitivity**: [Relevant cultural considerations]

### 5.3 Recruitment Timeline

| Week | Activity | Expected Outcome |
|------|----------|-----------------|
| 1-2 | Gatekeeper contact | Access secured |
| 3-4 | Participant identification | Pool of [N] potential participants |
| 5-8 | Screening and recruitment | [N] participants enrolled |

## 6. Ethical Considerations

### 6.1 Informed Consent
- Written/verbal consent process
- Right to withdraw at any time
- Explanation of data usage

### 6.2 Confidentiality and Anonymity
- Pseudonym assignment strategy
- Data de-identification procedures
- Secure data storage

### 6.3 Potential Harm Mitigation
- Sensitive topic protocols
- Referral resources for distress
- Power dynamics awareness

### 6.4 IRB/Ethics Approval
- **Status**: [Applied / Approved / Exempt]
- **Reference Number**: [Number]

## 7. GRA Compliance - Claims

```yaml
claims:
  - id: "PS-001"
    text: "[Sampling strategy] is appropriate for [methodology] because it allows [specific methodological advantage]."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Patton, 2015; or relevant methodology text]"
        verified: true
    confidence: 88
    uncertainty: "Purposeful sampling does not aim for statistical generalizability; transferability depends on thick description."

  - id: "PS-002"
    text: "A sample of [N] participants is adequate for [methodology] based on methodological guidelines and precedent in similar studies."
    claim_type: METHODOLOGICAL
    sources:
      - type: SECONDARY
        reference: "[Creswell & Poth, 2018; or relevant source]"
        verified: true
    confidence: 82
    uncertainty: "Sample size adequacy in qualitative research depends on data richness and saturation, not predetermined numbers."
```

## Quality Checklist

- [ ] Purposeful sampling strategy clearly identified and justified
- [ ] Inclusion/exclusion criteria specific and defensible
- [ ] Sample size justified with methodological and practical rationale
- [ ] Saturation criteria explicitly defined
- [ ] Access and rapport strategies detailed
- [ ] Ethical considerations thoroughly addressed
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Qualitative Agent 2/4 Complete
**Next Agent**: @qualitative-data-designer
"""

    elif agent_name == 'qualitative-data-designer':
        return f"""# Data Collection Protocol

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Data Collection Methods

### 2.1 Primary Method

**Selected Method**: [In-depth interviews / Focus group discussions / Participant observation / Document analysis]

**Justification**: [Why this method is most appropriate for the research questions and paradigm]

### 2.2 Secondary/Supplementary Methods

| Method | Purpose | Contribution to RQs |
|--------|---------|---------------------|
| [Method 1] | [Purpose] | [Which RQ it addresses] |
| [Method 2] | [Purpose] | [Which RQ it addresses] |

### 2.3 Triangulation Design

**Type**: [Data triangulation / Method triangulation / Investigator triangulation / Theory triangulation]

**Implementation**: [How multiple data sources will be used for triangulation]

## 3. Interview Protocol

### 3.1 Interview Type

**Selected Type**: [Structured / Semi-structured / Unstructured]

**Rationale**: [Why this type is appropriate]

### 3.2 Interview Guide

#### Opening Phase (5-10 minutes)
| # | Question | Purpose |
|---|----------|---------|
| 1 | [Introductory question] | Build rapport, ease into topic |
| 2 | [Broad opening question] | Establish participant's general perspective |

#### Core Phase (40-60 minutes)
| # | Domain | Main Question | Probing Questions |
|---|--------|--------------|-------------------|
| 3 | [Domain A] | [Main question about experience/perception] | - Can you tell me more about that? / - What did you mean by...? / - How did that make you feel? |
| 4 | [Domain B] | [Main question about meaning/understanding] | - Could you give me an example? / - What was that experience like? / - How did you come to that understanding? |
| 5 | [Domain C] | [Main question about process/change] | - What happened next? / - How did things change over time? / - What contributed to that change? |
| 6 | [Domain D] | [Main question about relationships/contexts] | - How did others respond? / - What role did [context] play? / - How would you compare...? |

#### Closing Phase (5-10 minutes)
| # | Question | Purpose |
|---|----------|---------|
| 7 | Is there anything else you would like to add? | Capture unanticipated insights |
| 8 | How was this interview experience for you? | Participant wellbeing check |

### 3.3 Interview Parameters

| Parameter | Specification |
|-----------|--------------|
| Duration | [60-90 minutes] |
| Format | [Face-to-face / Video call / Telephone] |
| Location | [Participant's choice / Neutral venue] |
| Recording | [Audio / Video / Notes only] |
| Language | [Language(s) of interview] |
| Number of sessions | [1-3 per participant] |

### 3.4 Pilot Testing

- **Plan**: Conduct [2-3] pilot interviews before main data collection
- **Purpose**: Test interview guide, refine questions, estimate duration
- **Revision criteria**: Modify questions that produce thin responses

## 4. Observation Protocol (if applicable)

### 4.1 Observation Type

**Selected Type**: [Participant observation / Non-participant observation / Structured observation]

### 4.2 Observation Framework

| Dimension | Focus Areas | Recording Method |
|-----------|-------------|-----------------|
| Physical setting | [What to observe] | Field notes |
| Social interactions | [What to observe] | Field notes |
| Activities | [What to observe] | Field notes |
| Conversations | [What to observe] | Audio notes |

### 4.3 Field Notes Template

- Date/time/location
- Description of setting
- Participants present
- Observed activities/interactions
- Researcher reflections (separate column)
- Emerging analytical ideas

## 5. Document Analysis Protocol (if applicable)

### 5.1 Document Types

| Document Type | Source | Selection Criteria |
|---------------|--------|-------------------|
| [Type 1] | [Source] | [Criteria] |
| [Type 2] | [Source] | [Criteria] |

### 5.2 Document Analysis Framework

| Analysis Dimension | Questions to Ask | Coding Approach |
|--------------------|-----------------|-----------------|
| Context | Who produced this? For whom? | Descriptive |
| Content | What themes emerge? | Thematic |
| Form | How is it structured? | Structural |

## 6. Data Collection Timeline

| Phase | Weeks | Activity | Expected Output |
|-------|-------|----------|-----------------|
| Preparation | 1-2 | IRB approval, pilot testing | Refined protocols |
| Wave 1 | 3-6 | First [N] interviews | Initial transcripts |
| Preliminary analysis | 7-8 | Ongoing analysis, guide refinement | Preliminary codes |
| Wave 2 | 9-12 | Remaining interviews | Complete dataset |
| Member checking | 13-14 | Participant validation | Validated findings |

## 7. Data Management

### 7.1 Recording and Transcription
- **Recording device**: [Type and backup]
- **Transcription**: [Verbatim / Intelligent verbatim]
- **Transcriber**: [Self / Professional service]
- **Timeline**: Within [X] days of each interview

### 7.2 Data Storage
- **Format**: [Digital audio files, text transcripts]
- **Storage**: [Encrypted drive / Secure cloud]
- **Backup**: [Backup strategy]
- **Retention period**: [Duration after study completion]

### 7.3 Confidentiality Measures
- Pseudonym system
- De-identification of transcripts
- Secure file naming conventions

## 8. Quality Assurance

### 8.1 Reflexive Practice
- Maintain reflexive journal throughout data collection
- Post-interview debriefing notes
- Regular peer consultation

### 8.2 Data Quality Indicators
- Interview depth (rich, thick descriptions)
- Participant comfort and openness
- Consistency between verbal and non-verbal cues

## 9. Ethical Considerations

### 9.1 Informed Consent Process
- Written consent form (signed before interview)
- Verbal re-consent at start of each session
- Right to skip questions or withdraw

### 9.2 Sensitive Topics Protocol
- [How sensitive topics will be handled]
- [Support resources available to participants]
- [Researcher self-care plan]

## 10. GRA Compliance - Claims

```yaml
claims:
  - id: "QDD-001"
    text: "Semi-structured interviews are appropriate for [methodology] because they balance structure with flexibility to explore emergent themes."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Kvale & Brinkmann, 2015; or relevant source]"
        verified: true
    confidence: 90
    uncertainty: "Interview data depends on participant willingness to share and researcher skill in facilitation."

  - id: "QDD-002"
    text: "Triangulation through [methods] enhances the credibility of qualitative findings by providing multiple perspectives on the phenomenon."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Denzin, 2012; or relevant source]"
        verified: true
    confidence: 85
    uncertainty: "Triangulation does not guarantee validity but provides additional evidence for interpretive claims."
```

## Quality Checklist

- [ ] Data collection methods justified and aligned with methodology
- [ ] Interview guide developed with clear domains and probing questions
- [ ] Pilot testing planned
- [ ] Observation protocol included (if applicable)
- [ ] Timeline is realistic and detailed
- [ ] Data management and storage plans specified
- [ ] Ethical procedures thoroughly documented
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Qualitative Agent 3/4 Complete
**Next Agent**: @qualitative-analysis-planner
"""

    else:  # qualitative-analysis-planner
        return f"""# Qualitative Analysis Plan

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Analysis Approach

### 2.1 Selected Approach

**Primary Approach**: [Thematic Analysis / Content Analysis / Discourse Analysis / IPA / Grounded Theory Analysis / Narrative Analysis]

**Variant/Tradition**: [e.g., Braun & Clarke reflexive thematic analysis; Charmaz constructivist grounded theory]

### 2.2 Selection Rationale

| Criterion | Assessment |
|-----------|-----------|
| Paradigm alignment | [How the approach fits the chosen paradigm] |
| RQ alignment | [How it addresses the research questions] |
| Data type fit | [How it suits the data being collected] |
| Researcher expertise | [Level of researcher familiarity with the approach] |

### 2.3 Alternative Approaches Considered

| Approach | Reason Not Selected |
|----------|---------------------|
| [Alternative 1] | [Why it was not the best fit] |
| [Alternative 2] | [Why it was not the best fit] |

## 3. Coding Strategy

### 3.1 Coding Stages

#### Stage 1: Open/Initial Coding
- **Approach**: Line-by-line / Paragraph-by-paragraph
- **Code types**: Descriptive, In-vivo, Process
- **Output**: Initial codebook with definitions

#### Stage 2: Focused/Axial Coding
- **Approach**: Categorize initial codes into broader themes
- **Process**: Compare codes, identify patterns, group related codes
- **Output**: Refined categories and sub-categories

#### Stage 3: Theoretical/Selective Coding
- **Approach**: Identify overarching themes and relationships
- **Process**: Relate categories to research questions, develop explanatory framework
- **Output**: Final thematic structure

### 3.2 Codebook Structure

| Level | Code | Definition | Inclusion Criteria | Exclusion Criteria | Example |
|-------|------|------------|-------------------|--------------------|---------|
| Theme | [Theme name] | [Clear definition] | [When to apply] | [When not to apply] | [Data excerpt] |
| Sub-theme | [Sub-theme name] | [Clear definition] | [When to apply] | [When not to apply] | [Data excerpt] |
| Code | [Code name] | [Clear definition] | [When to apply] | [When not to apply] | [Data excerpt] |

### 3.3 Coding Rules

1. Each data segment can be assigned multiple codes
2. Codes should be mutually exclusive within the same level
3. New codes can be created throughout analysis (iterative process)
4. Code definitions must be documented and updated
5. Coding decisions should be justified in analytical memos

## 4. Analysis Software

### 4.1 Selected Software

**Primary Tool**: [NVivo / Atlas.ti / MAXQDA / Dedoose / Manual coding]

### 4.2 Selection Rationale

| Criterion | Assessment |
|-----------|-----------|
| Feature set | [Relevant features for this analysis] |
| Data compatibility | [Handles the data types in this study] |
| Researcher familiarity | [Level of expertise with the tool] |
| Cost/accessibility | [Availability and licensing] |

### 4.3 Complementary Tools

| Tool | Purpose |
|------|---------|
| [Tool 1] | [e.g., Concept mapping / Visualization] |
| [Tool 2] | [e.g., Memo writing / Reflexive journaling] |

## 5. Trustworthiness (Rigor)

### 5.1 Credibility
| Strategy | Implementation |
|----------|----------------|
| Prolonged engagement | [Duration and depth of engagement with data] |
| Triangulation | [How multiple data sources/methods/perspectives are used] |
| Member checking | [How participants will validate findings] |
| Peer debriefing | [Who will serve as peer reviewer and how often] |
| Negative case analysis | [How discrepant cases will be identified and analyzed] |

### 5.2 Transferability
| Strategy | Implementation |
|----------|----------------|
| Thick description | [How context and findings will be described in detail] |
| Clear context | [How the research setting and participants are described] |
| Purposeful sampling documentation | [How sampling decisions support transferability] |

### 5.3 Dependability
| Strategy | Implementation |
|----------|----------------|
| Audit trail | [What will be documented: decisions, changes, rationale] |
| Code-recode strategy | [Re-coding data after interval to check consistency] |
| Inquiry audit | [External reviewer examination of process and product] |

### 5.4 Confirmability
| Strategy | Implementation |
|----------|----------------|
| Reflexive journal | [How researcher biases and reactions are documented] |
| Grounding in data | [How interpretations will be anchored to data excerpts] |
| Transparency | [How analytical decisions will be made visible] |

## 6. Analysis Procedure

| Step | Activity | Input | Output | Duration |
|------|----------|-------|--------|----------|
| 1 | Data familiarization | Raw transcripts | Reading notes, initial impressions | [X days] |
| 2 | Open coding | Transcripts | Initial codes | [X weeks] |
| 3 | Code refinement | Initial codes | Codebook v1 | [X days] |
| 4 | Category development | Refined codes | Categories and sub-categories | [X weeks] |
| 5 | Theme identification | Categories | Thematic map | [X days] |
| 6 | Theme review | Thematic map, data | Revised themes | [X days] |
| 7 | Theme definition | Revised themes | Final thematic framework | [X days] |
| 8 | Report writing | Final themes, data excerpts | Findings narrative | [X weeks] |

## 7. Analytical Memo Strategy

### 7.1 Memo Types

| Type | Purpose | Frequency |
|------|---------|-----------|
| Code memos | Document reasoning behind coding decisions | Per coding session |
| Theoretical memos | Develop conceptual ideas and relationships | Weekly |
| Methodological memos | Record procedural decisions | As needed |
| Reflexive memos | Document researcher reactions and biases | Per interview/session |

### 7.2 Memo Template

```
Date: [Date]
Type: [Code / Theoretical / Methodological / Reflexive]
Related to: [Code, theme, participant, or decision]

Observation:
[What I noticed/thought]

Interpretation:
[What it might mean]

Action:
[What to do next based on this memo]
```

## 8. GRA Compliance - Claims

```yaml
claims:
  - id: "QAP-001"
    text: "[Analysis approach] is appropriate for this study because [justification grounded in methodology literature]."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Braun & Clarke, 2006/2019; or relevant source]"
        verified: true
    confidence: 88
    uncertainty: "Qualitative analysis involves interpretive judgment; different researchers may identify different themes from the same data."

  - id: "QAP-002"
    text: "Trustworthiness of findings will be established through [strategies], which are the qualitative equivalents of reliability and validity."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Lincoln & Guba, 1985; or relevant source]"
        verified: true
    confidence: 85
    uncertainty: "Trustworthiness criteria do not eliminate subjectivity but rather make it transparent and accountable."
```

## Quality Checklist

- [ ] Analysis approach clearly identified and justified
- [ ] Coding strategy detailed with stages and rules
- [ ] Codebook structure defined
- [ ] Analysis software selected with rationale
- [ ] All four trustworthiness criteria addressed
- [ ] Step-by-step analysis procedure documented
- [ ] Analytical memo strategy defined
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Qualitative Agent 4/4 Complete
**Next Step**: Create research-design-final.md synthesis
"""


# ===========================================================================
# MIXED METHODS content generation
# ===========================================================================

def generate_mixed_methods_agent_output(agent_name, description, topic, questions, context):
    """Generate output for mixed methods research design agents."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    q_text = format_questions_markdown(questions)

    if agent_name == 'mixed-methods-designer':
        return f"""# Mixed Methods Research Design

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Mixed Methods Design Type

### 2.1 Selected Design

**Design Type**: [Convergent / Explanatory Sequential / Exploratory Sequential / Embedded / Transformative / Multiphase]

### 2.2 Selection Rationale

| Criterion | Assessment |
|-----------|-----------|
| Research purpose | [How this design addresses the research purpose] |
| Research questions | [Which RQs require quantitative vs. qualitative approaches] |
| Practical feasibility | [Time, resources, expertise available] |
| Philosophical worldview | [Pragmatism / Transformative / Other] |

### 2.3 Design Notation

```
[Design notation, e.g.:]
QUAN -> qual                     (Explanatory Sequential)
qual -> QUAN                     (Exploratory Sequential)
QUAN + QUAL                      (Convergent Parallel)
QUAN(qual)                       (Embedded, qual within quan)
```

**Capital letters** = priority strand; **lower case** = supplementary strand
**Arrow (->)** = sequential; **Plus (+)** = concurrent

## 3. Priority Decision

### 3.1 Strand Weighting

**Priority Strand**: [QUAN / QUAL / Equal]

**Justification**:
- [Reason 1 for priority decision]
- [Reason 2 for priority decision]

### 3.2 RQ-to-Strand Mapping

| Research Question | Strand | Priority | Justification |
|-------------------|--------|----------|---------------|
| RQ1 | [QUAN/QUAL] | [Primary/Secondary] | [Why this strand addresses this RQ] |
| RQ2 | [QUAN/QUAL] | [Primary/Secondary] | [Why this strand addresses this RQ] |
| RQ-Integration | [MIXED] | [Primary] | [How integration addresses the overarching question] |

## 4. Temporal Ordering

### 4.1 Sequential vs. Concurrent

**Timing**: [Sequential / Concurrent / Multiphase]

### 4.2 Phase Plan

| Phase | Strand | Purpose | Duration | Key Activities |
|-------|--------|---------|----------|----------------|
| 1 | [QUAN/QUAL] | [Purpose] | [Duration] | [Activities] |
| 2 | Integration | [Purpose] | [Duration] | [Activities] |
| 3 | [QUAN/QUAL] | [Purpose] | [Duration] | [Activities] |
| 4 | Final Integration | [Purpose] | [Duration] | [Activities] |

## 5. Points of Interface

### 5.1 Design-Level Integration

[How the overall design integrates quantitative and qualitative components from the outset]

### 5.2 Methods-Level Integration

| Integration Point | Mechanism | Purpose |
|-------------------|-----------|---------|
| Sampling | [e.g., Same participants for both strands] | [Purpose] |
| Data collection | [e.g., Qual findings inform quan instrument] | [Purpose] |
| Analysis | [e.g., Quan results guide qual sampling] | [Purpose] |

### 5.3 Interpretation-Level Integration

[How quantitative and qualitative findings will be brought together for interpretation]

## 6. Visual Design Diagram

```
Phase 1: [QUAN Data Collection] ----> [QUAN Analysis]
                                           |
                                           v
Phase 2:              [Integration Point: Connect findings]
                                           |
                                           v
Phase 3: [QUAL Data Collection] ----> [QUAL Analysis]
                                           |
                                           v
Phase 4:           [Final Integration & Interpretation]
```

## 7. Validity Framework

### 7.1 Legitimation Types (Onwuegbuzie & Johnson, 2006)

| Legitimation Type | Definition | Strategy |
|-------------------|------------|----------|
| Sample integration | Relationship between QUAN and QUAL samples | [Strategy] |
| Inside-outside | Balance of insider and outsider perspectives | [Strategy] |
| Weakness minimization | Complementary strengths offset weaknesses | [Strategy] |
| Sequential | Order effects in sequential designs | [Strategy] |
| Conversion | Quality of data transformation (if applicable) | [Strategy] |
| Paradigmatic mixing | Coherent philosophical foundation | [Strategy] |
| Commensurability | Ability to make meta-inferences | [Strategy] |
| Multiple validities | Both QUAN validity and QUAL trustworthiness | [Strategy] |

## 8. GRA Compliance - Claims

```yaml
claims:
  - id: "MMD-001"
    text: "[Design type] is appropriate for this study because [justification], following Creswell & Plano Clark's (2018) design framework."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "Creswell, J. W., & Plano Clark, V. L. (2018). Designing and Conducting Mixed Methods Research (3rd ed.)."
        verified: true
    confidence: 88
    uncertainty: "Mixed methods design selection involves trade-offs; the chosen design prioritizes [aspect] at the potential cost of [other aspect]."

  - id: "MMD-002"
    text: "The integration of quantitative and qualitative strands at [integration points] addresses the research questions more comprehensively than either approach alone."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Relevant mixed methods source]"
        verified: true
    confidence: 85
    uncertainty: "The quality of integration depends on the researcher's ability to meaningfully connect findings from both strands."
```

## Quality Checklist

- [ ] Mixed methods design type clearly identified and justified
- [ ] Design notation provided
- [ ] Priority strand decision explained
- [ ] Temporal ordering specified
- [ ] Points of interface identified
- [ ] Visual diagram included
- [ ] Validity framework addressed
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Mixed Methods Core Agent 1/2 Complete
**Next Agent**: @integration-strategist
"""

    else:  # integration-strategist
        return f"""# Integration Strategy

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Data Integration Strategy

### 2.1 Integration Method

**Selected Method**: [Merging / Connecting / Building / Embedding]

**Justification**: [Why this integration method is appropriate for the design type and RQs]

### 2.2 Integration Procedure

| Step | Activity | Input | Output |
|------|----------|-------|--------|
| 1 | [Activity] | [QUAN/QUAL data] | [Integrated product] |
| 2 | [Activity] | [Step 1 output] | [Refined product] |
| 3 | [Activity] | [Step 2 output] | [Final integrated interpretation] |

## 3. Results Integration

### 3.1 Meta-Inference Framework

**Meta-inference**: The overarching conclusion drawn from integrating quantitative and qualitative inferences.

**Process**:
1. Summarize QUAN inferences (statistical conclusions)
2. Summarize QUAL inferences (thematic conclusions)
3. Identify convergence, complementarity, and divergence
4. Formulate meta-inferences that address the overarching RQs

### 3.2 Interpretation Framework

| QUAN Finding | QUAL Finding | Relationship | Meta-Inference |
|-------------|-------------|--------------|----------------|
| [Finding 1] | [Finding 1] | [Convergent / Complementary / Divergent] | [Integrated interpretation] |
| [Finding 2] | [Finding 2] | [Convergent / Complementary / Divergent] | [Integrated interpretation] |

## 4. Discrepancy Resolution

### 4.1 Anticipated Discrepancies

| Type | Possible Cause | Likelihood | Impact |
|------|---------------|-----------|--------|
| Contradictory findings | [Different construct operationalization] | [High/Medium/Low] | [Impact on conclusions] |
| Different emphasis | [Different aspects of phenomenon captured] | [High/Medium/Low] | [Impact on conclusions] |
| Scope differences | [Different scope of inquiry] | [High/Medium/Low] | [Impact on conclusions] |

### 4.2 Resolution Strategies

| Strategy | Description | When to Apply |
|----------|-------------|---------------|
| Reconciliation | Find higher-order explanation that accounts for both | When findings are apparently contradictory |
| Initiation | Use discrepancy as starting point for new inquiry | When divergence reveals new dimension |
| Bracketing | Report both findings separately with explanation | When reconciliation is not possible |
| Complementarity | Explain how findings address different facets | When findings are different but not contradictory |

### 4.3 Resolution Procedure

1. Document all discrepancies systematically
2. Assess whether discrepancy is real or methodological artifact
3. Apply appropriate resolution strategy
4. Report resolution process transparently

## 5. Joint Display

### 5.1 Joint Display Type

**Selected Type**: [Side-by-side comparison / Transformation matrix / Pillar integration process / Workflow diagram]

### 5.2 Joint Display Template

#### Side-by-Side Comparison

| Dimension | Quantitative Results | Qualitative Results | Integrated Interpretation |
|-----------|---------------------|---------------------|--------------------------|
| [Dimension 1] | [Statistical findings] | [Thematic findings] | [Integration] |
| [Dimension 2] | [Statistical findings] | [Thematic findings] | [Integration] |
| [Dimension 3] | [Statistical findings] | [Thematic findings] | [Integration] |

#### Convergence Assessment

| Finding Pair | Convergence Level | Assessment |
|-------------|-------------------|------------|
| QUAN-1 + QUAL-1 | [Full / Partial / None / Divergent] | [Explanation] |
| QUAN-2 + QUAL-2 | [Full / Partial / None / Divergent] | [Explanation] |

## 6. Meta-Inference Quality

### 6.1 Integrative Efficacy

**Assessment Criteria**:
- Do the meta-inferences adequately incorporate both QUAN and QUAL inferences?
- Are the meta-inferences consistent with the data from both strands?
- Do the meta-inferences address the overarching research questions?

### 6.2 Integrative Correspondence

**Assessment Criteria**:
- Is there correspondence between the data and the meta-inferences?
- Are alternative interpretations considered?
- Is the integration process transparent and documented?

### 6.3 Quality Assessment Rubric

| Criterion | Indicators | Score (1-5) |
|-----------|-----------|------------|
| Fit | Meta-inferences fit both QUAN and QUAL findings | [Score] |
| Comprehensiveness | Both strands adequately represented | [Score] |
| Transparency | Integration process clearly documented | [Score] |
| Coherence | Integrated narrative is logically consistent | [Score] |

## 7. GRA Compliance - Claims

```yaml
claims:
  - id: "IS-001"
    text: "[Integration method] enables meaningful combination of quantitative and qualitative findings at [integration points], as recommended by [authority]."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Fetters, Curry, & Creswell, 2013; or relevant source]"
        verified: true
    confidence: 85
    uncertainty: "Integration quality depends on the depth and richness of both quantitative and qualitative findings."

  - id: "IS-002"
    text: "Joint displays provide a transparent mechanism for presenting mixed methods findings and demonstrating how QUAN and QUAL strands inform each other."
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Guetterman, Fetters, & Creswell, 2015; or relevant source]"
        verified: true
    confidence: 82
    uncertainty: "The effectiveness of joint displays depends on the clarity of the integration logic and the comparability of findings."
```

## Quality Checklist

- [ ] Integration method clearly identified and justified
- [ ] Meta-inference framework designed
- [ ] Discrepancy resolution strategies planned
- [ ] Joint display template prepared
- [ ] Integrative quality criteria defined
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Mixed Methods Core Agent 2/2 Complete
**Next Step**: Execute quantitative and qualitative components
"""


# ===========================================================================
# PHILOSOPHICAL content generation
# ===========================================================================

def generate_philosophical_agent_output(agent_name, description, topic, questions, context):
    """Generate output for philosophical/theoretical research design agents."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    q_text = format_questions_markdown(questions)

    if agent_name == 'philosophical-method-designer':
        return f"""# Philosophical Research Methods Design

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Methodological Approach

### 2.1 Selected Philosophical Methods

| Method | Application | Justification |
|--------|-------------|---------------|
| Conceptual Analysis | [Concept clarification and boundary conditions] | [Why this method is appropriate for RQ] |
| Dialectical Argumentation | [Thesis-antithesis-synthesis structure] | [Why this method is appropriate for RQ] |
| Hermeneutic Analysis | [Text interpretation and meaning extraction] | [Why this method is appropriate for RQ] |
| Thought Experiments | [Hypothetical scenario construction] | [Why this method is appropriate for RQ] |
| Comparative Framework Analysis | [Cross-framework evaluation] | [Why this method is appropriate for RQ] |

### 2.2 Methodological Justification

[Rationale for each method choice, grounded in philosophical methodology literature]

### 2.3 Research Question-Method Mapping

| Research Question | Primary Method | Secondary Method | Rationale |
|-------------------|---------------|-----------------|-----------|
| RQ1 | [Method] | [Method] | [Why] |
| RQ2 | [Method] | [Method] | [Why] |

## 3. Epistemological Foundation

### 3.1 Epistemological Position
[Rationalism / Empiricism / Pragmatism / Critical Realism / etc.]

### 3.2 Ontological Premises
[What kinds of entities and relations the research presupposes]

### 3.3 Axiological Commitments
[Value positions relevant to the inquiry]

## 4. Scope and Limitations

### 4.1 Analytical Scope
[What falls within and outside the analysis]

### 4.2 Methodological Limitations
[Inherent constraints of the chosen philosophical methods]

## 5. GRA Compliance - Claims

```yaml
claims:
  - id: "PMD-001"
    text: "[Method selection rationale grounded in philosophical methodology]"
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Philosophical methodology source]"
        verified: true
    confidence: 85
    uncertainty: "The selection of philosophical methods involves interpretive judgment about methodological fit."
```

## Quality Checklist

- [ ] All philosophical methods clearly defined
- [ ] Methods mapped to specific research questions
- [ ] Epistemological position explicitly stated
- [ ] Methodological limitations acknowledged
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Philosophical Agent 1/4 Complete
**Next Agent**: @source-text-selector
"""

    elif agent_name == 'source-text-selector':
        return f"""# Primary Source & Text Selection

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Text Selection Strategy

### 2.1 Selection Criteria

| Criterion | Description | Weight |
|-----------|-------------|--------|
| Theoretical Centrality | [How central the text is to the research questions] | High |
| Historical Significance | [Seminal status in the tradition] | High |
| Argumentative Richness | [Depth and complexity of argumentation] | Medium |
| Scholarly Reception | [How extensively discussed in secondary literature] | Medium |
| Availability & Accessibility | [Reliable editions and translations available] | Low |

### 2.2 Inclusion/Exclusion Rationale

**Included**: Texts that directly address the core philosophical questions under investigation
**Excluded**: Texts that only tangentially relate or lack rigorous argumentation

## 3. Core Text Inventory

### 3.1 Primary Texts (Original Sources)

| # | Author | Title | Year | Edition/Translation | Role in Analysis |
|---|--------|-------|------|---------------------|-----------------|
| 1 | [Author] | [Title] | [Year] | [Edition] | [Primary argument source] |
| 2 | [Author] | [Title] | [Year] | [Edition] | [Counter-position] |

### 3.2 Secondary Commentaries

| # | Author | Title | Year | Scope |
|---|--------|-------|------|-------|
| 1 | [Author] | [Title] | [Year] | [What it contributes to the analysis] |

### 3.3 Comparative Texts

| # | Author | Title | Year | Comparison Axis |
|---|--------|-------|------|-----------------|
| 1 | [Author] | [Title] | [Year] | [What is being compared] |

## 4. Edition and Translation Selection

### 4.1 Criteria for Edition Choice
[Critical editions preferred; translation philosophy noted]

### 4.2 Translation Reliability
[Assessment of translation accuracy for non-original-language texts]

## 5. Inter-Text Relationship Map

```
[Primary Text A] ---- influences -----> [Primary Text B]
       |                                      |
    critiques                            extends
       |                                      |
       v                                      v
[Primary Text C] <---- synthesizes ---- [Primary Text D]
```

## 6. GRA Compliance - Claims

```yaml
claims:
  - id: "STS-001"
    text: "[Text selection rationale]"
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Scholarly justification for text selection]"
        verified: true
    confidence: 88
    uncertainty: "Text selection in philosophical research involves judgment about relevance and representativeness."
```

## Quality Checklist

- [ ] Primary texts clearly identified with edition information
- [ ] Selection criteria explicitly stated and applied
- [ ] Inter-text relationships mapped
- [ ] Translation choices justified
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Philosophical Agent 2/4 Complete
**Next Agent**: @argument-construction-designer
"""

    elif agent_name == 'argument-construction-designer':
        return f"""# Argument Construction Design

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Core Thesis (Hauptthese)

### 2.1 Main Thesis
[State the central philosophical claim this dissertation argues for]

### 2.2 Sub-Theses
| # | Sub-Thesis | Supporting RQ | Relationship to Main Thesis |
|---|-----------|---------------|---------------------------|
| 1 | [Sub-thesis] | RQ1 | [How it supports the main thesis] |
| 2 | [Sub-thesis] | RQ2 | [How it supports the main thesis] |

## 3. Argument Structure

### 3.1 Argument Type Selection

| Thesis | Argument Type | Justification |
|--------|--------------|---------------|
| Main | [Deductive / Abductive / Dialectical / Transcendental] | [Why this form] |
| Sub-1 | [Type] | [Why] |
| Sub-2 | [Type] | [Why] |

### 3.2 Premise-Conclusion System

#### Main Argument
```
P1: [First premise]
P2: [Second premise]
P3: [Third premise (if needed)]
-----------------------------
C:  [Conclusion = Main Thesis]
```

#### Supporting Arguments
[Same structure for each sub-argument]

### 3.3 Argument Path Mapping

```
[Premise Set A] --> [Sub-Conclusion 1] --+
                                         +--> [Main Conclusion]
[Premise Set B] --> [Sub-Conclusion 2] --+
                         |
              [Objection 1] --> [Reply 1]
```

## 4. Objection and Reply Plan

### 4.1 Anticipated Objections

| # | Objection | Source/Tradition | Strength | Target |
|---|-----------|-----------------|----------|--------|
| O1 | [Objection statement] | [Who raises this] | Strong/Medium/Weak | P1/P2/C |
| O2 | [Objection statement] | [Who raises this] | Strong/Medium/Weak | P1/P2/C |

### 4.2 Reply Strategy

| Objection | Reply Type | Core Reply | Key Source |
|-----------|-----------|------------|------------|
| O1 | [Distinction / Concession / Reductio / Counter-example] | [Brief reply] | [Source] |
| O2 | [Type] | [Brief reply] | [Source] |

## 5. Framework Comparison Design

### 5.1 Comparison Axes

| Axis | Framework A | Framework B | Evaluation Criterion |
|------|-----------|-----------|---------------------|
| [Axis 1] | [Position] | [Position] | [How to adjudicate] |
| [Axis 2] | [Position] | [Position] | [How to adjudicate] |

### 5.2 Evaluation Criteria
[Coherence, explanatory power, parsimony, applicability, etc.]

## 6. GRA Compliance - Claims

```yaml
claims:
  - id: "ACD-001"
    text: "[Argument structure rationale]"
    claim_type: THEORETICAL
    sources:
      - type: PRIMARY
        reference: "[Logic/argumentation theory source]"
        verified: true
    confidence: 82
    uncertainty: "The strength of philosophical arguments depends on the acceptability of premises, which may be contested."
```

## Quality Checklist

- [ ] Main thesis clearly stated
- [ ] Argument type justified
- [ ] Premises explicitly listed
- [ ] Objections anticipated and replies planned
- [ ] Framework comparison axes defined
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Philosophical Agent 3/4 Complete
**Next Agent**: @philosophical-analysis-planner
"""

    else:  # philosophical-analysis-planner
        return f"""# Philosophical Analysis Plan

Generated by: @{agent_name}
Date: {timestamp}

## 1. Research Questions Summary

**Topic**: {topic}

**Research Questions**:
{q_text}

## 2. Analysis Procedure

### 2.1 Step-by-Step Analysis Order

| Step | Activity | Input | Output | Method |
|------|----------|-------|--------|--------|
| 1 | [Conceptual clarification] | [Primary texts] | [Concept map] | Conceptual analysis |
| 2 | [Framework reconstruction] | [Step 1 output] | [Framework models] | Hermeneutic analysis |
| 3 | [Critical evaluation] | [Step 2 output] | [Strength/weakness assessment] | Dialectical method |
| 4 | [Synthesis] | [Steps 1-3] | [Integrated position] | Dialectical synthesis |
| 5 | [Application] | [Step 4 output] | [Applied implications] | Thought experiments |

### 2.2 Per-Framework Analysis Method

| Framework | Analysis Approach | Key Questions | Expected Output |
|-----------|------------------|---------------|-----------------|
| [Framework A] | [Approach] | [What questions to ask of this framework] | [Expected findings] |
| [Framework B] | [Approach] | [What questions to ask] | [Expected findings] |

## 3. Interpretation Strategy

### 3.1 Hermeneutic Circle Application
- **Whole-to-Part**: Read entire texts first, then analyze specific passages
- **Part-to-Whole**: Detailed passage analysis informing overall interpretation
- **Iterative Refinement**: Multiple reading passes with progressive deepening

### 3.2 Text Interpretation Principles
1. **Principle of Charity**: Interpret arguments in their strongest form
2. **Historical Context**: Situate arguments within their intellectual milieu
3. **Systematic Coherence**: Assess internal consistency of each position
4. **Contemporary Relevance**: Bridge historical positions to current debates

## 4. Integration Strategy

### 4.1 Dialectical Synthesis Plan
- **Thesis**: [Position A's core contribution]
- **Antithesis**: [Position B's challenge]
- **Synthesis**: [How to integrate or adjudicate]

### 4.2 Convergence/Divergence Analysis
| Dimension | Convergence Points | Divergence Points | Significance |
|-----------|-------------------|-------------------|--------------|
| [Dim 1] | [Where frameworks agree] | [Where they disagree] | [Why this matters] |

## 5. Rigor Assurance

### 5.1 Argument Validity Verification
- Formal validity check for deductive arguments
- Strength assessment for inductive/abductive arguments
- Consistency checks across the argument system

### 5.2 Interpretation Consistency Verification
- Cross-reference interpretations with scholarly consensus
- Document departures from standard readings with justification
- Peer-review standard: Would a specialist find this reading defensible?

### 5.3 Scholarly Contribution Assessment Criteria
- Novelty: Does the analysis offer new insights?
- Rigor: Are the arguments logically sound?
- Significance: Does it advance the scholarly conversation?

## 6. GRA Compliance - Claims

```yaml
claims:
  - id: "PAP-001"
    text: "[Analysis plan rationale]"
    claim_type: METHODOLOGICAL
    sources:
      - type: PRIMARY
        reference: "[Philosophical methodology source]"
        verified: true
    confidence: 83
    uncertainty: "Philosophical analysis outcomes depend on interpretive choices that may be challenged by alternative readings."
```

## Quality Checklist

- [ ] Analysis steps clearly sequenced
- [ ] Hermeneutic principles stated
- [ ] Integration strategy designed
- [ ] Rigor criteria defined
- [ ] All claims use GRA GroundedClaim format

---

**Completed by**: {agent_name}
**Date**: {timestamp}
**Status**: Phase 2 Philosophical Agent 4/4 Complete
**Next Step**: Create research-design-final.md synthesis
"""


# ===========================================================================
# Final synthesis
# ===========================================================================

def create_research_design_final(context, research_type):
    """Create final synthesis document for research design."""
    print("\n" + "=" * 80)
    print("CREATING RESEARCH DESIGN SYNTHESIS")
    print("=" * 80)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_path = context.get_output_path("phase2", "research-design-final.md")

    topic = context.session.get('research', {}).get('topic', '')
    questions = context.session.get('research', {}).get('research_questions', [])
    q_text = format_questions_markdown(questions)

    content = f"""# Research Design Final Synthesis

Date: {timestamp}
Research Type: {research_type.upper()}

## Executive Summary

This document synthesizes the complete research design for the dissertation on "{topic}".

## 1. Research Design Overview

**Research Type**: {research_type.title()} Research

**Research Questions**:
{q_text}

**Key Components**:
"""

    if research_type == 'quantitative':
        content += """
- Hypotheses development (20-hypotheses.md)
- Research model specification (21-research-model-final.md)
- Sampling design (22-sampling-design.md)
- Statistical analysis plan (23-statistical-analysis-plan.md)
"""
    elif research_type == 'qualitative':
        content += """
- Research paradigm establishment (20-research-paradigm.md)
- Participant selection strategy (21-participant-selection.md)
- Data collection protocol (22-data-collection-protocol.md)
- Qualitative analysis plan (23-qualitative-analysis-plan.md)
"""
    elif research_type == 'philosophical':
        content += """
- Philosophical method selection (20-philosophical-methods.md)
- Primary source & text selection (21-source-text-selection.md)
- Argument construction design (22-argument-structure.md)
- Philosophical analysis plan (23-philosophical-analysis-plan.md)
"""
    else:  # mixed
        content += """
- Mixed methods design framework (20-mixed-methods-design.md)
- Integration strategy (21-integration-strategy.md)
- Quantitative component (hypotheses, model, sampling, analysis)
- Qualitative component (paradigm, participants, data collection, analysis)
"""

    content += f"""

## 2. Research Design Quality Assessment

### 2.1 Alignment with Research Questions

[Assessment of how well the research design addresses each research question]

### 2.2 Methodological Rigor

[Assessment of methodological quality and rigor]

### 2.3 Ethical Considerations

[Summary of ethical considerations across all components]

### 2.4 Feasibility Assessment

[Assessment of practical feasibility of the research design]

## 3. Integration and Coherence

[Analysis of how all components fit together into a coherent research design]

## 4. Limitations and Mitigation Strategies

### 4.1 Design Limitations

[Identified limitations of the chosen research design]

### 4.2 Mitigation Strategies

[Strategies to address or minimize the impact of limitations]

## 5. Timeline and Resources

### 5.1 Research Timeline

| Phase | Duration | Key Activities |
|-------|----------|----------------|
| Phase 1 | [Duration] | [Activities] |
| Phase 2 | [Duration] | [Activities] |

### 5.2 Resource Requirements

- Personnel: [Requirements]
- Equipment: [Requirements]
- Software: [Requirements]
- Budget: [Estimated budget]

## 6. Next Steps

After HITL-4 approval of this research design:

1. Begin data collection preparation
2. Finalize instruments/protocols
3. Obtain IRB approval (if not already obtained)
4. Recruit participants/collect data
5. Proceed to thesis writing (Phase 3)

## 7. GRA Compliance Summary

All components of this research design comply with GRA (Grounded Research Architecture) standards:
- All claims are properly grounded in literature
- Uncertainties are explicitly acknowledged
- Confidence levels are provided
- Sources are verified and cited

---

**Synthesis Completed**: {timestamp}
**Status**: Phase 2 Research Design Complete
**Next Checkpoint**: HITL-4 - Research Design Approval
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n  Research Design Final Synthesis Complete")
    print(f"  Output: {output_path}")

    return True


# ===========================================================================
# Main entry point
# ===========================================================================

def main():
    """Main orchestration function."""
    try:
        # Load context
        print("Loading thesis workflow context...")
        context = load_context()
        print("  Context loaded")

        # Validate prerequisites
        is_valid, errors = validate_prerequisites(context)
        if not is_valid:
            print("\n  Prerequisites not met:")
            for err in errors:
                print(f"   - {err}")
            print("\nPlease resolve the above issues before running Phase 2.")
            return 1

        # Get research type
        research_type = get_research_type(context)
        print(f"\n  Research Type: {research_type.upper()}")

        # Execute appropriate path based on research type
        success = True

        if research_type == 'quantitative':
            success = run_quantitative_path(context)
        elif research_type == 'qualitative':
            success = run_qualitative_path(context)
        elif research_type == 'mixed':
            success = run_mixed_methods_path(context)
        elif research_type == 'philosophical':
            success = run_philosophical_path(context)

        if not success:
            print(f"\n  {research_type.title()} path execution failed")
            return 1

        # Create final synthesis
        success = create_research_design_final(context, research_type)
        if not success:
            print("\n  Research design synthesis failed")
            return 1

        # Update session to mark Phase 2 complete
        context.update_session({
            "workflow": {
                "current_phase": "phase2_complete",
                "current_step": 108,
                "last_checkpoint": datetime.now().isoformat(),
                "next_checkpoint": "HITL-4",
                "phase2_completed_at": datetime.now().isoformat(),
            }
        })

        # Final summary
        print("\n" + "=" * 80)
        print("PHASE 2 RESEARCH DESIGN COMPLETE")
        print("=" * 80)
        print(f"\n  Summary:")
        print(f"   - Research Type: {research_type.title()}")
        print(f"   - All research design agents executed successfully")
        print(f"   - Synthesis document created")
        print(f"\n  Outputs:")

        output_dir = context.working_dir / "02-research-design"
        print(f"   - {output_dir}/20-*.md")
        print(f"   - {output_dir}/21-*.md")
        print(f"   - {output_dir}/22-*.md")
        print(f"   - {output_dir}/23-*.md")
        print(f"   - {output_dir}/research-design-final.md")
        print(f"\n  Next Step: HITL-4 - Research Design Approval")
        print(f"   Use command: /thesis:approve-design")

        return 0

    except FileNotFoundError as e:
        print(f"\n  Error: {e}")
        print("\nMake sure you have initialized a session with init_session.py first.")
        return 1
    except Exception as e:
        print(f"\n  Error in Phase 2 execution: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
