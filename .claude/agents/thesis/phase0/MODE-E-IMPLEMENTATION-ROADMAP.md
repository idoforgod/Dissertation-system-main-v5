# Mode E 최적화 구현 로드맵

**작성일**: 2026-01-28
**목표**: 5일 이내 Mode E를 Master-Subagent 아키텍처로 리팩토링

---

## 📅 5-Day Implementation Plan

### Day 1: Master Orchestrator 구현

#### 오전 (3시간)
```bash
# 1. Master agent 생성
mkdir -p .claude/agents/thesis/phase0
touch .claude/agents/thesis/phase0/paper-research-orchestrator.md

# 2. Orchestrator 로직 작성
# - Stage 순서 제어
# - Subagent 호출 로직
# - 오류 처리
```

**Deliverable**: `paper-research-orchestrator.md` (완성)

#### 오후 (3시간)
```bash
# 3. 기존 커맨드 업데이트
# - start-paper-upload.md를 orchestrator로 연결

# 4. 기본 테스트
# - 샘플 입력으로 orchestrator 동작 확인
```

**Deliverable**: `start-paper-upload.md` (업데이트)

---

### Day 2: Subagents 생성 (Stage 1-3)

#### 오전 (3시간)
```bash
# Subagent 디렉토리 생성
mkdir -p .claude/agents/thesis/phase0/subagents

# Subagent 1: paper-analyzer
touch .claude/agents/thesis/phase0/subagents/paper-analyzer.md

# Subagent 2: gap-identifier
touch .claude/agents/thesis/phase0/subagents/gap-identifier.md

# Subagent 3: hypothesis-generator
touch .claude/agents/thesis/phase0/subagents/hypothesis-generator.md
```

**각 subagent 작성 시간**: 약 50분
- 역할 정의: 10분
- 입출력 스키마: 10분
- 프로세스 로직: 20분
- 품질 기준: 10분

#### 오후 (3시간)
```bash
# 통합 테스트
# - orchestrator에서 Stage 1-3 subagent 호출
# - 출력물 검증
```

**Deliverable**: Subagents 1-3 (완성 + 테스트)

---

### Day 3: Subagents 생성 (Stage 4-6)

#### 오전 (3시간)
```bash
# Subagent 4: design-proposer
touch .claude/agents/thesis/phase0/subagents/design-proposer.md

# Subagent 5: feasibility-assessor
touch .claude/agents/thesis/phase0/subagents/feasibility-assessor.md

# Subagent 6: proposal-integrator
touch .claude/agents/thesis/phase0/subagents/proposal-integrator.md
```

#### 오후 (3시간)
```bash
# End-to-end 테스트
# - 전체 워크플로우 (Stage 1-6) 실행
# - 샘플 논문으로 검증
```

**Deliverable**: Subagents 4-6 (완성) + 전체 워크플로우 동작 확인

---

### Day 4: Skills 및 개별 Commands

#### 오전 (3시간)
```bash
# Skills 생성 (4개)
mkdir -p .claude/skills/{paper-analysis,hypothesis-development,research-design-templates,validation-checks}

# Skill 1: paper-analysis
# - SKILL.md
# - scripts/parse_pdf.py (선택 사항)

# Skill 2: hypothesis-development
# - SKILL.md
# - templates/*.yaml

# Skill 3: research-design-templates
# - SKILL.md
# - templates/*.yaml

# Skill 4: validation-checks
# - SKILL.md
# - scripts/check_gra.py (선택 사항)
```

#### 오후 (3시간)
```bash
# 개별 Stage Commands 생성 (7개)
touch .claude/commands/thesis/analyze-paper.md
touch .claude/commands/thesis/identify-gaps.md
touch .claude/commands/thesis/generate-hypotheses.md
touch .claude/commands/thesis/propose-design.md
touch .claude/commands/thesis/assess-feasibility.md
touch .claude/commands/thesis/integrate-proposal.md
touch .claude/commands/thesis/review-proposal.md
```

**Deliverable**: Skills (4개) + Commands (7개)

---

### Day 5: Hooks 및 최종 테스트

#### 오전 (2시간)
```bash
# Hooks 생성 (3개)
mkdir -p .claude/hooks/thesis
touch .claude/hooks/thesis/pre-stage.sh
touch .claude/hooks/thesis/post-stage.sh
touch .claude/hooks/thesis/hitl-checkpoint.sh

# .claude.json 업데이트
# - hook 등록
```

