# Context Optimization Plan for Mode E

**작성일**: 2026-01-28
**상태**: ✅ Design Complete → Ready for Implementation

---

## 문제 분석

### 현재 상황
```yaml
컨텍스트 사용량: 82,750 / 200,000 tokens (41%)
실패 원인: "Prompt is too long" - Task tool이 agent 정의 전체를 로드

Agent 파일 크기:
  - paper-research-orchestrator.md: 1,045 lines
  - paper-analyzer.md: 856 lines
  - gap-identifier.md: ~600 lines (예상)
  - hypothesis-generator.md: ~600 lines (예상)
  - design-proposer.md: ~700 lines (예상)
  - feasibility-assessor.md: ~500 lines (예상)
  - proposal-integrator.md: ~500 lines (예상)

총 Agent 정의 크기: ~4,800 lines → ~100,000+ tokens (추정)
```

### 근본 원인
1. **Verbose Agent Definitions**: 상세한 프레임워크, 예시, 작성 가이드가 agent 정의에 포함
2. **Orchestrator Overhead**: Master orchestrator가 6개 subagent 정의를 모두 참조
3. **No Context Management**: 각 Stage 완료 후 컨텍스트 정리 없음

---

## 해결 방안 (3단계)

### Phase 1: 즉시 실행 (오늘)

**Orchestrator 우회 - 직접 실행 방식**

```yaml
approach: "각 Stage를 개별 Python 스크립트로 실행"

workflow:
  stage_1_paper_analysis:
    executor: "Bash + Python"
    script: ".claude/skills/thesis-orchestrator/scripts/run_paper_analyzer.py"
    input: "{output_dir}/00-paper-based-design/uploaded-paper.pdf"
    output: "{output_dir}/00-paper-based-design/paper-deep-analysis.md"
    context_load: "minimal (only paper content)"

  stage_2_gap_identification:
    executor: "Bash + Python"
    script: ".claude/skills/thesis-orchestrator/scripts/run_gap_identifier.py"
    input: "{output_dir}/00-paper-based-design/paper-deep-analysis.md"
    output: "{output_dir}/00-paper-based-design/strategic-gap-analysis.md"
    context_load: "minimal (only previous output)"

  # ... repeat for stages 3-6

benefits:
  - "No orchestrator overhead"
  - "Each stage runs independently"
  - "Context resets between stages"
  - "Easier debugging and recovery"

implementation_time: "2-3 hours"
```

**새로운 스크립트 파일**:
```python
# .claude/skills/thesis-orchestrator/scripts/run_paper_analyzer.py
"""
Standalone script to run Stage 1 (Paper Analysis) without orchestrator.
"""

import sys
from pathlib import Path
from anthropic import Anthropic

def analyze_paper(paper_path: str, output_path: str):
    """Run paper analysis using Claude API directly."""

    # Read paper
    with open(paper_path, 'rb') as f:
        paper_content = f.read()

    # Load minimal prompt (not full agent definition)
    prompt = """
    Analyze this research paper using the following framework:

    1. Research Context (RQ, Theory, Paradigm, Literature)
    2. Methodology Evaluation (Design, Sample, Data Collection, Analysis)
    3. Findings Synthesis (Main findings, Effect sizes, Significance)
    4. Critical Evaluation (Strengths, Weaknesses, Limitations)

    Output: 5-7 pages, GRA compliant (cite page numbers), pTCS 70+
    """

    # Call Claude API
    client = Anthropic()
    response = client.messages.create(
        model="claude-opus-4-5-20251101",
        max_tokens=16000,
        messages=[{
            "role": "user",
            "content": prompt + "\n\nPaper content:\n" + paper_content.decode('utf-8')
        }]
    )

    # Save output
    with open(output_path, 'w') as f:
        f.write(response.content[0].text)

    print(f"✅ Paper analysis complete: {output_path}")

if __name__ == "__main__":
    analyze_paper(sys.argv[1], sys.argv[2])
```

---

### Phase 2: 단기 최적화 (1-2일)

**Agent 정의 파일 축약**

