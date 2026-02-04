#!/bin/bash
#
# Pre-Stage Hook for Mode E (Paper-based Research Design)
#
# Purpose: Validates inputs and environment before each stage execution
# Trigger: Before any Stage 1-6 agent execution
# Exit codes: 0 = success, 1 = validation failed

set -e  # Exit on error

# ============================================================================
# Configuration
# ============================================================================

STAGE_NAME="${1:-unknown}"
INPUT_FILE="${2:-}"
BASE_DIR="${3:-thesis-output}"
LOG_DIR="${BASE_DIR}/logs"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create log directory if not exists
mkdir -p "${LOG_DIR}"

LOG_FILE="${LOG_DIR}/pre-stage-${STAGE_NAME}-$(date +%Y%m%d-%H%M%S).log"

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

validate_environment() {
    log_info "Validating environment..."

    # Check base directory exists
    if [ ! -d "${BASE_DIR}" ]; then
        log_error "Base directory not found: ${BASE_DIR}"
        log_info "Creating base directory..."
        mkdir -p "${BASE_DIR}"
    fi

    # Check required directories
    local required_dirs=(
        "${BASE_DIR}/stage1-analysis"
        "${BASE_DIR}/stage2-gaps"
        "${BASE_DIR}/stage3-hypotheses"
        "${BASE_DIR}/stage4-design"
        "${BASE_DIR}/stage5-feasibility"
        "${BASE_DIR}/stage6-proposal"
        "${BASE_DIR}/logs"
    )

    for dir in "${required_dirs[@]}"; do
        if [ ! -d "${dir}" ]; then
            log_warn "Directory not found: ${dir}"
            log_info "Creating directory: ${dir}"
            mkdir -p "${dir}"
        fi
    done

    log_success "Environment validation passed"
    return 0
}

validate_input_file() {
    local stage="${1}"
    local input="${2}"

    log_info "Validating input file for ${stage}..."

    # Stage 1 requires PDF file
    if [ "${stage}" == "stage1" ] || [ "${stage}" == "paper-analyzer" ]; then
        if [ -z "${input}" ]; then
            log_error "Stage 1 requires PDF file path"
            return 1
        fi

        if [ ! -f "${input}" ]; then
            log_error "Input file not found: ${input}"
            return 1
        fi

        # Check file extension
        if [[ ! "${input}" =~ \.pdf$ ]]; then
            log_warn "Input file is not a PDF. Expected .pdf extension."
        fi

        # Check file size (warn if >50MB)
        local file_size=$(stat -f%z "${input}" 2>/dev/null || stat -c%s "${input}" 2>/dev/null || echo "0")
        local max_size=$((50 * 1024 * 1024))  # 50MB

        if [ "${file_size}" -gt "${max_size}" ]; then
            log_warn "Large file detected: $((file_size / 1024 / 1024))MB. Processing may take longer."
        fi

        log_success "Input file validated: ${input}"
    fi

    # Stages 2-6 require previous stage output
    if [ "${stage}" == "stage2" ] || [ "${stage}" == "gap-identifier" ]; then
        local required="${BASE_DIR}/stage1-analysis/stage1-paper-analysis.md"
        if [ ! -f "${required}" ]; then
            log_error "Stage 2 requires Stage 1 output: ${required}"
            log_info "Please run Stage 1 (paper-analyzer) first."
            return 1
        fi
        log_success "Stage 1 output found: ${required}"
    fi

    if [ "${stage}" == "stage3" ] || [ "${stage}" == "hypothesis-generator" ]; then
        local required="${BASE_DIR}/stage2-gaps/stage2-gap-analysis.md"
        if [ ! -f "${required}" ]; then
            log_error "Stage 3 requires Stage 2 output: ${required}"
            log_info "Please run Stage 2 (gap-identifier) first."
            return 1
        fi
        log_success "Stage 2 output found: ${required}"
    fi

    if [ "${stage}" == "stage4" ] || [ "${stage}" == "design-proposer" ]; then
        local required="${BASE_DIR}/stage3-hypotheses/stage3-hypotheses.md"
        if [ ! -f "${required}" ]; then
            log_error "Stage 4 requires Stage 3 output: ${required}"
            log_info "Please run Stage 3 (hypothesis-generator) first."
            return 1
        fi
        log_success "Stage 3 output found: ${required}"
    fi

    if [ "${stage}" == "stage5" ] || [ "${stage}" == "feasibility-assessor" ]; then
        local required="${BASE_DIR}/stage4-design/stage4-research-design.md"
        if [ ! -f "${required}" ]; then
            log_error "Stage 5 requires Stage 4 output: ${required}"
            log_info "Please run Stage 4 (design-proposer) first."
            return 1
        fi
        log_success "Stage 4 output found: ${required}"
    fi

    if [ "${stage}" == "stage6" ] || [ "${stage}" == "proposal-integrator" ]; then
        # Check all previous stages
        local required_files=(
            "${BASE_DIR}/stage1-analysis/stage1-paper-analysis.md"
            "${BASE_DIR}/stage2-gaps/stage2-gap-analysis.md"
            "${BASE_DIR}/stage3-hypotheses/stage3-hypotheses.md"
            "${BASE_DIR}/stage4-design/stage4-research-design.md"
            "${BASE_DIR}/stage5-feasibility/stage5-feasibility-assessment.md"
        )

        for file in "${required_files[@]}"; do
            if [ ! -f "${file}" ]; then
                log_error "Stage 6 requires all previous stages. Missing: ${file}"
                return 1
            fi
        done
        log_success "All previous stage outputs found"
    fi

    return 0
}

