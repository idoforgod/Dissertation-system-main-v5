# 안전한 구현 전략 (Safe Implementation Strategy)
# 5대 재설계 원칙 적용 - 기존 시스템 보존 보장

**작성일**: 2026-01-20
**핵심 원칙**: **기존 워크플로우를 절대 깨뜨리지 않는다**
**방법론**: Additive-Only + Progressive Enhancement

---

## 🎯 핵심 안전 원칙

### ⚠️ 절대 금지 사항 (NEVER)

```diff
- ❌ 기존 파일 삭제
- ❌ 기존 Agent 삭제
- ❌ 기존 커맨드 삭제
- ❌ 기존 스크립트 덮어쓰기
- ❌ 기존 워크플로우 경로 변경
- ❌ 하위 호환성 파괴
```

### ✅ 허용되는 작업 (ALLOWED)

```diff
+ ✅ 새로운 파일 추가 (기존 파일 유지)
+ ✅ 새로운 함수 추가 (기존 함수 유지)
+ ✅ 옵션 파라미터 추가 (기본값 = 기존 동작)
+ ✅ Wrapper 함수 추가 (기존 함수 호출)
+ ✅ 검증 레이어 추가 (opt-in)
+ ✅ 로깅/모니터링 추가 (비침투적)
```

---

## 1. 안전한 구현 전략: Additive-Only 방식

### 1.1 전략 개요

**핵심 아이디어**: 기존 시스템에 **새로운 레이어를 추가**하되, 기존 레이어는 **절대 건드리지 않음**

```
[기존 시스템]                [개선된 시스템]

init_session.py    →       init_session.py (원본 유지)
                            init_session_v2.py (새로운 검증 포함) ✅

sequential_executor.py →   sequential_executor.py (원본 유지)
                            validated_executor.py (검증 레이어) ✅

@thesis-writer     →       @thesis-writer (원본 유지)
                            @thesis-writer-validated (래퍼) ✅
```

**보장**:
- 기존 워크플로우: 계속 작동 (100% 호환)
- 새로운 워크플로우: 검증 포함 (opt-in)

---

## 2. 구현 로드맵: 3단계 점진적 접근

### Phase 1: 검증 레이어 추가 (1주) - 기존 시스템 영향 0%

**목표**: 기존 시스템을 전혀 건드리지 않고 새로운 검증 시스템 구축

#### Step 1.1: 새로운 파일 생성 (기존 파일 건드리지 않음)

```bash
# ✅ 새로운 파일 생성 (기존 파일 유지)
touch .claude/skills/thesis-orchestrator/scripts/workflow_validator.py
touch .claude/skills/thesis-orchestrator/scripts/validated_executor.py
touch .claude/skills/thesis-orchestrator/scripts/phase_validator.py

# ✅ 기존 파일은 그대로
ls -la scripts/
# init_session.py           (원본 유지) ✅
# sequential_executor.py    (원본 유지) ✅
# checklist_manager.py      (원본 유지) ✅
```

#### Step 1.2: 독립적인 검증 시스템 구축

```python
# ✅ workflow_validator.py (새로운 파일)
"""
독립적인 검증 시스템 - 기존 코드에 의존하지 않음
"""

class WorkflowValidator:
    """검증 전용 클래스 - 기존 시스템과 독립적"""

    def __init__(self, working_dir: Path):
        self.working_dir = working_dir

    def validate_step(self, step: int) -> tuple[bool, List[str]]:
        """Step 검증 - 기존 시스템 호출 안 함"""
        # 순수하게 파일 시스템만 검증
        pass

    def validate_phase(self, phase: int) -> Dict:
        """Phase 검증 - 기존 시스템 호출 안 함"""
        pass

# ❌ 기존 파일 수정 없음
# ❌ 기존 함수 변경 없음
```

#### Step 1.3: 테스트 작성 (기존 시스템 영향 없음)

```bash
# ✅ 새로운 테스트 파일
mkdir -p tests/unit/validation
touch tests/unit/validation/test_workflow_validator.py

# ✅ 기존 테스트는 그대로 (있다면)
```

**검증 방법**:
```bash
# 1. 기존 워크플로우 테스트 (변경 없어야 함)
/thesis:init "Test Topic"
/thesis:start topic "Test"
# ✅ 정상 작동 확인

# 2. 새로운 검증 시스템 독립 테스트
pytest tests/unit/validation/
# ✅ 통과 확인
```

