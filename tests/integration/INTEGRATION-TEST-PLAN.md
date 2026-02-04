# Integration Test Plan - Phase 2

**Date**: 2026-01-20
**Phase**: Phase 2 (Opt-in Integration)
**Status**: Ready for Testing

---

## Test Objectives

1. ✅ Verify validation layer works correctly when enabled
2. ✅ Verify existing workflow unchanged when validation disabled
3. ✅ Verify environment variables control behavior correctly
4. ✅ Verify slash commands function as documented
5. ✅ Verify no performance degradation

---

## Pre-Test Checklist

### Environment Setup

- [ ] Regression test passed (all original files intact)
- [ ] Python 3.8+ installed
- [ ] All validation scripts are executable
- [ ] Working directory exists (thesis-output/)
- [ ] No active validation sessions

### Verification

```bash
# 1. Check regression test
bash tests/regression/test_existing_workflow_intact.sh

# 2. Check Python version
python3 --version  # Should be 3.8+

# 3. Check scripts
ls -la .claude/skills/thesis-orchestrator/scripts/*.py

# 4. Check working directory
ls -la thesis-output/
```

---

## Test Suite

### Test 1: Basic Validation Enable/Disable

**Objective**: Verify validation can be enabled and disabled

**Steps**:
```bash
# 1. Check initial status
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status

# Expected: Validation DISABLED

# 2. Enable validation
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable

# Expected: Validation ENABLED, Fail-fast ENABLED

# 3. Check status again
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status

# Expected: Validation ENABLED

# 4. Disable validation
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --disable

# Expected: Validation DISABLED
```

**Success Criteria**:
- [  ] Enable command works
- [ ] Disable command works
- [ ] Status reflects changes
- [ ] Config file created at ~/.thesis-orchestrator/validation.json

---

### Test 2: Environment Variable Toggle

**Objective**: Verify USE_VALIDATION environment variable

**Steps**:
```bash
# 1. Set environment variable
export USE_VALIDATION=true

# 2. Check in Python
python3 -c "from validated_executor import should_use_validation; print(should_use_validation())"

# Expected: True

# 3. Unset
export USE_VALIDATION=false

# 4. Check again
python3 -c "from validated_executor import should_use_validation; print(should_use_validation())"

# Expected: False
```

**Success Criteria**:
- [ ] Environment variable is recognized
- [ ] should_use_validation() returns correct value
- [ ] Works with true/false, 1/0, yes/no

---

### Test 3: Slash Command - validate-phase

**Objective**: Verify /thesis:validate-phase command

**Prerequisites**:
- Test working directory with some files created

**Steps**:
```bash
# 1. Create test directory
mkdir -p thesis-output/test-validation-$(date +%s)
cd thesis-output/test-validation-*

# 2. Create minimal Phase 0 files
mkdir -p 00-session
echo '{}' > 00-session/session.json
echo '# Checklist' > 00-session/todo-checklist.md

# 3. Test validation command (simulated)
# Note: Actual command would be run through Claude interface
# For manual test: python3 phase_validator.py working_dir --phase 0
```

**Expected Output**:
```
======================================================================
✅ PASSED: Phase 0: Initialization
======================================================================

Completion: 2/2 steps (100.0%)
```

**Success Criteria**:
- [ ] Command recognizes test directory
- [ ] Detects existing files correctly
- [ ] Reports completion rate
- [ ] Saves validation report

---

### Test 4: Slash Command - validate-all

**Objective**: Verify /thesis:validate-all command

**Prerequisites**:
- Same test directory as Test 3

**Steps**:
```bash
# Run complete validation (simulated)
# Actual command: /thesis:validate-all
```

**Expected Output**:
```
######################################################################
❌ SOME FAILED: COMPLETE WORKFLOW VALIDATION
######################################################################

Phase Summary:
  Passed: 1/5 phases
  Overall Completion: 20.0%

  ✅ Phase 0: Initialization: 100.0% complete
  ❌ Phase 1: Literature Review: 0.0% complete
  ❌ Phase 2: Research Design: 0.0% complete
  ❌ Phase 3: Thesis Writing: 0.0% complete
  ❌ Phase 4: Publication Strategy: 0.0% complete
```

