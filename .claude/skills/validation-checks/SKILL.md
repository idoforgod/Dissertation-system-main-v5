---
name: validation-checks
description: GRA 준수 검증 및 pTCS 점수 자동 계산. 연구 제안서와 논문의 품질 보증을 위한 자동화된 검증 도구를 제공합니다.
---

# Validation Checks Skill

**목적**: 연구 품질 보증을 위한 자동화된 검증 시스템

이 Skill은 proposal-integrator agent 및 품질 검증 작업에서 사용됩니다.

---

## 주요 기능

### 1. GRA (GroundedClaim) 준수 검증

**GRA Framework**: 모든 주장(claim)은 출처(source)로 근거되어야 함

#### 1-1. 인용 검증 (Citation Verification)

```python
def verify_gra_compliance(text):
    """
    Check if all claims are properly cited

    Returns:
        dict: GRA compliance report
    """
    import re

    # 1. 주장 문장 탐지 (Claim detection)
    claim_patterns = [
        r'(Previous research|Studies|Researchers) (found|showed|demonstrated|indicated)',
        r'(It has been|It is) (shown|found|demonstrated) that',
        r'(Evidence suggests|Research indicates)',
        r'(.*) found that',
        r'According to (.*),',
    ]

    claims = []
    for pattern in claim_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            claims.append({
                "text": match.group(0),
                "position": match.start()
            })

    # 2. 인용 탐지 (Citation detection)
    citation_patterns = [
        r'\(([A-Z][a-z]+(?:,? (?:&|and) [A-Z][a-z]+)*,? \d{4}[a-z]?)\)',  # APA in-text
        r'\[(\d+(?:,\s*\d+)*)\]',  # Numbered
    ]

    citations = []
    for pattern in citation_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            citations.append({
                "citation": match.group(0),
                "position": match.start()
            })

    # 3. 매칭 검증 (Match claims with citations)
    uncited_claims = []
    for claim in claims:
        # 주장 후 50자 이내에 인용이 있는지 확인
        claim_pos = claim["position"]
        has_citation = any(
            claim_pos < cit["position"] < claim_pos + 50
            for cit in citations
        )
        if not has_citation:
            uncited_claims.append(claim["text"])

    # 4. GRA Compliance Score
    total_claims = len(claims)
    cited_claims = total_claims - len(uncited_claims)
    gra_score = (cited_claims / total_claims * 100) if total_claims > 0 else 0

    return {
        "total_claims": total_claims,
        "cited_claims": cited_claims,
        "uncited_claims": uncited_claims,
        "gra_compliance_score": gra_score,
        "status": "PASS" if gra_score >= 95 else "FAIL",
        "threshold": 95.0
    }
```

#### 1-2. 인용 형식 검증 (Citation Format Check)

```python
def check_citation_format(text, style="APA"):
    """
    Verify citation format consistency.

    Supports multiple citation styles: APA, Chicago, MLA, Harvard, IEEE.
    Style is read from session.json options.citation_style field.

    Args:
        text: Document text
        style: "APA" | "Chicago" | "MLA" | "Harvard" | "IEEE"

    Returns:
        dict: Format validation report
    """
    import re

    errors = []

    if style in ("APA", "apa7"):
        # APA 7th edition patterns
        # Check for common errors
        # 1. Missing comma before year
        wrong_pattern = r'\([A-Z][a-z]+ \d{4}\)'
        matches = re.finditer(wrong_pattern, text)
        for match in matches:
            errors.append({
                "type": "Missing comma before year",
                "found": match.group(0),
                "position": match.start(),
                "correction": "Add comma: (Author, Year)"
            })

        # 2. Wrong ampersand usage (APA uses & in parenthetical)
        wrong_and = r'\([A-Z][a-z]+ and [A-Z][a-z]+, \d{4}\)'
        matches = re.finditer(wrong_and, text)
        for match in matches:
            errors.append({
                "type": "Use '&' not 'and' in parenthetical citation",
                "found": match.group(0),
                "position": match.start(),
                "correction": "Use & instead of 'and'"
            })

    elif style in ("Chicago", "chicago17"):
        # Chicago 17th edition (footnote style)
        # Check for footnote markers
        footnote_pattern = r'\^\d+'
        footnotes = re.findall(footnote_pattern, text)
        if len(footnotes) == 0:
            errors.append({
                "type": "No footnote markers found",
                "found": "N/A",
                "position": 0,
                "correction": "Chicago style requires footnote markers (^1, ^2, etc.)"
            })

    elif style in ("MLA", "mla9"):
        # MLA 9th edition (Author Page)
        # Check for wrong format: (Author, Year) instead of (Author Page)
        wrong_mla = r'\([A-Z][a-z]+, \d{4}\)'
        matches = re.finditer(wrong_mla, text)
        for match in matches:
            errors.append({
                "type": "MLA uses (Author Page), not (Author, Year)",
                "found": match.group(0),
                "position": match.start(),
                "correction": "Use (Author Page) format, e.g., (Smith 42)"
            })

    elif style in ("Harvard", "harvard"):
        # Harvard (Author Year) - similar to APA but no comma
        # Check for comma between author and year (APA style in Harvard)
        wrong_harvard = r'\([A-Z][a-z]+, \d{4}\)'
        matches = re.finditer(wrong_harvard, text)
        for match in matches:
            errors.append({
                "type": "Harvard uses (Author Year), not (Author, Year)",
                "found": match.group(0),
                "position": match.start(),
                "correction": "Remove comma: (Author Year)"
            })

    elif style in ("IEEE", "ieee"):
        # IEEE uses numbered references [1], [2], etc.
        bracket_refs = re.findall(r'\[\d+\]', text)
        if len(bracket_refs) == 0:
            errors.append({
                "type": "No numbered references found",
                "found": "N/A",
                "position": 0,
                "correction": "IEEE style requires numbered references [1], [2], etc."
            })

    return {
        "style": style,
        "errors_found": len(errors),
        "errors": errors,
        "status": "PASS" if len(errors) == 0 else "FAIL"
    }
```

