#!/usr/bin/env python3
"""Sliding Window Context Manager.

Implements a sliding window pattern that keeps only the N most recent
agent outputs in full context, while older outputs are compressed to
summaries. This maintains constant memory usage regardless of workflow length.

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │  Sliding Window Pattern (Window Size = 3)               │
    ├─────────────────────────────────────────────────────────┤
    │  Agent 1 output (full)  ← Window                        │
    │  Agent 2 output (full)  ← Window                        │
    │  Agent 3 output (full)  ← Window                        │
    │      ↓ [Agent 4 arrives]                                │
    │  Agent 1 output → Compressed (summary)                  │
    │  Agent 2 output (full)  ← Window                        │
    │  Agent 3 output (full)  ← Window                        │
    │  Agent 4 output (full)  ← Window                        │
    │      ↓ [Agent 5 arrives]                                │
    │  Agent 2 output → Compressed (summary)                  │
    │  Agent 3 output (full)  ← Window                        │
    │  Agent 4 output (full)  ← Window                        │
    │  Agent 5 output (full)  ← Window                        │
    └─────────────────────────────────────────────────────────┘

Memory:
    Full outputs: 3 × 3,000 = 9,000 tokens (constant)
    Compressed: N × 50 = variable (grows slowly)
    Total: ~9,000 + (N × 50) tokens

Usage:
    window = SlidingWindowContext(
        working_dir="thesis-output/project",
        window_size=3
    )

    # Add new agent output
    window.add_agent_output(
        agent_name="literature-searcher",
        full_output=output_text,
        phase=1,
        wave=1
    )

    # Get current context
    context = window.get_current_context()
    # Returns: {
    #   'recent_full': [...],  # 3 most recent full outputs
    #   'compressed': [...],   # Older compressed summaries
    #   'total_memory': 9150   # tokens
    # }

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import deque

# Import MemoryManager for compression
from memory_manager import MemoryManager, AgentSummary


@dataclass
class WindowedOutput:
    """Output with window metadata."""

    agent_name: str
    phase: int
    wave: int
    full_output: str
    timestamp: str
    tokens: int
    in_window: bool  # True if in active window

    def to_dict(self) -> dict:
        return asdict(self)


class SlidingWindowContext:
    """Sliding window context manager."""

    DEFAULT_WINDOW_SIZE = 3  # Keep 3 most recent full outputs

    def __init__(
        self,
        working_dir: Path,
        window_size: int = DEFAULT_WINDOW_SIZE
    ):
        """Initialize sliding window context.

        Args:
            working_dir: Project working directory
            window_size: Number of recent outputs to keep in full
        """
        self.working_dir = Path(working_dir)
        self.window_size = window_size

        # Memory directories
        self.memory_dir = self.working_dir / "memory"
        self.window_dir = self.memory_dir / "sliding-window"
        self.window_dir.mkdir(parents=True, exist_ok=True)

        # Initialize MemoryManager for compression
        self.manager = MemoryManager(working_dir=self.working_dir)

        # Sliding window (deque for efficient push/pop)
        self.window: deque = deque(maxlen=window_size)

        # Compressed outputs (outside window)
        self.compressed_outputs: List[AgentSummary] = []

        # Tracking
        self.total_outputs_processed = 0
        self.window_slides = 0

        # Load state if exists
        self._load_state()

    def _load_state(self):
        """Load window state from disk."""
        state_file = self.window_dir / "window_state.json"

        if state_file.exists():
            with open(state_file) as f:
                state = json.load(f)

                # Restore window
                for output_data in state.get("window", []):
                    self.window.append(WindowedOutput(**output_data))

                # Restore compressed outputs
                for summary_data in state.get("compressed_outputs", []):
                    self.compressed_outputs.append(AgentSummary(**summary_data))

                # Restore counters
                self.total_outputs_processed = state.get("total_outputs_processed", 0)
                self.window_slides = state.get("window_slides", 0)

    def _save_state(self):
        """Save window state to disk."""
        state_file = self.window_dir / "window_state.json"

        state = {
            "window": [output.to_dict() for output in self.window],
            "compressed_outputs": [asdict(summary) for summary in self.compressed_outputs],
            "total_outputs_processed": self.total_outputs_processed,
            "window_slides": self.window_slides,
            "window_size": self.window_size,
            "timestamp": datetime.now().isoformat()
        }

        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def add_agent_output(
        self,
        agent_name: str,
        full_output: str,
        phase: int,
        wave: int
    ) -> Dict[str, Any]:
        """Add new agent output to sliding window.

        If window is full, oldest output is compressed and moved out.

        Args:
            agent_name: Agent name
            full_output: Full agent output
            phase: Current phase
            wave: Current wave

        Returns:
            Dictionary with window status
        """
        print(f"\n[SLIDING WINDOW] Adding {agent_name}...")

        # Create windowed output
        tokens = len(full_output.split())
        windowed_output = WindowedOutput(
            agent_name=agent_name,
            phase=phase,
            wave=wave,
            full_output=full_output,
            timestamp=datetime.now().isoformat(),
            tokens=tokens,
            in_window=True
        )

        # Check if window is full
        if len(self.window) == self.window_size:
            # Window is full - need to slide
            print(f"  [Window full] Sliding window...")

            # Remove oldest from window
            oldest = self.window[0]  # Will be auto-removed by deque
            oldest.in_window = False

            # Compress oldest output
            print(f"  [Compress] Compressing {oldest.agent_name}...")
            compressed = self.manager.compress_agent_output(
                agent_name=oldest.agent_name,
                full_output=oldest.full_output
            )

            # Add to compressed outputs
            self.compressed_outputs.append(compressed)

            # Archive full output
            archive_file = self.window_dir / f"archived_{oldest.agent_name}.md"
            with open(archive_file, 'w') as f:
                f.write(oldest.full_output)

            self.window_slides += 1
            print(f"  [Slide] Window slid ({self.window_slides} total slides)")

        # Add new output to window
        self.window.append(windowed_output)
        self.total_outputs_processed += 1

        # Save state
        self._save_state()

        # Calculate current memory
        window_memory = sum(o.tokens for o in self.window)
        compressed_memory = len(self.compressed_outputs) * 50  # 50 tokens each
        total_memory = window_memory + compressed_memory

        result = {
            "agent_name": agent_name,
            "window_position": len(self.window),
            "window_size": self.window_size,
            "window_full": len(self.window) == self.window_size,
            "compressed_count": len(self.compressed_outputs),
            "memory": {
                "window": window_memory,
                "compressed": compressed_memory,
                "total": total_memory
            }
        }

        print(f"  [Added] Position {len(self.window)}/{self.window_size}")
        print(f"  [Memory] Window: {window_memory:,} | Compressed: {compressed_memory:,} | Total: {total_memory:,}")

        return result

    def get_current_context(self) -> Dict[str, Any]:
        """Get current context with sliding window.

        Returns:
            Dictionary with full window outputs and compressed summaries
        """
        # Full outputs in window (most recent first)
        recent_full = [
            {
                "agent_name": output.agent_name,
                "phase": output.phase,
                "wave": output.wave,
                "output": output.full_output,
                "tokens": output.tokens
            }
            for output in reversed(self.window)  # Most recent first
        ]

        # Compressed summaries (oldest to newest)
        compressed = [
            {
                "agent_name": summary.agent_name,
                "summary": summary.summary,
                "key_findings": summary.key_findings,
                "tokens": 50  # Ultra-compact
            }
            for summary in self.compressed_outputs
        ]

        # Memory calculation
        window_memory = sum(o.tokens for o in self.window)
        compressed_memory = len(self.compressed_outputs) * 50
        total_memory = window_memory + compressed_memory

        return {
            "recent_full": recent_full,
            "compressed": compressed,
            "window_status": {
                "current_size": len(self.window),
                "max_size": self.window_size,
                "is_full": len(self.window) == self.window_size,
                "slides_count": self.window_slides
            },
            "memory": {
                "window": window_memory,
                "compressed": compressed_memory,
                "total": total_memory
            },
            "stats": {
                "total_outputs_processed": self.total_outputs_processed,
                "in_window": len(self.window),
                "compressed": len(self.compressed_outputs)
            }
        }

    def get_window_stats(self) -> Dict[str, Any]:
        """Get window statistics.

        Returns:
            Dictionary with window stats
        """
        context = self.get_current_context()

        return {
            "window_size": self.window_size,
            "current_in_window": len(self.window),
            "compressed_count": len(self.compressed_outputs),
            "total_processed": self.total_outputs_processed,
            "window_slides": self.window_slides,
            "memory_usage": context["memory"],
            "efficiency": {
                "baseline_memory": self.total_outputs_processed * 3000,
                "actual_memory": context["memory"]["total"],
                "reduction": (
                    1 - context["memory"]["total"] / max(1, self.total_outputs_processed * 3000)
                ) if self.total_outputs_processed > 0 else 0
            }
        }

    def clear_window(self):
        """Clear the entire window (compress all)."""
        print(f"\n[CLEAR WINDOW] Compressing all {len(self.window)} outputs...")

        for output in self.window:
            compressed = self.manager.compress_agent_output(
                agent_name=output.agent_name,
                full_output=output.full_output
            )
            self.compressed_outputs.append(compressed)

        self.window.clear()
        self._save_state()

        print(f"  [Cleared] All outputs compressed")


def main():
    """CLI interface for testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Sliding Window Context Manager"
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        required=True,
        help="Project working directory"
    )
    parser.add_argument(
        "--window-size",
        type=int,
        default=3,
        help="Window size (default 3)"
    )
    parser.add_argument(
        "--num-agents",
        type=int,
        default=10,
        help="Number of agents to simulate"
    )

    args = parser.parse_args()

    # Initialize sliding window
    window = SlidingWindowContext(
        working_dir=args.working_dir,
        window_size=args.window_size
    )

    print(f"\n{'='*70}")
    print(f"SLIDING WINDOW CONTEXT TEST")
    print(f"{'='*70}\n")

    print(f"Window size: {args.window_size}")
    print(f"Simulating: {args.num_agents} agents")

    # Simulate adding multiple agent outputs
    for i in range(args.num_agents):
        agent_name = f"agent-{i+1}"
        mock_output = f"# Agent {i+1} Output\n\n" + "." * 500  # Mock ~500 tokens

        result = window.add_agent_output(
            agent_name=agent_name,
            full_output=mock_output,
            phase=1,
            wave=(i // 4) + 1
        )

        print()  # Spacing

    # Show final stats
    print(f"\n{'='*70}")
    print(f"FINAL STATISTICS")
    print(f"{'='*70}\n")

    stats = window.get_window_stats()

    print(f"Window Configuration:")
    print(f"  Window size: {stats['window_size']}")
    print(f"  Current in window: {stats['current_in_window']}")
    print(f"  Compressed: {stats['compressed_count']}")
    print(f"  Total processed: {stats['total_processed']}")
    print(f"  Window slides: {stats['window_slides']}")

    print(f"\nMemory Usage:")
    print(f"  Window: {stats['memory_usage']['window']:,} tokens")
    print(f"  Compressed: {stats['memory_usage']['compressed']:,} tokens")
    print(f"  Total: {stats['memory_usage']['total']:,} tokens")

    print(f"\nEfficiency:")
    print(f"  Baseline memory: {stats['efficiency']['baseline_memory']:,} tokens")
    print(f"  Actual memory: {stats['efficiency']['actual_memory']:,} tokens")
    print(f"  Reduction: {stats['efficiency']['reduction']*100:.1f}%")

    # Show current context
    print(f"\n{'='*70}")
    print(f"CURRENT CONTEXT")
    print(f"{'='*70}\n")

    context = window.get_current_context()

    print(f"Recent Full Outputs ({len(context['recent_full'])}):")
    for output in context['recent_full']:
        print(f"  - {output['agent_name']} (Phase {output['phase']}, Wave {output['wave']}) - {output['tokens']:,} tokens")

    print(f"\nCompressed Outputs ({len(context['compressed'])}):")
    for comp in context['compressed'][:5]:  # Show first 5
        print(f"  - {comp['agent_name']} - {comp['summary'][:50]}...")
    if len(context['compressed']) > 5:
        print(f"  ... and {len(context['compressed']) - 5} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
