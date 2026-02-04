const fs = require('fs');
const path = require('path');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, PageBreak } = require('docx');

// 명령행 인자에서 세션 디렉토리 가져오기
const sessionDir = process.argv[2];
if (!sessionDir) {
  console.error('❌ 사용법: node export_to_docx.js <session-directory>');
  console.error('   예시: node export_to_docx.js thesis-output/aiof-free-will-possibilityin-study-2026-01-20');
  process.exit(1);
}

// session.json 읽기
const sessionPath = path.join(sessionDir, '00-session', 'session.json');
if (!fs.existsSync(sessionPath)) {
  console.error(`❌ session.json을 찾을 수 없습니다: ${sessionPath}`);
  process.exit(1);
}

const session = JSON.parse(fs.readFileSync(sessionPath, 'utf-8'));
const thesisDir = path.join(sessionDir, '03-thesis');

// 마크다운 파일 경로 동적 생성 (English & Korean 분리)
const allFiles = fs.readdirSync(thesisDir)
  .filter(f => (f.startsWith('chapter') || f.startsWith('ch')) && f.endsWith('.md'))
  .sort();

// English files (exclude -ko.md)
const englishFiles = allFiles
  .filter(f => !f.includes('-ko.md'))
  .map(f => path.join(thesisDir, f));

// Korean files (-ko.md only)
const koreanFiles = allFiles
  .filter(f => f.includes('-ko.md'))
  .map(f => path.join(thesisDir, f));

if (englishFiles.length === 0 && koreanFiles.length === 0) {
  console.error(`❌ ${thesisDir}에서 chapter*.md 파일을 찾을 수 없습니다.`);
  process.exit(1);
}

console.log(`📚 English chapters: ${englishFiles.length}개`);
console.log(`📚 Korean chapters: ${koreanFiles.length}개`);

function parseMarkdown(text) {
  const lines = text.split('\n');
  const paragraphs = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // 빈 줄 건너뛰기
    if (line.trim() === '' || line.trim() === '---') continue;

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
      // 강조된 제목
      const text = line.replace(/\*\*/g, '');
      paragraphs.push(new Paragraph({
        children: [new TextRun({ text: text, bold: true })],
        spacing: { before: 120, after: 120 }
      }));
    } else if (line.startsWith('- ') || line.startsWith('* ')) {
      // 리스트 항목
      paragraphs.push(new Paragraph({
        children: [new TextRun(line.substring(2))],
        indent: { left: 720 }
      }));
    } else if (line.startsWith('| ')) {
      // 테이블은 일반 텍스트로 처리
      paragraphs.push(new Paragraph({
        children: [new TextRun(line)],
        spacing: { before: 60, after: 60 }
      }));
    } else if (line.match(/^\d+\. /)) {
      // 번호 매긴 리스트
      paragraphs.push(new Paragraph({
        children: [new TextRun(line)],
        indent: { left: 720 }
      }));
    } else {
      // 일반 텍스트 파싱 (bold, italic)
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
    // **bold**
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
    }
    // *italic*
    else if (line[i] === '*') {
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

// Word 문서 생성 함수
function createWordDocument(files, language, font) {
  const allParagraphs = [];
  const researchTopic = session.research?.topic || 'Doctoral Dissertation';
  const currentDate = new Date().toLocaleDateString(language === 'ko' ? 'ko-KR' : 'en-US', {
    year: 'numeric',
    month: 'long'
  });
  const subtitle = language === 'ko' ? '박사학위논문' : 'Doctoral Dissertation';

  // 제목 페이지
  allParagraphs.push(
    new Paragraph({
      heading: HeadingLevel.TITLE,
      children: [new TextRun(researchTopic)],
      alignment: AlignmentType.CENTER,
      spacing: { before: 400, after: 200 }
    }),
    new Paragraph({
      children: [new TextRun(subtitle)],
      alignment: AlignmentType.CENTER,
      spacing: { after: 200 }
    }),
    new Paragraph({
      children: [new TextRun(currentDate)],
      alignment: AlignmentType.CENTER
    }),
    new Paragraph({ children: [new PageBreak()] })
  );

  // 각 장 처리
  files.forEach((file, idx) => {
    console.log(`  ${idx + 1}. ${path.basename(file)}`);
    const content = fs.readFileSync(file, 'utf-8');
    const paragraphs = parseMarkdown(content);
    allParagraphs.push(...paragraphs);

    if (idx < files.length - 1) {
      allParagraphs.push(new Paragraph({ children: [new PageBreak()] }));
    }
  });

  // Document 생성
  return new Document({
    styles: {
      default: {
        document: {
          run: { font, size: 22 }
        }
      },
      paragraphStyles: [
        {
          id: 'Title',
          name: 'Title',
          basedOn: 'Normal',
          run: { size: 44, bold: true, font },
          paragraph: { spacing: { before: 240, after: 120 }, alignment: AlignmentType.CENTER }
        },
        {
          id: 'Heading1',
          name: 'Heading 1',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 32, bold: true, font },
          paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 }
        },
        {
          id: 'Heading2',
          name: 'Heading 2',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 28, bold: true, font },
          paragraph: { spacing: { before: 180, after: 100 }, outlineLevel: 1 }
        },
        {
          id: 'Heading3',
          name: 'Heading 3',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 26, bold: true, font },
          paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 2 }
        },
        {
          id: 'Heading4',
          name: 'Heading 4',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 24, bold: true, font },
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
}

// Main execution
async function main() {
  const topicSlug = session.research?.topic_slug || 'thesis';

  // English Word document
  if (englishFiles.length > 0) {
    console.log(`\n📝 Creating English Word document...`);
    const enDoc = createWordDocument(englishFiles, 'en', 'Times New Roman');
    const enPath = path.join(thesisDir, `dissertation-full-en.docx`);
    const enBuffer = await Packer.toBuffer(enDoc);
    fs.writeFileSync(enPath, enBuffer);
    console.log(`✅ English version: ${enPath}`);
  }

  // Korean Word document
  if (koreanFiles.length > 0) {
    console.log(`\n📝 Creating Korean Word document...`);
    const koDoc = createWordDocument(koreanFiles, 'ko', 'Malgun Gothic');
    const koPath = path.join(thesisDir, `dissertation-full-ko.docx`);
    const koBuffer = await Packer.toBuffer(koDoc);
    fs.writeFileSync(koPath, koBuffer);
    console.log(`✅ Korean version: ${koPath}`);
  }

  // Update session.json
  if (!session.outputs) session.outputs = {};
  session.outputs.word_documents = {
    english: englishFiles.length > 0 ? path.join(thesisDir, 'dissertation-full-en.docx') : null,
    korean: koreanFiles.length > 0 ? path.join(thesisDir, 'dissertation-full-ko.docx') : null,
    created_at: new Date().toISOString(),
    chapters: {
      english: englishFiles.length,
      korean: koreanFiles.length
    }
  };
  fs.writeFileSync(sessionPath, JSON.stringify(session, null, 2));

  console.log(`\n✅ Word documents created!`);
  console.log(`📝 session.json updated`);
}

main().catch(console.error);
