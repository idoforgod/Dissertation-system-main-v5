---
name: paper-analysis
description: 학술 논문 분석을 위한 공통 로직 및 도구. PDF 파싱, 섹션 인식, 인용 추출, 언어 감지 등의 유틸리티를 제공합니다.
---

# Paper Analysis Skill

**목적**: 학술 논문 분석을 위한 재사용 가능한 유틸리티 및 템플릿

이 Skill은 paper-analyzer agent 및 다른 논문 분석 작업에서 사용되는 공통 기능을 제공합니다.

---

## 주요 기능

### 1. PDF 파싱 (PDF Parsing)

**기능**: PDF 논문 파일을 구조화된 텍스트로 변환

**사용 도구**:
- Python: `PyPDF2`, `pdfplumber`, `PyMuPDF`
- 또는 Claude의 Read tool (PDF 직접 읽기)

**출력 형식**:
```json
{
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "abstract": "Abstract text...",
  "sections": {
    "Introduction": "Section text...",
    "Methods": "Section text...",
    "Results": "Section text...",
    "Discussion": "Section text..."
  },
  "references": ["Reference 1", "Reference 2", ...],
  "page_count": 25
}
```

---

### 2. 섹션 자동 인식 (Section Detection)

**기능**: 논문의 주요 섹션을 자동으로 식별

**인식 대상**:
- Abstract / 초록
- Introduction / 서론
- Literature Review / 문헌검토
- Theoretical Framework / 이론적 배경
- Hypotheses / 가설
- Methods / Methodology / 연구방법
- Results / 결과
- Discussion / 논의
- Conclusion / 결론
- Limitations / 한계점
- Future Research / 향후 연구
- References / 참고문헌

**알고리즘**:
```python
def detect_sections(text):
    """
    Heuristic-based section detection
    """
    sections = {}
    section_patterns = {
        "Abstract": r"^\s*Abstract\s*$",
        "Introduction": r"^\s*(?:I\.|1\.?)?\s*Introduction\s*$",
        "Methods": r"^\s*(?:II\.|2\.?)?\s*(?:Methods?|Methodology)\s*$",
        "Results": r"^\s*(?:III\.|3\.?)?\s*Results\s*$",
        "Discussion": r"^\s*(?:IV\.|4\.?)?\s*Discussion\s*$",
        "Conclusion": r"^\s*(?:V\.|5\.?)?\s*Conclusion\s*$",
        "References": r"^\s*References\s*$"
    }

    # Pattern matching logic...
    return sections
```

---

### 3. 인용 추출 (Citation Extraction)

**기능**: 논문에서 인용 문헌을 추출

**지원 형식**:
- APA (7th Edition)
- MLA
- Chicago
- IEEE

**예시**:
```python
def extract_citations(text):
    """
    Extract citations from References section
    """
    # Regex for APA format
    apa_pattern = r'([A-Z][A-Za-z\'\-]+(?:,?\s+[A-Z]\.)*(?:,?\s+&\s+[A-Z][A-Za-z\'\-]+)?)\s+\((\d{4})\)\.\s+(.+?)\.(?:\s+([A-Za-z\s]+),\s+\*?(\d+)\*?\((\d+)\),\s+(\d+)(?:[\-–]\d+)?\.)?'

    citations = re.findall(apa_pattern, text)
    return citations
```

---

### 4. 언어 감지 및 번역 (Language Detection & Translation)

**기능**: 논문 언어를 감지하고 필요 시 번역

**지원 언어**:
- English ↔ Korean
- 기타 주요 언어 (자동 감지)

**사용 방법**:
```python
def detect_language(text):
    """
    Detect document language
    """
    # Use langdetect library or heuristics
    if has_korean_characters(text):
        return "ko"
    else:
        return "en"

def translate_if_needed(text, target_lang="en"):
    """
    Translate if not in target language
    """
    source_lang = detect_language(text)
    if source_lang != target_lang:
        # Use translation API or Claude
        translated = translate(text, source_lang, target_lang)
        return translated
    return text
```

---

### 5. 메타데이터 추출 (Metadata Extraction)

