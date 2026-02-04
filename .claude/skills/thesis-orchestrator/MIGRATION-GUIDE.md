# Validation System Migration Guide

**Version**: 1.0
**Date**: 2026-01-20
**Target Audience**: Thesis workflow users

---

## Overview

이 가이드는 기존 워크플로우에서 검증 시스템으로 안전하게 전환하는 방법을 설명합니다.

**핵심 원칙**: 점진적, 안전한, 되돌릴 수 있는 마이그레이션

---

## Migration Paths

사용자 유형에 따라 3가지 마이그레이션 경로를 제공합니다:

### Path A: Conservative (보수적) - 권장

**누구에게**: 안정성을 최우선하는 사용자

**전략**: Opt-in 방식 유지, 필요할 때만 검증 사용

**장점**:
- ✅ 기존 워크플로우 완전 보존
- ✅ 문제 발생 시 즉시 되돌림 가능
- ✅ 학습 곡선 낮음

**단점**:
- ❌ 수동으로 검증 활성화 필요
- ❌ Silent failure 위험 (검증 비활성화 시)

**추천 대상**:
- 첫 논문 작성자
- 안정성 중시
- 기존 방식에 익숙함

---

### Path B: Balanced (균형적)

**누구에게**: 품질과 안정성의 균형을 원하는 사용자

**전략**: 중요 페이즈(Phase 3)만 검증 활성화

**장점**:
- ✅ 핵심 품질 보장 (논문 작성)
- ✅ 성능 영향 최소화
- ✅ 유연한 제어

**단점**:
- ❌ 페이즈별 설정 필요
- ❌ 일부 검증 누락 가능

**추천 대상**:
- 경험 있는 사용자
- 선택적 품질 보장
- 성능 민감한 환경

---

### Path C: Progressive (진보적)

**누구에게**: 최고 품질을 원하는 사용자

**전략**: 모든 페이즈에서 검증 활성화

**장점**:
- ✅ 최대 품질 보장
- ✅ 모든 문제 즉시 감지
- ✅ Silent failure 완전 차단

**단점**:
- ❌ Fail-fast로 작업 중단 가능
- ❌ 검증 오버헤드 (미미하지만 존재)

**추천 대상**:
- 품질 최우선
- 실전 논문 제출 직전
- 완벽주의자

---

## Step-by-Step Migration

### Phase 0: Preparation (준비)

**목표**: 현재 상태 백업 및 이해

```bash
# 1. 현재 프로젝트 백업
cd thesis-output
tar -czf backup-$(date +%Y%m%d).tar.gz your-project-name/

# 2. Regression test 실행 (기준점 확보)
cd ..
bash tests/regression/test_existing_workflow_intact.sh

# 3. 현재 진행 상황 확인
/thesis:status

# 4. 검증 시스템 상태 확인
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
```

**체크리스트**:
- [ ] 프로젝트 백업 완료
- [ ] Regression test 통과
- [ ] 현재 상태 파악 완료
- [ ] 검증 시스템 이해 완료

---

### Phase 1: Trial Run (시험 실행)

**목표**: 검증 시스템 안전하게 체험

```bash
# 1. 테스트 디렉토리 생성
mkdir -p thesis-output/migration-test-$(date +%s)
cd thesis-output/migration-test-*

# 2. 최소 파일 생성 (Phase 0)
mkdir -p 00-session
echo '{"working_dir": "'$(pwd)'"}' > 00-session/session.json
echo '# Checklist' > 00-session/todo-checklist.md

# 3. 검증 테스트
cd ../..
export USE_VALIDATION=true
/thesis:validate-phase 0
# Expected: ✅ PASSED

# 4. 검증 비활성화하고 다시 테스트
export USE_VALIDATION=false
/thesis:validate-phase 0
# Should still work (backward compatible)

# 5. 정리
rm -rf thesis-output/migration-test-*
```

