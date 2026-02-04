#!/bin/bash
#
# HITL Checkpoint Hook for Mode E (Paper-based Research Design)
#
# Purpose: Triggers Human-in-the-Loop review at critical decision points
# Trigger: After Stage 6 (proposal integration) - Gate 1
# Exit codes: 0 = approved, 1 = rejected, 2 = revision required

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

GATE_NAME="${1:-gate1}"
PROPOSAL_FILE="${2:-}"
BASE_DIR="${3:-thesis-output}"
LOG_DIR="${BASE_DIR}/logs"
REVIEW_DIR="${BASE_DIR}/reviews"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create directories
mkdir -p "${LOG_DIR}" "${REVIEW_DIR}"

LOG_FILE="${LOG_DIR}/hitl-${GATE_NAME}-$(date +%Y%m%d-%H%M%S).log"
REVIEW_FILE="${REVIEW_DIR}/${GATE_NAME}-review-$(date +%Y%m%d-%H%M%S).json"

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
    echo "[${TIMESTAMP}] [INFO] $*" | tee -a "${LOG_FILE}"
}

log_warn() {
    echo "[${TIMESTAMP}] [WARN] $*" | tee -a "${LOG_FILE}"
}

log_error() {
    echo "[${TIMESTAMP}] [ERROR] $*" | tee -a "${LOG_FILE}" >&2
}

log_success() {
    echo "[${TIMESTAMP}] [SUCCESS] $*" | tee -a "${LOG_FILE}"
}

# ============================================================================
# Display Functions
# ============================================================================

display_banner() {
    echo ""
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│  🎓 HITL Checkpoint - Research Proposal Review              │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                              │"
    echo "│  All 6 stages have been completed!                          │"
    echo "│  Please review the final research proposal.                 │"
    echo "│                                                              │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
}

display_proposal_summary() {
    local proposal="${1}"

    log_info "Generating proposal summary..."

    # Extract key information
    local title=$(grep -m 1 "^# " "${proposal}" | sed 's/^# //' || echo "Untitled")
    local word_count=$(wc -w < "${proposal}")
    local page_count=$((word_count / 500))
    local h_count=$(grep -c "^H[0-9]:" "${proposal}" || echo "0")

    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│  Proposal Summary                                            │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                              │"
    printf "│  Title: %-53s │\n" "${title:0:53}"
    printf "│  Pages: ~%-3d                                              │\n" "${page_count}"
    printf "│  Hypotheses: %-3d                                          │\n" "${h_count}"
    printf "│  File: %-50s │\n" "$(basename "${proposal}")"
    echo "│                                                              │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
}

display_quality_metrics() {
    local proposal="${1}"

    log_info "Displaying quality metrics..."

    # Check if validation report exists
    local validation_file="${BASE_DIR}/validation-report.json"
    if [ -f "${validation_file}" ]; then
        echo "┌─────────────────────────────────────────────────────────────┐"
        echo "│  Quality Metrics                                             │"
        echo "├─────────────────────────────────────────────────────────────┤"
        echo "│                                                              │"

        # Extract metrics using jq
        if command -v jq &> /dev/null; then
            local gra=$(jq -r '.gra_compliance_score // "N/A"' "${validation_file}")
            local ptcs=$(jq -r '.ptcs_average // "N/A"' "${validation_file}")
            local format_errors=$(jq -r '.citation_format_errors // "N/A"' "${validation_file}")
            local missing_refs=$(jq -r '.missing_references // "N/A"' "${validation_file}")
            local overall=$(jq -r '.overall_quality_score // "N/A"' "${validation_file}")

            printf "│  GRA Compliance: %-6s %-35s │\n" "${gra}%" "$([ "${gra}" != "N/A" ] && [ "${gra%.*}" -ge 95 ] && echo "✅" || echo "⚠️ ")"
            printf "│  pTCS Average: %-8s %-33s │\n" "${ptcs}" "$([ "${ptcs}" != "N/A" ] && awk "BEGIN {exit !(${ptcs} >= 0.6)}" && echo "✅" || echo "⚠️ ")"
            printf "│  Citation Format Errors: %-3s %-28s │\n" "${format_errors}" "$([ "${format_errors}" == "0" ] && echo "✅" || echo "⚠️ ")"
            printf "│  Missing References: %-3s %-32s │\n" "${missing_refs}" "$([ "${missing_refs}" == "0" ] && echo "✅" || echo "⚠️ ")"
            printf "│  Overall Quality: %-5s/5.0 %-28s │\n" "${overall}" "$(awk "BEGIN {exit !(${overall} >= 4.0)}" && echo "✅" || echo "⚠️ ")"
        else
            echo "│  (Install 'jq' to view detailed metrics)                    │"
        fi

        echo "│                                                              │"
        echo "└─────────────────────────────────────────────────────────────┘"
        echo ""
    else
        echo "⚠️  Validation report not found. Run validation manually."
        echo ""
    fi
}

