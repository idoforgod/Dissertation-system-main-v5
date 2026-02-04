#!/usr/bin/env python3
"""
참고문헌 관리 스크립트

연구 문서에서 인용을 추출하고, 참고문헌을 체계적으로 관리합니다.
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Citation:
    """인용 정보를 담는 데이터 클래스"""
    key: str                    # 인용키 (예: list-2019)
    authors: str                # 저자명
    year: str                   # 출판연도
    title: str                  # 제목
    source: str                 # 출처 (저널명, 출판사 등)
    citation_type: str          # 유형 (primary, secondary, tertiary, web)
    full_citation: str          # 전체 인용문
    doi: Optional[str] = None   # DOI
    url: Optional[str] = None   # URL
    verified: bool = False      # 검증 여부
    notes: str = ""             # 노트


@dataclass
class CitationLocation:
    """인용 위치 정보"""
    document: str               # 문서 경로
    line_number: int            # 줄 번호
    context: str                # 주변 문맥


class ReferenceManager:
    """참고문헌 관리 클래스"""

    def __init__(self, research_dir: Path):
        """
        Args:
            research_dir: 연구 폴더 경로
        """
        self.research_dir = research_dir
        self.citations: dict[str, Citation] = {}
        self.locations: dict[str, list[CitationLocation]] = defaultdict(list)

        # 경로 설정
        self.tracker_path = research_dir / "09-references" / "citation-tracker.json"
        self.master_bib_path = research_dir / "01-sources" / "bibliography" / "master-bibliography.md"
        self.reference_master_path = research_dir / "09-references" / "reference-master.md"

        # 기존 데이터 로드
        self._load_existing_data()

    def _load_existing_data(self) -> None:
        """기존 인용 데이터를 로드합니다."""
        if self.tracker_path.exists():
            with open(self.tracker_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for key, citation_data in data.get("citations", {}).items():
                    self.citations[key] = Citation(**{
                        k: v for k, v in citation_data.items()
                        if k in Citation.__dataclass_fields__
                    })
                    for loc in citation_data.get("locations", []):
                        self.locations[key].append(CitationLocation(**loc))

    def extract_citations_from_text(self, text: str) -> list[tuple[str, str]]:
        """
        텍스트에서 인용을 추출합니다.

        Args:
            text: 분석할 텍스트

        Returns:
            (저자, 연도) 튜플 리스트
        """
        # APA 스타일 인용 패턴 (default)
        patterns = [
            # (Author, 2019) - APA / Harvard
            r'\(([A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)*(?:\s+et\s+al\.)?),?\s*(\d{4})\)',
            # Author (2019) - APA / Harvard
            r'([A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)*(?:\s+et\s+al\.)?)\s*\((\d{4})\)',
            # (Author, 2019, p. 42) - APA
            r'\(([A-Z][a-z]+(?:\s+(?:&|and)\s+[A-Z][a-z]+)*(?:\s+et\s+al\.)?),?\s*(\d{4}),\s*p+\.\s*\d+',
            # (Author 42) - MLA (author + page, no year)
            r'\(([A-Z][a-z]+(?:\s+(?:and)\s+[A-Z][a-z]+)*)\s+(\d{1,4})\)',
            # [1] or [1, 2] or [1]-[3] - IEEE (numbered)
            r'\[(\d+(?:\s*[-,]\s*\d+)*)\]',
            # ^1 or ^{1} - Chicago footnote superscript markers
            r'\^(\d+|\{\d+\})',
        ]

        citations = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            citations.extend(matches)

        return citations

    def generate_citation_key(self, author: str, year: str) -> str:
        """
        인용키를 생성합니다.

        Args:
            author: 저자명
            year: 연도

        Returns:
            인용키 (예: list-2019)
        """
        # 첫 번째 저자의 성만 추출
        first_author = author.split("&")[0].split("and")[0].strip()
        first_author = first_author.replace(" et al.", "").strip()

        # 소문자로 변환하고 특수문자 제거
        key = re.sub(r'[^a-z]', '', first_author.lower())

        return f"{key}-{year}"

    def scan_documents(self, folders: Optional[list[str]] = None) -> dict:
        """
        문서들을 스캔하여 인용을 추출합니다.

        Args:
            folders: 스캔할 폴더 목록 (기본: 모든 폴더)

        Returns:
            스캔 결과 통계
        """
        if folders is None:
            folders = [
                "02-literature-review",
                "03-research-design",
                "05-drafts",
                "06-final"
            ]

        stats = {
            "documents_scanned": 0,
            "citations_found": 0,
            "unique_citations": 0,
            "new_citations": 0
        }

        for folder in folders:
            folder_path = self.research_dir / folder
            if not folder_path.exists():
                continue

            for md_file in folder_path.rglob("*.md"):
                stats["documents_scanned"] += 1

                content = md_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    citations = self.extract_citations_from_text(line)

                    for author, year in citations:
                        stats["citations_found"] += 1
                        key = self.generate_citation_key(author, year)

                        # 위치 정보 추가
                        rel_path = md_file.relative_to(self.research_dir)
                        location = CitationLocation(
                            document=str(rel_path),
                            line_number=line_num,
                            context=line[:100]
                        )
                        self.locations[key].append(location)

                        # 새 인용인 경우 추가
                        if key not in self.citations:
                            stats["new_citations"] += 1
                            self.citations[key] = Citation(
                                key=key,
                                authors=author,
                                year=year,
                                title="",  # 나중에 채움
                                source="",
                                citation_type="unknown",
                                full_citation=f"{author} ({year})"
                            )

        stats["unique_citations"] = len(self.citations)
        return stats

    def add_citation(self, citation: Citation) -> None:
        """인용을 추가하거나 업데이트합니다."""
        self.citations[citation.key] = citation

    def save(self) -> None:
        """데이터를 파일로 저장합니다."""
        # citation-tracker.json 저장
        tracker_data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "total_citations": len(self.citations),
            "citations": {}
        }

        for key, citation in self.citations.items():
            citation_dict = asdict(citation)
            citation_dict["locations"] = [
                asdict(loc) for loc in self.locations.get(key, [])
            ]
            citation_dict["citation_count"] = len(self.locations.get(key, []))
            tracker_data["citations"][key] = citation_dict

        self.tracker_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracker_path, "w", encoding="utf-8") as f:
            json.dump(tracker_data, f, ensure_ascii=False, indent=2)

        # master-bibliography.md 업데이트
        self._update_master_bibliography()

        # reference-master.md 업데이트
        self._update_reference_master()

    def _update_master_bibliography(self) -> None:
        """마스터 참고문헌 목록을 업데이트합니다."""
        # 유형별로 분류
        by_type = defaultdict(list)
        for citation in self.citations.values():
            by_type[citation.citation_type].append(citation)

        content = f"""# 마스터 참고문헌 목록