check_dependencies() {
    log_info "Checking dependencies..."

    # Check if Python is available (for validation scripts)
    if ! command -v python3 &> /dev/null; then
        log_warn "Python 3 not found. Some validation features may be unavailable."
    else
        log_success "Python 3 found: $(python3 --version)"
    fi

    # Check if jq is available (for JSON processing)
    if ! command -v jq &> /dev/null; then
        log_warn "jq not found. JSON processing may be limited."
    else
        log_success "jq found"
    fi

    return 0
}

estimate_duration() {
    local stage="${1}"

    case "${stage}" in
        "stage1"|"paper-analyzer")
            echo "10-15 minutes"
            ;;
        "stage2"|"gap-identifier")
            echo "8-12 minutes"
            ;;
        "stage3"|"hypothesis-generator")
            echo "15-20 minutes"
            ;;
        "stage4"|"design-proposer")
            echo "20-30 minutes"
            ;;
        "stage5"|"feasibility-assessor")
            echo "5-8 minutes"
            ;;
        "stage6"|"proposal-integrator")
            echo "5-10 minutes"
            ;;
        *)
            echo "Unknown"
            ;;
    esac
}

# ============================================================================
# Main Execution
# ============================================================================

main() {
    log_info "=========================================="
    log_info "Pre-Stage Hook Started"
    log_info "Stage: ${STAGE_NAME}"
    log_info "Input: ${INPUT_FILE:-N/A}"
    log_info "Base Directory: ${BASE_DIR}"
    log_info "=========================================="

    # Validate environment
    if ! validate_environment; then
        log_error "Environment validation failed"
        exit 1
    fi

    # Validate input file
    if ! validate_input_file "${STAGE_NAME}" "${INPUT_FILE}"; then
        log_error "Input file validation failed"
        exit 1
    fi

    # Check dependencies (non-blocking)
    check_dependencies

    # Estimate duration
    local duration=$(estimate_duration "${STAGE_NAME}")
    log_info "Estimated duration: ${duration}"

    # Create stage-specific log directory
    local stage_log_dir="${BASE_DIR}/logs/${STAGE_NAME}"
    mkdir -p "${stage_log_dir}"

    # Save metadata
    cat > "${stage_log_dir}/metadata.json" <<EOF
{
  "stage": "${STAGE_NAME}",
  "input_file": "${INPUT_FILE:-null}",
  "base_dir": "${BASE_DIR}",
  "start_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "estimated_duration": "${duration}",
  "validation_status": "passed"
}
EOF

    log_success "Pre-stage validation completed successfully"
    log_info "Stage ${STAGE_NAME} is ready to execute"
    log_info "Log file: ${LOG_FILE}"
    log_info "=========================================="

    exit 0
}

# Run main function
main "$@"
