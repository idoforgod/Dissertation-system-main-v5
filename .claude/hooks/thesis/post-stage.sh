#!/bin/bash
#
# Post-Stage Hook for Mode E (Paper-based Research Design)
#
# Purpose: Collects metrics, validates outputs, and prepares for next stage
# Trigger: After each Stage 1-6 agent execution
# Exit codes: 0 = success, 1 = validation failed

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

STAGE_NAME="${1:-unknown}"
OUTPUT_FILE="${2:-}"
BASE_DIR="${3:-thesis-output}"
LOG_DIR="${BASE_DIR}/logs"
METRICS_DIR="${BASE_DIR}/metrics"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create directories
mkdir -p "${LOG_DIR}" "${METRICS_DIR}"

LOG_FILE="${LOG_DIR}/post-stage-${STAGE_NAME}-$(date +%Y%m%d-%H%M%S).log"
METRICS_FILE="${METRICS_DIR}/${STAGE_NAME}-metrics.json"

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
# Validation Functions
# ============================================================================

validate_output_file() {
    local output="${1}"

    log_info "Validating output file..."

    if [ -z "${output}" ]; then
        log_error "No output file specified"
        return 1
    fi

    if [ ! -f "${output}" ]; then
        log_error "Output file not found: ${output}"
        return 1
    fi

    # Check file size (warn if empty)
    local file_size=$(stat -f%z "${output}" 2>/dev/null || stat -c%s "${output}" 2>/dev/null || echo "0")
    if [ "${file_size}" -eq 0 ]; then
        log_error "Output file is empty: ${output}"
        return 1
    fi

    log_success "Output file validated: ${output} (${file_size} bytes)"
    return 0
}

validate_output_content() {
    local stage="${1}"
    local output="${2}"

    log_info "Validating output content for ${stage}..."

    # Basic checks for all stages
    local line_count=$(wc -l < "${output}")
    if [ "${line_count}" -lt 50 ]; then
        log_warn "Output file seems too short: ${line_count} lines"
    else
        log_success "Output file has ${line_count} lines"
    fi

    # Stage-specific validation
    case "${stage}" in
        "stage1"|"paper-analyzer")
            # Check for required sections
            if ! grep -q "Theoretical Framework" "${output}"; then
                log_warn "Missing section: Theoretical Framework"
            fi
            if ! grep -q "Methodological Analysis" "${output}"; then
                log_warn "Missing section: Methodological Analysis"
            fi
            if ! grep -q "Critical Evaluation" "${output}"; then
                log_warn "Missing section: Critical Evaluation"
            fi
            ;;

        "stage2"|"gap-identifier")
            # Check for research gaps
            if ! grep -q "Theoretical Gap" "${output}"; then
                log_warn "No theoretical gaps identified"
            fi
            if ! grep -q "Priority Score" "${output}"; then
                log_warn "Missing priority scores"
            fi
            ;;

        "stage3"|"hypothesis-generator")
            # Check for hypotheses
            local h_count=$(grep -c "^H[0-9]:" "${output}" || echo "0")
            if [ "${h_count}" -eq 0 ]; then
                log_error "No hypotheses found in output"
                return 1
            fi
            log_success "Found ${h_count} hypotheses"

            # Check for CTOSF scores
            if ! grep -q "CTOSF" "${output}"; then
                log_warn "Missing CTOSF evaluation"
            fi
            ;;

        "stage4"|"design-proposer")
            # Check for methodology sections
            if ! grep -q "Research Design" "${output}"; then
                log_warn "Missing section: Research Design"
            fi
            if ! grep -q "Sample Size" "${output}"; then
                log_warn "Missing sample size calculation"
            fi
            if ! grep -q "Data Analysis Plan" "${output}"; then
                log_warn "Missing data analysis plan"
            fi
            ;;

        "stage5"|"feasibility-assessor")
            # Check for feasibility score
            if ! grep -q "Feasibility Score" "${output}"; then
                log_warn "Missing feasibility score"
            fi
            if ! grep -q "GO\|NO-GO\|MODIFY" "${output}"; then
                log_warn "Missing Go/No-Go recommendation"
            fi
            ;;

        "stage6"|"proposal-integrator")
            # Check for quality validation
            if ! grep -q "GRA Compliance" "${output}"; then
                log_warn "Missing GRA compliance check"
            fi
            if ! grep -q "pTCS" "${output}"; then
                log_warn "Missing pTCS scores"
            fi

            # Check page count (should be 40-60 pages)
            local word_count=$(wc -w < "${output}")
            local estimated_pages=$((word_count / 500))  # ~500 words/page
            if [ "${estimated_pages}" -lt 30 ]; then
                log_warn "Proposal seems too short: ~${estimated_pages} pages"
            elif [ "${estimated_pages}" -gt 70 ]; then
                log_warn "Proposal seems too long: ~${estimated_pages} pages"
            else
                log_success "Proposal length: ~${estimated_pages} pages (target: 40-60)"
            fi
            ;;
    esac

    log_success "Content validation completed"
    return 0
}