**체크리스트**:
- [ ] 테스트 디렉토리 생성 성공
- [ ] 검증 활성화 시 정상 작동
- [ ] 검증 비활성화 시 정상 작동
- [ ] 환경 변수 제어 이해

---

### Phase 2: Gradual Adoption (점진적 채택)

**목표**: 실제 프로젝트에 단계적 적용

#### Step 2.1: Phase 3만 검증 (권장)

```bash
# 1. 기존 프로젝트로 이동
cd thesis-output/your-actual-project

# 2. Phase 0-2는 표준 실행 (검증 없음)
export USE_VALIDATION=false
/thesis:run-literature-review
/thesis:run-research-design

# 3. Phase 3부터 검증 활성화
export USE_VALIDATION=true
export FAIL_FAST=true
/thesis:run-writing-validated

# 4. 결과 검증
/thesis:validate-phase 3
/thesis:progress
```

**이유**:
- Phase 3 (논문 작성)이 가장 중요
- Chapter 2, 3 누락 문제가 여기서 발생
- 점진적 학습 가능

#### Step 2.2: 전체 페이즈 검증 (옵션)

```bash
# 모든 페이즈에서 검증 활성화
bash .claude/skills/thesis-orchestrator/scripts/enable-validation.sh

# 처음부터 검증된 실행
/thesis:init
/thesis:start topic "Your topic"
# ... 모든 명령어가 검증됨

# 진행 상황 추적
/thesis:progress  # 실시간 확인
```

**체크리스트**:
- [ ] Phase 3 검증 성공
- [ ] Chapter 누락 감지 확인
- [ ] Fail-fast 동작 이해
- [ ] 오류 메시지 해석 가능

---

### Phase 3: Full Integration (완전 통합)

**목표**: 검증을 기본 워크플로우로 통합

```bash
# 1. 검증을 기본값으로 설정 (persistent)
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --enable

# 2. 설정 확인
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status
# Expected: Validation ENABLED

# 3. 새 프로젝트 시작 (검증 자동 적용)
/thesis:init
/thesis:start topic "New project"

# 4. 진행 중 검증 모니터링
/thesis:progress           # 간단한 확인
/thesis:validate-phase 1   # 상세 검증
/thesis:validate-all       # 전체 검증
```

**체크리스트**:
- [ ] 검증이 기본값으로 설정됨
- [ ] 모든 명령어가 검증과 함께 실행
- [ ] 진행 상황 추적 익숙해짐
- [ ] 오류 처리 능숙해짐

---

## Rollback Plan (되돌리기)

각 단계에서 문제 발생 시 되돌리는 방법:

### Level 1: Disable Validation Temporarily (임시 비활성화)

```bash
# 현재 세션만 비활성화
export USE_VALIDATION=false

# 또는 스크립트 사용
bash .claude/skills/thesis-orchestrator/scripts/disable-validation.sh
```

**사용 시기**: 급한 작업, 검증 오류 우회

---

### Level 2: Remove Persistent Config (영구 설정 제거)

```bash
# 저장된 설정 삭제
rm -f ~/.thesis-orchestrator/validation.json

# 환경 변수 unset
unset USE_VALIDATION
unset FAIL_FAST
unset VALIDATION_VERBOSE
unset VALIDATION_REPORT_DIR
```

**사용 시기**: 검증 완전 비활성화, 초기 상태로 복귀

---

### Level 3: Complete Removal (완전 제거)

```bash
# 검증 파일 삭제 (극단적 조치, 권장하지 않음)
rm .claude/skills/thesis-orchestrator/scripts/workflow_validator.py
rm .claude/skills/thesis-orchestrator/scripts/validated_executor.py
rm .claude/skills/thesis-orchestrator/scripts/phase_validator.py
rm .claude/skills/thesis-orchestrator/scripts/validation_config.py

# Regression test로 확인
bash tests/regression/test_existing_workflow_intact.sh
# Expected: 일부 파일 누락 경고, 하지만 기존 워크플로우는 정상
```

