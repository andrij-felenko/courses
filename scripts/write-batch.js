export const meta = {
  name: 'write-batch',
  description: 'Повний v6-батч в один прогін. ФАЗИ: (1) Скаут — набрати батч на LIMIT тем: СПЕРШУ detailed-pending, далі basic-pending добиває решту (кожна тема несе свій рівень; явний level примушує один рівень); (2) Статті — opus-max агенти (стагер 2с), кожен пише ОДНУ статтю (проза+фігури+ref-лінки на свої вставки й нові залежні теми), лінки генерує в прозі, а вміст вставок НЕ пише — лише повертає їх список; (3) Вставки — opus-max агенти (стагер 2с) пишуть зібрані вставки під ці статті; (4) Фігури — sonnet-high агенти (стагер 2с) доводять SVG кожної написаної теки до «із зауваженнями: 0» (svgcheck: замалий шрифт + накладання тексту), правлячи figs.py; автори SVG самі НЕ гейтять; (5) Маніфест — серійно: статті→done, вставки→done, нові теми→pending. Жоден письменник маніфест НЕ чіпає. Усі фази письма — пулом щонайбільше CONCURRENCY(=4) агентів ОДНОЧАСНО (проти масових падінь на лімітах: валить макс. стільки, не весь фронт). args = {book, kind?:"book"|"catalog"|"guide", level?:"basic"|"detailed" (пропусти → мішаний detailed-first), limit?:10, scope?, stagger?, concurrency?, units?}',
  phases: [
    { title: 'Скаут', detail: 'набрати LIMIT: detailed-pending, тоді basic добиває (sonnet, grep)' },
    { title: 'Статті', detail: 'opus-max: одна стаття на агента + список своїх вставок і нових тем; пул 4, стагер 2с' },
    { title: 'Вставки', detail: 'opus-max: написати зібрані вставки під ці статті; пул 4, стагер 2с' },
    { title: 'Фігури', detail: 'sonnet-high: svg-гейт — svgcheck до «0» (шрифт+накладання), правка figs.py; пул 4, стагер 2с' },
    { title: 'Маніфест', detail: 'серійно: статті→done, вставки→done, нові теми→pending, детальні→pending' },
    { title: 'Контроль', detail: 'wordcount.js (§3-обсяг) + svgcheck.py по написаних теках; лише звіт, non-fatal' },
  ],
}

/* ── args ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
const BOOK = _a && _a.book ? String(_a.book) : ''
const KIND = (_a && _a.kind) || 'book'             // book | catalog | guide
const SELF = KIND === 'guide' ? 'guide' : 'book'   // префікс лінка на ВЛАСНУ книгу/курс (§6: ціль у курсі → guide:)
// Рівень версій. ДЕФОЛТ — МІШАНИЙ батч: спершу добираємо detailed-pending, тоді basic-pending добиває
// решту до LIMIT (детальна — ОСНОВНА версія §3: <slug>-d.md; базова <slug>.md лишається великим хвостом).
// Явний level:"detailed"|"basic" ПРИМУШУЄ одно-рівневий батч (стара поведінка). Кожна тема несе СВІЙ u.level.
const FORCE_LEVEL = (_a && (_a.level === 'basic' || _a.level === 'detailed')) ? _a.level : ''
const SCOUT_LEVELS = FORCE_LEVEL ? [FORCE_LEVEL] : ['detailed', 'basic']   // порядок пріоритету добору
const DEFAULT_LEVEL = FORCE_LEVEL || 'detailed'    // рівень для інлайн-units без явного level
const SCOPE = (_a && _a.scope) || ''
const STAGGER = Number(_a && _a.stagger) || 2000   // мс між стартами агентів (рознести хвилю)
const CONCURRENCY = Number(_a && _a.concurrency) || 4  // МАКС агентів ОДНОЧАСНО (пул): при вичерпанні лімітів падає щонайбільше стільки, не весь фронт. 4 → у польоті фактично 3–4 (провал на старті/передачі)
const LIMIT = Number(_a && _a.limit) || 10
const UNITS_IN = (_a && Array.isArray(_a.units)) ? _a.units.filter((u) => u && u.slug && u.section) : null
if (!BOOK) throw new Error('args.book обовʼязковий')

/* ── РЕЖИМ ДОРОБКИ (resume) — коли статті ВЖЕ написані на диску, а батч урвався на пізніших фазах.
   skipArticles: true → пропустити фазу «Статті» ЦІЛКОМ (нічого не переписуємо);
                 ["slug",…] → пропустити САМЕ ці теми (їхні статті вже на диску), а решту units — писати
                 як звичайно. Так один прогін закриває книгу, де частину статей батч устиг, а частину ні.
   Те, що мали б повернути вбиті агенти, подаємо готовим у args: inserts[] (з прози/журналу), newTopics[],
   detailed[] — воно ДОДАЄТЬСЯ до того, що повернуть агенти дописаних статей.
   Без цих args поведінка скрипта — стара, без змін. */
const _sa = _a && _a.skipArticles
const SKIP_LIST = Array.isArray(_sa) ? _sa.filter(Boolean).map(String) : null
const SKIP_ALL = _sa === true
const SKIP_ARTICLES = SKIP_ALL || !!(SKIP_LIST && SKIP_LIST.length)
const SKIP_SET = new Set(SKIP_LIST || [])
const INSERTS_IN = (_a && Array.isArray(_a.inserts)) ? _a.inserts.filter((i) => i && i.file && i.topicSlug && i.section) : null
const NEWTOPICS_IN = (_a && Array.isArray(_a.newTopics)) ? _a.newTopics.filter((t) => t && t.slug) : null
const DETAILED_IN = (_a && Array.isArray(_a.detailed)) ? _a.detailed.filter((d) => d && d.slug) : null
// insertsDone — вставки, ВЖЕ написані на диску попереднім (урваним) прогоном: писати НЕ треба,
// але зареєструвати в маніфесті ТРЕБА. Інакше свіжий батч зареєструє лише ті, що написав сам.
const INSERTS_DONE_IN = (_a && Array.isArray(_a.insertsDone)) ? _a.insertsDone.filter((i) => i && i.file && i.topicSlug && i.section) : null
// briefFile — JSON із повними брифами вставок (щоб не гнати кілобайти через args):
// { inserts:[{ topicSlug, file, brief }] }. Агент-письменник вставки бере свій бриф ЗВІДТИ.
const BRIEF_FILE = (_a && _a.briefFile) ? String(_a.briefFile) : ''
if (SKIP_ARTICLES && !UNITS_IN) throw new Error('skipArticles потребує args.units (теми, чиї статті вже на диску)')

const ROOT = 'E:\\develop\\courses'
const MF = `${KIND}/${BOOK}/manifest.js`
const MFWIN = `${ROOT}\\${MF.replace(/\//g, '\\')}`
const MAX_TRIES = 30, RETRY_WAIT = 60000
const SVG_TRIES = 6                                 // максимум ітерацій svg-гейта на теку (фаза Фігури)
const LIMIT_WAIT = 10 * 60 * 1000, LIMIT_MAX = 48   // ліміт сесії: спати 10 хв і повторювати (до ~8 год) — пауза до ресету, не фейл

