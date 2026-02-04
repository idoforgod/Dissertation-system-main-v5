# Endnotes Workflow for YAML Claims

## 개요 (Overview)

이 문서는 논문의 GroundedClaim YAML 블록을 본문에서 미주(endnotes)로 처리하는 워크플로우를 설명합니다.

## 🎯 목적 (Purpose)

### 문제점
- YAML 블록이 본문에 삽입되어 가독성 저하
- 일반 독자에게는 과도한 메타데이터
- 학술적 엄밀성과 가독성의 균형 필요

### 해결책
- 본문: YAML 블록을 간단한 미주 참조로 대체 `[^1]`
- 논문 끝: 모든 Claims를 "Endnotes: Claims Registry" 섹션에 정리
- 학술적 투명성 유지 + 가독성 향상

## 📋 워크플로우 단계

### Step 1: 논문 작성 (Writing Phase)

**thesis-writer-rlm 에이전트가 수행:**

```markdown
본문 예시:

Campbell (2021) identifies three analytical frames for digital religion:
religion online, online religion, and religion and networked technologies.

```yaml
claim:
  id: "CH2-014"
  text: "Campbell's (2021) digital religion framework..."
  claim_type: THEORETICAL
  confidence: 88
  pTCS: 85
  ...
```

This framework provides analytical categories for understanding AI applications.
```

**현재 상태:** YAML 블록이 본문에 직접 삽입됨

### Step 2: 미주 변환 (Endnotes Conversion)

**export_to_docx_with_endnotes.js 스크립트 실행:**

```bash
# 영문 버전 (미주 처리)
node .claude/skills/thesis-orchestrator/scripts/export_to_docx_with_endnotes.js \
  thesis-output/<session-dir> en

# 한글 버전 (미주 처리)
node .claude/skills/thesis-orchestrator/scripts/export_to_docx_with_endnotes.js \
  thesis-output/<session-dir> ko
```

**처리 과정:**
1. 모든 YAML 블록 추출
2. 각 블록에 순차 번호 부여 (1, 2, 3, ...)
3. 본문에서 YAML 블록 제거 → `[^N]` 참조로 대체
4. 논문 끝에 "Endnotes: Claims Registry" 섹션 생성
5. Word 문서 생성

### Step 3: 최종 결과

**본문 (Body):**
```markdown
Campbell (2021) identifies three analytical frames for digital religion:
religion online, online religion, and networked technologies.[^14]

This framework provides analytical categories for understanding AI applications.
```

**미주 섹션 (Endnotes Section):**
```
Endnotes: Claims Registry

[14] Claim CH2-014
Text: Campbell's (2021) digital religion framework distinguishes 'religion
online' (traditional content delivered digitally)...
Type: THEORETICAL
Confidence: 88 | pTCS: 85
Sources:
  - type: PRIMARY
    reference: "Campbell, H.A. (2021). Digital Religion..."
    verified: true
Uncertainty: "AI-specific applications require empirical investigation..."
```

## 🔧 기술 구현

### 스크립트: export_to_docx_with_endnotes.js

**기능:**
1. **YAML 추출:** 정규표현식으로 ```yaml ... ``` 블록 감지
2. **번호 부여:** 순차적으로 claim 번호 할당
3. **본문 대체:** YAML 블록 → `[^N]` 상첨자 참조
4. **미주 생성:** 논문 끝에 전체 Claims Registry 섹션
5. **통계 생성:** 총 claims 수, 평균 confidence, 평균 pTCS

**출력 파일:**
- `dissertation-full-en-endnotes.docx` (영문 미주 버전)
- `dissertation-full-ko-endnotes.docx` (한글 미주 버전)

### 기존 스크립트와 비교

| 항목 | export_to_docx.js | export_to_docx_with_endnotes.js |
|------|-------------------|--------------------------------|
| YAML 블록 | 본문에 그대로 포함 | 미주로 이동 |
| 본문 참조 | 없음 | [^N] 상첨자 |
| 미주 섹션 | 없음 | Claims Registry 자동 생성 |
| 통계 | 없음 | 총계/평균 자동 계산 |
| 가독성 | 낮음 | 높음 |
| 학술성 | 높음 | 높음 (유지) |

## 📊 샘플 결과

### 현재 논문 (AI Transformation Framework)

**처리 결과:**
```
✅ Word document created: dissertation-full-en-endnotes.docx
📊 Total claims processed: 63

Claims breakdown:
- Chapter 1: 6 claims
- Chapter 2: 23 claims
- Chapter 3: 15 claims
- Chapter 4: 12 claims
- Chapter 5: 7 claims

Average Confidence: 87
Average pTCS: 84
```

**파일 크기 비교:**
```
dissertation-full-en.docx         116 KB (YAML 포함)
dissertation-full-en-endnotes.docx 124 KB (미주 처리)
```

미주 섹션 추가로 8KB 증가 (약 7% 증가, 가독성 대비 매우 합리적)

## 🎓 학술적 이점

### 1. 가독성 향상
- 본문에서 기술적 메타데이터 제거
- 논리 흐름이 자연스럽게 이어짐
- 일반 독자도 쉽게 읽을 수 있음

### 2. 학술적 엄밀성 유지
- 모든 claims의 출처, 신뢰도 완전 보존
- 미주로 체계적 정리
- 심사위원이 필요시 즉시 확인 가능

### 3. 투명성 증대
- Claims Registry에서 전체 주장 목록 한눈에 파악
- 통계 정보로 논문 품질 입증
- GRA 방법론의 혁신성 부각