**Phase 1 완료 기준**:
- [ ] 새로운 검증 시스템 작동
- [ ] 기존 워크플로우 100% 정상 작동 (영향 없음)
- [ ] 단위 테스트 100% 통과

---

### Phase 2: Opt-in 통합 (1주) - 기존 시스템 선택적 사용

**목표**: 사용자가 **선택적으로** 새로운 검증 시스템 사용 가능

#### Step 2.1: Wrapper 생성 (기존 함수 래핑)

```python
# ✅ validated_executor.py (새로운 파일)
"""
기존 sequential_executor를 래핑하는 검증 레이어
"""

from sequential_executor import execute_step as _original_execute_step
from workflow_validator import WorkflowValidator

def execute_step_validated(step: int, **kwargs):
    """
    검증이 추가된 래퍼 함수
    기존 execute_step을 호출하되 검증 추가
    """

    # 1. 기존 함수 호출 (변경 없음)
    result = _original_execute_step(step, **kwargs)

    # 2. ✅ 검증 추가 (새로운 레이어)
    validator = WorkflowValidator(working_dir)
    success, missing = validator.validate_step(step)

    if not success:
        # 검증 실패 시 경고만 (아직 강제 안 함)
        logger.warning(f"⚠️ Validation warning for step {step}: {missing}")

    # 3. 기존 결과 그대로 반환
    return result

# ❌ 기존 execute_step 함수는 절대 수정하지 않음
```

#### Step 2.2: 환경 변수로 제어

```python
# ✅ 사용자가 선택
import os

USE_VALIDATION = os.getenv("THESIS_USE_VALIDATION", "false") == "true"

if USE_VALIDATION:
    # 새로운 검증 시스템 사용
    from validated_executor import execute_step_validated as execute_step
else:
    # 기존 시스템 사용 (기본값)
    from sequential_executor import execute_step

# 나머지 코드는 동일
```

#### Step 2.3: 새로운 커맨드 추가 (기존 커맨드 유지)

```bash
# ✅ 새로운 커맨드 추가
touch .claude/commands/thesis/run-writing-validated.md

# ✅ 기존 커맨드 유지
ls .claude/commands/thesis/
# run-writing.md            (원본, 기본값) ✅
# run-writing-validated.md  (검증 포함, opt-in) ✅
```

**사용 방법**:
```bash
# 기존 방식 (검증 없음, 기본값)
/thesis:run-writing

# 새로운 방식 (검증 포함, opt-in)
export THESIS_USE_VALIDATION=true
/thesis:run-writing

# 또는 명시적 커맨드
/thesis:run-writing-validated
```

**Phase 2 완료 기준**:
- [ ] 검증 시스템 opt-in 가능
- [ ] 기존 워크플로우 여전히 100% 작동 (기본값)
- [ ] 새로운 검증 워크플로우 작동 (opt-in)
- [ ] 사용자 선택권 보장

---

### Phase 3: 점진적 마이그레이션 (1주) - 신중한 전환

**목표**: 검증이 충분히 안정화된 후, **점진적으로** 기본값 전환

#### Step 3.1: 안정성 검증 (필수)

```bash
# 1. 새로운 검증 시스템으로 10회 이상 E2E 테스트
for i in {1..10}; do
  export THESIS_USE_VALIDATION=true
  ./tests/e2e/test_complete_workflow.sh
  if [ $? -ne 0 ]; then
    echo "❌ Test $i failed. Aborting migration."
    exit 1
  fi
done
echo "✅ All 10 tests passed. Safe to proceed."

# 2. 실제 주제로 테스트
export THESIS_USE_VALIDATION=true
/thesis:init "Real Research Topic"
/thesis:start topic "AI Ethics"
# ... Phase 1-4 전체 실행
# ✅ 150단계 모두 완료 확인
```

**검증 기준**:
- [ ] E2E 테스트 10회 연속 성공
- [ ] 실제 주제 워크플로우 100% 완료
- [ ] 모든 필수 파일 생성 확인
- [ ] 체크리스트 150단계 모두 완료

#### Step 3.2: 기본값 전환 (조건부)

**조건**: Step 3.1 검증 **모두 통과** 시에만

```python
# ✅ 기본값 변경 (기존 코드 유지)
USE_VALIDATION = os.getenv("THESIS_USE_VALIDATION", "true") == "true"
#                                                    ^^^^
#                                         "false" → "true"로 변경

# ❌ 기존 코드 삭제는 절대 안 함
# 기존 sequential_executor.py는 그대로 유지
# 사용자가 원하면 언제든 돌아갈 수 있음
```

