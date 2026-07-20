// НЕЗАЛЕЖНИЙ аудит з нуля. НЕ читає payload-*.json і взагалі жодних похідних.
// Джерела: (1) реальні файли на диску, (2) маніфести. Усе рахується наново.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';
const BOOKS = ['communications', 'algorithms', 'programming', 'math', 'electronics'];

// ── 1. усі теми/секції з УСІХ маніфестів репо ──
const TOPIC = new Map(), SECTION = new Set();
for (const kind of ['book', 'guide', 'catalog']) {
  const root = path.join(REPO, kind);
  if (!fs.existsSync(root)) continue;
  for (const b of fs.readdirSync(root)) {
    const mf = path.join(root, b, 'manifest.js');
    if (!fs.existsSync(mf)) continue;
    const w = { __BOOKS__: [], __GUIDES__: [] };
    try { new Function('window', fs.readFileSync(mf, 'utf8'))(w); } catch (e) { console.log('!! не парситься:', mf); continue; }
    for (const m of [...w.__BOOKS__, ...w.__GUIDES__]) {
      for (const s of (m.sections || [])) {
        SECTION.add(`${m.slug}/${s.slug}`);
        for (const t of (s.topics || [])) TOPIC.set(`${m.slug}/${t.slug}`, { ...t, section: s.slug, book: m.slug });
      }
      for (const mod of (m.modules || [])) for (const ch of (mod.chapters || [])) for (const st of (ch.steps || [])) if (st.slug) TOPIC.set(`${m.slug}/${st.slug}`, { ...st, book: m.slug });
    }
  }
}

// ── 2. пройти КОЖНУ теку теми кожної з 5 книг ──
const out = [];
for (const book of BOOKS) {
  const root = path.join(REPO, 'book', book);
  const missTopics = new Map(), missIns = new Set(), secRefs = new Map();
  let artOnDisk = 0, artDone = 0, artPendingButWritten = 0, insOnDisk = 0, insReg = 0;
  let topicsTotal = 0;

  for (const sec of fs.readdirSync(root, { withFileTypes: true })) {
    if (!sec.isDirectory()) continue;
    for (const top of fs.readdirSync(path.join(root, sec.name), { withFileTypes: true })) {
      if (!top.isDirectory()) continue;
      const dir = path.join(root, sec.name, top.name);
      const slug = top.name;
      const t = TOPIC.get(`${book}/${slug}`);
      topicsTotal++;
      const artFile = path.join(dir, slug + '.md');
      const hasArt = fs.existsSync(artFile);
      if (hasArt) {
        artOnDisk++;
        const st = t && t.basic ? t.basic.status : '(теми в маніфесті НЕМА)';
        if (st === 'done') artDone++;
        else artPendingButWritten++;
      }
      const insFiles = fs.readdirSync(dir).filter(f => /^(hist|comp|math|proj)-.*\.md$/.test(f));
      insOnDisk += insFiles.length;
      if (t) insReg += ['hist', 'comp', 'math', 'proj'].reduce((n, k) => n + (t[k] || []).length, 0);

      // рефи з УСІХ .md цієї теки
      for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.md'))) {
        const txt = fs.readFileSync(path.join(dir, f), 'utf8');
        // ref на ФАЙЛ-вставку: book:книга/тема/тип-назва.md
        const reF = /(?:book|guide):([a-z0-9-]+)\/([a-z0-9-]+)\/((?:hist|comp|math|proj)-[a-z0-9-]+\.md)/gi;
        let m;
        while ((m = reF.exec(txt))) {
          const owner = TOPIC.get(`${m[1]}/${m[2]}`);
          if (!owner) { missTopics.set(`${m[1]}/${m[2]}`, (missTopics.get(`${m[1]}/${m[2]}`) || 0) + 1); continue; }
          if (!owner.section) continue;   // крок guide — секції не має, шлях інший; тут не перевіряємо
          const p = path.join(REPO, 'book', m[1], owner.section, m[2], m[3]);
          if (!fs.existsSync(p)) missIns.add(`${m[1]}/${m[2]}/${m[3]}`);
        }
        // ref на ТЕМУ: book:книга/slug (2 сегменти)
        const reT = /(?:book|guide):([a-z0-9-]+)\/([a-z0-9-]+)(?![a-z0-9\-\/])/gi;
        while ((m = reT.exec(txt))) {
          const key = `${m[1]}/${m[2]}`;
          if (TOPIC.has(key)) continue;
          if (SECTION.has(key)) { secRefs.set(key, (secRefs.get(key) || 0) + 1); continue; }
          missTopics.set(key, (missTopics.get(key) || 0) + 1);
        }
      }
    }
  }
  out.push({ book, topicsTotal, artOnDisk, artDone, artPendingButWritten, insOnDisk, insReg, missTopics, missIns, secRefs });
}

const pad = (s, n) => String(s).padStart(n);
console.log('НЕЗАЛЕЖНИЙ АУДИТ — усе перераховано з файлів і маніфестів\n');
console.log('книга           тек   статей  з них   написані   вставок  з них   вставок');
console.log('                тем   на диску  done  та НЕ done  на диску  зареєстр.  БРАКУЄ');
for (const r of out)
  console.log(`${r.book.padEnd(15)} ${pad(r.topicsTotal, 4)}  ${pad(r.artOnDisk, 7)} ${pad(r.artDone, 6)} ${pad(r.artPendingButWritten, 10)}  ${pad(r.insOnDisk, 8)} ${pad(r.insReg, 9)}  ${pad(r.missIns.size, 7)}`);
const S = k => out.reduce((n, r) => n + (typeof r[k] === 'number' ? r[k] : r[k].size), 0);
console.log(`${'РАЗОМ'.padEnd(15)} ${pad(S('topicsTotal'), 4)}  ${pad(S('artOnDisk'), 7)} ${pad(S('artDone'), 6)} ${pad(S('artPendingButWritten'), 10)}  ${pad(S('insOnDisk'), 8)} ${pad(S('insReg'), 9)}  ${pad(S('missIns'), 7)}`);

console.log('\nНЕЗАВЕДЕНІ ТЕМИ (ref є, теми в жодному маніфесті нема):');
for (const r of out) {
  console.log(`── ${r.book}: ${r.missTopics.size}${r.secRefs.size ? `   ⚠ ref на СЕКЦІЮ: ${[...r.secRefs.keys()].join(', ')}` : ''}`);
  for (const [k, n] of [...r.missTopics].sort((a, b) => b[1] - a[1])) console.log(`     ${k.padEnd(42)} ×${n}`);
}
console.log(`\nРАЗОМ незаведених тем (унікальних по книгах): ${S('missTopics')}`);
console.log(`РАЗОМ вставок бракує: ${S('missIns')}`);
