# Fallback System Guide

**Purpose**: Automatic safety net for validation system failures

---

## Overview

Fallback 시스템은 검증 시스템에 문제가 생겼을 때 자동으로 표준 워크플로우로 전환하여 사용자의 작업을 보호합니다.

**핵심 원칙**: "검증 오류가 작업을 막아서는 안 된다"

---

## When Fallback Triggers

Fallback은 다음 상황에서 자동으로 발생합니다:

### 1. Validation Module Error

```python
# Scenario: workflow_validator.py에 문제가 있음
try:
    from workflow_validator import WorkflowValidator
except ImportError:
    # → FALLBACK: 표준 실행으로 전환
    print("⚠️  Validation module not available, using standard execution")
```

### 2. Validation Logic Error

```python
# Scenario: 검증 로직 자체에 버그가 있음
try:
    validator.enforce_step(115)
except Exception as e:
    # → FALLBACK: 표준 실행으로 계속
    logger.log_fallback(reason="Validation error", error=e)
    continue_without_validation()
```

### 3. Working Directory Issue

```python
# Scenario: 작업 디렉토리가 손상됨
try:
    validator = WorkflowValidator(working_dir)
except ValueError:
    # → FALLBACK: 검증 건너뛰고 계속
    execute_without_validation()
```

---

## How Fallback Works

### Automatic Flow

```
Normal Flow:
User → Validation → Agent → Validation → Success ✅

With Error (Automatic Fallback):
User → Validation → ERROR → ⚠️ FALLBACK → Agent → Success ✅
                                  ↓
                           Log event & Continue
```

### Example

```python
from validation_fallback import SafeValidatedExecutor

# Create safe executor
executor = SafeValidatedExecutor(working_dir)

# If validation fails, automatically uses standard execution
result = executor.execute_step(
    step=115,
    agent_function=write_chapter1,
    agent_name="chapter1-writer"
)
# → Either validated execution OR standard execution (automatic choice)
```

---

## Fallback Logging

모든 fallback 이벤트는 자동으로 기록됩니다:

### Log Location

```bash
~/.thesis-orchestrator/fallback-logs/
└── fallback-20260120.log
```

### Log Format

```json
{
  "timestamp": "2026-01-20T14:30:00",
  "function": "execute_step_115",
  "reason": "Validation function raised exception",
  "error": "FileNotFoundError: session.json not found",
  "error_type": "FileNotFoundError",
  "context": {
    "step": 115,
    "agent_name": "chapter1-writer"
  }
}
```

---

## Monitoring Fallbacks

### Check System Health

```bash
python3 .claude/skills/thesis-orchestrator/scripts/validation_fallback.py --health
```

**Output**:
```json
{
  "overall": "healthy",
  "checks": {
    "modules": {
      "status": "pass",
      "missing": []
    },
    "environment": {
      "status": "pass",
      "variables": {
        "USE_VALIDATION": "true",
        "FAIL_FAST": "true"
      }
    },
    "fallbacks_today": {
      "status": "pass",
      "count": 0
    }
  }
}

✅ Validation system is healthy
```

---

### View Recent Fallbacks

```bash
python3 validation_fallback.py --recent 5
```

**Output**:
```
Recent 5 fallback(s):

1. 2026-01-20T14:30:00
   Function: execute_step_115
   Reason: Validation function raised exception
   Error: FileNotFoundError: session.json not found

2. 2026-01-20T14:32:15
   Function: execute_step_117
   Reason: Validation function raised exception
   Error: DependencyError: Step 115 not complete
```

---

### Count Fallbacks

```bash
python3 validation_fallback.py --count
```

**Output**:
```
Fallbacks today: 2
⚠️  Few fallbacks - monitor system
```

**Interpretation**:
- 0 fallbacks: ✅ System is stable
- 1-5 fallbacks: ⚠️  Monitor system
- 6-10 fallbacks: ⚠️  Investigation recommended
- 11+ fallbacks: ❌ Investigation required

---

## Using Fallback Decorator

### Basic Usage

```python
from validation_fallback import with_fallback

@with_fallback
def my_validated_function():
    """This function has automatic fallback."""
    # Try validation
    validator.enforce_step(115)

    # If validation fails, function continues without it
    return execute_agent()

# Call function
result = my_validated_function()
# → Validated execution OR fallback (automatic)
```

---

### With Custom Fallback Function

```python
from validation_fallback import with_fallback

def standard_execution():
    """Fallback function - standard execution."""
    return execute_agent_without_validation()

@with_fallback(fallback_function=standard_execution)
def my_validated_function():
    """With custom fallback."""
    validator.enforce_step(115)
    return execute_agent_with_validation()

# If validation fails, calls standard_execution() automatically
result = my_validated_function()
```

---

## SafeValidatedExecutor

권장 방법: `SafeValidatedExecutor` 사용

### Example

```python
from validation_fallback import SafeValidatedExecutor

# Create safe executor (automatic fallback built-in)
executor = SafeValidatedExecutor(working_dir, fail_fast=True)

# Execute with automatic fallback
steps = [
    (115, write_chapter1, "chapter1-writer"),
    (117, write_chapter2, "chapter2-writer"),
    (119, write_chapter3, "chapter3-writer"),
]

for step, agent_func, agent_name in steps:
    result = executor.execute_step(step, agent_func, agent_name)
    # → If validation fails, automatically uses standard execution
    # → User's work continues regardless of validation errors
```

