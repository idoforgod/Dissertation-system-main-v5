---
tags: [thesis, writing, validation, phase3]
description: Run Phase 3 (Thesis Writing) with validation enabled
context: fork
agent: general-purpose
---

# Run Writing (Validated)

Phase 3 (논문 작성)을 검증 기능이 활성화된 상태로 실행합니다.

## Usage

```bash
/thesis:run-writing-validated
```

## What This Command Does

이 명령어는 기존 `/thesis:run-writing`과 동일한 작업을 수행하되, **fail-fast validation**이 추가됩니다:

### Standard Flow (기존):
1. 아웃라인 설계 (thesis-architect)
2. 챕터 1 작성 (thesis-writer)
3. 챕터 2 작성 (thesis-writer)
4. 챕터 3 작성 (thesis-writer)
5. 챕터 4 작성 (thesis-writer)
6. 챕터 5 작성 (thesis-writer)
7. 최종 논문 통합 (thesis-integrator)
8. 참고문헌 생성 (reference-compiler)

### Validated Flow (새로운):
1. 아웃라인 설계 ✅ **→ 검증: outline 파일 존재 확인**
2. 챕터 1 작성 ✅ **→ 검증: chapter1-*.md 파일 존재 확인**
3. 챕터 2 작성 ✅ **→ 검증: chapter2-*.md 파일 존재 확인 + Ch.1 의존성 확인**
4. 챕터 3 작성 ✅ **→ 검증: chapter3-*.md 파일 존재 확인 + Ch.1,2 의존성 확인**
5. 챕터 4 작성 ✅ **→ 검증: chapter4-*.md 파일 존재 확인 + Ch.1,2,3 의존성 확인**
6. 챕터 5 작성 ✅ **→ 검증: chapter5-*.md 파일 존재 확인 + Ch.1-4 의존성 확인**
7. 최종 논문 통합 ✅ **→ 검증: thesis-final.md 파일 존재 확인 + 모든 챕터 의존성 확인**
8. 참고문헌 생성 ✅ **→ 검증: references.md 파일 존재 확인**

## Key Differences from Standard

| Feature | Standard (`/thesis:run-writing`) | Validated (this command) |
|---------|----------------------------------|--------------------------|
| Chapter 2,3 skip bug | ❌ Silent failure possible | ✅ **Immediately detected** |
| Missing final thesis | ❌ Silent failure possible | ✅ **Immediately detected** |
| Dependency checking | ❌ None | ✅ **Ch.2 requires Ch.1, etc.** |
| Error detection | ❌ At end or never | ✅ **Immediately after each step** |
| Execution mode | Continue on error | **Stop immediately (fail-fast)** |

## Example Output

성공 시:

```
======================================================================
🔍 VALIDATED EXECUTION: Step 115 - thesis-writer-ch1
======================================================================

[1/3] Pre-execution validation...
✅ Dependencies satisfied for step 115

[2/3] Executing agent: thesis-writer-ch1...
✅ Agent execution completed

[3/3] Post-execution validation...
✅ Required outputs validated for step 115

======================================================================
✅ VALIDATED EXECUTION COMPLETE: Step 115
   Execution time: 45.23s
======================================================================
```

실패 시 (Chapter 2가 생성되지 않은 경우):

```
======================================================================
🔍 VALIDATED EXECUTION: Step 117 - thesis-writer-ch2
======================================================================

[1/3] Pre-execution validation...
✅ Dependencies satisfied for step 117

[2/3] Executing agent: thesis-writer-ch2...
✅ Agent execution completed

[3/3] Post-execution validation...
❌ Output validation failed: Step 117 validation failed. Missing files:
  - 03-thesis/chapter2-*.md

======================================================================
❌ VALIDATED EXECUTION FAILED: Step 117
   ABORT DEPLOYMENT - Required output missing
======================================================================
```

**워크플로우는 즉시 중단되며, 문제를 수정할 때까지 계속 진행하지 않습니다.**

## Implementation

The command executes the Python script that implements validated Phase 3 execution:

```bash
python3 .claude/skills/thesis-orchestrator/scripts/run_writing_validated.py
```

The script performs:

1. **Prerequisite Validation**: Checks Phase 0, 1, 2 completion
2. **Step-by-Step Execution**: Runs each agent with validation
   - Step 111: @thesis-architect (outline design)
   - Step 115: @thesis-writer (Chapter 1)
   - Step 117: @thesis-writer (Chapter 2)
   - Step 119: @thesis-writer (Chapter 3)
   - Step 121: @thesis-writer (Chapter 4)
   - Step 123: @thesis-writer (Chapter 5)
   - Step 129: @thesis-integrator (final integration)
   - Step 130: @reference-compiler (references)
3. **Post-Validation**: Verifies each output exists
4. **Final Report**: Comprehensive Phase 3 validation report

## When to Use

**Use `/thesis:run-writing-validated`** when:
- ✅ You want **guaranteed quality** (no silent failures)
- ✅ You need **fail-fast behavior** (stop on first error)
- ✅ You're debugging Chapter 2,3 missing issues
- ✅ You want **dependency checking** (Ch.2 requires Ch.1)
- ✅ You're willing to fix issues immediately as they occur

**Use `/thesis:run-writing`** (standard) when:
- ✅ You want existing behavior (for compatibility)
- ✅ You're doing exploratory writing
- ✅ You don't need immediate error detection

## Safety Notes

- This command uses **fail-fast** mode - execution stops on first error
- All validation is **additive-only** - does not modify existing workflow
- Can fall back to `/thesis:run-writing` at any time
- Regression tested to ensure existing workflow remains intact

## Related Commands

- `/thesis:run-writing` - Standard execution without validation
- `/thesis:validate-phase 3` - Validate Phase 3 without execution
- `/thesis:progress` - Check overall progress

$ARGUMENTS
