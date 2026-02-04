#!/usr/bin/env python3
"""Improvement Analyzer: Advisory-Only Analysis Engine.

This module analyzes performance metrics and generates improvement PROPOSALS.
It does NOT apply any changes. All proposals are advisory only, intended
for human review and decision-making.

Key principle: This module READS metrics and WRITES proposals to a new file.
It never modifies any existing workflow files.

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-31
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from path_utils import get_working_dir_from_session


# ============================================================================
# Constants
# ============================================================================

VERSION = "1.0.0"

# Analysis thresholds (for detecting issues, NOT for modifying the workflow)
ANALYSIS_RULES = {
    "low_ptcs_threshold": 75,        # Agent pTCS below this → flag for review
    "high_retry_threshold": 2,       # Retry count >= this → flag
    "gate_fail_rate_threshold": 0.3, # Gate fail rate > 30% → flag
    "output_length_min": 500,        # Suspiciously short output (bytes)
    "output_length_max": 100000,     # Suspiciously long output (bytes)
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ImprovementProposal:
    """A single improvement proposal (advisory only).

    This is a SUGGESTION for the human operator, not an instruction
    for the system to execute.
    """

    id: str
    proposal_type: str  # "prompt_review", "threshold_review", "structural_review"
    target: str  # Target file or component
    description: str  # Human-readable description
    evidence: str  # Data-backed justification
    risk_level: str  # "low", "medium", "high"
    expected_benefit: str  # Expected improvement
    priority: int  # 1 (highest) to 5 (lowest)

    # Advisory metadata
    category: str = "observation"  # "observation", "suggestion", "warning"
    affected_components: List[str] = None
    related_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.affected_components is None:
            self.affected_components = []
        if self.related_metrics is None:
            self.related_metrics = {}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AnalysisReport:
    """Complete analysis report with improvement proposals."""

    run_id: str
    timestamp: str
    version: str
    source_metrics_file: str

    # Proposals grouped by priority
    proposals: List[dict]

    # Summary
    total_proposals: int
    high_priority: int
    medium_priority: int
    low_priority: int

    # Analysis metadata
    rules_applied: Dict[str, Any]

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Improvement Analyzer (Advisory Only)
# ============================================================================

class ImprovementAnalyzer:
    """Analyzes performance metrics and generates advisory proposals.

    This class is ADVISORY ONLY. It:
    - READS performance metrics
    - ANALYZES patterns and anomalies
    - WRITES proposals to a new file
    - NEVER modifies any existing workflow files

    All proposals require human review before any action is taken.
    """

    def __init__(
        self,
        working_dir: Path,
        rules: Optional[Dict[str, Any]] = None,
        verbose: bool = True,
    ):
        """Initialize analyzer.

        Args:
            working_dir: Project working directory
            rules: Custom analysis rules (defaults to ANALYSIS_RULES)
            verbose: Print detailed logs
        """
        self.working_dir = Path(working_dir).resolve()
        self.rules = rules or dict(ANALYSIS_RULES)
        self.verbose = verbose

    # ========================================================================
    # Main Analysis
    # ========================================================================

    def analyze(self, metrics_file: Path) -> AnalysisReport:
        """Analyze a performance metrics file and generate proposals.

        Args:
            metrics_file: Path to performance-metrics-*.json

        Returns:
            AnalysisReport with advisory proposals
        """
        self._log(f"\n{'='*70}")
        self._log("IMPROVEMENT ANALYZER (Advisory Only)")
        self._log(f"{'='*70}")
        self._log(f"Metrics file: {metrics_file}")
        self._log("")

        # Load metrics
        with open(metrics_file, 'r', encoding='utf-8') as f:
            metrics = json.load(f)

        # Run all analysis rules
        proposals = []

        proposals.extend(self._analyze_agent_ptcs(metrics))
        proposals.extend(self._analyze_retry_patterns(metrics))
        proposals.extend(self._analyze_gate_performance(metrics))
        proposals.extend(self._analyze_output_anomalies(metrics))
        proposals.extend(self._analyze_cross_agent_patterns(metrics))

        # Assign IDs and sort by priority
        for i, p in enumerate(proposals, 1):
            p.id = f"IMP-{i:03d}"
        proposals.sort(key=lambda p: p.priority)

        # Build report
        proposal_dicts = [p.to_dict() for p in proposals]
        high = sum(1 for p in proposals if p.priority <= 2)
        medium = sum(1 for p in proposals if p.priority == 3)
        low = sum(1 for p in proposals if p.priority >= 4)

        report = AnalysisReport(
            run_id=metrics.get("run_id", "unknown"),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            version=VERSION,
            source_metrics_file=str(metrics_file),
            proposals=proposal_dicts,
            total_proposals=len(proposals),
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            rules_applied=self.rules,
        )

        self._log(f"\nGenerated {len(proposals)} proposals:")
        self._log(f"  High priority: {high}")
        self._log(f"  Medium priority: {medium}")
        self._log(f"  Low priority: {low}")

        return report

    def save_report(self, report: AnalysisReport) -> Path:
        """Save analysis report to improvement-data directory.

        Only creates NEW files. Never modifies existing ones.

        Args:
            report: AnalysisReport to save

        Returns:
            Path to saved report file
        """
        improvement_dir = self.working_dir / "00-session" / "improvement-data"
        improvement_dir.mkdir(parents=True, exist_ok=True)

        filename = f"improvement-proposals-{report.run_id}.json"
        output_path = improvement_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        self._log(f"Report saved: {output_path}")
        return output_path

    # ========================================================================
    # Analysis Rules (All Read-Only)
    # ========================================================================

    def _analyze_agent_ptcs(self, metrics: Dict) -> List[ImprovementProposal]:
        """Flag agents with consistently low pTCS scores."""
        proposals = []
        agents = metrics.get("agents", {})
        threshold = self.rules["low_ptcs_threshold"]

        for agent_name, agent_data in agents.items():
            ptcs = agent_data.get("ptcs")
            if ptcs is not None and ptcs < threshold:
                proposals.append(ImprovementProposal(
                    id="",  # Will be assigned later
                    proposal_type="prompt_review",
                    target=f"Agent: {agent_name}",
                    description=(
                        f"Agent '{agent_name}' has pTCS {ptcs:.1f}, "
                        f"below the review threshold of {threshold}. "
                        f"Consider reviewing the agent prompt for clarity, "
                        f"specificity, or missing examples."
                    ),
                    evidence=f"pTCS: {ptcs:.1f}/{threshold}",
                    risk_level="medium",
                    expected_benefit="Improved output quality and reduced retries",
                    priority=2,
                    category="suggestion",
                    affected_components=[agent_name],
                    related_metrics={"ptcs": ptcs, "threshold": threshold},
                ))

        return proposals

    def _analyze_retry_patterns(self, metrics: Dict) -> List[ImprovementProposal]:
        """Flag agents with high retry counts."""
        proposals = []
        agents = metrics.get("agents", {})
        threshold = self.rules["high_retry_threshold"]

        for agent_name, agent_data in agents.items():
            retry_count = agent_data.get("retry_count", 0)
            if retry_count >= threshold:
                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="prompt_review",
                    target=f"Agent: {agent_name}",
                    description=(
                        f"Agent '{agent_name}' required {retry_count} retries. "
                        f"This suggests the agent prompt may need clearer "
                        f"instructions or the output format expectations may "
                        f"be ambiguous."
                    ),
                    evidence=f"Retries: {retry_count} (threshold: {threshold})",
                    risk_level="medium",
                    expected_benefit="Fewer retries, faster workflow completion",
                    priority=2,
                    category="suggestion",
                    affected_components=[agent_name],
                    related_metrics={"retry_count": retry_count},
                ))

        return proposals

    def _analyze_gate_performance(self, metrics: Dict) -> List[ImprovementProposal]:
        """Flag gates with high failure rates or low scores."""
        proposals = []
        gates = metrics.get("gates", {})
        overall = metrics.get("overall", {})

        gate_pass_rate = overall.get("gate_pass_rate")
        if gate_pass_rate is not None and gate_pass_rate < (1 - self.rules["gate_fail_rate_threshold"]):
            proposals.append(ImprovementProposal(
                id="",
                proposal_type="structural_review",
                target="Gate System",
                description=(
                    f"Gate pass rate is {gate_pass_rate:.0%}, indicating "
                    f"systemic quality issues. Review the agents in failing "
                    f"waves/phases for common patterns."
                ),
                evidence=f"Gate pass rate: {gate_pass_rate:.0%}",
                risk_level="high",
                expected_benefit="Improved gate passage, smoother workflow",
                priority=1,
                category="warning",
                affected_components=["gate_controller"],
                related_metrics={"gate_pass_rate": gate_pass_rate},
            ))

        # Individual gate analysis
        for gate_id, gate_data in gates.items():
            if not gate_data.get("passed", True):
                ptcs = gate_data.get("ptcs")
                srcs = gate_data.get("srcs")
                attempts = gate_data.get("attempts", 1)

                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="threshold_review",
                    target=f"Gate: {gate_id}",
                    description=(
                        f"Gate '{gate_id}' failed after {attempts} attempt(s). "
                        f"pTCS: {ptcs}, SRCS: {srcs}. "
                        f"Review the agents contributing to this gate's inputs."
                    ),
                    evidence=f"Failed gate: pTCS={ptcs}, SRCS={srcs}, attempts={attempts}",
                    risk_level="high",
                    expected_benefit="Gate passage on subsequent runs",
                    priority=1,
                    category="warning",
                    affected_components=[gate_id],
                    related_metrics=gate_data,
                ))

        return proposals

    def _analyze_output_anomalies(self, metrics: Dict) -> List[ImprovementProposal]:
        """Flag agents with anomalous output sizes."""
        proposals = []
        agents = metrics.get("agents", {})
        min_len = self.rules["output_length_min"]
        max_len = self.rules["output_length_max"]

        for agent_name, agent_data in agents.items():
            output_length = agent_data.get("total_output_length", 0)

            if 0 < output_length < min_len:
                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="prompt_review",
                    target=f"Agent: {agent_name}",
                    description=(
                        f"Agent '{agent_name}' produced unusually short output "
                        f"({output_length} bytes). This may indicate incomplete "
                        f"execution or an overly brief response."
                    ),
                    evidence=f"Output: {output_length} bytes (min expected: {min_len})",
                    risk_level="low",
                    expected_benefit="More thorough agent outputs",
                    priority=4,
                    category="observation",
                    affected_components=[agent_name],
                    related_metrics={"output_length": output_length},
                ))

            elif output_length > max_len:
                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="prompt_review",
                    target=f"Agent: {agent_name}",
                    description=(
                        f"Agent '{agent_name}' produced unusually long output "
                        f"({output_length} bytes). This may indicate verbose or "
                        f"unfocused responses that increase processing cost."
                    ),
                    evidence=f"Output: {output_length} bytes (max expected: {max_len})",
                    risk_level="low",
                    expected_benefit="More focused agent outputs",
                    priority=5,
                    category="observation",
                    affected_components=[agent_name],
                    related_metrics={"output_length": output_length},
                ))

        return proposals

    def _analyze_cross_agent_patterns(self, metrics: Dict) -> List[ImprovementProposal]:
        """Identify patterns across multiple agents."""
        proposals = []
        agents = metrics.get("agents", {})

        # Check for widespread low confidence
        ptcs_scores = [
            (name, data.get("ptcs"))
            for name, data in agents.items()
            if data.get("ptcs") is not None
        ]

        if len(ptcs_scores) >= 3:
            avg_ptcs = sum(s for _, s in ptcs_scores) / len(ptcs_scores)
            if avg_ptcs < self.rules["low_ptcs_threshold"]:
                low_agents = [
                    name for name, score in ptcs_scores
                    if score < self.rules["low_ptcs_threshold"]
                ]
                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="structural_review",
                    target="Workflow-wide",
                    description=(
                        f"Average pTCS across {len(ptcs_scores)} agents is "
                        f"{avg_ptcs:.1f}, below threshold. This suggests a "
                        f"systemic issue rather than individual agent problems. "
                        f"Affected agents: {', '.join(low_agents)}"
                    ),
                    evidence=f"Avg pTCS: {avg_ptcs:.1f}, {len(low_agents)} agents below threshold",
                    risk_level="high",
                    expected_benefit="Systemic quality improvement",
                    priority=1,
                    category="warning",
                    affected_components=low_agents,
                    related_metrics={"avg_ptcs": avg_ptcs, "low_agents": low_agents},
                ))

        # Check for widespread retries
        total_retries = sum(
            data.get("retry_count", 0) for data in agents.values()
        )
        if total_retries > len(agents) * 1.5:
            proposals.append(ImprovementProposal(
                id="",
                proposal_type="structural_review",
                target="Retry System",
                description=(
                    f"Total retries ({total_retries}) across {len(agents)} agents "
                    f"is unusually high (>{len(agents) * 1.5:.0f} expected max). "
                    f"Review GRA schema compliance and output format requirements."
                ),
                evidence=f"Total retries: {total_retries}/{len(agents)} agents",
                risk_level="medium",
                expected_benefit="Reduced retry overhead",
                priority=3,
                category="suggestion",
                affected_components=["retry_system"],
                related_metrics={"total_retries": total_retries},
            ))

        return proposals

    # ========================================================================
    # Historical Comparison (Read-Only)
    # ========================================================================

    def compare_with_previous(
        self, current_metrics: Dict, previous_metrics_file: Path
    ) -> List[ImprovementProposal]:
        """Compare current metrics with a previous run (read-only).

        Args:
            current_metrics: Current run's metrics dict
            previous_metrics_file: Path to previous metrics file

        Returns:
            Additional proposals based on trend analysis
        """
        proposals = []

        try:
            with open(previous_metrics_file, 'r', encoding='utf-8') as f:
                prev = json.load(f)
        except (json.JSONDecodeError, OSError):
            self._log(f"Warning: Could not load previous metrics: {previous_metrics_file}")
            return proposals

        # Compare overall metrics
        curr_overall = current_metrics.get("overall", {})
        prev_overall = prev.get("overall", {})

        curr_ptcs = curr_overall.get("avg_ptcs")
        prev_ptcs = prev_overall.get("avg_ptcs")

        if curr_ptcs is not None and prev_ptcs is not None:
            delta = curr_ptcs - prev_ptcs
            if delta < -5:
                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="structural_review",
                    target="Workflow-wide",
                    description=(
                        f"Average pTCS dropped by {abs(delta):.1f} points compared "
                        f"to previous run ({prev_ptcs:.1f} -> {curr_ptcs:.1f}). "
                        f"Investigate whether the research topic complexity or "
                        f"system changes caused this regression."
                    ),
                    evidence=f"pTCS delta: {delta:+.1f} (prev: {prev_ptcs:.1f}, curr: {curr_ptcs:.1f})",
                    risk_level="high",
                    expected_benefit="Identify and address quality regression",
                    priority=1,
                    category="warning",
                    related_metrics={
                        "current_ptcs": curr_ptcs,
                        "previous_ptcs": prev_ptcs,
                        "delta": delta,
                    },
                ))
            elif delta > 5:
                proposals.append(ImprovementProposal(
                    id="",
                    proposal_type="prompt_review",
                    target="Workflow-wide",
                    description=(
                        f"Average pTCS improved by {delta:.1f} points compared "
                        f"to previous run ({prev_ptcs:.1f} -> {curr_ptcs:.1f}). "
                        f"Document what changed for future reference."
                    ),
                    evidence=f"pTCS delta: {delta:+.1f}",
                    risk_level="low",
                    expected_benefit="Knowledge preservation",
                    priority=5,
                    category="observation",
                    related_metrics={
                        "current_ptcs": curr_ptcs,
                        "previous_ptcs": prev_ptcs,
                        "delta": delta,
                    },
                ))

        return proposals

    # ========================================================================
    # Utilities
    # ========================================================================

    def _log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for improvement analyzer."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Improvement Analyzer - Advisory-only analysis engine"
    )
    parser.add_argument(
        "--metrics-file", type=str,
        help="Path to performance-metrics-*.json file"
    )
    parser.add_argument(
        "--previous", type=str, default=None,
        help="Path to previous metrics file for comparison"
    )
    parser.add_argument(
        "--working-dir", type=str, default=None,
        help="Working directory (auto-detected if omitted)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run with test data"
    )

    args = parser.parse_args()

    if args.test:
        print("\n" + "=" * 70)
        print("Improvement Analyzer - Test Mode")
        print("=" * 70)

        # Create mock metrics
        mock_metrics = {
            "run_id": "test-001",
            "agents": {
                "literature-searcher": {"ptcs": 82.5, "srcs": 78.0, "retry_count": 0,
                                         "total_output_length": 4500, "success": True},
                "variable-relationship-analyst": {"ptcs": 68.5, "srcs": 72.0,
                                                   "retry_count": 2,
                                                   "total_output_length": 3200,
                                                   "success": True},
                "methodology-critic": {"ptcs": 71.0, "srcs": 69.0, "retry_count": 1,
                                        "total_output_length": 200, "success": True},
            },
            "gates": {
                "wave-1": {"passed": True, "ptcs": 80.0, "srcs": 77.0, "attempts": 1},
                "wave-2": {"passed": False, "ptcs": 68.0, "srcs": 80.0, "attempts": 2},
            },
            "overall": {
                "avg_ptcs": 74.0,
                "avg_srcs": 73.0,
                "total_retries": 3,
                "gate_pass_rate": 0.5,
            },
        }

        # Write mock metrics to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(mock_metrics, f, indent=2)
            temp_path = f.name

        # Analyze
        analyzer = ImprovementAnalyzer(
            working_dir=Path.cwd(),
            verbose=True,
        )
        report = analyzer.analyze(Path(temp_path))
        print(json.dumps(report.to_dict(), indent=2))

        # Clean up
        Path(temp_path).unlink()
        return 0

    # Real analysis
    try:
        if not args.metrics_file:
            print("Error: --metrics-file is required (or use --test)")
            return 1

        if args.working_dir:
            working_dir = Path(args.working_dir).resolve()
        else:
            working_dir = get_working_dir_from_session()

        analyzer = ImprovementAnalyzer(
            working_dir=working_dir,
            verbose=not args.quiet,
        )
        report = analyzer.analyze(Path(args.metrics_file))

        # Compare with previous if provided
        if args.previous:
            with open(args.metrics_file, 'r', encoding='utf-8') as f:
                current = json.load(f)
            extra = analyzer.compare_with_previous(current, Path(args.previous))
            if extra:
                for p in extra:
                    p.id = f"IMP-{report.total_proposals + 1:03d}"
                    report.proposals.append(p.to_dict())
                    report.total_proposals += 1

        output_path = analyzer.save_report(report)
        print(f"\nAnalysis report saved: {output_path}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error analyzing metrics: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
