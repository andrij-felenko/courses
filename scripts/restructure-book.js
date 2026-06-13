export const meta = {
  name: 'restructure-book',
  description: 'Фаза B: винести модулі у per-module manifest.js — embedded М2–7 (topics[] зі вставками, як М1) і chemistry m1–6 (topics[] тем). Math/components робляться окремо механічно (split-modules.js).',
  phases: [
    { title: 'Збірка', detail: 'агент на модуль: читає legacy-дані (git HEAD) + _status.md → пише <module>/manifest.js' },
  ],
}

const ROOT = 'E:/develop/courses'

/* Модулі на винесення агентами (math/components — механічно, не тут). */
const ALL = [
  { book: 'embedded', type: 'textbook', n: 2, slug: 'block-2-components-analog' },
  { book: 'embedded', type: 'textbook', n: 3, slug: 'block-3-digital-processor' },
  { book: 'embedded', type: 'textbook', n: 4, slug: 'block-4-mcu-esp32' },
  { book: 'embedded', type: 'textbook', n: 5, slug: 'block-5-sensors-control' },
  { book: 'embedded', type: 'textbook', n: 6, slug: 'block-6-comms-radio' },
  { book: 'embedded', type: 'textbook', n: 7, slug: 'block-7-systems' },
  { book: 'chem', type: 'intro', n: 1, slug: 'm1-atoms' },
  { book: 'chem', type: 'intro', n: 2, slug: 'm2-bonds' },
  { book: 'chem', type: 'intro', n: 3, slug: 'm3-reactions' },
  { book: 'chem', type: 'intro', n: 4, slug: 'm4-inorganic' },
  { book: 'chem', type: 'intro', n: 5, slug: 'm5-organic' },
  { book: 'chem', type: 'intro', n: 6, slug: 'm6-counting' },
]

const CFG = {
  embedded: { legacy: 'manifest.js',      base: 'embedded',  scope: `${ROOT}/embedded/SYLLABUS.md` },
  chem:     { legacy: 'manifest-chem.js', base: 'chemistry', scope: `${ROOT}/chemistry/PLAN.md` },
}

/* args: { only:"embedded"|"chem" } або { book, n } для проби одного модуля */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) {} }
let queue = ALL
if (_a && _a.only) queue = queue.filter(m => m.book === _a.only)
if (_a && _a.book && _a.n) queue = queue.filter(m => m.book === _a.book && m.n === Number(_a.n))

const RET = {
  type: 'object', additionalProperties: false, required: ['ok', 'file'],
  properties: {
    ok: { type: 'boolean' }, file: { type: 'string' },
    chapters: { type: 'number' }, topics: { type: 'number' }, inserts: { type: 'number' },
    note: { type: 'string' },
  },
}

const STATUS_MAP = '🟢→done · ⬜→empty · 🟡→empty · 🔄→update · pending(у manifest)→empty'

function embeddedPrompt(m) {
  const file = `${ROOT}/embedded/${m.slug}/manifest.js`
  const status = `${ROOT}/embedded/${m.slug}/_status.md`
  return `Створи per-module маніфест \`${file}\` для Модуля ${m.n} книги embedded (нова архітектура). НЕ чіпай інші файли. Тільки читання джерел + Write цього одного файлу.

ФОРМАТ:
\`\`\`js
/* embedded/${m.slug}/manifest.js — per-module маніфест Модуля ${m.n}. Складає scripts/bookbuild.js
   (histories[]/extras[] ВИВОДЯТЬСЯ з topics[]). Нумерація — М.Р.Т. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: ${m.n}, slug: "${m.slug}", title: "<title модуля з manifest>",
  chapters: [
    { n: 1, title: "<title>", dir: "${m.slug}/<chSlug>", main: "<chSlug>.md", status: "done",
      scope: "<1 речення меж розділу зі SYLLABUS.md, якщо є>",
      topics: [
        { mrt: "${m.n}.1.1", title: "<назва теми>", status: "done" },
        // ... решта тем розділу в порядку М.Р.Т ...
        { kind: "hist", file: "hist-...md", at: "chapter", status: "done", title: "<коротко>" },
        { kind: "math", file: "math-...md", at: "${m.n}.1.2", status: "done", title: "<коротко>" }
        // ...
      ] }
    // ... розділи ...
  ]
});
\`\`\`

ДЖЕРЕЛА:
1. Виконай у теці ${ROOT}: \`git show HEAD:manifest.js\` — знайди обʼєкт модуля \`n: ${m.n}\` (slug "${m.slug}"). Звідти бери: title модуля; для КОЖНОГО розділу — n, title, dir, main, status і масиви histories[]/extras[] (це ТОЧНІ значення file вставок і їх ПОРЯДОК).
2. Прочитай \`${status}\` — рядки тем \`- 🟢 ${m.n}.Р.Т Назва\` (звідси mrt+title+status тем) і рядки вставок \`- 🟢 🧮 (до теми ${m.n}.Р.Т) Назва — \\\`файл.md\\\`\` / \`(до розділу)\` (звідси at + людська title вставки).
3. Прочитай \`${CFG.embedded.scope}\` — опис меж розділу (1–2 реч.) → chapter.scope.

КЛЮЧОВЕ правило порядку (інакше зламається рендер): bookbuild виводить histories[] = topics з kind:"hist" у порядку topics[]; extras[] = topics з kind comp/math/proj у порядку topics[]. Тому у topics[] кожного розділу:
- спершу всі ТЕМИ (mrt) у порядку М.Р.Т;
- далі hist-вставки — file і ПОРЯДОК точно як у оригінальному histories[];
- далі comp/math/proj-вставки — file і ПОРЯДОК точно як у оригінальному extras[].
kind за file: \`hist-*\`→hist, \`math-*\`→math, \`comp-*\`→comp, \`proj-*\`→proj; крос-шляхи \`../../../math/...\`→math, \`../../../components/...\`→comp. file ЗАВЖДИ з manifest (git show), НЕ зі _status.md (там можуть бути старі імена; at/title зіставляй за змістом).

СТАТУСИ: ${STATUS_MAP}. У manifest є розділи status:"pending" (ще не написані) — для них постав chapter.status:"empty", БЕЗ dir/main/histories/extras; topics[] = заплановані теми зі _status.md (⬜→empty) якщо є, інакше лише {n,title,status:"empty"}.

ПЕРЕВІРКА перед Write: для кожного DONE-розділу кількість і порядок hist-entries == оригінального histories[], comp/math/proj-entries == оригінального extras[]; \`node --check\` синтаксис OK. Поверни ok, file, chapters, topics (к-сть тем), inserts (к-сть вставок), note (чи збіглися довжини).`
}

