// Build the finish-batch payload for one book: units + missing inserts (prose-driven, journal-enriched) + newTopics + detailed queue
const fs = require('fs');
const path = require('path');

const REPO = 'E:\\develop\\courses';
const WF = 'C:\\Users\\andri\\.claude\\projects\\E--develop-courses\\6752e8fc-d288-48e2-9bc9-49d8a8c1c78a\\subagents\\workflows';
const RUNS = {
  communications: 'wf_733c29c7-cb1',
  algorithms: 'wf_2582bc1c-4b0',
  math: 'wf_a94e7a56-553',
  electronics: 'wf_562b6642-f12',
  programming: 'wf_8cb7a918-6b1',
};
const BOOK = process.argv[2];
if (!RUNS[BOOK]) { console.error('usage: node payload.js <book>'); process.exit(1); }

const lines = fs.readFileSync(path.join(WF, RUNS[BOOK], 'journal.jsonl'), 'utf8').split(/\r?\n/).filter(Boolean);
let units = [];
const briefs = new Map();      // file -> brief
const newTopics = [];
const detailed = [];           // {book, slug}
for (const l of lines) {
  const e = JSON.parse(l);
  const r = e.result;
  if (!r || typeof r !== 'object') continue;
  if (r.units) units = r.units;
  for (const b of (r.inserts || [])) if (b && b.file) briefs.set(b.file, b.brief || '');
  for (const t of (r.newTopics || [])) newTopics.push(t);
  for (const d of (r.deeperTargets || [])) if (d && d.slug) detailed.push({ book: d.book || BOOK, slug: d.slug });
  if (r.needDetailedSelf && r.files && r.files[0]) {
    const m = r.files[0].match(/([^\\\/]+)\.md$/);
    if (m) detailed.push({ book: BOOK, slug: m[1] });
  }
}

// walk prose of every written article -> the authoritative insert list.
// An insert belongs to the topic named IN THE LINK, not to the article doing the linking.
// A ref whose owner is another topic (or another book) is NOT ours to write here: usually a bad
// link in the prose (wrong/nonexistent slug) -> park it in LINKFIX for a human decision.
const INSERTS = [];
const DONE = [];
const LINKFIX = [];
const seen = new Set();
for (const u of units) {
  const dir = path.join(REPO, 'book', BOOK, u.section, u.slug);
  const md = path.join(dir, u.slug + '.md');
  if (!fs.existsSync(md)) continue;
  const txt = fs.readFileSync(md, 'utf8');
  const re = /(?:book|guide):([a-z0-9-]+)\/([a-z0-9-]+)\/((hist|comp|math|proj)-[a-z0-9-]+\.md)/gi;
  let m;
  while ((m = re.exec(txt))) {
    const linkBook = m[1], linkSlug = m[2], file = m[3], type = m[4].toLowerCase();
    if (linkBook !== BOOK || linkSlug !== u.slug) {
      const k = `${u.slug}|${linkBook}/${linkSlug}/${file}`;
      if (!seen.has(k)) { seen.add(k); LINKFIX.push({ inArticle: `${u.section}/${u.slug}.md`, ref: `book:${linkBook}/${linkSlug}/${file}`, ownerExists: fs.existsSync(path.join(REPO, 'book', linkBook)) }); }
      continue;
    }
    const key = `${u.slug}/${file}`;
    if (seen.has(key)) continue;
    seen.add(key);
    const rec = { file, type, section: u.section, topicSlug: u.slug, topicTitle: u.title };
    if (fs.existsSync(path.join(dir, file))) { DONE.push(rec); continue; }  // written already: register only
    INSERTS.push({ ...rec, brief: briefs.get(file) || '' });                // '' => agent derives brief from owner prose
  }
}

