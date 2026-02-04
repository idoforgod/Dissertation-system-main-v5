#!/usr/bin/env python3
"""
Word Export Trigger Hook

Automatically triggers Word document export when Phase 3 (Thesis Writing) completes.
Creates unified dissertation document with all chapters merged.

Hook Event: PostToolUse
Triggers: After thesis-reviewer completes (step 132 - Phase 3 complete)

Philosophy: MINIMALLY INVASIVE
- Does NOT modify workflow commands
- ONLY triggers export automation that was designed but not implemented
- Preserves existing export script functionality

Features:
- Auto-detects Phase 3 completion
- Exports both English and Korean versions
- Merges all chapters into single Word document
- Updates session metadata
- Provides download-ready thesis file

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-22
"""

import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "skills" / "thesis-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


# ============================================================================
# Configuration
# ============================================================================

# Agent that marks Phase 3 completion
PHASE3_COMPLETION_AGENT = 'thesis-reviewer'

# Export script path
EXPORT_SCRIPT = SCRIPT_DIR / 'export_to_docx.js'

# Chapter order (standard dissertation structure)
CHAPTER_ORDER = [
    'chapter1-introduction',
    'chapter2-literature-review',
    'chapter3-methodology',
    'chapter4-results',
    'chapter5-conclusion'
]


# ============================================================================
# Helper Functions
# ============================================================================

def find_session_dir(working_dir: str) -> Optional[Path]:
    """Find current thesis session directory.

    Args:
        working_dir: Working directory

    Returns:
        Session directory path or None
    """
    working_path = Path(working_dir)

    # Check for marker file
    marker_file = working_path / "thesis-output" / ".current-working-dir.txt"
    if marker_file.exists():
        session_dir = marker_file.read_text().strip()
        return Path(session_dir)

    # Fallback: most recent session
    thesis_output = working_path / "thesis-output"
    if not thesis_output.exists():
        return None

    session_dirs = [d for d in thesis_output.iterdir() if d.is_dir() and d.name != '_temp']
    if not session_dirs:
        return None

    return max(session_dirs, key=lambda d: d.stat().st_mtime)


def find_chapter_files(thesis_dir: Path) -> List[Path]:
    """Find all chapter markdown files in thesis directory.

    Args:
        thesis_dir: Thesis directory (03-thesis/)

    Returns:
        List of chapter file paths in order
    """
    if not thesis_dir.exists():
        return []

    chapter_files = []

    # Find files in standard order
    for chapter_name in CHAPTER_ORDER:
        # Check for English version
        en_file = thesis_dir / f"{chapter_name}.md"
        if en_file.exists():
            chapter_files.append(en_file)

    # If no files found with standard naming, try glob
    if not chapter_files:
        chapter_files = sorted(thesis_dir.glob("chapter*.md"))
        # Exclude Korean versions
        chapter_files = [f for f in chapter_files if '-ko.md' not in f.name]

    return chapter_files