#### 오후 (4시간)
```bash
# 종합 테스트
# 1. 전체 워크플로우 테스트
/thesis:start paper-upload --paper-path test/sample-paper.pdf

# 2. 개별 Stage 테스트
/thesis:analyze-paper --input test/sample-paper.pdf
/thesis:identify-gaps --input test/analysis-output.md

# 3. Hook 동작 확인
# - pre-stage validation
# - post-stage validation
# - hitl checkpoint

# 4. 문서화
# - README 업데이트
# - 사용 가이드 작성
```

**Deliverable**: 완전히 동작하는 Mode E 시스템 + 문서

---

## 🎯 구현 우선순위 매트릭스

| 컴포넌트 | 우선순위 | 소요 시간 | 의존성 | 완료 체크 |
|---------|---------|---------|--------|----------|
| Master Orchestrator | P0 | 6h | None | ⬜ |
| Subagent 1-3 | P0 | 6h | Orchestrator | ⬜ |
| Subagent 4-6 | P0 | 6h | Orchestrator | ⬜ |
| start-paper-upload (업데이트) | P0 | 1h | Orchestrator | ⬜ |
| Skills (기본) | P1 | 4h | None | ⬜ |
| Commands (개별 Stage) | P1 | 3h | Subagents | ⬜ |
| Hooks (기본) | P2 | 2h | None | ⬜ |
| 고급 기능 (병렬 실행) | P2 | 4h | All | ⬜ |
| 성능 최적화 | P3 | 4h | All | ⬜ |

**Legend**:
- P0 = Critical (필수)
- P1 = Important (중요)
- P2 = Nice-to-have (있으면 좋음)
- P3 = Future (나중에)

---

## 📝 구현 체크리스트

### Phase 1: Core Architecture (Day 1-3)

#### Master Orchestrator
- [ ] `paper-research-orchestrator.md` 생성
- [ ] Stage 순서 제어 로직
- [ ] Subagent 호출 로직 (Task tool)
- [ ] 오류 처리 및 재시도
- [ ] HITL checkpoint 통합
- [ ] 진행 상황 로깅

#### Subagents (6개)
- [ ] `paper-analyzer.md` (Stage 1)
  - [ ] 입출력 스키마 정의
  - [ ] 분석 프레임워크 구현
  - [ ] GRA 준수
- [ ] `gap-identifier.md` (Stage 2)
  - [ ] 5가지 갭 유형 식별
  - [ ] 갭 타당성 검증
- [ ] `hypothesis-generator.md` (Stage 3)
  - [ ] 가설 구조 정의
  - [ ] 품질 기준 적용
- [ ] `design-proposer.md` (Stage 4)
  - [ ] 양적/질적/혼합 설계
  - [ ] 템플릿 활용
- [ ] `feasibility-assessor.md` (Stage 5)
  - [ ] 자원 요구사항 평가
  - [ ] 윤리 고려사항 검토
- [ ] `proposal-integrator.md` (Stage 6)
  - [ ] 모든 출력물 통합
  - [ ] 최종 제안서 생성

#### Command 업데이트
- [ ] `start-paper-upload.md` 업데이트
  - [ ] Orchestrator 호출로 변경
  - [ ] 기존 동작 유지

---

### Phase 2: Skills & Commands (Day 4)

#### Skills (4개)
- [ ] `paper-analysis`
  - [ ] SKILL.md 작성
  - [ ] PDF 파싱 로직 (선택)
  - [ ] 템플릿 제공
- [ ] `hypothesis-development`
  - [ ] SKILL.md 작성
  - [ ] 가설 템플릿 (인과/조절/매개)
  - [ ] 품질 평가 기준
- [ ] `research-design-templates`
  - [ ] SKILL.md 작성
  - [ ] 양적/질적/혼합 템플릿
- [ ] `validation-checks`
  - [ ] SKILL.md 작성
  - [ ] GRA 검증 스크립트 (선택)
  - [ ] pTCS 계산 스크립트 (선택)

#### Commands (7개)
- [ ] `analyze-paper.md`
- [ ] `identify-gaps.md`
- [ ] `generate-hypotheses.md`
- [ ] `propose-design.md`
- [ ] `assess-feasibility.md`
- [ ] `integrate-proposal.md`
- [ ] `review-proposal.md`

---

### Phase 3: Automation & Testing (Day 5)

#### Hooks (3개)
- [ ] `pre-stage.sh`
  - [ ] 입력 파일 검증
  - [ ] 파일 크기 확인
- [ ] `post-stage.sh`
  - [ ] GRA 준수 검증
  - [ ] pTCS 점수 계산
- [ ] `hitl-checkpoint.sh`
  - [ ] 사용자 알림
  - [ ] 승인 대기

#### 테스트
- [ ] Unit tests (개별 subagent)
  - [ ] Mock 입력으로 각 subagent 테스트
- [ ] Integration tests (워크플로우)
  - [ ] 샘플 논문으로 전체 워크플로우 실행