display_stage_summary() {
    log_info "Displaying stage completion summary..."

    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│  Stage Completion                                            │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                              │"

    local stages=(
        "Stage 1: Paper Analysis"
        "Stage 2: Gap Identification"
        "Stage 3: Hypothesis Generation"
        "Stage 4: Research Design"
        "Stage 5: Feasibility Assessment"
        "Stage 6: Proposal Integration"
    )

    local files=(
        "${BASE_DIR}/stage1-analysis/stage1-paper-analysis.md"
        "${BASE_DIR}/stage2-gaps/stage2-gap-analysis.md"
        "${BASE_DIR}/stage3-hypotheses/stage3-hypotheses.md"
        "${BASE_DIR}/stage4-design/stage4-research-design.md"
        "${BASE_DIR}/stage5-feasibility/stage5-feasibility-assessment.md"
        "${BASE_DIR}/stage6-proposal/final-research-proposal.md"
    )

    for i in "${!stages[@]}"; do
        local stage="${stages[$i]}"
        local file="${files[$i]}"
        local status="⏳"
        local duration=""

        if [ -f "${file}" ]; then
            status="✅"
            # Get duration from metrics
            local stage_num=$((i + 1))
            local metrics_file="${BASE_DIR}/metrics/stage${stage_num}-metrics.json"
            if [ -f "${metrics_file}" ] && command -v jq &> /dev/null; then
                duration=$(jq -r '.duration_formatted // ""' "${metrics_file}")
            fi
        fi

        printf "│  ${status} %-44s" "${stage}"
        if [ -n "${duration}" ]; then
            printf " %-10s" "${duration}"
        fi
        echo " │"
    done

    echo "│                                                              │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
}

# ============================================================================
# Review Options
# ============================================================================

display_review_options() {
    echo "┌─────────────────────────────────────────────────────────────┐"
    echo "│  Review Options                                              │"
    echo "├─────────────────────────────────────────────────────────────┤"
    echo "│                                                              │"
    echo "│  1. ✅ APPROVE - Excellent, proceed to next phase           │"
    echo "│                                                              │"
    echo "│  2. ✏️  APPROVE with Minor Edits - Fix quality issues       │"
    echo "│                                                              │"
    echo "│  3. 🔄 REVISE Stage 6 - Re-integrate proposal                │"
    echo "│                                                              │"
    echo "│  4. 🔄🔄 REVISE Stages 4-6 - Revise methodology              │"
    echo "│                                                              │"
    echo "│  5. 🔄🔄🔄 REVISE Stages 3-6 - Revise hypotheses              │"
    echo "│                                                              │"
    echo "│  6. 🔄🔄🔄🔄 REVISE All Stages - Major revision                │"
    echo "│                                                              │"
    echo "│  7. ❌ REJECT - Not acceptable                               │"
    echo "│                                                              │"
    echo "└─────────────────────────────────────────────────────────────┘"
    echo ""
}

get_user_decision() {
    local decision=""
    local valid_choices=("1" "2" "3" "4" "5" "6" "7")

    while true; do
        read -p "Your choice (1-7): " decision

        # Check if choice is valid
        if [[ " ${valid_choices[@]} " =~ " ${decision} " ]]; then
            break
        else
            echo "Invalid choice. Please select 1-7."
        fi
    done

    echo "${decision}"
}

