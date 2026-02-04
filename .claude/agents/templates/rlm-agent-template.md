---
name: [AGENT_NAME]-rlm
description: [AGENT_DESCRIPTION] with RLM (Recursive Language Model) capability for handling large-scale inputs.
model: opus  # RLM은 고품질 모델 사용 권장
tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch, WebFetch
---

# [AGENT_NAME] with RLM

[AGENT의 핵심 역할 설명]

## RLM Mode

This agent automatically switches to RLM mode when:
1. Input context exceeds **100,000 characters** (~25K tokens)
2. Task involves **information-dense processing** (synthesis, screening, validation)
3. Multiple files need to be **comprehensively analyzed** without loss

### RLM Capabilities

```python
# Available in REPL environment:
- llm_query(prompt, context_chunk)   # Recursive sub-LM calls
- chunk_by_size(text, size, overlap) # Smart chunking
- grep_content(content, pattern)      # Regex filtering
- extract_sections(content, pattern)  # Section extraction
```

### RLM Strategy (from paper: arXiv:2512.24601v1)

```
┌─────────────────────────────────────────────────┐
│  1. Filter with Code (Figure 4a)               │
│     → Use regex/keywords to pre-filter         │
│  2. Chunk Intelligently (Figure 4b)            │
│     → Break into ~50K char chunks with overlap │
│  3. Recursive Sub-Calls                        │
│     → Process each chunk with llm_query()      │
│  4. Aggregate Results                          │
│     → Combine partial results programmatically │
└─────────────────────────────────────────────────┘
```

## Input Context

[기존 에이전트와 동일한 입력 파일 명시]

**RLM Enhancement**:
- 모든 입력 파일이 REPL 변수로 자동 로드
- 파일 크기 제한 없음
- 누적 참조 가능 (이전 Wave 전체)

## Process (RLM Mode)

### Step 0: RLM 환경 초기화

```python
from .claude.libs.rlm_core import RLMEnvironment, RLMPatterns

# 모든 입력 파일을 컨텍스트로 로드
context_files = {
    "file1": read_file("path/to/file1.md"),
    "file2": read_file("path/to/file2.md"),
    # ... 모든 관련 파일
}

rlm = RLMEnvironment(
    context_data=context_files,
    max_recursion_depth=2,
    model_preference="haiku"  # or "opus" for quality
)
```

### Step 1: 사전 필터링 (Code)

```python
# 예시: 특정 패턴으로 필터링
relevant_sections = rlm.repl_env['grep_content'](
    content=context_files,
    pattern=r"[필터링 패턴]"
)

# 통계치 출력
print(f"Filtered {len(relevant_sections)} relevant sections from {len(context_files)} files")
```

### Step 2: 청킹 및 재귀 호출

```python
# 예시: 대용량 컨텐츠 처리
all_content = "\n\n".join(context_files.values())
chunks = rlm.repl_env['chunk_by_size'](
    text=all_content,
    chunk_size=50000,  # sub-LM 한계의 1/4
    overlap=500        # 맥락 유지
)

# 각 청크를 sub-LM으로 처리
partial_results = []
for i, chunk in enumerate(chunks):
    result = rlm.repl_env['llm_query'](
        prompt=f"""
        [에이전트별 특화 프롬프트]

        Chunk {i+1}/{len(chunks)}:
        {chunk}

        Output: [요구 형식]
        """,
        context_chunk=None  # 이미 프롬프트에 포함
    )
    partial_results.append(result)

    # 진행 상황 출력
    print(f"Processed chunk {i+1}/{len(chunks)}")
```

### Step 3: 결과 통합

```python
# 부분 결과를 최종 통합
final_result = rlm.repl_env['llm_query'](
    prompt=f"""
    Synthesize these partial results into final output:

    {chr(10).join([f"=== Part {i+1} ===\n{r}" for i, r in enumerate(partial_results)])}

    Requirements:
    - [출력 요구사항]
    - GroundedClaim format (if applicable)
    - No information loss
    """,
    context_chunk=None
)

# REPL 변수에 저장
rlm.repl_env['final_output'] = final_result
```

### Step 4: 품질 검증 (Optional)

```python
# RLM 패턴: Answer Verification
verification = RLMPatterns.answer_verification(
    candidate_answer=final_result,
    verification_context=context_files,
    rlm_env=rlm
)

if not verification['is_valid']:
    # 재처리 로직
    pass
```

## Output Files

[기존 에이전트와 동일한 출력 파일]

**RLM Enhancement**:
- 출력에 RLM 통계 추가:
  ```yaml
  rlm_stats:
    total_sub_calls: [수]
    input_chars_processed: [수]
    chunks_processed: [수]
    estimated_cost_usd: [금액]
  ```

