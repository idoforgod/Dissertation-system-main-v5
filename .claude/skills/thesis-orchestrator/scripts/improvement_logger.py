#!/usr/bin/env python3
"""Improvement Logger: Audit Trail for Performance Analysis.

This module maintains a persistent history of all performance analyses,
proposals, and human decisions. It provides the audit trail needed to
understand how the system has been analyzed over time.

Key principle: This is a WRITE-ONLY APPEND log. It only creates new
entries or updates status of existing entries. It never modifies
any workflow files.

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
HISTORY_FILENAME = "improvement-history.json"

VALID_STATUSES = {
    "proposed",      # Initial state: analysis generated proposal
    "reviewed",      # Human has reviewed the proposal
    "accepted",      # Human accepted (will apply manually)
    "rejected",      # Human rejected (no action)
    "deferred",      # Human deferred to future review
    "noted",         # Informational only, no action needed
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class HistoryEntry:
    """A single entry in the improvement history."""

    # Identity
    entry_id: str
    proposal_id: str
    run_id: str

    # Timestamps
    proposed_at: str
    reviewed_at: Optional[str] = None

    # Proposal info
    proposal_type: str = ""
    target: str = ""
    description: str = ""
    risk_category: str = ""

    # Human decision
    status: str = "proposed"
    decision_by: str = ""  # "human" or empty
    decision_reason: str = ""

    # Metrics context (for trend analysis)
    metrics_at_proposal: Dict[str, Any] = None

    def __post_init__(self):
        if self.metrics_at_proposal is None:
            self.metrics_at_proposal = {}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ImprovementHistory:
    """Complete improvement history."""

    version: str
    last_updated: str
    entries: List[dict]

    # Summary stats
    total_entries: int
    by_status: Dict[str, int]
    by_risk: Dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Improvement Logger
# ============================================================================

class ImprovementLogger:
    """Manages the improvement history audit trail.

    This class:
    - APPENDS new entries to the history
    - UPDATES status of existing entries (proposed → reviewed → accepted/rejected)
    - READS history for reporting
    - NEVER modifies any workflow files

    History file: 00-session/improvement-data/improvement-history.json
    """

    def __init__(self, working_dir: Path, verbose: bool = True):
        """Initialize logger.

        Args:
            working_dir: Project working directory
            verbose: Print detailed logs
        """
        self.working_dir = Path(working_dir).resolve()
        self.history_file = (
            self.working_dir / "00-session" / "improvement-data" / HISTORY_FILENAME
        )
        self.verbose = verbose

    # ========================================================================
    # History Management
    # ========================================================================

    def load_history(self) -> List[dict]:
        """Load existing history entries.

        Returns:
            List of history entry dicts
        """
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("entries", [])
        except (json.JSONDecodeError, OSError) as e:
            self._log(f"Warning: Could not load history: {e}")
            return []

    def log_proposals(
        self,
        proposals: List[dict],
        classifications: List[dict],
        run_id: str,
        metrics_summary: Optional[Dict] = None,
    ) -> List[HistoryEntry]:
        """Log new proposals from an analysis run.

        Args:
            proposals: List of proposal dicts from analyzer
            classifications: List of classified proposal dicts from classifier
            run_id: Run identifier
            metrics_summary: Overall metrics summary for context

        Returns:
            List of new HistoryEntry objects
        """
        self._log(f"\n{'='*70}")
        self._log("IMPROVEMENT LOGGER")
        self._log(f"{'='*70}")

        existing = self.load_history()
        next_id = len(existing) + 1
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Build classification lookup
        class_lookup = {}
        for c in classifications:
            class_lookup[c.get("proposal_id", "")] = c

        new_entries = []
        for proposal in proposals:
            pid = proposal.get("id", "")
            classification = class_lookup.get(pid, {})

            entry = HistoryEntry(
                entry_id=f"HIST-{next_id:04d}",
                proposal_id=pid,
                run_id=run_id,
                proposed_at=now,
                proposal_type=proposal.get("proposal_type", ""),
                target=proposal.get("target", ""),
                description=proposal.get("description", ""),
                risk_category=classification.get("risk_category", "unknown"),
                status="proposed",
                metrics_at_proposal=metrics_summary or {},
            )
            new_entries.append(entry)
            next_id += 1

        # Save updated history
        all_entries = existing + [e.to_dict() for e in new_entries]
        self._save_history(all_entries)

        self._log(f"Logged {len(new_entries)} new proposals (total: {len(all_entries)})")
        return new_entries

    def update_status(
        self,
        entry_id: str,
        new_status: str,
        decision_reason: str = "",
    ) -> bool:
        """Update the status of a history entry.

        Args:
            entry_id: Entry ID (e.g., "HIST-0001")
            new_status: New status (must be in VALID_STATUSES)
            decision_reason: Reason for the decision

        Returns:
            True if updated successfully, False if entry not found
        """
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}. Valid: {VALID_STATUSES}")

        entries = self.load_history()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        for entry in entries:
            if entry.get("entry_id") == entry_id:
                entry["status"] = new_status
                entry["reviewed_at"] = now
                entry["decision_by"] = "human"
                entry["decision_reason"] = decision_reason
                self._save_history(entries)
                self._log(f"Updated {entry_id}: {new_status}")
                return True

        self._log(f"Warning: Entry {entry_id} not found")
        return False

    def get_pending_review(self) -> List[dict]:
        """Get all entries pending human review.

        Returns:
            List of entries with status "proposed"
        """
        entries = self.load_history()
        return [e for e in entries if e.get("status") == "proposed"]

    def get_summary(self) -> ImprovementHistory:
        """Get a summary of the improvement history.

        Returns:
            ImprovementHistory with summary statistics
        """
        entries = self.load_history()

        # Count by status
        by_status = {}
        for entry in entries:
            status = entry.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1

        # Count by risk
        by_risk = {}
        for entry in entries:
            risk = entry.get("risk_category", "unknown")
            by_risk[risk] = by_risk.get(risk, 0) + 1

        return ImprovementHistory(
            version=VERSION,
            last_updated=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            entries=entries,
            total_entries=len(entries),
            by_status=by_status,
            by_risk=by_risk,
        )

    # ========================================================================
    # Persistence
    # ========================================================================

    def _save_history(self, entries: List[dict]):
        """Save history entries to file."""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # Count by status and risk
        by_status = {}
        by_risk = {}
        for entry in entries:
            status = entry.get("status", "unknown")
            by_status[status] = by_status.get(status, 0) + 1
            risk = entry.get("risk_category", "unknown")
            by_risk[risk] = by_risk.get(risk, 0) + 1

        history = ImprovementHistory(
            version=VERSION,
            last_updated=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            entries=entries,
            total_entries=len(entries),
            by_status=by_status,
            by_risk=by_risk,
        )

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history.to_dict(), f, indent=2, ensure_ascii=False)

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
    """CLI interface for improvement logger."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Improvement Logger - Audit trail management"
    )
    parser.add_argument(
        "--working-dir", type=str, default=None,
        help="Working directory"
    )
    parser.add_argument(
        "--summary", action="store_true",
        help="Show history summary"
    )
    parser.add_argument(
        "--pending", action="store_true",
        help="Show pending reviews"
    )
    parser.add_argument(
        "--update", type=str, default=None,
        help="Update entry status (format: ENTRY_ID:STATUS[:REASON])"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run test"
    )

    args = parser.parse_args()

    if args.test:
        print("\n" + "=" * 70)
        print("Improvement Logger - Test Mode")
        print("=" * 70)

        import tempfile
        temp_dir = Path(tempfile.mkdtemp())
        (temp_dir / "00-session" / "improvement-data").mkdir(parents=True)

        logger = ImprovementLogger(working_dir=temp_dir, verbose=True)

        # Log some proposals
        proposals = [
            {"id": "IMP-001", "proposal_type": "prompt_review",
             "target": "Agent: test", "description": "Test proposal 1"},
            {"id": "IMP-002", "proposal_type": "structural_review",
             "target": "Workflow", "description": "Test proposal 2"},
        ]
        classifications = [
            {"proposal_id": "IMP-001", "risk_category": "low"},
            {"proposal_id": "IMP-002", "risk_category": "high"},
        ]

        logger.log_proposals(proposals, classifications, "test-001")

        # Show summary
        summary = logger.get_summary()
        print(f"\nTotal entries: {summary.total_entries}")
        print(f"By status: {summary.by_status}")
        print(f"By risk: {summary.by_risk}")

        # Update one entry
        logger.update_status("HIST-0001", "accepted", "Looks good")

        # Show pending
        pending = logger.get_pending_review()
        print(f"\nPending review: {len(pending)}")

        # Clean up
        import shutil
        shutil.rmtree(temp_dir)
        return 0

    # Real operations
    try:
        from path_utils import get_working_dir_from_session

        if args.working_dir:
            working_dir = Path(args.working_dir).resolve()
        else:
            working_dir = get_working_dir_from_session()

        logger = ImprovementLogger(working_dir=working_dir)

        if args.summary:
            summary = logger.get_summary()
            print(json.dumps(summary.to_dict(), indent=2, ensure_ascii=False))
        elif args.pending:
            pending = logger.get_pending_review()
            print(json.dumps(pending, indent=2, ensure_ascii=False))
        elif args.update:
            parts = args.update.split(":")
            if len(parts) < 2:
                print("Error: Format is ENTRY_ID:STATUS[:REASON]")
                return 1
            entry_id = parts[0]
            status = parts[1]
            reason = parts[2] if len(parts) > 2 else ""
            success = logger.update_status(entry_id, status, reason)
            return 0 if success else 1
        else:
            parser.print_help()

        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
