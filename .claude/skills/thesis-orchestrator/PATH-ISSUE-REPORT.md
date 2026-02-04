# 경로 오류 검수 보고서

## 문제 요약

**예상 경로**:
```
/Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output/
```

**실제 생성 경로**:
```
/Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/.claude/skills/thesis-orchestrator/thesis-output/
```

**경로 차이**: `.claude/skills/thesis-orchestrator/` 하위로 잘못 생성됨

---

## 원인 분석

### 1. 스크립트 실행 시점의 작업 디렉토리

```bash
현재 작업 디렉토리: /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/.claude/skills/thesis-orchestrator
```

skill이 실행될 때 자동으로 skill의 base directory로 이동하므로, pwd가 `.claude/skills/thesis-orchestrator`가 되었습니다.

### 2. init_session.py의 기본 파라미터

**파일**: `scripts/init_session.py`
**Line 520**:
```python
parser.add_argument(
    "--base-dir",
    type=Path,
    default=Path("thesis-output"),  # ⚠️ 상대 경로!
    help="Base directory for output"
)
```

### 3. 실행 명령어

```bash
python3 scripts/init_session.py "Can AI Have Free Will?..." \
    --mode topic \
    --type qualitative \
    --discipline "..."
```

**문제점**: `--base-dir` 파라미터를 명시하지 않음
→ 기본값 `Path("thesis-output")` 사용 (상대 경로)
→ 현재 작업 디렉토리 기준으로 생성

### 4. 경로 생성 과정

```
현재 디렉토리: /Users/cys/.../thesis-orchestrator
기본값: Path("thesis-output")  # 상대 경로
결과: /Users/cys/.../thesis-orchestrator/thesis-output/
```

---

## 이전 세션들과의 비교

### 이전 세션들 (올바른 경로)

```bash
$ ls /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output/

AI-free-will-impossibility-2026-01-20
ai-transformation-ax-framework-for-small-churches-2026-01-21
can-artificial-intelligence-possess-free-will-a-2026-01-22
can-artificial-intelligence-possess-free-will-an-2026-01-21
인공지능의 자유의지 가능성-2026-01-18
인공지능의 자유의지 가능성-v2-2026-01-18
```

**이전에는 어떻게 올바른 경로에 생성되었나?**

가능성 1: 프로젝트 루트에서 실행
```bash
cd /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3
python3 .claude/skills/thesis-orchestrator/scripts/init_session.py ...
```

가능성 2: 절대 경로 명시
```bash
python3 scripts/init_session.py ... --base-dir /Users/cys/.../thesis-output
```

---

## 근본 원인

### Primary Cause: 상대 경로 기본값
- `init_session.py`의 `--base-dir` 기본값이 상대 경로 `Path("thesis-output")`
- Claude Code skill 실행 시 자동으로 skill base directory로 이동
- 결과적으로 skill 디렉토리 하위에 생성

### Contributing Factors:
1. **Skill execution context**: Skill이 실행되면 자동으로 해당 skill의 base directory가 working directory가 됨
2. **Base directory 명시하지 않음**: `--base-dir` 파라미터를 절대 경로로 지정하지 않음
3. **상대 경로 의존**: 스크립트가 절대 경로가 아닌 상대 경로를 기본값으로 사용

---

## 해결 방안

### Option 1: 스크립트 수정 (권장)

**파일**: `scripts/init_session.py`

```python
# 현재 (Line 520)
default=Path("thesis-output")

# 수정안 1: 절대 경로 사용
import os
REPO_ROOT = Path(__file__).parent.parent.parent.parent  # Go up to repo root
default=REPO_ROOT / "thesis-output"

# 수정안 2: 환경 변수 사용
default=Path(os.environ.get("THESIS_OUTPUT_DIR", "thesis-output"))
```

### Option 2: 실행 시 명시 (임시 해결)

```bash
python3 scripts/init_session.py "..." \
    --base-dir /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output
```

### Option 3: Skill 스크립트 수정

Skill이 스크립트를 호출할 때 자동으로 올바른 경로 전달:

```python
base_dir = Path(__file__).parent.parent.parent / "thesis-output"
subprocess.run([
    "python3", "scripts/init_session.py", topic,
    "--base-dir", str(base_dir.resolve())
])
```

---

## 즉시 조치 사항

### 1. 생성된 파일 이동

```bash
# 현재 위치에서
mv thesis-output/can-ai-have-free-will-an-interdisciplinary-study-2026-01-24 \
   /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output/
```

### 2. session.json 경로 업데이트

```json
{
  "paths": {
    "base_dir": "/Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output",
    "output_dir": "can-ai-have-free-will-an-interdisciplinary-study-2026-01-24",
    "absolute_path": "/Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output/can-ai-have-free-will-an-interdisciplinary-study-2026-01-24"
  }
}
```

---

## 향후 방지 대책

### 1. 스크립트 개선
- `init_session.py`의 기본 경로를 절대 경로로 변경
- 경로 검증 로직 추가

### 2. Skill 개선
- Skill이 스크립트 호출 시 명시적으로 절대 경로 전달
- 경로 일관성 검증 추가

### 3. 문서화
- README에 경로 설정 가이드 추가
- Skill 사용 시 주의사항 명시

---

## 테스트 검증

### 현재 상태 확인
```bash
$ find /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3 \
  -name "can-ai-have-free-will-*" -type d

/Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/.claude/skills/thesis-orchestrator/thesis-output/can-ai-have-free-will-an-interdisciplinary-study-2026-01-24
```

### 이동 후 확인 (예상)
```bash
$ ls /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/thesis-output/

AI-free-will-impossibility-2026-01-20
can-ai-have-free-will-an-interdisciplinary-study-2026-01-24  ✅ NEW
...
```

---

## 결론

**근본 원인**: 상대 경로 기본값 + Skill execution context 조합

**즉시 조치**: 파일 이동

**장기 해결**: 스크립트 기본값을 절대 경로로 변경

**책임**: 스크립트 설계 시 상대 경로를 기본값으로 사용한 설계 결함

---

**보고서 작성 일시**: 2026-01-24
**작성자**: Claude (thesis-orchestrator workflow)
**상태**: 원인 규명 완료, 해결 방안 제시