- [ ] End-to-end tests
  - [ ] 실제 사용 시나리오 테스트

#### 문서화
- [ ] README 업데이트
- [ ] 사용 가이드 작성
- [ ] 예제 및 튜토리얼

---

## 🚀 Quick Start (Day 1 구현)

### Step 1: Master Orchestrator 생성

```bash
# 파일 생성
touch .claude/agents/thesis/phase0/paper-research-orchestrator.md
```

**파일 내용 (최소 버전)**:
```yaml
---
name: paper-research-orchestrator
description: 논문 기반 연구 설계 워크플로우 총괄 오케스트레이터
tools: Task(*), Read(*), Write(*), Bash(*)
model: sonnet
---

# Paper Research Orchestrator

논문 기반 연구 설계의 전체 워크플로우를 조율합니다.

## 역할

**Master Coordinator**:
- Stage 1-6 순차 실행
- Subagent 호출 및 결과 수집
- 오류 처리 및 재시도
- HITL checkpoint 관리

## 실행 프로세스

### 입력
- `paper_path`: 업로드된 논문 파일 경로

### 워크플로우

**Stage 1: 논문 심층 분석**
```
Task: paper-analyzer
Input: {paper_path}
Output: paper-deep-analysis.md
Duration: 10-15분
```

**Stage 2: 전략적 갭 식별**
```
Task: gap-identifier
Input: paper-deep-analysis.md
Output: strategic-gap-analysis.md
Duration: 8-12분
```

**Stage 3: 가설 도출**
```
Task: hypothesis-generator
Input: strategic-gap-analysis.md
Output: novel-hypotheses.md
Duration: 15-20분
```

**Stage 4: 연구 설계 제안**
```
Task: design-proposer
Input: novel-hypotheses.md
Output: research-design-proposal.md
Duration: 20-30분
```

**Stage 5: 실행가능성 평가**
```
Task: feasibility-assessor
Input: research-design-proposal.md
Output: feasibility-ethics-report.md
Duration: 5-8분
```

**Stage 6: 통합 제안서 생성**
```
Task: proposal-integrator
Input: [all previous outputs]
Output: integrated-research-proposal.md
Duration: 5-10분
```

**HITL-1 Checkpoint**
```
사용자 검토 및 승인 대기
```

### 오류 처리

각 Stage에서 오류 발생 시:
1. 로그 기록
2. 재시도 (최대 2회)
3. 재시도 실패 시 사용자에게 알림

### 출력

**성공 시**:
- `integrated-research-proposal.md` (최종 제안서)
- `integrated-research-proposal.docx` (Word export)

**실패 시**:
- 오류 로그 및 복구 가이드
```

---

### Step 2: 첫 번째 Subagent 생성 (paper-analyzer)

```bash
# 디렉토리 생성
mkdir -p .claude/agents/thesis/phase0/subagents

# 파일 생성
touch .claude/agents/thesis/phase0/subagents/paper-analyzer.md
```

**파일 내용 (최소 버전)**:
```yaml
---
name: paper-analyzer
description: 선행연구 논문 심층 분석 전문가 (Stage 1)
tools: Read(*), Write(*), WebSearch(*), Skill(scientific-skills:peer-review)
model: opus
---

# Paper Analyzer

업로드된 논문을 박사급 수준으로 분석합니다.

## 입력
- `paper_path`: 논문 파일 경로 (PDF, DOCX, TXT)

## 출력
- `paper-deep-analysis.md` (5-7 pages)

## 분석 프레임워크

### 1. Research Context
- 핵심 연구질문
- 이론적 프레임워크
- 연구 패러다임

### 2. Methodology Evaluation
- 연구 설계 유형
- 표본 특성 및 크기
- 자료수집 방법
- 분석 기법
- 타당도 평가

### 3. Findings Synthesis
- 핵심 발견사항
- 효과 크기
- 통계적 유의성
- 실무적 의의

### 4. Critical Evaluation
- 이론적 기여도
- 방법론적 강점
- 방법론적 약점
- 저자 명시 한계점
- 미명시 한계점 (비판적 발견)

## 품질 기준

- ✅ GRA Compliance: 모든 주장에 페이지 번호 인용
- ✅ Hallucination Firewall: "완벽", "모든" 같은 표현 금지
- ✅ pTCS Target: Claim-level 70+

## 실행 예시

**입력**: `user-resource/paper.pdf`

**출력 구조**:
```markdown
# Deep Analysis: [Paper Title]

## 1. Research Context
[분석 내용...]

## 2. Methodology Evaluation
[분석 내용...]

## 3. Findings Synthesis
[분석 내용...]

## 4. Critical Evaluation
[분석 내용...]

