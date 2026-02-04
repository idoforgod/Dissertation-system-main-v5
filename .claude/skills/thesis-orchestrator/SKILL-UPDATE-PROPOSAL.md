# Skill Update Proposal: Latest Claude Features

## 목표

최신 Claude skills 업데이트 기능을 thesis-orchestrator에 적용하여:
1. 성능 향상 (context forking)
2. 작업별 최적 agent 사용
3. 실시간 업데이트 지원 (hot-reload)

---

## Feature 1: Automatic Hot-Reload

### 현재 상태
✅ 이미 적용됨 (`.claude/skills/` 구조 사용)

### 추가 작업
없음. 새로운 스크립트 추가/수정 시 자동 반영됨.

---

## Feature 2: Context Forking (`context: fork`)

### 적용 전략

#### Tier 1: 필수 Fork (리소스 집약적)

| Command | Context | Reason |
|---------|---------|--------|
| `/thesis:run-literature-review` | `fork` | 15개 agent 순차 실행 (메인 컨텍스트 보호) |
| `/thesis:run-research-design` | `fork` | 4-8개 agent 순차 실행 |
| `/thesis:run-writing` | `fork` | 장별 작성 (대량 출력) |
| `/thesis:evaluate-srcs` | `fork` | SRCS 4축 평가 (계산 집약적) |
| `/thesis:check-plagiarism` | `fork` | 대량 텍스트 비교 |

#### Tier 2: 선택적 Fork (중간 복잡도)

| Command | Context | Reason |
|---------|---------|--------|
| `/thesis:validate-phase` | `fork` | Phase-level 검증 (많은 파일 읽기) |
| `/thesis:validate-all` | `fork` | 전체 검증 (리소스 집약적) |
| `/thesis:run-publication` | `fork` | 학술지 검색 + 포맷팅 |

#### Tier 3: No Fork (빠른 응답 필요)

| Command | Context | Reason |
|---------|---------|--------|
| `/thesis:status` | main | 빠른 상태 확인 필요 |
| `/thesis:progress` | main | 실시간 진행률 확인 |
| `/thesis:init` | main | 초기화 (간단) |
| `/thesis:resume` | main | 컨텍스트 복구 (즉시 실행) |

---

## Feature 3: Agent Field Specification

### Agent 매핑 전략

```yaml
# 1. 문헌 탐색 (빠른 검색 + 분석)
literature-searcher → agent: Explore
seminal-works-analyst → agent: Explore
trend-analyst → agent: Explore
methodology-scanner → agent: Explore

# 2. 심층 분석 (복잡한 다단계)
theoretical-framework-analyst → agent: general-purpose
empirical-evidence-analyst → agent: general-purpose
gap-identifier → agent: general-purpose
variable-relationship-analyst → agent: general-purpose

# 3. 비판적 평가 (전문 분석)
critical-reviewer → agent: general-purpose
methodology-critic → agent: general-purpose
limitation-analyst → agent: general-purpose
future-direction-analyst → agent: general-purpose

# 4. 종합 (복잡한 통합)
synthesis-agent → agent: general-purpose
conceptual-model-builder → agent: general-purpose

# 5. 품질 보증 (계산 집약적)
plagiarism-checker → agent: general-purpose
unified-srcs-evaluator → agent: general-purpose
research-synthesizer → agent: general-purpose

# 6. 연구설계 (다양한 유형)
hypothesis-developer → agent: general-purpose
research-model-developer → agent: Plan
sampling-designer → agent: Plan
statistical-planner → agent: Plan

# 7. 논문작성 (장별 작성)
thesis-architect → agent: Plan
thesis-writer → agent: general-purpose
thesis-reviewer → agent: general-purpose

# 8. 투고전략
publication-strategist → agent: Explore
manuscript-formatter → agent: Bash
```

---

## 구현 예시

### Before (현재)
```yaml
# .claude/commands/thesis/run-literature-review.md
---
description: 문헌검토 파이프라인 실행
---
```

### After (업데이트)
```yaml
# .claude/commands/thesis/run-literature-review.md
---
description: 문헌검토 파이프라인 실행. Wave 1-5를 순차적으로 실행하여 문헌검토를 완료합니다.
context: fork
agent: general-purpose
---
```

