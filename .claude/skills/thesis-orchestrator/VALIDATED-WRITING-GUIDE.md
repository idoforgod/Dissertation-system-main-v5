# Validated Writing Pipeline Guide

## Overview

The Validated Writing Pipeline (`/thesis:run-writing-validated`) is an enhanced version of the standard Phase 3 writing pipeline that adds fail-fast validation at each step.

## Problem Statement

The standard `/thesis:run-writing` command has known issues:

1. **Silent Failures**: Chapter 2 or 3 may be skipped without error
2. **Missing Final Output**: Final thesis integration may fail silently
3. **No Dependency Checking**: Chapter 2 can run even if Chapter 1 failed
4. **Late Error Detection**: Problems discovered only at the end or never

## Solution

The validated pipeline wraps each agent execution with validation:

```
┌─────────────────────────────────────────────────────────┐
│ Standard Pipeline                                       │
│ ───────────────────────────────────────────────────────│
│ Agent 1 → Agent 2 → Agent 3 → ... → Done               │
│           (may skip)  (may fail)        (check at end) │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ Validated Pipeline                                      │
│ ───────────────────────────────────────────────────────│
│ Agent 1 → ✅ Check → Agent 2 → ✅ Check → Agent 3 → ... │
│           (pass)              (FAIL! → STOP)           │
└─────────────────────────────────────────────────────────┘
```

## Usage

```bash
/thesis:run-writing-validated
```

Or directly:

```bash
python3 .claude/skills/thesis-orchestrator/scripts/run_writing_validated.py
```

## What It Does

### 1. Prerequisite Validation

Checks Phase 0, 1, 2 completion:

```
✅ Phase 0 validated (initialization)
✅ Phase 1 validated (literature review)
✅ Phase 2 validated (research design)
```

### 2. Step-by-Step Execution with Validation

For each step:

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

### 3. Fail-Fast on Error

If validation fails, execution stops immediately:

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

**Execution stops. Fix the issue before continuing.**

## Phase 3 Steps

| Step | Agent | Description | Output |
|------|-------|-------------|--------|
| 111 | thesis-architect | Design outline | `03-thesis/thesis-outline.md` |
| 115 | thesis-writer | Chapter 1 | `03-thesis/chapter1-*.md` |
| 117 | thesis-writer | Chapter 2 | `03-thesis/chapter2-*.md` |
| 119 | thesis-writer | Chapter 3 | `03-thesis/chapter3-*.md` |
| 121 | thesis-writer | Chapter 4 | `03-thesis/chapter4-*.md` |
| 123 | thesis-writer | Chapter 5 | `03-thesis/chapter5-*.md` |
| 129 | thesis-integrator | Final thesis | `03-thesis/thesis-final.md` |
| 130 | reference-compiler | References | `03-thesis/references.md` |

## Validation Rules

### Output Validation

Each step must produce its required output:

- **Step 111**: `thesis-outline.md` must exist
- **Step 115**: `chapter1-*.md` must exist
- **Step 117**: `chapter2-*.md` must exist
- **Step 119**: `chapter3-*.md` must exist
- **Step 121**: `chapter4-*.md` must exist
- **Step 123**: `chapter5-*.md` must exist
- **Step 129**: `thesis-final.md` must exist
- **Step 130**: `references.md` must exist

### Dependency Validation

Later steps require earlier steps:

- **Chapter 2** requires Chapter 1
- **Chapter 3** requires Chapters 1, 2
- **Chapter 4** requires Chapters 1, 2, 3
- **Chapter 5** requires Chapters 1, 2, 3, 4
- **Final thesis** requires all chapters
- **References** requires final thesis

## When to Use

### Use Validated Pipeline (`/thesis:run-writing-validated`) When:

- ✅ You need **guaranteed quality** (no silent failures)
- ✅ You want **fail-fast behavior** (stop on first error)
- ✅ You're debugging missing chapter issues
- ✅ You need **dependency checking**
- ✅ You're willing to fix issues immediately

### Use Standard Pipeline (`/thesis:run-writing`) When:

- ✅ You want existing behavior (for compatibility)
- ✅ You're doing exploratory writing
- ✅ You don't need immediate error detection

## Comparison

| Feature | Standard | Validated |
|---------|----------|-----------|
| Chapter 2,3 skip bug | ❌ Silent failure | ✅ Detected immediately |
| Missing final thesis | ❌ Silent failure | ✅ Detected immediately |
| Dependency checking | ❌ None | ✅ Full checking |
| Error detection | ❌ At end or never | ✅ Immediately |
| Execution mode | Continue on error | **Stop on first error** |

## Testing

Test the validated pipeline with mock data:

```bash
python3 .claude/skills/thesis-orchestrator/scripts/test_run_writing_validated.py
```

This creates a test session with Phase 0-2 complete and validates prerequisites.

## Implementation Details

### Architecture

```
run_writing_validated.py
├── Uses: validated_executor.py
│   ├── Pre-execution: workflow_validator.py (dependency check)
│   ├── Execution: Agent wrapper functions
│   └── Post-execution: workflow_validator.py (output check)
└── Uses: phase_validator.py (prerequisite check)
```

### Key Components

1. **ValidatedExecutor**: Wraps agent execution with validation
2. **PhaseValidator**: Validates phase-level completion
3. **WorkflowValidator**: Validates individual step outputs
4. **Agent Wrappers**: Thin wrappers around thesis writing agents

### Safety Features

- **Additive-Only**: Does not modify existing workflow
- **Independent**: Can be enabled/disabled at will
- **Fail-Fast**: Stops immediately on error
- **Non-invasive**: Can be removed without affecting existing code

## Troubleshooting

### Error: "No active session found"

```bash
# Solution: Initialize a session first
/thesis:init
```

### Error: "Phase X is not complete"

```bash
# Solution: Complete prerequisite phases
/thesis:validate-phase X  # Check what's missing
```

### Error: "Chapter X not found"

```bash
# Solution: Run the failed step again or check output directory
ls thesis-output/*/03-thesis/
```

## Related Commands

- `/thesis:run-writing` - Standard execution
- `/thesis:validate-phase 3` - Validate Phase 3 without execution
- `/thesis:progress` - Check overall progress
- `/thesis:review-chapter <N>` - Review specific chapter

## Future Enhancements

Potential improvements:

1. **Partial Resume**: Resume from last successful step
2. **Parallel Execution**: Run independent chapters in parallel
3. **Quality Metrics**: Add SRCS evaluation at each step
4. **Auto-Fix**: Suggest fixes for common errors
5. **Progress Tracking**: Real-time progress dashboard

## References

- [Validated Executor Implementation](../scripts/validated_executor.py)
- [Phase Validator Implementation](../scripts/phase_validator.py)
- [Workflow Validator Implementation](../scripts/workflow_validator.py)
- [Standard Writing Pipeline](../../commands/thesis/run-writing.md)
