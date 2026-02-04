# Validation Configuration Guide

이 문서는 논문 워크플로우의 검증 기능을 환경 변수를 통해 제어하는 방법을 설명합니다.

---

## Quick Start

### Enable Validation (검증 활성화)

```bash
# Method 1: Using helper script (권장)
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable

# Method 2: Manual environment variable
export USE_VALIDATION=true
export FAIL_FAST=true
```

### Disable Validation (검증 비활성화)

```bash
# Method 1: Using helper script (권장)
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --disable

# Method 2: Manual environment variable
export USE_VALIDATION=false
```

### Check Status (상태 확인)

```bash
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
```

---

## Environment Variables

### USE_VALIDATION

**Purpose**: 검증 레이어 활성화/비활성화

**Values**:
- `true`, `1`, `yes`: 검증 활성화
- `false`, `0`, `no`: 검증 비활성화 (기본값)

**Example**:
```bash
export USE_VALIDATION=true
```

**Effect**:
- When `true`: validated_executor가 자동으로 사용됨
- When `false`: 기존 워크플로우 그대로 사용 (검증 없음)

---

### FAIL_FAST

**Purpose**: 첫 번째 오류 발생 시 즉시 중단

**Values**:
- `true`, `1`, `yes`: Fail-fast 활성화 (기본값)
- `false`, `0`, `no`: 오류 발생해도 계속 실행

**Example**:
```bash
export FAIL_FAST=true
```

**Effect**:
- When `true`: 챕터 2가 누락되면 즉시 중단 (권장)
- When `false`: 오류를 기록하고 계속 실행 (디버깅용)

---

### VALIDATION_REPORT_DIR

**Purpose**: 검증 보고서 저장 디렉토리

**Values**: 임의의 디렉토리 경로

**Default**: `validation-reports`

**Example**:
```bash
export VALIDATION_REPORT_DIR=my-validation-reports
```

**Effect**:
- 검증 보고서가 지정된 디렉토리에 저장됨
- 상대 경로: working_dir 기준
- 절대 경로: 지정된 경로 그대로

---

### VALIDATION_VERBOSE

**Purpose**: 상세 검증 출력 활성화

**Values**:
- `true`, `1`, `yes`: 상세 출력
- `false`, `0`, `no`: 간략 출력 (기본값)

**Example**:
```bash
export VALIDATION_VERBOSE=true
```

**Effect**:
- When `true`: 모든 검증 단계를 상세히 출력
- When `false`: 요약 정보만 출력

---

## Usage Scenarios

### Scenario 1: First-time User (처음 사용자)

**Goal**: 안전하게 검증 기능 체험

```bash
# 1. Enable validation with fail-fast
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable

# 2. Check status
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status

# 3. Run workflow (validation will be automatic)
/thesis:run-writing-validated

# 4. If you want to go back to standard
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --disable
```

---

### Scenario 2: Debugging Chapter 2,3 Missing Issue

**Goal**: Chapter 2, 3가 누락되는 문제 디버깅

```bash
# 1. Enable validation with verbose output
export USE_VALIDATION=true
export FAIL_FAST=true
export VALIDATION_VERBOSE=true

# 2. Run validated execution
/thesis:run-writing-validated

# 3. Watch detailed output - will stop at first missing chapter
# Output will show exactly which step failed and what file is missing

# 4. Fix the issue and re-run
```

---

### Scenario 3: Production Run (안정적 실행)

**Goal**: 최종 논문 작성 시 100% 품질 보장

```bash
# 1. Enable strict validation
export USE_VALIDATION=true
export FAIL_FAST=true

# 2. Validate prerequisites first
/thesis:validate-phase 0  # Initialization
/thesis:validate-phase 1  # Literature Review
/thesis:validate-phase 2  # Research Design

# 3. Run writing with validation
/thesis:run-writing-validated

# 4. Validate final result
/thesis:validate-phase 3
/thesis:validate-all

# 5. Check progress
/thesis:progress
```

---

### Scenario 4: Development/Testing (개발/테스트)

**Goal**: 검증 없이 빠르게 테스트

