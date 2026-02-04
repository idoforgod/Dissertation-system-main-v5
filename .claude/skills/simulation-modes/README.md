# Simulation Modes

시뮬레이션 기능을 위한 Subagent들입니다. **Skill interface 없이** 직접 Task tool로 호출됩니다.

## 사용법

```bash
# 메인 AI가 자연어 요청을 이해하고 직접 Subagent 호출

사용자: "Quick 모드로 Phase 3 작성해줘"
→ AI: Task(subagent_type="simulation-controller", prompt="...")

사용자: "양적/질적/혼합 3가지 옵션 비교해줘"
→ AI: Task(subagent_type="alphago-evaluator", prompt="...")

사용자: "Autopilot으로 Phase 2까지 자동 실행"
→ AI: Task(subagent_type="autopilot-manager", prompt="...")
```

## Subagent 목록

### 1. simulation-controller
- **위치**: `.claude/agents/thesis/simulation/simulation-controller.md`
- **역할**: Quick/Full 시뮬레이션 실행 및 품질 검증
- **입력**: mode (quick|full|both), phase, context
- **출력**: simulation_result (pTCS, SRCS, files)

### 2. alphago-evaluator
- **위치**: `.claude/agents/thesis/simulation/alphago-evaluator.md`
- **역할**: 여러 옵션을 Quick으로 평가하여 최적안 추천
- **입력**: options[], context
- **출력**: evaluation_results, recommendation

### 3. autopilot-manager
- **위치**: `.claude/agents/thesis/simulation/autopilot-manager.md`
- **역할**: 불확실성 분석하여 자동으로 모드 선택 및 실행
- **입력**: command (on|off|until), mode, target_phase
- **출력**: autopilot_status, execution_log

### 4. thesis-writer-quick-rlm
- **위치**: `.claude/agents/thesis/phase3-writing/thesis-writer-quick-rlm.md`
- **역할**: RLM 기술로 Quick 모드 논문 작성 (3-5p/chapter)
- **입력**: chapter, context_files[]
- **출력**: compressed_chapter

## 왜 Skill Interface가 없나?

```yaml
이전 (비효율):
  User request → SKILL.md (850 tokens) → Task(Subagent)

  문제: SKILL.md는 "어떤 Subagent 호출하라"만 알려줌
       → 메인 AI가 이미 할 수 있는 일

현재 (효율):
  User request → Task(Subagent)

  이유: 메인 AI는 시스템 프롬프트에서 모든 Subagent 알고 있음
       → 자연어 이해로 직접 적절한 Subagent 선택

컨텍스트 절약: 850 tokens (100%)
```

## 컨텍스트 효율성

```yaml
메인 컨텍스트 로드:
  - 이 디렉토리: 0 tokens (Subagent만 존재)
  - Commands: ~300 tokens (선택적)

Subagent 실행:
  - 독립 컨텍스트 (Task tool)
  - RLM으로 대량 파일 처리
  - Hook으로 자동 상태 관리

총 절약: ~850 tokens vs 기존 Skill 방식
```

## 참조

- Commands: `.claude/commands/thesis/autopilot.md` (선택적)
- RLM Scripts: `.claude/skills/thesis-orchestrator/scripts/rlm_processor.py`
- Hooks: `.claude/hooks/post-tool-use/thesis-workflow-automation.py`
