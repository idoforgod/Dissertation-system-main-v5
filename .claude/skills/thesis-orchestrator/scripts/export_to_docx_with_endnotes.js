const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak } = require('docx');

// 명령행 인자 파싱
const sessionDir = process.argv[2];
const language = process.argv[3] || 'en'; // 'en' or 'ko'

if (!sessionDir) {
  console.error('❌ Usage: node export_to_docx_with_endnotes.js <session-directory> [language]');
  console.error('   Example: node export_to_docx_with_endnotes.js thesis-output/xxx-2026-01-21 en');
  process.exit(1);
}

const sessionPath = path.join(sessionDir, '00-session', 'session.json');
if (!fs.existsSync(sessionPath)) {
  console.error(`❌ session.json not found: ${sessionPath}`);
  process.exit(1);
}

const session = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
const thesisDir = path.join(sessionDir, '03-thesis');

// 마크다운 파일 선택
const allFiles = fs.readdirSync(thesisDir)
  .filter(f => f.startsWith('chapter') && f.endsWith('.md'))
  .sort();

const targetFiles = language === 'ko'
  ? allFiles.filter(f => f.includes('-ko.md')).map(f => path.join(thesisDir, f))
  : allFiles.filter(f => !f.includes('-ko.md')).map(f => path.join(thesisDir, f));

if (targetFiles.length === 0) {
  console.error(`❌ No chapter files found for language: ${language}`);
  process.exit(1);
}

console.log(`📚 Processing ${targetFiles.length} chapters (${language})...`);

// YAML 블록 추출 및 처리
const claimsRegistry = [];
let claimCounter = 1;

function extractYAMLBlocks(content, chapterNum) {
  const lines = content.split('\n');
  const processedLines = [];
  let inYaml = false;
  let yamlBlock = [];
  let yamlStartLine = -1;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // YAML 블록 시작 감지
    if (line.trim() === '```yaml' && !inYaml) {
      inYaml = true;
      yamlBlock = [];
      yamlStartLine = i;
      continue;
    }

    // YAML 블록 종료 감지
    if (line.trim() === '```' && inYaml) {
      inYaml = false;

      // YAML 파싱
      const yamlText = yamlBlock.join('\n');
      const claimMatch = yamlText.match(/id:\s*"([^"]+)"/);
      const textMatch = yamlText.match(/text:\s*"([^"]+)"/);
      const typeMatch = yamlText.match(/claim_type:\s*(\w+)/);
      const confidenceMatch = yamlText.match(/confidence:\s*(\d+)/);
      const pTCSMatch = yamlText.match(/pTCS:\s*(\d+)/);

      if (claimMatch) {
        const claimId = claimMatch[1];

        // Claims registry에 추가
        claimsRegistry.push({
          number: claimCounter,
          id: claimId,
          text: textMatch ? textMatch[1] : 'N/A',
          type: typeMatch ? typeMatch[1] : 'N/A',
          confidence: confidenceMatch ? confidenceMatch[1] : 'N/A',
          pTCS: pTCSMatch ? pTCSMatch[1] : 'N/A',
          chapter: chapterNum,
          yamlFull: yamlText
        });

        // 본문에 미주 참조 삽입
        processedLines.push(`[^${claimCounter}]`);
        processedLines.push(''); // 빈 줄 추가

        claimCounter++;
      }

      yamlBlock = [];
      continue;
    }

    // YAML 블록 내부
    if (inYaml) {
      yamlBlock.push(line);
      continue;
    }

    // 일반 라인
    processedLines.push(line);
  }

  return processedLines.join('\n');
}