// опційні правила книги/курсу/каталогу: якщо у корені є _canon.md — читаємо ПЕРШОЮ дією й тримаємось (перевага над загальним)
const RULESNOTE = `\n\n📕 ADDITIONAL RULES for this ${KIND === 'guide' ? 'course' : KIND === 'catalog' ? 'catalog book' : 'book'} (optional). AS YOUR FIRST ACTION, Bash-check whether the file ${ROOT}\\${KIND}\\${BOOK}\\_canon.md exists. IF IT DOES — READ it IN FULL and follow it strictly: these are rules specific to «${BOOK}» on top of the general canon (a running example, unified terms and names, the language of examples, stylistic conventions); where _canon refines the general rule — _canon WINS. IF the file is ABSENT — there are no additional rules for this book, write by the general canon.`

/* ── Канон письма (загальні правила; повне — AUTHORING.md) ── */
const CANON = `WRITING CANON (condensed; full — ${ROOT}\\AUTHORING.en.md). ⚠️ OUTPUT LANGUAGE: the article/insert prose is written in UKRAINIAN — the rules below are in English, the text you produce is Ukrainian (see «Living Ukrainian»).
• Feynman method: deep, from first causes; intuition and «WHY» → details; give motivation whenever there is even a slight need. Build the conclusion before the reader's eyes. Analogies precise + where they break. Cause-and-effect chains, not lists. Respect the reader's intelligence — no «as if for toddlers», no pathos. Do NOT meta-comment the style (don't explain in the text WHY you write this way) — just write in it.
• CONTINUITY AND CLARITY (§4): each link reachable from the previous in ONE step (a skipped «obvious» step is a hole the reader falls through); NECESSITY BEFORE STATEMENT — lead from the problem/cause so it could not be otherwise; EXAMPLE ILLUSTRATES, doesn't carry (remove the code — the «why» remains); ONE LINE — depth goes DEEP, a neighbouring concept = sentence+link, not a section; NO FILLER — every sentence about the SUBJECT, not about the text/its depth/honesty/route; no closing recap. SENTENCE CLARITY: one thought per sentence, don't nest clauses; name a term AFTER its mechanism, not before; symmetric things in parallel structure.
• Living Ukrainian (the prose OUTPUT is Ukrainian): real words only, no russicisms/calques/officialese/random synonymy; one term per concept. Source of the name in parentheses at first encounter: «атом (гр. átomos — неподільний)».
• Flow: each paragraph a bridge from the previous; through-line why→intuition→details→example; before the end reread as a whole and smooth the seams.
• Formulas — Unicode in code blocks (10⁻⁹, ε, ≈, ², ₀, ·), no LaTeX; decimal separator — dot (3.3). Worked example: bold condition-caption → code block with step-by-step computation → conclusion. CODE — real and correct, not pseudocode.
• CODE LANGUAGE — BY DOMAIN, not always C/C++: embedded/hardware/registers/hot-path → C/C++; general/web/backend/architecture → stack languages (TS/JS, Python, Go, Rust, Java…). LANGUAGE CHOICE — WEIGHTED SCORE: score EACH candidate language 0–10 for fitness FOR THIS example FROM ALL ANGLES (expressiveness, idiomaticity AND **efficiency/speed/memory** for this task) — NOT by language popularity: where the example is about performance, memory, systems level, parallelism or the hot path — performance languages (C/C++/Rust/Go/Zig) take a HIGHER raw score, even if TS/Python are more popular for general code; where the example is about domain expressiveness/DTO/script — the opposite. Multiply by a coefficient (C++ and TypeScript — ×1.5; other languages — ×1), write those whose product >5. E.g.: C++ raw 4 → 4·1.5=6 (WRITE); Python 4 → 4 (no). Several that pass the threshold — as TABS «:::tabs» (switcher on top; EACH tab an IDIOMATIC equivalent, NOT transliteration); a single one — an ordinary code block with the language in the fence (highlighting). C++/TS appear more often, but ONLY where they fit — a low raw score won't be saved by ×1.5 (we don't write registers in Python). Domain-locked code (registers, syscalls) — one language. In programming/algorithms: non-web proj (algorithm/data structure/systems/computation/performance/memory/parallelism) — C or C++ is MANDATORY (main language or one of the :::tabs tabs); the only exception is PURELY client-side frontend.
• Near an important concept — a box «> 🔧 **Навіщо це.**» (on the material of this topic).
• FIGURES: SVG only, pure Python without dependencies; figs.py IN THE TOPIC FOLDER, output ./img/. At the start of figs.py: «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *». Text frames — ONLY via textbox()/fitbox(). SPARINGLY 2–5, each carries weight; CHECK that figs.py runs FAST (doesn't loop). Embedding «![desc](/${KIND}/${BOOK}/<section>/<slug>/img/<file>.svg)» — from repo root (with /); caption in italics WITHOUT a number and «Рис.». RUN figs.py (from the topic folder) so the SVGs appear in ./img/. Lay out captions with MARGIN (wider columns/cells, larger viewBox), don't cram long lines side by side, route lines past labels — so there are no overlaps or tiny fonts. ⚠️ The FINAL svg-gate (svgcheck.py to «із зауваженнями: 0», v6 catches both tiny font and text OVERLAP on text/lines) is done by a SEPARATE pipeline step on Sonnet-high — you yourself do NOT need to run svgcheck and drive it to 0; your job is meaningful figures and a tidy layout with margin.
• FACTS: any historical/factual statement (date, name, «who was first», invention, patent, origin) — WEB-VERIFY RIGHT HERE (WebSearch/WebFetch); mark the evidential status. Don't stick the label «Russian» when sources give something more precise (Ukrainian, Pole, Serb, Jew, Georgian, Armenian, Balt…); distinguish idea/theory/implementation/system/patent.
• CROSS-LINKS — ONLY to real dependencies (not every mention!): a short 1–7 sentence recap «what to know» + ref-popup. DEFAULT is the general 2-segment link → book:<book>/<slug> (the renderer opens the basic, or the detailed if no basic) — use it almost always; a course target → guide:<course>/<slug>. No section in the link. EXPLICIT detailed = 3rd segment «/detail» (RARE — mainly a ref FROM A COURSE wanting the full version); an INSERT = 3rd segment «<type>-<name>.md» (WITH «.md»). Do NOT rewrite the whole target.
• NAMING slug-only; insert — <type>-<name>.md (type ∈ hist/comp/math/proj/api); an insert file starts with H1 (may use an emoji «# 📜 …»), and the title + first sentence THEMSELVES say what it is and why.
• LANGUAGE FINAL ON FIRST PASS — there will be no separate proofreading.${RULESNOTE}`

const KINDNOTE = KIND === 'guide'
  ? `\n\n⚠️ THIS IS A COURSE (guide), NOT a book-atom. A course article is CUMULATIVE — it BUILDS ON the steps already passed, ASSUMES what is already known, gradually DEEPENS. Sequence phrases («as we saw», «in the previous step», «we'll see later») are APPROPRIATE; lead the thread naturally (rely ONLY on what came before), without forcing. Needed book-topics EMBED as a popup (ref to book:), don't rewrite. Link the course's own topics/inserts as guide:<course>/...`
  : `\n\nThis is a book-atom: a SELF-CONTAINED article, WITHOUT numbering and WITHOUT sequence phrases («previous/next section», «as we saw», «we'll see later») — there is no order in the book. In general: a specific part/number only as an example-mention with a link (catalog/comp-), don't build the article on it.`

