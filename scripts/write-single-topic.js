const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = 'E:\\develop\\courses';

function parseArgs() {
  const arg1 = process.argv[2];
  const arg2 = process.argv[3];
  const arg3 = process.argv[4];
  const arg4 = process.argv[5];

  let book = 'math';
  let kind = 'book';
  let section = '';
  let slug = '';

  if (arg1) {
    if (arg1.startsWith('{')) {
      try {
        const parsed = JSON.parse(arg1);
        book = parsed.book || book;
        kind = parsed.kind || kind;
        section = parsed.section || '';
        slug = parsed.slug || '';
      } catch (e) {}
    } else {
      book = arg1;
      if (arg2) kind = arg2;
      if (arg3) section = arg3;
      if (arg4) slug = arg4;
    }
  }

  return { book, kind, section, slug };
}

const config = parseArgs();
const BOOK = config.book;
const KIND = config.kind;
const TARGET_SECTION = config.section;
const TARGET_SLUG = config.slug;

console.log(`================================================================`);
console.log(`🚀 SINGLE-TOPIC ITERATIVE AUDITOR & AUTHOR: ${KIND}/${BOOK}`);
console.log(`Rules: Feynman Method | Deep Substantive Explanation (Target Median: 2100–2600 words) | Zero Childish Fluff/Analogies | Pure Math Prose`);
console.log(`================================================================`);

// 1. Load Manifest
const manifestPath = path.join(ROOT, KIND, BOOK, 'manifest.js');
delete require.cache[require.resolve(manifestPath)];
global.window = { __BOOKS__: [], __GUIDES__: [] };
require(manifestPath);

let bookMeta = (global.window.__BOOKS__ || []).find(b => b.slug === BOOK);
if (!bookMeta) {
  bookMeta = (global.window.__GUIDES__ || []).find(g => g.slug === BOOK);
}

if (!bookMeta) {
  console.error(`Error: Could not find meta for ${KIND}/${BOOK} in manifest.`);
  process.exit(1);
}

// Build index of all existing topics in manifest across the entire repository
const allExistingTopics = new Set();
(global.window.__BOOKS__ || []).forEach(b => {
  if (b.sections) {
    b.sections.forEach(sec => {
      sec.topics.forEach(top => {
        allExistingTopics.add(`${b.slug}/${top.slug}`);
      });
    });
  }
});

let targetUnit = null;
if (TARGET_SECTION && TARGET_SLUG) {
  targetUnit = { section: TARGET_SECTION, slug: TARGET_SLUG };
} else if (bookMeta.sections) {
  for (const sec of bookMeta.sections) {
    for (const top of sec.topics) {
      const dStatus = top.detailed ? top.detailed.status : (top.status || 'pending');
      const bStatus = top.basic ? top.basic.status : 'empty';
      if (dStatus === 'pending' || dStatus === 'update' || dStatus === 'deeper' || dStatus === 'recheck') {
        targetUnit = { section: sec.slug, slug: top.slug, title: top.title, level: 'detailed' };
        break;
      } else if (bStatus === 'pending' || bStatus === 'update') {
        targetUnit = { section: sec.slug, slug: top.slug, title: top.title, level: 'basic' };
        break;
      }
    }
    if (targetUnit) break;
  }
}

if (!targetUnit) {
  console.log(`\n🎉 No pending topic found in ${KIND}/${BOOK}. All topics are done!`);
  process.exit(0);
}

console.log(`\n🎯 TARGET TOPIC FOR THIS RUN:`);
console.log(`   Section: ${targetUnit.section}`);
console.log(`   Slug:    ${targetUnit.slug}`);

const topicDir = path.join(ROOT, KIND, BOOK, targetUnit.section, targetUnit.slug);
if (!fs.existsSync(topicDir)) {
  fs.mkdirSync(topicDir, { recursive: true });
}

// 2. Inserts & Links Discovery Logic (§3 & §6 AUTHORING.md)
console.log(`\n================================================================`);
console.log(`[Discovery Engine] Evaluating Required Inserts & Cross-Links`);
console.log(`================================================================`);

const detailedFile = path.join(topicDir, `${targetUnit.slug}-d.md`);
const detailedExists = fs.existsSync(detailedFile);