#### Step 3.3: Fallback 메커니즘 (안전장치)

```python
# ✅ 검증 시스템 실패 시 자동으로 기존 시스템으로 Fallback

try:
    from validated_executor import execute_step_validated as execute_step
    logger.info("✅ Using validated execution (with verification)")
except Exception as e:
    logger.warning(f"⚠️ Validated executor failed: {e}")
    logger.warning("⚠️ Falling back to original executor")
    from sequential_executor import execute_step
    # ✅ 기존 시스템으로 자동 전환
```

**보장**:
- 검증 시스템 버그 발생 시 자동으로 기존 시스템 사용
- 사용자는 영향 없음

**Phase 3 완료 기준**:
- [ ] 검증 시스템 안정성 확보 (10회 연속 성공)
- [ ] 기본값 전환 완료
- [ ] Fallback 메커니즘 작동 확인
- [ ] 기존 시스템 여전히 사용 가능 (보존)

---

## 3. 파일 구조: Before & After

### Before (현재)
```
.claude/skills/thesis-orchestrator/
├── scripts/
│   ├── init_session.py           ✅ 유지
│   ├── sequential_executor.py    ✅ 유지
│   ├── checklist_manager.py      ✅ 유지
│   └── ...
├── agents/
│   └── thesis/
│       └── phase3-writing/
│           └── thesis-writer.md  ✅ 유지
└── commands/
    └── thesis/
        └── run-writing.md        ✅ 유지
```

### After (Phase 1-3 완료 후)
```
.claude/skills/thesis-orchestrator/
├── scripts/
│   ├── init_session.py           ✅ 원본 유지 (Fallback용)
│   ├── sequential_executor.py    ✅ 원본 유지 (Fallback용)
│   ├── checklist_manager.py      ✅ 원본 유지
│   ├── workflow_validator.py     ✅ 새로 추가 (검증)
│   ├── validated_executor.py     ✅ 새로 추가 (래퍼)
│   ├── phase_validator.py        ✅ 새로 추가 (Phase 검증)
│   └── ...
├── agents/
│   └── thesis/
│       └── phase3-writing/
│           ├── thesis-writer.md          ✅ 원본 유지
│           └── thesis-writer-validated.md ✅ 새로 추가 (opt-in)
└── commands/
    └── thesis/
        ├── run-writing.md                ✅ 원본 유지
        └── run-writing-validated.md      ✅ 새로 추가 (opt-in)
```

**핵심**:
- ✅ 모든 원본 파일 보존
- ✅ 새로운 파일만 추가
- ❌ 삭제된 파일 없음

---

## 4. 각 원칙별 안전한 구현 방법

### 원칙 1: Fail-Fast (실패 시 즉시 중단)

#### 안전한 구현

```python
# ✅ validated_executor.py (새로운 파일)

def execute_step_with_failfast(step: int, **kwargs):
    """Fail-Fast 원칙 적용 - 기존 함수 래핑"""

    # 1. 기존 실행
    result = _original_execute_step(step, **kwargs)

    # 2. ✅ 검증 추가 (새로운 레이어)
    if not result.success:
        # Fail-Fast: 즉시 중단
        raise WorkflowError(f"Step {step} failed. Stopping workflow.")

    return result

# ❌ 기존 sequential_executor.py 수정 안 함
```

**보장**:
- 기존 시스템: 실패해도 계속 진행 (기존 동작)
- 새로운 시스템: 실패 시 중단 (opt-in)

### 원칙 2: Verification-First (필수 산출물 검증)

#### 안전한 구현

```python
# ✅ workflow_validator.py (새로운 파일)

REQUIRED_OUTPUTS = {
    115: ["03-thesis/chapter1-*.md"],
    117: ["03-thesis/chapter2-*.md"],  # ⭐ 필수
    119: ["03-thesis/chapter3-*.md"],  # ⭐ 필수
    # ...
}

class WorkflowValidator:
    def validate_step(self, step: int):
        """검증 - 기존 시스템과 독립적"""
        required = REQUIRED_OUTPUTS.get(step, [])
        missing = []

        for pattern in required:
            if not list(self.working_dir.glob(pattern)):
                missing.append(pattern)

        return len(missing) == 0, missing

# ✅ 기존 시스템 호출 안 함 → 영향 없음
```

**통합 (opt-in)**:

```python
# ✅ validated_executor.py

def execute_step_validated(step: int, **kwargs):
    # 1. 기존 실행
    result = _original_execute_step(step, **kwargs)

    # 2. ✅ 검증 (opt-in)
    if USE_VALIDATION:
        validator = WorkflowValidator(working_dir)
        validator.enforce_step(step)

    return result
```

### 원칙 3: Explicit Dependencies (의존성 명시)

#### 안전한 구현

```python
# ✅ workflow_validator.py (새로운 파일)

STEP_DEPENDENCIES = {
    117: [115],           # Ch.2는 Ch.1 필요
    119: [115, 117],      # Ch.3은 Ch.1, Ch.2 필요
    121: [115, 117, 119], # Ch.4는 Ch.1-3 필요
    # ...
}

class DependencyValidator:
    def validate_dependencies(self, step: int):
        """의존성 검증 - 독립적"""
        deps = STEP_DEPENDENCIES.get(step, [])
        checklist = ChecklistManager(self.working_dir / "00-session" / "todo-checklist.md")

        for dep in deps:
            if not checklist.is_completed(dep):
                raise DependencyError(f"Step {step} requires step {dep}")

# ✅ 기존 코드 수정 안 함
```

### 원칙 4: Atomic Operations (모두 성공 또는 모두 실패)

#### 안전한 구현

```python
# ✅ validated_executor.py

def execute_phase3_atomic():
    """Atomic 실행 - 기존 함수 활용"""

    checkpoint = create_checkpoint()  # ✅ 새로운 기능

    try:
        # 기존 함수들 호출
        for chapter in [1, 2, 3, 4, 5]:
            execute_step(115 + 2*chapter - 2)  # 기존 함수

        # ✅ 검증 추가
        if USE_VALIDATION:
            validate_all_chapters()

    except Exception as e:
        # ✅ Rollback (새로운 기능)
        rollback(checkpoint)
        raise

# ❌ 기존 execute_step 수정 안 함
```

### 원칙 5: Progress Transparency (진행률 표시)

#### 안전한 구현

```python
# ✅ progress_tracker.py (새로운 파일)

class ProgressTracker:
    """진행률 추적 - 비침투적"""

    def __init__(self, total_steps=150):
        self.total = total_steps
        self.current = 0

    def update(self, step: int):
        """진행률 업데이트 - 기존 시스템 영향 없음"""
        self.current = step
        percentage = (step / self.total) * 100
        print(f"Progress: [{step}/{self.total}] {percentage:.1f}%")

# ✅ 기존 코드에 로깅만 추가 (비침투적)
```

**통합**:

```python
# ✅ validated_executor.py

tracker = ProgressTracker()  # ✅ 새로운 객체

def execute_step_with_progress(step: int, **kwargs):
    # 진행률 표시 (비침투적)
    tracker.update(step)

    # 기존 실행
    result = _original_execute_step(step, **kwargs)

    return result
```

---

## 5. 위험 관리: 무엇이 잘못될 수 있나?

### 위험 1: 새로운 코드에 버그

**시나리오**: `workflow_validator.py`에 버그 → 정상 파일도 "누락"으로 오판

**대응**:
```python
# ✅ Fallback 메커니즘
try:
    validator.enforce_step(step)
except ValidationError as e:
    logger.error(f"Validation failed: {e}")
    logger.warning("Continuing with original executor...")
    # 기존 시스템으로 자동 전환
```

**보장**: 버그 발생 시 기존 시스템으로 자동 전환

### 위험 2: 검증 로직이 너무 엄격

**시나리오**: 정상적인 변형(예: `chapter1-intro.md` vs. `chapter1-introduction.md`)도 차단

**대응**:
```python
# ✅ 유연한 패턴 매칭
required_patterns = ["chapter1-*.md", "chapter-1-*.md", "ch1-*.md"]
# 여러 패턴 허용

# ✅ 사용자 오버라이드
if os.getenv("THESIS_SKIP_VALIDATION"):
    logger.warning("⚠️ Validation skipped by user")
    return  # 검증 스킵
```

**보장**: 사용자가 언제든 검증 우회 가능

### 위험 3: 성능 저하

**시나리오**: 파일 검증으로 워크플로우 느려짐

**대응**:
```python
# ✅ 캐싱
class WorkflowValidator:
    def __init__(self):
        self._cache = {}

    def validate_step(self, step: int):
        if step in self._cache:
            return self._cache[step]

        result = self._validate_step_impl(step)
        self._cache[step] = result
        return result
```

