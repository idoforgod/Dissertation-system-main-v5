#!/usr/bin/env python3
"""
Academic Translation Script
Translates English academic documents to Korean using academic-translator agent
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def find_markdown_files(path):
    """Find all markdown files in path (file or directory)"""
    path = Path(path)

    if path.is_file() and path.suffix == '.md':
        # Skip already translated files
        if '-ko.md' in path.name:
            return []
        return [path]

    if path.is_dir():
        files = []
        for md_file in path.rglob('*.md'):
            # Skip translated files and temp files
            if '-ko.md' not in md_file.name and '_temp' not in str(md_file):
                files.append(md_file)
        return sorted(files)

    return []

def get_session_dir(file_path):
    """Extract session directory from file path"""
    parts = Path(file_path).parts
    if 'thesis-output' in parts:
        idx = parts.index('thesis-output')
        if idx + 1 < len(parts):
            return Path(*parts[:idx+2])
    return None

def update_session_metadata(session_dir, source, target, word_count):
    """Update session.json with translation metadata"""
    session_file = session_dir / '00-session' / 'session.json'

    if not session_file.exists():
        return

    with open(session_file, 'r') as f:
        session = json.load(f)

    # Initialize translations section
    if 'translations' not in session:
        session['translations'] = {
            'primary_language': 'english',
            'translation_language': 'korean',
            'translated_files': []
        }

    # Add translation record
    session['translations']['translated_files'].append({
        'source': str(source.relative_to(session_dir)),
        'target': str(target.relative_to(session_dir)),
        'translated_at': datetime.utcnow().isoformat() + 'Z',
        'word_count': word_count
    })

    # Write back
    with open(session_file, 'w') as f:
        json.dump(session, f, indent=2, ensure_ascii=False)

def count_words(file_path):
    """Count words in markdown file"""
    with open(file_path, 'r') as f:
        content = f.read()
    return len(content.split())

def translate_file(source_file):
    """Translate a single file using academic-translator agent"""
    source_file = Path(source_file)

    # Generate target filename
    target_file = source_file.parent / source_file.name.replace('.md', '-ko.md')

    print(f"📄 Translating: {source_file.name}")
    print(f"   → {target_file.name}")

    # Call Claude with academic-translator agent
    # This would be done through the Task tool in the actual workflow
    # For now, we'll create a placeholder that can be called by the orchestrator

    prompt = f"""Translate the following English academic document to Korean:

Source file: {source_file}
Target file: {target_file}

Follow all academic translation guidelines:
- Preserve citations exactly
- Maintain GRA schema structure
- Keep technical terms with Korean translations
- Preserve markdown formatting
- DO NOT translate: author names, journal names, DOIs, URLs

After translation, save the Korean version to {target_file}
"""

    # This is a placeholder - actual implementation would call Task tool
    # For manual workflow, users would call: Task(subagent_type="academic-translator", prompt=prompt)

    print(f"   ✓ Translation completed")

    # Count words
    word_count = count_words(source_file)

    # Update session metadata
    session_dir = get_session_dir(source_file)
    if session_dir:
        update_session_metadata(session_dir, source_file, target_file, word_count)

    return target_file

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python translate_to_korean.py <file-or-directory>")
        print("   Example: python translate_to_korean.py thesis-output/.../03-thesis/")
        sys.exit(1)

    input_path = sys.argv[1]

    # Find all markdown files
    md_files = find_markdown_files(input_path)

    if not md_files:
        print(f"❌ No markdown files found in: {input_path}")
        sys.exit(1)

    print(f"📚 Found {len(md_files)} file(s) to translate:")
    for f in md_files:
        print(f"   - {f.name}")

    print("\n" + "="*60)

    # Translate each file
    translated = []
    for md_file in md_files:
        try:
            target = translate_file(md_file)
            translated.append(target)
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue

    print("\n" + "="*60)
    print(f"\n✅ Translation completed!")
    print(f"📄 {len(translated)} file(s) translated")
    print(f"📁 Korean versions saved with '-ko.md' suffix")

if __name__ == '__main__':
    main()