#### 1-3. 참고문헌 일치 검증 (Reference Matching)

```python
def verify_reference_completeness(text, references_section):
    """
    Check if all in-text citations appear in reference list

    Returns:
        dict: Reference completeness report
    """
    import re

    # 1. Extract in-text citations
    in_text_pattern = r'\(([A-Z][a-z]+(?:,? (?:&|and|et al\.) [A-Z][a-z]+)*, \d{4}[a-b]?)\)'
    in_text_citations = set(re.findall(in_text_pattern, text))

    # 2. Extract reference list entries
    ref_pattern = r'^([A-Z][a-z]+,.*?\(\d{4}\))'
    reference_entries = set(re.findall(ref_pattern, references_section, re.MULTILINE))

    # 3. Match
    missing_in_references = []
    for citation in in_text_citations:
        # Simple matching (can be improved)
        author_year = citation.strip()
        if not any(author_year in ref for ref in reference_entries):
            missing_in_references.append(citation)

    # 4. Report
    return {
        "total_in_text_citations": len(in_text_citations),
        "total_reference_entries": len(reference_entries),
        "missing_in_references": missing_in_references,
        "completeness_score": (1 - len(missing_in_references) / len(in_text_citations)) * 100 if len(in_text_citations) > 0 else 100,
        "status": "PASS" if len(missing_in_references) == 0 else "WARNING"
    }
```

---

### 2. pTCS (Probabilistic Truth-Claim Score) 계산

**pTCS Framework**: 각 주장의 진실성 확률을 정량화

#### 2-1. pTCS 점수 계산 알고리즘