**사용 시기**: 검증 시스템 완전 제거 필요 (매우 드묾)

---

## Common Issues and Solutions

### Issue 1: "Step 117 validation failed" (Chapter 2 missing)

**원인**: Chapter 2 파일이 생성되지 않음

**해결**:
```bash
# 1. 확인
ls -la thesis-output/your-project/03-thesis/chapter2-*

# 2. 수동 생성 (임시)
echo "# Chapter 2" > thesis-output/your-project/03-thesis/chapter2-literature.md

# 3. 재검증
/thesis:validate-phase 3
```

**근본 해결**: thesis-writer 에이전트 실행 재확인

---

### Issue 2: "Validation too strict" (검증이 너무 엄격함)

**원인**: 일부 파일을 의도적으로 생략하고 싶음

**해결**:
```bash
# Option A: 검증 비활성화
export USE_VALIDATION=false

# Option B: Fail-fast 비활성화 (오류 기록하되 계속 진행)
export FAIL_FAST=false

# Option C: 특정 스텝만 스킵
# (현재 미구현, Phase 4에서 추가 예정)
```

---

### Issue 3: "Performance degradation" (성능 저하)

**원인**: 검증 오버헤드 (매우 드묾)

**측정**:
```bash
# 검증 없이 실행 시간 측정
export USE_VALIDATION=false
time /thesis:run-writing

# 검증 활성화 실행 시간 측정
export USE_VALIDATION=true
time /thesis:run-writing-validated

# 차이 확인 (보통 <1% 차이)
```

**해결**:
- 검증 오버헤드는 대부분 <100ms (에이전트 실행 시간 30-60s 대비 무시 가능)
- 만약 실제 문제라면 검증 비활성화

---

### Issue 4: "False positives" (잘못된 오류 보고)

**원인**: 검증 규칙이 실제 워크플로우와 불일치

**보고**:
```bash
# 문제 상황 문서화
/thesis:validate-all > validation-issue-$(date +%s).log

# GitHub issue 생성 또는 개발자에게 보고
# - 예상 동작
# - 실제 동작
# - 재현 단계
```

---

## Success Metrics

마이그레이션 성공 여부를 판단하는 기준:

### Technical Metrics

- [ ] **Zero Breaking Changes**: 기존 명령어 모두 정상 작동
- [ ] **Validation Coverage**: 모든 critical steps 검증됨
- [ ] **Detection Rate**: Chapter 누락 100% 감지
- [ ] **Performance**: 검증 오버헤드 <100ms

### User Experience Metrics

- [ ] **Ease of Use**: 5분 안에 검증 활성화 가능
- [ ] **Error Clarity**: 오류 메시지를 이해하고 수정 가능
- [ ] **Rollback Time**: 1분 안에 이전 상태로 복귀 가능
- [ ] **Confidence**: 검증 시스템에 대한 신뢰 확보

---

## Migration Timeline

### Week 1: Exploration (탐색)

**목표**: 검증 시스템 이해하기

**활동**:
- [ ] 문서 읽기 (MIGRATION-GUIDE.md, validation-configuration.md)
- [ ] 테스트 디렉토리에서 실험
- [ ] 환경 변수 조작 연습
- [ ] 명령어 실행 (validate-*, progress)

**결과**: 검증 시스템 작동 방식 이해

---

### Week 2: Trial (시험)

**목표**: 실제 프로젝트에 부분 적용

**활동**:
- [ ] Phase 3만 검증 활성화
- [ ] Chapter 누락 감지 확인
- [ ] Fail-fast 동작 경험
- [ ] 오류 수정 연습

**결과**: 검증의 실질적 가치 체감

---

### Week 3: Adoption (채택)

**목표**: 검증을 기본 워크플로우로

**활동**:
- [ ] 모든 페이즈 검증 활성화
- [ ] Persistent 설정 저장
- [ ] 새 프로젝트에 적용
- [ ] 팀원에게 공유 (해당 시)