**연구 주제**: {self.research_dir.name.rsplit('-', 1)[0]}
**마지막 업데이트**: {datetime.now().strftime("%Y-%m-%d")}
**총 자료 수**: {len(self.citations)}

---

## 1차 자료 (Primary Sources)

*핵심 논문 및 저서*

| 인용키 | 전체 인용 | 인용 횟수 | 검증 |
|--------|----------|----------|------|
"""

        for c in sorted(by_type.get("primary", []), key=lambda x: x.key):
            count = len(self.locations.get(c.key, []))
            verified = "V" if c.verified else ""
            content += f"| {c.key} | {c.full_citation} | {count} | {verified} |\n"

        content += """
---

## 2차 자료 (Secondary Sources)

*관련 연구 및 리뷰 논문*

| 인용키 | 전체 인용 | 인용 횟수 | 검증 |
|--------|----------|----------|------|
"""

        for c in sorted(by_type.get("secondary", []), key=lambda x: x.key):
            count = len(self.locations.get(c.key, []))
            verified = "V" if c.verified else ""
            content += f"| {c.key} | {c.full_citation} | {count} | {verified} |\n"

        content += """
---

## 3차 자료 (Tertiary Sources)

*백과사전, 교과서, 핸드북*

| 인용키 | 전체 인용 | 인용 횟수 | 검증 |
|--------|----------|----------|------|
"""

        for c in sorted(by_type.get("tertiary", []), key=lambda x: x.key):
            count = len(self.locations.get(c.key, []))
            verified = "V" if c.verified else ""
            content += f"| {c.key} | {c.full_citation} | {count} | {verified} |\n"

        content += """
---

## 미분류 자료