# ============================================================================
# Metrics Collection
# ============================================================================

collect_metrics() {
    local stage="${1}"
    local output="${2}"

    log_info "Collecting metrics..."

    # Read metadata from pre-stage
    local metadata_file="${BASE_DIR}/logs/${stage}/metadata.json"
    local start_time=""
    if [ -f "${metadata_file}" ]; then
        start_time=$(jq -r '.start_time' "${metadata_file}" 2>/dev/null || echo "")
    fi

    # Calculate duration
    local end_time=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local duration_seconds=0
    if [ -n "${start_time}" ]; then
        # Calculate duration in seconds (simplified)
        local start_epoch=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "${start_time}" +%s 2>/dev/null || echo "0")
        local end_epoch=$(date +%s)
        duration_seconds=$((end_epoch - start_epoch))
    fi

    # File metrics
    local file_size=$(stat -f%z "${output}" 2>/dev/null || stat -c%s "${output}" 2>/dev/null || echo "0")
    local line_count=$(wc -l < "${output}")
    local word_count=$(wc -w < "${output}")

    # Create metrics JSON
    cat > "${METRICS_FILE}" <<EOF
{
  "stage": "${stage}",
  "output_file": "${output}",
  "timestamp": "${end_time}",
  "start_time": "${start_time}",
  "end_time": "${end_time}",
  "duration_seconds": ${duration_seconds},
  "duration_formatted": "$(printf '%02d:%02d:%02d' $((duration_seconds/3600)) $((duration_seconds%3600/60)) $((duration_seconds%60)))",
  "file_metrics": {
    "size_bytes": ${file_size},
    "size_kb": $((file_size / 1024)),
    "line_count": ${line_count},
    "word_count": ${word_count}
  },
  "validation_status": "passed"
}
EOF

    log_success "Metrics collected: ${METRICS_FILE}"
    log_info "Duration: $(printf '%02d:%02d:%02d' $((duration_seconds/3600)) $((duration_seconds%3600/60)) $((duration_seconds%60)))"
    log_info "Output: ${line_count} lines, ${word_count} words, $((file_size / 1024)) KB"
}

# ============================================================================
# Next Stage Preparation
# ============================================================================

prepare_next_stage() {
    local current_stage="${1}"

    log_info "Preparing for next stage..."

    case "${current_stage}" in
        "stage1"|"paper-analyzer")
            log_info "Next: Stage 2 (gap-identifier)"
            log_info "Run: /thesis:identify-gaps --analysis-file ${OUTPUT_FILE}"
            ;;
        "stage2"|"gap-identifier")
            log_info "Next: Stage 3 (hypothesis-generator)"
            log_info "Run: /thesis:generate-hypotheses --gap-file ${OUTPUT_FILE}"
            ;;
        "stage3"|"hypothesis-generator")
            log_info "Next: Stage 4 (design-proposer)"
            log_info "Run: /thesis:propose-design --hypotheses-file ${OUTPUT_FILE}"
            ;;
        "stage4"|"design-proposer")
            log_info "Next: Stage 5 (feasibility-assessor)"
            log_info "Run: /thesis:assess-feasibility --design-file ${OUTPUT_FILE}"
            ;;
        "stage5"|"feasibility-assessor")
            log_info "Next: Stage 6 (proposal-integrator)"
            log_info "Run: /thesis:integrate-proposal --feasibility-file ${OUTPUT_FILE}"
            ;;
        "stage6"|"proposal-integrator")
            log_info "Next: HITL Review (Gate 1)"
            log_info "Run: /thesis:review-proposal --proposal-file ${OUTPUT_FILE}"
            ;;
    esac
}

