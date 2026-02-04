---
description: Export thesis chapters to a single Word document
context: fork
agent: haiku
---

# Export Thesis to Word Document

논문의 모든 장(chapter*.md)을 하나의 통합된 Word 파일로 변환합니다.

## 작업 수행

당신은 다음 단계를 순차적으로 수행해야 합니다:

### 1. 세션 디렉토리 확인

```bash
# 사용자가 인자를 제공한 경우
SESSION_DIR="$1"

# 인자가 없으면 최신 세션 자동 감지
if [ -z "$SESSION_DIR" ]; then
  SESSION_DIR=$(ls -td thesis-output/*/ 2>/dev/null | head -1 | sed 's:/$::')
fi

# 세션 디렉토리 검증
if [ ! -d "$SESSION_DIR" ]; then
  echo "❌ 세션 디렉토리를 찾을 수 없습니다: $SESSION_DIR"
  exit 1
fi

# session.json 존재 확인
if [ ! -f "$SESSION_DIR/00-session/session.json" ]; then
  echo "❌ session.json을 찾을 수 없습니다: $SESSION_DIR/00-session/session.json"
  exit 1
fi
```

### 2. docx 패키지 설치 확인

Bash 도구를 사용하여 다음을 실행:

```bash
# docx 패키지 확인 및 설치
if ! npm list docx >/dev/null 2>&1; then
  echo "📦 docx 패키지 설치 중..."
  npm install docx
fi
```

### 3. Word 문서 생성

Bash 도구를 사용하여 스크립트 실행:

```bash
node .claude/skills/thesis-orchestrator/scripts/export_to_docx.js "$SESSION_DIR"
```

### 4. 결과 확인 및 보고

- 생성된 Word 파일 경로 확인
- 파일 크기 표시
- 사용자에게 다운로드 가능 안내

## 출력 예시

```
📚 총 5개 장 파일 발견:
  1. chapter1-introduction.md
  2. chapter2-literature-review.md
  3. chapter3-methodology.md
  4. chapter4-results.md
  5. chapter5-conclusion.md

✅ Word 문서 생성 완료!
📁 저장 위치: thesis-output/.../03-thesis/박사논문_aiof-free-will-possibilityin-study_전체.docx
📄 총 5개 장이 통합되었습니다.
📝 session.json 업데이트 완료
```

## 에러 처리

당신은 다음 에러를 적절히 처리해야 합니다:

- **세션 없음**: `thesis-output/` 디렉토리에 세션이 없으면 사용자에게 먼저 `/thesis:start`를 실행하도록 안내
- **chapter 파일 없음**: Phase 3가 완료되지 않았으면 먼저 `/thesis:run-writing`을 실행하도록 안내
- **Node.js 없음**: Node.js 설치 필요성 안내
- **스크립트 실행 실패**: 에러 메시지 표시 및 문제 진단