---

## Fallback Scenarios

### Scenario 1: Module Not Found

**Problem**: `workflow_validator.py` 파일이 없음

**Fallback Behavior**:
```
⚠️  FALLBACK TRIGGERED: Failed to initialize ValidatedExecutor
   Function: SafeValidatedExecutor.__init__
   Error: ModuleNotFoundError: No module named 'workflow_validator'
   → Falling back to standard execution

⚠️  Validation not available, using standard execution
```

**Result**: 검증 없이 작업 계속 (사용자 작업 보호)

---

### Scenario 2: Validation Logic Error

**Problem**: 검증 로직에 버그가 있음

**Fallback Behavior**:
```
⚠️  FALLBACK TRIGGERED: Validation function raised exception
   Function: execute_step_115
   Error: AttributeError: 'NoneType' object has no attribute 'glob'
   → Falling back to standard execution

⚠️  Validation failed for step 115, falling back to standard execution
   Error: AttributeError: 'NoneType' object has no attribute 'glob'
   → Executing chapter1-writer without validation

✅ Standard execution succeeded for step 115
```

**Result**: 검증은 실패했지만 작업은 성공 (사용자 작업 보호)

---

### Scenario 3: Working Directory Corrupted

**Problem**: 작업 디렉토리가 손상됨

**Fallback Behavior**:
```
⚠️  FALLBACK TRIGGERED: Validated execution failed
   Function: execute_step_115
   Error: ValueError: Working directory does not exist
   → Falling back to standard execution

✅ Standard execution succeeded for step 115
```

**Result**: 검증은 불가능하지만 작업은 계속

---

## Health Status Levels

### Healthy ✅

```json
{
  "overall": "healthy",
  "checks": {
    "modules": {"status": "pass"},
    "fallbacks_today": {"count": 0}
  }
}
```

**Meaning**: 모든 것이 정상

**Action**: None required

---

### Degraded ⚠️

```json
{
  "overall": "degraded",
  "checks": {
    "modules": {"status": "pass"},
    "fallbacks_today": {"count": 12}
  }
}
```

**Meaning**: Fallback이 많이 발생 (11+ times)

**Action**:
1. 로그 확인: `python3 validation_fallback.py --recent 20`
2. 패턴 파악: 같은 오류가 반복되는지 확인
3. 수정 또는 검증 비활성화

---

### Unhealthy ❌

```json
{
  "overall": "unhealthy",
  "checks": {
    "modules": {
      "status": "fail",
      "missing": ["workflow_validator", "phase_validator"]
    }
  }
}
```

**Meaning**: 검증 모듈이 없음

**Action**:
1. 검증 시스템 재설치
2. 또는 검증 비활성화: `export USE_VALIDATION=false`

---

## Best Practices

### ✅ DO

1. **Monitor Fallbacks**: 정기적으로 fallback 로그 확인
2. **Investigate Patterns**: 반복되는 fallback 패턴 분석
3. **Use SafeValidatedExecutor**: 자동 fallback 권장
4. **Log Review**: 주기적으로 로그 검토

### ❌ DON'T

1. **Don't Ignore Fallbacks**: Fallback이 빈번하면 문제 조사 필요
2. **Don't Disable Logging**: 로그는 문제 진단에 필수
3. **Don't Panic**: Fallback은 안전장치, 작업은 계속됨
4. **Don't Modify Fallback Code**: 검증 시스템 코드 직접 수정 금지

---

## Troubleshooting

### Issue: Too Many Fallbacks

**Symptom**: 하루에 10+ fallback 발생

**Diagnosis**:
```bash
python3 validation_fallback.py --recent 20
# Look for patterns in errors
```

**Solution**:
1. 같은 오류 반복 → 검증 시스템 버그 또는 설정 문제
2. 다른 오류들 → 작업 디렉토리 또는 환경 문제
3. 임시 해결: `export USE_VALIDATION=false`

---

### Issue: Fallback Not Working

**Symptom**: 검증 오류로 작업이 중단됨

**Diagnosis**:
```bash
# Check if using SafeValidatedExecutor
grep -r "SafeValidatedExecutor" your-script.py

# Check if fallback is enabled
python3 -c "from validation_fallback import SafeValidatedExecutor; print('OK')"
```

**Solution**:
- `ValidatedExecutor` → `SafeValidatedExecutor`로 변경
- 또는 `@with_fallback` decorator 추가

---

## Summary

**Fallback 시스템의 목적**:
- ✅ 검증 오류가 작업을 막지 않음
- ✅ 자동으로 안전한 대체 실행
- ✅ 모든 이벤트 로깅 및 모니터링

**사용자 경험**:
- **Before Fallback**: 검증 오류 → 작업 중단 ❌
- **With Fallback**: 검증 오류 → 자동 fallback → 작업 계속 ✅

**권장 사용법**:
```python
from validation_fallback import SafeValidatedExecutor

# Use SafeValidatedExecutor instead of ValidatedExecutor
executor = SafeValidatedExecutor(working_dir)

# Automatic fallback on validation errors
result = executor.execute_step(step, agent, name)
```

---

**Fallback은 안전망입니다. 사용자의 작업을 보호하는 최후의 방어선입니다.**
