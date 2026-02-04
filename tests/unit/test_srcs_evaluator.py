"""
SRCS Evaluator Tests (TDD)
통합 SRCS 평가 시스템 테스트
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))


class TestClaimTypeClassification:
    """클레임 유형별 분류 테스트"""

    def test_classify_factual_claim(self):
        """사실적 클레임 분류"""
        from srcs_evaluator import classify_claim_type

        claim = {"text": "The sample size was 500 participants", "claim_type": "FACTUAL"}
        result = classify_claim_type(claim)
        assert result == "FACTUAL"

    def test_classify_empirical_claim(self):
        """실증적 클레임 분류"""
        from srcs_evaluator import classify_claim_type

        claim = {"text": "The effect size was d=0.45", "claim_type": "EMPIRICAL"}
        result = classify_claim_type(claim)
        assert result == "EMPIRICAL"

    def test_classify_theoretical_claim(self):
        """이론적 클레임 분류"""
        from srcs_evaluator import classify_claim_type

        claim = {"text": "According to social exchange theory", "claim_type": "THEORETICAL"}
        result = classify_claim_type(claim)
        assert result == "THEORETICAL"

    def test_auto_classify_from_text(self):
        """텍스트에서 자동 분류"""
        from srcs_evaluator import classify_claim_type

        claim = {"text": "According to social exchange theory, relationships are based on exchange"}
        result = classify_claim_type(claim)
        assert result == "THEORETICAL"


class TestSRCSCalculation:
    """SRCS 4축 점수 계산 테스트"""

    def test_calculate_cs_with_primary_source(self):
        """1차 출처 기반 CS 점수"""
        from srcs_evaluator import calculate_citation_score

        claim = {
            "sources": [
                {"type": "PRIMARY", "reference": "Author (2020)", "verified": True}
            ]
        }
        score = calculate_citation_score(claim)
        assert score >= 80

    def test_calculate_cs_no_sources(self):
        """출처 없는 클레임 CS 점수"""
        from srcs_evaluator import calculate_citation_score

        claim = {"sources": []}
        score = calculate_citation_score(claim)
        assert score == 0

    def test_calculate_gs_with_evidence(self):
        """근거 있는 GS 점수"""
        from srcs_evaluator import calculate_grounding_score

        claim = {
            "text": "The correlation was r=0.45 (p<0.01)",
            "sources": [{"type": "PRIMARY", "reference": "Study (2020)"}],
        }
        score = calculate_grounding_score(claim)
        assert score >= 70

    def test_calculate_us_with_uncertainty(self):
        """불확실성 표현 US 점수"""
        from srcs_evaluator import calculate_uncertainty_score

        claim = {
            "text": "Research suggests a possible relationship",
            "uncertainty": "Limited to Western contexts",
        }
        score = calculate_uncertainty_score(claim)
        assert score >= 70

    def test_calculate_vs_with_doi(self):
        """DOI 포함 VS 점수"""
        from srcs_evaluator import calculate_verifiability_score

        claim = {
            "sources": [
                {"reference": "Author (2020)", "doi": "10.1000/xyz123", "verified": True}
            ]
        }
        score = calculate_verifiability_score(claim)
        assert score >= 90


class TestWeightedSRCS:
    """가중치 적용 SRCS 점수 테스트"""

    def test_calculate_weighted_srcs(self):
        """가중치 적용 종합 점수"""
        from srcs_evaluator import calculate_weighted_srcs

        scores = {"cs": 85, "gs": 80, "us": 90, "vs": 75}
        # 가중치: CS=0.35, GS=0.35, US=0.10, VS=0.20
        weighted = calculate_weighted_srcs(scores)
        expected = 85 * 0.35 + 80 * 0.35 + 90 * 0.10 + 75 * 0.20
        assert abs(weighted - expected) < 0.1

    def test_srcs_threshold_pass(self):
        """임계값 통과 확인"""
        from srcs_evaluator import check_threshold

        scores = {"cs": 85, "gs": 80, "us": 90, "vs": 75}
        result = check_threshold(scores, threshold=75)
        assert result["passed"] is True

    def test_srcs_threshold_fail(self):
        """임계값 미달 확인"""
        from srcs_evaluator import check_threshold

        scores = {"cs": 50, "gs": 60, "us": 70, "vs": 55}
        result = check_threshold(scores, threshold=75)
        assert result["passed"] is False


class TestBulkEvaluation:
    """대량 클레임 평가 테스트"""

    def test_evaluate_all_claims(self):
        """전체 클레임 평가"""
        from srcs_evaluator import evaluate_all_claims

        claims = [
            {
                "id": "C-001",
                "text": "Claim 1",
                "claim_type": "FACTUAL",
                "sources": [{"type": "PRIMARY", "reference": "A (2020)", "verified": True}],
                "confidence": 85,
            },
            {
                "id": "C-002",
                "text": "Claim 2",
                "claim_type": "EMPIRICAL",
                "sources": [{"type": "PRIMARY", "reference": "B (2021)", "verified": True}],
                "confidence": 90,
            },
        ]

        result = evaluate_all_claims(claims)
        assert len(result["evaluated_claims"]) == 2
        assert "overall_scores" in result

    def test_identify_below_threshold(self):
        """임계값 미달 클레임 식별"""
        from srcs_evaluator import evaluate_all_claims

        claims = [
            {
                "id": "C-001",
                "text": "Good claim with evidence r=0.45 (p<0.01)",
                "claim_type": "FACTUAL",
                "sources": [{"type": "PRIMARY", "reference": "A (2020)", "doi": "10.1000/xyz", "verified": True}],
                "confidence": 90,
                "uncertainty": "Limited context",
            },
            {
                "id": "C-002",
                "text": "Weak claim",
                "claim_type": "EMPIRICAL",
                "sources": [],  # 출처 없음
                "confidence": 50,
            },
        ]

        result = evaluate_all_claims(claims, threshold=75)
        # C-002 (출처 없음)가 미달 목록에 있어야 함
        below_ids = [item["id"] for item in result["below_threshold"]]
        assert "C-002" in below_ids


class TestGradeAssignment:
    """등급 부여 테스트"""

    def test_grade_a(self):
        """A 등급 (90+)"""
        from srcs_evaluator import assign_grade

        grade = assign_grade(92)
        assert grade == "A"

    def test_grade_b(self):
        """B 등급 (80-89)"""
        from srcs_evaluator import assign_grade

        grade = assign_grade(85)
        assert grade == "B"

    def test_grade_c(self):
        """C 등급 (75-79)"""
        from srcs_evaluator import assign_grade

        grade = assign_grade(77)
        assert grade == "C"

    def test_grade_d(self):
        """D 등급 (60-74)"""
        from srcs_evaluator import assign_grade

        grade = assign_grade(68)
        assert grade == "D"

    def test_grade_f(self):
        """F 등급 (<60)"""
        from srcs_evaluator import assign_grade

        grade = assign_grade(45)
        assert grade == "F"


class TestReportGeneration:
    """보고서 생성 테스트"""

    def test_generate_summary_json(self, temp_dir):
        """srcs-summary.json 생성"""
        from srcs_evaluator import generate_summary

        evaluation_result = {
            "total_claims": 20,
            "by_type": {
                "FACTUAL": {"count": 8, "avg_score": 82},
                "EMPIRICAL": {"count": 10, "avg_score": 78},
                "THEORETICAL": {"count": 2, "avg_score": 85},
            },
            "overall_scores": {"cs": 80, "gs": 78, "us": 85, "vs": 75, "total": 79.3},
            "pass_rate": 85,
            "below_threshold": [],
            "inconsistencies": [],
            "grade": "C",
        }

        output_path = temp_dir / "srcs-summary.json"
        generate_summary(evaluation_result, output_path)

        assert output_path.exists()
        saved = json.loads(output_path.read_text())
        assert saved["total_claims"] == 20
        assert saved["grade"] == "C"

    def test_generate_quality_report_md(self, temp_dir):
        """quality-report.md 생성"""
        from srcs_evaluator import generate_quality_report

        evaluation_result = {
            "evaluation_date": "2026-01-18",
            "total_claims": 20,
            "by_type": {
                "FACTUAL": {"count": 8, "avg_score": 82},
                "EMPIRICAL": {"count": 10, "avg_score": 78},
                "THEORETICAL": {"count": 2, "avg_score": 85},
            },
            "overall_scores": {"cs": 80, "gs": 78, "us": 85, "vs": 75, "total": 79.3},
            "pass_rate": 85,
            "below_threshold": [],
            "inconsistencies": [],
            "grade": "C",
        }

        output_path = temp_dir / "quality-report.md"
        generate_quality_report(evaluation_result, output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "학술적 품질 보고서" in content or "Quality" in content
        assert "SRCS" in content


class TestFullEvaluationPipeline:
    """전체 평가 파이프라인 테스트"""

    def test_run_full_evaluation(self, temp_thesis_output):
        """전체 평가 실행"""
        from srcs_evaluator import run_srcs_evaluation

        # 테스트 파일 생성
        temp_dir = temp_thesis_output / "_temp"
        test_file = temp_dir / "01-literature-search-strategy.md"
        test_file.write_text("""# Literature Search
## Claims
```yaml
claims:
  - id: "LS-001"
    text: "The search strategy identified 500 articles"
    claim_type: FACTUAL
    sources:
      - type: PRIMARY
        reference: "Database search (2026)"
        verified: true
    confidence: 90
```
""")

        result = run_srcs_evaluation(temp_dir)
        assert "total_claims" in result
        assert "overall_scores" in result
        assert "grade" in result

    def test_evaluation_creates_output_files(self, temp_thesis_output):
        """출력 파일 생성 확인"""
        from srcs_evaluator import run_srcs_evaluation

        temp_dir = temp_thesis_output / "_temp"
        test_file = temp_dir / "01-literature-search-strategy.md"
        test_file.write_text("""# Test
## Claims
```yaml
claims:
  - id: "TEST-001"
    text: "Test claim"
    claim_type: FACTUAL
    sources:
      - type: PRIMARY
        reference: "Test (2026)"
        verified: true
    confidence: 85
```
""")

        result = run_srcs_evaluation(temp_dir, save_outputs=True)

        summary_path = temp_dir / "srcs-summary.json"
        report_path = temp_dir / "quality-report.md"

        assert summary_path.exists()
        assert report_path.exists()
