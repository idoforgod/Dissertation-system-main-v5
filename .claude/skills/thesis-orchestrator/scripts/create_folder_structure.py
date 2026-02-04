#!/usr/bin/env python3
"""
연구 자료 폴더 구조 생성 스크립트

박사논문 연구 워크플로우를 위한 체계적인 폴더 구조를 생성합니다.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Optional


def create_research_folder_structure(
    base_dir: Path,
    topic: str,
    date_str: Optional[str] = None
) -> Path:
    """
    연구 자료를 위한 체계적인 폴더 구조를 생성합니다.

    Args:
        base_dir: 기본 출력 디렉토리 (thesis-output/)
        topic: 연구 주제
        date_str: 날짜 문자열 (기본: 오늘 날짜)

    Returns:
        생성된 연구 폴더 경로
    """
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")

    # 연구 폴더 이름 생성
    folder_name = f"{topic}-{date_str}"
    research_dir = base_dir / folder_name

    # 폴더 구조 정의
    folders = [
        # 00-session: 세션 관리
        "00-session",
        "00-session/hitl-records",

        # 01-sources: 문헌 및 자료 관리
        "01-sources/bibliography",
        "01-sources/primary-sources/notes",
        "01-sources/secondary-sources/notes",
        "01-sources/tertiary-sources",
        "01-sources/web-sources/archive",

        # 02-literature-review: Phase 1 문헌검토
        "02-literature-review/wave-1-search",
        "02-literature-review/wave-2-analysis",
        "02-literature-review/wave-3-critique",
        "02-literature-review/wave-4-synthesis",
        "02-literature-review/wave-5-quality",

        # 03-research-design: Phase 2 연구설계
        "03-research-design/instruments",

        # 04-data: 연구 데이터
        "04-data/raw",
        "04-data/processed",
        "04-data/analysis",

        # 05-drafts: Phase 3 논문 초안
        "05-drafts/outline",
        "05-drafts/chapters",
        "05-drafts/revisions",
        "05-drafts/review-reports",

        # 06-final: 최종 산출물
        "06-final/appendices",
        "06-final/figures-tables/figures",
        "06-final/figures-tables/tables",

        # 07-submission: Phase 4 투고
        "07-submission/packages",

        # 08-quality: 품질 관리
        "08-quality/srcs-reports",
        "08-quality/gra-validations",
        "08-quality/plagiarism",
        "08-quality/claims-registry/claims-by-document",

        # 09-references: 참고자료 통합 관리
        "09-references/reading-notes",

        # 10-archive: 아카이브
        "10-archive/version-history",
        "10-archive/deprecated",
        "10-archive/backups",
    ]

    # 폴더 생성
    for folder in folders:
        folder_path = research_dir / folder
        folder_path.mkdir(parents=True, exist_ok=True)

    # README.md 생성
    create_readme(research_dir, topic, date_str)

    # 초기 파일 생성
    create_initial_files(research_dir, topic, date_str)

    return research_dir


def create_readme(research_dir: Path, topic: str, date_str: str) -> None:
    """README.md 파일을 생성합니다."""
    readme_content = f"""# {topic}

**연구 시작일**: {date_str}
**워크플로우 버전**: 2.0.0

---

## 프로젝트 구조

```
{research_dir.name}/
├── 00-session/          # 세션 및 워크플로우 관리
├── 01-sources/          # 문헌 및 자료 관리
├── 02-literature-review/ # Phase 1: 문헌검토
├── 03-research-design/  # Phase 2: 연구설계
├── 04-data/             # 연구 데이터
├── 05-drafts/           # Phase 3: 논문 초안
├── 06-final/            # 최종 산출물
├── 07-submission/       # Phase 4: 투고
├── 08-quality/          # 품질 관리
├── 09-references/       # 참고자료 통합 관리
└── 10-archive/          # 아카이브
```

## 폴더 설명

### 00-session
- `session.json`: 워크플로우 상태 및 설정
- `workflow-log.md`: 실행 로그
- `hitl-records/`: HITL 체크포인트 기록

