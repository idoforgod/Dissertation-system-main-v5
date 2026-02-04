# 경로 문제 해결 설계안 (최소 침습적 개선)

## 🎯 설계 원칙

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠️  절대 불변 원칙 (Non-Negotiable Constraints)            │
├─────────────────────────────────────────────────────────────┤
│  1. 워크플로우 철학 100% 보존                               │
│     - Quality First                                         │
│     - Sequential execution                                  │
│     - GRA Hook validation                                   │
│     - Opus model for all agents                             │
│     - English primary + Korean translation                  │
│                                                             │
│  2. 5-Phase 구조 불변                                       │
│     - Phase 0: 초기화                                       │
│     - Phase 1: 문헌검토 (5 Waves + 3 Gates)                │
│     - Phase 2: 연구설계                                     │
│     - Phase 3: 논문작성 (Doctoral-writing mandatory)        │
│     - Phase 4: 투고전략                                     │
│                                                             │
│  3. Agent 순서 및 로직 불변                                 │
│     - 27개 전문 에이전트 순차 실행                          │
│     - Wave-Gate 구조 유지                                   │
│     - HITL 체크포인트 8개 유지                              │
│                                                             │
│  4. 품질 보증 시스템 불변                                   │
│     - GroundedClaim schema                                  │
│     - SRCS 4축 평가                                         │
│     - pTCS scoring                                          │
│     - Doctoral-writing compliance                           │
│                                                             │
│  5. 이중 언어 출력 불변                                     │
│     - 모든 작업은 영어로 수행                               │
│     - 자동 한국어 번역                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📍 문제 정의 (Infrastructure Level Only)

**문제**: 파일 저장 경로가 skill 실행 컨텍스트에 따라 변동
**영향 범위**: Infrastructure/Configuration 레벨 (워크플로우 로직 무관)
**해결 범위**: 경로 설정 메커니즘만 개선

---

## 🔧 해결 방안 (3-Tier Approach)

### Tier 1: 즉시 적용 (Zero Risk)
**대상**: `scripts/init_session.py` 기본값만 수정
**영향**: 없음 (backward compatible)

#### 수정 내용
```python
# 파일: scripts/init_session.py
# Line: ~15-20 (import section)

import os
from pathlib import Path

def get_repo_root():
    """
    Find repository root by searching for .git or specific marker.
    Falls back to environment variable or current directory.

    Returns absolute path to repository root.
    """
    # Method 1: Search for .git directory
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / '.git').exists():
            return parent

    # Method 2: Search for marker file
    for parent in [current] + list(current.parents):
        if (parent / 'Dissertation-system-main-v3').exists() or \
           (parent.name == 'Dissertation-system-main-v3'):
            return parent

    # Method 3: Environment variable
    if 'THESIS_REPO_ROOT' in os.environ:
        return Path(os.environ['THESIS_REPO_ROOT'])

    # Method 4: Hardcoded fallback (specific to this installation)
    fallback = Path.home() / 'Desktop/AIagentsAutomation/Dissertation-system-main-v3'
    if fallback.exists():
        return fallback

    # Method 5: Relative from script location
    # Go up from: .claude/skills/thesis-orchestrator/scripts/
    return Path(__file__).parent.parent.parent.parent

# Line: ~520 (argparse section)
REPO_ROOT = get_repo_root()
DEFAULT_OUTPUT_DIR = REPO_ROOT / "thesis-output"

parser.add_argument(
    "--base-dir",
    type=Path,
    default=DEFAULT_OUTPUT_DIR,  # ✅ Now absolute!
    help="Base directory for output (default: <repo-root>/thesis-output)"
)
```

**보존 사항**:
- ✅ 모든 워크플로우 로직 불변
- ✅ Agent 실행 순서 불변
- ✅ 출력 파일 구조 불변
- ✅ 품질 검증 로직 불변
- ✅ Backward compatible (기존 `--base-dir` 명시 방식 여전히 작동)

---

### Tier 2: 검증 추가 (Low Risk)
**대상**: 경로 유효성 검증 로직 추가
**영향**: 없음 (validation only, no behavior change)

#### 수정 내용
```python
# 파일: scripts/init_session.py
# Function: initialize_workflow (Line ~431)

def initialize_workflow(
    topic: str,
    mode: str,
    base_dir: Path,
    research_type: str | None = None,
    discipline: str | None = None,
) -> Path:
    """Initialize a complete research workflow with path validation."""

    # ✅ NEW: Path validation
    base_dir = base_dir.resolve()  # Convert to absolute path

    # Validate base_dir
    if not base_dir.exists():
        print(f"⚠️  Base directory does not exist: {base_dir}")
        print(f"📁 Creating: {base_dir}")
        base_dir.mkdir(parents=True, exist_ok=True)

    # Verify write permissions
    if not os.access(base_dir, os.W_OK):
        raise PermissionError(f"No write permission for: {base_dir}")

    # Warn if using skill-local directory (likely unintended)
    if '.claude/skills' in str(base_dir):
        print("=" * 70)
        print("⚠️  WARNING: Output directory is inside skill folder!")
        print(f"📁 Path: {base_dir}")
        print("💡 Consider using repository root instead:")
        print(f"   {get_repo_root() / 'thesis-output'}")
        print("=" * 70)

    # ✅ Continue with existing logic (unchanged)
    output_dir = create_output_structure(base_dir, topic)
    # ... rest of function unchanged ...
```

