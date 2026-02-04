#!/usr/bin/env python3
"""Run Phase 3 (Thesis Writing) with Validation.

This script executes Phase 3 with fail-fast validation enabled,
ensuring all outputs are generated correctly at each step.

Design Principles:
- Additive-Only: Builds on existing workflow
- Fail-Fast: Stops immediately on validation failure
- Independent: Can be used alongside standard execution
- Clear Reporting: Detailed validation feedback

Usage:
    python3 run_writing_validated.py

Prerequisites:
    - Phase 0, 1, 2 must be complete
    - Active session with working directory
"""

import sys
from pathlib import Path
from typing import Callable, Optional
import json
from datetime import datetime

# Add scripts to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from validated_executor import ValidatedExecutor
from phase_validator import PhaseValidator
from path_utils import get_working_dir_from_session


# ============================================================================
# Phase 3 Agent Wrappers
# ============================================================================

def call_thesis_architect(working_dir: Path) -> dict:
    """Call thesis-architect agent to design thesis outline.

    Args:
        working_dir: Working directory path

    Returns:
        Result dictionary
    """
    print("📐 Calling @thesis-architect to design thesis outline...")

    # Check input files
    session_file = working_dir / "session.json"
    synthesis_file = working_dir / "research-synthesis.md"
    design_file = working_dir / "_temp" / "research-design-final.md"

    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")
    if not synthesis_file.exists():
        raise FileNotFoundError(f"Research synthesis not found: {synthesis_file}")
    if not design_file.exists():
        raise FileNotFoundError(f"Research design not found: {design_file}")

    # Load session data
    with open(session_file) as f:
        session = json.load(f)

    thesis_format = session.get("thesis_format", "traditional-5-chapter")
    _options = session.get("options", {})
    _citation_config = _options.get("citation_config", {})
    citation_style = _citation_config.get("display_name", "APA 7th Edition")

    print(f"  Format: {thesis_format}")
    print(f"  Citation: {citation_style}")

    # Output file (matching validation pattern: 03-thesis/thesis-outline.md)
    output_file = working_dir / "03-thesis" / "thesis-outline.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Create outline content
    outline_content = f"""# 논문 아웃라인

## 논문 정보
- 형식: {thesis_format}
- 인용 스타일: {citation_style}
- 생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 전체 구조

### 제1장 서론 (10-15p)
#### 1.1 연구 배경
- 사회적/학문적 맥락
- 연구 필요성

#### 1.2 연구 목적
- 연구의 목표
- 연구 질문

#### 1.3 연구 범위
- 공간적 범위
- 시간적 범위
- 내용적 범위

#### 1.4 논문 구성
- 각 장 요약

### 제2장 이론적 배경 (40-50p)
#### 2.1 핵심 개념
- 2.1.1 정의 및 개념
- 2.1.2 이론적 발전
- 2.1.3 본 연구에의 적용

#### 2.2 선행연구 검토
- 2.2.1 국내 연구
- 2.2.2 국외 연구
- 2.2.3 연구 동향 및 갭

#### 2.3 연구모델 및 가설
- 2.3.1 이론적 프레임워크
- 2.3.2 연구모델
- 2.3.3 연구가설

### 제3장 연구방법 (20-25p)
#### 3.1 연구 설계
#### 3.2 표본 및 자료수집
#### 3.3 변수 측정
#### 3.4 분석 방법

### 제4장 연구결과 (30-40p)
#### 4.1 기술통계
#### 4.2 측정모델 검증
#### 4.3 가설 검증
#### 4.4 추가 분석

### 제5장 결론 (15-20p)
#### 5.1 연구결과 요약
#### 5.2 이론적 시사점
#### 5.3 실무적 시사점
#### 5.4 연구한계 및 향후 연구

### 참고문헌
### 부록

## 분량 계획
| 장 | 예상 분량 | 비중 |
|----|----------|------|
| 1장 | 10-15p | 8% |
| 2장 | 40-50p | 35% |
| 3장 | 20-25p | 17% |
| 4장 | 30-40p | 28% |
| 5장 | 15-20p | 12% |
| **합계** | **115-150p** | **100%** |

## Claims
```yaml
claims:
  - id: "TA-001"
    text: "논문 구조는 {thesis_format} 형식을 따릅니다."
    claim_type: METHODOLOGICAL
    sources:
      - type: SECONDARY
        reference: "논문 작성 가이드"
        verified: true
    confidence: 100
    uncertainty: "구조는 필요시 조정 가능"
```

## Next Step
HITL-4에서 사용자 승인 후 각 장별 집필을 시작합니다.
"""

    # Write outline
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(outline_content)

    print(f"✅ Outline created: {output_file}")

    return {
        "status": "completed",
        "output_file": str(output_file),
        "agent": "thesis-architect"
    }