```python
def calculate_ptcs(claim, evidence):
    """
    Calculate Probabilistic Truth-Claim Score

    Args:
        claim: Research claim statement
        evidence: Supporting evidence with metadata

    Returns:
        dict: pTCS score and breakdown
    """

    # Evidence Quality Scoring (0-1)
    def score_evidence_quality(evidence):
        scores = {
            "peer_reviewed": 1.0 if evidence.get("peer_reviewed") else 0.5,
            "sample_size": min(evidence.get("sample_size", 0) / 1000, 1.0),
            "effect_size": _map_effect_size(evidence.get("effect_size")),
            "p_value": _map_p_value(evidence.get("p_value")),
            "replication": 1.0 if evidence.get("replicated") else 0.7,
        }
        return sum(scores.values()) / len(scores)

    def _map_effect_size(es):
        if es is None:
            return 0.5
        if es >= 0.8:  # Large
            return 1.0
        elif es >= 0.5:  # Medium
            return 0.8
        elif es >= 0.2:  # Small
            return 0.6
        else:
            return 0.4

    def _map_p_value(p):
        if p is None:
            return 0.5
        if p < 0.001:
            return 1.0
        elif p < 0.01:
            return 0.9
        elif p < 0.05:
            return 0.8
        else:
            return 0.5

    # Source Credibility (0-1)
    def score_source_credibility(evidence):
        journal_tier = evidence.get("journal_tier", "unknown")
        tier_scores = {
            "A+": 1.0,  # Top 5% journals (e.g., Nature, Science)
            "A": 0.9,   # Top 10%
            "B": 0.8,   # Reputable
            "C": 0.6,   # Lower tier
            "unknown": 0.5
        }

        citation_count = evidence.get("citation_count", 0)
        citation_score = min(citation_count / 100, 1.0)

        return (tier_scores[journal_tier] + citation_score) / 2

    # Convergence Score (multiple sources) (0-1)
    def score_convergence(evidence_list):
        if len(evidence_list) == 1:
            return 0.7  # Single source penalty
        elif len(evidence_list) >= 3:
            return 1.0  # Strong convergence
        else:
            return 0.85  # Moderate convergence

    # Calculate individual scores
    evidence_quality = score_evidence_quality(evidence)
    source_credibility = score_source_credibility(evidence)
    convergence = score_convergence([evidence])  # Simplified: assumes single evidence

    # Weighted combination
    weights = {
        "evidence_quality": 0.4,
        "source_credibility": 0.3,
        "convergence": 0.3
    }

    ptcs_score = (
        evidence_quality * weights["evidence_quality"] +
        source_credibility * weights["source_credibility"] +
        convergence * weights["convergence"]
    )

    # Confidence interval
    # Based on sample size and replication
    n = evidence.get("sample_size", 100)
    replicated = evidence.get("replicated", False)

    se = 1.96 / (n ** 0.5)  # Simplified SE
    if replicated:
        se *= 0.7  # Reduce uncertainty

    ci_lower = max(0, ptcs_score - se)
    ci_upper = min(1, ptcs_score + se)

    return {
        "claim": claim,
        "ptcs_score": round(ptcs_score, 3),
        "confidence_interval": [round(ci_lower, 3), round(ci_upper, 3)],
        "breakdown": {
            "evidence_quality": round(evidence_quality, 3),
            "source_credibility": round(source_credibility, 3),
            "convergence": round(convergence, 3)
        },
        "rating": _get_rating(ptcs_score),
        "interpretation": _interpret_score(ptcs_score)
    }

def _get_rating(score):
    if score >= 0.8:
        return "High Confidence"
    elif score >= 0.6:
        return "Moderate Confidence"
    elif score >= 0.4:
        return "Low Confidence"
    else:
        return "Very Low Confidence"

def _interpret_score(score):
    if score >= 0.8:
        return "Strong empirical support. Claim is highly credible."
    elif score >= 0.6:
        return "Reasonable support. Claim is plausible but needs more evidence."
    elif score >= 0.4:
        return "Weak support. Claim needs substantial additional evidence."
    else:
        return "Insufficient support. Claim should be qualified or removed."
```

#### 2-2. Batch pTCS Calculation

```python
def calculate_document_ptcs(document):
    """
    Calculate pTCS for all claims in a document

    Args:
        document: Dict with claims and evidence

    Returns:
        dict: Aggregate pTCS report
    """
    claims = document.get("claims", [])

    results = []
    for claim_data in claims:
        claim = claim_data["claim"]
        evidence = claim_data["evidence"]

        ptcs = calculate_ptcs(claim, evidence)
        results.append(ptcs)

    # Aggregate statistics
    scores = [r["ptcs_score"] for r in results]
    avg_score = sum(scores) / len(scores) if scores else 0

    distribution = {
        "high (≥0.8)": sum(1 for s in scores if s >= 0.8),
        "moderate (0.6-0.8)": sum(1 for s in scores if 0.6 <= s < 0.8),
        "low (0.4-0.6)": sum(1 for s in scores if 0.4 <= s < 0.6),
        "very_low (<0.4)": sum(1 for s in scores if s < 0.4)
    }

    return {
        "total_claims": len(claims),
        "average_ptcs": round(avg_score, 3),
        "distribution": distribution,
        "detailed_results": results,
        "overall_rating": _get_rating(avg_score),
        "recommendations": _generate_recommendations(results)
    }

def _generate_recommendations(results):
    recommendations = []

    low_confidence = [r for r in results if r["ptcs_score"] < 0.6]
    if low_confidence:
        recommendations.append({
            "priority": "HIGH",
            "issue": f"{len(low_confidence)} claims have low confidence scores",
            "action": "Strengthen evidence or qualify claims"
        })

    uncited = [r for r in results if r["breakdown"]["convergence"] < 0.8]
    if uncited:
        recommendations.append({
            "priority": "MEDIUM",
            "issue": f"{len(uncited)} claims lack convergent evidence",
            "action": "Add additional supporting citations"
        })

    return recommendations
```

