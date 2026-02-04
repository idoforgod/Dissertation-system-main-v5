# 워크플로우 시스템 재설계 계획
# Workflow System Redesign Plan

**작성일**: 2026-01-20
**목적**: 테스트에서 발견된 시스템 결함을 근본적으로 제거
**범위**: Thesis Orchestrator 워크플로우 전체 (Phase 0-4, 150 steps)

---

## Executive Summary

### 테스트 결과 기반 발견된 시스템 결함

| 결함 ID | 결함 내용 | 심각도 | 근본 원인 |
|---------|----------|--------|----------|
| **DEF-001** | Chapter 2, 3 순차 실행 실패 | CRITICAL | 순차 실행 보장 메커니즘 부재 |
| **DEF-002** | 체크리스트 미생성 | HIGH | 초기화 스크립트 검증 누락 |
| **DEF-003** | 최종본 통합 미실행 | CRITICAL | Phase 완료 조건 미검증 |
| **DEF-004** | 참고문헌 자동 정리 미실행 | HIGH | Step 의존성 관리 부재 |
| **DEF-005** | 투고 패키지 생성 미완료 | HIGH | Phase 4 실행 조건 미충족 |
| **DEF-006** | 진행 상태 추적 불가 | HIGH | 체크리스트 자동 업데이트 미작동 |
| **DEF-007** | 에러 복구 메커니즘 부재 | MEDIUM | Checkpoint 시스템 미구현 |

**결론**: 워크플로우 실행 **보장(guarantee) 메커니즘 전무** → 시스템 재설계 필요

---

## 1. 핵심 문제 분석

### 1.1 DEF-001: 순차 실행 보장 실패 (CRITICAL)

#### 현상
```
Chapter 1 ✅ → Chapter 2 ❌ → Chapter 3 ❌ → Chapter 4 ✅ → Chapter 5 ✅
```

#### 근본 원인
1. **Agent 호출 로직에 검증 없음**
   ```python
   # 현재 (추정)
   for chapter in [1, 2, 3, 4, 5]:
       run_agent("@thesis-writer", chapter=chapter)
       # ❌ 성공 여부 검증 없음
       # ❌ 파일 생성 확인 없음
   ```

2. **실패 시 중단 로직 없음**
   - Ch.2 실행 실패 시에도 Ch.3, 4, 5 계속 진행
   - 사용자에게 실패 알림 없음

3. **의존성 관리 부재**
   - Ch.4는 Ch.2, Ch.3에 의존하지만 검증 안 함

#### 영향
- 불완전한 논문 생성 (50% 누락)
- 사용자가 완료되었다고 착각
- 데이터 무결성 훼손

### 1.2 DEF-002: 체크리스트 미생성 (HIGH)

#### 근본 원인
```python
# init_session.py (추정)
def initialize_session(topic, mode, base_dir):
    create_directories()
    create_session_json()
    # ❌ create_checklist() 호출 조건부?
    # ❌ 또는 실패 시 에러 무시?
```

#### 영향
- 150단계 진행 상태 추적 불가
- 어느 단계가 완료되었는지 알 수 없음
- 디버깅 불가능

### 1.3 DEF-003: 최종본 통합 미실행 (CRITICAL)

#### 근본 원인
```python
# Step 129: 최종본 작성
# 조건: Ch.1-5 모두 완료

if all_chapters_completed():  # ❌ 이 검증이 없거나 잘못됨
    integrate_chapters()
else:
    # ❌ 에러 발생하지 않고 조용히 스킵
    pass
```

#### 영향
- thesis-final.md 미생성
- 제출 불가능한 상태

### 1.4 DEF-004, 005: Phase 4 실행 조건 미충족

#### 근본 원인
```python
# Phase 3 → Phase 4 전환 조건
if phase3_completed:  # ❌ 정의가 모호
    start_phase4()

# "completed"의 정의가 불명확:
# - 일부 챕터만 작성돼도 completed?
# - thesis-final.md 없어도 completed?
# - 참고문헌 없어도 completed?
```

#### 영향
- Phase 4가 부분적으로만 실행
- 투고 패키지 미생성

