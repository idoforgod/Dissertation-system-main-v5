---
description: 박사논문 연구 워크플로우 초기화 및 연구유형 선택 (HITL-0)
allowed-tools: Bash(*), Write(*), Read(*)
---

# 박사논문 연구 워크플로우 초기화

새로운 연구 세션을 초기화합니다.

## 실행 단계

1. **디렉토리 생성**: `thesis-output/[연구제목-날짜]/` 구조 생성
2. **세션 파일 생성**: `session.json` 초기화
3. **체크리스트 생성**: `todo-checklist.md` (150단계) 생성
4. **연구 옵션 설정**: 사용자에게 연구유형 및 학문분야 선택 요청

## 초기화 스크립트 실행

```bash
python3 .claude/skills/thesis-orchestrator/scripts/init_session.py "$ARGUMENTS" --mode topic --base-dir thesis-output
```

## HITL-0 체크포인트

사용자에게 다음 옵션을 선택하도록 요청:

### 입력 모드 선택
- **Mode A**: 연구 주제 입력 (기본)
- **Mode B**: 연구질문 직접 입력
- **Mode C**: 기존 문헌검토 분석
- **Mode D**: 학습모드
- **Mode E**: 선행연구 논문 업로드 ⭐ NEW

### 연구 유형
- 양적연구 (Quantitative Research)
- 질적연구 (Qualitative Research)
- 혼합연구 (Mixed Methods Research)
- 철학적/이론적 연구 (Philosophical/Theoretical Research)
- 아직 미정 (문헌검토 후 결정)

### 학문 분야
- 경영학/경제학
- 사회과학
- 인문학
- 자연과학/공학
- 의학/보건학
- 교육학
- 기타

### 인용 스타일 (Citation Style)
- APA 7th Edition (권장, 사회과학/경영학/교육학 표준)
- Chicago 17th Edition (인문학/역사학, 각주 방식)
- MLA 9th Edition (어문학/인문학)
- Harvard Referencing (영연방권 대학교 표준)
- IEEE (공학/컴퓨터과학, 번호 방식)

선택된 인용 스타일은 session.json에 저장되며, 이후 모든 Phase에서 자동 적용됩니다.

## 다음 단계

### Mode A-D 선택 시
초기화 완료 후 `/thesis:start [mode] [input]` 명령으로 워크플로우를 시작합니다.

### Mode E 선택 시
초기화 완료 후 `/thesis:start paper-upload --paper-path [파일경로]` 명령으로 논문 분석을 시작합니다.

$ARGUMENTS
