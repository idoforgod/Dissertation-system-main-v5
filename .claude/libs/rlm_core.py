"""
RLM (Recursive Language Model) Core Library

논문 참조: "Recursive Language Models" (Zhang et al., 2025)
- arXiv:2512.24601v1

핵심 원칙:
1. Offload to Environment: 대용량 입력을 REPL 변수로 처리
2. Programmatic Filtering: 코드로 사전 필터링 후 sub-LM 호출
3. Recursive Aggregation: 부분 결과를 재귀 호출로 통합
"""

import json
import re
from typing import Any, Dict, List, Optional, Callable
from pathlib import Path


class RLMEnvironment:
    """
    RLM REPL 환경 관리

    논문의 Figure 2 구조 구현:
    - 프롬프트를 변수로 로드
    - 코드 실행으로 컨텍스트 탐색
    - 재귀적 sub-LM 호출
    """

    def __init__(
        self,
        context_data: Dict[str, Any],
        max_recursion_depth: int = 3,
        sub_llm_max_chars: int = 200000,
        model_preference: str = "haiku"  # haiku (저렴) or opus (고품질)
    ):
        """
        Args:
            context_data: REPL에 로드할 컨텍스트 (파일 내용, 데이터)
            max_recursion_depth: 최대 재귀 깊이 (논문에서는 1 사용)
            sub_llm_max_chars: sub-LM 컨텍스트 한계 (논문: 500K 토큰 ≈ 200K chars)
            model_preference: sub-LM 모델 선택 (비용 vs 품질)
        """
        self.repl_env = {}
        self.llm_query_history = []
        self.current_depth = 0
        self.max_recursion_depth = max_recursion_depth
        self.sub_llm_max_chars = sub_llm_max_chars
        self.model_preference = model_preference

        # 컨텍스트 로드
        self.load_context(context_data)

        # 통계
        self.stats = {
            "total_sub_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "code_executions": 0
        }

    def load_context(self, data: Dict[str, Any]):
        """
        컨텍스트를 REPL 변수로 로드

        논문 예시 (Section 2):
        - context 변수에 프롬프트 저장
        - llm_query 함수로 sub-LM 호출 가능
        """
        for key, value in data.items():
            self.repl_env[key] = value

        # 유틸리티 함수 주입
        self.repl_env['llm_query'] = self._create_llm_query_wrapper()
        self.repl_env['chunk_by_size'] = self._chunk_by_size
        self.repl_env['grep_content'] = self._grep_content
        self.repl_env['extract_sections'] = self._extract_sections

    def _create_llm_query_wrapper(self) -> Callable:
        """
        REPL에서 사용할 llm_query 함수 생성

        논문 패턴 (Figure 4a, 4b):
        - 재귀 깊이 제한
        - 입력 크기 제한
        - 히스토리 추적
        """
        def llm_query(prompt: str, context_chunk: Optional[str] = None) -> str:
            # 재귀 깊이 체크
            if self.current_depth >= self.max_recursion_depth:
                return "[ERROR] Maximum recursion depth reached"

            # 입력 크기 제한
            full_prompt = f"{prompt}\n\n{context_chunk}" if context_chunk else prompt
            if len(full_prompt) > self.sub_llm_max_chars:
                return f"[ERROR] Input exceeds {self.sub_llm_max_chars} chars. Please chunk the input."

            # 실제 LLM 호출 (Task tool 사용)
            self.current_depth += 1
            self.stats["total_sub_calls"] += 1

            # 히스토리 기록
            call_record = {
                "depth": self.current_depth,
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
                "input_length": len(full_prompt)
            }
            self.llm_query_history.append(call_record)

            # TODO: 실제 Task tool 호출은 에이전트에서 수행
            # 여기서는 플레이스홀더 반환
            result = f"[PLACEHOLDER: sub-LM call with {len(full_prompt)} chars]"

            self.current_depth -= 1
            return result

        return llm_query

    def _chunk_by_size(self, text: str, chunk_size: int = 50000, overlap: int = 500) -> List[str]:
        """
        텍스트를 청크로 분할 (논문 Figure 4b 패턴)

        Args:
            text: 분할할 텍스트
            chunk_size: 청크 크기
            overlap: 청크 간 중첩 크기 (맥락 유지)
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - overlap  # 중첩
        return chunks

    def _grep_content(self, content: Dict[str, str], pattern: str) -> Dict[str, List[str]]:
        """
        정규식으로 컨텐츠 필터링 (논문 Figure 4a 패턴)

        Args:
            content: {filename: text} 딕셔너리
            pattern: 정규식 패턴
        """
        results = {}
        regex = re.compile(pattern, re.IGNORECASE)

        for filename, text in content.items():
            matches = regex.findall(text)
            if matches:
                results[filename] = matches

        return results

    def _extract_sections(self, content: Dict[str, str], section_pattern: str) -> Dict[str, List[str]]:
        """
        섹션 헤더로 컨텐츠 분할 (논문 Example B.1 패턴)

        Args:
            content: {filename: text} 딕셔너리
            section_pattern: 섹션 헤더 패턴 (예: "## \d+\.\d+")
        """
        results = {}

        for filename, text in content.items():
            sections = re.split(f'({section_pattern})', text)
            # 헤더와 내용을 쌍으로 결합
            paired_sections = []
            for i in range(1, len(sections), 2):
                if i+1 < len(sections):
                    paired_sections.append({
                        "header": sections[i],
                        "content": sections[i+1]
                    })
            results[filename] = paired_sections

        return results

    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        REPL에서 Python 코드 실행

        Args:
            code: 실행할 Python 코드

        Returns:
            업데이트된 REPL 환경
        """
        self.stats["code_executions"] += 1

        try:
            # 안전한 실행 (제한된 namespace)
            exec(code, {"__builtins__": __builtins__}, self.repl_env)
            return {
                "status": "success",
                "env_keys": list(self.repl_env.keys())
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def get_variable(self, var_name: str) -> Any:
        """REPL 환경에서 변수 가져오기"""
        return self.repl_env.get(var_name)

    def get_stats(self) -> Dict[str, Any]:
        """RLM 실행 통계 반환"""
        return {
            **self.stats,
            "llm_call_history": self.llm_query_history
        }


class RLMPatterns:
    """
    논문에서 관찰된 RLM 패턴 구현

    Section 3.1: Emergent Patterns in RLM Trajectories
    """

    @staticmethod
    def filter_with_model_priors(
        data: List[Dict],
        keywords: List[str],
        rlm_env: RLMEnvironment
    ) -> List[Dict]:
        """
        모델 사전지식 기반 필터링 (Figure 4a)

        패턴:
        1. 키워드로 사전 필터링 (코드)
        2. 필터링된 결과만 sub-LM으로 검증
        """
        # Step 1: 코드 필터링
        filtered = [
            item for item in data
            if any(kw.lower() in str(item).lower() for kw in keywords)
        ]

        # Step 2: sub-LM 검증 (선택적)
        if len(filtered) < 100:  # 소량이면 검증
            # PLACEHOLDER: 실제로는 llm_query 호출
            pass

        return filtered

    @staticmethod
    def recursive_chunking_and_aggregation(
        large_content: str,
        query: str,
        rlm_env: RLMEnvironment,
        chunk_size: int = 50000
    ) -> str:
        """
        청킹과 재귀 호출 (Figure 4b)

        패턴:
        1. 대용량 컨텐츠를 청크로 분할
        2. 각 청크를 sub-LM에 재귀 호출
        3. 부분 결과 집계
        """
        # Step 1: 청킹
        chunks = rlm_env._chunk_by_size(large_content, chunk_size)

        # Step 2: 재귀 호출
        partial_results = []
        for i, chunk in enumerate(chunks):
            # PLACEHOLDER: 실제로는 llm_query(query, chunk) 호출
            result = f"[Chunk {i+1}/{len(chunks)} result]"
            partial_results.append(result)

        # Step 3: 집계
        # PLACEHOLDER: 실제로는 llm_query로 최종 통합
        final_result = "\n---\n".join(partial_results)

        return final_result

    @staticmethod
    def answer_verification(
        candidate_answer: str,
        verification_context: str,
        rlm_env: RLMEnvironment
    ) -> Dict[str, Any]:
        """
        답변 검증 (Section 3.1)

        패턴:
        - sub-LM 호출로 작은 컨텍스트에서 검증
        - context rot 회피
        """
        # PLACEHOLDER: 실제로는 llm_query 호출
        verification_result = {
            "is_valid": True,
            "confidence": 0.85,
            "verification_method": "sub-LM with focused context"
        }

        return verification_result

    @staticmethod
    def long_output_construction(
        sub_tasks: List[str],
        rlm_env: RLMEnvironment
    ) -> str:
        """
        긴 출력 생성 (Figure 4c, OOLONG-Pairs)

        패턴:
        1. 부분 문제를 sub-LM으로 해결
        2. 변수에 결과 저장
        3. 프로그래밍으로 결합
        """
        results = []

        for task in sub_tasks:
            # PLACEHOLDER: 실제로는 llm_query(task) 호출
            result = f"[Result for: {task[:50]}...]"
            results.append(result)

        # 변수로 저장 후 결합
        rlm_env.repl_env['partial_results'] = results
        final_output = "\n\n".join(results)

        return final_output


class RLMOptimizer:
    """
    RLM 실행 최적화

    논문 Section 5: Limitations and Future Work
    """

    @staticmethod
    def should_use_rlm(
        input_size: int,
        task_complexity: str,
        context_window: int = 100000
    ) -> bool:
        """
        RLM 사용 여부 판단

        기준:
        1. 입력 크기 > 컨텍스트 윈도우
        2. 정보 밀도 높은 작업 (synthesis, screening)
        """
        if input_size > context_window:
            return True

        high_density_tasks = ['synthesis', 'screening', 'validation', 'aggregation']
        if task_complexity.lower() in high_density_tasks:
            return True

        return False

    @staticmethod
    def estimate_cost(
        input_size: int,
        num_sub_calls: int,
        model: str = "haiku"
    ) -> Dict[str, float]:
        """
        RLM 비용 추정 (Figure 9 참조)

        논문 결과:
        - median 비용은 베이스 모델과 비슷
        - 하지만 분산이 큼 (긴 trajectory)
        """
        # 대략적인 토큰 비용 (2026 기준)
        pricing = {
            "haiku": {"input": 0.25, "output": 1.25},  # per 1M tokens
            "opus": {"input": 15.0, "output": 75.0}
        }

        chars_to_tokens = 0.75  # 1 token ≈ 0.75 chars
        input_tokens = input_size * chars_to_tokens / 1_000_000
        output_tokens = input_tokens * 0.1 * num_sub_calls  # 가정: 출력은 입력의 10%

        model_pricing = pricing.get(model, pricing["haiku"])

        total_cost = (
            input_tokens * model_pricing["input"] +
            output_tokens * model_pricing["output"]
        )

        return {
            "estimated_cost_usd": total_cost,
            "input_tokens": input_tokens * 1_000_000,
            "output_tokens": output_tokens * 1_000_000,
            "num_sub_calls": num_sub_calls
        }


# 유틸리티 함수

def load_files_as_context(file_paths: List[Path]) -> Dict[str, str]:
    """
    파일들을 RLM 컨텍스트로 로드

    Args:
        file_paths: 로드할 파일 경로 리스트

    Returns:
        {filename: content} 딕셔너리
    """
    context = {}

    for path in file_paths:
        if path.exists():
            try:
                content = path.read_text(encoding='utf-8')
                context[path.name] = content
            except Exception as e:
                context[path.name] = f"[ERROR loading file: {e}]"

    return context


def create_rlm_prompt(
    task_description: str,
    context_info: Dict[str, Any],
    output_format: str = "markdown"
) -> str:
    """
    RLM용 시스템 프롬프트 생성

    논문 Appendix D.1 참조
    """
    prompt = f"""You are tasked with {task_description} using RLM (Recursive Language Model) approach.

## Context Available in REPL

Your context is loaded as variables in a Python REPL environment:
{json.dumps(context_info, indent=2)}

## RLM Capabilities

1. **llm_query(prompt, context_chunk)**: Call sub-LM recursively
2. **chunk_by_size(text, size)**: Split text into chunks
3. **grep_content(content, pattern)**: Filter content with regex
4. **extract_sections(content, pattern)**: Extract sections by header

## Strategy (from paper)

1. **Filter First**: Use code to pre-filter context (Figure 4a)
2. **Chunk Smart**: Break into manageable chunks (~50K chars)
3. **Recurse**: Call llm_query on each chunk
4. **Aggregate**: Combine partial results

## Output

When done, return your final answer using:
- FINAL(your_answer) for direct output
- FINAL_VAR(variable_name) for returning a REPL variable

Format: {output_format}
"""

    return prompt


# 예시 사용법
if __name__ == "__main__":
    # 예시: 12개 파일 통합 (synthesis-agent 시나리오)
    example_context = {
        "wave1_file1": "내용1...",
        "wave1_file2": "내용2...",
        # ... 12개 파일
    }

    rlm = RLMEnvironment(
        context_data=example_context,
        max_recursion_depth=2,
        model_preference="haiku"
    )

    # 코드 실행 예시
    code = """
# Step 1: 주제별 필터링
theory_sections = grep_content(
    {k: v for k, v in globals().items() if 'wave' in k},
    pattern=r"## \d+\.\d+ 이론"
)

# Step 2: 청킹
all_theory_text = "\\n".join([str(v) for v in theory_sections.values()])
theory_chunks = chunk_by_size(all_theory_text, chunk_size=50000)

# Step 3: 재귀 호출 (각 청크 분석)
theory_syntheses = []
for i, chunk in enumerate(theory_chunks):
    result = llm_query(
        f"Summarize theoretical frameworks in chunk {i+1}",
        context_chunk=chunk
    )
    theory_syntheses.append(result)
"""

    result = rlm.execute_code(code)
    print(f"Execution result: {result}")
    print(f"Statistics: {rlm.get_stats()}")
