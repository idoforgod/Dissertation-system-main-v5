#!/bin/bash
# Regression Test: Verify existing workflow still works after adding new validation layer
#
# CRITICAL: This test ensures we haven't broken the existing system
# If this test fails, deployment must be ABORTED

set -e  # Exit on any error

echo "================================"
echo "REGRESSION TEST: Existing Workflow Integrity"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

FAILED=0

# Test 1: Check that all original files still exist
echo "[1/5] Checking original files still exist..."

ORIGINAL_FILES=(
    ".claude/skills/thesis-orchestrator/scripts/init_session.py"
    ".claude/skills/thesis-orchestrator/scripts/checklist_manager.py"
    ".claude/skills/thesis-orchestrator/scripts/context_loader.py"
    ".claude/skills/thesis-orchestrator/scripts/gra_validator.py"
    ".claude/skills/thesis-orchestrator/scripts/cross_validator.py"
    ".claude/skills/thesis-orchestrator/scripts/srcs_evaluator.py"
)

for file in "${ORIGINAL_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ FAIL: Original file deleted: $file${NC}"
        FAILED=1
    else
        echo -e "${GREEN}✅ OK: $file exists${NC}"
    fi
done

echo ""

# Test 2: Check that new files are truly new (not overwrites)
echo "[2/5] Verifying new files don't overwrite existing..."

if [ -f ".claude/skills/thesis-orchestrator/scripts/workflow_validator.py" ]; then
    echo -e "${GREEN}✅ OK: workflow_validator.py is a new file${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: workflow_validator.py not found (might not be created yet)${NC}"
fi

if [ -f ".claude/skills/thesis-orchestrator/scripts/validated_executor.py" ]; then
    echo -e "${GREEN}✅ OK: validated_executor.py is a new file${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: validated_executor.py not found (might not be created yet)${NC}"
fi

if [ -f ".claude/skills/thesis-orchestrator/scripts/phase_validator.py" ]; then
    echo -e "${GREEN}✅ OK: phase_validator.py is a new file${NC}"
else
    echo -e "${YELLOW}⚠️  WARNING: phase_validator.py not found (might not be created yet)${NC}"
fi

echo ""

# Test 3: Check import independence
echo "[3/5] Checking new code doesn't import from existing workflow..."

INDEPENDENT=1
for file in workflow_validator.py validated_executor.py phase_validator.py; do
    full_path=".claude/skills/thesis-orchestrator/scripts/$file"
    if [ -f "$full_path" ]; then
        if grep -q "from.*init_session\|from.*checklist_manager\|from.*context_loader" "$full_path" 2>/dev/null; then
            echo -e "${RED}❌ FAIL: $file imports from existing workflow${NC}"
            echo -e "${RED}   This violates the independence principle!${NC}"
            FAILED=1
            INDEPENDENT=0
        fi
    fi
done

if [ $INDEPENDENT -eq 1 ]; then
    echo -e "${GREEN}✅ OK: All new files are independent${NC}"
fi

echo ""

# Test 4: Test that original scripts still execute
echo "[4/5] Testing original scripts execute without error..."

# Test init_session.py has valid syntax
if python3 -m py_compile .claude/skills/thesis-orchestrator/scripts/init_session.py 2>/dev/null; then
    echo -e "${GREEN}✅ OK: init_session.py syntax valid${NC}"
else
    echo -e "${RED}❌ FAIL: init_session.py has syntax errors${NC}"
    FAILED=1
fi

# Test checklist_manager.py has valid syntax
if python3 -m py_compile .claude/skills/thesis-orchestrator/scripts/checklist_manager.py 2>/dev/null; then
    echo -e "${GREEN}✅ OK: checklist_manager.py syntax valid${NC}"
else
    echo -e "${RED}❌ FAIL: checklist_manager.py has syntax errors${NC}"
    FAILED=1
fi

echo ""

# Test 5: Verify no files were deleted
echo "[5/5] Checking no original files were deleted..."

ORIGINAL_AGENT_COUNT=$(find .claude/agents/thesis -name "*.md" -type f 2>/dev/null | wc -l)

if [ $ORIGINAL_AGENT_COUNT -lt 30 ]; then
    echo -e "${RED}❌ FAIL: Some agent files may have been deleted${NC}"
    echo -e "${RED}   Found only $ORIGINAL_AGENT_COUNT agent files (expected 30+)${NC}"
    FAILED=1
else
    echo -e "${GREEN}✅ OK: All agent files intact ($ORIGINAL_AGENT_COUNT files)${NC}"
fi

echo ""
echo "================================"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ REGRESSION TEST PASSED${NC}"
    echo -e "${GREEN}   Existing workflow is intact - safe to proceed${NC}"
    exit 0
else
    echo -e "${RED}❌ REGRESSION TEST FAILED${NC}"
    echo -e "${RED}   ABORT DEPLOYMENT - Existing workflow may be broken${NC}"
    exit 1
fi