**기능**: 논문의 메타데이터를 추출

**추출 항목**:
```yaml
metadata:
  title: "Paper Title"
  authors: ["Author 1", "Author 2"]
  publication_year: 2023
  journal: "Journal Name"
  volume: 49
  issue: 2
  pages: "123-145"
  doi: "10.xxxx/xxxxx"
  keywords: ["keyword1", "keyword2"]
  abstract_word_count: 250
  total_word_count: 8500
  reference_count: 52
  table_count: 3
  figure_count: 5
```

---

## 템플릿 (Templates)

### Analysis Template

**파일**: `templates/analysis-template.yaml`

```yaml
paper_analysis_template:
  research_context:
    research_question: ""
    theoretical_framework: ""
    research_paradigm: ""

  methodology_evaluation:
    research_design: ""
    sample_characteristics: ""
    data_collection: ""
    analysis_techniques: ""
    validity_assessment: ""

  findings_synthesis:
    main_findings: []
    effect_sizes: []
    statistical_significance: ""
    practical_significance: ""

  critical_evaluation:
    theoretical_contribution: ""
    methodological_strengths: []
    methodological_weaknesses: []
    author_acknowledged_limitations: []
    unacknowledged_limitations: []
```

---

## 사용 예시 (Usage Examples)

### Example 1: 기본 논문 분석

```python
from skills.paper_analysis import parse_pdf, detect_sections

# 1. PDF 파싱
paper_data = parse_pdf("uploaded-paper.pdf")

# 2. 섹션 감지
sections = detect_sections(paper_data["text"])

# 3. 분석 템플릿 적용
analysis = apply_analysis_template(sections)

# 4. 출력
write_analysis("paper-deep-analysis.md", analysis)
```

### Example 2: 한국어 논문 처리

```python
# 1. 언어 감지
lang = detect_language(paper_text)

# 2. 영어로 번역 (분석용)
if lang == "ko":
    paper_text_en = translate_if_needed(paper_text, target_lang="en")
else:
    paper_text_en = paper_text

# 3. 분석 수행
analysis = analyze_paper(paper_text_en)

# 4. 한국어로 번역 (보고서)
analysis_ko = translate_if_needed(analysis, target_lang="ko")
```

---

## 스크립트 (Scripts)

### parse_pdf.py

**파일**: `scripts/parse_pdf.py`

```python
#!/usr/bin/env python3
"""
PDF 파싱 유틸리티
"""
import sys
import json
import re

def parse_pdf(pdf_path):
    """
    Parse PDF and extract structured data

    Args:
        pdf_path: Path to PDF file

    Returns:
        dict: Structured paper data
    """
    try:
        import PyPDF2

        with open(pdf_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)

            # Extract text
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            # Extract metadata
            metadata = {
                "page_count": len(reader.pages),
                "title": reader.metadata.get('/Title', ''),
                "author": reader.metadata.get('/Author', '')
            }

            return {
                "text": text,
                "metadata": metadata,
                "page_count": len(reader.pages)
            }

    except ImportError:
        # Fallback: Use Claude Read tool
        print("PyPDF2 not available. Use Claude Read tool instead.")
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_pdf.py <pdf_path>")
        sys.exit(1)

    result = parse_pdf(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 의존성 (Dependencies)

### Python Packages (Optional)

```txt
PyPDF2>=3.0.0
pdfplumber>=0.9.0
PyMuPDF>=1.23.0
langdetect>=1.0.9
```

**설치**:
```bash
pip install PyPDF2 pdfplumber pymupdf langdetect
```

**Note**: 이러한 패키지는 선택 사항입니다. Claude의 Read tool을 사용하면 추가 의존성 없이 PDF를 읽을 수 있습니다.

---

## 사용하는 Agents

이 Skill을 사용하는 agents:
- `paper-analyzer` (Stage 1)
- `literature-searcher` (Phase 1, Wave 1)
- `paper-research-designer` (Phase 0, Mode E - legacy)

---

## 버전 히스토리

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-28 | Initial release |

---

**작성자**: Claude Code
**상태**: ✅ Ready for use
