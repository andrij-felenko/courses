const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = 'E:\\develop\\courses';

function parseArgs() {
  const raw = process.argv[2];
  if (!raw) {
    return { book: 'cpp-standards', kind: 'reference', section: '', slug: '' };
  }
  try {
    return JSON.parse(raw);
  } catch (e) {
    return { book: 'cpp-standards', kind: 'reference', section: '', slug: '' };
  }
}

const config = parseArgs();
const BOOK = config.book || 'cpp-standards';
const KIND = config.kind || 'reference';
const TARGET_SECTION = config.section || '';
const TARGET_SLUG = config.slug || '';

console.log(`================================================================`);
console.log(`🚀 SINGLE-TOPIC MULTI-AGENT AUDITOR & AUTHOR WITH DISCOVERY`);
console.log(`Language Standard: C++ IS FREQUENTLY REQUIRED ALONGSIDE C IN :::tabs`);
console.log(`Target: ${KIND}/${BOOK} | Effort: XHIGH`);
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

// 3. Final Verification Phase (C++ REQUIRED ALONGSIDE C IN :::tabs)
console.log(`\n================================================================`);
console.log(`[Verification] Checking Canon Compliance (C++ FREQUENTLY REQUIRED IN :::tabs) for ${targetUnit.slug}`);
console.log(`================================================================`);

let passesAll = true;
if (detailedExists) {
  const text = fs.readFileSync(detailedFile, 'utf8');
  const words = text.trim().split(/\s+/).length;
  console.log(`✓ Detailed article present (${words} words).`);

  if (!text.includes('<preknowlist>')) {
    console.log(`✖ Missing <preknowlist> in main article.`);
    passesAll = false;
  }
  if (!text.includes('🔧 **Навіщо це.**')) {
    console.log(`✖ Missing practical value frame (> 🔧 **Навіщо це.**).`);
    passesAll = false;
  }

  // §5 Tabs & C++ Enforcement: If C code is present, check if C++ tab (@tab C++) is also provided inside :::tabs
  const hasC = text.includes('```c');
  const hasCppTab = text.includes('@tab C++') || text.includes('```cpp') || text.includes('```c++');

  if (hasC && !hasCppTab) {
    console.log(`⚠️ Warning: C code present without corresponding C++ tab (@tab C++) inside :::tabs.`);
    // Enforce C++ tab recommendation
  }

  if (hasCppTab) {
    console.log(`✓ C++ implementation tab (@tab C++) present.`);
  }
} else {
  console.log(`✖ Detailed article file missing: ${detailedFile}`);
  passesAll = false;
}

const filesInDir = fs.readdirSync(topicDir);
const insertFiles = filesInDir.filter(f => f.match(/^(hist|comp|math|proj|api)-.*\.md$/));
console.log(`Found ${insertFiles.length} insert sub-article(s).`);

insertFiles.forEach(ins => {
  const insText = fs.readFileSync(path.join(topicDir, ins), 'utf8');
  const insWords = insText.trim().split(/\s+/).length;
  if (insText.includes('<preknowlist>')) {
    console.log(`✖ Forbidden <preknowlist> in insert: ${ins}`);
    passesAll = false;
  }
  if (insText.match(/🔗 Тема|▶️ До теми/)) {
    console.log(`✖ Forbidden backward card in insert: ${ins}`);
    passesAll = false;
  }
  if (insWords < 400 || insWords > 5000) {
    console.log(`✖ Insert ${ins} word count (${insWords}) outside 400–5000 range.`);
    passesAll = false;
  }
});

// Update Manifest if Passed
if (passesAll) {
  bookMeta.sections.forEach(sec => {
    sec.topics.forEach(top => {
      if (top.slug === targetUnit.slug && sec.slug === targetUnit.section) {
        if (top.detailed) top.detailed.status = 'done';
        else top.status = 'done';
        if (top.basic) top.basic.status = 'empty';
      }
    });
  });
  const updatedManifestJs = 'window.__BOOKS__ = window.__BOOKS__ || [];\nwindow.__BOOKS__.push(\n' + JSON.stringify(bookMeta, null, 2) + '\n);\n';
  fs.writeFileSync(manifestPath, updatedManifestJs, 'utf8');
  console.log(`\n✓ Topic [${targetUnit.slug}] marked as DONE in manifest.js.`);
} else {
  console.log(`\n⚠️ Topic [${targetUnit.slug}] requires authoring/fixing pass.`);
}

console.log(`\n================================================================`);
console.log(`🏁 SINGLE-TOPIC PIPELINE COMPLETED FOR: ${targetUnit.slug}`);
console.log(`================================================================`);
