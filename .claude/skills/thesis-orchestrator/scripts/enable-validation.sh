#!/bin/bash
# Enable Validation - Quick Helper Script
#
# This script enables validation for the thesis workflow.
# It sets environment variables and provides user-friendly output.

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Enable Validation${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Set environment variables
export USE_VALIDATION=true
export FAIL_FAST=true

echo -e "${GREEN}✅ Validation ENABLED${NC}"
echo ""
echo "Settings:"
echo "  USE_VALIDATION=true"
echo "  FAIL_FAST=true"
echo ""

# Save to config file using Python helper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/validation_config.py" --enable --fail-fast true > /dev/null 2>&1

echo "Configuration saved to:"
echo "  ~/.thesis-orchestrator/validation.json"
echo ""

echo -e "${BLUE}================================${NC}"
echo "Next Steps:"
echo -e "${BLUE}================================${NC}"
echo ""
echo "1. Run workflow with validation:"
echo "   /thesis:run-writing-validated"
echo ""
echo "2. Check progress:"
echo "   /thesis:progress"
echo ""
echo "3. Validate specific phase:"
echo "   /thesis:validate-phase 3"
echo ""
echo "4. Disable validation:"
echo "   bash $SCRIPT_DIR/disable-validation.sh"
echo ""
