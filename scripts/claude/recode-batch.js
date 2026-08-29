export const meta = {
  name: 'recode-batch',
  description: 'Переписати код як СПРАВЖНІ ПРОЄКТИ у файлах — прохід Claude по тому, що позначено `recode` (усе, що написав Antigravity з кодом) або ще лежить в огорожах. ФАЗИ: (1) Черга — ЛОКАЛЬНИЙ recode-queue.js складає файлову чергу (робота файлова, не темна: тека проєкту названа .md-носієм, а в 56% тем поруч живуть proj і api); (2) Проєкти — opus/high, ОДИН АГЕНТ НА ФАЙЛ: читають СВІЙ файл, наявний код і `_canon.md` книги; контекст теми (preknowlist + перший абзац) дає черга готовим зрізом, чужих статей агент НЕ відкриває — заміряно, що ціла стаття коштує 41 КБ і не дає нічого; виносять код у `<тема>/<ім_я .md без розширення>/<мова>/` звичною для мови розкладкою; РОЛЬ у промпті названа прямо — професіонал показує студентам, як воно працює, і пише при них: код робочий, з обробкою помилок і незручними випадками, але БЕЗ релізної обвязки (конфігурованість, шари «щоб потім підмінити», узагальнення на чужі випадки); у прозі лишається `:::code`. пишуть ТЕ, ПРО ЩО ФАЙЛ (предмет вставки вирішує вміст теки: про буфер — буфер, про збірку — CMakeLists, про тести — тести), без обвязки й без запуску на перевірку; розкладку вирішують одразу й кладуть файли ПАЧКАМИ (кілька Write в одному ході): по файлу за виклик це повний круг генерації на кожен файл — заміряно 29 файлів = 29 кругів; обсяг — мінімально зрозумілий корисний код, десятків файлів не пишемо; (3) Гейт — ЛОКАЛЬНИЙ recode-gate.js: код виїхав · кожна мова дотягла до підлоги свого рівня · є c/ → є cpp/; (4) Добір — opus лише там, де тонко, і ⛔ БЕЗ ЧИСЕЛ: «розшир код», а не «допиши N рядків»; до 2 кіл, далі до людини; (5) Маніфест — ЛОКАЛЬНИЙ manifest-patch знімає `recode` з тих, хто пройшов; (6) Контроль — 06-та по зачеплених теках, звіт. args = {book, limit?:12, fences?:false, units?, concurrency?:4, stagger?:2000, rounds?:2}',
  phases: [
    { title: 'Черга', detail: 'ЛОКАЛЬНО recode-queue.js --write: файли з recode (або --fences: код досі в огорожах), важчі першими; рівень з готових оцінок' },
    { title: 'Проєкти', detail: 'opus, один агент на ФАЙЛ: свій файл + наявний код + зріз контексту; код у теки мов розкладкою справжнього проєкту, :::code у прозі; пул 4, стагер 2с' },
    { title: 'Гейт', detail: 'ЛОКАЛЬНО recode-gate.js --json: виїхав · дотягнув · пара c/cpp' },
    { title: 'Добір', detail: 'opus лише по тонких мовах; ⛔ підлог і чисел агентові НЕ показуємо — «доведи механізм до робочого»; до rounds кіл' },
    { title: 'Маніфест', detail: 'ЛОКАЛЬНО: recode-gate.js --ops → manifest-patch.js знімає recode з готових' },
    { title: 'Контроль', detail: '06-size.js по зачеплених теках; лише звіт' },
  ],
}

/* ── args ─────────────────────────────────────────────────────────────────── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
const BOOK = _a && _a.book ? String(_a.book) : ''
if (!BOOK) throw new Error('args.book обовʼязковий')
const LIMIT = Number(_a && _a.limit) || 12
const FENCES = !!(_a && _a.fences)
const CONCURRENCY = Number(_a && _a.concurrency) || 4
const STAGGER = Number(_a && _a.stagger) || 2000
const ROUNDS = Number(_a && _a.rounds) || 2
const UNITS_IN = (_a && Array.isArray(_a.units)) ? _a.units : null

const ROOT = 'E:\\develop\\courses'
const QFILE = `scripts/_finish/_recode-${BOOK}.json`

/* ── стіна ліміту: не пересиджуємо, а прибиваємо прогін ───────────────────── */
let WALL = null
const ABORT_ON_LIMIT = !(_a && _a.abortOnLimit === false)
const PROBE_WAIT = 5 * 60 * 1000
const MAX_TRIES = 3
const RETRY_WAIT = 20 * 1000
const NULL_STREAK_LIMIT = 4
let _nullStreak = 0