### 1.5 DEF-006: 체크리스트 자동 업데이트 미작동

#### 근본 원인
```python
# 각 Agent 실행 후
run_agent("@thesis-writer")
# ❌ 체크리스트 업데이트 호출 없음
# update_checklist(step=115, status="completed")
```

#### 영향
- 수동 추적 필요
- 진행률 파악 불가

---

## 2. 시스템 재설계 원칙

### 2.1 Fail-Fast 원칙

**현재**: 실패해도 계속 진행 (Fail-Silent)
**개선**: 실패 시 즉시 중단 및 에러 보고 (Fail-Fast)

```python
# BEFORE
for step in steps:
    try:
        execute(step)
    except:
        pass  # ❌ 조용히 무시

# AFTER
for step in steps:
    result = execute(step)
    if not result.success:
        raise WorkflowError(f"Step {step} failed: {result.error}")
        # 사용자에게 즉시 알림
```

### 2.2 Verification-First 원칙

**현재**: 실행 후 검증 없음
**개선**: 모든 단계 후 필수 산출물 검증

```python
# AFTER
REQUIRED_OUTPUTS = {
    115: ["chapter1-*.md"],
    117: ["chapter2-*.md"],
    129: ["thesis-final.md", "references.md"]
}

def execute_step(step):
    run_step(step)
    verify_outputs(REQUIRED_OUTPUTS[step])  # ✅ 필수
    update_checklist(step, "completed")     # ✅ 자동
```

### 2.3 Explicit Dependencies 원칙

**현재**: 암묵적 의존성
**개선**: 명시적 의존성 선언 및 검증

```python
# AFTER
STEP_DEPENDENCIES = {
    117: [115],           # Ch.2는 Ch.1 필요
    119: [115, 117],      # Ch.3은 Ch.1, Ch.2 필요
    129: [115,117,119,121,123]  # 통합본은 모든 챕터 필요
}

def execute_step(step):
    for dep in STEP_DEPENDENCIES.get(step, []):
        if not is_completed(dep):
            raise DependencyError(f"Step {step} requires step {dep}")
```

### 2.4 Atomic Operations 원칙

**현재**: 부분 완료 상태 허용
**개선**: 모두 성공 또는 모두 실패 (Atomicity)

```python
# AFTER
def run_phase3():
    checkpoint = create_checkpoint()
    try:
        for chapter in [1, 2, 3, 4, 5]:
            write_chapter(chapter)
            verify_chapter(chapter)
        integrate_chapters()
        verify_integration()
    except Exception as e:
        rollback(checkpoint)
        raise PhaseError(f"Phase 3 failed: {e}")
```

### 2.5 Progress Transparency 원칙

**현재**: 진행 상태 불투명
**개선**: 실시간 진행률 표시

```python
# AFTER
def execute_workflow():
    total_steps = 150
    for i, step in enumerate(steps, 1):
        print(f"[{i}/{total_steps}] {step.description}")
        execute_step(step)
        update_progress(i, total_steps)  # 66.7% (100/150)
```

---

## 3. 구체적 개선 방안

### 3.1 필수 산출물 검증 시스템 (DEF-001, 003, 004 해결)

#### 구현: `workflow_validator.py`