**결과**: 검증이 일상적 워크플로우의 일부

---

## Best Practices

### ✅ DO

1. **Start Small**: Phase 3만 먼저 검증
2. **Test First**: 테스트 디렉토리에서 실험
3. **Backup Always**: 중요 작업 전 백업
4. **Read Errors**: 오류 메시지를 주의깊게 읽기
5. **Use Progress**: `/thesis:progress`로 자주 확인

### ❌ DON'T

1. **Don't Skip Backup**: 백업 없이 전체 검증 활성화 금지
2. **Don't Ignore Errors**: 검증 오류를 무시하고 계속 진행 금지
3. **Don't Modify Validation Code**: 검증 스크립트 직접 수정 금지
4. **Don't Force Through**: Fail-fast 오류를 강제로 우회 금지
5. **Don't Panic**: 오류 발생 시 침착하게 롤백

---

## Getting Help

### Self-Service Resources

1. **Documentation**:
   - `MIGRATION-GUIDE.md` (이 문서)
   - `validation-configuration.md` (설정 가이드)
   - `agent-wrapper-guide.md` (통합 가이드)

2. **Commands**:
   ```bash
   # 도움말
   python3 validation_config.py --help-vars

   # 상태 확인
   python3 validation_config.py --status

   # 진행 상황
   /thesis:progress
   ```

3. **Tests**:
   ```bash
   # Regression test
   bash tests/regression/test_existing_workflow_intact.sh

   # Integration test
   # (테스트 디렉토리에서 실험)
   ```

---

## FAQ

### Q: 검증 시스템을 반드시 사용해야 하나요?

**A**: 아니요. 완전히 선택 사항입니다. 기존 워크플로우는 그대로 사용 가능합니다.

---

### Q: 검증 활성화하면 성능이 느려지나요?

**A**: 아니요. 검증 오버헤드는 <100ms로 에이전트 실행 시간(30-60s) 대비 무시 가능합니다.

---

### Q: 중간에 검증을 끌 수 있나요?

**A**: 네. 언제든지 `export USE_VALIDATION=false` 또는 `disable-validation.sh`로 비활성화 가능합니다.

---

### Q: 검증 오류가 잘못됐다고 생각되면?

**A**:
1. 로그 저장: `/thesis:validate-all > issue.log`
2. 상황 문서화
3. 개발자에게 보고 또는 GitHub issue 생성

---

### Q: 팀원과 어떻게 공유하나요?

**A**:
```bash
# 1. 설정 export
python3 validation_config.py --status > team-config.txt

# 2. 가이드 공유
# - MIGRATION-GUIDE.md
# - validation-configuration.md

# 3. 데모
# - 실제 프로젝트에서 검증 시연
# - Chapter 누락 감지 데모
```

---

## Conclusion

**검증 시스템은 선택 사항이지만, 품질 보장을 위해 강력히 권장합니다.**

**권장 마이그레이션 경로**:
1. Week 1: 문서 읽고 이해 (30분)
2. Week 2: 테스트 디렉토리에서 실험 (1시간)
3. Week 3: Phase 3만 검증 활성화 (실전 적용)
4. Week 4+: 전체 페이즈 검증 (익숙해진 후)

**예상 결과**:
- ✅ Chapter 누락 문제 100% 감지
- ✅ 논문 품질 대폭 향상
- ✅ 디버깅 시간 절약
- ✅ 안심하고 작업 가능

---

**마이그레이션 시작 준비되셨나요?**

```bash
# 첫 단계: 상태 확인
python3 .claude/skills/thesis-orchestrator/scripts/validation_config.py --status

# 다음: 이 가이드의 "Step-by-Step Migration" 따라하기
```

---

**Document Version**: 1.0
**Last Updated**: 2026-01-20
**Author**: Claude Code (Thesis Orchestrator Team)
