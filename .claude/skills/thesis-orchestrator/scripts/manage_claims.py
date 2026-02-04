#!/usr/bin/env python3
"""
클레임(주장) 관리 스크립트

GRA 프레임워크에 따라 연구 문서의 클레임을 추출하고 관리합니다.
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class Claim:
    """클레임 정보를 담는 데이터 클래스"""
    id: str                     # 클레임 ID (예: C-001)
    document: str               # 문서 경로
    claim_type: str             # 유형 (theoretical, methodological, empirical, normative)
    statement: str              # 주장 내용
    sources: list[str]          # 출처 (인용키 목록)
    confidence: int             # 신뢰도 (0-100)
    uncertainty: str            # 불확실성 표현
    verified: bool = False      # 검증 여부
    verification_method: str = ""  # 검증 방법
    notes: str = ""             # 노트


class ClaimsManager:
    """클레임 관리 클래스"""

    def __init__(self, research_dir: Path):
        """
        Args:
            research_dir: 연구 폴더 경로
        """
        self.research_dir = research_dir
        self.claims: dict[str, Claim] = {}

        # 경로 설정
        self.claims_index_path = research_dir / "08-quality" / "claims-registry" / "claims-index.json"
        self.claims_by_doc_dir = research_dir / "08-quality" / "claims-registry" / "claims-by-document"

        # 기존 데이터 로드
        self._load_existing_data()

    def _load_existing_data(self) -> None:
        """기존 클레임 데이터를 로드합니다."""
        if self.claims_index_path.exists():
            with open(self.claims_index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for claim_data in data.get("claims", []):
                    claim = Claim(**{
                        k: v for k, v in claim_data.items()
                        if k in Claim.__dataclass_fields__
                    })
                    self.claims[claim.id] = claim

    def extract_claims_from_document(self, doc_path: Path) -> list[Claim]:
        """
        문서에서 클레임을 추출합니다.

        Args:
            doc_path: 문서 경로

        Returns:
            추출된 클레임 리스트
        """
        content = doc_path.read_text(encoding="utf-8")
        extracted_claims = []

        # Claims 섹션 찾기
        claims_section_pattern = r'##\s*Claims\s+Section.*?(?=\n##\s|$)'
        claims_section_match = re.search(claims_section_pattern, content, re.DOTALL | re.IGNORECASE)

        if not claims_section_match:
            # 대안 패턴
            claims_section_pattern = r'##\s*(?:\d+\.\s*)?Claims.*?(?=\n##\s|$)'
            claims_section_match = re.search(claims_section_pattern, content, re.DOTALL | re.IGNORECASE)

        if not claims_section_match:
            return extracted_claims

        claims_text = claims_section_match.group(0)

        # 개별 클레임 추출
        claim_pattern = r'###\s*Claim\s+([A-Z]?\d*-?\d+).*?(?=###\s*Claim|$)'
        claim_matches = re.finditer(claim_pattern, claims_text, re.DOTALL | re.IGNORECASE)

        rel_path = str(doc_path.relative_to(self.research_dir))

        for match in claim_matches:
            claim_text = match.group(0)
            claim_id = match.group(1)

            # 필드 추출
            claim_type = self._extract_field(claim_text, r'Type[:\s]+([^\n]+)')
            statement = self._extract_field(claim_text, r'Statement[:\s]+([^\n]+)')
            sources_str = self._extract_field(claim_text, r'Sources?[:\s]+([^\n]+)')
            confidence_str = self._extract_field(claim_text, r'Confidence[:\s]+(\d+)')
            uncertainty = self._extract_field(claim_text, r'Uncertainty[:\s]+([^\n]+)')

            # sources 파싱
            sources = []
            if sources_str:
                # 다양한 형식 처리: "List(2019), Dennett(2003)" 또는 "list-2019, dennett-2003"
                sources = re.findall(r'[A-Za-z]+-?\d{4}|[A-Z][a-z]+\s*\(\d{4}\)', sources_str)

            # confidence 파싱
            confidence = int(confidence_str) if confidence_str else 0

            claim = Claim(
                id=f"{rel_path}:{claim_id}",
                document=rel_path,
                claim_type=claim_type or "unknown",
                statement=statement or "",
                sources=sources,
                confidence=confidence,
                uncertainty=uncertainty or ""
            )

            extracted_claims.append(claim)

        return extracted_claims

    def _extract_field(self, text: str, pattern: str) -> Optional[str]:
        """텍스트에서 특정 필드를 추출합니다."""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def scan_documents(self, folders: Optional[list[str]] = None) -> dict:
        """
        문서들을 스캔하여 클레임을 추출합니다.

        Args:
            folders: 스캔할 폴더 목록

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
            "documents_with_claims": 0,
            "total_claims": 0,
            "new_claims": 0,
            "claims_by_type": defaultdict(int)
        }

        for folder in folders:
            folder_path = self.research_dir / folder
            if not folder_path.exists():
                continue

            for md_file in folder_path.rglob("*.md"):
                stats["documents_scanned"] += 1

                claims = self.extract_claims_from_document(md_file)

                if claims:
                    stats["documents_with_claims"] += 1

                for claim in claims:
                    stats["total_claims"] += 1
                    stats["claims_by_type"][claim.claim_type] += 1

                    if claim.id not in self.claims:
                        stats["new_claims"] += 1
                        self.claims[claim.id] = claim
                    else:
                        # 기존 클레임 업데이트 (내용이 변경된 경우)
                        self.claims[claim.id] = claim

        return stats

    def save(self) -> None:
        """데이터를 파일로 저장합니다."""
        # claims-index.json 저장
        claims_list = [asdict(c) for c in self.claims.values()]

        # 통계 계산
        type_counts = defaultdict(int)
        verified_count = 0
        for c in self.claims.values():
            type_counts[c.claim_type] += 1
            if c.verified:
                verified_count += 1

        index_data = {
            "version": "1.0.0",
            "updated_at": datetime.now().isoformat(),
            "total_claims": len(self.claims),
            "verified_claims": verified_count,
            "claims_by_type": dict(type_counts),
            "claims": claims_list
        }

        self.claims_index_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.claims_index_path, "w", encoding="utf-8") as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

        # 문서별 클레임 저장
        self._save_claims_by_document()

    def _save_claims_by_document(self) -> None:
        """문서별로 클레임을 저장합니다."""
        # 문서별로 클레임 그룹화
        by_document = defaultdict(list)
        for claim in self.claims.values():
            by_document[claim.document].append(claim)

        self.claims_by_doc_dir.mkdir(parents=True, exist_ok=True)

        for doc_path, claims in by_document.items():
            # 파일명 생성 (경로의 /를 _로 대체)
            filename = doc_path.replace("/", "_").replace(".md", "") + "-claims.json"
            filepath = self.claims_by_doc_dir / filename

            doc_data = {
                "document": doc_path,
                "updated_at": datetime.now().isoformat(),
                "total_claims": len(claims),
                "claims": [asdict(c) for c in claims]
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(doc_data, f, ensure_ascii=False, indent=2)

    def generate_claims_report(self) -> str:
        """클레임 현황 보고서를 생성합니다."""
        # 통계 계산
        type_counts = defaultdict(int)
        confidence_sum = 0
        verified_count = 0
        unverified_sources = []

        for claim in self.claims.values():
            type_counts[claim.claim_type] += 1
            confidence_sum += claim.confidence
            if claim.verified:
                verified_count += 1
            if not claim.sources:
                unverified_sources.append(claim.id)

        avg_confidence = confidence_sum / len(self.claims) if self.claims else 0

        report = f"""# 클레임 현황 보고서

**생성일**: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 요약

| 항목 | 값 |
|------|-----|
| 총 클레임 수 | {len(self.claims)} |
| 검증된 클레임 | {verified_count} ({verified_count/len(self.claims)*100:.1f}% if self.claims else 0) |
| 평균 신뢰도 | {avg_confidence:.1f}/100 |

---

## 유형별 분류

| 유형 | 수량 | 비율 |
|------|------|------|
"""

        for ctype, count in sorted(type_counts.items()):
            pct = count / len(self.claims) * 100 if self.claims else 0
            report += f"| {ctype} | {count} | {pct:.1f}% |\n"

        report += """
---

## 신뢰도 분포

| 범위 | 수량 |
|------|------|
"""

        confidence_ranges = [(90, 100), (80, 89), (70, 79), (60, 69), (0, 59)]
        for low, high in confidence_ranges:
            count = sum(1 for c in self.claims.values() if low <= c.confidence <= high)
            report += f"| {low}-{high} | {count} |\n"

        if unverified_sources:
            report += f"""
---

## 출처 없는 클레임 ({len(unverified_sources)}개)

다음 클레임들은 출처가 명시되지 않았습니다:

"""
            for claim_id in unverified_sources[:10]:
                claim = self.claims[claim_id]
                report += f"- **{claim_id}**: {claim.statement[:50]}...\n"

            if len(unverified_sources) > 10:
                report += f"\n... 외 {len(unverified_sources) - 10}개\n"

        return report

    def get_claims_by_type(self, claim_type: str) -> list[Claim]:
        """특정 유형의 클레임을 반환합니다."""
        return [c for c in self.claims.values() if c.claim_type == claim_type]

    def get_claims_by_source(self, source_key: str) -> list[Claim]:
        """특정 출처를 인용한 클레임을 반환합니다."""
        return [c for c in self.claims.values() if source_key in c.sources]


def main():
    """메인 함수"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python manage_claims.py <research_dir> [scan|report]")
        sys.exit(1)

    research_dir = Path(sys.argv[1])
    action = sys.argv[2] if len(sys.argv) > 2 else "scan"

    manager = ClaimsManager(research_dir)

    if action == "scan":
        stats = manager.scan_documents()
        print(f"Scanned {stats['documents_scanned']} documents")
        print(f"Documents with claims: {stats['documents_with_claims']}")
        print(f"Total claims: {stats['total_claims']}")
        print(f"New claims: {stats['new_claims']}")
        print(f"Claims by type: {dict(stats['claims_by_type'])}")
        manager.save()
        print("Data saved.")

    elif action == "report":
        print(manager.generate_claims_report())

    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()