async function callAgent(prompt, opts) {
  if (WALL) return null
  let tries = 0, limitWaits = 0
  while (true) {
    let r = null, err = null
    try { r = await agent(prompt, opts) } catch (e) { r = null; err = e }
    if (r != null) { _nullStreak = 0; return r }
    _nullStreak++
    const emsg = String((err && err.message) || err || '')
    const isLimit = (_nullStreak >= NULL_STREAK_LIMIT) || /session limit|usage limit|hit your|resets \d|quota|rate limit/i.test(emsg)
    if (isLimit && ABORT_ON_LIMIT) {
      if (limitWaits < 1) {
        limitWaits++
        log(`⏳ схоже на ліміт (${opts && opts.label}) — контрольна пауза 5 хв і ОДНА спроба`)
        await new Promise((res) => setTimeout(res, PROBE_WAIT))
        _nullStreak = 0
        continue
      }
      if (!WALL) { WALL = { label: (opts && opts.label) || '?' }; log(`⛔ СТІНА ЛІМІТУ на «${WALL.label}» — нові агенти не стартують, написане лишається на диску`) }
      return null
    }
    if (++tries >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді після ${MAX_TRIES} спроб`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}

/* Пул: щонайбільше CONCURRENCY одночасно. Під стіною цикл стікає, а не рветься —
   інакше масив лишався б рідким і фаза рапортувала б успіх там, де нічого не було. */
async function staggered(items, fn) {
  const results = new Array(items.length)
  let next = 0
  async function worker() {
    while (next < items.length) { const i = next++; results[i] = await fn(items[i], i) }
  }
  const n = Math.min(CONCURRENCY, items.length)
  const workers = []
  for (let k = 0; k < n; k++) {
    workers.push(worker())
    if (k < n - 1) await new Promise((r) => setTimeout(r, STAGGER))
  }
  await Promise.all(workers)
  return results
}

/* ── схеми ────────────────────────────────────────────────────────────────── */
const QUEUE_RET = { type: 'object', additionalProperties: false, required: ['units'], properties: {
  units: { type: 'array', items: { type: 'object', additionalProperties: true, required: ['dir', 'file', 'slug'], properties: {
    dir: { type: 'string' }, file: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' },
    role: { type: 'string' }, ver: { type: ['string', 'null'] }, type: { type: ['string', 'null'] },
    status: { type: 'string' }, why: { type: 'string' }, level: { type: ['number', 'null'] },
    langs: { type: 'array', items: { type: 'string' } }, fencedLines: { type: 'number' }, ctx: { type: 'string' },
    moved: { type: 'array', items: { type: 'string' } } } } } } }

const PROJ_RET = { type: 'object', additionalProperties: false, required: ['ok', 'file', 'langs'], properties: {
  ok: { type: 'boolean' }, file: { type: 'string' },
  langs: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['lang', 'files'], properties: {
    lang: { type: 'string' }, files: { type: 'number' }, note: { type: 'string' } } } },
  addedCpp: { type: 'boolean' }, inlineLeft: { type: 'number' }, notes: { type: 'string' } } }

const GATE_RET = { type: 'object', additionalProperties: true, required: ['total', 'ok', 'rows'], properties: {
  total: { type: 'number' }, ok: { type: 'number' },
  rows: { type: 'array', items: { type: 'object', additionalProperties: true } } } }

const CMD_RET = { type: 'object', additionalProperties: false, required: ['out'], properties: { out: { type: 'string' } } }

/* ── ФАЗА 1 — черга (локально) ────────────────────────────────────────────── */
phase('Черга')
let units = UNITS_IN
if (!units) {
  const q = await callAgent(
    `Виконай РІВНО ОДНУ команду Bash із теки ${ROOT} і поверни її результат:\n\n` +
    `node scripts/claude/recode-queue.js --book ${BOOK} --limit ${LIMIT}${FENCES ? ' --fences' : ''} --write\n\n` +
    `Потім прочитай ${QFILE} і поверни його вміст у полі units. Нічого не редагуй.`,
    { label: `черга:${BOOK}`, phase: 'Черга', model: 'sonnet', effort: 'low', schema: QUEUE_RET })
  units = (q && q.units) || []
}
if (!units.length) { log('черга порожня — переписувати нема чого'); return { book: BOOK, units: 0 } }
log(`черга: ${units.length} файлів · рядків коду в огорожах ${units.reduce((a, u) => a + (u.fencedLines || 0), 0)}`)

/* ── ФАЗА 2 — проєкти ─────────────────────────────────────────────────────── */
/* ⛔ Підлоги й рівень у промпт НЕ йдуть. Показане число стає ціллю — заміряно
   двічі, в обидва боки. Повноту тут задає не лічильник, а бриф: «реалізуй усе,
   що проза назвала механізмом». Рівень потрібен гейтові, не письменникові.      */
function projPrompt(u) {
  const base = u.file.replace(/\.md$/, '')
  return `Ти переписуєш КОД одного файла корпусу. Прозу не чіпаєш.

ФАЙЛ:  ${ROOT}\\${u.dir.replace(/\//g, '\\')}\\${u.file}
ТЕМА:  ${u.title || u.slug}   (роль файла: ${u.role})

ХТО ТИ Й ДЛЯ КОГО ПИШЕШ
Ти професіонал у цій справі й показуєш студентам, як воно працює насправді. Пишеш при
них, у темпі заняття: часу на вилизування немає — і саме тому виходить те, що треба.

Такий код працює **по-справжньому**: обробка помилок і незручні випадки в ньому Є, бо
професіонал інакше не пише — він знає, де воно ламається, і показує це студентам.
Програма МУСИТЬ працювати.

Але будується вона **не для користувачів і не для ринку**: без конфігурованості, без
шарів «щоб потім підмінити», без узагальнень на випадки, яких у темі немає, без обвʼязки
навколо. На занятті на це немає ні часу, ні причини — і саме звідси береться правильний
обсяг, а не з лічильника.

СКІЛЬКИ ПИСАТИ
Нам не треба багато. Треба **мінімально зрозумілий корисний код** — рівно той, що його
написав би працюючий професіонал, показуючи справу студентам. Перевантаження розміром
тут не чеснота, а вада: суть у тому, щоб у курсі показати, ЯК це роблять, а не здати
проєкт.

⛔ **Десятків файлів не пишемо.** Модулів стільки, скільки їх має сама річ, — а річ тут
навчальна й мала. Тягне завести ще один файл «щоб було правильно» — спитай, чи піде
студент його читати; ні — це не модуль, а звичка.

ЩО ПРОЧИТАТИ
1. **Сам файл — цілком.** Абзаци довкола кожного :::code кажуть, для чого саме цей код;
   це головне джерело розуміння, і воно вже в тебе під руками.
2. **Наявний код** у теці проєкту — кожен файл.
3. Якщо в теці КНИГИ є _canon.md — прочитай його ПЕРШИМ: додаткові правила саме цієї
   книги (наскрізний приклад, єдині терміни), і вони мають перевагу.

⛔ **Інших .md теми не відкривай.** Контекст теми даний нижче — цього досить. Заміряно
на живому прогоні: агент прочитав 134 КБ, з них 41 КБ детальної статті й 19 КБ сусідньої
вставки, і не використав із них майже нічого. Читання чужих статей не робить код кращим,
лише довшим і дорожчим.
${u.ctx ? `
КОНТЕКСТ ТЕМИ (усе, що треба знати понад свій файл)
${u.ctx}
` : ''}

КУДИ ЙДЕ КОД
Кожен блок від 10 рядків справжньою мовою виносиш у файли:

    ${u.dir}/${base}/<мова>/<файли>

Тека мови — КОРІНЬ ПРОЄКТУ. Усередині — звичайна для цієї мови розкладка, з підтеками
включно: rust/src/, go/internal/, пакет у Python, у C пари <модуль>.c + <модуль>.h.
Розбивай на модулі ТАК, ЯК РОЗБИВАЮТЬ У СПРАВЖНІХ ПРОЄКТАХ: звична розкладка читається
легше за одну купу. Але «як зазвичай» тут — про річ ТАКОГО ЖЕ розміру, тобто про малу
навчальну: кілька модулів, а не десятки. Один величезний main.c правильний лише там, де
справжній проєкт такого розміру був би одним файлом.

ПИШИ ТЕ, ПРО ЩО ФАЙЛ
**Предмет файла вирішує, що лежить у теці** — не уявлення про «повний репозиторій».
Про кільцевий буфер — кільцевий буфер; про систему збірки — CMakeLists.txt, бо він і є
предмет; про тести — тести; про тулчейн — тулчейн-файл; про діагностику в GDB — скрипт
GDB. Питання щоразу одне: **чи це те, заради чого файл написано?**

Решта — обв'язка, і її не пишуть. README не доречний ніколи: його роль виконує сама
стаття. Конфіги середовища (OpenOCD, .clang-format, CI) і скрипти відлагоджувача — лише
коли самі стали предметом. Файл збірки — лише коли без нього приклад не запускається
взагалі, і тоді він один і мінімальний. Кожен файл поза предметом розбавляє те, заради
чого читач відкрив статтю.

⛔ **Нічого не запускай і не збирай для перевірки.** Правильність тут судить читання й
гейт, а не компілятор: складання тулчейну коштує більше за всю роботу.

ЩО ЛИШАЄТЬСЯ В ПРОЗІ
На місці винесеного блоку постав :::code <шлях від теки теми>, наприклад
«:::code ${base}/c/main.c». Кілька мов — по одному :::code на вкладку :::tabs.
Фрагменти менші за 10 рядків лишаються в тексті як були: там вони пояснюють, а не працюють.

Наявні файли коду — **чернетка** механічного виносу: розкладка їх ЗАМІНЮЄ, а не сусідить
із ними. Коли ти закінчив, у теці не лишилося жодного чернеткового файла, а кожен :::code
вказує на файл, який справді є в остаточній розкладці.

ЯК ПИСАТИ
Спершу **виріши всю розкладку одразу**: які файли будуть, що в кожному лежить, як вони
сходяться. Тоді **клади їх ПАЧКАМИ — по кілька Write в ОДНОМУ ході**, а не по файлу за раз.

Це не дрібниця. Один файл за виклик означає повний круг генерації на КОЖЕН файл, і весь
контекст їде наново щоразу: заміряно на живому прогоні — 29 файлів дали 29 кругів і чверть
години на самий лише друк. Тими самими пачками це п'ять-шість ходів. Пиши разом усе, що
належить одному модулю чи одній теці, і не перерішуй розкладку між записами.

ГОЛОВНЕ ПРАВИЛО — ПОВНОТА
Код мусить реалізувати ВСЕ, що проза називає механізмом. Жодного «залишаємо читачеві»,
«за аналогією», «решта симетрично», жодної заглушки там, де текст пообіцяв поведінку.
Назвав механізм — він працює в коді. Наявний код в огорожах — це ЧЕРНЕТКА, а не зразок:
де він неповний або обірваний, доводь до робочого стану, а не переносиш як є.

МОВИ
Мови, які вже є в тексті, лишаються — вибір зроблено до тебе${u.langs && u.langs.length ? ` (тут: ${u.langs.join(', ')})` : ''}.
АЛЕ якщо є C і немає C++ — заведи теку cpp/: §5 вимагає пари. Переклад мусить бути
ІДІОМАТИЧНИМ: контейнер або std::unique_ptr замість malloc/free · RAII замість close(fd)
у гілках goto out · std::span і std::string_view замість char* із довжиною окремим
аргументом · виняток або std::expected замість -1 та errno · шаблон чи std::variant
замість void* із switch за тегом. C, у якому лише замінили printf на std::cout, ГІРШИЙ
за відсутню теку. Розкладка тек c/ і cpp/ НЕ мусить дзеркалитись — ідіоматичний C++
ділиться на модулі інакше, і однакові імена файлів були б ознакою поганого перекладу.
Скрипти (sh, sql, cmake) виносяться так само, але вони обвʼязка, а не предмет.

ЧОГО НЕ РОБИШ
· не чіпаєш manifest.json — узагалі, ніяк;
· не переписуєш прозу — лише код і ті місця, де він стояв;
· не скорочуєш текст;
· не вигадуєш інтерфейсів неіснуючих бібліотек: якщо файл документує чужий контракт,
  він має бути СПРАВЖНІМ.

Коментарі в коді — українською.

У відповідь: ok, file, langs (мова + скільки файлів написав + коротка нота), addedCpp
(чи довелося заводити пару C++), inlineLeft (скільки блоків лишив у прозі), notes.`
}

phase('Проєкти')
const done = await staggered(units, (u) =>
  callAgent(projPrompt(u), { label: `проєкт:${u.slug}/${u.file}`, phase: 'Проєкти', model: 'opus', effort: 'high', schema: PROJ_RET })
    .then((r) => r || { ok: false, file: u.file, langs: [], notes: 'агент не відповів' }))
log(`написано проєктів: ${done.filter((d) => d && d.ok).length} з ${units.length}` +
  (done.filter((d) => d && d.addedCpp).length ? ` · додано пар C++: ${done.filter((d) => d && d.addedCpp).length}` : ''))
if (WALL) { log('прогін зупинено стіною ліміту; підняти — recode-queue.js складе чергу наново'); return { book: BOOK, aborted: true, units: units.length } }

/* ── ФАЗИ 3–4 — гейт і добір (до ROUNDS кіл) ─────────────────────────────── */
let gate = null
for (let round = 1; round <= ROUNDS; round++) {
  phase('Гейт')
  gate = await callAgent(
    `Виконай РІВНО ОДНУ команду Bash із теки ${ROOT} і поверни її вивід як JSON:\n\n` +
    `node scripts/claude/recode-gate.js --batch ${QFILE} --json\n\n` +
    `Команда може завершитися кодом 1 — це нормально, означає «є не готові». Нічого не редагуй.`,
    { label: `гейт ${round}`, phase: 'Гейт', model: 'sonnet', effort: 'low', schema: GATE_RET })
  if (!gate) { log('гейт не відповів — далі не йдемо'); break }
  log(`гейт ${round}: готові ${gate.ok} з ${gate.total}`)
  const bad = (gate.rows || []).filter((r) => !r.ok)
  if (!bad.length || round === ROUNDS || WALL) break

  phase('Добір')
  await staggered(bad, (r) => {
    const base = r.file.replace(/\.md$/, '')
    const thin = (r.thin || []).map((t) => t.lang)
    const other = (r.problems || []).filter((p) => !/тонко/.test(p))
    return callAgent(
      `Проєкт цього файла ще не готовий. Доведи його.

ФАЙЛ:  ${ROOT}\\${r.dir.replace(/\//g, '\\')}\\${r.file}
ТЕКА ПРОЄКТУ: ${r.dir}/${base}/<мова>/

${other.length ? 'ЩО НЕ ТАК:\n' + other.map((p) => '· ' + p).join('\n') + '\n\n' : ''}${thin.length ? `ТОНКО В МОВАХ: ${thin.join(', ')}.

Причина «тонко» майже завжди одна: проза назвала механізм, а в коді на його місці
заглушка або згадка. Пройди прозу й доведи КОЖЕН названий механізм до робочого — так,
як показав би студентам професіонал: обробка помилок і незручні випадки, які він знає ·
те, що справді збирається й запускається · звична для мови розкладка · тести там, де
вони щось перевіряють. Обсяг береться звідси, а не з дописування обгорток довкола коду.

` : ''}Прозу не переписуєш, маніфест не чіпаєш. Коментарі — українською.

У відповідь: ok, file, langs, addedCpp, inlineLeft, notes.`,
      { label: `добір:${r.slug}/${r.file}`, phase: 'Добір', model: 'opus', effort: 'high', schema: PROJ_RET })
      .then((x) => x || { ok: false, file: r.file, langs: [], notes: 'агент не відповів' })
  })
}

/* ── ФАЗА 5 — маніфест (локально) ────────────────────────────────────────── */
phase('Маніфест')
const okCount = gate ? gate.ok : 0
if (okCount > 0) {
  const mf = await callAgent(
    `Виконай ДВІ команди Bash із теки ${ROOT}, по черзі, і поверни вивід другої:\n\n` +
    `1) node scripts/claude/recode-gate.js --batch ${QFILE} --ops > scripts/_finish/_recode-ops-${BOOK}.json\n` +
    `2) node scripts/manifest-patch.js --book ${BOOK} --ops scripts/_finish/_recode-ops-${BOOK}.json\n\n` +
    `Маніфест НЕ читай і НЕ редагуй руками — його пише лише manifest-patch.js.`,
    { label: 'маніфест', phase: 'Маніфест', model: 'sonnet', effort: 'low', schema: CMD_RET })
  if (mf) log('recode знято з готових: ' + String(mf.out).split('\n').filter((l) => /статусів|вставок|✖/.test(l)).join(' | '))
} else log('знімати recode нема з кого — жоден файл не пройшов гейт')

/* ── ФАЗА 6 — контроль ───────────────────────────────────────────────────── */
phase('Контроль')
const dirsTouched = [...new Set(units.map((u) => u.dir))]
const ctrl = await callAgent(
  `Виконай із теки ${ROOT} по одній команді на теку й поверни СТИСЛИЙ звіт (лише рядки з ✖ і ▽):\n\n` +
  dirsTouched.map((d) => `node scripts/checks/06-size.js "${d}"`).join('\n') +
  `\n\nНічого не виправляй — тільки перелічи, де ще є дефекти обсягу чи коду.`,
  { label: 'контроль', phase: 'Контроль', model: 'sonnet', effort: 'low', schema: CMD_RET })
if (ctrl) log('контроль: ' + String(ctrl.out).slice(0, 1200))

return {
  book: BOOK,
  units: units.length,
  written: done.filter((d) => d && d.ok).length,
  gateOk: okCount,
  gateTotal: gate ? gate.total : 0,
  aborted: !!WALL,
}