| 인용키 | 전체 인용 | 인용 횟수 |
|--------|----------|----------|
"""

        for c in sorted(by_type.get("unknown", []), key=lambda x: x.key):
            count = len(self.locations.get(c.key, []))
            content += f"| {c.key} | {c.full_citation} | {count} |\n"

        self.master_bib_path.parent.mkdir(parents=True, exist_ok=True)
        self.master_bib_path.write_text(content, encoding="utf-8")

    def _update_reference_master(self) -> None:
        """참고자료 통합 관리 문서를 업데이트합니다."""
        # 인용 횟수 기준 상위 10개
        top_cited = sorted(
            self.citations.values(),
            key=lambda x: len(self.locations.get(x.key, [])),
            reverse=True
        )[:10]

        # 유형별 통계
        type_counts = defaultdict(int)
        for c in self.citations.values():
            type_counts[c.citation_type] += 1

        total_citations = sum(len(locs) for locs in self.locations.values())

        content = f"""# 참고자료 통합 관리

**연구 주제**: {self.research_dir.name.rsplit('-', 1)[0]}
**마지막 업데이트**: {datetime.now().strftime("%Y-%m-%d")}

---

## 개요

이 문서는 연구에 사용된 모든 참고자료를 통합 관리합니다.

## 통계

| 항목 | 수량 |
|------|------|
| 전체 자료 | {len(self.citations)} |
| 1차 자료 | {type_counts.get("primary", 0)} |
| 2차 자료 | {type_counts.get("secondary", 0)} |
| 3차 자료 | {type_counts.get("tertiary", 0)} |
| 미분류 | {type_counts.get("unknown", 0)} |
| 총 인용 횟수 | {total_citations} |

---

## 핵심 자료 (Most Cited)

*인용 횟수 상위 10개 자료*

| 순위 | 인용키 | 인용 횟수 | 저자 | 연도 |
|------|--------|----------|------|------|
"""

        for i, c in enumerate(top_cited, 1):
            count = len(self.locations.get(c.key, []))
            content += f"| {i} | {c.key} | {count} | {c.authors} | {c.year} |\n"

        content += """
---

## 인용 위치 요약

*각 자료가 인용된 문서 목록*

"""

        for key in sorted(self.locations.keys()):
            locations = self.locations[key]
            if not locations:
                continue

            content += f"### {key}\n\n"
            docs = set(loc.document for loc in locations)
            for doc in sorted(docs):
                content += f"- {doc}\n"
            content += "\n"

        content += """---

## 출처 검증 상태

| 인용키 | 검증 상태 | 비고 |
|--------|----------|------|
"""

        for c in sorted(self.citations.values(), key=lambda x: x.key):
            status = "검증됨" if c.verified else "미검증"
            content += f"| {c.key} | {status} | {c.notes} |\n"

        self.reference_master_path.parent.mkdir(parents=True, exist_ok=True)
        self.reference_master_path.write_text(content, encoding="utf-8")

    def get_citation_report(self) -> str:
        """인용 현황 보고서를 생성합니다."""
        total = len(self.citations)
        total_uses = sum(len(locs) for locs in self.locations.values())
        verified = sum(1 for c in self.citations.values() if c.verified)

        report = f"""# 인용 현황 보고서

생성일: {datetime.now().strftime("%Y-%m-%d %H:%M")}

## 요약

- 고유 자료 수: {total}
- 총 인용 횟수: {total_uses}
- 검증된 자료: {verified} ({verified/total*100:.1f}% if total else 0)
- 미검증 자료: {total - verified}

## 유형별 분류

"""
        type_counts = defaultdict(int)
        for c in self.citations.values():
            type_counts[c.citation_type] += 1

        for ctype, count in sorted(type_counts.items()):
            report += f"- {ctype}: {count}\n"

        return report


def main():
    """메인 함수"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python manage_references.py <research_dir> [scan|report]")
        sys.exit(1)

    research_dir = Path(sys.argv[1])
    action = sys.argv[2] if len(sys.argv) > 2 else "scan"

    manager = ReferenceManager(research_dir)

    if action == "scan":
        stats = manager.scan_documents()
        print(f"Scanned {stats['documents_scanned']} documents")
        print(f"Found {stats['citations_found']} citation instances")
        print(f"Unique citations: {stats['unique_citations']}")
        print(f"New citations: {stats['new_citations']}")
        manager.save()
        print("Data saved.")

    elif action == "report":
        print(manager.get_citation_report())

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