def merge_chapters_to_markdown(chapter_files: List[Path], output_file: Path) -> bool:
    """Merge all chapter files into single markdown file.

    Args:
        chapter_files: List of chapter markdown files
        output_file: Output merged markdown file

    Returns:
        True if successful, False otherwise
    """
    try:
        merged_content = []

        merged_content.append("# Doctoral Dissertation\n\n")
        merged_content.append("---\n\n")

        for i, chapter_file in enumerate(chapter_files, 1):
            print(f"   Merging: {chapter_file.name}")

            with open(chapter_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Add chapter separator
            if i > 1:
                merged_content.append("\n\n---\n\n")

            merged_content.append(content)

        # Write merged content
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(''.join(merged_content))

        return True

    except Exception as e:
        print(f"   ❌ Error merging chapters: {e}")
        return False


def convert_markdown_to_docx(md_file: Path, docx_file: Path) -> bool:
    """Convert markdown file to Word document using pandoc.

    Args:
        md_file: Input markdown file
        docx_file: Output Word document file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Check if pandoc is available
        result = subprocess.run(
            ['which', 'pandoc'],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print("   ⚠️  Pandoc not installed. Install with: brew install pandoc")
            return False

        # Convert using pandoc
        print(f"   Converting: {md_file.name} → {docx_file.name}")

        result = subprocess.run(
            [
                'pandoc',
                str(md_file),
                '-o', str(docx_file),
                '--from', 'markdown',
                '--to', 'docx',
                '--reference-doc', str(SCRIPT_DIR / 'templates' / 'dissertation-template.docx')
                if (SCRIPT_DIR / 'templates' / 'dissertation-template.docx').exists()
                else ''
            ],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes
        )

        if result.returncode == 0:
            print(f"   ✅ Word document created: {docx_file.name}")
            return True
        else:
            print(f"   ❌ Pandoc error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("   ❌ Conversion timeout (5 minutes)")
        return False
    except Exception as e:
        print(f"   ❌ Conversion error: {e}")
        return False


def export_thesis_to_word(session_dir: Path) -> Dict[str, any]:
    """Export thesis chapters to Word document.

    Args:
        session_dir: Session directory

    Returns:
        Export result dictionary
    """
    result = {
        'success': False,
        'en_docx': None,
        'ko_docx': None,
        'chapter_count': 0,
        'total_words': 0,
        'error': None
    }

    try:
        thesis_dir = session_dir / "03-thesis"

        if not thesis_dir.exists():
            result['error'] = "Thesis directory not found"
            return result

        # Find chapter files
        chapter_files = find_chapter_files(thesis_dir)

        if not chapter_files:
            result['error'] = "No chapter files found"
            return result

        result['chapter_count'] = len(chapter_files)
        print(f"   Found {len(chapter_files)} chapter(s)")

        # Merge English chapters
        en_merged = thesis_dir / "dissertation-full-en.md"
        if not merge_chapters_to_markdown(chapter_files, en_merged):
            result['error'] = "Failed to merge English chapters"
            return result

        # Convert English to Word
        en_docx = thesis_dir / "dissertation-full-en.docx"
        if convert_markdown_to_docx(en_merged, en_docx):
            result['en_docx'] = str(en_docx.relative_to(session_dir))

        # Find Korean chapter files
        ko_chapter_files = []
        for chapter_file in chapter_files:
            ko_file = chapter_file.parent / chapter_file.name.replace('.md', '-ko.md')
            if ko_file.exists():
                ko_chapter_files.append(ko_file)

        # Merge Korean chapters (if available)
        if ko_chapter_files:
            ko_merged = thesis_dir / "dissertation-full-ko.md"
            if merge_chapters_to_markdown(ko_chapter_files, ko_merged):
                # Convert Korean to Word
                ko_docx = thesis_dir / "dissertation-full-ko.docx"
                if convert_markdown_to_docx(ko_merged, ko_docx):
                    result['ko_docx'] = str(ko_docx.relative_to(session_dir))

        # Count total words
        with open(en_merged, 'r', encoding='utf-8') as f:
            content = f.read()
            result['total_words'] = len(content.split())

        result['success'] = True
        return result

    except Exception as e:
        result['error'] = str(e)
        return result


def update_session_with_export(session_dir: Path, export_result: Dict):
    """Update session.json with export metadata.

    Args:
        session_dir: Session directory
        export_result: Export result dictionary
    """
    session_file = session_dir / "00-session" / "session.json"

    if not session_file.exists():
        return

    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            session = json.load(f)

        # Initialize exports section
        if 'exports' not in session:
            session['exports'] = []

        # Add export record
        export_record = {
            'export_id': len(session['exports']) + 1,
            'exported_at': datetime.now().isoformat(),
            'type': 'word_document',
            'en_document': export_result.get('en_docx'),
            'ko_document': export_result.get('ko_docx'),
            'chapter_count': export_result.get('chapter_count', 0),
            'total_words': export_result.get('total_words', 0),
            'success': export_result.get('success', False)
        }

        session['exports'].append(export_record)

        # Update workflow status
        if 'workflow' not in session:
            session['workflow'] = {}

        session['workflow']['phase3_exported'] = True
        session['workflow']['export_timestamp'] = datetime.now().isoformat()

        # Write back
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"   ⚠️  Failed to update session: {e}")


def log_export(session_dir: Path, export_result: Dict):
    """Log export event.

    Args:
        session_dir: Session directory
        export_result: Export result dictionary
    """
    try:
        log_dir = session_dir / "00-session"
        log_file = log_dir / "word-export.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Export Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Success: {export_result['success']}\n")
            f.write(f"Chapters: {export_result['chapter_count']}\n")
            f.write(f"Total Words: {export_result['total_words']}\n")

            if export_result['en_docx']:
                f.write(f"English DOCX: {export_result['en_docx']}\n")
            if export_result['ko_docx']:
                f.write(f"Korean DOCX: {export_result['ko_docx']}\n")

            if export_result['error']:
                f.write(f"Error: {export_result['error']}\n")

            f.write(f"{'='*60}\n")

    except Exception:
        pass  # Silent failure for logging


# ============================================================================
# Hook Function
# ============================================================================

def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PostToolUse hook for automatic Word export.

    This hook runs AFTER thesis-reviewer completes (end of Phase 3)
    and automatically exports all thesis chapters to Word document.

    Args:
        context: Hook context

    Returns:
        Unmodified context
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    working_dir = context.get('working_directory', os.getcwd())

    # Only process Task tool completions
    if tool_name != 'Task':
        return context

    subagent_type = tool_input.get('subagent_type', '')

    # Normalize agent name (remove suffixes)
    normalized_agent = subagent_type
    for suffix in ['-rlm', '-validated', '-parallel']:
        if normalized_agent.endswith(suffix):
            normalized_agent = normalized_agent[:-len(suffix)]
            break

    # Check if this is Phase 3 completion
    if normalized_agent != PHASE3_COMPLETION_AGENT:
        return context

    # Find session directory
    session_dir = find_session_dir(working_dir)
    if not session_dir:
        return context

    print(f"\n{'='*60}")
    print(f"📄 Word Export Trigger: Phase 3 Complete")
    print(f"{'='*60}")

    try:
        # Execute Word export
        export_result = export_thesis_to_word(session_dir)

        # Log and update session
        log_export(session_dir, export_result)
        update_session_with_export(session_dir, export_result)

        # Report results
        if export_result['success']:
            print(f"✅ Word Export Complete")
            print(f"   Chapters: {export_result['chapter_count']}")
            print(f"   Total Words: {export_result['total_words']:,}")

            if export_result['en_docx']:
                print(f"   📄 English: {export_result['en_docx']}")
            if export_result['ko_docx']:
                print(f"   📄 Korean: {export_result['ko_docx']}")

            print(f"\n💡 Download-ready thesis documents created!")
        else:
            print(f"⚠️  Export Failed")
            print(f"   Error: {export_result['error']}")
            print(f"   💡 Manual export available: /thesis:export-docx")

    except Exception as e:
        print(f"❌ Export error: {e}")

    print(f"{'='*60}\n")

    return context


# ============================================================================
# Test Mode
# ============================================================================

if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'thesis-reviewer',
            'prompt': 'Review thesis...'
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"Export triggered: {result == test_context}")