### 01-sources
- `bibliography/`: 참고문헌 데이터베이스
- `primary-sources/`: 1차 자료 (핵심 논문)
- `secondary-sources/`: 2차 자료
- `tertiary-sources/`: 3차 자료
- `web-sources/`: 웹 자료 및 아카이브

### 02-literature-review
Wave 1-5로 구성된 체계적 문헌검토 문서

### 03-research-design
연구 패러다임, 사례 선정, 방법론 프로토콜

### 04-data
연구 데이터 (해당 시)

### 05-drafts
논문 아웃라인 및 장별 초안

### 06-final
최종 논문 및 부록

### 07-submission
학술지 투고 패키지

### 08-quality
SRCS 평가, GRA 검증, 표절 검사, 클레임 레지스트리

### 09-references
통합 참고문헌 관리 및 읽기 노트

### 10-archive
버전 히스토리 및 백업

---

## GRA (Grounded Research Architecture) 준수

모든 문서는 GRA 프레임워크를 준수합니다:
- Layer 1: Self-Verification (자기 검증)
- Layer 2: Cross-Validation (교차 검증)
- Layer 3: External Audit (외부 감사)

## SRCS (Source-Referenced Claim Scoring) 평가

품질 평가 기준:
- CS (Citation Score): 35%
- GS (Grounding Score): 35%
- US (Uncertainty Score): 10%
- VS (Verifiability Score): 20%

임계값: 75/100

---

*이 프로젝트는 Claude Code 기반 박사논문 연구 워크플로우 시스템으로 관리됩니다.*
"""

    readme_path = research_dir / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")


def create_initial_files(research_dir: Path, topic: str, date_str: str) -> None:
    """초기 필수 파일들을 생성합니다."""

    # session.json
    session_data = {
        "version": "2.0.0",
        "created_at": f"{date_str}T00:00:00Z",
        "updated_at": f"{date_str}T00:00:00Z",
        "research": {
            "topic": topic,
            "mode": "topic",
            "type": None,
            "discipline": None,
            "research_questions": [],
            "hypotheses": []
        },
        "workflow": {
            "status": "initialized",
            "current_phase": "phase0",
            "current_step": 0,
            "total_steps": 150,
            "last_checkpoint": None,
            "last_agent": None,
            "phases_completed": []
        },
        "sources": {
            "total_count": 0,
            "primary": 0,
            "secondary": 0,
            "tertiary": 0,
            "web": 0
        },
        "options": {
            "literature_depth": "comprehensive",
            "theoretical_framework": "existing",
            "citation_style": "apa7",
            "language": "korean",
            "thesis_format": "traditional_5chapter"
        },
        "quality": {
            "final_srcs_score": None,
            "final_grade": None,
            "gra_compliance": None,
            "plagiarism_status": None,
            "srcs_scores": [],
            "gra_validations": [],
            "plagiarism_checks": []
        },
        "outputs": {},
        "statistics": {
            "total_agents_executed": 0,
            "total_documents_generated": 0,
            "total_claims": 0,
            "total_references": 0
        }
    }

    session_path = research_dir / "00-session" / "session.json"
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    # workflow-log.md
    workflow_log = f"""# 워크플로우 실행 로그

**연구 주제**: {topic}
**시작일**: {date_str}

---

## 로그

| 시간 | Phase | 에이전트 | 상태 | 비고 |
|------|-------|---------|------|------|
| {date_str}T00:00:00Z | 초기화 | system | 완료 | 폴더 구조 생성 |

"""

    log_path = research_dir / "00-session" / "workflow-log.md"
    log_path.write_text(workflow_log, encoding="utf-8")

    # master-bibliography.md
    bibliography = f"""# 마스터 참고문헌 목록

**연구 주제**: {topic}
**마지막 업데이트**: {date_str}

---

## 1차 자료 (Primary Sources)

*핵심 논문 및 저서*

| 인용키 | 전체 인용 | 유형 | 검증 |
|--------|----------|------|------|

---

## 2차 자료 (Secondary Sources)

*관련 연구 및 리뷰 논문*

| 인용키 | 전체 인용 | 유형 | 검증 |
|--------|----------|------|------|

---