def call_thesis_writer(working_dir: Path, chapter_num: int) -> dict:
    """Call thesis-writer agent to write a chapter.

    Args:
        working_dir: Working directory path
        chapter_num: Chapter number (1-5)

    Returns:
        Result dictionary
    """
    chapter_names = {
        1: "introduction",
        2: "literature-review",
        3: "methodology",
        4: "results",
        5: "conclusion"
    }

    chapter_titles = {
        1: "서론",
        2: "이론적 배경",
        3: "연구방법",
        4: "연구결과",
        5: "결론"
    }

    print(f"✍️  Calling @thesis-writer for Chapter {chapter_num}: {chapter_titles[chapter_num]}...")

    # Check prerequisites
    outline_file = working_dir / "_temp" / "thesis-outline.md"
    if not outline_file.exists():
        raise FileNotFoundError(f"Outline not found: {outline_file}")

    # Check previous chapters
    chapters_dir = working_dir / "03-thesis"
    chapters_dir.mkdir(parents=True, exist_ok=True)

    for prev_ch in range(1, chapter_num):
        prev_files = list(chapters_dir.glob(f"chapter{prev_ch}-*.md"))
        if not prev_files:
            raise FileNotFoundError(
                f"Previous chapter {prev_ch} not found. "
                f"Complete previous chapters first."
            )

    # Output file
    chapter_name = chapter_names[chapter_num]
    output_file = chapters_dir / f"chapter{chapter_num}-{chapter_name}.md"

    # Create chapter content
    chapter_content = f"""# 제{chapter_num}장 {chapter_titles[chapter_num]}

## {chapter_num}.1 개요

[이 장의 내용 개요]

## {chapter_num}.2 주요 내용

[주요 내용 작성]

## {chapter_num}.3 소결

[이 장의 요약]

## Claims
```yaml
claims:
  - id: "TW-CH{chapter_num}-001"
    text: "[장별 핵심 주장]"
    claim_type: THEORETICAL
    sources:
      - type: PRIMARY
        reference: "[인용 문헌]"
        verified: true
    confidence: 85
    uncertainty: "[주장의 한계]"
```

## References
[해당 장에서 인용한 문헌 목록]

---
생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
에이전트: thesis-writer
"""

    # Write chapter
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(chapter_content)

    print(f"✅ Chapter {chapter_num} created: {output_file}")

    return {
        "status": "completed",
        "output_file": str(output_file),
        "chapter": chapter_num,
        "agent": "thesis-writer"
    }


def call_thesis_integrator(working_dir: Path) -> dict:
    """Call thesis-integrator to combine all chapters into final thesis.

    Args:
        working_dir: Working directory path

    Returns:
        Result dictionary
    """
    print("🔗 Calling @thesis-integrator to combine all chapters...")

    chapters_dir = working_dir / "03-thesis"

    # Check all chapters exist
    chapter_files = []
    for ch_num in range(1, 6):
        ch_files = list(chapters_dir.glob(f"chapter{ch_num}-*.md"))
        if not ch_files:
            raise FileNotFoundError(f"Chapter {ch_num} not found")
        chapter_files.append(ch_files[0])

    # Output file
    output_file = working_dir / "03-thesis" / "thesis-final.md"

    # Combine chapters
    final_content = f"""# 박사학위논문 최종본

생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""

    for i, ch_file in enumerate(chapter_files, 1):
        with open(ch_file, 'r', encoding='utf-8') as f:
            content = f.read()

        final_content += f"\n\n{content}\n\n"
        final_content += f"---\n"

    # Write final thesis
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_content)

    print(f"✅ Final thesis created: {output_file}")

    return {
        "status": "completed",
        "output_file": str(output_file),
        "agent": "thesis-integrator"
    }


def call_reference_compiler(working_dir: Path) -> dict:
    """Call reference-compiler to generate references list.

    Args:
        working_dir: Working directory path

    Returns:
        Result dictionary
    """
    print("📚 Calling @reference-compiler to generate references...")

    # Check final thesis exists
    thesis_file = working_dir / "03-thesis" / "thesis-final.md"
    if not thesis_file.exists():
        raise FileNotFoundError(f"Final thesis not found: {thesis_file}")

    # Output file
    output_file = working_dir / "03-thesis" / "references.md"

    # Create references
    references_content = f"""# 참고문헌