// додатковий нахил для книг про код: поряд з історією не забувай proj/math (алгоритм/код)
const INSERT_BIAS = (BOOK === 'programming' || BOOK === 'algorithms')
  ? `\n • (a book about ${BOOK === 'algorithms' ? 'algorithms' : 'programming'}) Keep history where it teaches. When the topic is algorithmic/structural/systems, weigh a proj (working code with a step-by-step breakdown and complexity) — it is the core of the book: if the code really exists, put it in an insert, don't leave it only in the prose. CODE LANGUAGE — by domain (§5): non-web proj → C/C++ MANDATORY (main or a tab); a general algorithm for a broad audience — 2–5 languages as «:::tabs» tabs. Add a MATH insert ONLY when the topic cannot be understood without the apparatus (proof/derivation/O(…) analysis) — and then PURELY mathematics (not a conceptual essay; explaining a separate concept → a new article, not a math insert). All by context, NOT for the sake of count.`
  : ''

/* ── helpers ── */
// Детектор ліміту БЕЗ тексту помилки. Пастка: при вичерпаному ліміті agent() НЕ кидає помилку —
// він тихо повертає null. Тоді err порожній, реджекс нижче не спрацьовує, і замість паузи скрипт
// молотить MAX_TRIES×RETRY_WAIT на КОЖНОМУ агенті пулу (2026-07-17: 312 svg-агентів замість 13).
// Тому: рахуємо ПОСПІЛЬ-нулі по всьому пулу. Кілька підряд = це не «агент не впорався», це стіна.
let _nullStreak = 0
const NULL_STREAK_LIMIT = 4          // < пулу, щоб зловити стіну раніше, ніж її вдарить увесь фронт
async function callAgent(prompt, opts) {
  let tries = 0, limitWaits = 0
  while (true) {
    let r = null, err = null
    try { r = await agent(prompt, opts) } catch (e) { r = null; err = e }
    if (r != null) { _nullStreak = 0; return r }
    _nullStreak++
    const isLimit = (_nullStreak >= NULL_STREAK_LIMIT) ||
      (err && /session limit|usage limit|hit your|resets \d|quota|rate limit/i.test(String((err && err.message) || err)))
    if (isLimit) {                                   // ліміт сесії: пауза до відновлення, не молотити й не кидати
      if (limitWaits >= LIMIT_MAX) { log(`⛔ ліміт не відпустив за ${LIMIT_MAX} спроб (${opts && opts.label})`); return null }
      limitWaits++
      log(`⏳ ЛІМІТ СЕСІЇ — чекаю ${LIMIT_WAIT / 60000} хв до відновлення й повторю [${limitWaits}/${LIMIT_MAX}] (${opts && opts.label})`)
      await new Promise((res) => setTimeout(res, LIMIT_WAIT))
      _nullStreak = 0   // після паузи — з чистого аркуша: інакше ОДИН справді зламаний агент (завжди null)
      continue          // сидітиме в лімітній гілці 8 год замість чесних MAX_TRIES×RETRY_WAIT
    }
    tries++
    if (tries >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді після ${MAX_TRIES} спроб`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}
// Пул конкурентності: щонайбільше CONCURRENCY викликів fn ОДНОЧАСНО (щоб при вичерпанні лімітів
// падало щонайбільше стільки агентів, а не весь фронт). Воркери стартують зі стагером STAGGER;
// звільнившись, воркер бере наступний елемент. Результати повертаються В ПОРЯДКУ items.
async function staggered(items, fn) {
  const results = new Array(items.length)
  let next = 0
  async function worker() {
    while (next < items.length) {
      const i = next++                              // JS однопотоковий — інкремент атомарний
      results[i] = await fn(items[i], i)
    }
  }
  const n = Math.min(CONCURRENCY, items.length)
  const workers = []
  for (let k = 0; k < n; k++) {
    workers.push(worker())
    if (k < n - 1) await new Promise((r) => setTimeout(r, STAGGER))   // рознести старти воркерів
  }
  await Promise.all(workers)
  return results
}
function topicDirWin(section, slug) { return `${ROOT}\\${KIND}\\${BOOK}\\${section}\\${slug}` }

/* ── схеми ── */
const UNITS = { type: 'object', additionalProperties: false, required: ['units'], properties: { units: { type: 'array', items: {
  type: 'object', additionalProperties: false, required: ['section', 'slug', 'title', 'level'],
  properties: { section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, scope: { type: 'string' }, level: { type: 'string', enum: ['basic', 'detailed'] } } } } } }
const ART_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: {
  ok: { type: 'boolean' }, files: { type: 'array', items: { type: 'string' } }, note: { type: 'string' },
  inserts: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'type', 'brief'], properties: { file: { type: 'string' }, type: { type: 'string' }, brief: { type: 'string' } } } },
  newTopics: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['kind', 'book', 'section', 'slug', 'title'], properties: { kind: { type: 'string' }, book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, needDetailed: { type: 'boolean' } } } },
  needDetailedSelf: { type: 'boolean' },
  deeperTargets: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['book', 'slug'], properties: { book: { type: 'string' }, slug: { type: 'string' } } } } } }
// newTopics і у вставці: вона лінкує за тим самим §6, отже так само може спертися на тему, якої ще
// нема. Без цього поля оголосити її не було чим — ref у прозі є, теми в маніфесті нема, лінк битий.
const INS_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, file: { type: 'string' }, note: { type: 'string' }, newTopics: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['kind', 'book', 'section', 'slug', 'title'], properties: { kind: { type: 'string' }, book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, needDetailed: { type: 'boolean' } } } } } }
const REG_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } }
const CTRL_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, problems: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'issue'], properties: { file: { type: 'string' }, issue: { type: 'string' } } } } } }

/* ──────────────── ФАЗА 1 — СКАУТ ──────────────── */
// Мішаний добір: скаут повертає до LIMIT кандидатів НА КОЖНУ версію з SCOUT_LEVELS (кожен тег level),
// а скрипт складає чергу за пріоритетом (detailed → basic), добиваючи до LIMIT і не дублюючи теми.
let WORK = []
if (UNITS_IN) {
  WORK = UNITS_IN.slice(0, LIMIT).map((u) => ({ ...u, level: (u.level === 'basic' || u.level === 'detailed') ? u.level : DEFAULT_LEVEL }))
  log(`Скаут (інлайн): ${WORK.length} тем (детальних ${WORK.filter((u) => u.level === 'detailed').length}, базових ${WORK.filter((u) => u.level === 'basic').length})`)
} else {
  phase('Скаут')
  const levelsDesc = SCOUT_LEVELS.join(' → ')
  const scout = await callAgent(
    `Знайди pending-теми на письмо в маніфесті ${MFWIN}. Потрібні ВЕРСІЇ в порядку пріоритету: ${levelsDesc}.
Схема: book/catalog — sections[]→topics[]; guide (v6) — modules[]→chapters[]→steps[]. В ОБОХ формах рядок секції/модуля містить "scope:", а тема/крок — { slug, title, basic:{status}, detailed:{status} } одним рядком; для guide поверни section = slug МОДУЛЯ. КРОК-ref (без slug) — ПРОПУСКАЙ.
ШВИДКО (не вантаж весь файл у відповідь): зроби Bash «grep -n» по файлу. Окремо витягни рядки секцій/модулів (містять "scope:"). Для КОЖНОЇ потрібної версії окремо знайди рядки тем, де САМЕ ЦЯ версія має status "pending" АБО "update" (обидва — черга на письмо цієї версії; НЕ бери "done"/"empty"/"deeper"/"recheck"): для detailed шукай 'detailed: { status: "pending" }' і 'detailed: { status: "update" }'; для basic — 'basic: { status: "pending" }' і 'basic: { status: "update" }'. Візьми ПЕРШІ ${LIMIT} таких тем У ПОРЯДКУ файлу НА КОЖНУ версію.
Для кожної теми визнач секцію (найближчий вищий рядок із "scope:"), витягни slug+title з її рядка, scope — з рядка секції, і ОБОВʼЯЗКОВО постав level = версія, за якою її знайдено ("detailed" чи "basic").
Поверни units:[{section, slug, title, scope, level}] — спершу всі знайдені detailed (до ${LIMIT}), тоді всі basic (до ${LIMIT}); скрипт сам обмежить сумарно до ${LIMIT}. Якщо якоїсь версії нема в черзі — просто не додавай її тем.`,
    { label: 'скаут', phase: 'Скаут', model: 'sonnet', schema: UNITS })
  const cand = ((scout && scout.units) || [])
    .filter((u) => u && u.slug && u.section)
    .map((u) => ({ ...u, level: (u.level === 'basic' || u.level === 'detailed') ? u.level : DEFAULT_LEVEL }))
  // складання за пріоритетом SCOUT_LEVELS; дедуп по section/slug (тема з обома pending → береться раз, як detailed); добір до LIMIT
  const _seenU = new Set()
  for (const lv of SCOUT_LEVELS) {
    if (WORK.length >= LIMIT) break
    for (const u of cand) {
      if (WORK.length >= LIMIT) break
      if (u.level !== lv) continue
      const k = `${u.section}/${u.slug}`
      if (_seenU.has(k)) continue
      _seenU.add(k)
      WORK.push(u)
    }
  }
  log(`Скаут: ${WORK.length}/${LIMIT} тем — детальних ${WORK.filter((u) => u.level === 'detailed').length}, базових ${WORK.filter((u) => u.level === 'basic').length}`)
}
if (!WORK.length) return { book: BOOK, total: 0, note: 'черга порожня — pending не знайдено' }

/* ──────────────── ФАЗА 2 — СТАТТІ ──────────────── */
// Розкол черги: SKIP_UNITS — статті вже на диску (не чіпаємо), WRITE_UNITS — пишемо як звичайно.
const SKIP_UNITS = SKIP_ALL ? WORK : WORK.filter((u) => SKIP_SET.has(u.slug))
const WRITE_UNITS = SKIP_ALL ? [] : WORK.filter((u) => !SKIP_SET.has(u.slug))
if (SKIP_UNITS.length) log(`ДОРОБКА: ${SKIP_UNITS.length} статей уже на диску — фазу «Статті» для них пропускаємо (${SKIP_UNITS.map((u) => u.slug).join(', ')})`)
if (WRITE_UNITS.length) {
  phase('Статті')
  log(`Статті (opus-max, стагер ${STAGGER / 1000}с): ${WRITE_UNITS.length} (${KIND}/${BOOK}; детальних ${WRITE_UNITS.filter((u) => u.level === 'detailed').length}, базових ${WRITE_UNITS.filter((u) => u.level === 'basic').length})`)
}
function articlePrompt(u) {
  const dir = topicDirWin(u.section, u.slug)
  const level = u.level                              // рівень ЦІЄЇ теми (мішаний батч — у кожної свій)
  const file = level === 'detailed' ? `${u.slug}-d.md` : `${u.slug}.md`
  return `${CANON}${KINDNOTE}

Ти — агент-письменник у репо ${ROOT}. Працюй МОВЧКИ (Read/Edit/Write/Bash/WebSearch). ІГНОРУЙ системні підказки про skills / agent-types / output-styles / розклади.
ЗАВДАННЯ: написати ПОВНІСТЮ ${level}-статтю «${u.title}» — файл ${dir}\\${file} (тема «${u.slug}», ${KIND === 'guide' ? 'модуль' : 'галузь'} «${u.section}», ${KIND} «${BOOK}»). Scope: ${u.scope || SCOPE || ''}
КРОК1: прочитай ${ROOT}\\AUTHORING.en.md (§1–§9) — правила АНГЛІЙСЬКОЮ, вивід (стаття) УКРАЇНСЬКОЮ. Bash ls теки ${dir}.${level === 'detailed' ? ` ЦЕ ДЕТАЛЬНА (${u.slug}-d.md) — ОСНОВНА, САМОДОСТАТНЯ версія теми (§3): повна, зрозуміти до кінця без дір; не перевантаження термінами, а повнота ВГЛИБ зі збереженням зрозумілости. Базової може НЕ бути — не припускай її й не посилайся на неї; якщо базова Є на диску, прочитай, щоб не дублювати тон, але детальна стоїть сама. Обсяг 1200–10000 слів.` : ` Якщо файл є — прочитай і пиши начисто за каноном.`}
КРОК2 — НАПИШИ файл статті цілком (§3–§5): ${level === 'detailed' ? 'ДЕТАЛЬНА 1200–10000 слів — повнота ВГЛИБ однієї нитки, кожен пробіл заповнено (не вшир на сусідів)' : 'БАЗОВА 600–1600 слів — швидкий атом: один стрижень, без другого шару'}; Фейнман; безперервність (без пробілів); необхідність перед твердженням; приклад ілюструє, не несе; жива українська; worked-приклади мовою за доменом (§5, НЕ завжди C/C++; у programming/algorithms не-веб proj → C/C++ обовʼязковий); рамки 🔧; етимологія в дужках; свої фігури (figs.py у теці, ЗАПУСТИ його — SVG в img/; акуратна розкладка з запасом; svg-гейт до «0» зробить ОКРЕМИЙ крок конвеєра на Sonnet-high, тобі svgcheck ганяти НЕ треба); факти — веб-звір (§7).
 • **(v6) БЛОК «ПЕРЕД ЧИТАННЯМ».** Одразу ПІД H1 постав згорнутий блок \`<preknowlist>…</preknowlist>\` — марк. список ref-лінків на ПЕРЕДУМОВИ (що точно треба знати, без чого статтю не зрозуміти), кожен рядок = лінк + коротко «що саме знати». Лінки 2-сегментні на ТЕМУ (\`book:<книга>/<slug>\` чи \`guide:<курс>/<slug>\`, дзеркально §6), лише ВАГОМІ передумови. ${KIND === 'guide' ? 'КУРС: клади лише передумови ЗЗОВНІ курсу АБО ще не пройдені по нитці — те, що курс уже дав раніше, НЕ додавай.' : 'book/catalog: усі справжні передумови (стаття standalone).'} Якщо тема-передумова ще не існує в репо — обробляй як залежність (додай у newTopics, КРОК3).${KIND === 'catalog' ? `
 • **(§8) КАТАЛОГ — КОНКРЕТНИЙ ОБʼЄКТ.** Описуєш саме цю річ (плату/модуль/прилад/деталь): читач має УПІЗНАТИ її, зрозуміти що робить і як влаштована, як підʼєднати/використати й чого стерегтися. Секції добирай САМ під природу пристрою; партномери/моделі ДОРЕЧНІ (це каталог). БЕЗ фраз послідовності. ЛІНКИ каталогу — ЗАВЖДИ префікс book: (родини в __BOOKS__): тема book:РОДИНА/slug; вставка book:РОДИНА/slug/ТИП-назва.md. Префікса catalog: НЕ існує, і шлях-лінк у дужках-catalog НЕ вживай — тільки book:-попап.
 • **(§8) ПЛАТА/МОДУЛЬ ЗІ СХЕМОЮ — ОБОВʼЯЗКОВО.** Якщо річ має схему устрою АБО схему підключення: (а) зобрази ОБИДВІ SVG-фігури — принципову схему + розводку ПІН-У-ПІН (svgcheck 0); (б) опиши їх (живлення, рівні, підтяжки, що куди); (в) дай API у api-вставці — додай у inserts[] { file:"api-<name>.md", type:"api", brief:"API/довідка: розводка+регістри+протокол (залізо) та/або бібліотека/типові виклики + робочий C/C++, пастки" }. Без цих трьох board/модуль-стаття НЕПОВНА. Голі пасиви/розхідники (резистори, дроти, припій) — без схеми/API, коротко за призначенням.
 • **(§8) РОДИНА — ЛІНКУЙ, НЕ ПОВТОРЮЙ.** Якщо продукт належить до лінійки з кількох варіантів (спільний виробник/архітектура/історія — ESP32, Arduino, RPi, KY-серія…) — НЕ переказуй спільну історію/архітектуру ТУТ. Постав ref-попап на ОГЛЯДОВУ статтю родини book:<родина>/<family> (напр. book:boards/esp32-family) по спільне й опиши ЛИШЕ специфіку цього продукту. Нема family-топіка — додай у newTopics { kind:"catalog", book:"<родина>", section:"<секція>", slug:"<family>", title:"Родина …" } (і постав на нього ref).` : ''}
КРОК3 — ЛІНКИ Й СПИСКИ (головне для конвеєра):
 • ВЛАСНІ ВСТАВКИ (низький поріг рішення, але КОНТЕКСТНО — скільки просить тема). Якщо в темі є під-блок, який можна корисно розгорнути окремо (історія народження / математика-виведення / код-проєкт / розбір алгоритму / клас-компонент) — винеси його вставкою, а не стискай у статті. Вагаєшся «варте окремої вставки чи ні» — радше РОБИ. НОРМИ на кількість НЕМА: скільки просить логіка теми — стільки й став (одна тема — жодної вставки, інша — кілька різних типів, коли кожна справді потрібна: hist/math/proj доповнюють одне одного). Заради числа НЕ додавай. Межа — якість: кожна несе окремий шар, не переказ статті. НЕ пиши вміст вставки тут. Натомість: (а) встав у прозі ref-зноску-попап [текст](${SELF}:${BOOK}/${u.slug}/<type>-<name>.md) — лінк ОБОВʼЯЗКОВО з розширенням «.md» (без нього рушій не відкриє) — з конспектом 1–7 речень; (б) додай її в inserts:[{file:"<type>-<name>.md", type:"hist|comp|math|proj|api", brief:"2–4 речення: що саме вставка має покрити"}]. Її напише НАСТУПНА фаза. ⚠️ КОЖНА вставка, на яку ти поставив ref у прозі, МУСИТЬ бути в inserts[] з ТИМ САМИМ іменем файлу — жодного ref без запису (інакше файл не створять → битий лінк).${KIND === 'catalog' ? ' (catalog — без comp-.)' : ''}${INSERT_BIAS}
 • НОВІ ЗАЛЕЖНІ ТЕМИ — ПРОАКТИВНО, НЕ ПОКЛАДАЙСЯ НА ПЛАН. План курсу/книги НЕ вичерпний на 100% — саме ПІД ЧАС письма ти найкраще бачиш, чого бракує. Перш ніж завершити, пройдись по ВАГОМИХ поняттях, які стаття ПРИПУСКАЄ відомими або на які СПИРАЄТЬСЯ, і для кожного ПЕРЕВІР наявність у репо: Bash grep по slug/назві у ${ROOT}\\book\\*\\manifest.js та ${ROOT}\\guide\\*\\manifest.js (досить готова АБО стаб pending/empty). Якщо вагомого поняття НЕМА НІДЕ — це ПРОГАЛИНА плану: НЕ обходь її (не уникай згадки й не лишай голий inline-текст без ref!), а ЗАВЕДИ тему — постав ref (book:<книга>/<slug> або guide:<курс>/<slug>) і додай у newTopics:[{kind,book,section,slug,title,needDetailed}]. Для book — РЕАЛЬНА наявна галузь-section, що найкраще пасує (нову галузь лише якщо жодна наявна не підходить); для guide — модуль. Якщо лінкуєш на ЯВНУ ДЕТАЛЬНУ нової теми (…/detail, рідко) — needDetailed:true. Лінк на вставку-файл — з «.md». Файл НЕ створюй (заведе фаза Маніфест; дублі вона відсіє). Поріг — вагомість (§6): справжня залежність, без якої тему не зрозуміти, НЕ кожна побіжна згадка. Краще завести зайву тему-стаб, ніж лишити приховану прогалину.${level === 'basic' ? `
 • ДЕТАЛЬНА ВЕРСІЯ ЦІЄЇ ТЕМИ (§3, НИЗЬКИЙ ПОРІГ). Оціни: чи має тема РЕАЛЬНИЙ другий шар — виведення формул, протокол/алгоритм, багатогранна архітектура/залізо, багато граничних випадків? Якщо, пишучи базову, ти СТИСКАВ матеріал — постав needDetailedSelf:true (детальну поставлять у чергу). Проста довідка/огляд/вузька замітка — needDetailedSelf:false.` : ''}
 • DEEPER-ЦІЛІ (§6). Якщо ставиш ЯВНУ ДЕТАЛЬНУ («…/detail», рідко — головно ref із курсу) на тему, що ВЖЕ Є в репо, але має лише базову, — додай ту тему в deeperTargets:[{book,slug}] (щоб її детальну поставили в чергу). Лінк лишай на /detail.
 • МАНІФЕСТ НЕ ЧІПАЙ. Вставки САМ не пиши (це фаза 3).
КРОК4 — САМОАУДИТ: фігури згенеровано (figs.py запущено, SVG в img/; svg-гейт до «0» — окремий Sonnet-крок, не твій); обсяг у смузі §3; без LaTeX/«Рис.»; ${KIND === 'guide' ? 'нитка курсу доречна (лише назад)' : 'самодостатньо, без фраз послідовності'}.
Поверни: ok, files (стаття+фігури), inserts (свої вставки на фазу 3), newTopics (нові залежні теми на реєстрацію), needDetailedSelf (чи варта ця тема детальної, §3), deeperTargets (наявні теми, ref-нуті як /detail, §6), note.`
}
// Списки з args (доробка) — стартова база; далі ДОДАЄМО те, що повернуть агенти дописаних статей.
const DETAILED_NEED = (DETAILED_IN || []).map((d) => ({ book: d.book || BOOK, slug: d.slug }))
let doneArticles = SKIP_UNITS.slice()
let INSERTS = (INSERTS_IN || []).slice()
let NEWTOPICS = (NEWTOPICS_IN || []).slice()
if (WRITE_UNITS.length) {
  const aResults = await staggered(WRITE_UNITS, (u) =>
    callAgent(articlePrompt(u), { label: `стаття:${u.slug}`, phase: 'Статті', model: 'opus', effort: 'max', schema: ART_RET })
      .then((pr) => ({ u, ok: !!(pr && pr.ok), inserts: (pr && pr.inserts) || [], newTopics: (pr && pr.newTopics) || [], needDetailedSelf: !!(pr && pr.needDetailedSelf), deeperTargets: (pr && pr.deeperTargets) || [], note: pr && pr.note }))
      .catch(() => ({ u, ok: false, inserts: [], newTopics: [], needDetailedSelf: false, deeperTargets: [] })))
  const okR = aResults.filter((r) => r.ok)
  doneArticles = doneArticles.concat(okR.map((r) => r.u))
  INSERTS = INSERTS.concat(okR.flatMap((r) => r.inserts.map((i) => ({ ...i, section: r.u.section, topicSlug: r.u.slug, topicTitle: r.u.title }))))
  NEWTOPICS = NEWTOPICS.concat(okR.flatMap((r) => r.newTopics))
  // §3/§6 — детальні версії у чергу: власна тема (needDetailedSelf, лише коли пишемо basic) + deeper-цілі (ref на /detail наявних тем)
  for (const r of okR) if (r.u.level === 'basic' && r.needDetailedSelf) DETAILED_NEED.push({ book: BOOK, slug: r.u.slug })
  for (const r of okR) for (const d of (r.deeperTargets || [])) if (d && d.slug) DETAILED_NEED.push({ book: d.book || BOOK, slug: d.slug })
  log(`Статей дописано: ${okR.length}/${WRITE_UNITS.length}`)
}
log(`Разом статей готово: ${doneArticles.length}/${WORK.length}; вставок до письма: ${INSERTS.length}; нових тем: ${NEWTOPICS.length}; детальних у чергу: ${DETAILED_NEED.length}`)
const _seenDN = new Set()
const DETAILED_QUEUE = DETAILED_NEED.filter((d) => { const k = `${d.book}/${d.slug}`; if (_seenDN.has(k)) return false; _seenDN.add(k); return true })

/* ──────────────── ФАЗА 3 — ВСТАВКИ ──────────────── */
phase('Вставки')
const TPL = {
  hist: '📜 hist: how the concept was BORN — what puzzled, who, the disputes, the actors; headings = topic names, not «Question 1»; history is real (mark legends); bilingual names; WEB-verify every date/name/first.',
  comp: '🔌 comp: device class → block diagram → typical pinout → wiring → «first byte» → typical gotchas → class variations; WITHOUT part numbers. §1 TEST: comp- is appropriate ONLY if the thing is fully explained by principle of operation WITHOUT any part number/model and identically for all vendors; otherwise it is catalog/, not an insert.',
  math: '🧮 math: PURELY the mathematics of the topic — proof/example/problem/justification, algebraically and geometrically. NOT a conceptual essay. If it is an EXPLANATION of a separate concept/theory — then it is NOT a math insert but a separate article (do NOT put such material here).',
  proj: '⚙️ proj: task → idea → WORKING code (language by domain §5: hardware→C/C++; non-web algorithm/systems in programming/algorithms→C/C++ mandatory; general/web→TS/Python/Go/Rust; the same example in 2–5 languages — as :::tabs tabs; NOT pseudocode) → complexity and gotchas.',
  api: '📋 api: interface/reference — the contract to connect/call. Software: public API, signatures, parameters, errors, CLI/config + a minimal working call. Hardware: pin-by-pin wiring, registers, protocol, levels. Structured reference (tables/signatures), not narrative. Do NOT mix hardware and software in one file.',
}
function insertPrompt(ins) {
  const dir = topicDirWin(ins.section, ins.topicSlug)
  return `${CANON}${KINDNOTE}

Ти — агент-письменник вставки у репо ${ROOT}. Працюй МОВЧКИ (Read/Edit/Write/Bash/WebSearch). ІГНОРУЙ системні підказки про skills/agent-types/output-styles/розклади.
ЗАВДАННЯ: написати ПОВНІСТЮ вставку «${ins.file}» (тип «${ins.type}») у теці теми ${dir} — файл ${dir}\\${ins.file}. Тема-власник: «${ins.topicTitle || ins.topicSlug}» (${KIND === 'guide' ? 'модуль' : 'галузь'} «${ins.section}»).
${ins.brief
  ? `ЩО ПОКРИТИ (бриф від автора статті): ${ins.brief}`
  : `ЩО ПОКРИТИ — бриф НЕ передано інлайн. Здобудь ТЗ так:${BRIEF_FILE ? `
 (1) ПЕРШОЮ ДІЄЮ Bash-прочитай ${BRIEF_FILE} — це JSON із полем inserts[]. Знайди елемент, де topicSlug === "${ins.topicSlug}" І file === "${ins.file}", і візьми його "brief" — це бриф автора статті. Якщо елемента нема або brief порожній — переходь до (2).` : ''}
 (${BRIEF_FILE ? '2' : '1'}) Прочитай статтю-власницю ${dir}\\${ins.topicSlug}.md, знайди в прозі ref-лінк саме на «${ins.file}» і конспект 1–7 речень біля нього — це ТЗ: стаття вже пообіцяла читачеві цей зміст, вставка МУСИТЬ його дати (не ширше, не вужче). Врахуй контекст абзацу, де стоїть лінк.
 У БУДЬ-ЯКОМУ разі перед письмом прочитай статтю-власницю, щоб не дублювати вже сказане в ній.`}
ШАБЛОН ТИПУ: ${TPL[ins.type] || TPL.hist}
ВИМОГИ: §3 — почни з H1 («# Назва», можна з емодзі; заголовок+1-ше речення САМІ кажуть ЩО це й НАВІЩО); 600–9000 слів; несе вагу (НЕ переказ теми/банальність); Фейнман; жива українська; формули Unicode у код-блоках; свої фігури за потреби (figs.py у ${dir}, ЗАПУСТИ його — SVG в img/; svg-гейт до «0» — окремий Sonnet-крок, не твій); факти — веб-звір; крос-лінки ${SELF}:/book:/guide: за §6 (тема/крок — 2 сегменти, загальний лінк; явна детальна — 3-й сегмент /detail; вставка <type>-<name>.md — з «.md»). Вставка БЕЗ зворотних лінків на статтю-власника (НЕ лінкуй назад на «${ins.topicSlug}»). МАНІФЕСТ НЕ ЧІПАЙ.
 • НОВІ ЗАЛЕЖНІ ТЕМИ — так само, як автор статті (§6). Якщо ти спираєшся на вагоме поняття, якого В РЕПО НЕМА (Bash-grep по slug/назві в ${ROOT}\\book\\*\\manifest.js та ${ROOT}\\guide\\*\\manifest.js — досить стаба pending/empty), НЕ обходь згадку й НЕ лишай голий текст без ref: постав ref (book:<книга>/<slug>) і додай тему в newTopics:[{kind,book,section,slug,title,needDetailed}] — section бери РЕАЛЬНУ наявну, що найкраще пасує. Файл НЕ створюй (заведе фаза «Маніфест»; дублі вона відсіє). Поріг — справжня залежність, без якої вставку не зрозуміти, НЕ кожна побіжна згадка.
Поверни: ok, file, note, newTopics (нові залежні теми на реєстрацію; [] якщо нема).`
}
const iResults = INSERTS.length
  ? await staggered(INSERTS, (ins) =>
      callAgent(insertPrompt(ins), { label: `вставка:${ins.topicSlug}/${ins.file}`, phase: 'Вставки', model: 'opus', effort: 'max', schema: INS_RET })
        .then((pr) => ({ ins, ok: !!(pr && pr.ok), newTopics: (pr && pr.newTopics) || [] }))
        .catch(() => ({ ins, ok: false, newTopics: [] })))
  : []
// нові теми, оголошені ВСТАВКАМИ, — у ту саму чергу на реєстрацію, що й з статей
NEWTOPICS = NEWTOPICS.concat(iResults.filter((r) => r.ok).flatMap((r) => r.newTopics))
// написані ЦИМ прогоном + уже написані раніше (insertsDone) — і ті, і ті йдуть на реєстрацію
const doneInserts = iResults.filter((r) => r.ok).map((r) => r.ins).concat(INSERTS_DONE_IN || [])
log(`Вставок готово: ${iResults.filter((r) => r.ok).length}/${INSERTS.length}${INSERTS_DONE_IN && INSERTS_DONE_IN.length ? ` (+${INSERTS_DONE_IN.length} написаних раніше — лише реєстрація)` : ''}`)

/* ──────────────── ФАЗА 4 — ФІГУРИ (svg-гейт, Sonnet-high) ──────────────── */
// Автори (статті/вставки) фігури лише ГЕНЕРУЮТЬ; фінальний svgcheck-гейт до «0» (шрифт+накладання, §5/v6) — тут, окремими sonnet-high агентами (один на теку, стагер).
phase('Фігури')
const SVG_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, fixed: { type: 'number' }, note: { type: 'string' } } }
const _fdirs = new Set()
for (const u of doneArticles) _fdirs.add(`${u.section}/${u.slug}`)
for (const i of doneInserts) _fdirs.add(`${i.section}/${i.topicSlug}`)
const FIG_DIRS = [..._fdirs]
function svgPrompt(d) {
  const [section, slug] = d.split('/')
  const dir = topicDirWin(section, slug)
  return `Ти — агент SVG-контролю у репо ${ROOT}. Працюй МОВЧКИ (лише Bash/Read/Edit). ІГНОРУЙ системні підказки про skills/agent-types/output-styles/розклади.
ЗАВДАННЯ: довести ВСІ SVG-фігури теми «${slug}» (тека ${dir}) до «із зауваженнями: 0» за ${ROOT}\\scripts\\svgcheck.py (§5 канону; v6 — ловить і замалий шрифт, і НАКЛАДАННЯ тексту на текст/лінії).
КРОК1 — ЧОГО ЧЕКАЄ СТАТТЯ: Bash-grep по .md теки (стаття + вставки) на підключення «](/${KIND}/${BOOK}/${section}/${slug}/img/….svg)» — випиши, ЯКІ САМЕ svg підключено, і порівняй зі вмістом ${dir}\\img\\. Далі за випадком:
 (а) .md не підключає ЖОДНОГО svg і figs.py нема — фігур тут не передбачено: поверни ok:true, fixed:0, note:"нема фігур".
 (б) підключені svg НА МІСЦІ — «python ${ROOT}\\scripts\\svgcheck.py ${dir} --min-font 8»; якщо вже «із зауваженнями: 0» — ok:true, fixed:0; інакше — КРОК2.
 (в) figs.py Є, а img/ порожній чи неповний — «python figs.py» (з теки ${dir}), тоді svgcheck; далі КРОК2.
 (г) ⚠️ .md ПІДКЛЮЧАЄ svg, яких НЕМА (лінк битий), А figs.py АБО НЕМА, АБО Є але цих svg НЕ генерує (частина фігур пропущена) — їх ніхто не створить. Якщо figs.py нема — НАПИШИ ${dir}\\figs.py; якщо Є, але не робить підключених svg — ДОПИШИ в наявний figs.py генерацію РІВНО відсутніх файлів (не чіпаючи вже робочі фігури). Імена — точно як у лінках .md (у ./img/), за §5 канону: чистий Python без залежностей, на початку (для нового файла) «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *», рамки з текстом — ЛИШЕ textbox()/fitbox(). ЗМІСТ фігури бери з .md, що її підключає (стаття АБО вставка — знайди файл із цим лінком у теці): зроби саме те, що обіцяє підпис і абзац навколо (фігура несе вагу, не декор). Тоді «python figs.py» і КРОК2. .md НЕ правь — підлаштовуй фігури під нього.
КРОК2 (лише якщо є зауваження): відкрий ${dir}\\figs.py і ПРАВ РОЗКЛАДКУ, не зміст — розсунь підписи (ширші клітини/колонки, більший viewBox), веди лінії ПОВЗ написи, не втискай довгі рядки поруч; рамки з текстом — ЛИШЕ через textbox()/fitbox() зі svgkit (він у ${ROOT}\\scripts). Зміст/сенс фігури НЕ міняй.
КРОК3: «python figs.py» (з ${dir}), тоді знову svgcheck. Повторюй КРОК2–3, доки «із зауваженнями: 0» (щонайбільше ${SVG_TRIES} ітерацій). НЕ чіпай .md статті, вставки й маніфест — ЛИШЕ figs.py та img/.
Поверни: ok (true ⟺ кінцево «0 зауважень» або фігур нема), fixed (скільки фігур виправив), note (що зробив; якщо не довів до 0 — яке зауваження лишилось і де).`
}
let svgResults = []
if (FIG_DIRS.length) {
  log(`SVG-гейт (sonnet high, стагер ${STAGGER / 1000}с): ${FIG_DIRS.length} тек`)
  svgResults = await staggered(FIG_DIRS, (d) =>
    callAgent(svgPrompt(d), { label: `svg:${d}`, phase: 'Фігури', model: 'sonnet', effort: 'high', schema: SVG_RET })
      .then((pr) => ({ d, ok: !!(pr && pr.ok), fixed: (pr && pr.fixed) || 0, note: pr && pr.note }))
      .catch(() => ({ d, ok: false, fixed: 0 })))
  const svgFixed = svgResults.reduce((s, r) => s + (r.fixed || 0), 0)
  const svgBad = svgResults.filter((r) => !r.ok)
  log(`SVG-гейт: тек ${FIG_DIRS.length}, виправлено фігур ${svgFixed}${svgBad.length ? `; НЕ доведено до 0: ${svgBad.map((r) => r.d).join(', ')}` : '; усі «0 зауважень»'}`)
}

