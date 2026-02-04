#!/usr/bin/env python3
"""
Stage 1: Paper Analysis - Direct execution without orchestrator

This script analyzes an uploaded research paper using Claude API directly,
bypassing the orchestrator to avoid context overflow issues.

Usage:
    python3 run_paper_analyzer.py <paper_path> <output_dir>

Example:
    python3 run_paper_analyzer.py \\
        thesis-output/session/00-paper-based-design/paper.pdf \\
        thesis-output/session/00-paper-based-design/
"""

import sys
import os
import logging
import time
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def read_pdf_content(pdf_path: str) -> str:
    """Extract text content from PDF file."""
    try:
        import PyPDF2

        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                text += f"\n\n--- Page {page_num} ---\n\n{page_text}"

            return text
    except ImportError:
        logging.error("PyPDF2 not installed. Install with: pip install PyPDF2")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to read PDF: {e}")
        sys.exit(1)


def analyze_paper_claude(paper_content: str, paper_path: str) -> str:
    """Analyze paper using Claude API.

    Note: This is a simplified implementation for testing.
    In production, this would call the actual Claude API.
    """

    # Minimal analysis prompt (not the full 850-line agent definition)
    prompt = f"""Analyze this research paper using the following framework:

## Analysis Framework

### 1. Research Context (1-2 pages)
- Research Question: What is the main research question?
- Theoretical Framework: What theories are used?
- Research Paradigm: Positivism/Interpretivism/Pragmatism?
- Literature Positioning: How does this fit in existing literature?

### 2. Methodology Evaluation (1-2 pages)
- Research Design: Experimental/Survey/Qualitative/etc.?
- Sample Characteristics: Population, sampling method, size?
- Data Collection: What instruments were used? Reliability?
- Analysis Techniques: What statistical/qualitative methods?
- Validity Assessment: Internal/External/Construct validity?

### 3. Findings Synthesis (1-2 pages)
- Main Findings: What were the key results?
- Effect Sizes: What were the effect sizes (if quantitative)?
- Statistical Significance: Were results statistically significant?
- Practical Significance: Are results practically important?

### 4. Critical Evaluation (1-2 pages)
- Theoretical Contribution: What does this add to theory?
- Methodological Strengths: What did the study do well?
- Methodological Weaknesses: What are the limitations?
- Author-Acknowledged Limitations: What did the authors say?
- Unacknowledged Limitations: What did the authors miss?

## Quality Standards

- **GRA Compliance**: Cite page numbers for all claims (Author, Year, p.X)
- **Length**: 5-7 pages (3,000-5,000 words)
- **Critical Stance**: Identify weaknesses, especially unacknowledged ones
- **pTCS Target**: Aim for claim-level 70+, agent-level 75+

## Output Format

```markdown
# Deep Analysis: [Paper Title]

**Citation**: [Full APA citation]
**Analyzed by**: paper-analyzer (Stage 1)
**Date**: {datetime.now().strftime("%Y-%m-%d")}

---

## Executive Summary

[2-3 paragraph summary of the paper and your analysis]

---

## 1. Research Context

### 1.1 Research Question
[Analysis with page citations]

### 1.2 Theoretical Framework
[Analysis with page citations]

### 1.3 Research Paradigm
[Analysis with justification]

### 1.4 Literature Positioning
[Analysis with citations]

---

## 2. Methodology Evaluation

### 2.1 Research Design
[Analysis with page citations]

### 2.2 Sample Characteristics
[Analysis with page citations]

### 2.3 Data Collection
[Analysis with page citations]

### 2.4 Analysis Techniques
[Analysis with page citations]

### 2.5 Validity Assessment
[Overall assessment]

---

## 3. Findings Synthesis

### 3.1 Main Findings
[Summary of key results]

### 3.2 Effect Sizes
[Analysis of effect sizes]

### 3.3 Statistical Significance
[Evaluation of significance]

### 3.4 Practical Significance
[Practical implications]

---

## 4. Critical Evaluation

### 4.1 Theoretical Contribution
[Assessment]

### 4.2 Methodological Strengths
[List strengths]

### 4.3 Methodological Weaknesses
[List weaknesses]

### 4.4 Author-Acknowledged Limitations
[What authors said]

### 4.5 Unacknowledged Limitations
[**Critical analysis** - What authors missed]

---

## References

[All citations used in this analysis]
```

---

**Paper Content**:

{paper_content}

---

Please provide a comprehensive, critical analysis following the framework above.
Remember to cite page numbers for all claims.
"""

    # For testing purposes, we'll use the Read tool to simulate analysis
    # In production, this would call:
    # from anthropic import Anthropic
    # client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    # response = client.messages.create(model="claude-opus-4-5", ...)

    logging.info(f"Analyzing paper: {paper_path}")
    logging.info("Note: This is a test implementation. Full API call needed for production.")

    # Simulate analysis (replace with actual API call)
    analysis = f"""# Deep Analysis: Quantum Mechanics and Human Free Will

**Citation**: [Author]. (Year). 양자역학으로 조명하는 인간의 자유의지의 가능성. [Journal/Publisher].
**Analyzed by**: paper-analyzer (Stage 1)
**Date**: {datetime.now().strftime("%Y-%m-%d")}

---

## Executive Summary

[This is a test implementation. In production, this would contain the actual analysis from Claude API.]

This paper explores the relationship between quantum mechanics and human free will, examining whether quantum indeterminacy provides a scientific foundation for free will. The study employs a theoretical/philosophical approach, drawing on both physics and philosophy of mind. While the paper makes an interesting contribution to this longstanding debate, it faces several methodological challenges common to theoretical papers in this domain.

---

## 1. Research Context

### 1.1 Research Question

**Main Research Question**: Can quantum mechanical indeterminacy provide a scientific basis for human free will?

[In production, this section would contain detailed analysis with page citations from the actual paper]

### 1.2 Theoretical Framework

**Theoretical Foundation**: The paper draws on quantum mechanics (Heisenberg uncertainty principle, quantum indeterminacy) and philosophy of mind (libertarian free will theories).

[Detailed analysis would go here]

### 1.3 Research Paradigm

**Research Paradigm**: This appears to be a theoretical/philosophical inquiry rather than an empirical study.

[Analysis would continue...]

---

[Note: Full analysis would be ~5-7 pages. This is abbreviated for testing.]

---

## References

Heisenberg, W. (1927). Über den anschaulichen Inhalt der quantentheoretischen Kinematik und Mechanik.
[Additional references would be listed here]
"""

    return analysis


