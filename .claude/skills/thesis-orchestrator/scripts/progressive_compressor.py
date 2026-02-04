#!/usr/bin/env python3
"""Progressive Compression Pipeline for Thesis Workflow.

Implements automatic compression at three checkpoints:
1. Agent Checkpoint: 3,000 tokens → 50 tokens (98.3% compression)
2. Wave Checkpoint: 12,000 tokens → 500 tokens (95.8% compression)
3. Phase Checkpoint: 45,000 tokens → 2,000 tokens (95.6% compression)

This ensures bounded memory usage throughout the workflow.

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │  Progressive Compression Pipeline                       │
    ├─────────────────────────────────────────────────────────┤
    │  Agent Output (3k tokens)                               │
    │      ↓ [Agent Checkpoint]                               │
    │  Ultra-Compact Summary (50 tokens) → session.json       │
    │      ↓                                                   │
    │  Wave Outputs (12k tokens)                              │
    │      ↓ [Wave Checkpoint]                                │
    │  Wave Cache (500 tokens) → wave-cache/wave-N.json       │
    │      ↓                                                   │
    │  Phase Outputs (45k tokens)                             │
    │      ↓ [Phase Checkpoint]                               │
    │  Phase Synthesis (2k tokens) → phase-N-synthesis.md     │
    └─────────────────────────────────────────────────────────┘

Usage:
    compressor = ProgressiveCompressor(working_dir="thesis-output/project")

    # Agent checkpoint
    compressor.compress_on_agent_complete(
        agent_name="literature-searcher",
        full_output=agent_output,
        phase=1,
        wave=1
    )

    # Wave checkpoint
    compressor.compress_on_wave_complete(
        wave_number=1,
        phase=1
    )

    # Phase checkpoint
    compressor.compress_on_phase_complete(
        phase_number=1
    )

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict

# Import MemoryManager from Phase A-1
from memory_manager import (
    MemoryManager,
    AgentSummary,
    WaveCache,
    PhaseSynthesis
)


class ProgressiveCompressor:
    """Progressive compression at agent/wave/phase checkpoints."""

    def __init__(self, working_dir: Path):
        """Initialize compressor.

        Args:
            working_dir: Project working directory (thesis-output/project/)
        """
        self.working_dir = Path(working_dir)
        self.memory_dir = self.working_dir / "memory"
        self.temp_dir = self.working_dir / "_temp"
        self.archive_dir = self.working_dir / "_archive"

        # Initialize MemoryManager
        self.manager = MemoryManager(working_dir=self.working_dir, max_budget=50000)

        # Load session state
        self.session_file = self.memory_dir / "session.json"
        self.session = self._load_session()

        # Load memory budget
        self.budget_file = self.memory_dir / "memory-budget.json"
        self.budget = self._load_budget()

        # Tracking
        self.agent_outputs: Dict[int, Dict[int, List[str]]] = {}  # phase -> wave -> [outputs]

    def _load_session(self) -> Dict[str, Any]:
        """Load session.json."""
        if not self.session_file.exists():
            raise FileNotFoundError(f"session.json not found: {self.session_file}")

        with open(self.session_file) as f:
            return json.load(f)

    def _save_session(self):
        """Save session.json."""
        with open(self.session_file, 'w') as f:
            json.dump(self.session, f, indent=2)

    def _load_budget(self) -> Dict[str, Any]:
        """Load memory-budget.json."""
        if not self.budget_file.exists():
            raise FileNotFoundError(f"memory-budget.json not found: {self.budget_file}")

        with open(self.budget_file) as f:
            return json.load(f)

    def _save_budget(self):
        """Save memory-budget.json."""
        with open(self.budget_file, 'w') as f:
            json.dump(self.budget, f, indent=2)

    def _update_budget(self, tokens_added: int, phase: int):
        """Update memory budget tracking.

        Args:
            tokens_added: Tokens added to context
            phase: Current phase number
        """
        # Update current usage
        self.budget["budget"]["current_usage"] += tokens_added
        self.budget["budget"]["remaining"] = (
            self.budget["budget"]["max_tokens"] - self.budget["budget"]["current_usage"]
        )
        self.budget["budget"]["utilization"] = (
            self.budget["budget"]["current_usage"] / self.budget["budget"]["max_tokens"]
        )

        # Update phase usage
        phase_key = f"phase_{phase}"
        if phase_key in self.budget["by_phase"]:
            self.budget["by_phase"][phase_key] += tokens_added

        # Add history entry
        self.budget["history"].append({
            "timestamp": datetime.now().isoformat(),
            "event": "compression_checkpoint",
            "usage": self.budget["budget"]["current_usage"],
            "phase": phase
        })

        # Check for alerts
        utilization = self.budget["budget"]["utilization"]
        if utilization > 0.9:
            self.budget["alerts"].append({
                "level": "critical",
                "message": f"Memory usage at {utilization*100:.1f}% (> 90%)",
                "timestamp": datetime.now().isoformat()
            })
        elif utilization > 0.75:
            self.budget["alerts"].append({
                "level": "warning",
                "message": f"Memory usage at {utilization*100:.1f}% (> 75%)",
                "timestamp": datetime.now().isoformat()
            })

        self._save_budget()

    def compress_on_agent_complete(
        self,
        agent_name: str,
        full_output: str,
        phase: int,
        wave: int
    ) -> AgentSummary:
        """Checkpoint 1: Compress agent output to ultra-compact summary.

        Compression: 3,000 tokens → 50 tokens (98.3% reduction)

        Args:
            agent_name: Agent name (e.g., "literature-searcher")
            full_output: Full agent output (markdown)
            phase: Current phase number (0-4)
            wave: Current wave number (1-5)

        Returns:
            AgentSummary with ultra-compact summary
        """
        print(f"\n{'='*70}")
        print(f"🗜️  AGENT CHECKPOINT: {agent_name}")
        print(f"{'='*70}\n")

        # 1. Compress using MemoryManager
        print(f"[1/4] Compressing output...")
        summary = self.manager.compress_agent_output(agent_name, full_output)
        print(f"  ✓ Compressed: {summary.tokens_compressed} → {len(summary.summary.split())} tokens")
        print(f"  ✓ Ratio: {summary.compression_ratio:.1%}")

        # 2. Archive full output to _temp/
        print(f"\n[2/4] Archiving full output...")
        temp_file = self.temp_dir / f"phase{phase}_wave{wave}_{agent_name}.md"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_file, 'w') as f:
            f.write(full_output)
        print(f"  ✓ Archived: {temp_file.relative_to(self.working_dir.parent)}")

        # 3. Update session.json with agent summary
        print(f"\n[3/4] Updating session.json...")
        self.session["agent_summaries"][agent_name] = asdict(summary)
        self.session["current_agent"] = agent_name
        self.session["current_phase"] = phase
        self.session["current_wave"] = wave
        self.session["project"]["last_updated"] = datetime.now().isoformat()
        self._save_session()
        print(f"  ✓ Updated: agent_summaries['{agent_name}']")

        # 4. Update memory budget
        print(f"\n[4/4] Updating memory budget...")
        # Add only the compressed summary tokens to budget
        tokens_added = len(summary.summary.split())
        self._update_budget(tokens_added, phase)
        print(f"  ✓ Budget: +{tokens_added} tokens")
        print(f"  ✓ Total usage: {self.budget['budget']['current_usage']:,} / {self.budget['budget']['max_tokens']:,}")

        # Track for wave compression
        if phase not in self.agent_outputs:
            self.agent_outputs[phase] = {}
        if wave not in self.agent_outputs[phase]:
            self.agent_outputs[phase][wave] = []
        self.agent_outputs[phase][wave].append(agent_name)

        print(f"\n{'='*70}")
        print(f"✅ AGENT CHECKPOINT COMPLETE: {agent_name}")
        print(f"{'='*70}\n")

        return summary

    def compress_on_wave_complete(
        self,
        wave_number: int,
        phase: int,
        gate_passed: bool = True,
        gate_scores: Optional[Dict[str, float]] = None
    ) -> WaveCache:
        """Checkpoint 2: Compress wave outputs to wave cache.

        Compression: 12,000 tokens → 500 tokens (95.8% reduction)

        Args:
            wave_number: Wave number (1-5)
            phase: Current phase number (0-4)
            gate_passed: Whether gate validation passed
            gate_scores: Optional gate validation scores

        Returns:
            WaveCache with compressed wave summary
        """
        print(f"\n{'='*70}")
        print(f"🗜️  WAVE CHECKPOINT: Wave {wave_number} (Phase {phase})")
        print(f"{'='*70}\n")

        # 1. Collect agent summaries for this wave
        print(f"[1/4] Collecting agent summaries...")
        if phase not in self.agent_outputs or wave_number not in self.agent_outputs[phase]:
            raise ValueError(f"No agent outputs found for Phase {phase}, Wave {wave_number}")

        agent_names = self.agent_outputs[phase][wave_number]
        agent_summaries = []
        for agent_name in agent_names:
            if agent_name in self.session["agent_summaries"]:
                agent_summaries.append(self.session["agent_summaries"][agent_name])

        print(f"  ✓ Collected {len(agent_summaries)} agent summaries")

        # 2. Compress using MemoryManager
        print(f"\n[2/4] Compressing to wave cache...")
        wave_cache = self.manager.compress_wave(
            wave_number=wave_number,
            agent_outputs=agent_summaries,
            gate_passed=gate_passed,
            gate_scores=gate_scores or {}
        )
        print(f"  ✓ Compressed: {wave_cache.tokens_compressed} → ~500 tokens")
        print(f"  ✓ Ratio: {wave_cache.compression_ratio:.1%}")

        # 3. Save wave cache to wave-cache/
        print(f"\n[3/4] Saving wave cache...")
        wave_cache_file = self.memory_dir / "wave-cache" / f"wave-{wave_number}.json"
        wave_cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(wave_cache_file, 'w') as f:
            json.dump(asdict(wave_cache), f, indent=2)
        print(f"  ✓ Saved: {wave_cache_file.relative_to(self.working_dir.parent)}")

        # 4. Update memory budget
        print(f"\n[4/4] Updating memory budget...")
        tokens_added = 500  # Wave cache max size
        self._update_budget(tokens_added, phase)

        # Update compression stats
        total_agent_tokens = sum(s["tokens_compressed"] for s in agent_summaries)
        self.budget["compression_stats"]["total_outputs"] += total_agent_tokens
        self.budget["compression_stats"]["compressed_to"] += 500
        self.budget["compression_stats"]["compression_ratio"] = (
            self.budget["compression_stats"]["compressed_to"] /
            max(1, self.budget["compression_stats"]["total_outputs"])
        )
        self.budget["compression_stats"]["savings"] = (
            f"{(1 - self.budget['compression_stats']['compression_ratio']) * 100:.1f}%"
        )
        self._save_budget()

        print(f"  ✓ Budget: +{tokens_added} tokens")
        print(f"  ✓ Compression savings: {self.budget['compression_stats']['savings']}")

        print(f"\n{'='*70}")
        print(f"✅ WAVE CHECKPOINT COMPLETE: Wave {wave_number}")
        print(f"{'='*70}\n")

        return wave_cache

    def compress_on_phase_complete(
        self,
        phase_number: int,
        quality_metrics: Optional[Dict[str, float]] = None,
        research_questions: Optional[List[str]] = None
    ) -> PhaseSynthesis:
        """Checkpoint 3: Compress phase outputs to phase synthesis.

        Compression: 45,000 tokens → 2,000 tokens (95.6% reduction)

        Args:
            phase_number: Phase number (0-4)
            quality_metrics: Optional quality metrics (pTCS, SRCS)
            research_questions: Optional research questions derived

        Returns:
            PhaseSynthesis with compressed phase summary
        """
        print(f"\n{'='*70}")
        print(f"🗜️  PHASE CHECKPOINT: Phase {phase_number}")
        print(f"{'='*70}\n")

        # 1. Collect wave caches for this phase
        print(f"[1/4] Collecting wave caches...")
        wave_caches = []
        wave_cache_dir = self.memory_dir / "wave-cache"

        # Find all wave caches for this phase
        for wave_file in sorted(wave_cache_dir.glob("wave-*.json")):
            with open(wave_file) as f:
                wave_data = json.load(f)
                wave_caches.append(wave_data)

        print(f"  ✓ Collected {len(wave_caches)} wave caches")

        # 2. Compress using MemoryManager
        print(f"\n[2/4] Compressing to phase synthesis...")
        phase_synthesis = self.manager.compress_phase(
            phase_number=phase_number,
            wave_caches=wave_caches,
            quality_metrics=quality_metrics or {},
            research_questions=research_questions or []
        )
        print(f"  ✓ Compressed: {phase_synthesis.tokens_compressed} → ~2,000 tokens")
        print(f"  ✓ Ratio: {phase_synthesis.compression_ratio:.1%}")

        # 3. Save phase synthesis
        print(f"\n[3/4] Saving phase synthesis...")
        synthesis_file = self.memory_dir / f"phase-{phase_number}-synthesis.md"
        with open(synthesis_file, 'w') as f:
            f.write(phase_synthesis.key_findings)
        print(f"  ✓ Saved: {synthesis_file.relative_to(self.working_dir.parent)}")

        # 4. Update memory budget
        print(f"\n[4/4] Updating memory budget...")
        tokens_added = 2000  # Phase synthesis max size
        self._update_budget(tokens_added, phase_number)

        # Archive old wave caches (move to _archive/)
        print(f"\n[Bonus] Archiving wave caches...")
        archive_wave_dir = self.archive_dir / f"phase-{phase_number}" / "wave-cache"
        archive_wave_dir.mkdir(parents=True, exist_ok=True)
        for wave_file in wave_cache_dir.glob("wave-*.json"):
            archive_file = archive_wave_dir / wave_file.name
            wave_file.rename(archive_file)
            print(f"  ✓ Archived: {wave_file.name}")

        print(f"\n{'='*70}")
        print(f"✅ PHASE CHECKPOINT COMPLETE: Phase {phase_number}")
        print(f"   Memory usage: {self.budget['budget']['current_usage']:,} / {self.budget['budget']['max_tokens']:,}")
        print(f"   Utilization: {self.budget['budget']['utilization']*100:.1f}%")
        print(f"{'='*70}\n")

        return phase_synthesis

    def get_compression_stats(self) -> Dict[str, Any]:
        """Get current compression statistics.

        Returns:
            Dictionary with compression stats
        """
        return {
            "memory_usage": {
                "current": self.budget["budget"]["current_usage"],
                "max": self.budget["budget"]["max_tokens"],
                "remaining": self.budget["budget"]["remaining"],
                "utilization": f"{self.budget['budget']['utilization']*100:.1f}%"
            },
            "compression": {
                "total_outputs": self.budget["compression_stats"]["total_outputs"],
                "compressed_to": self.budget["compression_stats"]["compressed_to"],
                "ratio": f"{self.budget['compression_stats']['compression_ratio']:.1%}",
                "savings": self.budget["compression_stats"]["savings"]
            },
            "by_phase": self.budget["by_phase"],
            "alerts": self.budget["alerts"][-5:]  # Last 5 alerts
        }


def main():
    """CLI interface for testing."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Progressive Compression Pipeline"
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        required=True,
        help="Project working directory"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show compression statistics"
    )

    args = parser.parse_args()

    compressor = ProgressiveCompressor(working_dir=args.working_dir)

    if args.stats:
        stats = compressor.get_compression_stats()
        print("\n" + "="*70)
        print("COMPRESSION STATISTICS")
        print("="*70 + "\n")

        print("Memory Usage:")
        for key, value in stats["memory_usage"].items():
            print(f"  {key}: {value}")

        print("\nCompression:")
        for key, value in stats["compression"].items():
            print(f"  {key}: {value}")

        print("\nBy Phase:")
        for phase, tokens in stats["by_phase"].items():
            print(f"  {phase}: {tokens:,} tokens")

        if stats["alerts"]:
            print("\nRecent Alerts:")
            for alert in stats["alerts"]:
                print(f"  [{alert['level'].upper()}] {alert['message']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