```python
#!/usr/bin/env python3
"""Workflow output validation system."""

from pathlib import Path
from typing import List, Dict
import re

# 각 Step의 필수 산출물 정의
REQUIRED_OUTPUTS: Dict[int, List[str]] = {
    # Phase 0
    1: ["00-session/session.json"],
    7: ["00-session/todo-checklist.md"],

    # Phase 3 (Critical)
    111: ["03-thesis/thesis-outline.md"],
    115: ["03-thesis/chapter1-*.md"],
    117: ["03-thesis/chapter2-*.md"],  # ⭐ 필수
    119: ["03-thesis/chapter3-*.md"],  # ⭐ 필수
    121: ["03-thesis/chapter4-*.md"],
    123: ["03-thesis/chapter5-*.md"],
    129: ["03-thesis/thesis-final.md"],  # ⭐ 필수
    130: ["03-thesis/references.md"],

    # Phase 4
    138: ["04-publication/manuscript-formatted.md"],
    139: ["04-publication/abstract-english.md"],
    141: ["04-publication/cover-letter.md"],
}

class OutputValidator:
    def __init__(self, working_dir: Path):
        self.working_dir = working_dir

    def validate_step(self, step: int) -> tuple[bool, List[str]]:
        """Validate required outputs for a step.

        Returns:
            (success, missing_files)
        """
        required = REQUIRED_OUTPUTS.get(step, [])
        missing = []

        for pattern in required:
            matches = list(self.working_dir.glob(pattern))
            if not matches:
                missing.append(pattern)

        return len(missing) == 0, missing

    def validate_phase(self, phase: int) -> Dict[str, any]:
        """Validate all steps in a phase."""
        phase_steps = {
            0: range(1, 19),
            1: range(19, 89),
            2: range(89, 109),
            3: range(109, 133),
            4: range(133, 151)
        }[phase]

        results = {}
        for step in phase_steps:
            success, missing = self.validate_step(step)
            if not success:
                results[step] = missing

        return results

    def enforce_step(self, step: int):
        """Enforce validation - raise error if files missing."""
        success, missing = self.validate_step(step)
        if not success:
            raise ValidationError(
                f"Step {step} validation failed. Missing files:\n" +
                "\n".join(f"  - {f}" for f in missing)
            )

class ValidationError(Exception):
    pass
```

#### 통합: 모든 Agent 실행 후 검증

```python
# sequential_executor.py (개선)

from workflow_validator import OutputValidator, ValidationError

def execute_step(step: int, agent: str, **kwargs):
    """Execute a step with validation."""

    # 1. 실행 전 의존성 검증
    verify_dependencies(step)

    # 2. Agent 실행
    result = run_agent(agent, **kwargs)

    # 3. ✅ 실행 후 필수 산출물 검증
    validator = OutputValidator(working_dir)
    try:
        validator.enforce_step(step)
    except ValidationError as e:
        # 실패 시 즉시 중단 및 사용자 알림
        log_error(f"Step {step} failed validation: {e}")
        raise WorkflowError(f"Cannot proceed. {e}")

    # 4. 체크리스트 업데이트
    update_checklist(step, "completed")

    return result
```

### 3.2 체크리스트 자동 관리 시스템 (DEF-002, 006 해결)

#### 구현: `checklist_manager.py` 개선

```python
# 기존 checklist_manager.py에 추가

class ChecklistManager:
    def __init__(self, checklist_path: Path):
        self.path = checklist_path
        if not self.path.exists():
            raise ChecklistError(f"Checklist not found: {checklist_path}")
        self.data = self._load()

    def _load(self) -> List[Dict]:
        """Load checklist from markdown."""
        # Parse markdown and extract step status
        pass

    def update_step(self, step: int, status: str):
        """Update step status and save."""
        if status not in ["pending", "in_progress", "completed"]:
            raise ValueError(f"Invalid status: {status}")

        self.data[step-1]["status"] = status
        self.data[step-1]["updated_at"] = datetime.now()
        self._save()

    def _save(self):
        """Save checklist to markdown."""
        # Generate markdown from data
        pass

    def get_progress(self) -> Dict:
        """Get progress statistics."""
        completed = sum(1 for s in self.data if s["status"] == "completed")
        total = len(self.data)
        return {
            "completed": completed,
            "total": total,
            "percentage": completed / total * 100,
            "current_step": self._get_current_step()
        }

    def verify_all_completed(self, steps: List[int]) -> bool:
        """Verify all specified steps are completed."""
        for step in steps:
            if self.data[step-1]["status"] != "completed":
                return False
        return True

class ChecklistError(Exception):
    pass
```

#### init_session.py 개선: 체크리스트 생성 강제