**Success Criteria**:
- [ ] Shows all 5 phases
- [ ] Correctly identifies Phase 0 as complete
- [ ] Shows other phases as incomplete
- [ ] Generates JSON report

---

### Test 5: Slash Command - progress

**Objective**: Verify /thesis:progress command

**Prerequisites**:
- Same test directory

**Steps**:
```bash
# Run progress check (simulated)
# Actual command: /thesis:progress
```

**Expected Output**:
```
Workflow Progress: 14.3%
Completed: 2/14 critical steps

  ✅ Phase 0: Initialization
  ❌ Phase 1: Literature Review
  ❌ Phase 2: Research Design
  ❌ Phase 3: Thesis Writing
  ❌ Phase 4: Publication Strategy
```

**Success Criteria**:
- [ ] Shows overall completion percentage
- [ ] Lists all phases with status
- [ ] Fast execution (<1 second)

---

### Test 6: Regression - Standard Workflow Unaffected

**Objective**: Verify standard workflow unchanged when validation disabled

**Steps**:
```bash
# 1. Disable validation
export USE_VALIDATION=false

# 2. Run regression test
bash tests/regression/test_existing_workflow_intact.sh

# Expected: ALL PASS

# 3. Verify original files
ls -la .claude/skills/thesis-orchestrator/scripts/*.py | grep -E "init_session|checklist_manager|context_loader"

# Expected: All original files present
```

**Success Criteria**:
- [ ] Regression test passes
- [ ] All original files untouched
- [ ] No validation overhead when disabled

---

### Test 7: Validation Detects Missing Files

**Objective**: Verify validation catches missing Chapter 2, 3

**Prerequisites**:
- Test directory with Phase 3 partially complete

**Setup**:
```bash
# Create test scenario (Ch.1, 4, 5 exist; Ch.2, 3 missing)
mkdir -p 03-thesis
echo "# Chapter 1" > 03-thesis/chapter1-introduction.md
echo "# Chapter 4" > 03-thesis/chapter4-results.md
echo "# Chapter 5" > 03-thesis/chapter5-conclusion.md
# Intentionally skip Ch.2 and Ch.3
```

**Test**:
```bash
# Enable validation
export USE_VALIDATION=true

# Validate Phase 3
# Expected: FAIL with Ch.2, Ch.3 missing
```

**Expected Output**:
```
======================================================================
❌ FAILED: Phase 3: Thesis Writing
======================================================================

❌ 2 step(s) failed:

  Step 117:
    - Missing: 03-thesis/chapter2-*.md

  Step 119:
    - Missing: 03-thesis/chapter3-*.md
```

**Success Criteria**:
- [ ] Detects missing Ch.2
- [ ] Detects missing Ch.3
- [ ] Does NOT flag Ch.1, 4, 5 (they exist)
- [ ] Clear error messages

---

### Test 8: Dependency Validation

**Objective**: Verify dependency checking (Ch.2 requires Ch.1)

**Setup**:
```bash
# Create only Ch.2 (no Ch.1)
mkdir -p 03-thesis
echo "# Chapter 2" > 03-thesis/chapter2-literature.md
```

**Test**:
```python
from workflow_validator import DependencyValidator
from pathlib import Path

validator = DependencyValidator(Path("thesis-output/test-*"))
success, missing = validator.validate_dependencies(117)  # Ch.2

# Expected: success=False, missing=[115] (Ch.1 required)
```

**Success Criteria**:
- [ ] Detects Ch.1 dependency missing
- [ ] Lists step 115 as prerequisite
- [ ] Prevents execution until resolved

---

### Test 9: Fail-Fast Behavior

**Objective**: Verify execution stops on first error

