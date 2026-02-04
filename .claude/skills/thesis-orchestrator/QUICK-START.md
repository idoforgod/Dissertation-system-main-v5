# Validation System - Quick Start Guide

**목표**: 5분 안에 검증 시스템 시작하기

---

## What is This?

논문 작성 워크플로우의 **품질 보증 시스템**입니다.

**해결하는 문제**:
- ❌ Chapter 2, 3 누락 (silent failure)
- ❌ Final thesis 생성 안 됨
- ❌ 진행 상황 파악 불가

**제공하는 해결책**:
- ✅ 모든 필수 파일 존재 확인
- ✅ 의존성 자동 검증 (Ch.2는 Ch.1 이후)
- ✅ 실시간 진행 상황 추적
- ✅ Fail-fast 오류 감지

---

## 30-Second Quickstart

```bash
# 1. 검증 활성화
bash .claude/skills/thesis-orchestrator/scripts/enable-validation.sh

# 2. 진행 상황 확인
/thesis:progress

# 3. 검증 활성화된 논문 작성
/thesis:run-writing-validated
```

**그게 다입니다!** 이제 Chapter 2, 3 누락 시 즉시 감지됩니다.

---

## 5-Minute Tutorial

### Step 1: 현재 상태 확인 (30초)

```bash
# 검증 시스템 상태 확인
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
```

**Expected Output**:
```
Validation:     ⏭️  DISABLED
Fail-fast:      ✅ ENABLED
```

→ 기본값: 비활성화 (backward compatible)

---

### Step 2: 검증 활성화 (30초)

```bash
# 방법 1: 스크립트 사용 (권장)
bash .claude/skills/thesis-orchestrator/scripts/enable-validation.sh

# 방법 2: 환경 변수
export USE_VALIDATION=true
export FAIL_FAST=true

# 방법 3: Python CLI
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable
```

**Expected Output**:
```
✅ Validation ENABLED

Settings:
  USE_VALIDATION=true
  FAIL_FAST=true
```

---

### Step 3: 진행 상황 확인 (30초)

```bash
# 현재 프로젝트 진행 상황
/thesis:progress
```

**Example Output**:
```
Workflow Progress: 75.0%
Completed: 6/8 critical steps

  ✅ Phase 0: Initialization
  ✅ Phase 1: Literature Review
  ✅ Phase 2: Research Design
  ❌ Phase 3: Thesis Writing  ← Chapter 2, 3 missing!
  ⏭️  Phase 4: Publication Strategy
```

→ **즉시 문제 파악 가능!**

---

### Step 4: 특정 페이즈 검증 (1분)

```bash
# Phase 3 (논문 작성) 상세 검증
/thesis:validate-phase 3
```

**Example Output**:
```
======================================================================
❌ FAILED: Phase 3: Thesis Writing
======================================================================

Completion: 6/8 steps (75.0%)

❌ 2 step(s) failed:

  Step 117:
    - Missing: 03-thesis/chapter2-*.md  ← 정확히 어떤 파일이 없는지!

  Step 119:
    - Missing: 03-thesis/chapter3-*.md

======================================================================
```

→ **정확한 문제 위치와 누락 파일 확인!**

---

### Step 5: 검증 활성화된 작업 실행 (2분)

```bash
# 검증과 함께 논문 작성
/thesis:run-writing-validated
```

**What Happens**:
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

**If Chapter 2 Missing**:
```
======================================================================
🔍 VALIDATED EXECUTION: Step 117 - thesis-writer-ch2
======================================================================

[1/3] Pre-execution validation...
✅ Dependencies satisfied (Ch.1 exists)

[2/3] Executing agent: thesis-writer-ch2...
✅ Agent execution completed

[3/3] Post-execution validation...
❌ Output validation failed!
   Missing: 03-thesis/chapter2-*.md

======================================================================
❌ EXECUTION STOPPED
   Fix the issue and re-run
======================================================================
```

→ **즉시 중단! 문제 수정 후 재실행**

---

## Common Commands

### Check Status

```bash
# Quick progress
/thesis:progress

# Detailed validation
/thesis:validate-phase 3
/thesis:validate-all

# System health
python3 validation_fallback.py --health
```

---

### Enable/Disable

```bash
# Enable
bash enable-validation.sh

# Disable
bash disable-validation.sh

# Check current status
python3 validation_config.py --status
```

---

### Validated Commands

```bash
# Use validated versions
/thesis:run-writing-validated  # Phase 3 with validation
/thesis:validate-phase [0-4]   # Validate specific phase
/thesis:validate-all           # Validate everything
/thesis:progress              # Quick progress check
```

---

## When to Use Validation

### ✅ Use Validation When:

- 실전 논문 작성 (품질 보장)
- Chapter 누락 문제 경험함
- 진행 상황 추적 필요
- 품질 최우선

**Enable**:
```bash
export USE_VALIDATION=true
```

---

### ⏭️ Skip Validation When:

- 빠른 실험/테스트
- 기존 방식 선호
- 검증 오버헤드 우려 (실제로는 <100ms)

**Disable**:
```bash
export USE_VALIDATION=false
```

---

## Troubleshooting (2분)

### Problem: "Step 117 validation failed"

**Cause**: Chapter 2 파일 없음

**Fix**:
```bash
# 1. 확인
ls thesis-output/your-project/03-thesis/chapter2-*

# 2. 누락 파일 확인
/thesis:validate-phase 3

# 3. thesis-writer 재실행
/thesis:run-writing-validated
```

---

### Problem: "Validation too strict"

**Solution**: Fail-fast 비활성화 (계속 진행)
```bash
export FAIL_FAST=false
```

---

### Problem: "Want to go back"

**Solution**: 검증 비활성화
```bash
bash .claude/skills/thesis-orchestrator/scripts/disable-validation.sh
```

→ **기존 워크플로우로 즉시 복귀**

---

## What You Get

### Before Validation

```bash
# Phase 3 실행
/thesis:run-writing

# 결과 확인
ls thesis-output/project/03-thesis/

# 발견
chapter1-introduction.md  ← ✅ OK
chapter4-results.md       ← ✅ OK
chapter5-conclusion.md    ← ✅ OK

# ❌ Chapter 2, 3 누락 - 나중에 발견!
# ❌ thesis-final.md 없음 - 나중에 발견!
```

**문제**: Silent failure (나중에 발견)

---

### After Validation

```bash
# Phase 3 실행 (검증 활성화)
export USE_VALIDATION=true
/thesis:run-writing-validated

# 실행 중
✅ Chapter 1 created
❌ Chapter 2 MISSING - STOPPED!
   → Fix now, not later!

# 즉시 수정
# ... fix thesis-writer ...

# 재실행
/thesis:run-writing-validated

✅ Chapter 1 created
✅ Chapter 2 created ← Fixed!
✅ Chapter 3 created
✅ ...all chapters created
✅ thesis-final.md created
```

**이점**: Immediate detection (즉시 감지)

---

## Next Steps

### Just Starting?

1. **Read**: MIGRATION-GUIDE.md (10분)
2. **Try**: 테스트 디렉토리에서 실험 (5분)
3. **Apply**: 실제 프로젝트 Phase 3만 적용 (안전)

### Already Using?

1. **Monitor**: `python3 validation_fallback.py --recent`
2. **Optimize**: Verbose 모드로 디버깅
3. **Share**: 팀원에게 공유

### Advanced?

1. **Customize**: agent-wrapper-guide.md 참조
2. **Integrate**: 자체 에이전트에 검증 추가
3. **Contribute**: 피드백 제공

---

## Summary

**What**: 논문 워크플로우 품질 보증 시스템

**Why**: Chapter 누락, silent failure 방지

**How**: 3 commands
```bash
bash enable-validation.sh
/thesis:progress
/thesis:run-writing-validated
```

**When**: 실전 논문 작성 시 (권장)

**Where**: Phase 3 (논문 작성)에서 가장 유용

**Who**: 모든 논문 작성자

---

**5분이면 충분합니다. 지금 바로 시작하세요!**

```bash
# Right now:
cd /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v1
bash .claude/skills/thesis-orchestrator/scripts/enable-validation.sh
/thesis:progress
```

---

## pTCS 신뢰도 시스템 (신규)

**AlphaFold pIDDT 영감**: 자체 신뢰도 예측 시스템

### 5분 퀵스타트

pTCS (predicted Thesis Confidence Score) 시스템에 대한 자세한 내용은:
- **[DUAL-CONFIDENCE-QUICK-GUIDE.md](DUAL-CONFIDENCE-QUICK-GUIDE.md)** - 5분 퀵스타트
- **[DUAL-CONFIDENCE-IMPLEMENTATION-REPORT.md](DUAL-CONFIDENCE-IMPLEMENTATION-REPORT.md)** - 전체 구현 보고서

### 신규 Commands
```bash
# 실시간 모니터링
/thesis:monitor-confidence

# pTCS 계산
/thesis:calculate-ptcs

# pTCS + SRCS 통합 평가
/thesis:evaluate-dual-confidence

# Gate 검증
/thesis:validate-gate wave 1
/thesis:validate-gate phase 1
```

**특징**:
- 🔴🟡🔵🟢 컬러 코딩 (0-100 점수)
- pTCS 60% + SRCS 40% 가중 평균
- pTCS 우선 기준 (강한 기준)
- Retry-until-pass 자동 반복