if (detailedExists) {
  const text = fs.readFileSync(detailedFile, 'utf8');

  // Scan for book: links in text
  const bookLinkRegex = /book:([a-zA-Z0-9_-]+)\/([a-zA-Z0-9_-]+)/g;
  let match;
  const missingLinkTargets = [];

  while ((match = bookLinkRegex.exec(text)) !== null) {
    const targetBook = match[1];
    const targetSlug = match[2];
    const key = `${targetBook}/${targetSlug}`;

    if (!allExistingTopics.has(key)) {
      missingLinkTargets.push({ book: targetBook, slug: targetSlug });
    }
  }

  if (missingLinkTargets.length > 0) {
    console.log(`⚠️ Discovered ${missingLinkTargets.length} missing cross-link target(s) in prose:`);
    missingLinkTargets.forEach(t => {
      console.log(`   + Registering new topic [${t.slug}] as 'empty' in ${t.book}/manifest.js`);

      // Auto-register stub in manifest
      const targetManifestPath = path.join(ROOT, 'book', t.book, 'manifest.js');
      if (fs.existsSync(targetManifestPath)) {
        delete require.cache[require.resolve(targetManifestPath)];
        global.window = { __BOOKS__: [] };
        require(targetManifestPath);
        const tBookMeta = global.window.__BOOKS__.find(b => b.slug === t.book);
        if (tBookMeta && tBookMeta.sections && tBookMeta.sections.length > 0) {
          const firstSec = tBookMeta.sections[0];
          const existsInSec = firstSec.topics.some(tp => tp.slug === t.slug);
          if (!existsInSec) {
            firstSec.topics.push({
              slug: t.slug,
              title: t.slug.replace(/-/g, ' '),
              status: 'empty',
              levels: ['detailed'],
              detailed: { status: 'empty' }
            });
            const newMJs = 'window.__BOOKS__ = window.__BOOKS__ || [];\nwindow.__BOOKS__.push(\n' + JSON.stringify(tBookMeta, null, 2) + '\n);\n';
            fs.writeFileSync(targetManifestPath, newMJs, 'utf8');
            console.log(`     ✓ Registered ${t.slug} in ${t.book}/manifest.js as 'empty'.`);
          }
        }
      }
    });
  } else {
    console.log(`✓ All cross-links in prose point to valid existing topics.`);
  }
}

// 3. Strict Cognitive Auditor (Feynman + Depth Target 2100–2600 + Low Cognitive Load + Zero Fictional Fluff)
console.log(`\n================================================================`);
console.log(`[Cognitive & Feynman Auditor] Iterative Verification for ${targetUnit.slug}`);
console.log(`================================================================`);

let passesAll = true;
const auditIssues = [];