function chemPrompt(m) {
  const file = `${ROOT}/chemistry/${m.slug}/manifest.js`
  const status = `${ROOT}/chemistry/${m.slug}/_status.md`
  return `Створи per-module маніфест \`${file}\` для Модуля ${m.n} книги «Хімія» (нова архітектура). НЕ чіпай інші файли. Тільки читання + Write цього файлу.

ФОРМАТ:
\`\`\`js
/* chemistry/${m.slug}/manifest.js — per-module маніфест Модуля ${m.n}. Складає scripts/bookbuild.js.
   Хімія: вставок нема (histories[]/extras[] порожні), є лише теми. */
(window.__MODREG__ = window.__MODREG__ || []).push({
  n: ${m.n}, slug: "${m.slug}", title: "<title модуля з manifest>",
  chapters: [
    { n: "1", title: "<title>", dir: "${m.slug}/<chSlug>", main: "<chSlug>.md", status: "done",
      scope: "<1 реч. меж розділу з PLAN.md, якщо є>",
      topics: [
        { mrt: "${m.n}.1.1", title: "<назва теми>", status: "done" },
        { mrt: "${m.n}.1.2", title: "<назва теми>", status: "done" }
      ] }
  ]
});
\`\`\`

ДЖЕРЕЛА:
1. \`git show HEAD:manifest-chem.js\` (у теці ${ROOT}) — обʼєкт модуля \`n: ${m.n}\` (slug "${m.slug}"): title модуля; для кожного розділу n, title, dir, main, status. Histories у «Хімії» порожні — extras/histories у per-module НЕ став (рушій виведе порожні).
2. \`${status}\` — рядки тем \`- 🟢 ${m.n}.Р.Т Назва\` (mrt+title+status). Зістав тему з розділом за М.Р: тема "${m.n}.2.3" → розділ n="2".
3. \`${CFG.chem.scope}\` — короткий опис меж розділу → chapter.scope (необовʼязково).

СТАТУСИ: ${STATUS_MAP}. Розділ status з manifest (pending→empty).
ПЕРЕВІРКА: \`node --check\` OK; кожна тема зі _status.md потрапила в правильний розділ. Поверни ok, file, chapters, topics, inserts:0, note.`
}

phase('Збірка')
log(`Винось ${queue.length} модулів: ${queue.map(m => m.book + '/' + m.slug).join(', ')}`)

const results = await pipeline(queue, (m) => {
  const prompt = m.type === 'textbook' ? embeddedPrompt(m) : chemPrompt(m)
  return agent(prompt, {
    label: `${m.book}:${m.slug}`,
    phase: 'Збірка',
    model: m.type === 'textbook' ? 'opus' : 'sonnet',   // embedded byte-match → Opus; chem простіше → Sonnet
    schema: RET,
  }).then(r => ({ ...m, ...(r || { ok: false }) }))
})

const ok = results.filter(r => r && r.ok)
const bad = results.filter(r => !r || !r.ok)
log(`\n═══ ПІДСУМОК ═══`)
log(`✅ Готово: ${ok.length}/${queue.length}`)
ok.forEach(r => log(`  ${r.book}/${r.slug}: розділів ${r.chapters}, тем ${r.topics}, вставок ${r.inserts}`))
if (bad.length) log(`❌ Невдало: ${bad.map(r => (r && r.book + '/' + r.slug) || '?').join(', ')}`)

return {
  done: ok.length, total: queue.length, failed: bad.length,
  files: ok.map(r => r.file),
  failedModules: bad.map(r => r && (r.book + '/' + r.slug)),
}
