# Agent Wrapper Guide

이 문서는 기존 에이전트를 검증 레이어로 래핑하는 방법을 설명합니다.

---

## Overview

**Wrapper Pattern**을 사용하면 기존 에이전트 코드를 수정하지 않고 검증 기능을 추가할 수 있습니다:

```
기존 에이전트 호출:
User → Agent → Output

검증 래퍼 사용:
User → Validator → Agent → Validator → Output
        ↑ Pre-check      ↑ Post-check
```

---

## Basic Wrapper Pattern

### Template

```python
from validated_executor import ValidatedExecutor, should_use_validation

def run_agent_with_validation(
    working_dir: Path,
    step: int,
    agent_function: Callable,
    agent_name: str
):
    """Run agent with optional validation.

    Args:
        working_dir: Working directory
        step: Step number
        agent_function: Agent to execute
        agent_name: Agent name for logging
    """
    # Check if validation is enabled
    if should_use_validation():
        # Use validated executor
        executor = ValidatedExecutor(working_dir, fail_fast=True)
        result = executor.execute_step(
            step=step,
            agent_function=agent_function,
            agent_name=agent_name
        )
        return result
    else:
        # Use standard execution (no validation)
        return agent_function()
```

### Usage

```python
# Instead of calling agent directly:
# result = thesis_writer_chapter1()

# Use wrapper:
result = run_agent_with_validation(
    working_dir=Path("thesis-output/my-project"),
    step=115,
    agent_function=thesis_writer_chapter1,
    agent_name="thesis-writer-ch1"
)
```

---

## Example: Thesis Writer Wrapper

### Scenario

You want to add validation to the thesis writer workflow without modifying existing agents.

### Original Code (Before)

```python
def run_phase3_writing(working_dir: Path):
    """Run Phase 3: Thesis Writing (Original)."""

    # Step 111: Design outline
    thesis_architect_result = Task(
        description="Design thesis outline",
        prompt="Create detailed thesis outline...",
        subagent_type="thesis-architect"
    )

    # Step 115: Write Chapter 1
    chapter1_result = Task(
        description="Write Chapter 1",
        prompt="Write introduction chapter...",
        subagent_type="thesis-writer"
    )

    # Step 117: Write Chapter 2
    chapter2_result = Task(
        description="Write Chapter 2",
        prompt="Write literature review...",
        subagent_type="thesis-writer"
    )

    # ... more chapters

    return {
        "outline": thesis_architect_result,
        "chapter1": chapter1_result,
        "chapter2": chapter2_result
    }
```

### Validated Code (After - Opt-in)

```python
from pathlib import Path
from validated_executor import ValidatedExecutor, should_use_validation

def run_phase3_writing_validated(working_dir: Path):
    """Run Phase 3: Thesis Writing with optional validation."""

    # Create executor if validation enabled
    if should_use_validation():
        executor = ValidatedExecutor(working_dir, fail_fast=True)
        print("✅ Validation enabled - using fail-fast mode")
    else:
        executor = None
        print("⏭️  Validation disabled - using standard mode")

    # Step 111: Design outline
    def run_thesis_architect():
        return Task(
            description="Design thesis outline",
            prompt="Create detailed thesis outline...",
            subagent_type="thesis-architect"
        )

    if executor:
        outline_result = executor.execute_step(
            step=111,
            agent_function=run_thesis_architect,
            agent_name="thesis-architect"
        )
    else:
        outline_result = run_thesis_architect()

    # Step 115: Write Chapter 1
    def run_chapter1():
        return Task(
            description="Write Chapter 1",
            prompt="Write introduction chapter...",
            subagent_type="thesis-writer"
        )

    if executor:
        chapter1_result = executor.execute_step(
            step=115,
            agent_function=run_chapter1,
            agent_name="thesis-writer-ch1"
        )
    else:
        chapter1_result = run_chapter1()

    # Step 117: Write Chapter 2 (with dependency on Ch.1)
    def run_chapter2():
        return Task(
            description="Write Chapter 2",
            prompt="Write literature review...",
            subagent_type="thesis-writer"
        )

    if executor:
        # Validation will check:
        # 1. Ch.1 exists (dependency)
        # 2. Ch.2 is created after execution
        chapter2_result = executor.execute_step(
            step=117,
            agent_function=run_chapter2,
            agent_name="thesis-writer-ch2"
        )
    else:
        chapter2_result = run_chapter2()

    # ... more chapters

    return {
        "outline": outline_result,
        "chapter1": chapter1_result,
        "chapter2": chapter2_result
    }
```

---

## Advanced: Phase-Level Wrapper

### Template

```python
from phase_validator import PhaseValidator

def run_phase_with_validation(
    working_dir: Path,
    phase: int,
    phase_function: Callable
):
    """Run entire phase with pre/post validation.

    Args:
        working_dir: Working directory
        phase: Phase number (0-4)
        phase_function: Phase execution function
    """
    if not should_use_validation():
        # Standard execution
        return phase_function()

    # Pre-validation: Check prerequisites
    validator = PhaseValidator(working_dir)

    print(f"\n[Pre-validation] Checking Phase {phase} prerequisites...")

    # Check previous phases are complete
    for prev_phase in range(phase):
        report = validator.validate_phase_verbose(prev_phase)
        if not report.all_passed:
            raise PhaseValidationError(
                f"Phase {prev_phase} must be complete before Phase {phase}.\\n"
                f"{report.summary()}"
            )

    print(f"✅ Prerequisites satisfied for Phase {phase}")

    # Execute phase
    result = phase_function()

    # Post-validation: Check outputs
    print(f"\n[Post-validation] Checking Phase {phase} outputs...")

    report = validator.validate_phase_verbose(phase)
    if not report.all_passed:
        raise PhaseValidationError(
            f"Phase {phase} validation failed.\\n{report.summary()}"
        )

    print(f"✅ Phase {phase} completed and validated")

    return result
```