```python
# init_session.py (개선)

def initialize_session(topic, mode, base_dir):
    # 1. 디렉토리 생성
    working_dir = create_directories(topic, base_dir)

    # 2. session.json 생성
    create_session_json(working_dir, topic, mode)

    # 3. ✅ 체크리스트 생성 (필수)
    checklist_path = create_checklist(working_dir)

    # 4. ✅ 생성 검증
    if not checklist_path.exists():
        raise InitializationError("Failed to create checklist")

    # 5. session.json에 경로 기록
    session = load_session_json(working_dir)
    session["checklist_path"] = str(checklist_path)
    save_session_json(working_dir, session)

    return working_dir

def create_checklist(working_dir: Path) -> Path:
    """Create 150-step checklist."""
    from checklist_manager import ChecklistManager

    checklist_path = working_dir / "00-session" / "todo-checklist.md"

    # Use checklist_manager.py create function
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/checklist_manager.py", "create", str(working_dir)],
        cwd=Path(__file__).parent,
        capture_output=True
    )

    if result.returncode != 0:
        raise InitializationError(f"Checklist creation failed: {result.stderr}")

    return checklist_path
```

### 3.3 순차 실행 보장 메커니즘 (DEF-001 해결)

#### 구현: `sequential_executor.py` 개선

```python
#!/usr/bin/env python3
"""Sequential execution engine with guarantees."""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging

@dataclass
class Step:
    id: int
    description: str
    agent: str
    dependencies: List[int]
    required_outputs: List[str]
    params: Dict

class SequentialExecutor:
    def __init__(self, working_dir: Path):
        self.working_dir = working_dir
        self.validator = OutputValidator(working_dir)
        self.checklist = ChecklistManager(working_dir / "00-session" / "todo-checklist.md")
        self.logger = logging.getLogger(__name__)

    def execute_phase3_writing(self):
        """Execute Phase 3 with strict guarantees."""

        chapters = [
            Step(115, "Chapter 1: Introduction", "@thesis-writer",
                 [114], ["03-thesis/chapter1-*.md"], {"chapter": 1}),
            Step(117, "Chapter 2: Literature Review", "@thesis-writer",
                 [115, 116], ["03-thesis/chapter2-*.md"], {"chapter": 2}),  # ⭐
            Step(119, "Chapter 3: Methodology", "@thesis-writer",
                 [117, 118], ["03-thesis/chapter3-*.md"], {"chapter": 3}),  # ⭐
            Step(121, "Chapter 4: Results", "@thesis-writer",
                 [119, 120], ["03-thesis/chapter4-*.md"], {"chapter": 4}),
            Step(123, "Chapter 5: Conclusion", "@thesis-writer",
                 [121, 122], ["03-thesis/chapter5-*.md"], {"chapter": 5}),
        ]

        # ✅ 순차 실행 보장
        for step in chapters:
            self._execute_step_with_validation(step)

        # ✅ 통합 단계 (모든 챕터 필수)
        integration = Step(129, "Integrate all chapters", "@thesis-integrator",
                          [115, 117, 119, 121, 123],  # 모든 챕터 필수
                          ["03-thesis/thesis-final.md"], {})
        self._execute_step_with_validation(integration)

    def _execute_step_with_validation(self, step: Step):
        """Execute single step with full validation."""

        # 1. ✅ 의존성 검증
        for dep in step.dependencies:
            if not self.checklist.is_completed(dep):
                raise DependencyError(
                    f"Step {step.id} requires step {dep} to be completed first"
                )

        # 2. 진행 상태 업데이트
        self.checklist.update_step(step.id, "in_progress")
        self.logger.info(f"[{step.id}/150] {step.description}")

        # 3. Agent 실행
        try:
            result = self._run_agent(step.agent, **step.params)
        except Exception as e:
            self.logger.error(f"Agent execution failed: {e}")
            raise ExecutionError(f"Step {step.id} failed: {e}")

        # 4. ✅ 필수 산출물 검증
        for output_pattern in step.required_outputs:
            matches = list(self.working_dir.glob(output_pattern))
            if not matches:
                raise ValidationError(
                    f"Step {step.id} failed: Required output '{output_pattern}' not found"
                )

        # 5. 완료 표시
        self.checklist.update_step(step.id, "completed")
        self.logger.info(f"✅ Step {step.id} completed")

    def _run_agent(self, agent: str, **params) -> any:
        """Run agent using Task tool."""
        # Implementation using claude-code Task tool
        pass

class DependencyError(Exception):
    pass

class ExecutionError(Exception):
    pass
```

