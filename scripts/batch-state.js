#!/usr/bin/env node
/**
 * batch-state.js — ЛОКАЛЬНО (без агентів, без токенів) з'ясовує, що батч устиг, а що ні,
 * і готує payload на доробку. Потрібен, коли прогін обірвала стіна ліміту: фази «Фігури»
 * й «Маніфест» не відпрацювали, тож написане лежить на диску, але читачеві невидиме.
 *
 *   node scripts/batch-state.js --book programming --kind book
 *   node scripts/batch-state.js --book programming --kind book --apply
 *
 * Без --apply: тільки звіт + `scripts/_finish/state-<book>.json`.
 * З --apply: додатково реєструє в маніфесті все, що ВЖЕ на диску (статті → done, вставки → done)
 *            через scripts/manifest-patch.js. Нічого не пише й не переписує — лише статуси.
 *
 * ⚠️ Джерело правди — ДИСК, не журнал прогону: убиті агенти часто вже записали файл,
 *    але результату не повернули, тож у журналі їх нема (див. пам'ять batch-resume-recovery).
 */
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const arg = (n, d) => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : d };
const has = (n) => argv.includes('--' + n);

const BOOK = arg('book');
const KIND = arg('kind', 'book');
if (!BOOK) { console.error('потрібен --book <slug> (і --kind book|catalog|reference|guide)'); process.exit(1) }

const MF = path.join(ROOT, KIND, BOOK, 'manifest.js');
if (!fs.existsSync(MF)) { console.error('нема маніфесту: ' + MF); process.exit(1) }

global.window = { __BOOKS__: [], __GUIDES__: [] };
require(MF);
const bk = (global.window.__BOOKS__[0] || global.window.__GUIDES__[0]);
if (!bk) { console.error('маніфест не зареєстрував книгу'); process.exit(1) }

const INS_RE = /^(hist|comp|math|proj|api)-[a-z0-9-]+\.md$/;
const TYPES = ['hist', 'comp', 'math', 'proj', 'api'];

/** Плоский список тем: {section, slug, title, topic, dir} — однаково для book-подібних і для guide. */
function topics() {
  const out = [];
  if (bk.type === 'guide') {
    for (const m of bk.modules || [])
      for (const ch of m.chapters || [])
        for (const st of ch.steps || [])
          if (st && st.slug) out.push({ section: m.slug, slug: st.slug, title: st.title, topic: st, dir: path.join(ROOT, KIND, BOOK, m.slug, st.slug) });
  } else {
    for (const s of bk.sections || [])
      for (const t of s.topics || [])
        out.push({ section: s.slug, slug: t.slug, title: t.title, topic: t, dir: path.join(ROOT, KIND, BOOK, s.slug, t.slug) });
  }
  return out;
}

const unregArticles = [];   // файл є, статус не done → зареєструвати
const missingArticles = []; // статус pending, файла нема → ще писати
const unregInserts = [];    // файл є, у маніфесті нема → зареєструвати
const notDoneInserts = [];  // у маніфесті є, статус не done, файл є → перевести в done
const missingInserts = [];  // у маніфесті/прозі є, файла нема → ще писати
const units = [];           // payload: теми, чиї статті вже на диску (для skipArticles)

for (const T of topics()) {
  const reg = new Set();
  for (const k of TYPES) for (const i of (T.topic[k] || [])) reg.add(i.file);

  for (const [ver, file] of [['basic', T.slug + '.md'], ['detailed', T.slug + '-d.md']]) {
    const st = T.topic[ver] && T.topic[ver].status;
    const onDisk = fs.existsSync(path.join(T.dir, file));
    if (onDisk && st !== 'done') { unregArticles.push({ section: T.section, slug: T.slug, ver, status: st }); units.push({ section: T.section, slug: T.slug, title: T.title || T.slug, level: ver }) }
    else if (onDisk && st === 'done') units.push({ section: T.section, slug: T.slug, title: T.title || T.slug, level: ver });
    else if (!onDisk && st === 'pending') missingArticles.push(T.section + '/' + T.slug + ' ' + ver);
  }

  // вставки, зареєстровані в маніфесті
  for (const k of TYPES) for (const i of (T.topic[k] || [])) {
    const onDisk = fs.existsSync(path.join(T.dir, i.file));
    if (!onDisk) missingInserts.push({ section: T.section, topicSlug: T.slug, topicTitle: T.title, file: i.file, type: k, why: 'у маніфесті, файла нема' });
    else if (i.status !== 'done') notDoneInserts.push({ section: T.section, topicSlug: T.slug, file: i.file, type: k, status: i.status });
  }
  // вставки, що лежать на диску, але в маніфесті їх нема
  // ⚠️ Стаття теми, чий slug сам починається з типу вставки (api-design → api-design-d.md),
  // під INS_RE підпадає. Тому власні файли статті виключаємо явно, інакше вони поїдуть у вставки.
  const ownFiles = new Set([T.slug + '.md', T.slug + '-d.md']);
  if (fs.existsSync(T.dir)) for (const f of fs.readdirSync(T.dir)) {
    if (INS_RE.test(f) && !reg.has(f) && !ownFiles.has(f)) unregInserts.push({ section: T.section, topicSlug: T.slug, topicTitle: T.title, file: f, type: f.split('-')[0] });
  }
  // вставки, обіцяні в ПРОЗІ, але не написані (обидва формати лінка — §6 і відносний)
  for (const file of [T.slug + '.md', T.slug + '-d.md']) {
    const p = path.join(T.dir, file);
    if (!fs.existsSync(p)) continue;
    const txt = fs.readFileSync(p, 'utf8');
    const refs = new Set();
    // ⚠️ лише вставки ВЛАСНОЇ теми: лінк на чужу (book:<книга>/<інша-тема>/api-…md) — законний,
    // її файл лежить у теці тієї теми, і вимагати його тут було б хибним спрацюванням.
    for (const m of txt.matchAll(/\]\((?:book|guide):[a-z0-9-]+\/([a-z0-9-]+)\/((?:hist|comp|math|proj|api)-[a-z0-9-]+\.md)\)/g)) {
      if (m[1] === T.slug) refs.add(m[2]);
    }
    for (const m of txt.matchAll(/\]\(((?:hist|comp|math|proj|api)-[a-z0-9-]+\.md)\)/g)) refs.add(m[1]);
    for (const f of refs) {
      if (f === T.slug + '.md' || f === T.slug + '-d.md') continue;   // це власна стаття, не вставка
      if (fs.existsSync(path.join(T.dir, f))) continue;
      if (missingInserts.some((x) => x.topicSlug === T.slug && x.file === f)) continue;
      missingInserts.push({ section: T.section, topicSlug: T.slug, topicTitle: T.title, file: f, type: f.split('-')[0], why: 'обіцяна в прозі, файла нема' });
    }
  }
}