// ── Відновлення newTopics З ПРОЗИ ─────────────────────────────────────────────
// Той самий провал, що й із вставками: статтю урваний прогін записав, а список нових залежних тем
// не повернув. Але ref-и стоять у прозі. Беремо 2-сегментні book:<книга>/<slug>, яких НЕМА в жодному
// маніфесті, і заводимо як pending. Заголовок — з тексту лінка [текст](book:…), секція — на розсуд
// агента фази «Маніфест» (кладемо підказку: секція статті-джерела).
function allManifestSlugs() {
  const set = new Set();
  for (const kind of ['book', 'guide']) {
    const root = path.join(REPO, kind);
    if (!fs.existsSync(root)) continue;
    for (const b of fs.readdirSync(root)) {
      const mf = path.join(root, b, 'manifest.js');
      if (!fs.existsSync(mf)) continue;
      const w = { __BOOKS__: [], __GUIDES__: [] };
      try { new Function('window', fs.readFileSync(mf, 'utf8'))(w); } catch (e) { continue; }
      for (const m of [...w.__BOOKS__, ...w.__GUIDES__]) {
        for (const s of (m.sections || [])) { set.add(`${m.slug}/${s.slug}`); for (const t of (s.topics || [])) set.add(`${m.slug}/${t.slug}`); }
        for (const mod of (m.modules || [])) for (const ch of (mod.chapters || [])) for (const st of (ch.steps || [])) if (st.slug) set.add(`${m.slug}/${st.slug}`);
      }
    }
  }
  return set;
}
const KNOWN = allManifestSlugs();
const RECOVERED = [];
const rseen = new Set();
for (const u of units) {
  const dir = path.join(REPO, 'book', BOOK, u.section, u.slug);
  if (!fs.existsSync(dir)) continue;
  // ВСІ .md теки, не лише стаття: детальна й ВСТАВКИ лінкують за тим самим §6, тож так само
  // можуть спиратися на тему, якої ще нема (а канал оголосити її вставка дістала лише зараз).
  for (const f of fs.readdirSync(dir).filter(x => x.endsWith('.md'))) {
    const txt = fs.readFileSync(path.join(dir, f), 'utf8');
    // [текст](book:книга/slug) — 2 сегменти, без файлу
    const re = /\[([^\]]{1,120})\]\((book|guide):([a-z0-9-]+)\/([a-z0-9-]+)\)/gi;
    let m;
    while ((m = re.exec(txt))) {
      const [, text, kind, tb, tslug] = m;
      if (kind !== 'book') continue;
      const key = `${tb}/${tslug}`;
      if (KNOWN.has(key) || rseen.has(key)) continue;          // вже є тема АБО секція з таким slug
      rseen.add(key);
      if (newTopics.some(t => t.slug === tslug && (t.book || BOOK) === tb)) continue;  // уже в списку з журналу
      if (tb !== BOOK) {
        // Крос-книжна: секція-підказка з НАШОЇ книги тут безглузда — секцію обере той, хто заводить.
        // mkargs винесе її в cross-book.json на серійну реєстрацію (два батчі на один маніфест = втрачена правка).
        RECOVERED.push({ kind: 'book', book: tb, section: '', slug: tslug, titleHint: text.trim(), fromArticle: `${BOOK}/${u.section}/${u.slug}/${f}`, needDetailed: false });
        continue;
      }
      // titleHint (а не title): текст лінка — це шматок речення, часто в непрямому відмінку
      // («поліномом Жегалкіна») або обрізаний («лінійних діофантових»). Остаточну назву сформулює
      // агент фази «Маніфест», прочитавши контекст лінка у файлі-джерелі.
      RECOVERED.push({ kind: 'book', book: tb, section: u.section, slug: tslug, titleHint: text.trim(), fromArticle: `${u.section}/${u.slug}/${f}`, needDetailed: false });
    }
  }
}
for (const r of RECOVERED) newTopics.push(r);

// dedupe newTopics / detailed
const ntSeen = new Set();
const NEWTOPICS = newTopics.filter(t => {
  if (!t || !t.slug || !(t.title || t.titleHint)) return false;
  const k = `${t.book || BOOK}/${t.slug}`;
  if (ntSeen.has(k)) return false; ntSeen.add(k); return true;
});
const dSeen = new Set();
const DETAILED = detailed.filter(d => { const k = `${d.book}/${d.slug}`; if (dSeen.has(k)) return false; dSeen.add(k); return true; });

// articles already on disk -> skip (do NOT rewrite); the rest get written by the Articles phase
const onDisk = units.filter(u => fs.existsSync(path.join(REPO, 'book', BOOK, u.section, u.slug, u.slug + '.md'))).map(u => u.slug);
const missing = units.filter(u => !onDisk.includes(u.slug)).map(u => u.slug);

const payload = { book: BOOK, units, onDisk, missing, inserts: INSERTS, insertsDone: DONE, newTopics: NEWTOPICS, detailed: DETAILED, linkfix: LINKFIX };
const outp = path.join(__dirname, `payload-${BOOK}.json`);
fs.writeFileSync(outp, JSON.stringify(payload, null, 2), 'utf8');
const noBrief = INSERTS.filter(i => !i.brief).length;
console.log(`${BOOK}: units ${units.length} | onDisk(skip) ${onDisk.length} | to write ${missing.length}${missing.length ? ' -> ' + missing.join(', ') : ''}`);
console.log(`  insertsDone(register only) ${DONE.length}`);
console.log(`  inserts to write ${INSERTS.length} (brief from journal ${INSERTS.length - noBrief}, from prose ${noBrief}) | newTopics ${NEWTOPICS.length} | detailed ${DETAILED.length}`);
const cross = NEWTOPICS.filter(t => (t.book || BOOK) !== BOOK);
if (cross.length) console.log(`  ⚠ CROSS-BOOK newTopics (пише в ЧУЖИЙ маніфест): ${cross.map(t => t.book + '/' + t.slug).join(', ')}`);
if (LINKFIX.length) { console.log(`  ⚠ LINKFIX (ref на ЧУЖУ вставку — вставку тут НЕ пишемо, треба правити лінк):`); for (const l of LINKFIX) console.log(`     ${l.inArticle} -> ${l.ref}`); }
console.log('->', outp);
