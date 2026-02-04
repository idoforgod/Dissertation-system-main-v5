# Quick Reference: Validated Writing Pipeline

## Command

```bash
/thesis:run-writing-validated
```

## What It Does

Runs Phase 3 (Thesis Writing) with **fail-fast validation** at each step.

## Prerequisites

- ✅ Phase 0 complete (initialization)
- ✅ Phase 1 complete (literature review)
- ✅ Phase 2 complete (research design)

## Execution Flow

```
1. Validate prerequisites (Phase 0-2)
   ↓
2. Step 111: @thesis-architect → thesis-outline.md
   ↓ ✅ Validate output
3. Step 115: @thesis-writer → chapter1-*.md
   ↓ ✅ Validate output
4. Step 117: @thesis-writer → chapter2-*.md (requires Ch.1)
   ↓ ✅ Validate output
5. Step 119: @thesis-writer → chapter3-*.md (requires Ch.1,2)
   ↓ ✅ Validate output
6. Step 121: @thesis-writer → chapter4-*.md (requires Ch.1,2,3)
   ↓ ✅ Validate output
7. Step 123: @thesis-writer → chapter5-*.md (requires Ch.1-4)
   ↓ ✅ Validate output
8. Step 129: @thesis-integrator → thesis-final.md (requires all chapters)
   ↓ ✅ Validate output
9. Step 130: @reference-compiler → references.md (requires final thesis)
   ↓ ✅ Validate output
10. Final Phase 3 validation
```

## Key Differences from Standard

| Feature | Standard | Validated |
|---------|----------|-----------|
| Validation | ❌ At end | ✅ Each step |
| Fail-fast | ❌ No | ✅ **Yes** |
| Dependencies | ❌ Not checked | ✅ **Enforced** |
| Silent failures | ❌ Possible | ✅ **Detected** |

## When to Use

### Use Validated (`/thesis:run-writing-validated`)

- ✅ Production writing
- ✅ Need guaranteed quality
- ✅ Want immediate error detection
- ✅ Debugging missing chapters

### Use Standard (`/thesis:run-writing`)

- ✅ Exploratory writing
- ✅ Quick iterations
- ✅ Don't need validation

## Success Output

```
======================================================================
✅ VALIDATED EXECUTION COMPLETE: Step 115
   Execution time: 45.23s
======================================================================
```

## Failure Output

```
❌ Output validation failed: Step 117 validation failed. Missing files:
  - 03-thesis/chapter2-*.md

======================================================================
❌ VALIDATED EXECUTION FAILED: Step 117
   ABORT DEPLOYMENT - Required output missing
======================================================================
```

**Execution stops immediately. Fix issue before continuing.**

## Outputs

All files in `thesis-output/{working-dir}/03-thesis/`:

- `thesis-outline.md` (Step 111)
- `chapter1-*.md` (Step 115)
- `chapter2-*.md` (Step 117)
- `chapter3-*.md` (Step 119)
- `chapter4-*.md` (Step 121)
- `chapter5-*.md` (Step 123)
- `thesis-final.md` (Step 129)
- `references.md` (Step 130)

## Common Errors

### "No active session found"

**Solution**: Run `/thesis:init` first

### "Phase X is not complete"

**Solution**: Complete prerequisite phases first
```bash
/thesis:validate-phase X  # Check what's missing
```

### "Chapter X not found"

**Solution**: Re-run failed step or check output directory
```bash
ls thesis-output/*/03-thesis/
```

## Related Commands

- `/thesis:run-writing` - Standard (no validation)
- `/thesis:validate-phase 3` - Check Phase 3 status
- `/thesis:progress` - Overall progress
- `/thesis:review-chapter <N>` - Review chapter

## Testing

```bash
# Create test environment
python3 .claude/skills/thesis-orchestrator/scripts/test_run_writing_validated.py

# Run on test data
cd test-thesis-output
python3 ../.claude/skills/thesis-orchestrator/scripts/run_writing_validated.py
```

## Direct Execution

```bash
python3 .claude/skills/thesis-orchestrator/scripts/run_writing_validated.py
```

## Safety

- ✅ Additive-only (doesn't modify existing code)
- ✅ Optional (standard pipeline always available)
- ✅ Independent (can be removed without issues)
- ✅ Non-invasive (doesn't break existing functionality)

## Documentation

- **Full Guide**: `VALIDATED-WRITING-GUIDE.md`
- **Implementation**: `RUN-WRITING-VALIDATED-IMPLEMENTATION.md`
- **Command Doc**: `.claude/commands/thesis/run-writing-validated.md`
- **Script**: `.claude/skills/thesis-orchestrator/scripts/run_writing_validated.py`

---

**Status**: ✅ Ready for use

**Version**: 1.0

**Date**: 2026-01-20
