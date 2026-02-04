---
description: 연구 유형 설정 (HITL-3). 양적/질적/혼합 연구 유형을 선택합니다.
---

# 연구 유형 설정 (HITL-3)

## 역할

이 커맨드는 **연구 유형을 선택**하는 HITL-3 체크포인트입니다.

## 연구 유형 옵션

### 양적연구 (Quantitative Research)
```
○ 실험연구 (Experimental)
  - 무작위 통제 실험
  - 진실험 설계

○ 준실험연구 (Quasi-Experimental)
  - 비동등 통제집단 설계
  - 단절적 시계열 설계

○ 조사연구 (Survey)
  - 횡단 조사
  - 종단 조사 (패널/코호트)

○ 2차자료 분석 (Secondary Data Analysis)
  - 기존 데이터베이스 활용
```

### 질적연구 (Qualitative Research)
```
○ 현상학적 연구 (Phenomenology)
  - 체험의 본질 탐구

○ 근거이론 (Grounded Theory)
  - 이론 생성

○ 사례연구 (Case Study)
  - 단일/다중 사례

○ 문화기술지 (Ethnography)
  - 문화적 맥락 이해

○ 내러티브 연구 (Narrative Inquiry)
  - 개인 경험 이야기
```

### 혼합연구 (Mixed Methods)
```
○ 수렴적 설계 (Convergent Design)
  - QUAN + QUAL 동시 수행

○ 설명적 순차 설계 (Explanatory Sequential)
  - QUAN → qual

○ 탐색적 순차 설계 (Exploratory Sequential)
  - QUAL → quan

○ 내재적 설계 (Embedded Design)
  - 주 방법 내 보조 방법 내재
```

## 프로세스

### Step 1: 문헌검토 결과 기반 제안

`research-synthesis.md`를 분석하여:
- 연구 질문 특성
- 선행연구 주요 방법론
- 연구 갭 특성

### Step 2: 적합한 연구 유형 추천

```markdown
## 추천 연구 유형

### 1순위: [유형명]
- 적합도: ⭐⭐⭐⭐⭐
- 근거: [추천 이유]
- 장점: [장점]
- 단점: [단점]

### 2순위: [유형명]
[동일 형식]
```

### Step 3: 사용자 선택

사용자가 연구 유형 선택

### Step 4: session.json 업데이트

```json
{
  "research": {
    "type": "quantitative|qualitative|mixed",
    "subtype": "survey|case_study|convergent|..."
  }
}
```

## 다음 단계

선택된 연구 유형에 따라 해당 경로의 에이전트들이 실행됩니다.