### 3.4 Phase 완료 조건 명확화 (DEF-003, 005 해결)

#### 구현: `phase_transitions.py`

```python
#!/usr/bin/env python3
"""Phase transition validation."""

from pathlib import Path
from typing import List

class PhaseValidator:
    def __init__(self, working_dir: Path):
        self.working_dir = working_dir
        self.checklist = ChecklistManager(working_dir / "00-session" / "todo-checklist.md")

    def validate_phase3_completion(self) -> tuple[bool, List[str]]:
        """Validate Phase 3 is fully completed."""

        errors = []

        # ✅ 모든 챕터 존재 검증
        required_chapters = [
            "03-thesis/chapter1-*.md",
            "03-thesis/chapter2-*.md",  # ⭐ 필수
            "03-thesis/chapter3-*.md",  # ⭐ 필수
            "03-thesis/chapter4-*.md",
            "03-thesis/chapter5-*.md",
        ]

        for pattern in required_chapters:
            if not list(self.working_dir.glob(pattern)):
                errors.append(f"Missing: {pattern}")

        # ✅ 통합본 존재 검증
        if not (self.working_dir / "03-thesis" / "thesis-final.md").exists():
            errors.append("Missing: thesis-final.md")

        # ✅ 참고문헌 존재 검증
        if not (self.working_dir / "03-thesis" / "references.md").exists():
            errors.append("Missing: references.md")

        # ✅ 체크리스트 단계 검증
        required_steps = list(range(109, 133))  # Step 109-132
        if not self.checklist.verify_all_completed(required_steps):
            incomplete = [s for s in required_steps if not self.checklist.is_completed(s)]
            errors.append(f"Incomplete steps: {incomplete}")

        return len(errors) == 0, errors

    def enforce_phase3_completion(self):
        """Enforce Phase 3 completion - raise error if not complete."""
        success, errors = self.validate_phase3_completion()
        if not success:
            raise PhaseIncompleteError(
                "Phase 3 is not complete. Cannot proceed to Phase 4.\n" +
                "Missing items:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )

class PhaseIncompleteError(Exception):
    pass
```

#### 통합: Phase 전환 시 검증

```python
# 워크플로우 오케스트레이터에서

def transition_to_phase4():
    """Transition from Phase 3 to Phase 4."""

    # ✅ Phase 3 완료 검증 (강제)
    validator = PhaseValidator(working_dir)
    validator.enforce_phase3_completion()

    # 검증 통과 시에만 Phase 4 진행
    execute_phase4()
```

### 3.5 에러 복구 메커니즘 (DEF-007 해결)

#### 구현: Checkpoint 시스템

```python
#!/usr/bin/env python3
"""Checkpoint and recovery system."""

import json
from pathlib import Path
from datetime import datetime
import shutil

class CheckpointManager:
    def __init__(self, working_dir: Path):
        self.working_dir = working_dir
        self.checkpoint_dir = working_dir / "00-session" / "checkpoints"
        self.checkpoint_dir.mkdir(exist_ok=True)

    def create_checkpoint(self, step: int, description: str) -> Path:
        """Create a checkpoint before risky operation."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_name = f"step{step:03d}_{timestamp}"
        checkpoint_path = self.checkpoint_dir / checkpoint_name

        # Save current state
        state = {
            "step": step,
            "description": description,
            "timestamp": timestamp,
            "session": self._read_session_json(),
            "checklist_state": self._get_checklist_state(),
            "files": self._list_output_files()
        }

        checkpoint_path.mkdir(exist_ok=True)
        (checkpoint_path / "state.json").write_text(json.dumps(state, indent=2))

        return checkpoint_path

    def rollback(self, checkpoint_path: Path):
        """Rollback to a checkpoint."""

        state = json.loads((checkpoint_path / "state.json").read_text())

        # Restore checklist state
        self._restore_checklist_state(state["checklist_state"])

        # Restore session.json
        self._write_session_json(state["session"])

        # Note: Files are not deleted (preserve for debugging)
        # But checklist state is rolled back

    def list_checkpoints(self) -> List[Dict]:
        """List available checkpoints."""
        checkpoints = []
        for cp_dir in sorted(self.checkpoint_dir.iterdir()):
            if cp_dir.is_dir():
                state_file = cp_dir / "state.json"
                if state_file.exists():
                    state = json.loads(state_file.read_text())
                    checkpoints.append({
                        "path": cp_dir,
                        "step": state["step"],
                        "description": state["description"],
                        "timestamp": state["timestamp"]
                    })
        return checkpoints
```

