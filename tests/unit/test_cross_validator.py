"""
Cross Validator Tests (TDD)
Wave 간 교차 검증 모듈 테스트
"""

import json
import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / ".claude" / "skills" / "thesis-orchestrator" / "scripts"))


class TestClaimExtraction:
    """클레임 추출 테스트"""

    def test_extract_claims_from_markdown(self, temp_dir):
        """마크다운에서 Claims 섹션 추출"""
        from cross_validator import extract_claims_from_file

        content = """# Test Document

## Content
Some content here.

## Claims
```yaml
claims:
  - id: "TEST-001"
    text: "Test claim 1"
    claim_type: FACTUAL
    confidence: 85
  - id: "TEST-002"
    text: "Test claim 2"
    claim_type: EMPIRICAL
    confidence: 90
```
"""
        file_path = temp_dir / "test.md"
        file_path.write_text(content)

        claims = extract_claims_from_file(file_path)
        assert len(claims) == 2
        assert claims[0]["id"] == "TEST-001"
        assert claims[1]["id"] == "TEST-002"

    def test_extract_claims_empty_section(self, temp_dir):
        """빈 Claims 섹션 처리"""
        from cross_validator import extract_claims_from_file

        content = """# Test Document
## Claims
```yaml
claims: []
```
"""
        file_path = temp_dir / "test.md"
        file_path.write_text(content)

        claims = extract_claims_from_file(file_path)
        assert claims == []

    def test_extract_claims_no_section(self, temp_dir):
        """Claims 섹션 없는 파일"""
        from cross_validator import extract_claims_from_file

        content = """# Test Document
## Content
Some content.
"""
        file_path = temp_dir / "test.md"
        file_path.write_text(content)

        claims = extract_claims_from_file(file_path)
        assert claims == []


class TestInconsistencyDetection:
    """불일치 탐지 테스트"""

    def test_detect_numeric_inconsistency(self):
        """수치 불일치 탐지"""
        from cross_validator import detect_inconsistencies

        claims = [
            {"id": "A-001", "text": "The effect size was 0.45", "agent": "agent_a"},
            {"id": "B-001", "text": "The effect size was 0.78", "agent": "agent_b"},
        ]

        inconsistencies = detect_inconsistencies(claims)
        assert len(inconsistencies) >= 1
        assert any("effect size" in inc["topic"].lower() for inc in inconsistencies)

    def test_detect_contradictory_claims(self):
        """상반된 주장 탐지"""
        from cross_validator import detect_inconsistencies

        claims = [
            {
                "id": "A-001",
                "text": "X has a positive effect on Y",
                "agent": "agent_a",
            },
            {
                "id": "B-001",
                "text": "X has a negative effect on Y",
                "agent": "agent_b",
            },
        ]

        inconsistencies = detect_inconsistencies(claims)
        assert len(inconsistencies) >= 1
        assert inconsistencies[0]["type"] == "CONTRADICTION"

    def test_detect_no_inconsistency(self):
        """불일치 없는 경우"""
        from cross_validator import detect_inconsistencies

        claims = [
            {"id": "A-001", "text": "The sample size was 500", "agent": "agent_a"},
            {"id": "B-001", "text": "A different topic entirely", "agent": "agent_b"},
        ]

        inconsistencies = detect_inconsistencies(claims)
        # 다른 주제에 대한 주장이므로 불일치 없음
        assert len(inconsistencies) == 0

    def test_detect_percentage_inconsistency(self):
        """백분율 불일치 탐지"""
        from cross_validator import detect_inconsistencies

        claims = [
            {"id": "A-001", "text": "The response rate was 75%", "agent": "agent_a"},
            {"id": "B-001", "text": "The response rate was 82%", "agent": "agent_b"},
        ]

        inconsistencies = detect_inconsistencies(claims)
        assert len(inconsistencies) >= 1


class TestCrossValidationGate:
    """교차 검증 게이트 테스트"""

    def test_gate_pass_high_consistency(self):
        """높은 일관성으로 게이트 통과"""
        from cross_validator import evaluate_gate

        validation_result = {
            "total_claims": 20,
            "inconsistencies": [],
            "consistency_score": 95,
        }

        gate_result = evaluate_gate(validation_result, threshold=80)
        assert gate_result["passed"] is True
        assert gate_result["score"] == 95

    def test_gate_fail_low_consistency(self):
        """낮은 일관성으로 게이트 실패"""
        from cross_validator import evaluate_gate

        validation_result = {
            "total_claims": 20,
            "inconsistencies": [
                {"type": "CONTRADICTION", "severity": "HIGH"},
                {"type": "NUMERIC_MISMATCH", "severity": "MEDIUM"},
                {"type": "CONTRADICTION", "severity": "HIGH"},
            ],
            "consistency_score": 60,
        }

        gate_result = evaluate_gate(validation_result, threshold=80)
        assert gate_result["passed"] is False
        assert gate_result["score"] == 60

    def test_gate_conditional_pass(self):
        """조건부 통과"""
        from cross_validator import evaluate_gate

        validation_result = {
            "total_claims": 20,
            "inconsistencies": [{"type": "NUMERIC_MISMATCH", "severity": "LOW"}],
            "consistency_score": 78,
        }

        gate_result = evaluate_gate(validation_result, threshold=75)
        assert gate_result["passed"] is True
        assert gate_result["warnings"] is not None