**보장**: 성능 영향 최소화

### 위험 4: 기존 사용자 워크플로우 중단

**시나리오**: Phase 3 전환 후 기존 사용자가 문제 발생

**대응**:
```python
# ✅ 환경 변수로 비활성화
export THESIS_USE_VALIDATION=false

# ✅ 또는 기존 커맨드 사용
/thesis:run-writing  # 검증 없음 (기존 방식)
```

**보장**: 기존 워크플로우 100% 호환 유지

---

## 6. 테스트 전략: 안전 확인

### Level 1: 기존 시스템 회귀 테스트

```bash
# ✅ 새로운 코드 추가 후 매번 실행
export THESIS_USE_VALIDATION=false  # 기존 시스템 사용

/thesis:init "Regression Test"
/thesis:start topic "Test"
/thesis:run-literature-review
/thesis:run-research-design
/thesis:run-writing
/thesis:run-publication

# ✅ 기존 동작 확인
if [ $? -eq 0 ]; then
  echo "✅ Regression test passed - existing workflow intact"
else
  echo "❌ Regression test failed - ABORT DEPLOYMENT"
  exit 1
fi
```

**기준**: 100% 통과 (하나라도 실패 시 배포 중단)

### Level 2: 새로운 시스템 단위 테스트

```bash
# ✅ 새로운 검증 시스템만 테스트 (기존 시스템 영향 없음)
pytest tests/unit/validation/test_workflow_validator.py
pytest tests/unit/validation/test_phase_validator.py
```

### Level 3: 통합 테스트

```bash
# ✅ 검증 시스템 opt-in 테스트
export THESIS_USE_VALIDATION=true

/thesis:init "Integration Test"
/thesis:run-writing-validated

# 검증 작동 확인
```

### Level 4: E2E 안정성 테스트

```bash
# ✅ 10회 연속 성공 확인
for i in {1..10}; do
  export THESIS_USE_VALIDATION=true
  ./tests/e2e/test_complete_workflow.sh
  if [ $? -ne 0 ]; then
    echo "❌ E2E test $i failed"
    exit 1
  fi
done

echo "✅ All 10 E2E tests passed - Safe to migrate"
```

---

## 7. 롤백 계획: 문제 발생 시

### 시나리오 1: Phase 1 중 버그 발견

**상황**: `workflow_validator.py`에 심각한 버그

**조치**:
```bash
# ✅ 새로운 파일만 삭제 (기존 파일은 그대로)
rm scripts/workflow_validator.py
rm scripts/validated_executor.py

# ✅ 기존 시스템 여전히 작동
/thesis:run-writing  # 정상 작동
```

**영향**: 없음 (기존 시스템 영향 없었음)

### 시나리오 2: Phase 2 중 통합 문제

**상황**: 래퍼 함수가 기존 함수와 충돌

**조치**:
```bash
# ✅ 환경 변수로 즉시 비활성화
export THESIS_USE_VALIDATION=false

# ✅ 또는 코드 수정
# validated_executor.py의 USE_VALIDATION 기본값 변경
USE_VALIDATION = False  # "true" → False로 변경
```

**영향**: 최소 (opt-in이므로 선택한 사용자만 영향)

### 시나리오 3: Phase 3 전환 후 문제

**상황**: 기본값 전환 후 사용자 불만

**조치**:
```bash
# ✅ 한 줄만 수정 (기본값 되돌리기)
# validated_executor.py
USE_VALIDATION = os.getenv("THESIS_USE_VALIDATION", "false")  # "true" → "false"

# ✅ 또는 git revert
git revert <commit-hash>
```

**영향**: 없음 (기존 코드 보존되어 있음)

---

## 8. 진행 일정: 3주 + 안전 버퍼

### Week 1: Phase 1 (검증 레이어 추가) + 안전 검증

| 일 | 작업 | 검증 |
|---|------|------|
| 1-2 | `workflow_validator.py` 구현 | 단위 테스트 |
| 3 | `validated_executor.py` 구현 | 통합 테스트 |
| 4 | `phase_validator.py` 구현 | 통합 테스트 |
| 5 | **회귀 테스트** | ✅ 기존 시스템 정상 확인 |

**Week 1 완료 조건**:
- [ ] 새로운 파일 3개 생성
- [ ] 단위 테스트 100% 통과
- [ ] **회귀 테스트 100% 통과** ⭐