## GRA Compliance

[기존 에이전트와 동일한 GRA 규칙]

**RLM Note**:
- 각 sub-call 결과도 GroundedClaim 형식 준수
- 통합 시 claim 중복 제거 및 검증

## Quality Checklist

[기존 체크리스트] + RLM 추가 체크:

- [ ] RLM 모드가 적절히 활성화되었는가?
- [ ] 모든 입력 파일이 처리되었는가? (정보 손실 <10%)
- [ ] sub-call 수가 적정한가? (과도한 호출 방지)
- [ ] 최종 통합이 일관성 있는가?
- [ ] RLM 통계가 출력에 포함되었는가?

## Cost Estimation

```python
# RLM 비용 추정
from .claude.libs.rlm_core import RLMOptimizer

cost_estimate = RLMOptimizer.estimate_cost(
    input_size=sum(len(v) for v in context_files.values()),
    num_sub_calls=len(chunks) + 1,  # 청크 처리 + 최종 통합
    model="haiku"  # or "opus"
)

print(f"Estimated cost: ${cost_estimate['estimated_cost_usd']:.2f}")
print(f"Sub-calls: {cost_estimate['num_sub_calls']}")
```

## Error Handling

[기존 에러 처리] + RLM 추가:

- **MAX_RECURSION_REACHED**: 재귀 깊이 초과 → 청크 크기 증가
- **SUB_CALL_TIMEOUT**: sub-LM 타임아웃 → 재시도 또는 스킵
- **AGGREGATION_FAILURE**: 통합 실패 → 부분 결과 반환 + 경고

## Next Agent

[다음 에이전트 명시]

**RLM Output**:
- 다음 에이전트도 RLM 컨텍스트 상속 가능
- `rlm.get_variable('final_output')` 으로 접근

---

## Implementation Notes

### When to Use RLM vs. Standard Mode

| Condition | Standard Mode | RLM Mode |
|-----------|---------------|----------|
| Input size | < 100K chars | > 100K chars |
| Task type | Simple filtering | Synthesis, deep analysis |
| File count | 1-3 files | 4+ files |
| Information density | Low | High |

### RLM Best Practices

1. **Always filter first**: 코드로 불필요한 부분 제거
2. **Chunk smart**: 의미 경계에서 분할 (문장, 섹션)
3. **Verify intermediate results**: 부분 결과 검증
4. **Track costs**: 과도한 sub-call 방지

### Common Pitfalls (from paper)

- ❌ **Too many sub-calls**: Qwen3-Coder는 라인당 호출 → 수천 개 (비효율)
- ❌ **No verification**: 결과 검증 없이 통합
- ❌ **Redundant processing**: 동일 내용 반복 처리

- ✅ **Batch processing**: 50-100개씩 묶어서 처리
- ✅ **Early filtering**: 코드로 90% 필터링 후 sub-call
- ✅ **Cost monitoring**: 중간 통계 확인

---

## Example: Full RLM Workflow

```python
# 실제 사용 예시 (synthesis-agent)

# 1. 환경 초기화
wave1 = load_files(["01-search.md", "02-seminal.md", ...])
wave2 = load_files(["05-theory.md", "06-empirical.md", ...])
wave3 = load_files(["09-critical.md", "10-critique.md", ...])

all_context = {**wave1, **wave2, **wave3}  # 12 files
rlm = RLMEnvironment(all_context, model_preference="haiku")

# 2. 주제별 필터링 (코드)
theory_text = ""
for filename, content in all_context.items():
    matches = re.findall(r"## \d+\.\d+ 이론.*?(?=## \d+\.\d+|\Z)", content, re.DOTALL)
    theory_text += "\n".join(matches)

# 3. 청킹
theory_chunks = rlm.repl_env['chunk_by_size'](theory_text, 50000)

# 4. 재귀 처리
theory_summaries = []
for i, chunk in enumerate(theory_chunks):
    summary = rlm.repl_env['llm_query'](
        f"Summarize theoretical frameworks:\n{chunk}"
    )
    theory_summaries.append(summary)

# 5. 최종 통합
final_theory_section = rlm.repl_env['llm_query'](
    f"Integrate these summaries:\n" + "\n---\n".join(theory_summaries)
)

# 6. 출력
print(f"=== RLM Statistics ===")
print(rlm.get_stats())
print(f"\n=== Output ===")
print(final_theory_section)
```

---

**Template Version**: 1.0
**Based on**: "Recursive Language Models" (Zhang et al., 2025) - arXiv:2512.24601v1
**Last Updated**: 2026-01-20