#### 통합: 위험한 작업 전 Checkpoint

```python
def execute_risky_step(step: int):
    """Execute step with checkpoint protection."""

    checkpoint_mgr = CheckpointManager(working_dir)

    # ✅ Checkpoint 생성
    checkpoint = checkpoint_mgr.create_checkpoint(step, steps[step].description)

    try:
        execute_step(step)
    except Exception as e:
        # ✅ 실패 시 Rollback
        logger.error(f"Step {step} failed. Rolling back...")
        checkpoint_mgr.rollback(checkpoint)
        raise
```

---

## 4. 구현 우선순위

### Phase 1: 핵심 검증 시스템 (1주)

| 우선순위 | 작업 | 산출물 | 소요 |
|---------|------|--------|------|
| **P0** | 필수 산출물 검증 시스템 | `workflow_validator.py` | 2일 |
| **P0** | 순차 실행 보장 메커니즘 | `sequential_executor.py` 개선 | 2일 |
| **P0** | Phase 완료 조건 검증 | `phase_transitions.py` | 1일 |
| **P1** | 체크리스트 강제 생성 | `init_session.py` 개선 | 1일 |
| **P1** | 통합 테스트 | Phase 3 완전 실행 검증 | 1일 |

### Phase 2: 자동화 개선 (1주)

| 우선순위 | 작업 | 산출물 | 소요 |
|---------|------|--------|------|
| **P1** | 체크리스트 자동 업데이트 | `checklist_manager.py` 개선 | 2일 |
| **P1** | 진행률 실시간 표시 | UI 개선 | 1일 |
| **P2** | Checkpoint 시스템 | `checkpoint_manager.py` | 2일 |
| **P2** | 로깅 시스템 강화 | 구조화된 로그 | 1일 |

### Phase 3: 안정성 강화 (1주)

| 우선순위 | 작업 | 산출물 | 소요 |
|---------|------|--------|------|
| **P2** | 에러 복구 메커니즘 | Rollback 기능 | 2일 |
| **P2** | HITL 프로세스 명확화 | 명시적 확인 프롬프트 | 2일 |
| **P3** | 성능 최적화 | 병렬 실행 (안전한 부분만) | 2일 |

---

## 5. 검증 방법

### 5.1 단위 테스트

```python
# tests/test_workflow_validator.py

def test_step_validation():
    """Test step output validation."""
    validator = OutputValidator(test_working_dir)

    # Step 115: Ch.1 required
    create_file(test_working_dir / "03-thesis" / "chapter1-intro.md")
    success, missing = validator.validate_step(115)
    assert success == True
    assert missing == []

    # Step 117: Ch.2 required (missing)
    success, missing = validator.validate_step(117)
    assert success == False
    assert "chapter2-*.md" in missing[0]

def test_sequential_execution():
    """Test chapters are written in sequence."""
    executor = SequentialExecutor(test_working_dir)

    # Should write Ch.1, 2, 3, 4, 5 in order
    executor.execute_phase3_writing()

    # Verify all chapters exist
    for i in [1, 2, 3, 4, 5]:
        assert list(test_working_dir.glob(f"03-thesis/chapter{i}-*.md"))
```

### 5.2 통합 테스트