if (detailedExists) {
  const text = fs.readFileSync(detailedFile, 'utf8');
  const words = text.trim().split(/\s+/).length;
  console.log(`✓ Detailed article present (${words} words).`);

  // SUBSTANTIVE DEPTH CHECK: Median target for detailed articles is 2100–2600 words (§3 AUTHORING.md).
  // 1000 is lower bound floor, not the goal! We enforce at least 1800 words for true deep coverage.
  if (words < 1800) {
    auditIssues.push(`Substantive Depth Violation: Detailed article is hovering near floor (${words} words). Target median in AUTHORING.md §3 is 2100–2600 words. Expand deep mathematical proofs, axioms, edge cases, and mechanics.`);
  }

  // Check for repeated dummy word loops or garbage padding (e.g. "Текст Текст Текст...")
  const wordsArray = text.trim().split(/\s+/);
  let consecutiveRepeatCount = 0;
  for (let i = 1; i < wordsArray.length; i++) {
    if (wordsArray[i].toLowerCase() === wordsArray[i - 1].toLowerCase() && wordsArray[i].length > 1) {
      consecutiveRepeatCount++;
    }
  }
  if (consecutiveRepeatCount > 10 || /Текст Текст|Lorem ipsum|placeholder|sample text|Історія Історія|Доведення Доведення/i.test(text)) {
    auditIssues.push(`Garbage Text Violation: Detected repetitive dummy text padding ("Текст Текст...", repeated words loop). Write authentic, deep Feynman prose!`);
  }

  if (!text.includes('<preknowlist>')) {
    auditIssues.push(`Missing <preknowlist> in main article.`);
  }

  // Check intro narrative
  const cleanText = text.replace(/<preknowlist>[\s\S]*?<\/preknowlist>/g, '');
  const proseParagraphs = cleanText.split(/\r?\n\s*\r?\n/).map(p => p.trim()).filter(p => p && !p.startsWith('#'));
  const firstPara = proseParagraphs[0] || '';

  if (firstPara.length < 40) {
    auditIssues.push(`Intro sentence missing or too short.`);
  }

  // Check: NO Childish Fictional Fluff Tropes
  const forbiddenTropes = [/перукар/i, /детектив/i, /фотокамер/i, /монет/i, /уяви себе/i, /гра у/i, /містечк/i, /підкидан/i];
  const foundTropes = forbiddenTropes.filter(re => re.test(text));
  if (foundTropes.length > 0) {
    auditIssues.push(`Cognitive Fluff Violation: Contains forbidden childish fictional story tropes (${foundTropes.map(r => r.source).join(', ')}). Explain directly on the math concept itself!`);
  }

  // Check: Cognitive Ease (Conceptual clarity, cause-and-effect flow, zero friction in mental model)
  const causeEffectIndicators = [/отже/i, /тому/i, /це означає/i, /звідси випливає/i, /як наслідок/i, /це приводить до/i, /завдяки цьому/i];
  const hasCauseEffect = causeEffectIndicators.some(re => re.test(text));
  if (!hasCauseEffect && proseParagraphs.length > 6) {
    auditIssues.push(`Causal Chain Continuity Violation: Missing clear logical cause-and-effect transitions (отже, тому, це означає, звідси випливає). Every section must build an unbroken logical bridge without leaps.`);
  }

  // Check: NO Dry Textbook Opening Tropes
  const dryTextbookPatterns = [
    /нехай\s+[A-Za-z0-9_ℙℤℚℝℂ\s,]+—\s*/i,
    /розглянемо\s+множину/i,
    /теорема\s+стверджує,\s*що/i,
    /визначається\s+як\s+потрійка/i,
    /є\s+комутативним\s+кільцем/i,
    /утворює\s+частково\s+впорядковану\s+множину/i,
    /є\s+векторним\s+простором/i,
    /у\s+математичній\s+теорії\s+визначають/i,
    /формула\s+має\s+наступний\s+вигляд/i
  ];
  const firstThreeParaText = proseParagraphs.slice(0, 3).join(' ');
  const dryMatch = dryTextbookPatterns.find(re => re.test(firstThreeParaText));
  if (dryMatch) {
    auditIssues.push(`Textbook Opening Violation: Intro contains dry formal definition ("${dryMatch.exec(firstThreeParaText)[0]}"). Section 1 MUST build intuition from first principles and state the core problem before introducing formal mathematical definitions!`);
  }

  // Check: Problem Motivation in First 3 Paragraphs
  const intuitionPatterns = [/чому/i, /проблема/i, /обмеження/i, /навіщо/i, /якщо\s+спробувати/i, /виникає\s+питання/i, /першопричин/i, /намагалися\s+розв'язати/i, /зіткнулися\s+з/i];
  const hasMotivation = intuitionPatterns.some(re => re.test(firstThreeParaText));
  if (!hasMotivation && !KIND.includes('hist')) {
    auditIssues.push(`Missing Problem Motivation: First 3 paragraphs must explain WHY this problem exists, what constraint forced this solution, or what intuition underlies it (found zero motivation markers: чому, проблема, обмеження, навіщо, першопричин).`);
  }

  // Check: Passive Academic Tone
  const passiveAcademicPatterns = [
    /дано\s+векторний/i,
    /характерною\s+рисою\s+є\s+те,\s*що/i,
    /розглянемо\s+формальне\s+визначення/i,
    /слід\s+зазначити,\s*що\s+існує/i
  ];
  const passiveMatch = passiveAcademicPatterns.find(re => re.test(text));
  if (passiveMatch) {
    auditIssues.push(`Passive Academic Tone Violation: Found passive textbook phrasing ("${passiveMatch.exec(text)[0]}"). Rewrite as an active step-by-step investigation with the reader!`);
  }

  // Check: NO LaTeX Notation (§5 AUTHORING.md)
  // The reader engine (book.js) has ZERO KaTeX/MathJax renderer. LaTeX renders as raw unparsed $...\$ / backslashes!
  const latexRegex = /\$|\\frac|\\mathbb|\\mathcal|\\text\{|\\log_|\\sqrt|\\cdot|\\le|\\ge|\\to|\\forall|\\exists|\\land|\\lor|\\neg|\\vdash|\\models/;
  if (latexRegex.test(text)) {
    auditIssues.push(`LaTeX Formula Violation in detailed article: NO LaTeX allowed ($...$, \\frac, \\mathbb, etc.). The browser engine has no KaTeX! Convert to Unicode symbols (· ≤ ≥ → ∀ ∃ ¬ ∧ ∨ ⊢), inline code, or aligned formula code blocks.`);
  }

  // Domain-based code block check:
  // Code in main text is allowed IF the book category/domain naturally demands it (programming, algorithms, reference/unix-linux).
  // Non-code domains (math, chemistry, physics, philosophy) keep main text focused on domain prose; code goes into proj-*/api-* inserts.
  const nonCodeBooks = ['math', 'chemistry', 'physics', 'philosophy'];
  if (KIND === 'book' && nonCodeBooks.includes(BOOK)) {
    if (text.includes('```c') || text.includes('```cpp') || text.includes('```python') || text.includes('```js')) {
      auditIssues.push(`Domain Violation: Main article in ${BOOK} book should contain domain-pure prose (${BOOK}). Code belongs in proj-*/api-* inserts or programming/algorithm books.`);
    }
  }

  // SVG Figure Audit (§5 AUTHORING.md)
  const figsPyPath = path.join(topicDir, 'figs.py');
  const imgDir = path.join(topicDir, 'img');
  const hasFigsPy = fs.existsSync(figsPyPath);
  const hasImgDir = fs.existsSync(imgDir) && fs.readdirSync(imgDir).some(f => f.endsWith('.svg'));
  
  // 1. Run figs.py if present
  if (hasFigsPy) {
    try {
      const { execSync } = require('child_process');
      execSync(`python figs.py`, { cwd: topicDir, stdio: 'pipe' });
    } catch (e) {
      auditIssues.push(`SVG Generation Failure: figs.py failed to execute cleanly in ${topicDir}. Error: ${e.message}`);
    }
  }

  // 2. Run svgcheck.py if img/ directory has SVG files
  if (hasImgDir) {
    try {
      const { execSync } = require('child_process');
      const rootDir = path.resolve(__dirname, '..');
      const relImgPath = path.relative(rootDir, imgDir).replace(/\\/g, '/');
      execSync(`python scripts/svgcheck.py ${relImgPath} --links`, { cwd: rootDir, stdio: 'pipe' });
    } catch (e) {
      auditIssues.push(`SVG Geometry Violation: svgcheck.py found overlapping text/lines or missing links in ${imgDir}. Output: ${e.stdout ? e.stdout.toString() : e.message}`);
    }
  }

  // 3. Check if visual concepts exist but no SVG is linked
  const visualKeywords = [/дерево/i, /куб/i, /автомат/i, /граф/i, /схема/i, /архітектур/i, /діаграм/i, /ієрархі/i];
  const hasVisualKeyword = visualKeywords.some(re => re.test(text));
  const hasSvgReference = text.includes('.svg');
  if (hasVisualKeyword && !hasSvgReference && !hasFigsPy) {
    auditIssues.push(`SVG Figure Missing: Topic contains visual/structural concepts (${visualKeywords.filter(r => r.test(text)).map(r => r.source).join(', ')}), but has no figs.py script or linked SVG diagram in prose. Create figs.py using scripts/svgkit.py!`);
  }

} else {
  auditIssues.push(`Detailed article file missing: ${detailedFile}`);
}

// Evaluate Inserts (Full 5 insert types: hist, comp, math, proj, api)
const filesInDir = fs.readdirSync(topicDir);
const insertFiles = filesInDir.filter(f => f.match(/^(hist|comp|math|proj|api)-.*\.md$/));
console.log(`Found ${insertFiles.length} insert sub-article(s) (Inserts are contextual: 0 is valid if self-contained).`);

const foundInserts = { hist: [], comp: [], math: [], proj: [], api: [] };

insertFiles.forEach(ins => {
  const insText = fs.readFileSync(path.join(topicDir, ins), 'utf8');
  const insWords = insText.trim().split(/\s+/).length;
  const prefix = ins.split('-')[0];

  // Rule 1: H1 Title
  if (!insText.trim().startsWith('#')) {
    auditIssues.push(`Insert ${ins} missing H1 title header (# Title).`);
  }
  // Rule 2: Self-justifying intro
  const insParagraphs = insText.split(/\r?\n\s*\r?\n/).map(p => p.trim()).filter(p => p && !p.startsWith('#'));
  const firstInsPara = insParagraphs[0] || '';
  if (firstInsPara.length < 30) {
    auditIssues.push(`Insert ${ins} missing self-justifying intro sentence.`);
  }
  // Rule 3: No preknowlist in inserts
  if (insText.includes('<preknowlist>')) {
    auditIssues.push(`Forbidden <preknowlist> in insert: ${ins}`);
  }
  // Rule 4: No backward navigation cards
  if (insText.match(/🔗 Тема|▶️ До теми/)) {
    auditIssues.push(`Forbidden backward card in insert: ${ins}`);
  }
  // Rule 5: Word count (400–5000)
  if (insWords < 400 || insWords > 5000) {
    auditIssues.push(`Insert ${ins} word count (${insWords}) outside 400–5000 range.`);
  }

  // Rule 6: NO LaTeX Notation in Inserts (§5 AUTHORING.md)
  const insLatexRegex = /\$|\\frac|\\mathbb|\\mathcal|\\text\{|\\log_|\\sqrt|\\cdot|\\le|\\ge|\\to|\\forall|\\exists|\\land|\\lor|\\neg|\\vdash|\\models/;
  if (insLatexRegex.test(insText)) {
    auditIssues.push(`LaTeX Formula Violation in insert ${ins}: NO LaTeX allowed ($...$, \\frac, \\mathbb, etc.). The browser engine has no KaTeX! Convert to Unicode symbols (· ≤ ≥ → ∀ ∃ ¬ ∧ ∨ ⊢), inline code, or aligned formula code blocks.`);
  }

  // Rule 6: Type-Specific Semantic & Structural Audit (§3 AUTHORING.md)
  if (prefix === 'proj') {
    if (!insText.includes('```')) {
      auditIssues.push(`Insert ${ins} (proj) missing concrete code implementation block.`);
    }
    // Calculate prose words outside code blocks
    const proseWithoutCode = insText.replace(/```[\s\S]*?```/g, '').trim();
    const proseWords = proseWithoutCode.split(/\s+/).filter(Boolean).length;
    if (proseWords < 200) {
      auditIssues.push(`Insert ${ins} (proj) is a raw code dump with insufficient explanatory prose (${proseWords} words outside code). Must include problem statement, architectural logic, step-by-step code breakdown, and I/O complexity analysis.`);
    }
  } else if (prefix === 'api') {
    if (!insText.includes('```') && !insText.includes('|')) {
      auditIssues.push(`Insert ${ins} (api) missing structured API specification code block or table.`);
    }
    const proseWords = insText.replace(/```[\s\S]*?```/g, '').trim().split(/\s+/).filter(Boolean).length;
    if (proseWords < 150) {
      auditIssues.push(`Insert ${ins} (api) missing contract explanation, invariants, or usage patterns.`);
    }
  } else if (prefix === 'math') {
    const proseWords = insText.replace(/\$\$[\s\S]*?\$\$/g, '').trim().split(/\s+/).filter(Boolean).length;
    if (proseWords < 200) {
      auditIssues.push(`Insert ${ins} (math) is a raw formula dump without explanatory prose (${proseWords} words). Must explain mathematical intuition, step-by-step derivation, and practical meaning.`);
    }
  }

  if (foundInserts[prefix]) {
    foundInserts[prefix].push({ file: ins, status: 'done' });
  }
});

// Report Results
if (auditIssues.length === 0) {
  bookMeta.sections.forEach(sec => {
    sec.topics.forEach(top => {
      if (top.slug === targetUnit.slug && sec.slug === targetUnit.section) {
        if (top.detailed) top.detailed.status = 'done';
        else top.status = 'done';
        if (top.basic) top.basic.status = 'empty';

        // Sync insert arrays in manifest with actual existing inserts
        top.hist = foundInserts.hist;
        top.comp = foundInserts.comp;
        top.math = foundInserts.math;
        top.proj = foundInserts.proj;
        top.api = foundInserts.api;
      }
    });
  });
  const updatedManifestJs = 'window.__BOOKS__ = window.__BOOKS__ || [];\nwindow.__BOOKS__.push(\n' + JSON.stringify(bookMeta, null, 2) + '\n);\n';
  fs.writeFileSync(manifestPath, updatedManifestJs, 'utf8');
  console.log(`\n🎉 100% PERFECT! Topic [${targetUnit.slug}] passed all cognitive & Feynman checks. Marked as DONE in manifest.js.`);
} else {
  console.log(`\n⚠️ AUDIT FAILED for [${targetUnit.slug}]. Iterative refinement pass needed!`);
  console.log(`   Found ${auditIssues.length} issue(s):`);
  auditIssues.forEach((issue, idx) => {
    console.log(`   ${idx + 1}. ✖ ${issue}`);
  });
  process.exit(1);
}

console.log(`\n================================================================`);
console.log(`🏁 SINGLE-TOPIC PIPELINE COMPLETED FOR: ${targetUnit.slug}`);
console.log(`================================================================`);
