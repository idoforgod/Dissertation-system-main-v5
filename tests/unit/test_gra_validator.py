"""Unit tests for gra_validator.py - GRA validation module."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))


class TestHallucinationFirewall:
    """Tests for hallucination detection functionality."""

    def test_detect_block_patterns(self):
        """Test detection of BLOCK-level hallucination patterns."""
        from gra_validator import detect_hallucination_patterns

        # Pure BLOCK-level texts (absolute/universal claims)
        block_texts = [
            "모든 연구가 일치한다",
            "항상 그렇다",
            "절대로 실패하지 않는다",
            "완벽하게 일치한다",
            "전혀 없다",
        ]

        for text in block_texts:
            result = detect_hallucination_patterns(text)
            assert result["level"] == "BLOCK", f"Expected BLOCK for: {text}"
            assert len(result["matches"]) > 0

        # SOFTEN-level texts (overconfident but not absolute)
        soften_texts = [
            "이것은 100% 확실하다",
            "예외 없이 성립한다",
        ]

        for text in soften_texts:
            result = detect_hallucination_patterns(text)
            assert result["level"] == "SOFTEN", f"Expected SOFTEN for: {text}"
            assert len(result["matches"]) > 0

    def test_detect_require_source_patterns(self):
        """Test detection of REQUIRE_SOURCE patterns."""
        from gra_validator import detect_hallucination_patterns

        texts = [
            "p < .001로 유의하다",
            "효과크기 d = 0.8이다",
            "r = 0.75의 상관관계",
        ]

        for text in texts:
            result = detect_hallucination_patterns(text)
            assert result["level"] in ("REQUIRE_SOURCE", "BLOCK"), f"Expected REQUIRE_SOURCE for: {text}"

    def test_detect_soften_patterns(self):
        """Test detection of SOFTEN-level patterns."""
        from gra_validator import detect_hallucination_patterns

        texts = [
            "확실히 그렇다고 할 수 있다",
            "명백히 증명되었다",
            "분명히 차이가 있다",
        ]

        for text in texts:
            result = detect_hallucination_patterns(text)
            assert result["level"] in ("SOFTEN", "BLOCK", "REQUIRE_SOURCE")

    def test_clean_text_passes(self):
        """Test that clean text passes without issues."""
        from gra_validator import detect_hallucination_patterns

        text = "선행연구에 따르면 조직몰입과 직무성과 간 정적 상관관계가 보고되었다 (Meyer & Allen, 1991)."
        result = detect_hallucination_patterns(text)

        assert result["level"] == "PASS"
        assert len(result["matches"]) == 0


class TestGroundedClaimValidation:
    """Tests for GroundedClaim schema validation."""

    def test_valid_claim_passes(self, sample_claims: list[dict]):
        """Test that valid claims pass validation."""
        from gra_validator import validate_claim

        for claim in sample_claims:
            is_valid, errors = validate_claim(claim)
            assert is_valid, f"Claim {claim['id']} should be valid: {errors}"

    def test_claim_missing_id_fails(self):
        """Test that claim without ID fails."""
        from gra_validator import validate_claim

        claim = {
            "text": "Test claim",
            "claim_type": "EMPIRICAL",
            "sources": [],
            "confidence": 80,
        }

        is_valid, errors = validate_claim(claim)
        assert not is_valid
        assert any("id" in e.lower() for e in errors)

    def test_claim_invalid_type_fails(self):
        """Test that claim with invalid type fails."""
        from gra_validator import validate_claim

        claim = {
            "id": "TEST-001",
            "text": "Test claim",
            "claim_type": "INVALID_TYPE",
            "sources": [],
            "confidence": 80,
        }

        is_valid, errors = validate_claim(claim)
        assert not is_valid
        assert any("claim_type" in e.lower() for e in errors)

    def test_empirical_claim_without_primary_source_fails(self):
        """Test that EMPIRICAL claim without PRIMARY source fails."""
        from gra_validator import validate_claim

        claim = {
            "id": "TEST-001",
            "text": "Empirical finding",
            "claim_type": "EMPIRICAL",
            "sources": [
                {"type": "SECONDARY", "reference": "Some review", "verified": False}
            ],
            "confidence": 85,
        }

        is_valid, errors = validate_claim(claim)
        assert not is_valid
        assert any("primary" in e.lower() for e in errors)

    def test_confidence_below_threshold_warns(self):
        """Test that confidence below type threshold generates warning."""
        from gra_validator import validate_claim

        claim = {
            "id": "TEST-001",
            "text": "Factual statement",
            "claim_type": "FACTUAL",
            "sources": [
                {"type": "PRIMARY", "reference": "Source", "verified": True}
            ],
            "confidence": 80,  # FACTUAL requires 95+
        }

        is_valid, errors = validate_claim(claim)
        # Should still be valid but with warning
        assert any("confidence" in e.lower() for e in errors)

    def test_claim_with_hallucination_fails(self):
        """Test that claim with hallucination pattern fails."""
        from gra_validator import validate_claim

        claim = {
            "id": "TEST-001",
            "text": "모든 연구가 일치하며 예외 없이 성립한다",
            "claim_type": "EMPIRICAL",
            "sources": [
                {"type": "PRIMARY", "reference": "Test", "verified": True}
            ],
            "confidence": 100,
        }

        is_valid, errors = validate_claim(claim)
        assert not is_valid
        assert any("hallucination" in e.lower() for e in errors)


class TestSRCSEvaluation:
    """Tests for SRCS score calculation."""

    def test_calculate_citation_score(self, sample_claims: list[dict]):
        """Test citation score calculation."""
        from gra_validator import calculate_citation_score

        claim = sample_claims[0]  # Has PRIMARY source with DOI
        score = calculate_citation_score(claim)

        assert 0 <= score <= 100
        assert score >= 80  # Should be high with PRIMARY + DOI

    def test_calculate_grounding_score(self, sample_claims: list[dict]):
        """Test grounding score calculation."""
        from gra_validator import calculate_grounding_score

        claim = sample_claims[0]
        score = calculate_grounding_score(claim)

        assert 0 <= score <= 100

    def test_calculate_uncertainty_score(self, sample_claims: list[dict]):
        """Test uncertainty score calculation."""
        from gra_validator import calculate_uncertainty_score

        claim = sample_claims[0]  # Has uncertainty field
        score = calculate_uncertainty_score(claim)

        assert 0 <= score <= 100
        assert score >= 70  # Has uncertainty expressed

    def test_calculate_verifiability_score(self, sample_claims: list[dict]):
        """Test verifiability score calculation."""
        from gra_validator import calculate_verifiability_score

        claim = sample_claims[0]  # Has DOI, verified sources
        score = calculate_verifiability_score(claim)

        assert 0 <= score <= 100
        assert score >= 80  # Should be high with DOI

    def test_calculate_srcs_total(self, sample_claims: list[dict]):
        """Test total SRCS score calculation."""
        from gra_validator import calculate_srcs_score

        claim = sample_claims[0]
        scores = calculate_srcs_score(claim)

        assert "cs" in scores
        assert "gs" in scores
        assert "us" in scores
        assert "vs" in scores
        assert "total" in scores
        assert 0 <= scores["total"] <= 100


class TestClaimTypeRequirements:
    """Tests for claim type specific requirements."""

    def test_factual_requires_high_confidence(self):
        """Test that FACTUAL claims require 95+ confidence."""
        from gra_validator import get_confidence_threshold

        threshold = get_confidence_threshold("FACTUAL")
        assert threshold == 95

    def test_empirical_requires_primary_source(self):
        """Test that EMPIRICAL claims require PRIMARY source."""
        from gra_validator import requires_primary_source

        assert requires_primary_source("EMPIRICAL") is True
        assert requires_primary_source("THEORETICAL") is True
        assert requires_primary_source("SPECULATIVE") is False

    def test_speculative_has_low_threshold(self):
        """Test that SPECULATIVE has low confidence threshold."""
        from gra_validator import get_confidence_threshold

        threshold = get_confidence_threshold("SPECULATIVE")
        assert threshold == 60


class TestValidationReport:
    """Tests for validation report generation."""

    def test_generate_validation_report(self, sample_claims: list[dict]):
        """Test validation report generation for multiple claims."""
        from gra_validator import generate_validation_report

        report = generate_validation_report(sample_claims)

        assert "total_claims" in report
        assert "valid_claims" in report
        assert "invalid_claims" in report
        assert "average_srcs" in report
        assert "claims" in report

        assert report["total_claims"] == len(sample_claims)

    def test_report_includes_individual_scores(self, sample_claims: list[dict]):
        """Test that report includes individual claim scores."""
        from gra_validator import generate_validation_report

        report = generate_validation_report(sample_claims)

        for claim_report in report["claims"]:
            assert "id" in claim_report
            assert "is_valid" in claim_report
            assert "srcs_scores" in claim_report
            assert "errors" in claim_report

    def test_report_calculates_pass_rate(self, sample_claims: list[dict]):
        """Test that report calculates pass rate correctly."""
        from gra_validator import generate_validation_report

        report = generate_validation_report(sample_claims)

        expected_rate = (report["valid_claims"] / report["total_claims"]) * 100
        assert report["pass_rate"] == pytest.approx(expected_rate, rel=0.01)
