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
 * З --apply: реєструє те, що ВЖЕ на диску, але в маніфест не потрапило (фаза «Маніфест» не
 *            відпрацювала): статті pending→done, незареєстровані вставки. Статті й вставки в
 *            `recheck` НЕ ЧІПАЄ — цей статус ставить конвеєр Antigravity, а в `done` переводить
 *            ЛЮДИНА через `review-*` (`.agents/rules/pipeline.md`). Нічого не пише — лише статуси.
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
const JOURNAL = arg('journal');            // journal.jsonl обірваного прогону — звідти беруться newTopics
if (!BOOK) { console.error('потрібен --book <slug> — слуг книги в root/ (вид визначиться сам)'); process.exit(1) }

const M7 = require('./lib/manifest7.js');
const BOOKDIR = M7.bookDirOf(BOOK);
if (!BOOKDIR) { console.error('нема книги «' + BOOK + '» у root/ — перевір слуг (root/shelf.json)'); process.exit(1) }
const MF = path.join(BOOKDIR, 'manifest.json');
const BOOKMF = M7.loadBook(BOOKDIR);
if (!BOOKMF) { console.error('нема маніфесту: ' + MF); process.exit(1) }
const bk = BOOKMF.manifest;

const INS_RE = /^(hist|comp|math|proj|api)-[a-z0-9-]+\.md$/;
const TYPES = ['hist', 'comp', 'math', 'proj', 'api'];

/** Плоский список тем: {section, slug, title, topic, dir}.
    v7: «section» — це ГРУПА з маніфесту, а тека теми лежить ПЛАСКО під книгою,
    бо ні групи, ні розділу в шляху немає. */
function topics() {
  return M7.allTopics(BOOKMF).filter((t) => t.own).map((t) => ({
    section: t.group, chapter: t.chapter, slug: t.slug, title: t.title,
    topic: t.node, dir: path.join(BOOKDIR, t.slug),
  }));
}

/* ⚠️ `recheck` — НЕ слід урваного батчу, а домовлений проміжний стан
   (`.agents/rules/pipeline.md`): `finish-batch.js` Antigravity ставить його КОЖНІЙ написаній
   статті й вставці. Сімнадцять перевірок кажуть, що конвеєр свою частину зробив, — це не те
   саме, що «людина це читала». **У `done` переводить ЛЮДИНА (через `review-*`), а не батч.**
   `update`/`deeper` — так само чужа воля, тільки вже людська.
   Урваний батч лишає статтю в `pending`: фаза «Маніфест» просто не відпрацювала. Доти скрипт
   цього не розрізняв і на --apply переводив у `done` все, що лежить на диску, — тобто одним
   рухом видав би за прочитане людиною 2324 теми, які чекають саме на неї, і знищив би чергу
   ревізії. Тепер такі теми лише показуємо. */