---

## pTCS/SRCS 통합 명령어 신규 생성

### 신규 Command 1: pTCS 실시간 모니터링
```yaml
# .claude/commands/thesis/monitor-confidence.md
---
description: pTCS + SRCS 실시간 모니터링 대시보드
context: fork
agent: general-purpose
---

# pTCS + SRCS 실시간 모니터링

python3 .claude/skills/thesis-orchestrator/scripts/confidence_monitor.py --project "$PROJECT_NAME"
```

### 신규 Command 2: pTCS 계산
```yaml
# .claude/commands/thesis/calculate-ptcs.md
---
description: pTCS 점수 계산 (Claim/Agent/Phase/Workflow)
context: fork
agent: Explore
---

# pTCS 계산

python3 .claude/skills/thesis-orchestrator/scripts/ptcs_calculator.py --input "$INPUT_FILE"
```

### 신규 Command 3: Dual Confidence 평가
```yaml
# .claude/commands/thesis/evaluate-dual-confidence.md
---
description: pTCS + SRCS 통합 신뢰도 평가
context: fork
agent: general-purpose
---

# Dual Confidence 평가

python3 .claude/skills/thesis-orchestrator/scripts/dual_confidence_system.py --phase "$PHASE_NUMBER"
```

### 신규 Command 4: Gate 검증
```yaml
# .claude/commands/thesis/validate-gate.md
---
description: Wave/Phase Gate 자동 검증
context: fork
agent: general-purpose
---

# Gate 검증

python3 .claude/skills/thesis-orchestrator/scripts/gate_controller.py --gate-type "$GATE_TYPE" --gate-number "$GATE_NUMBER"
```

---

## 마이그레이션 계획

### Phase 1: 핵심 Commands에 context fork 추가 (1일)
- `/thesis:run-literature-review`
- `/thesis:run-research-design`
- `/thesis:run-writing`

### Phase 2: 계산 집약적 Commands에 fork 추가 (1일)
- `/thesis:evaluate-srcs`
- `/thesis:check-plagiarism`
- `/thesis:validate-phase`
- `/thesis:validate-all`

### Phase 3: Agent field 지정 (1일)
- 각 command에 적절한 agent 매핑
- 테스트 및 성능 비교

### Phase 4: 신규 pTCS Commands 생성 (0.5일)
- `monitor-confidence.md`
- `calculate-ptcs.md`
- `evaluate-dual-confidence.md`
- `validate-gate.md`

---

## 예상 효과

### 1. 성능 향상
- Context forking으로 메인 컨텍스트 보호
- 리소스 집약적 작업 분리 실행

### 2. 안정성 향상
- 대량 출력 작업이 메인 세션에 영향 없음
- Error isolation (fork에서 발생한 오류가 메인에 영향 없음)

### 3. 최적화
- 작업 유형별 최적 agent 사용
- 빠른 작업은 메인에서, 무거운 작업은 fork에서

---

## 테스트 계획

### Test 1: Context Fork 효과
```bash
# Before (no fork)
time /thesis:run-literature-review

# After (with fork)
time /thesis:run-literature-review  # context: fork 적용
```

### Test 2: Agent 최적화
```bash
# 각 agent type별 실행 시간 비교
- Explore vs general-purpose for literature-searcher
- Plan vs general-purpose for thesis-architect
```

### Test 3: 신규 Commands
```bash
/thesis:monitor-confidence
/thesis:calculate-ptcs --input "thesis-output/_temp/01-literature-search-strategy.md"
/thesis:evaluate-dual-confidence --phase 1
/thesis:validate-gate --gate-type wave --gate-number 1
```

---

## 다음 단계

1. 사용자 승인
2. Phase 1-4 순차 구현
3. 각 Phase별 테스트
4. 문서 업데이트 (SKILL.md, QUICK-START.md)
5. 최종 검증

---

**이 제안을 승인하시겠습니까?**

- ✅ 전체 승인 후 순차 구현
- ⚠️ 일부만 선택적 적용
- ❌ 보류 (추가 논의 필요)
