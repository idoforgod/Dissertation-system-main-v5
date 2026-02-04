# Thesis Workflow Automation Hook

**Version**: 1.0.0
**Type**: PostToolUse Hook
**Purpose**: Automatic post-processing after thesis workflow agent completion

---

## Philosophy: Minimally Invasive

This hook **does NOT modify** the existing thesis-orchestrator workflow. It **ONLY adds** automation that was designed but not implemented:

✅ **Preserves**:
- All existing command files (`.claude/commands/thesis/*.md`)
- All existing agent definitions
- All existing workflow logic
- 100% of original workflow philosophy

✅ **Adds**:
- Automatic checklist updates
- Automatic session state tracking
- Automatic Korean translation triggers
- Audit logging

---

## How It Works

### Trigger Conditions

This hook activates when:
1. **Tool**: `Task` tool completes
2. **Subagent**: One of 42 thesis-related agents (e.g., `literature-searcher`, `synthesis-agent`)
3. **Context**: Working directory contains `thesis-output/` session

### Automation Flow

```
Agent Completes
    ↓
PostToolUse Hook Triggered
    ↓
├─► Update Checklist (todo-checklist.md)
│   └─ Mark step as completed [x]
│   └─ Update progress footer
│
├─► Update Session State (session.json)
│   └─ Increment current_step
│   └─ Record last_agent
│   └─ Update current_phase
│
├─► Log Completion (workflow-execution.log)
│   └─ Timestamp + agent name
│
└─► Check Translation Trigger
    └─ If at wave/phase boundary:
        └─ Queue auto-translation
        └─ Log to auto-translation.log
```

---

## Agent-to-Step Mapping

| Agent | Step | Phase/Wave |
|-------|------|------------|
| `literature-searcher` | 23 | Phase 1 Wave 1 |
| `seminal-works-analyst` | 27 | Phase 1 Wave 1 |
| `trend-analyst` | 31 | Phase 1 Wave 1 |
| `methodology-scanner` | 33 | Phase 1 Wave 1 |
| ... | ... | ... |
| `research-synthesizer` | 82 | Phase 1 Wave 5 |

*(Full mapping in source code)*

---

## Translation Triggers

Auto-translation is triggered at these checkpoints:

| Step | Trigger | Directory |
|------|---------|-----------|
| 33 | Wave 1 complete | `01-literature/` |
| 49 | Wave 2 complete | `01-literature/` |
| 65 | Wave 3 complete | `01-literature/` |
| 73 | Wave 4 complete | `01-literature/` |
| 82 | Wave 5 complete (Phase 1) | `01-literature/` |
| 108 | Phase 2 complete | `02-research-design/` |
| 132 | Phase 3 complete | `03-thesis/` |
| 146 | Phase 4 complete | `04-publication/` |

---

## Output Files

### Checklist Updates

**Before**:
```markdown
- [ ] 23. @literature-searcher 완료

**진행 상태**: Step 22 / 150
**현재 Phase**: Phase 1 Wave 1 - 기초 문헌 탐색
```

**After** (automatic):
```markdown
- [x] 23. @literature-searcher 완료

**진행 상태**: Step 23 / 150
**현재 Phase**: Phase 1 Wave 1 - 기초 문헌 탐색
```

### Session Updates

**Before**:
```json
{
  "workflow": {
    "current_step": 1,
    "current_phase": "phase0",
    "last_agent": null
  }
}
```

**After** (automatic):
```json
{
  "workflow": {
    "current_step": 23,
    "current_phase": "phase1",
    "last_agent": "literature-searcher",
    "last_checkpoint": "2026-01-22T10:30:00Z"
  },
  "updated_at": "2026-01-22T10:30:00Z"
}
```

### Log Files

**`workflow-execution.log`**:
```
[2026-01-22T10:15:00] Step 23: @literature-searcher completed
[2026-01-22T10:22:30] Step 27: @seminal-works-analyst completed
[2026-01-22T10:29:45] Step 31: @trend-analyst completed
```

**`auto-translation.log`**:
```
[2026-01-22T10:35:00] wave1: 4 files queued for translation
  - wave1-01-literature-search.md
  - wave1-02-seminal-works.md
  - wave1-03-trend-analysis.md
  - wave1-04-methodology-scan.md
```

---

## Testing

### Manual Test

```bash
# 1. Navigate to project root
cd /Users/cys/Desktop/AIagentsAutomation/Dissertation-system-main-v1

# 2. Run test mode
python .claude/hooks/post-tool-use/thesis-workflow-automation.py
```