**Setup**:
```bash
# Enable fail-fast
export USE_VALIDATION=true
export FAIL_FAST=true
```

**Test Scenario**:
- Execute Phase 3 writing
- Step 115 (Ch.1) succeeds → continues
- Step 117 (Ch.2) fails → STOPS immediately
- Step 119 (Ch.3) never executed

**Success Criteria**:
- [ ] Execution stops at first failure
- [ ] Clear error message displayed
- [ ] Subsequent steps not attempted
- [ ] Exit code non-zero

---

### Test 10: Performance Benchmark

**Objective**: Verify minimal performance impact

**Test**:
```bash
# Test 1: Validation disabled
export USE_VALIDATION=false
time /thesis:validate-phase 0

# Test 2: Validation enabled
export USE_VALIDATION=true
time /thesis:validate-phase 0

# Compare execution times
```

**Success Criteria**:
- [ ] Validation adds <100ms overhead
- [ ] File existence checks are fast
- [ ] No memory leaks
- [ ] Scales linearly with file count

---

## Integration Test Results

### Summary Template

```
Test Date: _______________
Tester: __________________

Results:
[ ] Test 1: Enable/Disable          - PASS / FAIL
[ ] Test 2: Environment Variables   - PASS / FAIL
[ ] Test 3: validate-phase          - PASS / FAIL
[ ] Test 4: validate-all            - PASS / FAIL
[ ] Test 5: progress                - PASS / FAIL
[ ] Test 6: Regression              - PASS / FAIL
[ ] Test 7: Missing Files Detection - PASS / FAIL
[ ] Test 8: Dependency Validation   - PASS / FAIL
[ ] Test 9: Fail-Fast Behavior      - PASS / FAIL
[ ] Test 10: Performance            - PASS / FAIL

Overall: PASS / FAIL

Notes:
_________________________________________________
_________________________________________________
```

---

## Post-Test Actions

### If All Tests Pass ✅

1. Mark Phase 2 complete
2. Document results in PHASE-2-COMPLETION-REPORT.md
3. Proceed to Phase 3 (Gradual Migration)

### If Any Tests Fail ❌

1. Document failure in test results
2. Create issue for failed test
3. Fix issue and re-run tests
4. Do NOT proceed to Phase 3 until all pass

---

## Manual Test Execution

For manual testing (when automated tests not available):

```bash
# 1. Setup
cd /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v1

# 2. Run regression
bash tests/regression/test_existing_workflow_intact.sh

# 3. Test validation config
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --help-vars
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --disable

# 4. Test helper scripts
bash .claude/skills/thesis-orchestrator/scripts/enable-validation.sh
bash .claude/skills/thesis-orchestrator/scripts/disable-validation.sh

# 5. Verify Python imports
python3 -c "from workflow_validator import WorkflowValidator; print('OK')"
python3 -c "from validated_executor import ValidatedExecutor; print('OK')"
python3 -c "from phase_validator import PhaseValidator; print('OK')"

# 6. Create test directory and validate
mkdir -p thesis-output/integration-test-$(date +%s)
cd thesis-output/integration-test-*
mkdir -p 00-session
echo '{}' > 00-session/session.json
python3 ../../.claude/skills/thesis-orchestrator/scripts/phase_validator.py . --phase 0

# 7. Cleanup
cd ../..
rm -rf thesis-output/integration-test-*
```

---

## Acceptance Criteria

Phase 2 is considered complete when:

- [ ] All 10 integration tests pass
- [ ] Regression test passes
- [ ] No breaking changes to existing workflow
- [ ] Documentation is complete
- [ ] User can opt-in/opt-out easily
- [ ] Performance is acceptable (<100ms overhead)

---

## Next Phase Preview

**Phase 3 (Week 3)**: Gradual Migration
- Make validation the default (opt-out instead of opt-in)
- Add automatic fallback mechanisms
- Create migration guide for users
- Collect feedback and iterate