// 마크다운 파싱 (기존 함수 재사용)
function parseMarkdown(text) {
  const lines = text.split('\n');
  const paragraphs = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    if (line.trim() === '' || line.trim() === '---') continue;

    // 미주 참조 감지
    if (line.match(/^\[\^\d+\]$/)) {
      const noteNum = line.match(/\[(\^\d+)\]/)[1];
      paragraphs.push(new Paragraph({
        children: [new TextRun({ text: noteNum, superScript: true })],
        spacing: { after: 0 }
      }));
      continue;
    }

    // 헤딩 파싱
    if (line.startsWith('#### ')) {
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_4,
        children: [new TextRun(line.substring(5))]
      }));
    } else if (line.startsWith('### ')) {
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_3,
        children: [new TextRun(line.substring(4))]
      }));
    } else if (line.startsWith('## ')) {
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_2,
        children: [new TextRun(line.substring(3))]
      }));
    } else if (line.startsWith('# ')) {
      paragraphs.push(new Paragraph({
        heading: HeadingLevel.HEADING_1,
        children: [new TextRun(line.substring(2))]
      }));
    } else if (line.startsWith('**') && line.endsWith('**')) {
      const text = line.replace(/\*\*/g, '');
      paragraphs.push(new Paragraph({
        children: [new TextRun({ text: text, bold: true })],
        spacing: { before: 120, after: 120 }
      }));
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      paragraphs.push(new Paragraph({
        children: [new TextRun(line.substring(2))],
        indent: { left: 720 }
      }));
    } else if (line.startsWith('| ')) {
      paragraphs.push(new Paragraph({
        children: [new TextRun(line)],
        spacing: { before: 60, after: 60 }
      }));
    } else if (line.match(/^\d+\. /)) {
      paragraphs.push(new Paragraph({
        children: [new TextRun(line)],
        indent: { left: 720 }
      }));
    } else {
      const textRuns = parseInlineFormatting(line);
      if (textRuns.length > 0) {
        paragraphs.push(new Paragraph({
          children: textRuns,
          spacing: { after: 120 }
        }));
      }
    }
  }

  return paragraphs;
}

function parseInlineFormatting(line) {
  const runs = [];
  let current = '';
  let i = 0;

  while (i < line.length) {
    if (line[i] === '*' && line[i+1] === '*') {
      if (current) {
        runs.push(new TextRun(current));
        current = '';
      }
      i += 2;
      let boldText = '';
      while (i < line.length && !(line[i] === '*' && line[i+1] === '*')) {
        boldText += line[i];
        i++;
      }
      if (boldText) runs.push(new TextRun({ text: boldText, bold: true }));
      i += 2;
    } else if (line[i] === '*') {
      if (current) {
        runs.push(new TextRun(current));
        current = '';
      }
      i++;
      let italicText = '';
      while (i < line.length && line[i] !== '*') {
        italicText += line[i];
        i++;
      }
      if (italicText) runs.push(new TextRun({ text: italicText, italics: true }));
      i++;
    } else {
      current += line[i];
      i++;
    }
  }

  if (current) runs.push(new TextRun(current));
  return runs;
}

// 미주 섹션 생성
function createEndnotesSection() {
  const paragraphs = [];

  // 페이지 나누기
  paragraphs.push(new Paragraph({ children: [new PageBreak()] }));

  // 미주 제목
  paragraphs.push(new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun('Endnotes: Claims Registry')],
    spacing: { before: 240, after: 240 }
  }));

  paragraphs.push(new Paragraph({
    children: [new TextRun('This section contains the complete GroundedClaim metadata for all claims referenced in the dissertation. Each claim includes its ID, type, confidence score, pTCS (predicted Thesis Confidence Score), sources, and uncertainty acknowledgment.')],
    spacing: { after: 240 }
  }));

  // 각 claim 추가
  claimsRegistry.forEach(claim => {
    // Claim 번호 및 ID
    paragraphs.push(new Paragraph({
      children: [
        new TextRun({ text: `[${claim.number}] `, superScript: true, bold: true }),
        new TextRun({ text: `Claim ${claim.id}`, bold: true })
      ],
      spacing: { before: 200, after: 80 }
    }));

    // Claim 텍스트
    paragraphs.push(new Paragraph({
      children: [
        new TextRun({ text: 'Text: ', bold: true }),
        new TextRun(claim.text)
      ],
      spacing: { after: 60 },
      indent: { left: 360 }
    }));

    // Type
    paragraphs.push(new Paragraph({
      children: [
        new TextRun({ text: 'Type: ', bold: true }),
        new TextRun(claim.type)
      ],
      spacing: { after: 60 },
      indent: { left: 360 }
    }));

    // Confidence & pTCS
    paragraphs.push(new Paragraph({
      children: [
        new TextRun({ text: 'Confidence: ', bold: true }),
        new TextRun(`${claim.confidence}  |  `),
        new TextRun({ text: 'pTCS: ', bold: true }),
        new TextRun(claim.pTCS)
      ],
      spacing: { after: 60 },
      indent: { left: 360 }
    }));

    // Full YAML (축약)
    const yamlLines = claim.yamlFull.split('\n').slice(0, 15); // 처음 15줄만
    yamlLines.forEach(line => {
      paragraphs.push(new Paragraph({
        children: [new TextRun(line)],
        spacing: { after: 20 },
        indent: { left: 720 }
      }));
    });

    if (claim.yamlFull.split('\n').length > 15) {
      paragraphs.push(new Paragraph({
        children: [new TextRun({ text: '... (see full metadata in source files)', italics: true })],
        spacing: { after: 120 },
        indent: { left: 720 }
      }));
    }
  });

  // Summary statistics
  paragraphs.push(new Paragraph({ children: [new PageBreak()] }));
  paragraphs.push(new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun('Claims Registry Summary')],
    spacing: { before: 240, after: 120 }
  }));

  const totalClaims = claimsRegistry.length;
  const avgConfidence = Math.round(claimsRegistry.reduce((sum, c) => sum + parseInt(c.confidence), 0) / totalClaims);
  const avgPTCS = Math.round(claimsRegistry.reduce((sum, c) => sum + parseInt(c.pTCS), 0) / totalClaims);

  paragraphs.push(new Paragraph({
    children: [new TextRun({ text: `Total Claims: ${totalClaims}`, bold: true })],
    spacing: { after: 80 }
  }));
  paragraphs.push(new Paragraph({
    children: [new TextRun({ text: `Average Confidence: ${avgConfidence}`, bold: true })],
    spacing: { after: 80 }
  }));
  paragraphs.push(new Paragraph({
    children: [new TextRun({ text: `Average pTCS: ${avgPTCS}`, bold: true })],
    spacing: { after: 80 }
  }));

  return paragraphs;
}

