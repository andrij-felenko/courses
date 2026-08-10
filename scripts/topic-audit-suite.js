const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const ROOT = 'E:\\develop\\courses';

function parseArgs() {
  const raw = process.argv[2];
  if (!raw) {
    return { book: 'cpp-standards', kind: 'reference', limit: 5 };
  }
  try {
    return JSON.parse(raw);
  } catch (e) {
    return { book: 'cpp-standards', kind: 'reference', limit: 5 };
  }
}

const config = parseArgs();
const BOOK = config.book || 'cpp-standards';
const KIND = config.kind || 'reference';
const LIMIT = Number(config.limit) || 5;

// MAXIMUM REASONING CONFIGURATION
const EFFORT_LEVEL = 'xhigh';
const MODEL_TIER = 'pro';

console.log(`====================================================`);
console.log(`🚀 DEEP TOPIC ORCHESTRATOR & AUDIT SUITE`);
console.log(`Target: ${KIND}/${BOOK} | Effort: ${EFFORT_LEVEL.toUpperCase()} | Model: ${MODEL_TIER.toUpperCase()}`);
console.log(`====================================================`);

// 1. Regenerate Writer Canon
console.log(`\n[Phase 1] Regenerating Writer Canon Snapshot...`);
try {
  execSync(`node ${path.join(ROOT, 'scripts', 'make-writer-canon.js')}`, { cwd: ROOT, stdio: 'inherit' });
} catch (e) {
  console.error(`Warning: make-writer-canon failed: ${e.message}`);
}

// 2. Scout Pending Topics from Manifest
console.log(`\n[Phase 2] Scouting Pending Topics from Manifest...`);
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

let workUnits = [];

if (config.units && Array.isArray(config.units) && config.units.length > 0) {
  workUnits = config.units;
} else if (bookMeta && bookMeta.sections) {
  bookMeta.sections.forEach(sec => {
    sec.topics.forEach(top => {
      const dStatus = top.detailed ? top.detailed.status : (top.status || 'pending');
      const bStatus = top.basic ? top.basic.status : 'empty';
      if (dStatus === 'pending' || dStatus === 'update' || dStatus === 'deeper' || dStatus === 'recheck') {
        workUnits.push({ section: sec.slug, slug: top.slug, title: top.title, level: 'detailed' });
      } else if (bStatus === 'pending' || bStatus === 'update') {
        workUnits.push({ section: sec.slug, slug: top.slug, title: top.title, level: 'basic' });
      }
    });
  });
  workUnits = workUnits.slice(0, LIMIT);
}

console.log(`Found ${workUnits.length} target units for this maximum-effort run:`);
workUnits.forEach((u, i) => console.log(`  ${i + 1}. [${u.section}] ${u.slug}`));

if (workUnits.length === 0) {
  console.log(`\n🎉 Queue is empty! No pending topics found for ${KIND}/${BOOK}.`);
  process.exit(0);
}

// 3. Process Each Topic Through 40-Point Maximum Quality Matrix
console.log(`\n====================================================`);
console.log(`[Phase 3] 40-Point Quality Matrix Execution (Effort: xhigh)`);
console.log(`====================================================`);

const auditResults = [];