## 3차 자료 (Tertiary Sources)

*백과사전, 교과서, 핸드북*

| 인용키 | 전체 인용 | 유형 | 검증 |
|--------|----------|------|------|

---

## 웹 자료 (Web Sources)

| URL | 접근일 | 아카이브 | 검증 |
|-----|--------|---------|------|

"""

    bib_path = research_dir / "01-sources" / "bibliography" / "master-bibliography.md"
    bib_path.write_text(bibliography, encoding="utf-8")

    # citation-tracker.json
    citation_tracker = {
        "version": "1.0.0",
        "updated_at": f"{date_str}T00:00:00Z",
        "citations": {}
    }

    tracker_path = research_dir / "09-references" / "citation-tracker.json"
    with open(tracker_path, "w", encoding="utf-8") as f:
        json.dump(citation_tracker, f, ensure_ascii=False, indent=2)

    # claims-index.json
    claims_index = {
        "version": "1.0.0",
        "updated_at": f"{date_str}T00:00:00Z",
        "total_claims": 0,
        "claims": []
    }

    claims_path = research_dir / "08-quality" / "claims-registry" / "claims-index.json"
    with open(claims_path, "w", encoding="utf-8") as f:
        json.dump(claims_index, f, ensure_ascii=False, indent=2)

    # reference-master.md
    reference_master = f"""# 참고자료 통합 관리

**연구 주제**: {topic}
**마지막 업데이트**: {date_str}

---

## 개요

이 문서는 연구에 사용된 모든 참고자료를 통합 관리합니다.

## 통계

| 항목 | 수량 |
|------|------|
| 전체 자료 | 0 |
| 1차 자료 | 0 |
| 2차 자료 | 0 |
| 3차 자료 | 0 |
| 웹 자료 | 0 |
| 총 인용 횟수 | 0 |

---

## 핵심 자료 (Most Cited)

*인용 횟수 상위 10개 자료*

| 순위 | 인용키 | 인용 횟수 | 저자 | 연도 |
|------|--------|----------|------|------|

---

## 자료별 인용 위치

*citation-tracker.json 참조*

---

## 출처 검증 상태

| 인용키 | 검증 상태 | 검증일 | 비고 |
|--------|----------|--------|------|

"""

    ref_path = research_dir / "09-references" / "reference-master.md"
    ref_path.write_text(reference_master, encoding="utf-8")

    # source-verification.md
    verification = f"""# 출처 검증 기록

**연구 주제**: {topic}
**마지막 업데이트**: {date_str}

---

## 검증 원칙

1. **1차 자료**: 반드시 원문 확인
2. **2차 자료**: DOI 또는 URL 확인
3. **웹 자료**: 아카이브 보관 권장

## 검증 기록

| 인용키 | 검증일 | 검증자 | 방법 | 결과 | 비고 |
|--------|--------|--------|------|------|------|

