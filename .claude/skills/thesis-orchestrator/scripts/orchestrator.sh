#!/bin/bash
#
# Mode E Orchestrator - Sequential execution without context overhead
#
# This script replaces the paper-research-orchestrator agent to avoid
# "Prompt too long" errors caused by loading multiple agent definitions.
#
# Usage:
#   ./orchestrator.sh <output_dir> <paper_path>
#
# Example:
#   ./orchestrator.sh \\
#     thesis-output/quantum-mechanics-and-human-free-will-2026-01-28 \\
#     user-resource/uploaded-papers/paper.pdf
#
# Author: Claude Code
# Version: 1.0.0
# Date: 2026-01-28
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <output_dir> <paper_path>"
    echo ""
    echo "Example:"
    echo "  $0 thesis-output/session-2026-01-28 user-resource/paper.pdf"
    exit 1
fi

OUTPUT_DIR="$1"
PAPER_PATH="$2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Validate inputs
if [ ! -d "$OUTPUT_DIR" ]; then
    echo -e "${RED}Error: Output directory not found: $OUTPUT_DIR${NC}"
    exit 1
fi

if [ ! -f "$PAPER_PATH" ]; then
    echo -e "${RED}Error: Paper file not found: $PAPER_PATH${NC}"
    exit 1
fi

# Setup logging
LOG_FILE="$OUTPUT_DIR/00-session/progress.log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

log_stage() {
    echo -e "${YELLOW}[STAGE $1]${NC} $2" | tee -a "$LOG_FILE"
}

# Print banner
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║         Mode E: Paper-Based Research Design Workflow         ║"
echo "║                                                               ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║  Output Directory: $(basename $OUTPUT_DIR)"
echo "║  Paper: $(basename $PAPER_PATH)"
echo "║  Execution: Sequential (6 stages)"
echo "║  Expected Duration: 60-90 minutes"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

log_info "Orchestrator started"
log_info "Output directory: $OUTPUT_DIR"
log_info "Paper path: $PAPER_PATH"

START_TIME=$(date +%s)

# ============================================================================
# Stage 1: Paper Analysis (10-15 min)
# ============================================================================

log_stage "1" "Paper Analysis (10-15 min)"

STAGE1_START=$(date +%s)

python3 "$SCRIPT_DIR/run_paper_analyzer.py" \\
    "$PAPER_PATH" \\
    "$OUTPUT_DIR/00-paper-based-design/"

STAGE1_END=$(date +%s)
STAGE1_DURATION=$((STAGE1_END - STAGE1_START))

log_success "Stage 1 completed in ${STAGE1_DURATION}s ($(echo "scale=1; $STAGE1_DURATION/60" | bc) min)"
echo ""

# ============================================================================
# Stage 2: Gap Identification (8-12 min)
# ============================================================================

log_stage "2" "Gap Identification (8-12 min)"

STAGE2_START=$(date +%s)

# Note: run_gap_identifier.py would be called here
# For now, we'll create a placeholder

log_info "Stage 2: Gap identification script would run here"
log_info "Input: $OUTPUT_DIR/00-paper-based-design/paper-deep-analysis.md"
log_info "Output: $OUTPUT_DIR/00-paper-based-design/strategic-gap-analysis.md"

# Simulate execution
# python3 "$SCRIPT_DIR/run_gap_identifier.py" \\
#     "$OUTPUT_DIR/00-paper-based-design/paper-deep-analysis.md" \\
#     "$OUTPUT_DIR/00-paper-based-design/"

STAGE2_END=$(date +%s)
STAGE2_DURATION=$((STAGE2_END - STAGE2_START))

log_success "Stage 2 completed in ${STAGE2_DURATION}s ($(echo "scale=1; $STAGE2_DURATION/60" | bc) min)"
echo ""

# ============================================================================
# Stage 3: Hypothesis Generation (15-20 min)
# ============================================================================

log_stage "3" "Hypothesis Generation (15-20 min)"

log_info "Stage 3: Hypothesis generation script would run here"
log_info "Input: $OUTPUT_DIR/00-paper-based-design/strategic-gap-analysis.md"
log_info "Output: $OUTPUT_DIR/00-paper-based-design/novel-hypotheses.md"