---

### 3. 통합 품질 검증 (Integrated Quality Check)

```python
def run_full_validation(document_path):
    """
    Run complete validation suite

    Returns:
        dict: Comprehensive validation report
    """
    import json

    # 1. Read document
    with open(document_path, 'r') as f:
        document = json.load(f)

    text = document.get("text", "")
    references = document.get("references", "")

    # 2. Run all checks
    gra_report = verify_gra_compliance(text)
    # Read citation style from session.json if available, default to APA
    citation_style = session_options.get("citation_style", "apa7") if session_options else "apa7"
    format_report = check_citation_format(text, style=citation_style)
    reference_report = verify_reference_completeness(text, references)
    ptcs_report = calculate_document_ptcs(document)

    # 3. Overall Quality Score
    quality_components = {
        "gra_compliance": gra_report["gra_compliance_score"] / 100,
        "citation_format": 1.0 if format_report["status"] == "PASS" else 0.7,
        "reference_completeness": reference_report["completeness_score"] / 100,
        "ptcs_average": ptcs_report["average_ptcs"]
    }

    overall_quality = sum(quality_components.values()) / len(quality_components)

    # 4. Pass/Fail Determination
    passing_criteria = {
        "gra_compliance": gra_report["gra_compliance_score"] >= 95,
        "citation_format": format_report["status"] == "PASS",
        "reference_completeness": reference_report["completeness_score"] >= 95,
        "ptcs_threshold": ptcs_report["average_ptcs"] >= 0.6
    }

    all_passed = all(passing_criteria.values())

    return {
        "document": document_path,
        "timestamp": "2026-01-28",
        "overall_quality_score": round(overall_quality, 3),
        "overall_status": "PASS" if all_passed else "FAIL",
        "component_scores": quality_components,
        "passing_criteria": passing_criteria,
        "detailed_reports": {
            "gra_compliance": gra_report,
            "citation_format": format_report,
            "reference_completeness": reference_report,
            "ptcs_analysis": ptcs_report
        },
        "critical_issues": _extract_critical_issues(gra_report, format_report, reference_report, ptcs_report),
        "recommendations": _compile_all_recommendations(gra_report, format_report, reference_report, ptcs_report)
    }

def _extract_critical_issues(gra, format_check, ref_check, ptcs):
    issues = []

    if gra["gra_compliance_score"] < 95:
        issues.append({
            "severity": "CRITICAL",
            "category": "GRA Compliance",
            "description": f"{len(gra['uncited_claims'])} claims lack proper citations"
        })

    if ptcs["average_ptcs"] < 0.6:
        issues.append({
            "severity": "HIGH",
            "category": "Evidence Quality",
            "description": "Average pTCS below threshold (0.6)"
        })

    return issues

def _compile_all_recommendations(gra, format_check, ref_check, ptcs):
    recommendations = []

    # From GRA
    if gra["uncited_claims"]:
        recommendations.append("Add citations for uncited claims")

    # From format check
    if format_check["errors_found"] > 0:
        recommendations.append("Fix citation format errors")

    # From reference check
    if ref_check["missing_in_references"]:
        recommendations.append("Add missing references to reference list")

    # From pTCS
    recommendations.extend([rec["action"] for rec in ptcs.get("recommendations", [])])

    return recommendations
```

---

## 품질 기준 (Quality Standards)

### Acceptance Criteria

```yaml
quality_standards:
  gra_compliance:
    threshold: 95%
    description: "At least 95% of claims must have citations"
    severity: "CRITICAL"

  citation_format:
    errors_allowed: 0
    description: "All citations must follow APA 7th format"
    severity: "HIGH"

  reference_completeness:
    threshold: 95%
    description: "At least 95% of in-text citations must appear in references"
    severity: "HIGH"

  ptcs_average:
    threshold: 0.6
    description: "Average pTCS score must be ≥ 0.6"
    severity: "HIGH"

  overall_quality:
    threshold: 0.75
    description: "Overall quality score must be ≥ 0.75"
    severity: "MEDIUM"
```

---

