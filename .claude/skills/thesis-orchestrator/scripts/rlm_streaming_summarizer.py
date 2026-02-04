#!/usr/bin/env python3
"""RLM Streaming Summary System.

Provides real-time progress monitoring and streaming summaries during
RLM chunk processing. Allows users to see intermediate results and
track progress without waiting for full completion.

Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │  RLM Streaming Pattern                                  │
    ├─────────────────────────────────────────────────────────┤
    │  Chunk 1 Processing → Stream Summary 1                  │
    │      ↓ [Callback]                                       │
    │  Progress Update: 10% complete                          │
    │      ↓                                                   │
    │  Chunk 2 Processing → Stream Summary 2                  │
    │      ↓ [Callback]                                       │
    │  Progress Update: 20% complete                          │
    │      ↓                                                   │
    │  ... (continue for all chunks)                          │
    │      ↓                                                   │
    │  Final Synthesis → Complete                             │
    └─────────────────────────────────────────────────────────┘

Usage:
    # Define callback
    def on_chunk_complete(summary):
        print(f"Chunk {summary.chunk_id} complete!")
        print(f"Key findings: {summary.key_findings}")

    # Create streaming processor
    processor = StreamingRLMProcessor(
        working_dir="thesis-output/project",
        on_chunk_complete=on_chunk_complete
    )

    # Process with real-time updates
    result = processor.process_with_streaming(
        dataset=papers,
        agent_name="literature-searcher-rlm"
    )

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum

# Import RLM processor
from rlm_processor import RLMProcessor, RLMResult


class StreamEventType(Enum):
    """Types of streaming events."""
    STARTED = "started"
    CHUNK_STARTED = "chunk_started"
    CHUNK_PROGRESS = "chunk_progress"
    CHUNK_COMPLETE = "chunk_complete"
    MERGE_STARTED = "merge_started"
    MERGE_COMPLETE = "merge_complete"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class StreamEvent:
    """Streaming event with metadata."""

    event_type: StreamEventType
    timestamp: str
    data: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "data": self.data
        }


@dataclass
class StreamingSummary:
    """Real-time streaming summary for a chunk."""

    chunk_id: int
    chunk_size: int
    progress: float  # 0.0 to 1.0
    key_findings: List[str]
    current_memory: int
    estimated_completion: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


class StreamingRLMProcessor(RLMProcessor):
    """RLM processor with streaming summary capabilities."""

    def __init__(
        self,
        working_dir: Path,
        chunk_size: int = RLMProcessor.DEFAULT_CHUNK_SIZE,
        on_started: Optional[Callable[[StreamEvent], None]] = None,
        on_chunk_started: Optional[Callable[[StreamEvent], None]] = None,
        on_chunk_progress: Optional[Callable[[StreamEvent], None]] = None,
        on_chunk_complete: Optional[Callable[[StreamEvent], None]] = None,
        on_merge_started: Optional[Callable[[StreamEvent], None]] = None,
        on_merge_complete: Optional[Callable[[StreamEvent], None]] = None,
        on_completed: Optional[Callable[[StreamEvent], None]] = None,
        on_error: Optional[Callable[[StreamEvent], None]] = None
    ):
        """Initialize streaming RLM processor.

        Args:
            working_dir: Project working directory
            chunk_size: Number of items per chunk
            on_started: Callback when processing starts
            on_chunk_started: Callback when chunk processing starts
            on_chunk_progress: Callback for chunk progress updates
            on_chunk_complete: Callback when chunk completes
            on_merge_started: Callback when merging starts
            on_merge_complete: Callback when merging completes
            on_completed: Callback when all processing completes
            on_error: Callback for errors
        """
        super().__init__(working_dir, chunk_size)

        # Callbacks
        self.on_started = on_started
        self.on_chunk_started = on_chunk_started
        self.on_chunk_progress = on_chunk_progress
        self.on_chunk_complete = on_chunk_complete
        self.on_merge_started = on_merge_started
        self.on_merge_complete = on_merge_complete
        self.on_completed = on_completed
        self.on_error = on_error

        # Streaming state
        self.streaming_summaries: List[StreamingSummary] = []
        self.stream_log: List[StreamEvent] = []

    def _emit_event(
        self,
        event_type: StreamEventType,
        data: Dict[str, Any]
    ):
        """Emit a streaming event.

        Args:
            event_type: Type of event
            data: Event data
        """
        event = StreamEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data
        )

        # Add to log
        self.stream_log.append(event)

        # Call appropriate callback
        callback_map = {
            StreamEventType.STARTED: self.on_started,
            StreamEventType.CHUNK_STARTED: self.on_chunk_started,
            StreamEventType.CHUNK_PROGRESS: self.on_chunk_progress,
            StreamEventType.CHUNK_COMPLETE: self.on_chunk_complete,
            StreamEventType.MERGE_STARTED: self.on_merge_started,
            StreamEventType.MERGE_COMPLETE: self.on_merge_complete,
            StreamEventType.COMPLETED: self.on_completed,
            StreamEventType.ERROR: self.on_error
        }

        callback = callback_map.get(event_type)
        if callback:
            callback(event)

    def _create_streaming_summary(
        self,
        chunk_id: int,
        chunk_size: int,
        chunk_analysis: str,
        progress: float
    ) -> StreamingSummary:
        """Create real-time streaming summary.

        Args:
            chunk_id: Chunk identifier
            chunk_size: Size of chunk
            chunk_analysis: Chunk analysis text
            progress: Progress (0.0 to 1.0)

        Returns:
            StreamingSummary
        """
        # Extract key findings from analysis
        lines = chunk_analysis.split('\n')
        key_findings = []
        for line in lines:
            if line.startswith(('1.', '2.', '3.', '-', 'RQ')):
                key_findings.append(line.strip())
            if len(key_findings) >= 5:  # Top 5 findings
                break

        # Current memory
        current_memory = len(chunk_analysis.split())

        # Estimate completion time (placeholder)
        estimated_completion = None
        if progress < 1.0:
            remaining_chunks = int((1.0 - progress) / (progress / (chunk_id + 1)))
            estimated_completion = f"{remaining_chunks} chunks remaining"

        return StreamingSummary(
            chunk_id=chunk_id,
            chunk_size=chunk_size,
            progress=progress,
            key_findings=key_findings,
            current_memory=current_memory,
            estimated_completion=estimated_completion
        )

    def _process_chunk_with_streaming(
        self,
        chunk_id: int,
        chunk: List[Any],
        agent_name: str,
        total_chunks: int
    ):
        """Process chunk with streaming updates.

        Overrides parent _process_chunk to add streaming.

        Args:
            chunk_id: Chunk identifier
            chunk: Chunk data
            agent_name: Agent name
            total_chunks: Total number of chunks

        Returns:
            ChunkResult
        """
        # Emit chunk started event
        self._emit_event(
            StreamEventType.CHUNK_STARTED,
            {
                "chunk_id": chunk_id,
                "chunk_size": len(chunk),
                "total_chunks": total_chunks
            }
        )

        # Process chunk (using parent method)
        result = self._process_chunk(chunk_id, chunk, agent_name)

        # Calculate progress
        progress = (chunk_id + 1) / total_chunks

        # Create streaming summary
        streaming_summary = self._create_streaming_summary(
            chunk_id=chunk_id,
            chunk_size=len(chunk),
            chunk_analysis=result.chunk_analysis,
            progress=progress
        )

        self.streaming_summaries.append(streaming_summary)

        # Emit chunk complete event
        self._emit_event(
            StreamEventType.CHUNK_COMPLETE,
            {
                "chunk_id": chunk_id,
                "summary": streaming_summary.to_dict(),
                "progress": progress,
                "progress_percentage": f"{progress * 100:.1f}%"
            }
        )

        return result

    def process_with_streaming(
        self,
        dataset: List[Any],
        agent_name: str,
        chunk_size: int = None
    ) -> RLMResult:
        """Process large dataset with streaming updates.

        Main entry point for streaming RLM processing.

        Args:
            dataset: List of items to process
            agent_name: Name of RLM agent
            chunk_size: Optional chunk size override

        Returns:
            RLMResult with final synthesis
        """
        start_time = datetime.now()

        # Emit started event
        self._emit_event(
            StreamEventType.STARTED,
            {
                "agent_name": agent_name,
                "dataset_size": len(dataset),
                "chunk_size": chunk_size or self.chunk_size
            }
        )

        print(f"\n{'='*70}")
        print(f"🔄 STREAMING RLM PROCESSING: {agent_name}")
        print(f"{'='*70}\n")

        print(f"Dataset size: {len(dataset)} items")
        chunk_size = chunk_size or self.chunk_size
        print(f"Chunk size: {chunk_size} items")

        # 1. Chunk dataset
        print(f"\n[1/4] Chunking dataset...")
        chunks = self._chunk_dataset(dataset, chunk_size)
        print(f"  ✓ Created {len(chunks)} chunks")

        # 2. Process each chunk with streaming
        print(f"\n[2/4] Processing chunks with streaming...")
        chunk_results = []
        for i, chunk in enumerate(chunks):
            result = self._process_chunk_with_streaming(
                chunk_id=i,
                chunk=chunk,
                agent_name=agent_name,
                total_chunks=len(chunks)
            )
            chunk_results.append(result)

            # Save chunk result
            self._save_chunk_result(result, agent_name)

        print(f"  ✓ All chunks processed")

        # 3. Merge summaries
        print(f"\n[3/4] Merging chunk summaries...")

        # Emit merge started event
        self._emit_event(
            StreamEventType.MERGE_STARTED,
            {
                "num_chunks": len(chunks),
                "total_items": sum(r.chunk_size for r in chunk_results)
            }
        )

        final_synthesis = self._merge_summaries(chunk_results)

        # Emit merge complete event
        self._emit_event(
            StreamEventType.MERGE_COMPLETE,
            {
                "synthesis_size": len(final_synthesis.split())
            }
        )

        # 4. Create final result
        print(f"\n[4/4] Finalizing result...")
        total_time = (datetime.now() - start_time).total_seconds()
        total_items = sum(r.chunk_size for r in chunk_results)

        baseline_memory = total_items * 150
        compression_ratio = self.current_peak_memory / baseline_memory if baseline_memory > 0 else 0

        rlm_result = RLMResult(
            agent_name=agent_name,
            total_items=total_items,
            num_chunks=len(chunks),
            chunk_results=chunk_results,
            final_synthesis=final_synthesis,
            peak_memory=self.current_peak_memory,
            total_time=total_time,
            compression_ratio=compression_ratio,
            timestamp=datetime.now().isoformat()
        )

        # Save final result
        self._save_final_result(rlm_result, agent_name)

        # Emit completed event
        self._emit_event(
            StreamEventType.COMPLETED,
            {
                "total_items": total_items,
                "peak_memory": self.current_peak_memory,
                "total_time": total_time,
                "compression_ratio": compression_ratio,
                "reduction_percentage": f"{(1 - compression_ratio) * 100:.1f}%"
            }
        )

        print(f"\n{'='*70}")
        print(f"✅ STREAMING RLM COMPLETE: {agent_name}")
        print(f"   Total items: {total_items:,}")
        print(f"   Peak memory: {self.current_peak_memory:,} tokens")
        print(f"   Reduction: {(1 - compression_ratio) * 100:.1f}%")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Stream events: {len(self.stream_log)}")
        print(f"{'='*70}\n")

        return rlm_result

    def get_stream_log(self) -> List[StreamEvent]:
        """Get complete stream log.

        Returns:
            List of stream events
        """
        return self.stream_log

    def save_stream_log(self, agent_name: str):
        """Save stream log to file.

        Args:
            agent_name: Agent name
        """
        log_file = self.rlm_chunks_dir / f"{agent_name}_stream_log.json"

        log_data = [event.to_dict() for event in self.stream_log]

        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)

        print(f"Stream log saved: {log_file}")


# Example callbacks
def example_on_started(event: StreamEvent):
    """Example callback for started event."""
    print(f"[STARTED] Processing {event.data['dataset_size']} items...")


def example_on_chunk_complete(event: StreamEvent):
    """Example callback for chunk complete event."""
    chunk_id = event.data['chunk_id']
    progress = event.data['progress_percentage']
    summary = event.data['summary']

    print(f"\n[CHUNK {chunk_id + 1} COMPLETE] Progress: {progress}")
    print(f"  Key findings:")
    for finding in summary['key_findings'][:3]:  # Top 3
        print(f"    - {finding}")


def example_on_completed(event: StreamEvent):
    """Example callback for completed event."""
    print(f"\n[COMPLETED] All processing finished!")
    print(f"  Total items: {event.data['total_items']:,}")
    print(f"  Peak memory: {event.data['peak_memory']:,} tokens")
    print(f"  Reduction: {event.data['reduction_percentage']}")


def main():
    """CLI interface with streaming example."""
    import argparse

    parser = argparse.ArgumentParser(
        description="RLM Streaming Processor"
    )
    parser.add_argument(
        "--working-dir",
        type=str,
        required=True,
        help="Project working directory"
    )
    parser.add_argument(
        "--dataset-size",
        type=int,
        default=1000,
        help="Size of mock dataset"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=100,
        help="Chunk size"
    )
    parser.add_argument(
        "--agent-name",
        type=str,
        default="literature-searcher-rlm",
        help="Agent name"
    )

    args = parser.parse_args()

    # Create mock dataset
    mock_dataset = [
        {"paper_id": i, "title": f"Paper {i}"}
        for i in range(args.dataset_size)
    ]

    # Create streaming processor with callbacks
    processor = StreamingRLMProcessor(
        working_dir=args.working_dir,
        chunk_size=args.chunk_size,
        on_started=example_on_started,
        on_chunk_complete=example_on_chunk_complete,
        on_completed=example_on_completed
    )

    # Process with streaming
    result = processor.process_with_streaming(
        dataset=mock_dataset,
        agent_name=args.agent_name
    )

    # Save stream log
    processor.save_stream_log(args.agent_name)

    print("\n✅ Streaming processing complete!")
    print(f"   Stream events logged: {len(processor.get_stream_log())}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