```bash
#!/bin/bash
# tests/integration/test_full_workflow.sh

# 1. 초기화
python3 init_session.py "Test Topic" --mode topic

# 2. 체크리스트 존재 검증
if [ ! -f "todo-checklist.md" ]; then
    echo "FAIL: Checklist not created"
    exit 1
fi

# 3. Phase 3 실행
python3 run_phase3.py

# 4. 모든 챕터 존재 검증
for ch in {1..5}; do
    if ! ls 03-thesis/chapter${ch}-*.md 1> /dev/null 2>&1; then
        echo "FAIL: Chapter ${ch} missing"
        exit 1
    fi
done

# 5. 통합본 존재 검증
if [ ! -f "03-thesis/thesis-final.md" ]; then
    echo "FAIL: thesis-final.md missing"
    exit 1
fi

echo "PASS: All tests passed"
```

### 5.3 End-to-End 테스트

```python
# tests/e2e/test_complete_workflow.py

def test_complete_workflow():
    """Test complete workflow from init to finalize."""

    # Phase 0
    working_dir = init_session("E2E Test Topic", "topic")
    assert (working_dir / "00-session" / "session.json").exists()
    assert (working_dir / "00-session" / "todo-checklist.md").exists()

    # Phase 1
    run_phase1()
    assert (working_dir / "00-session" / "research-synthesis.md").exists()

    # Phase 2
    run_phase2()
    assert (working_dir / "02-research-design" / "paradigm-statement.md").exists()

    # Phase 3 (Critical)
    run_phase3()
    for ch in [1, 2, 3, 4, 5]:
        assert list(working_dir.glob(f"03-thesis/chapter{ch}-*.md")), \
            f"Chapter {ch} missing"
    assert (working_dir / "03-thesis" / "thesis-final.md").exists()
    assert (working_dir / "03-thesis" / "references.md").exists()

    # Phase 4
    run_phase4()
    assert (working_dir / "04-publication" / "manuscript-formatted.md").exists()

    # Checklist 완료 검증
    checklist = ChecklistManager(working_dir / "00-session" / "todo-checklist.md")
    progress = checklist.get_progress()
    assert progress["percentage"] == 100.0, \
        f"Workflow incomplete: {progress['percentage']}%"
```

---

## 6. 롤아웃 계획

### 6.1 Phase 1 롤아웃 (1주차)

**목표**: 핵심 검증 시스템 구현

**Step 1**: `workflow_validator.py` 구현
```bash
# Day 1-2
touch .claude/skills/thesis-orchestrator/scripts/workflow_validator.py
# Implement REQUIRED_OUTPUTS and OutputValidator class
```

**Step 2**: `sequential_executor.py` 개선
```bash
# Day 3-4
# Add validation to execute_step()
# Add dependency checking
```

**Step 3**: 통합 테스트
```bash
# Day 5
pytest tests/test_workflow_validator.py
pytest tests/integration/test_phase3.py
```

### 6.2 Phase 2 롤아웃 (2주차)

**목표**: 자동화 개선

**Step 1**: 체크리스트 자동 업데이트
**Step 2**: 진행률 UI
**Step 3**: Checkpoint 시스템

### 6.3 Phase 3 롤아웃 (3주차)

**목표**: 안정성 강화 및 최종 검증

**Step 1**: 에러 복구
**Step 2**: End-to-End 테스트
**Step 3**: 프로덕션 배포

---

## 7. 성공 기준

### 7.1 필수 요구사항 (Must Have)

- [ ] **Chapter 2, 3 생략 불가능**: 모든 5개 챕터 필수 생성
- [ ] **thesis-final.md 자동 생성**: Step 129 100% 실행
- [ ] **체크리스트 자동 생성**: init_session.py 100% 성공률
- [ ] **진행률 실시간 추적**: 150단계 모두 추적 가능
- [ ] **실패 시 즉시 중단**: Fail-Fast 원칙 100% 적용

### 7.2 검증 가능한 지표

| 지표 | 현재 | 목표 | 측정 방법 |
|------|------|------|----------|
| 워크플로우 완료율 | 80% | 100% | E2E 테스트 통과율 |
| 필수 파일 누락률 | 42% | 0% | 검증 시스템 통과율 |
| 체크리스트 생성율 | 0% | 100% | init 성공률 |
| Phase 3 완성도 | 58% | 100% | 5개 챕터 모두 존재 |
| Phase 4 완성도 | 17% | 100% | 투고 패키지 완성 |

