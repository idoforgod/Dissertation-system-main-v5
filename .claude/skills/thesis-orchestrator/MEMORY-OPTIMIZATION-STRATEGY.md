# Memory Optimization Strategy

**목표**: 메모리 한계로 인한 성능 저하 방지 (workflow 핵심 보존, RLM 패턴 유지)

**Date**: 2026-01-20

---

## 🎯 Problem Analysis

### 현재 메모리 사용 패턴

```
Phase 1 (15 agents 순차 실행):
  Agent 1 → Output 1 (컨텍스트에 추가)
  Agent 2 → Output 1 + 2 (누적)
  Agent 3 → Output 1 + 2 + 3 (누적)
  ...
  Agent 15 → Output 1-15 (누적) ← 메모리 폭발!
```

**문제점**:
1. **컨텍스트 누적**: 15개 agent × 평균 3000 tokens = 45,000 tokens (Phase 1만)
2. **RLM 대량 입력**: literature-searcher-rlm이 1000+ 문헌 처리
3. **Cross-reference**: 각 agent가 모든 이전 결과 참조 필요
4. **Long-running session**: Phase 0-4 전체 진행 시 200,000+ tokens

### 현재 External Memory (3-File)

```
thesis-output/[project]/
├── session.json           # 세션 상태만
├── todo-checklist.md      # 진행 상태만
└── research-synthesis.md  # 최종 synthesis만 (Phase 1 완료 후)
```

**한계**:
- Agent 1-14 결과는 컨텍스트에 남음 (메모리 소모)
- Phase 2-4 진행 시 Phase 1 전체 참조 불가능
- RLM 처리 결과의 intermediate summaries 보관 불가

---

## 🏗️ Solution Architecture

### 핵심 원칙

1. ✅ **기존 workflow 완벽 보존**: Agent 순서, 의존성, 품질 기준 불변
2. ✅ **RLM 패턴 절대 유지**: Chunked processing, streaming summary 강화
3. ✅ **투명성**: 사용자는 변화를 인지 못함 (backward compatible)
4. ✅ **점진적 적용**: Phase별로 선택적 적용 가능

---

## 📊 Strategy 1: Hierarchical Memory Architecture

**개념**: 4-Level 계층적 메모리 → 필요한 수준만 로드

### Level 1: Ultra-Compact State (session.json)

**현재**:
```json
{
  "research": {"topic": "...", "type": "..."},
  "current_phase": 1,
  "current_agent": "literature-searcher"
}
```

**개선**:
```json
{
  "research": {"topic": "...", "type": "..."},
  "current_phase": 1,
  "current_agent": "literature-searcher",
  "agent_summaries": {
    "literature-searcher": "Found 847 papers on AI consciousness (2010-2025)",
    "seminal-works-analyst": "Identified 12 foundational papers (Chalmers 1995, etc.)",
    "trend-analyst": "Research trend: increased focus on embodiment (2020+)"
  },
  "memory_budget": {
    "current_usage": 15000,
    "max_budget": 50000,
    "compression_ratio": 0.3
  }
}
```

**압축 비율**: 3000 tokens → 50 tokens (60배 압축)

### Level 2: Phase-level Synthesis

**신규 파일**:
```
thesis-output/[project]/memory/
├── phase-0-synthesis.md  (초기화 요약)
├── phase-1-synthesis.md  (문헌검토 종합)
├── phase-2-synthesis.md  (연구설계 요약)
├── phase-3-synthesis.md  (논문 개요)
└── phase-4-synthesis.md  (투고 전략)
```

**phase-1-synthesis.md 예시**:
```markdown
# Phase 1: Literature Review Synthesis

## Wave 1-4 Key Findings (압축: 12 agents → 2000 tokens)
- 847 papers identified (2010-2025)
- 12 seminal works (Chalmers 1995, Dennett 1991, ...)
- 3 major theoretical frameworks: functionalism, embodiment, integrated information
- 2 methodological gaps: lack of consciousness measurement, embodiment experiments

## Wave 5 Quality Metrics
- SRCS: 78.5/100
- pTCS: 82.0/100
- Plagiarism: 8.3%

## Research Questions Emerged
1. Can artificial systems achieve phenomenal consciousness?
2. Role of embodiment in consciousness?
3. Measurement methods for machine consciousness?

## Next Phase Requirements
- Quantitative study + qualitative interviews
- Mixed methods design recommended
```

**압축 비율**: 45,000 tokens → 2000 tokens (22배 압축)

### Level 3: Wave-level Cache