## 사용 예시 (Usage Examples)

### Example 1: 단일 주장 검증

```python
from skills.validation_checks import calculate_ptcs

# 주장과 증거
claim = "Transformational leadership positively affects employee creativity"
evidence = {
    "peer_reviewed": True,
    "sample_size": 250,
    "effect_size": 0.45,  # Medium
    "p_value": 0.001,
    "replicated": True,
    "journal_tier": "A",
    "citation_count": 85
}

# pTCS 계산
result = calculate_ptcs(claim, evidence)

print(f"Claim: {result['claim']}")
print(f"pTCS Score: {result['ptcs_score']}")
print(f"Rating: {result['rating']}")
print(f"Interpretation: {result['interpretation']}")
```

### Example 2: 문서 전체 검증

```python
from skills.validation_checks import run_full_validation

# 전체 검증 실행
report = run_full_validation("thesis-output/proposal.json")

# 결과 출력
print(f"Overall Quality: {report['overall_quality_score']}")
print(f"Status: {report['overall_status']}")

# 문제점 확인
if report['critical_issues']:
    print("\nCritical Issues:")
    for issue in report['critical_issues']:
        print(f"  - [{issue['severity']}] {issue['description']}")

# 권장사항 확인
print("\nRecommendations:")
for rec in report['recommendations']:
    print(f"  - {rec}")
```

### Example 3: GRA만 빠르게 검증

```python
from skills.validation_checks import verify_gra_compliance

# 텍스트 읽기
with open("chapter-2.md", "r") as f:
    text = f.read()

# GRA 검증
gra_report = verify_gra_compliance(text)

if gra_report["status"] == "FAIL":
    print(f"GRA Compliance: {gra_report['gra_compliance_score']:.1f}%")
    print(f"Uncited claims: {len(gra_report['uncited_claims'])}")
    for claim in gra_report['uncited_claims'][:5]:  # Show first 5
        print(f"  - {claim}")
```

---

## 자동화 스크립트 (Automation Scripts)

### validate_proposal.py

**파일**: `scripts/validate_proposal.py`

```python
#!/usr/bin/env python3
"""
연구 제안서 자동 검증 스크립트

Usage:
    python validate_proposal.py <proposal_file> [--output report.json]
"""
import sys
import json
import argparse
from pathlib import Path

# Import validation functions
from skills.validation_checks import run_full_validation

def main():
    parser = argparse.ArgumentParser(description="Validate research proposal")
    parser.add_argument("proposal_file", help="Path to proposal JSON file")
    parser.add_argument("--output", default="validation-report.json", help="Output report file")
    parser.add_argument("--strict", action="store_true", help="Strict mode (fail on warnings)")

    args = parser.parse_args()

    # Check file exists
    if not Path(args.proposal_file).exists():
        print(f"Error: File not found: {args.proposal_file}")
        sys.exit(1)

    print(f"Validating: {args.proposal_file}")
    print("=" * 60)

    # Run validation
    report = run_full_validation(args.proposal_file)

    # Display summary
    print(f"\n📊 Validation Results")
    print(f"Overall Quality Score: {report['overall_quality_score']:.3f}")
    print(f"Status: {report['overall_status']}")

    # Component scores
    print(f"\n📈 Component Scores:")
    for component, score in report['component_scores'].items():
        status = "✅" if report['passing_criteria'][component] else "❌"
        print(f"  {status} {component}: {score:.3f}")

    # Critical issues
    if report['critical_issues']:
        print(f"\n⚠️  Critical Issues ({len(report['critical_issues'])}):")
        for issue in report['critical_issues']:
            print(f"  - [{issue['severity']}] {issue['description']}")

    # Recommendations
    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations'][:10]:  # Limit to 10
            print(f"  - {rec}")

    # Save report
    with open(args.output, 'w') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\n📄 Full report saved to: {args.output}")

    # Exit code
    if report['overall_status'] == "FAIL":
        print("\n❌ Validation FAILED")
        sys.exit(1)
    else:
        print("\n✅ Validation PASSED")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

---

## 사용하는 Agents

이 Skill을 사용하는 agents:
- `proposal-integrator` (Stage 6) - 주요 사용자
- `thesis-writer` (Phase 3) - 논문 작성 중 검증
- `plagiarism-checker` (Wave 5) - 인용 검증

---

## 버전 히스토리

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-28 | Initial release |

---

**작성자**: Claude Code
**상태**: ✅ Ready for use
