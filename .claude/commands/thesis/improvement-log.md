---
description: 워크플로우 개선 이력 조회 (Audit Trail)
allowed-tools: Read(*), Bash(python3:*), Glob(*), Grep(*)
---

# 개선 이력 조회

전체 개선 분석 이력을 조회하고 트렌드를 확인합니다.

## 실행

```python
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from improvement_logger import ImprovementLogger
from path_utils import get_working_dir_from_session

# 세션에서 작업 디렉토리 자동 감지
try:
    working_dir = get_working_dir_from_session()
except FileNotFoundError:
    print("No active session. Run /thesis:init first.")
    sys.exit(1)

logger = ImprovementLogger(working_dir=working_dir, verbose=True)
```

## 조회 옵션

### 전체 요약

```python
summary = logger.get_summary()
print(f"Total entries: {summary.total_entries}")
print(f"By status: {summary.by_status}")
print(f"By risk: {summary.by_risk}")
```

### 검토 대기 항목

```python
pending = logger.get_pending_review()
for entry in pending:
    print(f"  {entry['entry_id']}: [{entry['risk_category']}] {entry['target']} - {entry['description'][:60]}...")
```

### 전체 이력

```python
history = logger.load_history()
for entry in history:
    status_emoji = {
        "proposed": "...",
        "accepted": "v",
        "rejected": "x",
        "deferred": "~",
        "noted": "i",
        "reviewed": "?",
    }.get(entry['status'], '?')
    print(f"  [{status_emoji}] {entry['entry_id']} | {entry['risk_category']:8s} | {entry['target']}")
```

## 출력 형식

```
══════════════════════════════════════════════════════
  IMPROVEMENT HISTORY
══════════════════════════════════════════════════════

Summary:
  Total entries: 12
  Proposed: 3
  Accepted: 5
  Rejected: 2
  Deferred: 1
  Noted: 1

By Risk Level:
  Critical: 1
  High: 3
  Medium: 5
  Low: 3

──────────────────────────────────────────────────────
Recent Entries:
──────────────────────────────────────────────────────
  [v] HIST-0012 | low      | Agent: thesis-writer
      Run: 2026-01-31-103000
      Decision: Accepted - will add examples

  [x] HIST-0011 | critical | Gate System
      Run: 2026-01-31-103000
      Decision: Rejected - topic-specific issue

  [...] HIST-0010 | medium   | Agent: methodology-critic
      Run: 2026-01-30-150000
      Status: Pending review
══════════════════════════════════════════════════════
```

## 상태 업데이트

이력 항목의 상태를 업데이트하려면:

```python
# Accept a proposal
logger.update_status("HIST-0001", "accepted", "Will apply in next session")

# Reject a proposal
logger.update_status("HIST-0002", "rejected", "Topic-specific, not systemic")

# Defer for later review
logger.update_status("HIST-0003", "deferred", "Need more data from next run")
```

## 데이터 위치

```
thesis-output/<project>/00-session/improvement-data/
├── improvement-history.json         <- 이 파일을 조회
├── performance-metrics-*.json       # 성능 메트릭 (각 분석 실행별)
├── improvement-proposals-*.json     # 개선 제안 (각 분석 실행별)
├── classified-proposals-*.json      # 위험도 분류 (각 분석 실행별)
└── analysis-summary-*.json          # 분석 요약 (각 분석 실행별)
```

## 관련 명령어

- `/thesis:review-improvements` - 성능 분석 실행 및 제안 검토
- `/thesis:monitor-confidence` - 실시간 pTCS 모니터링
- `/thesis:status` - 워크플로우 상태 확인

$ARGUMENTS
