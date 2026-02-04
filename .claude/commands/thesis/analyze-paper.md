---
name: analyze-paper
description: Stage 1 - 선행연구 논문 심층 분석. 업로드된 논문을 4개 프레임워크로 분석하고 비판적 평가를 수행합니다.
agent: paper-analyzer
allowed-tools:
  - Read(*)
  - Write(*)
  - Task(*)
model: opus
---

# /thesis:analyze-paper

**Stage 1**: 선행연구 논문 심층 분석

이 커맨드는 업로드된 논문을 심층 분석하여 연구 설계의 기초를 마련합니다.

---

## 사용 방법

### 기본 사용

```bash
/thesis:analyze-paper --paper-path user-resource/uploaded-papers/smith-2023.pdf
```

### 고급 옵션

```bash
# 분석 깊이 지정
/thesis:analyze-paper --paper-path <경로> --depth comprehensive

# 특정 프레임워크만 사용
/thesis:analyze-paper --paper-path <경로> --frameworks "theoretical,methodological"

# 출력 경로 지정
/thesis:analyze-paper --paper-path <경로> --output thesis-output/stage1-analysis.md
```

---

## 파라미터

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| `--paper-path` | Yes | - | 분석할 논문 파일 경로 (PDF) |
| `--depth` | No | `standard` | 분석 깊이: `quick`, `standard`, `comprehensive` |
| `--frameworks` | No | `all` | 사용할 프레임워크: `theoretical`, `methodological`, `empirical`, `critical` (쉼표 구분) |
| `--output` | No | `stage1-paper-analysis.md` | 출력 파일 경로 |
| `--language` | No | `auto` | 논문 언어: `auto`, `en`, `ko` |

---

## 출력 구조

```
stage1-paper-analysis.md
├─ 1. Paper Metadata
│  ├─ Title, Authors, Year
│  ├─ Journal, Citation Count
│  └─ Keywords
├─ 2. Theoretical Framework Analysis
│  ├─ Main Theories
│  ├─ Theoretical Contributions
│  └─ Theoretical Gaps
├─ 3. Methodological Analysis
│  ├─ Research Design
│  ├─ Sample & Data Collection
│  ├─ Analysis Techniques
│  ├─ Validity Assessment
│  └─ Methodological Strengths/Weaknesses
├─ 4. Empirical Evidence Analysis
│  ├─ Key Findings
│  ├─ Effect Sizes
│  ├─ Statistical Significance
│  └─ Practical Significance
├─ 5. Critical Evaluation
│  ├─ Author-Acknowledged Limitations
│  ├─ Unacknowledged Limitations (비판적 분석)
│  ├─ Alternative Explanations
│  └─ Boundary Conditions
└─ 6. Summary & Implications
   ├─ Main Contributions
   ├─ Limitations Summary
   └─ Future Research Directions
```

---

## 예시

### Example 1: 표준 분석

```bash
/thesis:analyze-paper --paper-path user-resource/uploaded-papers/transformational-leadership-study.pdf
```

**출력**:
```markdown
# Paper Analysis: Transformational Leadership and Innovation

## 1. Paper Metadata
- **Title**: The Impact of Transformational Leadership on Employee Innovation
- **Authors**: Smith, J., & Johnson, M.
- **Year**: 2023
- **Journal**: Academy of Management Journal (A+ tier)
- **Citations**: 127
- **DOI**: 10.5465/amj.2023.xxxx

## 2. Theoretical Framework Analysis
### Main Theories
1. **Transformational Leadership Theory (Bass, 1985)**
   - Four dimensions: Idealized influence, Inspirational motivation...

2. **Self-Determination Theory (Deci & Ryan, 2000)**
   - Intrinsic motivation as mediating mechanism...

### Theoretical Contributions
- Integrates two major theories to explain innovation process
- Proposes intrinsic motivation as key mediator
- Extends leadership literature to innovation context

### Theoretical Gaps
- Does not consider boundary conditions (e.g., organizational climate)
- Limited discussion of dark side of transformational leadership
- Assumes universal applicability across cultures

[... 계속 ...]
```

### Example 2: 빠른 분석 (시간 제한)

```bash
/thesis:analyze-paper --paper-path paper.pdf --depth quick
```

주요 섹션만 분석 (20-30분 소요)

### Example 3: 특정 프레임워크만

```bash
/thesis:analyze-paper --paper-path paper.pdf --frameworks "theoretical,critical"
```

이론적 분석과 비판적 평가만 수행

---

## 분석 깊이 비교

| Depth | Time | Frameworks | Output Pages | Best For |
|-------|------|------------|--------------|----------|
| `quick` | 20-30분 | 2개 (핵심만) | 8-12 pages | 시간 제한, 예비 검토 |
| `standard` | 40-60분 | 4개 (전체) | 15-20 pages | 일반적 연구 (권장) |
| `comprehensive` | 60-90분 | 4개 + 상세 | 25-35 pages | 박사논문, 체계적 검토 |

---

## Prerequisites

이 커맨드 실행 전 필요한 것:

1. **논문 파일 준비**
   - PDF 형식
   - `user-resource/uploaded-papers/` 폴더에 배치
   - 파일명: 영문, 공백 없이 (예: `smith-2023.pdf`)

2. **세션 초기화** (선택)
   - `/thesis:init` 실행 (자동으로 디렉토리 생성)
   - 또는 수동으로 `thesis-output/` 폴더 생성

---

## 다음 단계

분석 완료 후:

```bash
# Stage 2로 진행 (연구 갭 식별)
/thesis:identify-gaps --analysis-file stage1-paper-analysis.md

# 또는 전체 워크플로우 재개
/thesis:run-paper-upload --resume-from stage2
```

---

## 오류 처리

### 파일을 찾을 수 없음
```
Error: File not found: user-resource/uploaded-papers/paper.pdf

Solution:
1. 파일 경로 확인
2. 파일을 올바른 폴더에 배치
3. 파일명에 특수문자나 공백이 없는지 확인
```

### PDF 파싱 오류
```
Error: Unable to parse PDF. The file may be corrupted or image-based.

Solution:
1. PDF가 텍스트 기반인지 확인 (이미지 PDF는 OCR 필요)
2. 파일이 손상되지 않았는지 확인
3. 다른 PDF로 시도
```

### 메모리 부족 (대용량 파일)
```
Warning: Large file detected (>50MB). Using streaming mode.

Solution:
- 자동으로 처리됨
- 분석 시간이 더 걸릴 수 있음
```

---

## 관련 커맨드

- `/thesis:start-paper-upload` - 전체 워크플로우 시작
- `/thesis:identify-gaps` - Stage 2 실행
- `/thesis:status` - 진행 상태 확인

---

**버전**: 1.0.0
**작성일**: 2026-01-28
**에이전트**: paper-analyzer (Opus)