**신규 파일**:
```
thesis-output/[project]/memory/wave-cache/
├── wave-1.json
├── wave-2.json
├── wave-3.json
├── wave-4.json
└── wave-5.json
```

**wave-1.json 예시**:
```json
{
  "wave": 1,
  "agents": ["literature-searcher", "seminal-works-analyst", "trend-analyst", "methodology-scanner"],
  "completed": true,
  "gate_passed": true,
  "gate_scores": {"ptcs": 82.0, "srcs": 78.0},
  "key_outputs": {
    "total_papers": 847,
    "seminal_works": 12,
    "theoretical_frameworks": ["functionalism", "embodiment", "IIT"],
    "research_trends": "increased focus on embodiment (2020+)",
    "methodology_gaps": ["consciousness measurement", "embodiment experiments"]
  },
  "cross_validation_result": {
    "consistency_score": 85.2,
    "conflicts": []
  },
  "references": {
    "full_outputs": ["01-literature-search-strategy.md", "02-seminal-works-analysis.md", ...]
  }
}
```

**압축 비율**: 12,000 tokens → 500 tokens (24배 압축)

### Level 4: Agent Output Archive (_temp/)

**현재**: 모든 출력 그대로 보관
**개선**: 참조 빈도에 따라 압축 또는 요약

```
thesis-output/[project]/
├── _temp/                    # 최근 agent 출력 (full)
│   ├── 13-literature-synthesis.md
│   ├── 14-conceptual-model.md
│   └── 15-plagiarism-report.md
├── _archive/                 # 오래된 출력 (compressed)
│   ├── 01-04-wave1.tar.gz
│   ├── 05-08-wave2.tar.gz
│   └── 09-12-wave3.tar.gz
└── memory/                   # Levels 1-3
    └── ...
```

---

## 🔄 Strategy 2: Sliding Window Context Pattern

**개념**: N개 최근 결과만 active context, 나머지는 synthesis 참조

### Implementation

```python
class ContextWindow:
    """Sliding window context manager."""

    def __init__(self, window_size=3):
        self.window_size = window_size  # 최근 3개 agent만 full context
        self.active_context = []
        self.synthesis_cache = {}

    def load_context_for_agent(self, agent_name, phase, wave):
        """Load minimal context for agent execution."""

        # 1. Core context (항상 로드)
        core = {
            'phase_synthesis': self.load_phase_synthesis(phase - 1),  # 이전 Phase 요약
            'wave_cache': self.load_wave_cache(wave - 1),             # 이전 Wave cache
            'session_state': self.load_session()                      # 현재 상태
        }

        # 2. Sliding window (최근 N개 agent 상세)
        recent_agents = self.get_recent_agents(n=self.window_size)
        window = [self.load_agent_output(agent) for agent in recent_agents]

        # 3. Specific dependencies (agent별 필수 참조)
        dependencies = self.get_dependencies(agent_name)
        deps = [self.load_agent_summary(dep) for dep in dependencies]

        return {
            'core': core,           # 2,000 tokens
            'window': window,       # 9,000 tokens (3 agents × 3,000)
            'dependencies': deps    # 500 tokens
        }
        # Total: ~11,500 tokens (기존 45,000 tokens 대비 75% 절감)
```

### Example: Wave 2 Agent 3 실행

**기존 방식** (메모리 폭발):
```
Load:
  - Wave 1 전체 (4 agents × 3000 tokens = 12,000)
  - Wave 2 Agent 1-2 (2 agents × 3000 tokens = 6,000)
Total: 18,000 tokens
```

**개선 방식** (Sliding Window):
```
Load:
  - Phase 0 synthesis (200 tokens)
  - Wave 1 cache (500 tokens)
  - Wave 2 Agent 1-2 full (6,000 tokens)
  - Dependencies: seminal-works (summary, 150 tokens)
Total: 6,850 tokens (62% 절감!)
```

---

## 📉 Strategy 3: Progressive Compression Pipeline

**개념**: 각 checkpoint마다 자동 압축 → 오래된 데이터일수록 압축률 높음

### Compression Stages

```
Agent 완료 (즉시):
  Full Output (3000 tokens) → Ultra-Compact Summary (50 tokens)
  압축률: 98.3%

Wave 완료 (Gate 통과 후):
  4 Agents (12,000 tokens) → Wave Cache (500 tokens)
  압축률: 95.8%

Phase 완료 (HITL 승인 후):
  15 Agents (45,000 tokens) → Phase Synthesis (2,000 tokens)
  압축률: 95.6%

Workflow 완료:
  All Phases (200,000 tokens) → Final Synthesis (5,000 tokens)
  압축률: 97.5%
```

