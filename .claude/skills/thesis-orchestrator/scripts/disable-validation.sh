#!/bin/bash
# Disable Validation - Quick Helper Script
#
# This script disables validation and reverts to standard workflow.

set -e

# Colors
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Disable Validation${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Unset environment variables
export USE_VALIDATION=false

echo -e "${YELLOW}⏭️  Validation DISABLED${NC}"
echo ""
echo "Settings:"
echo "  USE_VALIDATION=false"
echo ""

# Save to config file using Python helper
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/validation_config.py" --disable > /dev/null 2>&1

echo "Configuration saved to:"
echo "  ~/.thesis-orchestrator/validation.json"
echo ""

echo -e "${BLUE}================================${NC}"
echo "Next Steps:"
echo -e "${BLUE}================================${NC}"
echo ""
echo "Using standard workflow (no validation)"
echo ""
echo "1. Run standard writing:"
echo "   /thesis:run-writing"
echo ""
echo "2. Check status:"
echo "   /thesis:status"
echo ""
echo "3. Re-enable validation:"
echo "   bash $SCRIPT_DIR/enable-validation.sh"
echo ""
echo "Note: You can still manually validate anytime:"
echo "  /thesis:validate-all"
echo "  /thesis:validate-phase 3"
echo ""
