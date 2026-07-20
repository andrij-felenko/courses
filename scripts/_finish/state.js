// WHERE WE ARE: per book — articles on disk, inserts written vs needed, manifest status, what's left.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';
const BOOKS = ['communications', 'algorithms', 'programming', 'math', 'electronics'];

function loadManifest(book) {
  const src = fs.readFileSync(path.join(REPO, 'book', book, 'manifest.js'), 'utf8');
  const w = { __BOOKS__: [], __GUIDES__: [] };
  new Function('window', src)(w);
  return w.__BOOKS__[0];
}
function findTopic(man, section, slug) {
  for (const s of man.sections || []) if (s.slug === section) for (const t of s.topics || []) if (t.slug === slug) return t;
  return null;
}

const L = [];
const totals = { art: 0, artNeed: 0, ins: 0, insNeed: 0, done: 0 };
for (const book of BOOKS) {
  const p = require(`./payload-${book}.json`);
  const man = loadManifest(book);
  let art = 0, ins = 0, mdone = 0;
  const missingArt = [], missingIns = [];
  for (const u of p.units) {
    const dir = path.join(REPO, 'book', book, u.section, u.slug);
    if (fs.existsSync(path.join(dir, u.slug + '.md'))) art++; else missingArt.push(u.slug);
    const t = findTopic(man, u.section, u.slug);
    if (t && t.basic && t.basic.status === 'done') mdone++;
  }
  for (const i of p.inserts) {
    const f = path.join(REPO, 'book', book, i.section, i.topicSlug, i.file);
    if (fs.existsSync(f)) ins++; else missingIns.push(`${i.topicSlug}/${i.file}`);
  }
  totals.art += art; totals.artNeed += p.units.length;
  totals.ins += ins; totals.insNeed += p.inserts.length;
  totals.done += mdone;
  L.push(`${book.toUpperCase()}`);
  L.push(`  статті:  ${art}/${p.units.length} на диску${missingArt.length ? '   БРАКУЄ: ' + missingArt.join(', ') : ''}`);
  L.push(`  вставки: ${ins}/${p.inserts.length} написано${missingIns.length ? `   лишилось ${missingIns.length}` : '   ✔ усі'}`);
  L.push(`  маніфест: basic done ${mdone}/${p.units.length}${mdone === 0 ? '   (нічого не зареєстровано)' : ''}`);
  if (missingIns.length) L.push(`     ще писати: ${missingIns.slice(0, 40).join(', ')}`);
  L.push('');
}
L.push('#'.repeat(70));
L.push(`РАЗОМ: статті ${totals.art}/${totals.artNeed} | вставки ${totals.ins}/${totals.insNeed} | зареєстровано done ${totals.done}/${totals.artNeed}`);
L.push(`ЛИШИЛОСЬ написати: статей ${totals.artNeed - totals.art}, вставок ${totals.insNeed - totals.ins}`);
fs.writeFileSync(path.join(__dirname, 'state.txt'), L.join('\n'), 'utf8');
console.log(L.join('\n'));