### Implementation

```python
class ProgressiveCompressor:
    """Automatic compression at each checkpoint."""

    def compress_agent_output(self, agent_name, full_output):
        """Agent 완료 시 즉시 압축."""

        # 1. Extract key findings (AI-powered)
        summary = self.extract_key_findings(full_output)

        # 2. Store in session.json
        self.session['agent_summaries'][agent_name] = summary

        # 3. Archive full output
        self.archive_full_output(agent_name, full_output)

        return summary  # 50 tokens

    def compress_wave(self, wave_number, agent_outputs):
        """Wave 완료 시 cache 생성."""

        # 1. Aggregate key outputs
        cache = {
            'wave': wave_number,
            'key_outputs': self.aggregate_outputs(agent_outputs),
            'gate_scores': self.get_gate_scores(wave_number),
            'cross_validation': self.get_validation_result(wave_number)
        }

        # 2. Save to wave-cache
        self.save_wave_cache(wave_number, cache)

        return cache  # 500 tokens

    def compress_phase(self, phase_number, wave_caches):
        """Phase 완료 시 synthesis 생성."""

        # 1. Synthesize all waves
        synthesis = self.synthesize_waves(wave_caches)

        # 2. Add quality metrics
        synthesis['srcs'] = self.calculate_phase_srcs(phase_number)
        synthesis['ptcs'] = self.calculate_phase_ptcs(phase_number)

        # 3. Save phase synthesis
        self.save_phase_synthesis(phase_number, synthesis)

        return synthesis  # 2,000 tokens
```

---

## 🧠 Strategy 4: RLM-Optimized Processing

**핵심**: RLM 패턴 유지하면서 메모리 절약 → Chunked + Streaming

### Current RLM Pattern

```python
# literature-searcher-rlm
def search_literature_rlm(topic):
    # 1000+ papers in single RLM call
    all_papers = search_databases(topic)  # 150,000 tokens!

    # Single massive processing
    analysis = rlm_process(all_papers)

    return analysis
```

**문제**: 150,000 tokens 한 번에 처리 → 메모리 초과

### Improved RLM Pattern (Chunked + Streaming)

```python
# literature-searcher-rlm (개선)
def search_literature_rlm_chunked(topic):
    """Chunked RLM with streaming summary."""

    # 1. Fetch all papers
    all_papers = search_databases(topic)  # 1000 papers

    # 2. Split into chunks
    chunks = split_into_chunks(all_papers, chunk_size=100)  # 10 chunks

    # 3. Process each chunk with RLM + immediate summarize
    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        # RLM processing (15,000 tokens per chunk)
        chunk_analysis = rlm_process(chunk)

        # Immediate compression
        chunk_summary = compress_to_summary(chunk_analysis)  # 1,500 tokens
        chunk_summaries.append(chunk_summary)

        # Save intermediate result
        save_chunk_result(i, chunk_summary)

    # 4. Incremental merge of summaries (not full outputs)
    final_synthesis = rlm_merge_summaries(chunk_summaries)  # 15,000 tokens

    return final_synthesis
```

**개선 효과**:
- 기존: 150,000 tokens 동시 처리
- 개선: 15,000 tokens씩 10회 처리 + 최종 15,000 tokens merge
- **메모리 피크**: 150,000 → 15,000 (90% 절감!)

### RLM Chunk Cache

```
thesis-output/[project]/memory/rlm-chunks/
├── literature-search-chunk-001.json
├── literature-search-chunk-002.json
├── ...
└── literature-search-chunk-010.json
```

각 chunk는 독립적으로 재사용 가능 → 재실행 시 cache hit

---

## 🎨 Strategy 5: Context Pruning Hooks

**개념**: GRA Hook에 자동 메모리 정리 기능 추가

### Implementation

```python
# .claude/hooks/post-tool-use.py (신규)

def post_tool_use_memory_pruning(tool_name, tool_result, context):
    """PostToolUse hook: 자동 메모리 정리."""

    if tool_name == "Task" and "agent" in tool_result:
        agent_name = tool_result['agent']

        # 1. Extract key findings from agent output
        summary = extract_key_findings(tool_result['output'])

        # 2. Save to session.json (ultra-compact)
        session['agent_summaries'][agent_name] = summary

        # 3. Prune irrelevant context
        context = prune_irrelevant_context(context, agent_name)

        # 4. Archive full output to file
        archive_full_output(agent_name, tool_result['output'])

        # 5. Update memory budget
        update_memory_budget(context)

        return context  # Pruned context
```