### Usage

```python
# Wrap Phase 3 execution
result = run_phase_with_validation(
    working_dir=working_dir,
    phase=3,
    phase_function=lambda: run_phase3_writing(working_dir)
)
```

---

## Integration Strategies

### Strategy 1: Parallel Commands (권장)

기존 명령어와 새로운 명령어를 병행 운영:

```
/thesis:run-writing          ← 기존 (검증 없음)
/thesis:run-writing-validated ← 새로운 (검증 포함)
```

**Pros**:
- No breaking changes
- Users choose what they want
- Easy rollback

**Cons**:
- Code duplication

---

### Strategy 2: Environment Variable Toggle

하나의 명령어가 환경 변수로 동작 변경:

```python
def run_writing(working_dir: Path):
    if should_use_validation():
        return run_writing_validated(working_dir)
    else:
        return run_writing_standard(working_dir)
```

**Pros**:
- Single command
- User controls behavior

**Cons**:
- More complex logic

---

### Strategy 3: Gradual Migration

기존 코드에 점진적으로 검증 추가:

**Phase 1**: Add validation as opt-in
```python
if USE_VALIDATION:
    validate_step(115)
chapter1 = thesis_writer()
```

**Phase 2**: Make validation default
```python
validate_step(115)  # Always validate
chapter1 = thesis_writer()
```

**Phase 3**: Remove toggle (validation always on)

---

## Best Practices

### ✅ DO

1. **Use should_use_validation()** to check if validation is enabled
2. **Preserve original behavior** when validation is disabled
3. **Fail-fast by default** when validation is enabled
4. **Log validation results** for debugging
5. **Test both modes** (with and without validation)

### ❌ DON'T

1. **Don't modify existing agent code** directly
2. **Don't make validation mandatory** without opt-in period
3. **Don't skip validation errors** silently
4. **Don't mix validation and business logic**
5. **Don't forget to handle exceptions**

---

## Example: Complete Integration

```python
#!/usr/bin/env python3
"""Phase 3 Execution with Optional Validation."""

import sys
from pathlib import Path
from validated_executor import ValidatedExecutor, should_use_validation
from phase_validator import PhaseValidator

def run_phase3_complete(working_dir: Path):
    """Run Phase 3 with optional validation."""

    # Initialize
    use_validation = should_use_validation()
    executor = ValidatedExecutor(working_dir) if use_validation else None

    print(f"\\nMode: {'Validated' if use_validation else 'Standard'}")

    # Pre-validation (if enabled)
    if use_validation:
        validator = PhaseValidator(working_dir)
        for phase in [0, 1, 2]:
            report = validator.validate_phase_verbose(phase)
            if not report.all_passed:
                print(f"❌ Phase {phase} not complete")
                print(report.summary())
                sys.exit(1)
        print("✅ Prerequisites satisfied\\n")

    # Define steps
    steps = [
        (111, "thesis-architect", lambda: design_outline()),
        (115, "thesis-writer-ch1", lambda: write_chapter_1()),
        (117, "thesis-writer-ch2", lambda: write_chapter_2()),
        (119, "thesis-writer-ch3", lambda: write_chapter_3()),
        (121, "thesis-writer-ch4", lambda: write_chapter_4()),
        (123, "thesis-writer-ch5", lambda: write_chapter_5()),
        (129, "thesis-integrator", lambda: integrate_thesis()),
        (130, "reference-compiler", lambda: compile_references())
    ]

    # Execute
    results = {}
    for step, agent_name, agent_func in steps:
        if executor:
            result = executor.execute_step(step, agent_func, agent_name)
            results[step] = result
        else:
            results[step] = agent_func()

    # Post-validation (if enabled)
    if use_validation:
        validator = PhaseValidator(working_dir)
        report = validator.validate_phase_verbose(3)
        if not report.all_passed:
            print("❌ Phase 3 validation failed")
            print(report.summary())
            sys.exit(1)
        print("\\n✅ Phase 3 completed and validated")

    return results

# Agent function placeholders
def design_outline():
    return Task(description="Design outline", subagent_type="thesis-architect")

def write_chapter_1():
    return Task(description="Write Ch.1", subagent_type="thesis-writer")

# ... etc

if __name__ == "__main__":
    working_dir = Path("thesis-output/my-project")
    run_phase3_complete(working_dir)
```

---

## Testing

### Test Both Modes

```bash
# Test without validation
export USE_VALIDATION=false
python3 run_phase3.py

# Test with validation
export USE_VALIDATION=true
python3 run_phase3.py
```

### Verify Regression

```bash
# Ensure existing workflow still works
bash tests/regression/test_existing_workflow_intact.sh
```

---

## Summary

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| Basic Wrapper | Single agent | Low |
| Phase Wrapper | Entire phase | Medium |
| Parallel Commands | New feature | Low |
| Env Toggle | Flexible control | Medium |
| Gradual Migration | Long-term adoption | High |

**Recommendation**: Start with **Parallel Commands** (safest, easiest rollback).