class TestConsistencyScoring:
    """일관성 점수 계산 테스트"""

    def test_calculate_consistency_perfect(self):
        """완벽한 일관성 점수"""
        from cross_validator import calculate_consistency_score

        claims = [
            {"id": "A-001", "text": "Claim A", "agent": "agent_a"},
            {"id": "B-001", "text": "Claim B", "agent": "agent_b"},
        ]
        inconsistencies = []

        score = calculate_consistency_score(claims, inconsistencies)
        assert score == 100

    def test_calculate_consistency_with_issues(self):
        """불일치가 있는 일관성 점수"""
        from cross_validator import calculate_consistency_score

        claims = [{"id": f"C-{i:03d}", "text": f"Claim {i}", "agent": "agent"} for i in range(10)]

        inconsistencies = [
            {"type": "CONTRADICTION", "severity": "HIGH"},
            {"type": "NUMERIC_MISMATCH", "severity": "MEDIUM"},
        ]

        score = calculate_consistency_score(claims, inconsistencies)
        assert 0 <= score < 100

    def test_consistency_score_severity_weighting(self):
        """심각도별 가중치 반영"""
        from cross_validator import calculate_consistency_score

        claims = [{"id": f"C-{i:03d}", "text": f"Claim {i}", "agent": "agent"} for i in range(10)]

        high_severity = [{"type": "CONTRADICTION", "severity": "HIGH"}]
        low_severity = [{"type": "NUMERIC_MISMATCH", "severity": "LOW"}]

        score_high = calculate_consistency_score(claims, high_severity)
        score_low = calculate_consistency_score(claims, low_severity)

        assert score_low > score_high  # HIGH severity should reduce score more


class TestWaveValidation:
    """Wave별 검증 테스트"""

    def test_validate_wave_outputs(self, temp_thesis_output):
        """Wave 출력 파일 검증"""
        from cross_validator import validate_wave

        # Wave 1 파일 생성
        wave1_files = [
            "01-literature-search-strategy.md",
            "02-seminal-works-analysis.md",
            "03-research-trend-analysis.md",
            "04-methodology-scan.md",
        ]

        for fname in wave1_files:
            file_path = temp_thesis_output / "_temp" / fname
            file_path.write_text(f"""# {fname}
## Claims
```yaml
claims:
  - id: "W1-001"
    text: "Wave 1 claim"
    claim_type: FACTUAL
    confidence: 85
```
""")

        result = validate_wave(temp_thesis_output / "_temp", wave=1)
        assert result["wave"] == 1
        assert result["files_validated"] == 4
        assert "consistency_score" in result

    def test_validate_wave_missing_files(self, temp_thesis_output):
        """Wave 파일 누락 감지"""
        from cross_validator import validate_wave

        # 일부 파일만 생성
        file_path = temp_thesis_output / "_temp" / "01-literature-search-strategy.md"
        file_path.write_text("# Test\n## Claims\n")

        result = validate_wave(temp_thesis_output / "_temp", wave=1)
        assert result["files_validated"] < 4
        assert "missing_files" in result


class TestCrossValidationReport:
    """교차 검증 보고서 테스트"""

    def test_generate_report(self):
        """검증 보고서 생성"""
        from cross_validator import generate_validation_report

        validation_result = {
            "wave": 1,
            "total_claims": 15,
            "inconsistencies": [
                {
                    "type": "NUMERIC_MISMATCH",
                    "agent1": "agent_a",
                    "agent2": "agent_b",
                    "topic": "sample size",
                    "severity": "MEDIUM",
                }
            ],
            "consistency_score": 85,
            "gate_passed": True,
        }

        report = generate_validation_report(validation_result)
        assert "Wave 1" in report
        assert "일관성 점수" in report or "Consistency" in report
        assert "85" in report

    def test_report_includes_recommendations(self):
        """권고사항 포함 확인"""
        from cross_validator import generate_validation_report

        validation_result = {
            "wave": 2,
            "total_claims": 20,
            "inconsistencies": [
                {"type": "CONTRADICTION", "severity": "HIGH", "topic": "effect direction"}
            ],
            "consistency_score": 70,
            "gate_passed": False,
        }

        report = generate_validation_report(validation_result)
        assert "권고" in report or "Recommendation" in report


class TestFullCrossValidation:
    """전체 교차 검증 프로세스 테스트"""

    def test_run_cross_validation(self, temp_thesis_output):
        """전체 교차 검증 실행"""
        from cross_validator import run_cross_validation

        # 테스트 파일 생성
        temp_dir = temp_thesis_output / "_temp"
        test_file = temp_dir / "01-literature-search-strategy.md"
        test_file.write_text("""# Literature Search
## Claims
```yaml
claims:
  - id: "LS-001"
    text: "Test claim"
    claim_type: FACTUAL
    confidence: 90
```
""")

        result = run_cross_validation(temp_dir, waves=[1])
        assert "waves_validated" in result
        assert "overall_consistency" in result

    def test_cross_validation_output_file(self, temp_thesis_output):
        """교차 검증 결과 파일 생성"""
        from cross_validator import run_cross_validation, save_validation_result

        result = {
            "waves_validated": [1],
            "overall_consistency": 88,
            "gate_results": [{"wave": 1, "passed": True}],
        }

        output_path = temp_thesis_output / "_temp" / "cross-validation-result.json"
        save_validation_result(result, output_path)

        assert output_path.exists()
        saved = json.loads(output_path.read_text())
        assert saved["overall_consistency"] == 88
