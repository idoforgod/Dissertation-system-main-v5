#!/usr/bin/env python3
"""Change Classifier: Advisory Risk Assessment for Human Prioritization.

This module classifies improvement proposals by risk level to help
humans prioritize their review. It does NOT gate any automated changes
because NO automated changes are made in the safe version.

Key principle: Classification is ADVISORY. All proposals require human
review regardless of classification. The classification helps humans
focus on high-risk items first.

CORE_PHILOSOPHY_INVARIANTS (never modifiable by any system):
1. ALL sub-agents use opus model
2. ALL execution is sequential (no parallel across phases)
3. GRA validation on ALL outputs
4. Cost/time are secondary to quality
5. English work + Korean translation
6. 9 HITL checkpoints (cannot add/remove without approval)
7. 150-step granularity
8. Dual Confidence: pTCS (60%) + SRCS (40%)
9. Phase order: 0->1->2->3->4
10. Wave order within Phase 1: 1->2->3->4->5

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


# ============================================================================
# Constants
# ============================================================================

VERSION = "1.0.0"

# Core philosophy invariants - these should NEVER be modified by any system
CORE_PHILOSOPHY_INVARIANTS = [
    "all_agents_use_opus",
    "sequential_execution_only",
    "gra_validation_on_all_outputs",
    "quality_over_cost_time",
    "english_work_korean_translation",
    "hitl_checkpoints_fixed",
    "150_step_granularity",
    "dual_confidence_ptcs60_srcs40",
    "phase_order_0_1_2_3_4",
    "wave_order_1_2_3_4_5",
]

# Keywords that indicate a proposal touches core invariants.
# Uses multi-word phrases to avoid false positives from common words
# (e.g., "model" alone would match "research-model-developer").
INVARIANT_KEYWORDS = {
    "all_agents_use_opus": [
        "change model", "switch model", "use sonnet", "use haiku",
        "replace opus", "model: sonnet", "model: haiku",
    ],
    "sequential_execution_only": [
        "parallel execution", "run in parallel", "concurrent execution",
        "async execution", "simultaneous agents",
    ],
    "gra_validation_on_all_outputs": [
        "disable gra", "skip gra", "remove gra",
        "bypass grounded", "remove validation",
    ],
    "quality_over_cost_time": [
        "skip quality", "bypass quality", "reduce quality",
        "prioritize speed", "prioritize cost",
    ],
    "english_work_korean_translation": [
        "korean only", "english only", "change language",
        "remove translation", "skip translation",
    ],
    "hitl_checkpoints_fixed": [
        "remove hitl", "add hitl", "skip hitl",
        "remove checkpoint", "add checkpoint", "bypass approval",
    ],
    "150_step_granularity": [
        "change step count", "total steps", "reduce steps",
        "add steps", "change granularity",
    ],
    "dual_confidence_ptcs60_srcs40": [
        "ptcs weight", "srcs weight", "change 60%", "change 40%",
        "confidence weight", "rebalance confidence",
    ],
    "phase_order_0_1_2_3_4": [
        "phase order", "phase sequence", "reorder phase",
        "skip phase", "remove phase",
    ],
    "wave_order_1_2_3_4_5": [
        "wave order", "wave sequence", "reorder wave",
        "skip wave", "remove wave",
    ],
}

# Structural change indicators
STRUCTURAL_KEYWORDS = [
    "add agent", "remove agent", "new agent", "delete agent",
    "add step", "remove step", "new step", "delete step",
    "add phase", "remove phase", "new phase",
    "add wave", "remove wave", "new wave",
    "workflow structure", "pipeline change",
]


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ClassifiedProposal:
    """A proposal with risk classification (advisory only)."""

    # Original proposal data
    proposal_id: str
    proposal_type: str
    target: str
    description: str

    # Classification (advisory)
    risk_category: str  # "low", "medium", "high", "critical"
    risk_reasons: List[str]
    touches_invariants: List[str]  # Which invariants it could affect
    is_structural: bool  # Whether it changes workflow structure

    # Human guidance
    review_priority: int  # 1 (review first) to 5 (review last)
    review_guidance: str  # Advice for the human reviewer

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ClassificationReport:
    """Complete classification report for human review."""

    run_id: str
    timestamp: str
    version: str
    source_proposals_file: str

    # Classified proposals
    classified: List[dict]

    # Summary
    total_proposals: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int

    # Invariant check summary
    invariants_touched: Dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Change Classifier (Advisory Only)
# ============================================================================

class ChangeClassifier:
    """Classifies proposals by risk level for human prioritization.

    This class is PURELY ADVISORY. It helps humans understand:
    - Which proposals are highest risk
    - Which proposals touch core invariants
    - Which proposals should be reviewed first
    - What to look for during review

    It does NOT enable or disable any automated changes.
    """

    def __init__(self, verbose: bool = True):
        """Initialize classifier.

        Args:
            verbose: Print detailed logs
        """
        self.verbose = verbose

    # ========================================================================
    # Main Classification
    # ========================================================================

    def classify(self, proposals_file: Path) -> ClassificationReport:
        """Classify all proposals in a proposals file.

        Args:
            proposals_file: Path to improvement-proposals-*.json

        Returns:
            ClassificationReport with advisory classifications
        """
        self._log(f"\n{'='*70}")
        self._log("CHANGE CLASSIFIER (Advisory Only)")
        self._log(f"{'='*70}")
        self._log(f"Proposals file: {proposals_file}")
        self._log("")

        # Load proposals
        with open(proposals_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        proposals = data.get("proposals", [])
        classified = []
        invariants_touched = {inv: 0 for inv in CORE_PHILOSOPHY_INVARIANTS}

        for proposal in proposals:
            cp = self._classify_single(proposal)
            classified.append(cp.to_dict())

            # Track invariant touches
            for inv in cp.touches_invariants:
                if inv in invariants_touched:
                    invariants_touched[inv] += 1

        # Sort by review priority
        classified.sort(key=lambda x: x["review_priority"])

        # Count by category
        critical = sum(1 for c in classified if c["risk_category"] == "critical")
        high = sum(1 for c in classified if c["risk_category"] == "high")
        medium = sum(1 for c in classified if c["risk_category"] == "medium")
        low = sum(1 for c in classified if c["risk_category"] == "low")

        report = ClassificationReport(
            run_id=data.get("run_id", "unknown"),
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            version=VERSION,
            source_proposals_file=str(proposals_file),
            classified=classified,
            total_proposals=len(classified),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            invariants_touched={k: v for k, v in invariants_touched.items() if v > 0},
        )

        self._log(f"\nClassified {len(classified)} proposals:")
        self._log(f"  Critical: {critical}")
        self._log(f"  High: {high}")
        self._log(f"  Medium: {medium}")
        self._log(f"  Low: {low}")

        if report.invariants_touched:
            self._log(f"\n  Invariants potentially affected:")
            for inv, count in report.invariants_touched.items():
                self._log(f"    {inv}: {count} proposal(s)")

        return report

    def save_report(self, report: ClassificationReport, output_dir: Path) -> Path:
        """Save classification report.

        Args:
            report: ClassificationReport to save
            output_dir: improvement-data directory

        Returns:
            Path to saved report
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"classified-proposals-{report.run_id}.json"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        self._log(f"Classification report saved: {output_path}")
        return output_path

    # ========================================================================
    # Single Proposal Classification
    # ========================================================================

    def _classify_single(self, proposal: Dict) -> ClassifiedProposal:
        """Classify a single proposal."""
        proposal_id = proposal.get("id", "unknown")
        proposal_type = proposal.get("proposal_type", "")
        target = proposal.get("target", "")
        description = proposal.get("description", "")

        # Combine text for analysis
        full_text = f"{proposal_type} {target} {description}".lower()

        # Check invariants
        touched_invariants = self._check_invariants(full_text)

        # Check structural changes
        is_structural = self._is_structural_change(full_text)

        # Determine risk reasons
        risk_reasons = []

        if touched_invariants:
            risk_reasons.append(
                f"Touches core invariants: {', '.join(touched_invariants)}"
            )

        if is_structural:
            risk_reasons.append("Involves structural workflow changes")

        if proposal_type == "structural_review":
            risk_reasons.append("Classified as structural review by analyzer")

        if proposal_type == "threshold_review":
            risk_reasons.append("Involves threshold values (user requirements)")

        # Determine risk category
        risk_category = self._determine_risk_category(
            touched_invariants, is_structural, proposal_type,
            proposal.get("risk_level", "low")
        )

        # Generate review guidance
        review_guidance = self._generate_guidance(
            risk_category, touched_invariants, is_structural, proposal
        )

        # Determine review priority
        priority_map = {"critical": 1, "high": 2, "medium": 3, "low": 4}
        review_priority = priority_map.get(risk_category, 5)

        return ClassifiedProposal(
            proposal_id=proposal_id,
            proposal_type=proposal_type,
            target=target,
            description=description,
            risk_category=risk_category,
            risk_reasons=risk_reasons,
            touches_invariants=touched_invariants,
            is_structural=is_structural,
            review_priority=review_priority,
            review_guidance=review_guidance,
        )

    # ========================================================================
    # Risk Detection Methods
    # ========================================================================

    def _check_invariants(self, text: str) -> List[str]:
        """Check which core philosophy invariants a proposal might affect."""
        touched = []
        for invariant, keywords in INVARIANT_KEYWORDS.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    touched.append(invariant)
                    break
        return touched

    def _is_structural_change(self, text: str) -> bool:
        """Check if a proposal involves structural workflow changes."""
        for keyword in STRUCTURAL_KEYWORDS:
            if keyword.lower() in text:
                return True
        return False

    def _determine_risk_category(
        self,
        touched_invariants: List[str],
        is_structural: bool,
        proposal_type: str,
        analyzer_risk: str,
    ) -> str:
        """Determine the overall risk category."""
        # Critical: touches any core invariant
        if touched_invariants:
            return "critical"

        # High: structural changes or high-risk flagged by analyzer
        if is_structural or analyzer_risk == "high":
            return "high"

        # Medium: threshold reviews or medium-risk
        if proposal_type == "threshold_review" or analyzer_risk == "medium":
            return "medium"

        # Low: prompt reviews and observations
        return "low"

    def _generate_guidance(
        self,
        risk_category: str,
        touched_invariants: List[str],
        is_structural: bool,
        proposal: Dict,
    ) -> str:
        """Generate human-readable review guidance."""
        if risk_category == "critical":
            invariant_list = ", ".join(touched_invariants)
            return (
                f"CRITICAL: This proposal may affect core philosophy invariants "
                f"({invariant_list}). These are foundational principles that "
                f"should never be changed without deep consideration. Review "
                f"carefully and verify the proposal does not violate these "
                f"principles before taking any manual action."
            )

        if risk_category == "high":
            return (
                "HIGH RISK: This proposal involves significant changes. "
                "Consider the downstream effects on agents and gates that "
                "depend on the affected components. Test any manual changes "
                "on a separate run before applying to the main workflow."
            )

        if risk_category == "medium":
            return (
                "MEDIUM RISK: This proposal suggests adjustments that could "
                "affect quality scores. Review the evidence and consider whether "
                "the issue is topic-specific or systemic before acting."
            )

        return (
            "LOW RISK: This is an observational finding. No immediate action "
            "required, but worth noting for future workflow runs."
        )

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
    """CLI interface for change classifier."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Change Classifier - Advisory risk assessment"
    )
    parser.add_argument(
        "--proposals-file", type=str,
        help="Path to improvement-proposals-*.json"
    )
    parser.add_argument(
        "--output-dir", type=str, default=None,
        help="Output directory for classification report"
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
        print("Change Classifier - Test Mode")
        print("=" * 70)

        # Create mock proposals
        mock_proposals = {
            "run_id": "test-001",
            "proposals": [
                {
                    "id": "IMP-001",
                    "proposal_type": "prompt_review",
                    "target": "Agent: variable-relationship-analyst",
                    "description": "Agent has low pTCS. Consider reviewing prompt clarity.",
                    "risk_level": "medium",
                },
                {
                    "id": "IMP-002",
                    "proposal_type": "threshold_review",
                    "target": "Gate: wave-2",
                    "description": "Gate failed. pTCS weight might need review.",
                    "risk_level": "high",
                },
                {
                    "id": "IMP-003",
                    "proposal_type": "structural_review",
                    "target": "Workflow-wide",
                    "description": "Consider adding a new agent for parallel execution.",
                    "risk_level": "high",
                },
            ],
        }

        import tempfile
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(mock_proposals, f, indent=2)
            temp_path = f.name

        classifier = ChangeClassifier(verbose=True)
        report = classifier.classify(Path(temp_path))
        print(json.dumps(report.to_dict(), indent=2))

        Path(temp_path).unlink()
        return 0

    # Real classification
    try:
        if not args.proposals_file:
            print("Error: --proposals-file is required (or use --test)")
            return 1

        classifier = ChangeClassifier(verbose=not args.quiet)
        report = classifier.classify(Path(args.proposals_file))

        if args.output_dir:
            classifier.save_report(report, Path(args.output_dir))

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error classifying proposals: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