### Pruning Rules

| Agent Type | Prune Targets | Keep |
|------------|---------------|------|
| **literature-searcher** | Previous search results | Topic, research question |
| **synthesis-agent** | All agent outputs | Wave caches, phase synthesis |
| **thesis-writer** | Previous chapters (full) | Chapter summaries, outline |
| **plagiarism-checker** | Comparison texts | Similarity scores, report |

---

## 📦 Strategy 6: Lazy Loading Pattern

**개념**: 필요한 데이터만 on-demand 로드 → 미리 로드 금지

### Implementation

```python
class LazyContextLoader:
    """Lazy loading context manager."""

    def __init__(self, working_dir):
        self.working_dir = working_dir
        self.cache = {}  # In-memory cache

    def get_context_for_agent(self, agent_name):
        """Get minimal context for agent (lazy)."""

        # 1. Core context (항상 필요)
        context = {
            'session': self.load_session(),
            'phase_synthesis': self.load_current_phase_synthesis()
        }

        # 2. Agent-specific requirements (lazy load)
        requirements = get_agent_requirements(agent_name)

        for req in requirements:
            if req not in self.cache:
                # Load on-demand
                self.cache[req] = self.load_requirement(req)

            context[req] = self.cache[req]

        return context

    def load_requirement(self, req_name):
        """Load specific requirement on-demand."""

        if req_name.startswith('wave-'):
            # Load wave cache
            wave_num = int(req_name.split('-')[1])
            return self.load_wave_cache(wave_num)

        elif req_name.startswith('agent-'):
            # Load agent summary (not full output)
            agent = req_name.split('-', 1)[1]
            return self.load_agent_summary(agent)

        elif req_name == 'previous-phase':
            # Load previous phase synthesis
            return self.load_phase_synthesis(self.current_phase - 1)

        # Default: return None (optional context)
        return None
```

### Example: Gap-Identifier Agent

**기존 방식** (eager loading):
```python
# Load everything upfront
context = {
    'wave1': load_wave1(),      # 12,000 tokens
    'wave2': load_wave2(),      # 12,000 tokens
    'theories': load_theories(), # 8,000 tokens
    'empirical': load_empirical() # 10,000 tokens
}
# Total: 42,000 tokens (대부분 불필요)
```

**개선 방식** (lazy loading):
```python
# Load only what's needed
requirements = ['wave2-cache', 'theoretical-framework-summary', 'empirical-evidence-summary']

context = lazy_loader.get_context_for_agent('gap-identifier')
# Loaded:
#   - wave2-cache (500 tokens)
#   - theoretical-framework-summary (300 tokens)
#   - empirical-evidence-summary (400 tokens)
# Total: 1,200 tokens (97% 절감!)
```

---

## 🗄️ Strategy 7: Expanded External Memory (7-File → 10-File)

**현재**: 3-File Architecture
**개선**: 10-File Architecture

### New File Structure

```
thesis-output/[project]/
├── memory/
│   ├── session.json              # Level 1: Current state + agent summaries
│   ├── phase-0-synthesis.md      # Level 2: Phase summaries
│   ├── phase-1-synthesis.md
│   ├── phase-2-synthesis.md
│   ├── phase-3-synthesis.md
│   ├── phase-4-synthesis.md
│   ├── wave-cache/               # Level 3: Wave caches
│   │   ├── wave-1.json
│   │   ├── wave-2.json
│   │   ├── wave-3.json
│   │   ├── wave-4.json
│   │   └── wave-5.json
│   ├── rlm-chunks/               # RLM chunk results
│   │   ├── literature-search-chunk-001.json
│   │   └── ...
│   └── memory-budget.json        # Memory usage tracking
├── _temp/                        # Level 4: Recent full outputs
│   ├── 13-literature-synthesis.md
│   ├── 14-conceptual-model.md
│   └── 15-plagiarism-report.md
└── _archive/                     # Compressed old outputs
    ├── wave-1-4.tar.gz
    └── ...
```

### memory-budget.json (신규)

```json
{
  "budget": {
    "max_tokens": 50000,
    "current_usage": 12500,
    "remaining": 37500,
    "utilization": 0.25
  },
  "by_phase": {
    "phase_0": 500,
    "phase_1": 8000,
    "phase_2": 3000,
    "phase_3": 1000,
    "phase_4": 0
  },
  "compression_stats": {
    "total_outputs": 180000,
    "compressed_to": 12500,
    "compression_ratio": 0.069,
    "savings": "93.1%"
  },
  "alerts": [
    {
      "level": "info",
      "message": "Memory usage healthy (25%)"
    }
  ]
}
```