### Week 2: Phase 2 (Opt-in 통합) + 안정성 검증

| 일 | 작업 | 검증 |
|---|------|------|
| 1-2 | Wrapper 함수 구현 | 통합 테스트 |
| 3 | 환경 변수 제어 구현 | 수동 테스트 |
| 4 | 새로운 커맨드 추가 | E2E 테스트 |
| 5 | **안정성 검증 (5회 E2E)** | ✅ 연속 성공 확인 |

**Week 2 완료 조건**:
- [ ] Opt-in 방식 작동
- [ ] E2E 테스트 5회 연속 성공
- [ ] **회귀 테스트 여전히 100% 통과** ⭐

### Week 3: Phase 3 (점진적 마이그레이션) + 최종 검증

| 일 | 작업 | 검증 |
|---|------|------|
| 1-2 | **안정성 재검증 (10회 E2E)** | ✅ 연속 성공 확인 |
| 3 | 기본값 전환 (조건부) | 통합 테스트 |
| 4 | Fallback 메커니즘 구현 | 장애 시뮬레이션 |
| 5 | **최종 회귀 테스트** | ✅ 전체 확인 |

**Week 3 완료 조건**:
- [ ] E2E 테스트 10회 연속 성공
- [ ] 기본값 전환 완료
- [ ] Fallback 작동 확인
- [ ] **회귀 테스트 최종 통과** ⭐

### +1 Week: 안전 버퍼 (예비)

**용도**: 예상치 못한 문제 발생 시 대응

---

## 9. 의사결정 체크리스트

### Phase 1 → Phase 2 전환 시

**질문 체크리스트**:
- [ ] 새로운 검증 시스템이 단위 테스트 100% 통과하는가?
- [ ] **회귀 테스트가 100% 통과하는가?** ⭐
- [ ] 새로운 코드가 기존 코드를 import/호출하는가? (NO여야 함)
- [ ] 새로운 파일만 추가되었는가? (삭제/수정 없음)
- [ ] 문서화가 완료되었는가?

**하나라도 NO이면 다음 Phase 진행 금지**

### Phase 2 → Phase 3 전환 시

**질문 체크리스트**:
- [ ] Opt-in 방식이 정상 작동하는가?
- [ ] E2E 테스트가 5회 연속 성공하는가?
- [ ] **회귀 테스트가 여전히 100% 통과하는가?** ⭐
- [ ] Fallback 메커니즘이 구현되었는가?
- [ ] 사용자가 언제든 이전 방식으로 돌아갈 수 있는가?

**하나라도 NO이면 다음 Phase 진행 금지**

### Phase 3 기본값 전환 시

**질문 체크리스트**:
- [ ] E2E 테스트가 10회 연속 성공하는가?
- [ ] 실제 주제로 워크플로우 100% 완료 확인했는가?
- [ ] **회귀 테스트가 최종 통과하는가?** ⭐
- [ ] 사용자가 환경 변수로 비활성화 할 수 있는가?
- [ ] 기존 코드가 여전히 존재하는가? (삭제 안 됨)

**하나라도 NO이면 전환 금지**

---

## 10. 결론 및 제안

### 핵심 안전 원칙 재확인

```
✅ 기존 시스템 절대 삭제 안 함
✅ 새로운 레이어만 추가
✅ 점진적 opt-in 방식
✅ 매 단계마다 회귀 테스트
✅ Fallback 메커니즘 필수
```

### 제안하는 진행 방식

**Option A**: 완전 안전 모드 (권장 ⭐)
- 3주 + 1주 버퍼 = 4주
- 매 Phase 완료 후 회귀 테스트 필수
- 기본값 전환 신중히 결정 (10회 E2E 통과 후)

**Option B**: 빠른 진행 (비권장)
- 3주 압축
- 회귀 테스트 축소
- 위험: 기존 시스템 깨질 가능성

### 다음 단계

**즉시 시작 가능**:
1. Week 1 Day 1-2: `workflow_validator.py` 구현
2. 단위 테스트 작성
3. 회귀 테스트 확인

**논의 필요**:
- [ ] Option A (안전) vs. Option B (빠름) 선택
- [ ] Phase 전환 기준 확정
- [ ] 회귀 테스트 자동화 방법

---

**작성자**: Claude Sonnet 4.5
**작성일**: 2026-01-20
**버전**: 1.0
**핵심 원칙**: **기존 워크플로우 절대 깨뜨리지 않기**
