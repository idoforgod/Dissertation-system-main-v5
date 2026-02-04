---
description: Autopilot(전자동화) 모드 제어. 워크플로우 전체를 자동 실행하고 HITL 체크포인트를 자동 승인합니다.
---

# Autopilot(전자동화) 모드

워크플로우의 모든 Phase를 순차적으로 자동 실행합니다.
HITL 체크포인트를 자동 승인하되, 품질 미달 시 자동 PAUSE합니다.

## 핵심 정의

**autopilot = 전자동화**:
1. HITL 체크포인트(0~8)만 '자동 승인'한다
2. 워크플로우의 모든 단계를 빠짐없이 '전부' 실행한다
3. 어떤 단계도 '자동 건너뛰기'하지 않는다
4. 품질 기준 미달 시 자동 PAUSE하고 사용자에게 제어권을 반환한다

## 명령어

### 1. Autopilot 활성화

```bash
/thesis:autopilot on [mode]
```

**모드:**
- `full` (기본): 완전 자동. 모든 Phase 실행 + HITL 자동승인
- `semi`: 각 Phase 전에 사용자 확인. HITL에서도 사용자 확인
- `review-only`: 자동 실행 + 결과 표시 + 자동 승인

**예시:**
```bash
/thesis:autopilot on full        # 완전 자동 (전자동화)
/thesis:autopilot on semi        # 반자동 (Phase별 확인)
```

### 2. 특정 Phase까지만

```bash
/thesis:autopilot until [phase]
```

**예시:**
```bash
/thesis:autopilot until phase2   # Phase 2까지만 자동 실행
/thesis:autopilot until phase1   # 문헌검토까지만
```

### 3. 상태 확인

```bash
/thesis:autopilot status
```

session.json에서 autopilot 상태를 읽어 표시합니다:
- 활성 여부, 모드, 현재 Phase/Step
- PAUSE 여부 및 사유
- 자동승인된 HITL 목록
- 품질 점수 현황

### 4. 비활성화

```bash
/thesis:autopilot off
```

Autopilot을 즉시 중단하고 사용자에게 제어권을 반환합니다.

## 작동 방식

Autopilot은 기존 Phase 파이프라인을 순차 연결합니다:

```
Phase 0 → HITL-0,1 자동승인 → Phase 1 → HITL-2 자동승인 →
Phase 2 → HITL-3,4 자동승인 → Phase 3 → HITL-5,6,7 자동승인 →
Phase 4 → HITL-8 자동승인 → Completion
```

**품질 PAUSE 조건** (자동승인 거부):
- pTCS < 75
- SRCS < 75
- plagiarism >= 15%
- doctoral-writing score < 80 (Phase 3)

## 참조

- Implementation: `.claude/agents/thesis/simulation/autopilot-manager.md`
- Workflow Constants: `scripts/workflow_constants.py` (HITL_STEPS, AUTOPILOT_DEFAULTS)