const AWAITS_HUMAN = new Set(['recheck', 'update', 'deeper']);
const flaggedArticles = [];  // файл є, статус чекає людського ока → НЕ чіпаємо
const flaggedInserts = [];   // те саме для вставок
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
    if (onDisk && AWAITS_HUMAN.has(st)) { flaggedArticles.push({ slug: T.slug, ver, status: st }); units.push({ section: T.section, slug: T.slug, title: T.title || T.slug, level: ver }) }
    else if (onDisk && st !== 'done') { unregArticles.push({ section: T.section, slug: T.slug, ver, status: st }); units.push({ section: T.section, slug: T.slug, title: T.title || T.slug, level: ver }) }
    else if (onDisk && st === 'done') units.push({ section: T.section, slug: T.slug, title: T.title || T.slug, level: ver });
    else if (!onDisk && st === 'pending') missingArticles.push(T.section + '/' + T.slug + ' ' + ver);
  }

  // вставки, зареєстровані в маніфесті
  for (const k of TYPES) for (const i of (T.topic[k] || [])) {
    const onDisk = fs.existsSync(path.join(T.dir, i.file));
    if (!onDisk) missingInserts.push({ section: T.section, topicSlug: T.slug, topicTitle: T.title, file: i.file, type: k, why: 'у маніфесті, файла нема' });
    else if (AWAITS_HUMAN.has(i.status)) flaggedInserts.push({ topicSlug: T.slug, file: i.file, status: i.status });
    else if (i.status !== 'done') notDoneInserts.push({ section: T.section, topicSlug: T.slug, file: i.file, type: k, status: i.status });
  }
  // вставки, що лежать на диску, але в маніфесті їх нема
  // ⚠️ Стаття теми, чий slug сам починається з типу вставки (api-design → api-design-d.md),
  // під INS_RE підпадає. Тому власні файли статті виключаємо явно, інакше вони поїдуть у вставки.
  const ownFiles = new Set([T.slug + '.md', T.slug + '-d.md']);
  if (fs.existsSync(T.dir)) for (const f of fs.readdirSync(T.dir)) {
    /* Статус нової вставки беремо в її ТЕМИ. Урваний батч лишає тему в pending → стаття
       щойно стала done, отже й вставка done. А тема в `recheck` ще чекає людського ока —
       її вставка так само; зареєструвати вставку як done означало б видати за прочитане
       людиною те, чого людина не бачила. Беремо той самий статус, що в теми. */
    if (INS_RE.test(f) && !reg.has(f) && !ownFiles.has(f)) {
      const ownerSt = (T.topic.detailed && T.topic.detailed.status) || (T.topic.basic && T.topic.basic.status);
      unregInserts.push({ section: T.section, topicSlug: T.slug, topicTitle: T.title, file: f, type: f.split('-')[0],
                          asStatus: AWAITS_HUMAN.has(ownerSt) ? ownerSt : 'done' });
    }
  }
  // вставки, обіцяні в ПРОЗІ, але не написані (обидва формати лінка — §6 і відносний)
  for (const file of [T.slug + '.md', T.slug + '-d.md']) {
    const p = path.join(T.dir, file);
    if (!fs.existsSync(p)) continue;
    const txt = fs.readFileSync(p, 'utf8');
    const refs = new Set();
    // ⚠️ лише вставки ВЛАСНОЇ теми — звіряємо І КНИГУ, І слуг. Лінк на чужу вставку законний:
    // її файл лежить у теці тієї теми. Пастка: однакові слуги в різних книгах (тема «crc» є і в
    // programming, і в communications) — порівняння лише за слугом дає хибне «файла нема».
    // ⚠️ префікс лише `root:` — `book:`/`guide:` зняті ще при переході на єдину адресу, і доти
    // цей матчер не знаходив НІЧОГО: «обіцяні в прозі» завжди виходило 0.
    for (const m of txt.matchAll(/\]\(root:([a-z0-9-]+)\/([a-z0-9-]+)\/((?:hist|comp|math|proj|api)-[a-z0-9-]+\.md)\)/g)) {
      if (m[1] === BOOK && m[2] === T.slug) refs.add(m[3]);
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
line(`\n=== СТАН БАТЧУ: ${BOOK} ===`);
line(`  статті НА ДИСКУ, але не done у маніфесті: ${unregArticles.length}` + (unregArticles.length ? ' → ' + unregArticles.map((a) => a.slug + ':' + a.ver + '(' + a.status + ')').join(', ') : ''));
line(`  статті pending, файла НЕМА (ще писати):   ${missingArticles.length}` + (missingArticles.length ? ' → ' + missingArticles.slice(0, 12).join(', ') + (missingArticles.length > 12 ? ' …' : '') : ''));
line(`  вставки НА ДИСКУ, у маніфесті НЕМА:       ${unregInserts.length}` + (unregInserts.length ? ' → ' + unregInserts.map((i) => i.topicSlug + '/' + i.file).join(', ') : ''));
line(`  вставки в маніфесті зі статусом ≠ done:   ${notDoneInserts.length}`);
line(`  ── НЕ ЧІПАЮ (чекають людського ока) ──`);
line(`  статті recheck (Antigravity) / update / deeper:             ${flaggedArticles.length}` + (flaggedArticles.length ? ` (${[...new Set(flaggedArticles.map((a) => a.status))].join(', ')})` : ''));
line(`  вставки recheck (Antigravity) / update / deeper:            ${flaggedInserts.length}` + (flaggedInserts.length ? ` (${[...new Set(flaggedInserts.map((i) => i.status))].join(', ')})` : ''));
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

/* ── newTopics із журналу обірваного прогону ─────────────────────────────────────────────
   Коли стіна вбиває прогін до фази «Маніфест», гинуть не лише статуси, а й НОВІ ТЕМИ, що їх
   оголосили автори: кожна незаведена = битий лінк «теми нема в жодному маніфесті». Диск про них
   не знає — вони живуть тільки в journal.jsonl. Тому: --journal <шлях до journal.jsonl>. */
const ntJobs = new Map();
if (JOURNAL) {
  if (!fs.existsSync(JOURNAL)) { console.error('нема журналу: ' + JOURNAL); process.exit(1) }
  const res = fs.readFileSync(JOURNAL, 'utf8').trim().split('\n')
    .map((l) => { try { return JSON.parse(l) } catch (e) { return null } }).filter(Boolean)
    .filter((x) => x.type === 'result').map((x) => x.result).filter(Boolean);
  const seen = new Map();
  for (const r of res) for (const t of (r.newTopics || [])) {
    if (!t || !t.slug || !t.section) continue;
    const kind = t.kind || 'book', book = t.book || BOOK;
    seen.set(kind + '/' + book + '/' + t.slug, { kind, book, section: t.section, slug: t.slug, title: t.title || t.titleHint || t.slug });
  }
  let already = 0, noSection = 0;
  for (const t of seen.values()) {
    /* v7: ключ черги — СЛУГ книги, а не шлях. Доти тут будувався «<книга>/manifest.json»
       від кореня репо: такого файла в дереві root/ немає, тож existsSync падав і КОЖНА
       нова тема з журналу мовчки гинула — саме та, яку більше нізвідки не взяти. */
    const rel = t.book;
    const bd2 = M7.bookDirOf(rel);
    if (!bd2) { console.log('   ✖ нема книги «' + rel + '» у root/ → ' + t.slug); continue }
    const b2 = M7.loadBook(bd2);
    if (!b2) { console.log('   ✖ нема маніфесту книги «' + rel + '» → ' + t.slug); continue }
    if (M7.findTopic(b2, t.slug)) { already++; continue }
    if (!M7.groupSlugs(b2).has(t.section)) { console.log('   ⚠ нема групи «' + t.section + '» у «' + rel + '» → ' + t.slug + ' (пропускаю)'); noSection++; continue }
    if (!ntJobs.has(rel)) ntJobs.set(rel, []);
    ntJobs.get(rel).push({ op: 'topic', section: t.section, slug: t.slug, title: t.title });
  }
  const total = [...ntJobs.values()].reduce((s, v) => s + v.length, 0);
  console.log(`\n  НОВІ ТЕМИ з журналу: оголошено ${seen.size} · уже є ${already} · без галузі ${noSection} · ДО ЗАВЕДЕННЯ ${total}`);
  for (const [rel, ops2] of ntJobs) console.log('     ' + rel + ': ' + ops2.length + ' → ' + ops2.map((o) => o.section + '/' + o.slug).join(', '));
} else {
  console.log('\n  (нові теми не перевірялись — подай --journal <…\\journal.jsonl> обірваного прогону)');
}

if (!has('apply')) {
  line(`\n  Нічого не змінено. Щоб зареєструвати написане в маніфесті: додай --apply`);
  process.exit(0);
}

const ops = [];
for (const a of unregArticles) ops.push({ op: 'status', slug: a.slug, ver: a.ver, status: 'done' });
for (const i of unregInserts) ops.push({ op: 'insert', slug: i.topicSlug, section: i.section, type: i.type, file: i.file, status: i.asStatus || 'done' });
for (const i of notDoneInserts) ops.push({ op: 'insert', slug: i.topicSlug, section: i.section, type: i.type, file: i.file, status: 'done' });
// нові теми — окремими викликами патчера, бо вони можуть цілити в ЧУЖІ маніфести
for (const [rel, ops2] of ntJobs) {
  const f = path.join(OUTDIR, '_mfops-nt-' + rel + '.json');
  fs.writeFileSync(f, JSON.stringify(ops2, null, 1), 'utf8');
  const o = execFileSync(process.execPath, [path.join(ROOT, 'scripts', 'manifest-patch.js'), rel, '--ops', f], { cwd: ROOT, encoding: 'utf8' });
  line('  нові теми → ' + o.trim());
}

if (!ops.length) { line('\n  --apply: статусів/вставок міняти нічого — маніфест уже збігається з диском.'); process.exit(0) }

/* v7: пишемо самі через manifest7 — JSON редагується безпечно за побудовою. */
line(`\n  --apply: ${ops.length} операцій у ${path.relative(ROOT, MF)}`);
const rep = M7.applyOps(BOOKDIR, ops);
line(`  груп +${rep.group || 0} · розділів +${rep.chapter || 0} · тем +${rep.topic || 0} · статусів ${rep.status || 0} · вставок ${rep.insert || 0}`);
(rep.errors || []).forEach((e) => line('  ✖ ' + e));
