# Dissertation Research Workflow System v5

AI 기반 박사논문 연구 워크플로우 시뮬레이션 시스템

> 연구 아이디어 입력 → 150페이지 완성 논문 출력

## 개요

본 시스템은 박사논문 연구의 전 과정을 시뮬레이션하는 AI 워크플로우 시스템입니다. 연구 주제 탐색부터 문헌검토, 연구설계, 논문 작성, 학술지 투고 전략까지 전 과정을 61개의 전문 AI 에이전트가 수행합니다.

## 주요 기능

- **7가지 입력 모드**: 연구 주제, 연구질문, 논문 업로드, 프로포절 업로드, 자유입력 등
- **4단계 연구 파이프라인**: 초기화 → 문헌검토 → 연구설계 → 논문작성
- **3가지 연구 유형 지원**: 양적연구, 질적연구, 혼합연구
- **GRA 아키텍처**: 3중 품질보증 시스템으로 학술적 환각(hallucination) 방지
- **시뮬레이션 모드**: Quick(20-30쪽) / Full(150쪽+) 선택 가능
- **Autopilot 모드**: 불확실성 기반 자동/수동 전환
- **이중 언어 출력**: 영어 연구 + 한국어 번역

## 시스템 구성

| 구성 요소         | 수량 | 설명                                          |
| ----------------- | ---- | --------------------------------------------- |
| AI 에이전트       | 61개 | 문헌검색, 가설생성, 연구설계 등 전문 에이전트 |
| 인터랙티브 커맨드 | 46개 | 워크플로우 제어 슬래시 커맨드                 |
| 핵심 스크립트     | 52개 | 검증, 게이트 관리, 품질 평가 등               |
| 품질 게이트       | 4개  | Wave/Phase 간 교차 검증                       |

## 빠른 시작

### 사전 요구사항

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) 설치
- Python 3.10+
- Node.js 18+

### 실행

```bash
# 프로젝트 디렉토리 진입
cd Dissertation-system-main-v4

# 의존성 설치
pip install -e ".[dev]"
npm install

# Claude Code에서 워크플로우 시작
# 방법 1: 슬래시 커맨드
/thesis:start

# 방법 2: 빠른 시작
/thesis:quick-start

# 방법 3: 논문 업로드 기반
/thesis:start-paper-upload

# 방법 4: 프로포절 업로드 기반
/thesis:start-proposal-upload
```

## 워크플로우 구조

```
Phase 0: 초기화
  └─ 입력 모드 선택 (A~G) → 연구유형 설정

Phase 1: 문헌검토 (5 Waves)
  ├─ Wave 1: 문헌검색 · 핵심문헌 · 트렌드 · 방법론 스캔
  ├─ Wave 2: 이론적 프레임워크 · 실증분석 · 갭 식별 · 변수관계
  ├─ Wave 3: 비판적 검토 · 방법론 비평 · 한계점 · 미래방향
  ├─ Wave 4: 종합 · 개념모델 구축
  └─ Wave 5: 표절검사 · SRCS 평가 · 최종 종합

Phase 2: 연구설계
  ├─ 양적연구: 가설개발 → 연구모델 → 표본설계 → 통계계획
  ├─ 질적연구: 패러다임 → 참여자선정 → 자료수집 → 분석전략
  └─ 혼합연구: 설계유형 → 양적+질적 → 통합전략

Phase 3: 논문작성
  └─ 아웃라인 설계 → 챕터별 집필 → 품질검토

Phase 4: 출판전략
  └─ 학술지 선정 → 원고 포맷팅
```

## 품질 보증

- **GRA (Grounded Research Architecture)**: 3중 환각 방지 아키텍처
- **pTCS (Predictive Thesis Completion Score)**: 논문 완성도 예측 점수
- **SRCS (Systematic Reasoning & Claim Scoring)**: 체계적 추론 및 주장 점수
- **교차 검증 게이트**: 각 Phase 완료 시 자동 품질 검증

## 기술 스택

- **AI 프레임워크**: Claude Code CLI (Agents, Skills, Commands)
- **백엔드**: Python 3.10+, Node.js
- **품질 관리**: Ruff, pre-commit hooks, pytest
- **CI/CD**: GitHub Actions

## 프로젝트 구조

```
.claude/
  ├─ agents/thesis/      # 61개 전문 AI 에이전트
  ├─ commands/thesis/     # 46개 인터랙티브 커맨드
  ├─ skills/              # 핵심 스킬 및 오케스트레이터
  └─ hooks/               # 사전/사후 검증 훅
prompt/                   # 워크플로우 설계 문서
tests/                    # 단위/통합/E2E 테스트
user-resource/            # 사용자 업로드 자료
thesis-output/            # 생성된 논문 출력물
```

## 상세 매뉴얼

자세한 사용법은 [USER_MANUAL.md](./USER_MANUAL.md)를 참조하세요.

## 저작권

Copyright (c) 2025-2026 최윤식 (Yoonsik, Choi). All rights reserved.

자세한 내용은 [copyright.md](./copyright.md)를 참조하세요.
