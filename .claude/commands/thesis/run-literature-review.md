---
description: 문헌검토 파이프라인 실행. Wave 1-5를 순차적으로 실행하여 문헌검토를 완료합니다.
context: fork
agent: general-purpose
---

# 문헌검토 파이프라인 실행

## 역할

이 커맨드는 **Phase 1 (Literature Review) 전체 파이프라인**을 순차적으로 실행합니다.

## 전제 조건

- `/thesis:init` 완료
- `/thesis:start` 완료 (모드 선택)
- HITL-1 (연구주제 확정) 완료

## 실행 순서

### Wave 1: 문헌 탐색 (4 agents)
```
1. @literature-searcher → 01-literature-search-strategy.md
2. @seminal-works-analyst → 02-seminal-works-analysis.md
3. @trend-analyst → 03-research-trend-analysis.md
4. @methodology-scanner → 04-methodology-scan.md
```
→ Cross-Validation Gate 1

### Wave 2: 심층 분석 (4 agents)
```
5. @theoretical-framework-analyst → 05-theoretical-framework.md
6. @empirical-evidence-analyst → 06-empirical-evidence-synthesis.md
7. @gap-identifier → 07-research-gap-analysis.md
8. @variable-relationship-analyst → 08-variable-relationship-analysis.md
```
→ Cross-Validation Gate 2

### Wave 3: 비판적 평가 (4 agents)
```
9. @critical-reviewer → 09-critical-review.md
10. @methodology-critic → 10-methodology-critique.md
11. @limitation-analyst → 11-limitation-analysis.md
12. @future-direction-analyst → 12-future-research-directions.md
```
→ Cross-Validation Gate 3

### Wave 4: 종합 (2 agents)
```
13. @synthesis-agent → 13-literature-synthesis.md
14. @conceptual-model-builder → 14-conceptual-model.md
```
→ Full SRCS Evaluation

### Wave 5: 품질 보증 (3 agents)
```
15. @plagiarism-checker → 15-plagiarism-report.md
16. @unified-srcs-evaluator → srcs-summary.json, quality-report.md
17. @research-synthesizer → research-synthesis.md (최종)
```

## 품질 게이트

### Cross-Validation Gates (Wave 1-3)
- 일관성 점수: 75점 이상 필수
- 불일치 발견 시 경고/중단

### Full SRCS Evaluation (Wave 4)
- SRCS 종합 점수: 75점 이상 필수
- 등급 C 이상 필수

### Plagiarism Check (Wave 5)
- 유사도: 15% 미만 필수
- 초과 시 작업 중단

## 출력

에이전트 실행 시 `_temp/`에 파일이 생성되며, `reorganize_outputs.py`로 정규 디렉토리에 정리합니다.

```
thesis-output/{session-dir}/
├── _temp/                          ← 런타임 에이전트 출력 (원본)
│   ├── 01-literature-search-strategy.md
│   ├── 02-seminal-works-analysis.md
│   ├── ... (15개 파일)
│   ├── cross-validation-result.json
│   ├── srcs-summary.json
│   └── quality-report.md
├── 01-literature/                  ← 정규 디렉토리 (reorganize 후)
│   ├── 01-literature-search-strategy.md
│   ├── 02-seminal-works-analysis.md
│   └── ... (동일 파일, 정리된 구조)
└── 00-session/
    └── session.json                ← SOT (workflow state 추적)
```

## 실행 방법

1. 각 에이전트를 Task 도구로 순차 호출
2. 각 Wave 완료 후 cross_validator.py 실행
3. Wave 4 완료 후 srcs_evaluator.py 실행
4. 모든 품질 게이트 통과 시 완료

## 완료 후

HITL-2 (`/thesis:review-literature`)로 사용자 승인 요청
