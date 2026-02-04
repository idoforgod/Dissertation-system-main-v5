---
description: 워크플로우 성능 분석 실행 및 개선 제안 검토 (Advisory Only)
allowed-tools: Read(*), Bash(python3:*), Glob(*), Grep(*)
---

# 성능 분석 및 개선 제안 검토

워크플로우 성능을 분석하고 개선 제안을 검토합니다.

## 핵심 원칙

- **Advisory Only**: 모든 제안은 자문 사항입니다. 자동으로 어떤 파일도 수정되지 않습니다.
- **Read-Only**: 기존 워크플로우 파일을 절대 수정하지 않습니다.
- **Human Decision**: 모든 결정은 사용자가 내립니다.

## 실행

### 1단계: 성능 분석 실행

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from self_improvement_engine import SelfImprovementEngine
from path_utils import get_working_dir_from_session

# 세션에서 작업 디렉토리 자동 감지
try:
    working_dir = get_working_dir_from_session()
except FileNotFoundError:
    print("No active session. Run /thesis:init first.")
    sys.exit(1)

# 엔진 실행 (Advisory 모드)
engine = SelfImprovementEngine(working_dir=working_dir, verbose=True)
results = engine.run_report()
```

### 2단계: 제안 검토

분석 결과에서 개선 제안을 검토합니다. 각 제안에 대해:

```
┌─────────────────────────────────────────────────┐
│  IMPROVEMENT PROPOSAL REVIEW                     │
├─────────────────────────────────────────────────┤
│  ID: IMP-001                                     │
│  Target: Agent: variable-relationship-analyst     │
│  Risk: medium                                    │
│  Description: Agent has low pTCS (68.5).         │
│  Guidance: Review agent prompt for clarity.       │
│                                                   │
│  Decision: [Accept] [Reject] [Defer] [Note]      │
└─────────────────────────────────────────────────┘
```

### 3단계: 결정 기록

사용자의 결정을 이력에 기록합니다:

```python
from improvement_logger import ImprovementLogger

logger = ImprovementLogger(working_dir=working_dir)

# 각 제안에 대한 결정 기록
# logger.update_status("HIST-0001", "accepted", "Will review prompt")
# logger.update_status("HIST-0002", "rejected", "Topic-specific issue")
# logger.update_status("HIST-0003", "deferred", "Review after next run")
```

## 출력 형식

### 분석 요약

```
════════════════════════════════════════════════════════
  PERFORMANCE ANALYSIS SUMMARY (Advisory)
════════════════════════════════════════════════════════

Performance Metrics:
  Average pTCS: XX.X/100
  Average SRCS: XX.X/100
  Gate Pass Rate: XX%
  Total Retries: X

Improvement Proposals: N
  Critical: X
  High:     X
  Medium:   X
  Low:      X

Next Steps:
  1. Review each proposal below
  2. Accept, reject, or defer
  3. Manually apply accepted changes if desired
════════════════════════════════════════════════════════
```

### 제안 상세

각 제안에 대해 다음 정보를 표시합니다:
- **ID**: 제안 식별자
- **Type**: prompt_review / threshold_review / structural_review
- **Target**: 대상 컴포넌트
- **Risk**: critical / high / medium / low
- **Description**: 상세 설명
- **Evidence**: 데이터 기반 근거
- **Guidance**: 검토 시 참고 사항

## 상태값

| 상태 | 의미 |
|------|------|
| proposed | 분석에서 도출됨 (검토 대기) |
| reviewed | 검토 완료 |
| accepted | 승인 (수동 적용 예정) |
| rejected | 거절 (조치 불필요) |
| deferred | 보류 (다음 검토 시 재확인) |
| noted | 참고 사항 (조치 불필요) |

## 관련 명령어

- `/thesis:improvement-log` - 전체 이력 조회
- `/thesis:monitor-confidence` - 실시간 pTCS 모니터링
- `/thesis:validate-gate` - Gate 검증

$ARGUMENTS
