---
description: Translate English academic documents to Korean using academic-translator agent
context: fork
agent: general-purpose
---

# Translate Academic Documents to Korean

Automatically translates all English academic outputs to Korean while preserving:
- Citations and references
- GRA (Grounded Research Architecture) schema
- Markdown formatting
- Technical terminology
- **⭐ Doctoral-writing quality standards (80+ compliance score REQUIRED)**

## How It Works

This command identifies all English `.md` files in the session directory and translates them using the **academic-translator** agent. Each translated file is saved with a `-ko.md` suffix.

## Usage

```bash
# Translate specific file
/thesis:translate <file-path>

# Translate entire phase directory
/thesis:translate thesis-output/<session>/03-thesis/

# Translate all outputs in session
/thesis:translate thesis-output/<session>/
```

## Workflow

You must perform the following steps:

### Step 1: Identify Files to Translate

Use Glob or Bash to find all `.md` files in the specified path:
```bash
find <path> -name "*.md" ! -name "*-ko.md" -type f
```

Skip files that are:
- Already translated (`*-ko.md`)
- Temporary (`_temp/`)
- Session metadata (`session.json`)

### Step 2: Translate Each File

For each English source file, invoke the **academic-translator** agent using the Task tool:

```
Task(
  subagent_type="academic-translator",
  model="opus",
  description="Translate academic document to Korean with doctoral-writing standards",
  prompt=f"""
Translate this English academic document to Korean:

Source: {source_file}
Target: {target_file}

Guidelines:
1. Preserve all citations exactly (author names, journal names, DOIs)
2. Maintain GRA GroundedClaim schema structure
3. Translate technical terms with first-occurrence explanation
4. Keep markdown formatting intact
5. Maintain academic tone and rigor

⭐ DOCTORAL-WRITING COMPLIANCE (MANDATORY):
This is NOT just translation—produce high-quality Korean academic text that meets:
- Clarity (명료성): 85+ - Clear subject-predicate, active voice for research actions
- Conciseness (간결성): 82+ - Sentences ~25 words, no redundancy
- Academic Rigor (학술적 엄격성): 90+ - Formal tone, precise terminology
- Logical Flow (논리적 흐름): 85+ - Natural Korean transitions, coherent structure
- OVERALL COMPLIANCE: 80+ (REQUIRED)

Apply doctoral-writing principles at every sentence. Prioritize quality over speed.

Read the source file, translate content with doctoral-writing standards, and write to target file.
"""
)
```

### Step 3: Verify Translation Quality

After each translation:
- Verify `-ko.md` file was created
- Check file size is reasonable (should be similar to English version)
- Confirm markdown structure is preserved
- **⭐ Verify doctoral-writing compliance**:
  - Clarity: Clear subject-predicate, precise terms
  - Conciseness: Sentences ~25 words, no redundancy
  - Academic Rigor: Formal tone, consistent terminology
  - Logical Flow: Natural Korean transitions
  - **Overall: 80+ compliance score (MANDATORY)**

### Step 4: Update Session Metadata

Read session.json and add translation record:

```python
{
  "translations": {
    "primary_language": "english",
    "translation_language": "korean",
    "translated_files": [
      {
        "source": "03-thesis/chapter1-introduction.md",
        "target": "03-thesis/chapter1-introduction-ko.md",
        "translated_at": "2026-01-20T14:00:00Z",
        "word_count": 5420
      }
    ]
  }
}
```

### Step 5: Report Results

Provide a summary:
```
✅ Translation completed!
📚 Translated files:
   1. chapter1-introduction.md → chapter1-introduction-ko.md (5,420 words)
   2. chapter2-literature-review.md → chapter2-literature-review-ko.md (12,350 words)
   3. chapter3-methodology.md → chapter3-methodology-ko.md (8,200 words)
   ...

📁 Korean versions available at: thesis-output/<session>/
```

## Output Structure

```
thesis-output/<session-dir>/
├── 01-literature-review/
│   ├── wave1-literature-search.md (English)
│   ├── wave1-literature-search-ko.md (Korean) ⭐
│   ├── wave2-theoretical-framework.md (English)
│   └── wave2-theoretical-framework-ko.md (Korean) ⭐
├── 02-research-design/
│   ├── research-design-report.md (English)
│   └── research-design-report-ko.md (Korean) ⭐
└── 03-thesis/
    ├── chapter1-introduction.md (English)
    ├── chapter1-introduction-ko.md (Korean) ⭐
    ├── chapter2-literature-review.md (English)
    ├── chapter2-literature-review-ko.md (Korean) ⭐
    ...
```

## Translation Standards

### What Gets Translated
- All prose and narrative text
- Section headers and titles
- Table headers and content
- GroundedClaim text and uncertainty fields
- Figure captions

### What Stays in English
- Author names: "List, C." NOT "리스트, C."
- Journal names: "Minds and Machines"
- DOIs and URLs
- Statistical notation: `(β = 0.45, p < .001)`
- GroundedClaim IDs: `LIT-001`
- Field names: `claim_type`, `confidence`, etc.

### Example Translation

**English** (`chapter1-introduction.md`):
```markdown
## 1.1 Research Background

The question of free will in artificial intelligence has gained prominence
as AI systems demonstrate increasingly sophisticated decision-making
capabilities (List, 2019; Martela, 2025).

**GroundedClaim: INT-001**
- Text: AI systems can exhibit functional free will through recursive self-modeling
- Type: THEORETICAL
- Source: List (2019, p. 87)
- Confidence: 75
```

**Korean** (`chapter1-introduction-ko.md`):
```markdown
## 1.1 연구 배경

인공지능의 자유의지 문제는 AI 시스템이 점점 더 정교한 의사결정
능력을 보여줌에 따라 중요성을 얻고 있다(List, 2019; Martela, 2025).

**GroundedClaim: INT-001**
- Text: AI 시스템은 재귀적 자기 모델링을 통해 기능적 자유의지를 나타낼 수 있다
- Type: THEORETICAL
- Source: List (2019, p. 87)
- Confidence: 75
```

## Integration with Workflow

This command is **automatically invoked** after each phase completion:

```
Phase 1 (English) → /thesis:translate → Phase 1 (Korean)
Phase 2 (English) → /thesis:translate → Phase 2 (Korean)
Phase 3 (English) → /thesis:translate → Phase 3 (Korean)
```

Users can also manually invoke for specific files or directories.

## Error Handling

| Issue | Action |
|-------|--------|
| Source file not found | Skip and report |
| Target file exists | Overwrite with confirmation |
| Translation fails | Retry once, then skip and report |
| GRA validation fails | Flag for manual review |

## Quality Assurance

After translation:
1. Verify all citations intact using Grep
2. Confirm GRA schema valid
3. Check markdown renders correctly
4. Ensure technical terms consistent across files
5. **⭐ Verify doctoral-writing compliance (MANDATORY)**:
   - Clarity Score: 85+ (clear subject-predicate, precise terms)
   - Conciseness Score: 82+ (sentences ~25 words, no redundancy)
   - Academic Rigor: 90+ (formal tone, consistent terminology)
   - Logical Flow: 85+ (natural Korean transitions, coherent structure)
   - **Overall Compliance: 80+ (REQUIRED for all translations)**

   If any translation scores below 80, it MUST be revised.

## Performance

- Average translation speed: ~500 words/minute (opus model)
- Typical dissertation (150 pages ≈ 45,000 words): ~90 minutes
- Parallel processing: Up to 3 files simultaneously for optimal performance
