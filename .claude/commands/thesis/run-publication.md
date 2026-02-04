---
description: 투고 전략 파이프라인 실행. 학술지 선정부터 투고 패키지 준비까지 수행합니다.
context: fork
agent: general-purpose
---

# 투고 전략 파이프라인 실행

## 역할

이 커맨드는 **Phase 4 (Publication Strategy) 파이프라인**을 실행합니다.

## 전제 조건

- Phase 3 (Writing) 완료
- HITL-7 (초안 검토) 승인 완료
- `thesis-final.md` 생성 완료

## 실행 순서

### Step 1: 학술지 선정
```
@publication-strategist → journal-recommendation.md
```

### Step 2: 학술지 선택 (HITL)
사용자가 추천 목록에서 학술지 선택

### Step 3: 투고 패키지 준비
```
@manuscript-formatter → submission-package/
  ├── manuscript.md
  ├── abstract.md
  ├── keywords.md
  ├── cover-letter.md
  ├── title-page.md
  └── checklist.md
```

## 출력

```
thesis-output/
├── _temp/
│   └── journal-recommendation.md
└── submission-package/
    ├── manuscript.md
    ├── abstract.md
    ├── keywords.md
    ├── highlights.md
    ├── cover-letter.md
    ├── title-page.md
    ├── figures/
    ├── tables/
    ├── supplementary/
    └── checklist.md
```

## 완료 후

HITL-8 (`/thesis:finalize`)로 최종 완료