```bash
# 1. Disable validation
export USE_VALIDATION=false

# 2. Run standard workflow (faster, no validation overhead)
/thesis:run-writing

# 3. After development, validate manually
/thesis:validate-phase 3
```

---

## Configuration Persistence

### Session-Level (세션 단위)

Environment variables set with `export` are session-level:

```bash
export USE_VALIDATION=true  # Only for current terminal session
```

To make permanent, add to your shell profile:

```bash
# Add to ~/.zshrc or ~/.bashrc
export USE_VALIDATION=true
export FAIL_FAST=true
```

### Project-Level (프로젝트 단위)

Use the helper script to save configuration:

```bash
# Saves to ~/.thesis-orchestrator/validation.json
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable
```

This configuration persists across sessions and terminals.

---

## Checking Configuration

### Quick Check

```bash
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
```

**Output**:
```
======================================================================
Validation Configuration Status
======================================================================

Validation:     ✅ ENABLED
Fail-fast:      ✅ ENABLED
Verbose:        ⏭️  DISABLED
Report Dir:     validation-reports

Config File:    /Users/username/.thesis-orchestrator/validation.json
Status:         Configured

======================================================================
```

### Detailed Help

```bash
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --help-vars
```

---

## Best Practices

### ✅ Recommended for Most Users

```bash
# Enable validation with fail-fast
export USE_VALIDATION=true
export FAIL_FAST=true
```

**Why**:
- Catches errors immediately (Chapter 2,3 missing)
- Prevents silent failures
- Ensures all required outputs exist
- No performance impact on quality

### ⚠️ Advanced: Non-Fail-Fast Mode

```bash
# Continue execution even on errors (for debugging)
export USE_VALIDATION=true
export FAIL_FAST=false
```

**Use when**:
- Debugging workflow issues
- Want to see all errors at once (not just first one)
- Analyzing multiple failure points

### ⏭️ Disable When Not Needed

```bash
# Disable validation
export USE_VALIDATION=false
```

**Use when**:
- Just exploring/experimenting
- Want original workflow behavior
- Performance testing
- Compatibility testing

---

## Troubleshooting

### Issue: Validation not working

**Check**:
```bash
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
```

If `Validation: ⏭️ DISABLED`, enable it:
```bash
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable
```

### Issue: Too much output

**Solution**:
```bash
# Disable verbose mode
export VALIDATION_VERBOSE=false
```

### Issue: Want to revert to standard workflow

**Solution**:
```bash
# Disable validation
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --disable
```

---

## FAQ

### Q: Does enabling validation modify my existing workflow?

**A**: No. Validation is completely additive - it only adds checks on top of existing workflow. Your original code is never modified.

### Q: Can I enable validation mid-workflow?

**A**: Yes. You can enable/disable at any time. Validation will apply to subsequent steps.

### Q: What happens if I have validation enabled but use standard commands?

**A**: Standard commands (`/thesis:run-writing`) ignore validation settings. Only validated commands (`/thesis:run-writing-validated`) use validation.

### Q: Performance impact?

**A**: Minimal. File existence checks are very fast (<1ms per step). Validation overhead is negligible compared to agent execution time (30-60 seconds per chapter).

### Q: Is validation required?

**A**: No. Validation is completely optional (opt-in). You can use the standard workflow without any validation.

---

## Summary

| Setting | Effect | When to Use |
|---------|--------|-------------|
| `USE_VALIDATION=true` | 검증 활성화 | 품질 보장 필요 시 |
| `USE_VALIDATION=false` | 검증 비활성화 | 탐색/실험 시 |
| `FAIL_FAST=true` | 첫 오류에서 중단 | 대부분의 경우 (권장) |
| `FAIL_FAST=false` | 오류 무시하고 계속 | 디버깅 시 |
| `VALIDATION_VERBOSE=true` | 상세 출력 | 문제 파악 시 |
| `VALIDATION_VERBOSE=false` | 간략 출력 | 일반적 사용 |

**Default (기본값)**: 검증 비활성화 (기존 워크플로우 그대로)

**Recommended (권장)**: 검증 활성화 + Fail-fast (품질 보장)