### 4. 국제 표준 호환
- 미주(endnotes) 형식은 학술 논문 표준
- APA, Chicago, MLA 등 모든 스타일 가이드와 호환
- 저널 투고 시 편집 용이

## 🔄 워크플로우 통합

### Phase 3 (Thesis Writing) 수정 제안

**기존 프로세스:**
```
thesis-writer-rlm (각 장 작성, YAML 포함)
  ↓
dissertation-full-en.docx (YAML 그대로)
```

**신규 프로세스 (권장):**
```
thesis-writer-rlm (각 장 작성, YAML 포함)
  ↓
export_to_docx.js → dissertation-full-en.docx (학술 검토용)
  ↓
export_to_docx_with_endnotes.js → dissertation-full-en-endnotes.docx (제출용)
```

### 사용 시나리오

**시나리오 1: 박사학위 심사**
→ `dissertation-full-en-endnotes.docx` 제출
→ 본문 가독성 + 미주로 엄밀성 입증

**시나리오 2: 저널 투고**
→ `dissertation-full-en-endnotes.docx` 사용
→ 저널 편집자가 미주 형식 선호
→ 필요시 각주(footnotes)로 변환 용이

**시나리오 3: 동료 검토**
→ `dissertation-full-en.docx` 사용
→ 검토자가 YAML 메타데이터 직접 확인 필요

**시나리오 4: 출판/배포**
→ `dissertation-full-en-endnotes.docx` 기반
→ 일반 독자용으로 미주 섹션만 제거 가능

## 📝 커맨드 추가 제안

### 새로운 slash command

**`/thesis:export-with-endnotes [language]`**

```yaml
command:
  name: "export-with-endnotes"
  description: "Export dissertation with claims as endnotes"
  usage: "/thesis:export-with-endnotes [en|ko]"
  script: "scripts/export_to_docx_with_endnotes.js"
  output:
    - "dissertation-full-en-endnotes.docx"
    - "dissertation-full-ko-endnotes.docx"
```

**실행 예시:**
```bash
/thesis:export-with-endnotes en
# → 영문 미주 버전 생성

/thesis:export-with-endnotes ko
# → 한글 미주 버전 생성

/thesis:export-with-endnotes both
# → 영문/한글 모두 생성
```

## 🎯 Best Practices

### 1. 작성 단계
- thesis-writer-rlm은 계속 YAML 블록 포함해서 작성
- Markdown 원본에는 YAML 유지 (버전 관리)

### 2. 검토 단계
- 내부 검토: YAML 포함 버전 사용
- GRA 품질 검증: YAML 메타데이터 필수

### 3. 제출 단계
- 박사학위 심사: 미주 버전 제출
- 저널 투고: 미주 버전 제출
- 출판사: 요구사항에 따라 선택

### 4. 아카이빙
- 모든 버전 보관:
  - `*.md` (원본, YAML 포함)
  - `*-en.docx` (YAML 포함 Word)
  - `*-en-endnotes.docx` (미주 처리 Word)

## 📚 참고 자료

### 미주 vs 각주

| 특성 | 각주 (Footnotes) | 미주 (Endnotes) |
|------|-----------------|----------------|
| 위치 | 각 페이지 하단 | 논문/장 끝 |
| 가독성 | 즉시 확인 가능 | 본문 집중 가능 |
| 편집 | 복잡 (페이지 조정) | 간단 |
| 학술 표준 | 인문학 선호 | 과학/공학 선호 |
| Claims Registry | 부적합 (너무 김) | **최적** |

**결론:** Claims는 미주가 최적

### GRA와 미주의 조화

```
GRA (Grounded Research Architecture)
├─ Markdown 원본: YAML 블록 완전 보존
├─ 품질 검증: YAML 메타데이터 활용
├─ 통계 생성: 자동 계산
└─ Word 출력: 미주로 변환
    ├─ 본문: 깔끔한 학술 논문
    └─ 미주: 완전한 Claims Registry
```

## 🔮 향후 개선 방향

### 1. 자동화 강화
```javascript
// 논문 작성 완료 시 자동 실행
on_phase_complete('thesis-writing', () => {
  export_to_docx();  // YAML 포함
  export_to_docx_with_endnotes('en');  // 영문 미주
  export_to_docx_with_endnotes('ko');  // 한글 미주
});
```

### 2. 하이퍼링크 추가
- 본문 `[^N]` 클릭 → 해당 미주로 점프
- 미주에서 본문으로 역링크

### 3. 필터링 옵션
```bash
# confidence 낮은 claim만 미주로
export_to_docx_with_endnotes --threshold=80

# 특정 타입만 미주로
export_to_docx_with_endnotes --types=EMPIRICAL,THEORETICAL
```

### 4. PDF 출력
```bash
# Word → PDF 자동 변환
export_to_docx_with_endnotes --format=pdf
```

## ✅ 체크리스트

논문 제출 전 확인사항:

- [ ] Markdown 원본에 모든 YAML 블록 포함 확인
- [ ] `export_to_docx_with_endnotes.js` 실행 완료
- [ ] 생성된 Word 문서에서 미주 참조 번호 확인
- [ ] "Endnotes: Claims Registry" 섹션 완성도 확인
- [ ] 통계 정보 (총 claims, 평균값) 정확성 확인
- [ ] 본문 가독성 향상 확인
- [ ] 모든 버전 파일 백업 완료

## 📞 문의

이 워크플로우에 대한 질문이나 제안사항이 있으면:
- GitHub Issue 생성
- `thesis-orchestrator` skill 개발자에게 문의

---

**Last Updated**: 2026-01-21
**Version**: 1.0
**Status**: ✅ Production Ready