**보존 사항**:
- ✅ 모든 워크플로우 로직 불변
- ✅ 기존 동작 100% 보존 (validation만 추가)
- ✅ 경고만 표시, 실행은 계속됨

---

### Tier 3: 문서화 개선 (Zero Risk)
**대상**: README 및 사용 가이드
**영향**: 없음 (documentation only)

#### 추가 문서
```markdown
# 파일: scripts/README.md (NEW)

# Thesis Orchestrator Scripts

## 경로 설정 가이드

### 기본 동작 (권장)
스크립트는 자동으로 올바른 경로를 찾습니다:
```bash
python3 scripts/init_session.py "Your topic"
# 자동으로 <repo-root>/thesis-output/ 에 저장
```

### 수동 경로 지정
필요시 경로를 직접 지정할 수 있습니다:
```bash
python3 scripts/init_session.py "Your topic" \
    --base-dir /custom/path/to/output
```

### 환경 변수 사용
환경 변수로 기본 경로 변경 가능:
```bash
export THESIS_REPO_ROOT=/path/to/repo
python3 scripts/init_session.py "Your topic"
```

### 경로 확인
생성된 세션의 경로는 session.json에서 확인:
```bash
cat thesis-output/<session-dir>/00-session/session.json | jq .paths
```
```

**보존 사항**:
- ✅ 모든 워크플로우 불변
- ✅ 문서만 추가

---

## 🧪 테스트 계획 (검증 전용)

### Test Case 1: 기본 경로 (Tier 1 검증)
```bash
cd /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v3/.claude/skills/thesis-orchestrator
python3 scripts/init_session.py "Test topic"

# 예상 결과:
# ✅ /Users/cys/.../Dissertation-system-main-v3/thesis-output/test-topic-2026-01-24/
```

### Test Case 2: 명시적 경로 (Backward Compatibility)
```bash
python3 scripts/init_session.py "Test topic" \
    --base-dir /tmp/test-output

# 예상 결과:
# ✅ /tmp/test-output/test-topic-2026-01-24/
```

### Test Case 3: 환경 변수 (Tier 1 검증)
```bash
export THESIS_REPO_ROOT=/custom/repo
python3 scripts/init_session.py "Test topic"

# 예상 결과:
# ✅ /custom/repo/thesis-output/test-topic-2026-01-24/
```

### Test Case 4: 워크플로우 무결성 (핵심 검증)
```bash
# 전체 워크플로우 실행
python3 scripts/init_session.py "AI free will test"

# 검증:
# ✅ 모든 27개 에이전트 순차 실행
# ✅ 5 Waves + 3 Gates 정상 작동
# ✅ SRCS/pTCS 점수 정상
# ✅ Doctoral-writing 적용 정상
# ✅ 이중 언어 출력 정상
# ✅ 파일 구조 동일
```

---

## 📊 변경 영향 분석

| 구성 요소 | 변경 여부 | 영향도 |
|----------|----------|--------|
| **워크플로우 철학** | ❌ 불변 | 0% |
| **Phase 구조** | ❌ 불변 | 0% |
| **Agent 순서** | ❌ 불변 | 0% |
| **Wave-Gate 구조** | ❌ 불변 | 0% |
| **HITL 체크포인트** | ❌ 불변 | 0% |
| **GRA 검증** | ❌ 불변 | 0% |
| **SRCS/pTCS** | ❌ 불변 | 0% |
| **Doctoral-writing** | ❌ 불변 | 0% |
| **이중 언어** | ❌ 불변 | 0% |
| **출력 파일 구조** | ❌ 불변 | 0% |
| **경로 설정 메커니즘** | ✅ 개선 | Infrastructure only |
| **경로 검증** | ✅ 추가 | Validation only |
| **문서화** | ✅ 개선 | Documentation only |

**총 영향도**: 0% (워크플로우 로직), 100% 개선 (Infrastructure)

---

## 🎯 구현 우선순위

### Priority 1: Tier 1 (즉시 적용 권장)
- **파일**: `scripts/init_session.py` (1개 파일만 수정)
- **변경 범위**: ~30 lines
- **위험도**: Zero (backward compatible)
- **효과**: 경로 문제 완전 해결

### Priority 2: Tier 2 (선택 사항)
- **파일**: `scripts/init_session.py` (동일 파일)
- **변경 범위**: ~20 lines (validation logic)
- **위험도**: Zero (warning only)
- **효과**: 사용자 경험 개선