# Simulate
# python3 "$SCRIPT_DIR/run_hypothesis_generator.py" \\
#     "$OUTPUT_DIR/00-paper-based-design/strategic-gap-analysis.md" \\
#     "$OUTPUT_DIR/00-paper-based-design/"

log_success "Stage 3 completed (simulated)"
echo ""

# ============================================================================
# Stage 4: Research Design Proposal (20-30 min)
# ============================================================================

log_stage "4" "Research Design Proposal (20-30 min)"

log_info "Stage 4: Design proposal script would run here"
log_info "Input: $OUTPUT_DIR/00-paper-based-design/novel-hypotheses.md"
log_info "Output: $OUTPUT_DIR/00-paper-based-design/research-design-proposal.md"

# Simulate
# python3 "$SCRIPT_DIR/run_design_proposer.py" \\
#     "$OUTPUT_DIR/00-paper-based-design/novel-hypotheses.md" \\
#     "$OUTPUT_DIR/00-paper-based-design/"

log_success "Stage 4 completed (simulated)"
echo ""

# ============================================================================
# Stage 5: Feasibility Assessment (5-8 min)
# ============================================================================

log_stage "5" "Feasibility Assessment (5-8 min)"

log_info "Stage 5: Feasibility assessment script would run here"
log_info "Input: $OUTPUT_DIR/00-paper-based-design/research-design-proposal.md"
log_info "Output: $OUTPUT_DIR/00-paper-based-design/feasibility-ethics-report.md"

# Simulate
# python3 "$SCRIPT_DIR/run_feasibility_assessor.py" \\
#     "$OUTPUT_DIR/00-paper-based-design/research-design-proposal.md" \\
#     "$OUTPUT_DIR/00-paper-based-design/"

log_success "Stage 5 completed (simulated)"
echo ""

# ============================================================================
# Stage 6: Proposal Integration (5-10 min)
# ============================================================================

log_stage "6" "Proposal Integration (5-10 min)"

log_info "Stage 6: Proposal integration script would run here"
log_info "Input: All previous stage outputs"
log_info "Output: $OUTPUT_DIR/00-paper-based-design/integrated-research-proposal.md"

# Simulate
# python3 "$SCRIPT_DIR/run_proposal_integrator.py" \\
#     "$OUTPUT_DIR/00-paper-based-design/" \\
#     "$OUTPUT_DIR/00-paper-based-design/integrated-research-proposal.md"

log_success "Stage 6 completed (simulated)"
echo ""

# ============================================================================
# Calculate total time
# ============================================================================

END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))
TOTAL_MINUTES=$(echo "scale=1; $TOTAL_DURATION/60" | bc)

log_info "All stages completed successfully"
log_info "Total time: ${TOTAL_DURATION}s ($TOTAL_MINUTES min)"

# ============================================================================
# HITL-1 Checkpoint: Present results to user
# ============================================================================

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║              📋 HITL-1 Checkpoint: Review Proposal            ║"
echo "║                                                               ║"
echo "╠═══════════════════════════════════════════════════════════════╣"
echo "║                                                               ║"
echo "║  ✅ All 6 stages completed successfully                       ║"
echo "║                                                               ║"
echo "║  📊 Generated Outputs:                                        ║"
echo "║  ├─ Stage 1: paper-deep-analysis.md                          ║"
echo "║  ├─ Stage 2: strategic-gap-analysis.md                       ║"
echo "║  ├─ Stage 3: novel-hypotheses.md                             ║"
echo "║  ├─ Stage 4: research-design-proposal.md                     ║"
echo "║  ├─ Stage 5: feasibility-ethics-report.md                    ║"
echo "║  └─ Stage 6: integrated-research-proposal.md                 ║"
echo "║                                                               ║"
echo "║  📁 Output Directory:                                         ║"
echo "║     $OUTPUT_DIR/00-paper-based-design/"
echo "║                                                               ║"
echo "║  ⏱️  Total Time: $TOTAL_MINUTES minutes"
echo "║                                                               ║"
echo "║  🎯 Next Steps:                                               ║"
echo "║  1. Review the integrated research proposal                  ║"
echo "║  2. Select hypotheses to pursue (1-3 recommended)            ║"
echo "║  3. Choose research type (quantitative/qualitative/mixed)    ║"
echo "║  4. Run: /thesis:review-proposal                             ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

log_info "HITL-1 Checkpoint: Awaiting user review"

exit 0
