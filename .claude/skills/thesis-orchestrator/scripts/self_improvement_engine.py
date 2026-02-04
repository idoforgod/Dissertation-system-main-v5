#!/usr/bin/env python3
"""Self-Improvement Engine: Advisory Performance Analysis Orchestrator.

This module orchestrates the ADVISORY self-improvement pipeline:
1. Collect performance metrics (read-only)
2. Analyze metrics and generate proposals (advisory)
3. Classify proposals by risk level (advisory)
4. Log everything to audit trail
5. Generate human-readable summary report

IMPORTANT: This engine does NOT modify any existing workflow files.
All output is advisory, intended for human review and decision-making.
The human operator decides which (if any) proposals to act on.

Safety guarantee: No file in the existing workflow is ever modified
by this engine. It only READS existing data and CREATES new report
files in the improvement-data/ directory.

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-31
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from path_utils import get_working_dir_from_session
from performance_collector import PerformanceCollector
from improvement_analyzer import ImprovementAnalyzer
from change_classifier import ChangeClassifier
from improvement_logger import ImprovementLogger


# ============================================================================
# Constants
# ============================================================================

VERSION = "1.0.0"


# ============================================================================
# Self-Improvement Engine (Advisory Only)
# ============================================================================

class SelfImprovementEngine:
    """Orchestrates the advisory self-improvement pipeline.

    Pipeline:
        Collect → Analyze → Classify → Log → Report

    All output is ADVISORY. No existing workflow files are modified.
    The human operator makes all decisions about whether to act
    on any proposals.
    """

    def __init__(self, working_dir: Path, verbose: bool = True):
        """Initialize engine.

        Args:
            working_dir: Project working directory
            verbose: Print detailed logs
        """
        self.working_dir = Path(working_dir).resolve()
        self.verbose = verbose

        # Initialize components
        self.collector = PerformanceCollector(
            working_dir=self.working_dir, verbose=verbose
        )
        self.analyzer = ImprovementAnalyzer(
            working_dir=self.working_dir, verbose=verbose
        )
        self.classifier = ChangeClassifier(verbose=verbose)
        self.logger = ImprovementLogger(
            working_dir=self.working_dir, verbose=verbose
        )

        # Output directory
        self.improvement_dir = (
            self.working_dir / "00-session" / "improvement-data"
        )

    # ========================================================================
    # Full Pipeline
    # ========================================================================

    def run_report(
        self,
        phase: Optional[str] = None,
        wave: Optional[str] = None,
        previous_metrics: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """Run the full advisory pipeline and generate report.

        Args:
            phase: Phase to analyze (None = all)
            wave: Wave to analyze (None = all)
            previous_metrics: Path to previous metrics for comparison

        Returns:
            Summary dict with all results
        """
        self._log(f"\n{'='*70}")
        self._log("SELF-IMPROVEMENT ENGINE (Advisory Mode)")
        self._log(f"{'='*70}")
        self._log(f"Working dir: {self.working_dir}")
        self._log(f"Scope: phase={phase}, wave={wave}")
        self._log(f"Mode: ADVISORY ONLY (no files modified)")
        self._log("")

        results = {
            "version": VERSION,
            "mode": "advisory",
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

        # Step 1: Collect metrics
        self._log("\n--- Step 1/4: Collecting Performance Metrics ---")
        perf_report = self.collector.collect(phase=phase, wave=wave)
        metrics_path = self.collector.save_report(perf_report)
        results["metrics_file"] = str(metrics_path)
        results["metrics_summary"] = perf_report.overall

        # Step 2: Analyze metrics
        self._log("\n--- Step 2/4: Analyzing Metrics ---")
        analysis_report = self.analyzer.analyze(metrics_path)

        # Include historical comparison if previous metrics provided
        if previous_metrics and previous_metrics.exists():
            self._log(f"Comparing with previous: {previous_metrics}")
            with open(metrics_path, 'r', encoding='utf-8') as f:
                current = json.load(f)
            extra = self.analyzer.compare_with_previous(current, previous_metrics)
            if extra:
                for p in extra:
                    p.id = f"IMP-{analysis_report.total_proposals + 1:03d}"
                    analysis_report.proposals.append(p.to_dict())
                    analysis_report.total_proposals += 1

        proposals_path = self.analyzer.save_report(analysis_report)
        results["proposals_file"] = str(proposals_path)
        results["total_proposals"] = analysis_report.total_proposals

        # Step 3: Classify proposals
        self._log("\n--- Step 3/4: Classifying Proposals ---")
        class_report = self.classifier.classify(proposals_path)
        class_path = self.classifier.save_report(class_report, self.improvement_dir)
        results["classification_file"] = str(class_path)
        results["risk_summary"] = {
            "critical": class_report.critical_count,
            "high": class_report.high_count,
            "medium": class_report.medium_count,
            "low": class_report.low_count,
        }
        results["invariants_touched"] = class_report.invariants_touched

        # Step 4: Log to history
        self._log("\n--- Step 4/4: Logging to History ---")
        self.logger.log_proposals(
            proposals=analysis_report.proposals,
            classifications=class_report.classified,
            run_id=perf_report.run_id,
            metrics_summary=perf_report.overall,
        )
        results["history_updated"] = True

        # Generate summary
        summary = self._generate_summary(results, class_report)
        results["summary"] = summary

        # Save summary report
        summary_path = self._save_summary(results, perf_report.run_id)
        results["summary_file"] = str(summary_path)

        self._log(f"\n{'='*70}")
        self._log("ANALYSIS COMPLETE")
        self._log(f"{'='*70}")
        self._log(summary)
        self._log(f"\nAll reports saved to: {self.improvement_dir}")
        self._log(f"Review proposals: /thesis:review-improvements")
        self._log(f"View history: /thesis:improvement-log")

        return results

    # ========================================================================
    # Collect-Only Mode
    # ========================================================================

    def collect_only(
        self,
        phase: Optional[str] = None,
        wave: Optional[str] = None,
    ) -> Path:
        """Run only the metrics collection step.

        Args:
            phase: Phase to analyze
            wave: Wave to analyze

        Returns:
            Path to metrics file
        """
        self._log("\n--- Collect-Only Mode ---")
        report = self.collector.collect(phase=phase, wave=wave)
        return self.collector.save_report(report)

    # ========================================================================
    # Analyze-Only Mode
    # ========================================================================

    def analyze_only(self, metrics_file: Path) -> Path:
        """Run only the analysis step on existing metrics.

        Args:
            metrics_file: Path to metrics file

        Returns:
            Path to proposals file
        """
        self._log("\n--- Analyze-Only Mode ---")
        report = self.analyzer.analyze(metrics_file)
        return self.analyzer.save_report(report)

    # ========================================================================
    # Summary Generation
    # ========================================================================

    def _generate_summary(
        self,
        results: Dict,
        class_report: Any,
    ) -> str:
        """Generate human-readable summary."""
        lines = []
        lines.append("")
        lines.append("=" * 60)
        lines.append("  PERFORMANCE ANALYSIS SUMMARY (Advisory)")
        lines.append("=" * 60)
        lines.append("")

        # Metrics overview
        metrics = results.get("metrics_summary", {})
        if metrics:
            lines.append("Performance Metrics:")
            avg_ptcs = metrics.get("avg_ptcs")
            avg_srcs = metrics.get("avg_srcs")
            if avg_ptcs is not None:
                lines.append(f"  Average pTCS: {avg_ptcs:.1f}/100")
            if avg_srcs is not None:
                lines.append(f"  Average SRCS: {avg_srcs:.1f}/100")
            lines.append(f"  Total retries: {metrics.get('total_retries', 0)}")
            rate = metrics.get('gate_pass_rate')
            if rate is not None:
                lines.append(f"  Gate pass rate: {rate:.0%}")
            lines.append(f"  Completion rate: {metrics.get('completion_rate', 0):.0%}")
            lines.append("")

        # Proposals overview
        risk = results.get("risk_summary", {})
        total = results.get("total_proposals", 0)
        lines.append(f"Improvement Proposals: {total}")
        if total > 0:
            lines.append(f"  Critical: {risk.get('critical', 0)}")
            lines.append(f"  High:     {risk.get('high', 0)}")
            lines.append(f"  Medium:   {risk.get('medium', 0)}")
            lines.append(f"  Low:      {risk.get('low', 0)}")
        lines.append("")

        # Invariant alerts
        invariants = results.get("invariants_touched", {})
        if invariants:
            lines.append("Core Invariant Alerts:")
            for inv, count in invariants.items():
                lines.append(f"  {inv}: {count} proposal(s)")
            lines.append("")

        # Action items
        lines.append("Next Steps:")
        lines.append("  1. Run /thesis:review-improvements to review proposals")
        lines.append("  2. Accept, reject, or defer each proposal")
        lines.append("  3. Manually apply accepted changes if desired")
        lines.append("  4. Run /thesis:improvement-log to view history")
        lines.append("")
        lines.append("NOTE: No workflow files have been modified.")
        lines.append("All proposals are advisory and require human action.")
        lines.append("=" * 60)

        return "\n".join(lines)

    def _save_summary(self, results: Dict, run_id: str) -> Path:
        """Save summary report to file."""
        self.improvement_dir.mkdir(parents=True, exist_ok=True)
        filename = f"analysis-summary-{run_id}.json"
        output_path = self.improvement_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        return output_path

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
    """CLI interface for self-improvement engine."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Self-Improvement Engine - Advisory performance analysis"
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Run full advisory pipeline (collect + analyze + classify + log)"
    )
    parser.add_argument(
        "--collect-only", action="store_true",
        help="Only collect performance metrics"
    )
    parser.add_argument(
        "--analyze-only", type=str, default=None,
        help="Only analyze existing metrics file"
    )
    parser.add_argument(
        "--phase", type=str, default=None,
        help="Phase to analyze (e.g., 'phase1')"
    )
    parser.add_argument(
        "--wave", type=str, default=None,
        help="Wave to analyze (e.g., 'wave1')"
    )
    parser.add_argument(
        "--previous", type=str, default=None,
        help="Previous metrics file for comparison"
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
        help="Run with test mode"
    )

    args = parser.parse_args()

    if args.test:
        print("\n" + "=" * 70)
        print("Self-Improvement Engine - Test Mode")
        print("=" * 70)
        print("\nThis engine runs in ADVISORY mode only.")
        print("It reads existing data and generates reports.")
        print("No workflow files are ever modified.")
        print("\nTo run a full analysis:")
        print("  python3 self_improvement_engine.py --report")
        print("\nTo collect metrics only:")
        print("  python3 self_improvement_engine.py --collect-only")
        print("\nTo analyze existing metrics:")
        print("  python3 self_improvement_engine.py --analyze-only <file>")
        return 0

    # Resolve working directory
    try:
        if args.working_dir:
            working_dir = Path(args.working_dir).resolve()
        else:
            working_dir = get_working_dir_from_session()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    engine = SelfImprovementEngine(
        working_dir=working_dir,
        verbose=not args.quiet,
    )

    try:
        if args.report:
            previous = Path(args.previous) if args.previous else None
            engine.run_report(
                phase=args.phase,
                wave=args.wave,
                previous_metrics=previous,
            )
        elif args.collect_only:
            path = engine.collect_only(phase=args.phase, wave=args.wave)
            print(f"\nMetrics saved: {path}")
        elif args.analyze_only:
            path = engine.analyze_only(Path(args.analyze_only))
            print(f"\nProposals saved: {path}")
        else:
            parser.print_help()
            return 1

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
