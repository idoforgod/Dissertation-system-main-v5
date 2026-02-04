---
description: 표절 검사 (유사도 분석, 15% 미만 필수)
context: fork
agent: general-purpose
---

# 표절 검사

논문 또는 문헌검토 결과의 표절 및 유사도를 검사합니다.

## 역할

이 커맨드는 **plagiarism-checker agent**를 실행하여:
- 기존 문헌과의 유사도 분석
- 자기표절 검사
- 부적절한 인용 탐지
- 패러프레이징 검증

## 전제 조건

- 검사할 논문/문헌검토 파일 존재
- 참조 문헌 데이터베이스 접근 가능

## 유사도 기준

| 유사도 | 판정 | 조치 |
|--------|------|------|
| 0-15% | ✅ Pass | 안전 |
| 16-25% | ⚠️ Caution | 검토 권장 |
| 26-40% | ❌ High | 수정 필수 |
| 41%+ | 🚨 Critical | 작업 중단 |

**Threshold: 15% 미만 필수**

## 실행 방법

plagiarism-checker agent를 Task 도구로 호출:

```markdown
Task: plagiarism-checker agent 실행

Description: 표절 검사 수행

Input:
- 검사 대상: thesis-output/[project]/_temp/*.md (또는 thesis-final.md)
- 참조 데이터: 기존 문헌, 선행연구

Output:
- plagiarism-report.md
- similarity-score.json
```

## 출력 형식

### plagiarism-report.md
```markdown
# 표절 검사 보고서

## 전체 유사도
- **Overall Similarity**: 12.3%
- **Status**: ✅ PASSED (< 15%)

## 세부 분석

### 1. 외부 문헌 유사도
- Source 1: Journal Article XYZ (8.5%)
- Source 2: Conference Paper ABC (2.1%)
- Source 3: Book Chapter DEF (1.7%)

### 2. 자기표절 검사
- 이전 작업물: 0.0% (해당 없음)

### 3. 부적절한 인용
- 발견되지 않음 ✅

### 4. 패러프레이징 품질
- 적절함 ✅

## 권장 사항
- 추가 조치 불필요
```

## 실행 예시

```python
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path.cwd() / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))

# Get working directory
import json
session_file = Path("thesis-output") / "session.json"
if session_file.exists():
    with open(session_file) as f:
        session = json.load(f)
    working_dir = Path(session["working_dir"])
else:
    print("❌ Error: No active session found")
    sys.exit(1)

# Find files to check
temp_dir = working_dir / "_temp"
target_files = list(temp_dir.glob("*.md"))

# Also check final thesis if exists
thesis_final = working_dir / "thesis-final.md"
if thesis_final.exists():
    target_files.append(thesis_final)

if not target_files:
    print("❌ Error: No files to check")
    sys.exit(1)

print(f"\n📋 Checking {len(target_files)} file(s) for plagiarism...")

# Call plagiarism-checker agent via Task tool
# (This is a placeholder - actual implementation uses Task tool)
print("\n⚙️  Running plagiarism-checker agent...")

# Simulate result (actual implementation calls agent)
similarity_score = 12.3

print("\n" + "="*70)
print("           PLAGIARISM CHECK RESULTS")
print("="*70)
print(f"\n📊 Overall Similarity: {similarity_score:.1f}%")

threshold = 15.0
if similarity_score < threshold:
    print(f"✅ PASSED: Similarity ({similarity_score:.1f}%) < threshold ({threshold}%)")
    status = "PASS"
else:
    print(f"❌ FAILED: Similarity ({similarity_score:.1f}%) >= threshold ({threshold}%)")
    status = "FAIL"

# Save report
report_file = working_dir / "plagiarism-report.md"
print(f"\n📄 Report saved to: {report_file}")
print("="*70)

sys.exit(0 if status == "PASS" else 1)
```

## 검사 범위

1. **Wave 5 (Phase 1)**: 문헌검토 결과
2. **Phase 3**: 논문 장별 초안
3. **Final**: 최종 논문 전체

## 조치 사항

### 유사도 15% 초과 시
1. 유사 구절 식별
2. 적절한 인용 추가
3. 패러프레이징 개선
4. 재검사 수행

### 유사도 25% 초과 시
- **작업 중단** (SKILL.md 규정)
- 전면 수정 필요
- 재작성 고려

## 관련 명령어

- `/thesis:evaluate-srcs` - SRCS 평가
- `/thesis:validate-phase` - Phase 검증
- `/thesis:run-writing` - 논문 작성

$ARGUMENTS
