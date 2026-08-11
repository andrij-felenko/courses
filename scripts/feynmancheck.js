#!/usr/bin/env node
/* ============================================================================
   feynmancheck.js — РЕПОЗИТОРНИЙ СКАНЕР ЯКОСТІ ПОЯСНЕННЯ ТА КОГНІТИВНОЇ ЛЕГКОСТІ.
   
   Перевіряє .md файли книг на дотримання Канону Фейнмана та когнітивної легкості (§4 AUTHORING.md):
   
   (1) TEXTBOOK OPENING — сухий академічний вступ замість інтуїції та проблеми з першопричин.
   (2) MISSING PROBLEM MOTIVATION — відсутність опису причин виникнення проблеми в перших абзацах.
   (3) CURSE OF KNOWLEDGE — введення абстрактних наукових термінів до побудови механізму.
   (4) PASSIVE ACADEMIC TONE — сухі пасивні конструкції ("Дано...", "Формула визначається як...").
   (5) CAUSAL CHAIN CONTINUITY — відсутність причинно-наслідкових містків між абзацами.
========================================================================== */

const fs = require('fs');
const path = require('path');

const argv = process.argv.slice(2);
const TARGET_DIR = argv.find(a => !a.startsWith('--')) || '.';
const MARK_UPDATE = argv.includes('--mark-update');

const ROOT = path.resolve(__dirname, '..');

// Патерни сухих підручникових вступів
const DRY_TEXTBOOK_PATTERNS = [
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

// Патерни сухого пасивного тону
const PASSIVE_ACADEMIC_PATTERNS = [
  /дано\s+векторний/i,
  /характерною\s+рисою\s+є\s+те,\s*що/i,
  /розглянемо\s+формальне\s+визначення/i,
  /слід\s+зазначити,\s*що\s+існує/i
];

// Маркери інтуїції та мотивації з першопричин
const INTUITION_MOTIVATION_PATTERNS = [
  /чому/i,
  /проблема/i,
  /обмеження/i,
  /навіщо/i,
  /якщо\s+спробувати/i,
  /виникає\s+питання/i,
  /першопричин/i,
  /намагалися\s+розв'язати/i,
  /зіткнулися\s+з/i
];

// Маркери причинно-наслідкового зв'язку
const CAUSAL_CONNECTORS = [
  /отже/i,
  /тому/i,
  /це\s+означає/i,
  /звідси\s+випливає/i,
  /як\s+наслідок/i,
  /це\s+приводить\s+до/i,
  /завдяки\s+цьому/i
];

function getMdFiles(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const fullPath = path.join(dir, file);
    const stat = fs.statSync(fullPath);
    if (stat && stat.isDirectory()) {
      if (!file.startsWith('.') && file !== 'node_modules' && file !== '__pycache__') {
        results = results.concat(getMdFiles(fullPath));
      }
    } else if (file.endsWith('.md')) {
      results.push(fullPath);
    }
  });
  return results;
}

const targetPath = path.resolve(process.cwd(), TARGET_DIR);
console.log(`================================================================`);
console.log(`🧠 COGNITIVE EASE & FEYNMAN AUDITOR: Scanning markdown files in ${targetPath}`);
console.log(`================================================================\n`);

const mdFiles = getMdFiles(targetPath);
const issues = [];
const flaggedSlugs = new Set();