```yaml
strategy: "핵심 로직만 agent 정의에 유지, 나머지는 references로 분리"

current_structure:
  paper-analyzer.md:
    - name, description, tools, model (10 lines)
    - Core Principles (20 lines)
    - Analysis Framework (400 lines) ← TOO VERBOSE
    - Quality Standards (100 lines)
    - Execution Guide (150 lines) ← TOO VERBOSE
    - Examples (150 lines) ← TOO VERBOSE

optimized_structure:
  paper-analyzer.md:
    - name, description, tools, model (10 lines)
    - Core Task (50 lines) ← ESSENTIAL ONLY
    - Output Format (30 lines)
    - Quality Gates (20 lines)
    - Total: ~110 lines (87% reduction)

  references/paper-analyzer-framework.md:
    - Detailed analysis framework (moved here)
    - Examples and templates (moved here)
    - Execution guides (moved here)

benefits:
  - "Agent definition: 850 lines → 110 lines (87% reduction)"
  - "Context load: ~100k tokens → ~15k tokens (85% reduction)"
  - "Still accessible via references when needed"

implementation:
  - Refactor all 7 agent files (orchestrator + 6 subagents)
  - Create references/ directory for detailed guides
  - Update agent calls to reference external guides if needed

implementation_time: "4-6 hours"
```

**최적화 후 Agent 정의 예시**:
```markdown
---
name: paper-analyzer
description: Deep analysis of research papers (Stage 1)
tools: Read(*), Write(*), WebSearch(*)
model: opus
---

# Paper Analyzer

Analyze research papers using a 4-section framework.

## Core Task

1. **Research Context** (1-2 pages)
   - Research question and theoretical framework
   - Paradigm and literature positioning

2. **Methodology Evaluation** (1-2 pages)
   - Design, sample, data collection, analysis techniques
   - Validity assessment (internal, external, construct)

3. **Findings Synthesis** (1-2 pages)
   - Main findings, effect sizes, statistical/practical significance

4. **Critical Evaluation** (1-2 pages)
   - Theoretical contribution
   - Strengths and weaknesses (acknowledged and unacknowledged)

## Output Format

```markdown
# Deep Analysis: [Paper Title]

## 1. Research Context
[Analysis with page citations]

## 2. Methodology Evaluation
[Analysis with page citations]

## 3. Findings Synthesis
[Analysis with specific statistics]

## 4. Critical Evaluation
[Critical assessment]

## References
[All citations]
```

## Quality Gates

- **GRA Compliance**: All claims cite page numbers (Author, Year, p.X)
- **pTCS Target**: Claim-level 70+, Agent-level 75+
- **Length**: 5-7 pages (3,000-5,000 words)
- **Critical Stance**: Identify unacknowledged limitations

## References

For detailed framework and examples, see:
- `references/paper-analyzer-framework.md` (full analysis framework)
- `references/paper-analyzer-examples.md` (before/after examples)
```

**축약 효과**:
- 원본: 856 lines → 최적화: ~110 lines
- 컨텍스트 절감: ~85%

---

### Phase 3: 중장기 최적화 (1주)

**Orchestrator 재설계 - Lightweight Coordinator**

```yaml
current_orchestrator:
  role: "Master coordinator with full subagent definitions"
  size: 1,045 lines
  approach: "Task tool로 subagent 호출"
  context_load: "모든 subagent 정의 로드"

optimized_orchestrator:
  role: "Lightweight coordinator with minimal logic"
  size: ~150 lines
  approach: "Bash scripts + API calls (orchestrator 우회)"
  context_load: "None (직접 실행)"

new_architecture:
  orchestrator.sh:
    description: "Bash script that runs stages sequentially"

    pseudocode: |
      #!/bin/bash

      # Stage 1
      python3 run_paper_analyzer.py $PAPER_PATH $OUTPUT_DIR

      # Stage 2
      python3 run_gap_identifier.py $OUTPUT_DIR/paper-deep-analysis.md $OUTPUT_DIR

      # Stage 3
      python3 run_hypothesis_generator.py $OUTPUT_DIR/strategic-gap-analysis.md $OUTPUT_DIR

      # ... stages 4-6

      # HITL Checkpoint
      echo "📋 HITL-1: Review integrated proposal at $OUTPUT_DIR/integrated-research-proposal.md"

  benefits:
    - "No context overhead (Bash doesn't use Claude context)"
    - "Simple, debuggable, fast"
    - "Easy to pause/resume at any stage"
    - "No 'Prompt too long' errors"

implementation:
  - Write orchestrator.sh
  - Create run_*.py for each stage
  - Update /thesis:start paper-upload to call orchestrator.sh
  - Deprecate paper-research-orchestrator.md agent

implementation_time: "1-2 days"
```