### Priority 3: Tier 3 (선택 사항)
- **파일**: `scripts/README.md` (신규)
- **변경 범위**: Documentation
- **위험도**: Zero
- **효과**: 사용성 개선

---

## 📝 구현 체크리스트

### Tier 1 Implementation
- [ ] `get_repo_root()` 함수 추가
- [ ] `DEFAULT_OUTPUT_DIR` 계산 로직 추가
- [ ] argparse default 변경
- [ ] 테스트 실행 (Test Case 1-4)
- [ ] 기존 워크플로우 무결성 검증

### Tier 2 Implementation (Optional)
- [ ] Path validation 로직 추가
- [ ] Warning message 추가
- [ ] 테스트 실행
- [ ] Edge case 검증

### Tier 3 Implementation (Optional)
- [ ] README.md 작성
- [ ] Usage examples 추가
- [ ] Troubleshooting guide 추가

---

## 🔒 품질 보증 (Quality Assurance)

### 불변성 검증 체크리스트
- [ ] ✅ Phase 0-4 구조 유지 확인
- [ ] ✅ 27개 에이전트 순서 불변 확인
- [ ] ✅ 5 Waves 구조 유지 확인
- [ ] ✅ 3 Gates 검증 작동 확인
- [ ] ✅ 8 HITL 체크포인트 유지 확인
- [ ] ✅ GroundedClaim schema 불변 확인
- [ ] ✅ SRCS 4축 평가 작동 확인
- [ ] ✅ pTCS scoring 작동 확인
- [ ] ✅ Doctoral-writing 적용 확인
- [ ] ✅ Bilingual output 작동 확인
- [ ] ✅ 파일 구조 동일성 확인

### 회귀 테스트
```bash
# 기존 워크플로우와 100% 동일한 출력 검증
# (경로만 다르고 내용은 동일해야 함)

# Before fix:
python3 scripts/init_session.py "Test" --base-dir /tmp/before

# After fix:
python3 scripts/init_session.py "Test" --base-dir /tmp/after

# Compare:
diff -r /tmp/before/<session>/ /tmp/after/<session>/
# 예상: 경로 정보 제외하고 모든 파일 내용 동일
```

---

## 📋 코드 리뷰 체크리스트

### 변경 전 필수 확인
- [ ] ✅ 워크플로우 철학 문서 재검토
- [ ] ✅ Phase 구조 다이어그램 확인
- [ ] ✅ Agent dependency graph 확인
- [ ] ✅ 기존 테스트 케이스 전수 실행

### 변경 후 필수 확인
- [ ] ✅ 모든 기존 테스트 통과
- [ ] ✅ 신규 경로 테스트 통과
- [ ] ✅ Backward compatibility 확인
- [ ] ✅ Documentation 업데이트

---

## 🎓 설계 철학 재확인

```
┌─────────────────────────────────────────────────────────────┐
│  이 개선안은 다음을 절대 변경하지 않습니다:                  │
├─────────────────────────────────────────────────────────────┤
│  ✅ 학술적 품질 최우선 (Quality First)                      │
│  ✅ 순차 실행 (Sequential Execution)                        │
│  ✅ GRA 검증 (All outputs validated)                        │
│  ✅ Opus 모델 (All agents use Opus)                         │
│  ✅ 영어 우선 + 한국어 자동 번역                            │
│  ✅ 5-Phase 구조 (Phase 0-4)                                │
│  ✅ Wave-Gate 구조 (5 Waves, 3 Gates)                       │
│  ✅ HITL 체크포인트 (8개)                                   │
│  ✅ Doctoral-writing 필수 (Phase 3)                         │
│  ✅ 이중 언어 출력 (English + Korean)                       │
│  ✅ 27개 전문 에이전트                                      │
│  ✅ GroundedClaim schema                                    │
│  ✅ SRCS/pTCS 품질 점수                                     │
└─────────────────────────────────────────────────────────────┘

변경하는 것:
  📍 파일 저장 경로 결정 로직만 (Infrastructure level)
```

---

## 승인 및 적용

### 승인 필요 사항
- [ ] Tier 1 구현 승인 (권장: 즉시 적용)
- [ ] Tier 2 구현 승인 (선택: 안전성 추가)
- [ ] Tier 3 구현 승인 (선택: 문서화)

### 적용 방법
```bash
# Tier 1만 적용하는 경우 (최소 변경)
# 1. scripts/init_session.py 수정 (~50 lines)
# 2. 테스트 실행
# 3. 완료
```

---

**설계 원칙 준수 확인**: ✅
**워크플로우 철학 보존**: ✅
**최소 침습적 개선**: ✅
**Backward Compatibility**: ✅

---

**작성일**: 2026-01-24
**작성자**: Claude (thesis-orchestrator design review)
**상태**: 승인 대기