const insertsDone = [...unregInserts, ...notDoneInserts.map((i) => ({ ...i }))]
  .map(({ section, topicSlug, topicTitle, file, type }) => ({ section, topicSlug, topicTitle, file, type }));

const line = (s) => console.log(s);
line(`\n=== СТАН БАТЧУ: ${KIND}/${BOOK} ===`);
line(`  статті НА ДИСКУ, але не done у маніфесті: ${unregArticles.length}` + (unregArticles.length ? ' → ' + unregArticles.map((a) => a.slug + ':' + a.ver + '(' + a.status + ')').join(', ') : ''));
line(`  статті pending, файла НЕМА (ще писати):   ${missingArticles.length}` + (missingArticles.length ? ' → ' + missingArticles.slice(0, 12).join(', ') + (missingArticles.length > 12 ? ' …' : '') : ''));
line(`  вставки НА ДИСКУ, у маніфесті НЕМА:       ${unregInserts.length}` + (unregInserts.length ? ' → ' + unregInserts.map((i) => i.topicSlug + '/' + i.file).join(', ') : ''));
line(`  вставки в маніфесті зі статусом ≠ done:   ${notDoneInserts.length}`);
line(`  вставки ОБІЦЯНІ, але не написані:         ${missingInserts.length}` + (missingInserts.length ? '\n' + missingInserts.map((i) => '      · ' + i.topicSlug + '/' + i.file + '  (' + i.why + ')').join('\n') : ''));

const OUTDIR = path.join(ROOT, 'scripts', '_finish');
fs.mkdirSync(OUTDIR, { recursive: true });
const payload = {
  book: BOOK, kind: KIND, limit: units.length + 5, concurrency: 4, skipArticles: true,
  units, insertsDone, inserts: missingInserts.map(({ section, topicSlug, topicTitle, file, type }) => ({ section, topicSlug, topicTitle, file, type })),
};
const OUT = path.join(OUTDIR, `state-${BOOK}.json`);
fs.writeFileSync(OUT, JSON.stringify(payload, null, 1), 'utf8');
line(`\n  payload на доробку → ${path.relative(ROOT, OUT)}  (units ${units.length}, insertsDone ${insertsDone.length}, inserts ${payload.inserts.length})`);

if (!has('apply')) {
  line(`\n  Нічого не змінено. Щоб зареєструвати написане в маніфесті: додай --apply`);
  process.exit(0);
}

const ops = [];
for (const a of unregArticles) ops.push({ op: 'status', slug: a.slug, ver: a.ver, status: 'done' });
for (const i of unregInserts) ops.push({ op: 'insert', slug: i.topicSlug, section: i.section, type: i.type, file: i.file, status: 'done' });
for (const i of notDoneInserts) ops.push({ op: 'insert', slug: i.topicSlug, section: i.section, type: i.type, file: i.file, status: 'done' });
if (!ops.length) { line('\n  --apply: міняти нічого — маніфест уже збігається з диском.'); process.exit(0) }

const opsFile = path.join(OUTDIR, `_mfops-state-${BOOK}.json`);
fs.writeFileSync(opsFile, JSON.stringify(ops, null, 1), 'utf8');
line(`\n  --apply: ${ops.length} операцій → ${path.relative(ROOT, opsFile)}`);
const out = execFileSync(process.execPath, [path.join(ROOT, 'scripts', 'manifest-patch.js'), `${KIND}/${BOOK}/manifest.js`, '--ops', opsFile], { cwd: ROOT, encoding: 'utf8' });
line('  ' + out.trim());
