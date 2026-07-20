// ЗВІДКИ ЦИФРИ: (1) 18+1 НОВИХ тем — з ref-ів у прозі на теми, яких нема в жодному маніфесті;
//               (2) 24 detailed — це вже НАПИСАНІ 13+13 статей, чия detailed-версія стоїть empty.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';

// ── усі теми з усіх маніфестів репо ──
const TOPIC = new Set();
for (const kind of ['book', 'guide', 'catalog']) {
  const root = path.join(REPO, kind);
  if (!fs.existsSync(root)) continue;
  for (const b of fs.readdirSync(root)) {
    const mf = path.join(root, b, 'manifest.js');
    if (!fs.existsSync(mf)) continue;
    const w = { __BOOKS__: [], __GUIDES__: [] };
    try { new Function('window', fs.readFileSync(mf, 'utf8'))(w); } catch { continue; }
    for (const m of [...w.__BOOKS__, ...w.__GUIDES__]) {
      for (const s of m.sections || []) for (const t of s.topics || []) TOPIC.add(`${m.slug}/${t.slug}`);
      for (const mo of m.modules || []) for (const c of mo.chapters || []) for (const st of c.steps || []) if (st.slug) TOPIC.add(`${m.slug}/${st.slug}`);
    }
  }
}

for (const book of ['math', 'electronics']) {
  const a = JSON.parse(fs.readFileSync(path.join(__dirname, `args-${book}.json`), 'utf8'));
  const p = JSON.parse(fs.readFileSync(path.join(__dirname, `payload-${book}.json`), 'utf8'));

  console.log('='.repeat(78));
  console.log(`${book.toUpperCase()}  —  (1) НОВІ ТЕМИ, які батч заведе як pending: ${(a.newTopics || []).length}`);
  console.log('='.repeat(78));
  for (const t of a.newTopics || []) {
    const key = `${t.book || book}/${t.slug}`;
    // хто на неї лінкує
    const from = [];
    for (const u of p.units) {
      const f = path.join(REPO, 'book', book, u.section, u.slug, u.slug + '.md');
      if (!fs.existsSync(f)) continue;
      const src = fs.readFileSync(f, 'utf8');
      const re = new RegExp(`book:${(t.book || book)}\\/${t.slug}(?![\\w-])`, 'g');
      const n = (src.match(re) || []).length;
      if (n) from.push(`${u.slug}${n > 1 ? '×' + n : ''}`);
    }
    console.log(`  ${t.slug.padEnd(30)} ${TOPIC.has(key) ? '[ВЖЕ Є]' : '[нова] '} ${t.title || t.titleHint || '(без назви!)'}`);
    console.log(`  ${' '.repeat(30)} ← лінкують: ${from.join(', ') || '(?)'}`);
  }

  console.log(`\n${book.toUpperCase()}  —  (2) DETAILED: 13 вже НАПИСАНИХ статей цього батчу`);
  const w = { __BOOKS__: [] };
  new Function('window', fs.readFileSync(path.join(REPO, 'book', book, 'manifest.js'), 'utf8'))(w);
  const T = new Map();
  for (const s of w.__BOOKS__[0].sections || []) for (const t of s.topics || []) T.set(t.slug, t);
  const queued = new Set((a.detailed || []).map(d => d.slug));
  for (const u of p.units) {
    const t = T.get(u.slug);
    const st = t && t.detailed ? t.detailed.status : '???';
    console.log(`  ${u.slug.padEnd(30)} detailed=${String(st).padEnd(8)} ${queued.has(u.slug) ? '← батч ПОСТАВИТЬ pending' : '  лишиться empty'}`);
  }
  console.log();
}