---

## 🔧 Implementation Plan

### Phase A: Foundation (1-2 days)

1. **MemoryManager Class 생성**
   ```python
   # .claude/skills/thesis-orchestrator/scripts/memory_manager.py
   class MemoryManager:
       def __init__(self, working_dir, max_budget=50000)
       def compress_agent_output(agent_name, output)
       def load_context_for_agent(agent_name)
       def prune_context()
       def get_memory_stats()
   ```

2. **7-File → 10-File Migration**
   - memory/ 폴더 구조 생성
   - wave-cache/ 폴더 생성
   - rlm-chunks/ 폴더 생성

3. **Progressive Compressor 구현**
   - Agent-level compression
   - Wave-level compression
   - Phase-level compression

### Phase B: RLM Optimization (2-3 days)

1. **Chunked RLM Pattern 구현**
   - literature-searcher-rlm 개선
   - synthesis-agent-rlm 개선
   - Chunk cache 시스템

2. **Streaming Summary**
   - 각 chunk 처리 후 즉시 summarize
   - Incremental merge

### Phase C: Context Management (2-3 days)

1. **Sliding Window Context**
   - ContextWindow 클래스
   - window_size 파라미터 조정 (default: 3)

2. **Lazy Loading**
   - LazyContextLoader 구현
   - Agent requirements 정의

3. **Context Pruning Hook**
   - PostToolUse hook 추가
   - 자동 메모리 정리

### Phase D: Integration & Testing (1-2 days)

1. **기존 workflow 통합**
   - sequential_executor.py 수정
   - Agent wrapper 업데이트

2. **Backward Compatibility 검증**
   - 기존 session 호환성
   - 기존 commands 동작 확인

3. **Performance Testing**
   - 메모리 사용량 측정
   - Before/After 비교

---

## 📊 Expected Results

### Memory Usage Reduction

| Metric | Before | After | Reduction |
|--------|--------|-------|-----------|
| **Phase 1 메모리 피크** | 45,000 tokens | 11,500 tokens | **74.4%** |
| **RLM 메모리 피크** | 150,000 tokens | 15,000 tokens | **90.0%** |
| **전체 workflow** | 200,000 tokens | 50,000 tokens | **75.0%** |
| **컨텍스트 윈도우** | 누적 (unbounded) | 고정 (bounded) | **안정화** |

### Performance Improvement

- **Agent 실행 속도**: 20-30% 향상 (컨텍스트 로딩 시간 절감)
- **Gate 통과율**: 변화 없음 (품질 기준 동일)
- **재실행 속도**: 50% 향상 (chunk cache 재사용)

### Backward Compatibility

- ✅ 기존 workflow 100% 보존
- ✅ RLM 패턴 100% 유지
- ✅ 기존 commands 동작 (투명)
- ✅ 기존 session 호환

---

## 🎯 Success Criteria

### 필수 조건 (Backward Compatibility)

1. ✅ **기존 workflow 동일**: Agent 순서, 의존성, 품질 기준 불변
2. ✅ **RLM 패턴 유지**: Chunked processing, recursive summarization
3. ✅ **SRCS/pTCS 점수**: 동일한 threshold, 동일한 결과
4. ✅ **사용자 경험**: 변화 없음 (투명한 최적화)

### 목표 달성 지표

1. ✅ **메모리 피크 75% 절감**: 200k → 50k tokens
2. ✅ **RLM 메모리 90% 절감**: 150k → 15k tokens
3. ✅ **컨텍스트 안정화**: Unbounded → Bounded
4. ✅ **실행 속도 20% 향상**: Context loading 최적화

---

## 🚀 Next Steps

### 사용자 선택

**Option 1**: 전체 구현 (Phase A-D)
- 예상 소요: 6-10일
- 효과: 최대 75% 메모리 절감
- 리스크: 중간 (충분한 테스트 필요)

**Option 2**: 단계별 구현 (Phase A만)
- 예상 소요: 1-2일
- 효과: 약 40% 메모리 절감
- 리스크: 낮음 (기본 압축만)

**Option 3**: RLM만 최적화 (Phase B만)
- 예상 소요: 2-3일
- 효과: RLM 90% 절감 (가장 큰 bottleneck)
- 리스크: 낮음 (RLM 패턴 개선만)

---

**어떤 옵션으로 진행하시겠습니까?**