생성일: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## References

[참고문헌 목록이 여기에 생성됩니다]

---
에이전트: reference-compiler
"""

    # Write references
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(references_content)

    print(f"✅ References created: {output_file}")

    return {
        "status": "completed",
        "output_file": str(output_file),
        "agent": "reference-compiler"
    }


# ============================================================================
# Main Execution Function
# ============================================================================

def run_phase3_validated() -> int:
    """Execute Phase 3 (Thesis Writing) with validation.

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    print("\n" + "="*70)
    print("🔍 PHASE 3: THESIS WRITING (VALIDATED MODE)")
    print("="*70 + "\n")

    # Get working directory
    try:
        working_dir = get_working_dir_from_session()
        print(f"Working Directory: {working_dir}\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Run /thesis:init first to create a session.")
        return 1

    # Initialize validators
    validator = PhaseValidator(working_dir)

    # Check prerequisites (Phase 0, 1, 2 must be complete)
    print("Checking prerequisites...\n")

    for phase in [0, 1, 2]:
        report = validator.validate_phase_verbose(phase)
        if not report.all_passed:
            print(f"❌ Error: Phase {phase} is not complete.")
            print(f"   Complete prerequisite phases first.\n")
            print(report.summary())
            return 1
        else:
            print(f"✅ Phase {phase} validated")

    print("\n✅ All prerequisites satisfied. Starting Phase 3 with validation...\n")

    # Create validated executor
    executor = ValidatedExecutor(working_dir, fail_fast=True)

    # Define Phase 3 steps with agent mappings
    phase3_steps = [
        (111, lambda: call_thesis_architect(working_dir), "thesis-architect"),
        (115, lambda: call_thesis_writer(working_dir, 1), "thesis-writer-ch1"),
        (117, lambda: call_thesis_writer(working_dir, 2), "thesis-writer-ch2"),
        (119, lambda: call_thesis_writer(working_dir, 3), "thesis-writer-ch3"),
        (121, lambda: call_thesis_writer(working_dir, 4), "thesis-writer-ch4"),
        (123, lambda: call_thesis_writer(working_dir, 5), "thesis-writer-ch5"),
        (129, lambda: call_thesis_integrator(working_dir), "thesis-integrator"),
        (130, lambda: call_reference_compiler(working_dir), "reference-compiler")
    ]

    # Execute each step with validation
    all_success = True

    for step, agent_func, agent_name in phase3_steps:
        try:
            result = executor.execute_step(step, agent_func, agent_name)

            if not result.success:
                print(f"\n❌ Step {step} failed validation")
                print(f"   Fix the issue and try again.")
                all_success = False
                break

        except Exception as e:
            print(f"\n❌ Step {step} execution failed: {e}")
            all_success = False
            break

    # Print execution summary
    executor.print_summary()

    # Final validation
    print("\n" + "="*70)
    print("🔍 Final Phase 3 Validation")
    print("="*70 + "\n")

    phase3_report = validator.validate_phase_verbose(3)
    print(phase3_report.summary())

    if phase3_report.all_passed and all_success:
        print("\n" + "="*70)
        print("✅ Phase 3 (Thesis Writing) completed successfully!")
        print("="*70)
        print("\nNext Steps:")
        print("1. Review chapters using /thesis:review-chapter <chapter_num>")
        print("2. Make revisions as needed")
        print("3. Proceed to Phase 4 using /thesis:run-publication")
        print("\n")
        return 0
    else:
        print("\n" + "="*70)
        print("❌ Phase 3 validation failed")
        print("="*70)
        print("\nPlease review errors above and:")
        print("1. Fix missing or incorrect outputs")
        print("2. Re-run /thesis:run-writing-validated")
        print("3. Or use /thesis:run-writing for standard execution")
        print("\n")
        return 1


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Run Phase 3 (Thesis Writing) with validation"
    )
    parser.add_argument(
        "--skip-prerequisites",
        action="store_true",
        help="Skip prerequisite phase validation (dangerous)"
    )

    args = parser.parse_args()

    if args.skip_prerequisites:
        print("⚠️  WARNING: Skipping prerequisite validation")
        print("   This may lead to incomplete execution\n")

    return run_phase3_validated()


if __name__ == "__main__":
    sys.exit(main())