"""

    verif_path = research_dir / "09-references" / "source-verification.md"
    verif_path.write_text(verification, encoding="utf-8")


def migrate_old_structure(old_dir: Path, new_dir: Path) -> None:
    """
    기존 폴더 구조의 파일들을 새 구조로 마이그레이션합니다.

    Args:
        old_dir: 기존 연구 폴더
        new_dir: 새 구조의 연구 폴더
    """
    import shutil

    # 매핑 정의: 기존 경로 -> 새 경로
    migration_map = {
        # 세션 파일
        "session.json": "00-session/session.json",
        "todo-checklist.md": "00-session/todo-checklist.md",
        "workflow-completion-report.md": "00-session/workflow-completion-report.md",

        # _temp 문서들 -> 02-literature-review
        "_temp/00-topic-exploration.md": "02-literature-review/00-topic-exploration.md",
        "_temp/01-literature-search-strategy.md": "02-literature-review/wave-1-search/01-literature-search-strategy.md",
        "_temp/02-seminal-works-analysis.md": "02-literature-review/wave-1-search/02-seminal-works-analysis.md",
        "_temp/03-research-trend-analysis.md": "02-literature-review/wave-1-search/03-research-trend-analysis.md",
        "_temp/04-methodology-scan.md": "02-literature-review/wave-1-search/04-methodology-scan.md",
        "_temp/05-theoretical-framework.md": "02-literature-review/wave-2-analysis/05-theoretical-framework.md",
        "_temp/06-empirical-evidence-synthesis.md": "02-literature-review/wave-2-analysis/06-empirical-evidence-synthesis.md",
        "_temp/07-research-gap-analysis.md": "02-literature-review/wave-2-analysis/07-research-gap-analysis.md",
        "_temp/08-variable-relationship-analysis.md": "02-literature-review/wave-2-analysis/08-variable-relationship-analysis.md",
        "_temp/09-critical-review.md": "02-literature-review/wave-3-critique/09-critical-review.md",
        "_temp/10-methodology-critique.md": "02-literature-review/wave-3-critique/10-methodology-critique.md",
        "_temp/11-limitation-analysis.md": "02-literature-review/wave-3-critique/11-limitation-analysis.md",
        "_temp/12-future-research-directions.md": "02-literature-review/wave-3-critique/12-future-research-directions.md",
        "_temp/13-literature-synthesis.md": "02-literature-review/wave-4-synthesis/13-literature-synthesis.md",
        "_temp/14-conceptual-model.md": "02-literature-review/wave-4-synthesis/14-conceptual-model.md",
        "_temp/15-plagiarism-report.md": "02-literature-review/wave-5-quality/15-plagiarism-report.md",

        # 연구설계 -> 03-research-design
        "_temp/20-research-paradigm.md": "03-research-design/20-research-paradigm.md",
        "_temp/21-case-selection.md": "03-research-design/21-case-selection.md",
        "_temp/22-philosophical-method-protocol.md": "03-research-design/22-method-protocol.md",
        "_temp/23-philosophical-analysis-plan.md": "03-research-design/23-analysis-plan.md",
        "_temp/research-design-final.md": "03-research-design/research-design-final.md",
        "_temp/thesis-outline.md": "05-drafts/outline/thesis-outline.md",
        "_temp/journal-recommendation.md": "07-submission/journal-recommendation.md",

        # chapters -> 05-drafts/chapters
        "chapters/chapter-1-introduction.md": "05-drafts/chapters/chapter-1-introduction.md",
        "chapters/chapter-2-literature.md": "05-drafts/chapters/chapter-2-literature.md",
        "chapters/chapter-3-methodology.md": "05-drafts/chapters/chapter-3-methodology.md",
        "chapters/chapter-4-analysis.md": "05-drafts/chapters/chapter-4-analysis.md",
        "chapters/chapter-5-conclusion.md": "05-drafts/chapters/chapter-5-conclusion.md",

        # 최종 산출물 -> 06-final
        "thesis-final.md": "06-final/thesis-final.md",
        "research-synthesis.md": "02-literature-review/research-synthesis.md",

        # 품질 관리 -> 08-quality
        "quality-report.md": "08-quality/srcs-reports/quality-report.md",
        "srcs-summary.json": "08-quality/srcs-reports/srcs-summary.json",

        # 투고 패키지 -> 07-submission/packages
        "submission-package/abstract.md": "07-submission/packages/default/abstract.md",
        "submission-package/keywords.md": "07-submission/packages/default/keywords.md",
        "submission-package/cover-letter.md": "07-submission/packages/default/cover-letter.md",
        "submission-package/title-page.md": "07-submission/packages/default/title-page.md",
        "submission-package/checklist.md": "07-submission/packages/default/checklist.md",
    }

    for old_path, new_path in migration_map.items():
        src = old_dir / old_path
        dst = new_dir / new_path

        if src.exists():
            # 대상 디렉토리 생성
            dst.parent.mkdir(parents=True, exist_ok=True)
            # 파일 복사
            shutil.copy2(src, dst)
            print(f"Migrated: {old_path} -> {new_path}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python create_folder_structure.py <base_dir> <topic>")
        sys.exit(1)

    base_dir = Path(sys.argv[1])
    topic = sys.argv[2]

    research_dir = create_research_folder_structure(base_dir, topic)
    print(f"Created research folder structure at: {research_dir}")
