#!/usr/bin/env python3
"""Test Progressive Compressor."""

from pathlib import Path
from progressive_compressor import ProgressiveCompressor

# Test data
AGENT_OUTPUT = """# Literature Search Results

## Search Strategy
- Databases: Web of Science, Scopus, PubMed
- Keywords: "AI consciousness", "machine sentience", "artificial self-awareness"
- Date range: 2010-2025
- Total papers: 847

## Key Findings

### Empirical Studies (n=234)
1. Neural correlates of consciousness in AI systems
2. Self-modeling in large language models
3. Metacognitive awareness in reinforcement learning agents

### Theoretical Frameworks (n=312)
1. Integrated Information Theory (IIT) applications to AI
2. Global Workspace Theory (GWT) in neural networks
3. Higher-order thought theories for machine consciousness

### Critical Reviews (n=301)
1. Philosophical objections to AI consciousness
2. Hard problem of consciousness in artificial systems
3. Chinese Room argument applications

## Top 20 Seminal Papers
1. Dehaene et al. (2017) - "What is consciousness, and could machines have it?"
2. Koch & Tononi (2015) - "Integrated Information Theory"
3. Chalmers (2010) - "The Singularity: A philosophical analysis"
... (continues for 2500 more tokens)
"""

def main():
    # Setup
    working_dir = Path("/Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v1/thesis-output/test-memory-arch")
    compressor = ProgressiveCompressor(working_dir)

    print("\n" + "="*70)
    print("TESTING PROGRESSIVE COMPRESSOR")
    print("="*70 + "\n")

    # Test 1: Agent Checkpoint
    print("\n" + "="*70)
    print("TEST 1: AGENT CHECKPOINT")
    print("="*70)

    agent_summary = compressor.compress_on_agent_complete(
        agent_name="literature-searcher",
        full_output=AGENT_OUTPUT,
        phase=1,
        wave=1
    )

    print(f"\nAgent Summary:")
    print(f"  Name: {agent_summary.agent_name}")
    print(f"  Summary: {agent_summary.summary[:100]}...")
    print(f"  Key Findings: {len(agent_summary.key_findings)}")

    # Test 2: Wave Checkpoint
    print("\n" + "="*70)
    print("TEST 2: WAVE CHECKPOINT")
    print("="*70)

    # Add more agents to make it realistic
    for agent in ["seminal-works-analyst", "trend-analyst", "methodology-scanner"]:
        compressor.compress_on_agent_complete(
            agent_name=agent,
            full_output=AGENT_OUTPUT,  # Same output for testing
            phase=1,
            wave=1
        )

    wave_cache = compressor.compress_on_wave_complete(
        wave_number=1,
        phase=1,
        gate_passed=True,
        gate_scores={"pTCS": 85.0, "SRCS": 78.5}
    )

    print(f"\nWave Cache:")
    print(f"  Wave: {wave_cache.wave}")
    print(f"  Agents: {len(wave_cache.agents)}")
    print(f"  Gate passed: {wave_cache.gate_passed}")

    # Test 3: Show Stats
    print("\n" + "="*70)
    print("TEST 3: COMPRESSION STATISTICS")
    print("="*70 + "\n")

    stats = compressor.get_compression_stats()

    print("Memory Usage:")
    for key, value in stats["memory_usage"].items():
        print(f"  {key}: {value}")

    print("\nCompression:")
    for key, value in stats["compression"].items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