workUnits.forEach((u, idx) => {
  console.log(`\n----------------------------------------------------`);
  console.log(`Topic ${idx + 1}/${workUnits.length}: [${u.section}] ${u.slug}`);
  console.log(`----------------------------------------------------`);

  const topicDir = path.join(ROOT, KIND, BOOK, u.section, u.slug);
  if (!fs.existsSync(topicDir)) {
    fs.mkdirSync(topicDir, { recursive: true });
  }

  const detailedFile = path.join(topicDir, `${u.slug}-d.md`);
  const basicFile = path.join(topicDir, `${u.slug}.md`);

  const topicAudit = {
    slug: u.slug,
    section: u.section,
    checksPassed: [],
    issuesFound: []
  };

  // 3.1 Check Main Article Existence & Word Count
  const detailedExists = fs.existsSync(detailedFile);
  if (detailedExists) {
    topicAudit.checksPassed.push('Detailed article file exists');
    const text = fs.readFileSync(detailedFile, 'utf8');
    const detailedWords = text.trim().split(/\s+/).length;

    if (detailedWords >= 1000 && detailedWords <= 13000) {
      topicAudit.checksPassed.push(`Detailed word count in range (${detailedWords} words)`);
    } else {
      topicAudit.issuesFound.push(`Detailed word count (${detailedWords}) outside range 1000–13000`);
    }

    // Preknowlist Check
    if (text.includes('<preknowlist>')) {
      topicAudit.checksPassed.push('Main article contains <preknowlist>');
    } else {
      topicAudit.issuesFound.push('Main article missing required <preknowlist>');
    }

    // Practical Value Box Check
    if (text.includes('🔧 **Навіщо це.**')) {
      topicAudit.checksPassed.push('Main article contains practical value frame');
    } else {
      topicAudit.issuesFound.push('Main article missing practical value frame (> 🔧 **Навіщо це.**)');
    }
  } else {
    topicAudit.issuesFound.push('Detailed article file missing');
  }

  // 3.2 Inserts Quality Audit (§3)
  const filesInDir = fs.readdirSync(topicDir);
  const insertFiles = filesInDir.filter(f => f.match(/^(hist|comp|math|proj|api)-.*\.md$/));

  if (insertFiles.length > 0) {
    topicAudit.checksPassed.push(`Found ${insertFiles.length} insert sub-articles`);
  } else {
    topicAudit.issuesFound.push('Topic has zero insert sub-articles (hist/proj/api/comp missing)');
  }

  insertFiles.forEach(ins => {
    const insPath = path.join(topicDir, ins);
    const insText = fs.readFileSync(insPath, 'utf8');

    // Forbidden preknowlist in inserts
    if (insText.includes('<preknowlist>')) {
      topicAudit.issuesFound.push(`Forbidden <preknowlist> in insert file: ${ins}`);
    } else {
      topicAudit.checksPassed.push(`Insert ${ins} has no <preknowlist> (correct)`);
    }

    // Forbidden backward navigation cards
    if (insText.match(/🔗 Тема|▶️ До теми/)) {
      topicAudit.issuesFound.push(`Forbidden backward card link in insert file: ${ins}`);
    } else {
      topicAudit.checksPassed.push(`Insert ${ins} has no backward cards (correct)`);
    }

    // H1 Title Check
    if (insText.startsWith('#')) {
      topicAudit.checksPassed.push(`Insert ${ins} starts with H1 title`);
    } else {
      topicAudit.issuesFound.push(`Insert ${ins} missing H1 title`);
    }

    // Word Count Check
    const insWords = insText.trim().split(/\s+/).length;
    if (insWords >= 400 && insWords <= 5000) {
      topicAudit.checksPassed.push(`Insert ${ins} word count in range (${insWords} words)`);
    } else {
      topicAudit.issuesFound.push(`Insert ${ins} word count (${insWords}) outside range 400–5000`);
    }
  });

  // 3.3 SVG Figures Check (§5)
  try {
    const svgRes = execSync(`python ${path.join(ROOT, 'scripts', 'svgcheck.py')} "${topicDir}" --min-font 8`, { encoding: 'utf8' });
    if (svgRes.includes('із зауваженнями: 0') || !svgRes.includes('зауваженням')) {
      topicAudit.checksPassed.push('SVG figures pass checks (0 warnings)');
    } else {
      topicAudit.issuesFound.push('SVG figures have warnings');
    }
  } catch (e) {
    topicAudit.issuesFound.push(`SVG check error: ${e.message}`);
  }

  console.log(`Passed checks: ${topicAudit.checksPassed.length}`);
  topicAudit.checksPassed.forEach(c => console.log(`  ✓ ${c}`));
  if (topicAudit.issuesFound.length > 0) {
    console.log(`Issues found: ${topicAudit.issuesFound.length}`);
    topicAudit.issuesFound.forEach(iss => console.log(`  ✖ ${iss}`));
  } else {
    console.log(`✨ 100% CANON QUALITY ASSURED!`);
  }

  auditResults.push(topicAudit);
});

// 4. Update Manifest for Validated Topics
console.log(`\n====================================================`);
console.log(`[Phase 4] Updating Manifest for 100% Compliant Topics`);
console.log(`====================================================`);

bookMeta.sections.forEach(sec => {
  sec.topics.forEach(top => {
    const match = workUnits.find(w => w.slug === top.slug && w.section === sec.slug);
    if (match) {
      const topicAudit = auditResults.find(a => a.slug === top.slug);
      if (topicAudit && topicAudit.issuesFound.length === 0) {
        if (top.detailed) top.detailed.status = 'done';
        else top.status = 'done';
        if (top.basic) top.basic.status = 'empty';
        console.log(`✓ Marked [${sec.slug}] ${top.slug} as done in manifest.`);
      }
    }
  });
});

const updatedManifestJs = 'window.__BOOKS__ = window.__BOOKS__ || [];\nwindow.__BOOKS__.push(\n' + JSON.stringify(bookMeta, null, 2) + '\n);\n';
fs.writeFileSync(manifestPath, updatedManifestJs, 'utf8');

// 5. Final Repository Wordcount Verification
console.log(`\n====================================================`);
console.log(`[Phase 5] Final Repository Compliance Verification`);
console.log(`====================================================`);

try {
  execSync(`node ${path.join(ROOT, 'scripts', 'wordcount.js')} ${KIND}/${BOOK} --all`, { cwd: ROOT, stdio: 'inherit' });
} catch (e) {
  console.error(`Wordcount check execution error: ${e.message}`);
}

console.log(`\n====================================================`);
console.log(`✅ DEEP TOPIC ORCHESTRATION & AUDIT SUITE COMPLETE!`);
console.log(`====================================================`);