---

## 메모리 최적화 전략 통합

기존 `MEMORY-OPTIMIZATION-STRATEGY.md`와 통합:

```yaml
existing_strategies:
  - RLM (Recursive Language Model) for large inputs
  - Context snapshots for recovery
  - Incremental processing

new_strategies:
  - Agent definition minification
  - Orchestrator bypass (direct execution)
  - Reference-based documentation

combined_approach:
  phase0_mode_e:
    method: "Direct execution (Bash + Python)"
    reason: "6 stages × large agents = context explosion"

  phase1_literature:
    method: "RLM agents for synthesis tasks"
    reason: "Wave 4 synthesis needs all 12 previous outputs"

  phase3_writing:
    method: "RLM + Context snapshots"
    reason: "Chapter writing needs all previous context"
```

---

## 구현 계획

### Week 1: 즉시 실행 (Priority 1)

**Day 1 (오늘)**:
- [ ] orchestrator.sh 작성
- [ ] run_paper_analyzer.py 작성
- [ ] Stage 1 테스트 실행

**Day 2**:
- [ ] run_gap_identifier.py 작성
- [ ] run_hypothesis_generator.py 작성
- [ ] Stages 2-3 테스트 실행

**Day 3**:
- [ ] run_design_proposer.py 작성
- [ ] run_feasibility_assessor.py 작성
- [ ] run_proposal_integrator.py 작성
- [ ] Full workflow 테스트 (Stage 1-6)

### Week 2: 단기 최적화 (Priority 2)

**Day 4-5**:
- [ ] Agent 정의 파일 7개 리팩토링
- [ ] references/ 디렉토리 생성 및 상세 가이드 이동
- [ ] 컨텍스트 사용량 측정 및 비교

**Day 6-7**:
- [ ] 최적화된 agent 정의로 전체 테스트
- [ ] 문서 업데이트 (SKILL.md, README.md)

### Week 3: 중장기 최적화 (Priority 3)

**Day 8-10**:
- [ ] Orchestrator 완전 제거 및 orchestrator.sh로 대체
- [ ] /thesis:start paper-upload 커맨드 업데이트
- [ ] End-to-end 테스트 (Mode E 전체)

**Day 11-12**:
- [ ] 다른 Phase (Phase 1-4) 최적화 적용
- [ ] RLM 통합 확인
- [ ] 전체 시스템 통합 테스트

---

## 예상 효과

```yaml
before_optimization:
  context_usage:
    orchestrator: "~20k tokens"
    6_subagents: "~80k tokens"
    total: "~100k tokens (50% of limit)"

  result: "Prompt too long" errors

after_phase1:
  context_usage:
    bash_orchestrator: "0 tokens (no Claude context)"
    python_scripts: "minimal (~5k per stage)"
    total: "~5k tokens per stage (2.5%)"

  result: "✅ No errors, fast execution"

after_phase2:
  context_usage:
    minified_agents: "~15k tokens (if using Task tool)"
    total: "~15k tokens (7.5%)"

  result: "✅ 85% reduction, Task tool usable again"

after_phase3:
  context_usage:
    orchestrator_sh: "0 tokens"
    direct_api_calls: "~3k per stage"
    total: "~3k tokens per stage (1.5%)"

  result: "✅ Optimal, production-ready"
```

---

## 다음 단계

1. **즉시 실행**: orchestrator.sh + run_*.py 스크립트 작성 (오늘)
2. **테스트**: 현재 논문으로 Stage 1-6 실행 검증 (내일)
3. **단기 최적화**: Agent 정의 리팩토링 시작 (이번 주)

---

**작성자**: Claude Code
**검토 필요**: @thesis-orchestrator 시스템 아키텍트
**우선순위**: 🔴 Critical (시스템 동작 불가 상태)