## References
- [Original paper citation]
- [Supporting literature...]
```
```

---

### Step 3: 커맨드 업데이트

```bash
# 기존 커맨드 파일 수정
vim .claude/commands/thesis/start-paper-upload.md
```

**변경 사항**:
```yaml
# BEFORE
agent: paper-research-designer

# AFTER
agent: paper-research-orchestrator
```

---

### Step 4: 기본 테스트

```bash
# 1. 샘플 논문 준비
mkdir -p test
cp ~/sample-paper.pdf test/

# 2. 워크플로우 실행
/thesis:start paper-upload --paper-path test/sample-paper.pdf

# 3. 결과 확인
# - paper-deep-analysis.md 생성되었는가?
# - 내용이 5-7 pages인가?
# - GRA 준수하는가?
```

---

## 📊 진행 상황 트래킹

### Week 1 (Day 1-5)

| Day | 작업 | 예상 시간 | 완료 | 비고 |
|-----|------|----------|------|------|
| 1 | Master Orchestrator | 6h | ⬜ | |
| 2 | Subagents 1-3 | 6h | ⬜ | |
| 3 | Subagents 4-6 + E2E 테스트 | 6h | ⬜ | |
| 4 | Skills + Commands | 6h | ⬜ | |
| 5 | Hooks + 최종 테스트 | 6h | ⬜ | |

**총 예상 시간**: 30시간 (5일 x 6시간/일)

---

## 🎓 학습 가이드

### 새로운 개념

#### Master-Subagent Pattern
```
Master (Orchestrator)
  ├─ 워크플로우 제어
  ├─ Subagent 호출
  └─ 결과 통합

Subagent (Specialist)
  ├─ 단일 책임
  ├─ 독립 실행 가능
  └─ 재사용 가능
```

#### Skills vs Agents
```
Skill:
  - 재사용 가능한 로직
  - 도구 집합 (templates, scripts)
  - 여러 agent가 공유

Agent:
  - 특정 태스크 전문가
  - 독립적으로 실행
  - Skills 활용 가능
```

#### Hooks
```
Hook:
  - 자동화된 검증
  - Tool 사용 전/후 실행
  - 오류 조기 발견
```

---

## 🔧 트러블슈팅

### 자주 발생하는 문제

#### 1. Subagent를 찾을 수 없음
```bash
Error: subagent 'paper-analyzer' not found

Solution:
1. 파일 경로 확인: .claude/agents/thesis/phase0/subagents/paper-analyzer.md
2. Frontmatter에 name 필드 확인
3. Agent 등록 확인
```

#### 2. Stage 출력물이 생성되지 않음
```bash
Error: Output file not found

Solution:
1. Subagent가 Write tool 접근 권한 있는지 확인
2. Output 경로가 올바른지 확인
3. Subagent 로그 확인
```

#### 3. Hook 실행 실패
```bash
Error: pre-stage hook failed

Solution:
1. Hook 스크립트 실행 권한 확인: chmod +x .claude/hooks/thesis/pre-stage.sh
2. 스크립트 문법 오류 확인
3. Hook 등록 확인: .claude.json
```

---

## 📚 참고 자료

### 내부 문서
- [MODE-E-OPTIMIZATION-DESIGN.md](./MODE-E-OPTIMIZATION-DESIGN.md) - 상세 설계
- [GRA Architecture](./../../../skills/thesis-orchestrator/references/gra-architecture.md) - GRA 준수 가이드

### 외부 자료
- Claude Code Agent 문서
- Task Tool 사용법
- Skill 개발 가이드

---

## ✅ 완료 기준

### Definition of Done

각 단계가 완료되었다고 판단하는 기준:

#### Master Orchestrator
- [ ] 6개 Stage 순차 실행 가능
- [ ] 오류 처리 로직 동작
- [ ] 로그 기록 정상

#### Subagents
- [ ] 독립 실행 가능
- [ ] 입출력 스키마 준수
- [ ] GRA Compliance

#### Commands
- [ ] 전체 워크플로우 실행 가능
- [ ] 개별 Stage 실행 가능
- [ ] HITL checkpoint 동작

#### Skills
- [ ] 재사용 가능
- [ ] 문서화 완료
- [ ] 예제 제공

#### Hooks
- [ ] 자동 검증 동작
- [ ] 오류 시 Block
- [ ] 로그 기록

#### 전체 시스템
- [ ] 샘플 논문으로 E2E 테스트 성공
- [ ] 기존 동작과 호환
- [ ] 성능 개선 확인 (시간/비용)

---

**작성자**: Claude Code
**업데이트**: 2026-01-28
**상태**: ⬜ 준비 | ⬜ 진행 중 | ⬜ 완료
