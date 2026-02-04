# Agent Structure Fix Plan

## Problem
- Agents are nested in subdirectories (thesis/phase1-literature/wave1/*.md)
- Task tool cannot find agents in subdirectories
- Need flat structure in .claude/agents/

## Solution Options

### Option 1: Flatten with Prefixes (RECOMMENDED)
Move all files to .claude/agents/ with naming convention:
- thesis-phase1-wave1-literature-searcher.md
- thesis-phase2-quantitative-hypothesis-developer.md
- etc.

### Option 2: Symbolic Links
Create symlinks in .claude/agents/ pointing to nested files

### Option 3: Update Task Tool
Modify Task tool to support subdirectory search (requires system change)

## Current Agent Count
```bash
find thesis -name "*.md" -type f | wc -l
# Result: (to be filled)
```

## Action Plan
1. Disable hooks (DONE)
2. Create backup of thesis/ directory
3. Flatten agent files with prefix naming
4. Test agent invocation
5. Re-enable hooks with timeout fix