/* ──────────────── ФАЗА 5 — МАНІФЕСТ (серійно) ──────────────── */
phase('Маніфест')
if (doneArticles.length) {
  const donePayload = doneArticles.map((u) => ({ slug: u.slug, ver: u.level }))
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2 — статус ПЕР-ВЕРСІЙНИЙ). Для КОЖНОГО {slug, ver} з переліку знайди тему за slug і зміни статус САМЕ версії ver ("basic" чи "detailed") на "done" (Edit точково — лише поле ver тієї теми; ІНШУ версію й решту тем не чіпай). ПЕРЕЛІК: ${JSON.stringify(donePayload)}\nПоверни ok, count.`,
    { label: 'статті→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
if (doneInserts.length) {
  const payload = doneInserts.map((i) => ({ section: i.section, topicSlug: i.topicSlug, type: i.type, file: i.file }))
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2): зареєструй НАПИСАНІ вставки як ГОТОВІ. Для кожної знайди тему за (section, topicSlug) і додай у масив свого типу елемент { file, status: "done" } (масив type створи, якщо його ще нема; НЕ дублюй, якщо вже є — лише постав status:"done"). Edit точково. ВСТАВКИ: ${JSON.stringify(payload)}\nПоверни ok, count.`,
    { label: 'вставки→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
if (NEWTOPICS.length) {
  await callAgent(
    `Зареєструй НОВІ залежні теми зі статусом "pending" у ВІДПОВІДНИХ маніфестах (схема v6 §2) за kind+book (book/<book>/manifest.js | catalog/<book>/manifest.js | guide/<course>/manifest.js). Для кожної знайди section за її slug і Edit-точково додай { slug, title, basic:{status:"pending"}, detailed:{status: needDetailed ? "pending" : "empty"} }, НЕ дублюючи наявне (спершу перевір, чи вже є такий slug). Якщо section відсутня — створи.
⚠️ ЕЛЕМЕНТИ З "titleHint" (замість "title") — тему відновлено з ПРОЗИ, і hint це СИРИЙ текст ref-лінка: часто в непрямому відмінку («поліномом Жегалкіна»), обрізаний («лінійних діофантових») чи з малої літери. НЕ клади його в маніфест як є. Прочитай статтю-джерело ${ROOT}\\${KIND}\\${BOOK}\\<fromArticle>, знайди той лінк, глянь контекст речення — і СФОРМУЛЮЙ правильний заголовок теми: називний відмінок, повна самодостатня назва, з великої літери, жива українська без кальок («поліномом Жегалкіна» → «Поліном Жегалкіна»; «лінійних діофантових» → «Лінійні діофантові рівняння»; «тези Черча–Тюринга» → «Теза Черча — Тюринга»).
⚠️ "section" у таких елементів — лише ПІДКАЗКА (це секція статті-джерела). Якщо тема за змістом краще лягає в іншу НАЯВНУ секцію цієї книги — клади туди; нову секцію створюй, лише коли жодна не пасує.
НОВІ ТЕМИ: ${JSON.stringify(NEWTOPICS)}\nПоверни ok, count.`,
    { label: 'нові→pending', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}

if (DETAILED_QUEUE.length) {
  await callAgent(
    `Постав детальні версії В ЧЕРГУ (§3/§6). Для кожної {book,slug} з переліку: у ВІДПОВІДНОМУ маніфесті book/<book>/manifest.js знайди тему за slug і ЯКЩО її detailed.status === "empty" — Edit-точково зміни на "pending" (треба написати -d.md). Якщо detailed вже "pending"/"done"/"deeper"/"update" — НЕ чіпай. basic та інші теми НЕ чіпай. Не дублюй. ПЕРЕЛІК: ${JSON.stringify(DETAILED_QUEUE)}\nПоверни ok, count.`,
    { label: 'детальні→pending', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}

/* ──────────────── ФАЗА 6 — КОНТРОЛЬ (§3-обсяг + фігури; лише звіт) ──────────────── */
let PROBLEMS = []
const _cdirs = new Set()
for (const u of doneArticles) _cdirs.add(`${u.section}/${u.slug}`)
for (const i of doneInserts) _cdirs.add(`${i.section}/${i.topicSlug}`)
const DONE_DIRS = [..._cdirs]
if (DONE_DIRS.length) {
  phase('Контроль')
  const ctrl = await callAgent(
    `Ти — агент-контролер якості у репо ${ROOT}. Працюй МОВЧКИ (лише Bash). НІЧОГО НЕ ПИШИ й НЕ ПРАВ — тільки перевір і звітуй.
Цей батч написав теми (${KIND}/${BOOK}), теки (відносно кореня репо): ${JSON.stringify(DONE_DIRS.map((d) => `${KIND}/${BOOK}/${d}`))}
ПЕРЕВІРКА 1 — ОБСЯГ §3: Bash «node ${ROOT}\\scripts\\wordcount.js ${KIND}/${BOOK} --all». У виводі знайди ЛИШЕ файли з ТЕК цього батчу, що позначені як поза смугою (замало/забагато слів за §3: базова 600–1600, детальна 1200–10000, вставка 600–9000).
ПЕРЕВІРКА 2 — ФІГУРИ: для КОЖНОЇ теки батчу зроби Bash «python ${ROOT}\\scripts\\svgcheck.py ${ROOT}\\${KIND}\\${BOOK}\\<секція>\\<slug> --min-font 8» і знайди фігури «із зауваженнями» (не 0).
Поверни problems:[{file, issue}] — лише РЕАЛЬНІ порушення у теках цього батчу (порожньо, якщо все гаразд). НЕ виправляй.`,
    { label: 'контроль', phase: 'Контроль', model: 'sonnet', schema: CTRL_RET })
  PROBLEMS = (ctrl && ctrl.problems) || []
  if (PROBLEMS.length) { log(`⚠️ Контроль знайшов ${PROBLEMS.length} проблем(и):`); for (const p of PROBLEMS) log(`   • ${p.file}: ${p.issue}`) }
  else log(`Контроль: обсяг §3 і фігури — без зауважень`)
}

const okN = doneArticles.length
const insWritten = iResults.filter((r) => r.ok).length      // написані ЦИМ прогоном (doneInserts містить ще й insertsDone)
const svgFixedTotal = svgResults.reduce((s, r) => s + (r.fixed || 0), 0)
const svgUnresolved = svgResults.filter((r) => !r.ok).map((r) => r.d)
return { book: BOOK, kind: KIND, level: FORCE_LEVEL || 'mixed', byLevel: { detailed: doneArticles.filter((u) => u.level === 'detailed').length, basic: doneArticles.filter((u) => u.level === 'basic').length }, scouted: WORK.length, articles: okN, articlesFailed: WORK.length - okN, inserts: insWritten, insertsRegisteredOnly: (INSERTS_DONE_IN || []).length, insertsFailed: INSERTS.length - insWritten, newTopics: NEWTOPICS.length, detailedQueued: DETAILED_QUEUE.length, svgFixed: svgFixedTotal, svgUnresolved, problems: PROBLEMS }