# ============================================================================
# Progress Summary
# ============================================================================

generate_progress_summary() {
    log_info "Generating progress summary..."

    # Check which stages are completed
    local completed_stages=()
    local stage_files=(
        "stage1:${BASE_DIR}/stage1-analysis/stage1-paper-analysis.md"
        "stage2:${BASE_DIR}/stage2-gaps/stage2-gap-analysis.md"
        "stage3:${BASE_DIR}/stage3-hypotheses/stage3-hypotheses.md"
        "stage4:${BASE_DIR}/stage4-design/stage4-research-design.md"
        "stage5:${BASE_DIR}/stage5-feasibility/stage5-feasibility-assessment.md"
        "stage6:${BASE_DIR}/stage6-proposal/final-research-proposal.md"
    )

    local total_duration=0
    for stage_file in "${stage_files[@]}"; do
        local stage="${stage_file%%:*}"
        local file="${stage_file#*:}"

        if [ -f "${file}" ]; then
            completed_stages+=("${stage}")

            # Add duration if metrics available
            local metrics="${METRICS_DIR}/${stage}-metrics.json"
            if [ -f "${metrics}" ]; then
                local duration=$(jq -r '.duration_seconds' "${metrics}" 2>/dev/null || echo "0")
                total_duration=$((total_duration + duration))
            fi
        fi
    done

    local completed_count=${#completed_stages[@]}
    local progress_percent=$((completed_count * 100 / 6))

    log_info "=========================================="
    log_info "Progress Summary"
    log_info "=========================================="
    log_info "Completed Stages: ${completed_count}/6 (${progress_percent}%)"
    log_info "Stages: ${completed_stages[*]}"
    log_info "Total Duration: $(printf '%02d:%02d:%02d' $((total_duration/3600)) $((total_duration%3600/60)) $((total_duration%60)))"
    log_info "=========================================="

    # Create progress file
    cat > "${BASE_DIR}/progress.json" <<EOF
{
  "completed_stages": [$(printf '"%s",' "${completed_stages[@]}" | sed 's/,$//')],
  "completed_count": ${completed_count},
  "total_stages": 6,
  "progress_percent": ${progress_percent},
  "total_duration_seconds": ${total_duration},
  "last_updated": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
}
EOF
}

# ============================================================================
# Auto-trigger Next Stage (Optional)
# ============================================================================

auto_trigger_next() {
    local current_stage="${1}"
    local auto_continue="${AUTO_CONTINUE:-false}"

    if [ "${auto_continue}" == "true" ]; then
        log_info "Auto-continue enabled. Triggering next stage..."

        case "${current_stage}" in
            "stage1"|"paper-analyzer")
                log_info "Auto-triggering Stage 2..."
                # Note: Actual triggering would be done by orchestrator
                ;;
            # ... other stages
        esac
    else
        log_info "Auto-continue disabled. Manual trigger required for next stage."
    fi
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_info "=========================================="
    log_info "Post-Stage Hook Started"
    log_info "Stage: ${STAGE_NAME}"
    log_info "Output: ${OUTPUT_FILE}"
    log_info "Base Directory: ${BASE_DIR}"
    log_info "=========================================="

    # Validate output file
    if ! validate_output_file "${OUTPUT_FILE}"; then
        log_error "Output file validation failed"
        exit 1
    fi

    # Validate content
    if ! validate_output_content "${STAGE_NAME}" "${OUTPUT_FILE}"; then
        log_warn "Content validation found issues (non-critical)"
    fi

    # Collect metrics
    collect_metrics "${STAGE_NAME}" "${OUTPUT_FILE}"

    # Generate progress summary
    generate_progress_summary

    # Prepare next stage
    prepare_next_stage "${STAGE_NAME}"

    # Auto-trigger (if enabled)
    auto_trigger_next "${STAGE_NAME}"

    log_success "Post-stage processing completed successfully"
    log_info "Stage ${STAGE_NAME} finished"
    log_info "Metrics: ${METRICS_FILE}"
    log_info "Log: ${LOG_FILE}"
    log_info "=========================================="

    exit 0
}

# Run main function
main "$@"