### 7.3 회귀 테스트

**보장**: 테스트 통과 후 동일 문제 재발 불가

```bash
# 매 커밋마다 실행
./tests/regression/test_chapter_generation.sh
# ✅ 모든 5개 챕터 생성 검증
# ✅ thesis-final.md 생성 검증
# ✅ 체크리스트 존재 검증
```

---

## 8. 마이그레이션 전략

### 8.1 기존 워크플로우와의 호환성

**방침**: 점진적 마이그레이션

```python
# 환경 변수로 제어
STRICT_MODE = os.getenv("THESIS_STRICT_MODE", "false") == "true"

if STRICT_MODE:
    # 새로운 검증 시스템 사용
    validator.enforce_step(step)
else:
    # 기존 방식 (경고만)
    success, missing = validator.validate_step(step)
    if not success:
        logger.warning(f"Validation failed (non-strict): {missing}")
```

### 8.2 테스트 환경

```bash
# 테스트용 strict mode
export THESIS_STRICT_MODE=true
./run_workflow_test.sh

# 프로덕션 전환 (Phase 3 롤아웃 후)
# .env 파일에 추가
THESIS_STRICT_MODE=true
```

---

## 9. 문서화 계획

### 9.1 업데이트 필요 문서

| 문서 | 경로 | 업데이트 내용 |
|------|------|--------------|
| SKILL.md | thesis-orchestrator/SKILL.md | 검증 시스템 설명 추가 |
| README.md | thesis-orchestrator/README.md | 새로운 보장 사항 명시 |
| Agent 정의 | agents/thesis/phase3-writing/*.md | 필수 산출물 명시 |

### 9.2 신규 문서

- `GUARANTEES.md`: 시스템이 보장하는 사항 명시
- `TROUBLESHOOTING.md`: 검증 실패 시 대처 방법
- `ARCHITECTURE.md`: 검증 시스템 아키텍처

---

## 10. 리스크 관리

### 10.1 예상 리스크

| 리스크 | 확률 | 영향 | 대응 |
|--------|------|------|------|
| 검증이 너무 엄격해서 정상 워크플로우 차단 | 중간 | 높음 | 검증 로직 신중히 설계, 테스트 충분히 |
| 성능 저하 (검증 오버헤드) | 낮음 | 중간 | 병렬화, 캐싱 |
| 기존 사용자 워크플로우 중단 | 낮음 | 높음 | 점진적 마이그레이션, STRICT_MODE |

### 10.2 롤백 계획

**만약 심각한 버그 발견 시**:
```bash
# 1. STRICT_MODE 비활성화
export THESIS_STRICT_MODE=false

# 2. 이전 버전으로 롤백
git revert <commit>

# 3. 핫픽스 적용
git cherry-pick <fix-commit>
```

---

## 11. 결론

### 11.1 핵심 개선 사항

1. **Fail-Fast**: 실패 시 즉시 중단 및 에러 보고
2. **Verification-First**: 모든 단계 후 필수 산출물 검증
3. **Explicit Dependencies**: 의존성 명시 및 자동 검증
4. **Progress Transparency**: 실시간 진행률 표시
5. **Atomic Operations**: 부분 완료 상태 불가

### 11.2 기대 효과

| 효과 | 현재 | 개선 후 |
|------|------|---------|
| 워크플로우 완료율 | 80% | 100% |
| 필수 파일 생성율 | 58% | 100% |
| 사용자 신뢰도 | 낮음 | 높음 |
| 디버깅 시간 | 높음 | 낮음 |
| 재실행 필요성 | 높음 | 낮음 |

### 11.3 다음 단계

**즉시 시작**:
1. `workflow_validator.py` 구현 (P0)
2. `sequential_executor.py` 개선 (P0)
3. 통합 테스트 작성

**논의 필요**:
- STRICT_MODE 기본값 (true vs. false)
- 검증 실패 시 사용자 경험 (에러 메시지 형식)
- 롤아웃 일정 조정

---

**작성자**: Claude Sonnet 4.5
**작성일**: 2026-01-20
**버전**: 1.0
**상태**: 논의 필요
