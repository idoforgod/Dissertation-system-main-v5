---
description: pTCS + SRCS 실시간 모니터링 대시보드
context: fork
agent: general-purpose
---

# pTCS + SRCS 실시간 모니터링

실시간 신뢰도 모니터링 대시보드를 표시합니다.

## 역할

이 커맨드는 **Confidence Monitor**를 실행하여:
- pTCS 실시간 분포 (🔴🟡🔵🟢)
- Agent 진행 상태
- Gate 통과 상태
- 활성 경고 (Alerts)

## 출력 형식

```
══════════════════════════════════════════════════════════════════════
           THESIS CONFIDENCE MONITOR (pTCS + SRCS)
══════════════════════════════════════════════════════════════════════

Project: AI-free-will-impossibility
Current Phase: 1
Current Agent: literature-searcher
Agent pTCS: 82/100 🔵

──────────────────────────────────────────────────────────────────────
📊 Real-time pTCS Status (Predictive)
──────────────────────────────────────────────────────────────────────
Total Claims: 45
  🔴 Low (0-60):       3 (  6.7%)
  🟡 Medium (61-70):   8 ( 17.8%)
  🔵 Good (71-85):    20 ( 44.4%)
  🟢 High (86-100):   14 ( 31.1%)

Agent Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 20.0%
Completed: 8/41 agents

──────────────────────────────────────────────────────────────────────
🎯 SRCS Gate Status (Evaluative)
──────────────────────────────────────────────────────────────────────
Wave Gates:
  Gate 1: ✅ PASSED (pTCS: 82.0, SRCS: 78.0)
  Gate 2: ⏳ IN PROGRESS
  Gate 3: ⏭️  PENDING

──────────────────────────────────────────────────────────────────────
⚠️  Active Alerts
──────────────────────────────────────────────────────────────────────
1. ⚠️ Warning: Claim LIT-012 has low confidence (pTCS: 58)
2. ⚠️ Warning: Agent trend-analyst needs review (pTCS: 68)
──────────────────────────────────────────────────────────────────────
```

## 실행 방법

```python
import sys
from pathlib import Path
import json

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

from confidence_monitor import ConfidenceMonitor

# Get working directory
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
    project_name = session.get("research", {}).get("topic", "Unknown")
else:
    print("❌ Error: No active session found. Run /thesis:init first.")
    sys.exit(1)

# Initialize monitor
monitor = ConfidenceMonitor(
    project_name=project_name,
    working_dir=working_dir
)

# Generate and display dashboard
dashboard = monitor.generate_dashboard()
print(dashboard)

# Save dashboard snapshot
snapshot_file = working_dir / "confidence-monitor-snapshot.txt"
with open(snapshot_file, 'w') as f:
    f.write(dashboard)

print(f"\n💾 Dashboard snapshot saved to: {snapshot_file}")
```

## 컬러 코딩 (AlphaFold 스타일)

| pTCS 범위 | 색상 | 의미 |
|-----------|------|------|
| 0-60 | 🔴 Red | Immediate review required |
| 61-70 | 🟡 Yellow | Review recommended |
| 71-85 | 🔵 Cyan | Good confidence |
| 86-100 | 🟢 Green | High confidence |

## 사용 시점

- ✅ 문헌검토 진행 중 (Phase 1)
- ✅ 연구설계 진행 중 (Phase 2)
- ✅ 논문작성 진행 중 (Phase 3)
- ✅ Gate 통과 전 품질 확인

## 관련 명령어

- `/thesis:calculate-ptcs` - pTCS 점수 계산
- `/thesis:evaluate-dual-confidence` - pTCS + SRCS 통합 평가
- `/thesis:validate-gate` - Gate 검증

$ARGUMENTS
