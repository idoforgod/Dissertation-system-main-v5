---
name: rlm-integration-guide
description: RLM 통합 가이드. subagent-creator와 skill-creator가 RLM 템플릿을 활용할 수 있도록 지원합니다.
---

# RLM Integration Guide for Agent/Skill Creation

## For subagent-creator

When creating new sub-agents, consider RLM mode if:

1. **Input size > 100K chars** - Multiple large files as input
2. **Quadratic complexity** - Pairwise comparisons needed
3. **Information-dense** - Synthesis, screening, validation tasks
4. **High information loss** - Standard mode would lose >30% context

### Template Selection

```python
# In subagent-creator workflow:

if should_use_rlm(agent_spec):
    template_path = ".claude/agents/templates/rlm-agent-template.md"
else:
    template_path = ".claude/agents/templates/standard-agent-template.md"

# Copy and customize template
```

### RLM Template Customization

```python
# Replace placeholders in rlm-agent-template.md:

# [AGENT_NAME] → actual agent name
# [AGENT_DESCRIPTION] → role description
# [필터링 패턴] → specific regex patterns
# [에이전트별 특화 프롬프트] → task-specific instructions
# [출력 요구사항] → output format requirements
```

### Quick RLM Check

```python
def should_use_rlm(agent_spec):
    """Determine if agent should use RLM"""
    indicators = [
        agent_spec.get('input_file_count', 0) > 4,
        agent_spec.get('total_input_size', 0) > 100000,
        agent_spec.get('task_type') in ['synthesis', 'screening', 'validation'],
        agent_spec.get('complexity') in ['linear', 'quadratic']
    ]
    return sum(indicators) >= 2  # 2+ indicators = use RLM
```

## For skill-creator

When creating skills that wrap agents, add RLM options:

### Skill Frontmatter

```yaml
---
name: my-skill
rlm_enabled: true  # Enable RLM support
rlm_auto_switch: true  # Auto-detect when to use RLM
rlm_threshold: 100000  # Character threshold for activation
---
```

### Skill Execution

```python
# In skill execution logic:

from pathlib import Path
from rlm_core import RLMOptimizer

# Check if RLM should be used
input_size = estimate_input_size(skill_context)

if skill_config.get('rlm_auto_switch') and input_size > skill_config.get('rlm_threshold', 100000):
    # Use RLM-enabled agent
    agent_name = f"{base_agent_name}-rlm"
    print(f"🔄 RLM Mode activated ({input_size:,} chars)")
else:
    # Use standard agent
    agent_name = base_agent_name

# Execute agent
execute_agent(agent_name, skill_context)
```

## Available RLM Agents

| Agent | RLM Version | Primary Benefit |
|-------|-------------|-----------------|
| synthesis-agent | synthesis-agent-rlm | 12 files, <10% loss |
| literature-searcher | literature-searcher-rlm | 1000+ papers |
| thesis-writer | thesis-writer-rlm | 23 files, 95% citation accuracy |
| unified-srcs-evaluator | unified-srcs-evaluator-rlm | 100+ claims, O(N²) |
| plagiarism-checker | plagiarism-checker-rlm | Full context comparison |
| conceptual-model-builder | conceptual-model-builder-rlm | 14 files |
| variable-relationship-analyst | variable-relationship-analyst-rlm | Quadratic checks |
| cross-validator | cross-validator-rlm | Wave gate validation |

## RLM Core Library

Location: `.claude/libs/rlm_core.py`

Key Classes:
- `RLMEnvironment`: REPL environment manager
- `RLMPatterns`: Emergent patterns (Figure 4a/4b/4c)
- `RLMOptimizer`: Cost estimation and optimization

Example Usage:

```python
from rlm_core import RLMEnvironment, RLMPatterns

context = {"file1.md": "content1", "file2.md": "content2"}
rlm = RLMEnvironment(context_data=context, model_preference="haiku")

# Filter with code
filtered = rlm.repl_env['grep_content'](content=context, pattern=r"pattern")

# Chunk and process
chunks = rlm.repl_env['chunk_by_size'](text=large_text, chunk_size=50000)
results = [rlm.repl_env['llm_query'](f"Process: {chunk}") for chunk in chunks]

# Get stats
print(rlm.get_stats())
```

## Auto-Switch Hook

Location: `.claude/hooks/pre-tool-use/rlm-context-monitor.py`

Automatically detects and injects RLM instructions when:
- Context size > 100K chars
- File count ≥ 4
- High information density for priority agents

## Cost Management

```python
from rlm_core import RLMOptimizer

# Before executing RLM agent
cost_est = RLMOptimizer.estimate_cost(
    input_size=total_chars,
    num_sub_calls=estimated_calls,
    model="haiku"
)

print(f"Estimated cost: ${cost_est['estimated_cost_usd']:.2f}")
print(f"Max expected: ${cost_est['max_expected_usd']:.2f}")

# Typical costs (Haiku):
# - synthesis-agent: $0.50-1.50
# - literature-searcher (1000 papers): $2-5
# - thesis-writer (per chapter): $1-3
# - unified-srcs-evaluator (100 claims): $1-2
```

## Best Practices

1. **Always filter first**: Use code (grep, regex) to reduce context before sub-LM calls
2. **Chunk smart**: Split at semantic boundaries (paragraphs, sections)
3. **Verify intermediate**: Check partial results before final aggregation
4. **Track costs**: Monitor sub-call counts to avoid runaway expenses
5. **Set recursion limits**: Default max_recursion_depth=2 is usually sufficient

## Testing RLM Agents

```python
# Test RLM agent locally
from rlm_core import RLMEnvironment

# Small test context
test_context = {
    "test1.md": "Sample content 1" * 1000,
    "test2.md": "Sample content 2" * 1000
}

rlm = RLMEnvironment(test_context, model_preference="haiku")

result = rlm.repl_env['llm_query']("Summarize the test context")
print(result)
print(rlm.get_stats())

# Expected: Low cost (<$0.10), fast execution
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| MAX_RECURSION_REACHED | Increase chunk_size to reduce sub-calls |
| SUB_CALL_TIMEOUT | Use smaller context or split task |
| HIGH_COST | Check sub-call count, use Haiku not Opus |
| INFORMATION_LOSS | Reduce chunk_size, increase overlap |

---

**Guide Version**: 1.0
**Last Updated**: 2026-01-20
**For**: Claude Code subagent-creator & skill-creator integration