**Expected Output**:
```
============================================================
📋 Post-Processing: @literature-searcher
============================================================
✅ Checklist updated: Step 23 completed
   Progress: 23/150 (15.3%)
✅ Session updated: phase1 - Step 23
============================================================

=== Test Result ===
Context returned: True
```

### Integration Test

Run actual workflow and verify automation:

```bash
# Start workflow
/thesis:start question "Your research question"

# After first agent completes, check:
cat thesis-output/*/00-session/todo-checklist.md  # Should show [x] for completed steps
cat thesis-output/*/00-session/session.json       # Should show current_step > 1
cat thesis-output/*/00-session/workflow-execution.log  # Should show agent completions
```

---

## Troubleshooting

### Issue: Hook not triggering

**Symptom**: Agent completes but checklist not updated

**Solution**:
1. Check hook file exists: `.claude/hooks/post-tool-use/thesis-workflow-automation.py`
2. Check executable permission: `chmod +x thesis-workflow-automation.py`
3. Check working directory contains `thesis-output/`
4. Check Claude Code hooks are enabled in settings

### Issue: Import errors

**Symptom**: `ImportError: cannot import checklist_manager`

**Solution**:
1. Verify scripts exist in `.claude/skills/thesis-orchestrator/scripts/`
2. Check Python path configuration
3. Hook will gracefully degrade if imports fail (non-critical)

### Issue: Translation not triggered

**Symptom**: Wave completes but no Korean files

**Solution**:
1. Check `auto-translation.log` to confirm trigger
2. Manually run: `/thesis:translate thesis-output/<session>/01-literature/`
3. Translation is queued but requires manual execution (by design)

---

## Design Decisions

### Why Queue Translation Instead of Execute?

**Decision**: Hook logs translation intent but doesn't execute

**Rationale**:
1. Translation is expensive (90 minutes for full dissertation)
2. User should control when to spend API credits
3. User can review English output before translating
4. Maintains separation of concerns (hook = tracking, command = action)

**Alternative**: Set `AUTO_EXECUTE_TRANSLATION = True` in hook to auto-run

### Why PostToolUse Instead of PreToolUse?

**Decision**: Run hook AFTER agent completion

**Rationale**:
1. Need confirmation agent succeeded before updating progress
2. Can access tool_output to verify success
3. Matches semantic meaning ("this step is done")

### Why Not Modify Commands Directly?

**Decision**: Use hooks instead of editing command files

**Rationale**:
1. **Minimally invasive**: Zero changes to existing files
2. **Modular**: Can disable by removing hook file
3. **Testable**: Can test hook independently
4. **Maintainable**: Clear separation of workflow vs. automation

---

## Future Enhancements (P1/P2)

### P1: Gate Automation
- Hook detects gate steps (34, 50, 66, 74, 82)
- Auto-executes `cross_validator.py`, `gate_controller.py`
- Blocks progression if gate fails

### P2: Auto-Translation Execution
- Add flag: `AUTO_TRANSLATE = True`
- Hook directly invokes `/thesis:translate` command
- Provides real-time progress updates

### P2: Retry Logic
- Hook detects agent failures
- Automatically re-runs failed agents (max 3 attempts)
- Logs retry attempts

---

## Maintenance

### Updating Agent-Step Mapping

If new agents are added to the workflow:

1. Edit `AGENT_STEP_MAP` dictionary in hook
2. Add new translation triggers to `TRANSLATION_TRIGGERS` if needed
3. Test with dummy context

### Updating Translation Triggers

If wave/phase boundaries change:

1. Edit `TRANSLATION_TRIGGERS` dictionary
2. Ensure keys match step numbers from agent mapping
3. Verify directory paths in `translation_targets`

---

## Version History

### v1.0.0 (2026-01-22)
- Initial release
- Automatic checklist updates
- Automatic session state tracking
- Translation trigger logging
- Audit trail logging

---

## License

Part of Thesis Orchestrator v2.1.0
Preserves 100% of original workflow philosophy

---

## Support

For issues or questions:
1. Check `workflow-execution.log` for audit trail
2. Check `auto-translation.log` for translation queue
3. Verify hook permissions: `ls -la .claude/hooks/post-tool-use/`
4. Test hook manually: `python thesis-workflow-automation.py`

**Remember**: This hook is designed to be **invisible** during normal operation. If you notice it, something is probably wrong. Good automation is silent automation.