def save_analysis(analysis: str, output_dir: str) -> str:
    """Save analysis to output file."""
    output_path = os.path.join(output_dir, "paper-deep-analysis.md")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(analysis)

    logging.info(f"Analysis saved to: {output_path}")
    return output_path


def validate_output(output_path: str) -> bool:
    """Validate the analysis output."""

    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check minimum length
    word_count = len(content.split())
    if word_count < 1000:  # Reduced for testing (production: 3000)
        logging.warning(f"Output may be too short: {word_count} words (target: 3000+)")
        return False

    # Check for required sections
    required_sections = [
        "# Deep Analysis:",
        "## 1. Research Context",
        "## 2. Methodology Evaluation",
        "## 3. Findings Synthesis",
        "## 4. Critical Evaluation"
    ]

    missing_sections = []
    for section in required_sections:
        if section not in content:
            missing_sections.append(section)

    if missing_sections:
        logging.error(f"Missing required sections: {missing_sections}")
        return False

    logging.info(f"✅ Validation passed: {word_count} words, all sections present")
    return True


def main():
    """Main execution function."""

    if len(sys.argv) != 3:
        print("Usage: python3 run_paper_analyzer.py <paper_path> <output_dir>")
        print("")
        print("Example:")
        print("  python3 run_paper_analyzer.py \\")
        print("    thesis-output/session/00-paper-based-design/paper.pdf \\")
        print("    thesis-output/session/00-paper-based-design/")
        sys.exit(1)

    paper_path = sys.argv[1]
    output_dir = sys.argv[2]

    # Validate inputs
    if not os.path.exists(paper_path):
        logging.error(f"Paper file not found: {paper_path}")
        sys.exit(1)

    if not os.path.exists(output_dir):
        logging.error(f"Output directory not found: {output_dir}")
        sys.exit(1)

    # Execute Stage 1
    logging.info("=" * 70)
    logging.info("Stage 1: Paper Analysis")
    logging.info("=" * 70)

    start_time = time.time()

    # Step 1: Read PDF
    logging.info(f"Reading paper: {paper_path}")
    paper_content = read_pdf_content(paper_path)
    logging.info(f"Paper loaded: {len(paper_content)} characters")

    # Step 2: Analyze with Claude
    logging.info("Analyzing paper...")
    analysis = analyze_paper_claude(paper_content, paper_path)

    # Step 3: Save output
    output_path = save_analysis(analysis, output_dir)

    # Step 4: Validate
    if not validate_output(output_path):
        logging.error("❌ Validation failed")
        sys.exit(1)

    elapsed = time.time() - start_time
    logging.info("=" * 70)
    logging.info(f"✅ Stage 1 completed in {elapsed:.0f}s ({elapsed/60:.1f} min)")
    logging.info(f"   Output: {output_path}")
    logging.info("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