get_revision_notes() {
    echo ""
    echo "Please provide revision requirements:"
    read -p "> " revision_notes
    echo "${revision_notes}"
}

# ============================================================================
# Decision Processing
# ============================================================================

process_decision() {
    local decision="${1}"
    local proposal="${2}"

    log_info "Processing user decision: ${decision}"

    case "${decision}" in
        "1")
            log_success "User approved proposal"
            echo ""
            echo "✅ Proposal APPROVED"
            echo "   Mode E workflow complete!"
            echo ""
            save_review_decision "APPROVED" ""
            return 0
            ;;

        "2")
            log_info "User approved with minor edits"
            echo ""
            echo "✏️  Proposal APPROVED with Minor Edits"
            echo "   Auto-fixing quality issues..."
            echo ""

            # Trigger auto-fix (if available)
            # This would call a separate script or Python tool
            log_info "Auto-fix not implemented in this hook. Manual fix required."

            save_review_decision "APPROVED_WITH_EDITS" ""
            return 0
            ;;

        "3")
            log_info "User requested Stage 6 revision"
            echo ""
            echo "🔄 REVISE Stage 6"
            local notes=$(get_revision_notes)
            save_review_decision "REVISE_STAGE6" "${notes}"
            return 2
            ;;

        "4")
            log_info "User requested Stages 4-6 revision"
            echo ""
            echo "🔄🔄 REVISE Stages 4-6"
            local notes=$(get_revision_notes)
            save_review_decision "REVISE_STAGES_4_6" "${notes}"
            return 2
            ;;

        "5")
            log_info "User requested Stages 3-6 revision"
            echo ""
            echo "🔄🔄🔄 REVISE Stages 3-6"
            local notes=$(get_revision_notes)
            save_review_decision "REVISE_STAGES_3_6" "${notes}"
            return 2
            ;;

        "6")
            log_info "User requested all stages revision"
            echo ""
            echo "🔄🔄🔄🔄 REVISE All Stages"
            local notes=$(get_revision_notes)
            save_review_decision "REVISE_ALL" "${notes}"
            return 2
            ;;

        "7")
            log_warn "User rejected proposal"
            echo ""
            echo "❌ Proposal REJECTED"
            local notes=$(get_revision_notes)
            save_review_decision "REJECTED" "${notes}"
            return 1
            ;;

        *)
            log_error "Invalid decision: ${decision}"
            return 1
            ;;
    esac
}

save_review_decision() {
    local decision="${1}"
    local notes="${2}"

    log_info "Saving review decision..."

    cat > "${REVIEW_FILE}" <<EOF
{
  "gate": "${GATE_NAME}",
  "proposal_file": "${PROPOSAL_FILE}",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "decision": "${decision}",
  "revision_notes": "${notes}",
  "reviewer": "${USER:-unknown}"
}
EOF

    log_success "Review decision saved: ${REVIEW_FILE}"
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_info "=========================================="
    log_info "HITL Checkpoint Started"
    log_info "Gate: ${GATE_NAME}"
    log_info "Proposal: ${PROPOSAL_FILE}"
    log_info "=========================================="

    # Validate proposal file
    if [ ! -f "${PROPOSAL_FILE}" ]; then
        log_error "Proposal file not found: ${PROPOSAL_FILE}"
        exit 1
    fi

    # Display interface
    display_banner
    display_proposal_summary "${PROPOSAL_FILE}"
    display_quality_metrics "${PROPOSAL_FILE}"
    display_stage_summary

    # Get user decision
    display_review_options
    local decision=$(get_user_decision)

    # Process decision
    process_decision "${decision}" "${PROPOSAL_FILE}"
    local exit_code=$?

    log_info "=========================================="
    log_info "HITL Checkpoint Completed"
    log_info "Decision: $(cat "${REVIEW_FILE}" | jq -r '.decision' 2>/dev/null || echo "unknown")"
    log_info "Log: ${LOG_FILE}"
    log_info "Review: ${REVIEW_FILE}"
    log_info "=========================================="

    exit ${exit_code}
}

# Run main function
main "$@"