// Word 문서 생성
async function createWordDocument() {
  const allParagraphs = [];
  const researchTopic = session.research?.topic || 'Doctoral Dissertation';
  const currentDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long'
  });

  // 제목 페이지
  allParagraphs.push(
    new Paragraph({
      heading: HeadingLevel.TITLE,
      children: [new TextRun(researchTopic)],
      alignment: AlignmentType.CENTER,
      spacing: { before: 400, after: 200 }
    }),
    new Paragraph({
      children: [new TextRun('Doctoral Dissertation')],
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 }
    }),
    new Paragraph({
      children: [new TextRun(currentDate)],
      alignment: AlignmentType.CENTER
    }),
    new Paragraph({ children: [new PageBreak()] })
  );

  // 각 장 처리 (YAML 블록 추출)
  targetFiles.forEach((file, idx) => {
    console.log(`  ${idx + 1}. ${path.basename(file)}`);
    const content = fs.readFileSync(file, 'utf-8');
    const processedContent = extractYAMLBlocks(content, idx + 1);
    const paragraphs = parseMarkdown(processedContent);
    allParagraphs.push(...paragraphs);

    if (idx < targetFiles.length - 1) {
      allParagraphs.push(new Paragraph({ children: [new PageBreak()] }));
    }
  });

  // 미주 섹션 추가
  console.log(`\n📌 Adding endnotes section (${claimsRegistry.length} claims)...`);
  const endnotes = createEndnotesSection();
  allParagraphs.push(...endnotes);

  // Document 생성
  const doc = new Document({
    styles: {
      default: {
        document: {
          run: { font: 'Times New Roman', size: 22 }
        }
      },
      paragraphStyles: [
        {
          id: 'Title',
          name: 'Title',
          basedOn: 'Normal',
          run: { size: 44, bold: true, font: 'Times New Roman' },
          paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER }
        },
        {
          id: 'Heading1',
          name: 'Heading 1',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 32, bold: true, font: 'Times New Roman' },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
        },
        {
          id: 'Heading2',
          name: 'Heading 2',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 28, bold: true, font: 'Times New Roman' },
          paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 }
        },
        {
          id: 'Heading3',
          name: 'Heading 3',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 26, bold: true, font: 'Times New Roman' },
          paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 2 }
        },
        {
          id: 'Heading4',
          name: 'Heading 4',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 24, bold: true, font: 'Times New Roman' },
          paragraph: { spacing: { before: 120, after: 60 }, outlineLevel: 3 }
        }
      ]
    },
    sections: [{
      properties: {
        page: {
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children: allParagraphs
    }]
  });

  const suffix = language === 'ko' ? 'ko-endnotes' : 'en-endnotes';
  const outputPath = path.join(thesisDir, `dissertation-full-${suffix}.docx`);
  const buffer = await Packer.toBuffer(doc);
  fs.writeFileSync(outputPath, buffer);

  console.log(`\n✅ Word document created: ${outputPath}`);
  console.log(`📊 Total claims processed: ${claimsRegistry.length}`);

  return outputPath;
}

// Main execution
createWordDocument().catch(console.error);