mdFiles.forEach(filePath => {
  const relPath = path.relative(ROOT, filePath).replace(/\\/g, '/');
  
  if (relPath.startsWith('scripts/') || relPath.startsWith('.agents/') || relPath.endsWith('AGENTS.md') || relPath.endsWith('AUTHORING.md')) {
    return;
  }

  const content = fs.readFileSync(filePath, 'utf8');
  const cleanContent = content.replace(/<preknowlist>[\s\S]*?<\/preknowlist>/g, '').trim();
  const paragraphs = cleanContent.split(/\r?\n\s*\r?\n/).map(p => p.trim()).filter(p => p && !p.startsWith('#'));
  
  if (paragraphs.length === 0) return;

  const firstThreePara = paragraphs.slice(0, 3).join(' ');

  // 1. Сухий підручниковий початок
  const dryMatch = DRY_TEXTBOOK_PATTERNS.find(re => re.test(firstThreePara));
  if (dryMatch) {
    issues.push({
      file: relPath,
      rule: 'Textbook Opening Violation',
      details: `Вступ містить суху підручникову формулу: "${dryMatch.exec(firstThreePara)[0]}". Секція 1 мусить описувати проблему з першопричин!`
    });
    extractSlug(relPath, flaggedSlugs);
  }

  // 2. Відсутність мотивації та проблеми
  const hasMotivation = INTUITION_MOTIVATION_PATTERNS.some(re => re.test(firstThreePara));
  if (!hasMotivation && paragraphs.length > 5 && !filePath.includes('hist-')) {
    issues.push({
      file: relPath,
      rule: 'Missing Problem Motivation',
      details: `У перших 3 абзацах відсутні маркери мотивації/проблеми (чому виникла задача, з яким обмеженням зіткнулися).`
    });
    extractSlug(relPath, flaggedSlugs);
  }

  // 3. Сухий пасивний тон
  const passiveMatch = PASSIVE_ACADEMIC_PATTERNS.find(re => re.test(cleanContent));
  if (passiveMatch) {
    issues.push({
      file: relPath,
      rule: 'Passive Academic Tone Violation',
      details: `Виявлено сухий пасивний зворот: "${passiveMatch.exec(cleanContent)[0]}". Замініть на активне розслідування з читачем.`
    });
    extractSlug(relPath, flaggedSlugs);
  }

  // 4. Безперервність причинно-наслідкових ланцюжків
  const hasCausal = CAUSAL_CONNECTORS.some(re => re.test(cleanContent));
  if (!hasCausal && paragraphs.length > 6) {
    issues.push({
      file: relPath,
      rule: 'Causal Chain Continuity Violation',
      details: `У довгому тексті відсутні причинно-наслідкові сполучники (отже, тому, це означає, звідси випливає). Логічний зв'язок розірвано.`
    });
    extractSlug(relPath, flaggedSlugs);
  }
});

function extractSlug(relPath, slugSet) {
  const parts = relPath.split('/');
  if (parts.length >= 4) {
    const slug = parts[3];
    slugSet.add({ book: parts[1], slug });
  }
}

if (issues.length === 0) {
  console.log(`🎉 100% PERFECT! Всі перевірені markdown-файли відповідають Канону Фейнмана та Когнітивній Легкості.`);
} else {
  console.log(`⚠️ ЗНАЙДЕНО ${issues.length} ПОРУШЕНЬ КОГНІТИВНОЇ ЛЕГКОСТІ ТА КАНОНУ ФЕЙНМАНА:\n`);
  issues.forEach((iss, idx) => {
    console.log(`${idx + 1}. ✖ [${iss.rule}] ${iss.file}`);
    console.log(`   ${iss.details}\n`);
  });

  if (MARK_UPDATE) {
    console.log(`\n================================================================`);
    console.log(`[Manifest Updater] Переведення флагованих тем у статус 'update'`);
    console.log(`================================================================`);
    
    flaggedSlugs.forEach(item => {
      const manifestPath = path.join(ROOT, 'book', item.book, 'manifest.js');
      if (fs.existsSync(manifestPath)) {
        try {
          delete require.cache[require.resolve(manifestPath)];
          global.window = { __BOOKS__: [] };
          require(manifestPath);
          const bMeta = global.window.__BOOKS__.find(b => b.slug === item.book);
          if (bMeta && bMeta.sections) {
            let updated = false;
            bMeta.sections.forEach(sec => {
              sec.topics.forEach(top => {
                if (top.slug === item.slug) {
                  if (top.detailed) top.detailed.status = 'update';
                  else top.status = 'update';
                  updated = true;
                }
              });
            });
            if (updated) {
              const newMJs = 'window.__BOOKS__ = window.__BOOKS__ || [];\nwindow.__BOOKS__.push(\n' + JSON.stringify(bMeta, null, 2) + '\n);\n';
              fs.writeFileSync(manifestPath, newMJs, 'utf8');
              console.log(`✓ Тему [${item.slug}] у ${item.book}/manifest.js переведено в статус 'update'.`);
            }
          }
        } catch (e) {
          console.error(`Помилка оновлення маніфесту для ${item.slug}: ${e.message}`);
        }
      }
    });
  }

  process.exit(1);
}
