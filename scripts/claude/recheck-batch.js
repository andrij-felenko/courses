/* ⚠️ ЛЕГАСІ КАМПАНІЇ RECHECK (завершена 2026-07-25). Читає ПРИБРАНЕ дерево v6
   (book/ + guide/ + catalog/ + manifest.js із window.__BOOKS__), тож на дереві v7
   не працює — не запускай, доки не переписано. Живий конвеєр ревізії сьогодні:
   review-batch.js → review-queue.js → review-apply.js. */
export const meta = {
  name: 'recheck-batch',
  description: 'RECHECK-кампанія за новим каноном. Батч N тем зі статусом recheck. ФАЗИ: (1) Скаут recheck; (2) Оцінка — 1 sonnet-high агент НА ТЕМУ (ПОВНІ інлайн-правила, AUTHORING НЕ читає — дешево) читає basic+detailed+вставки, збирає механіку через Bash (wordcount, orphan-grep) і судить за новими правилами 2.1–2.6; (3) Дія у 3 ВИДИМІ етапи: ПЕРЕНОС (sonnet — ЛИШЕ git mv basic→detailed/proj→api; стаття вже повна, контент НЕ переписуємо — дешево) · НАПИСАННЯ DETAIL (opus-max — нова/переписана детальна + math→стаття/rewrite вставок; читає AUTHORING) · НАПИСАННЯ BASIC (opus-max — нова коротка базова); осиротілі вставки лишаємо в банері; (4) Маніфест — recheck→done, нове→pending/done, перенесене перереєструвати; (5) Лінки — накопичити зміни у scripts/_recheck-linkchanges-<book>.json (застосуємо ОКРЕМИМ фінальним проходом по ВСІХ батчах). Пул CONCURRENCY(=4) одночасно. args = {book, kind?:"book"|"catalog"|"guide", limit?:30, concurrency?, stagger?, units?, insertsOnly?}',
  phases: [
    { title: 'Скаут', detail: 'знайти перші N recheck-тем (sonnet, grep)' },
    { title: 'Оцінка', detail: '1 sonnet-high на тему (Bash-механіка + ПОВНІ інлайн-правила, без AUTHORING); пул' },
    { title: 'Перенос', detail: 'sonnet: ЛИШЕ git mv (basic→detailed / proj→api) — стаття вже повна, контент НЕ чіпаємо; дешево' },
    { title: 'Написання detail', detail: 'opus-max: написати/переписати ДЕТАЛЬНУ (+ math→стаття, rewrite вставок) — читає AUTHORING' },
    { title: 'Написання basic', detail: 'opus-max: написати/переписати КОРОТКУ базову — читає AUTHORING' },
    { title: 'Маніфест', detail: 'recheck→done, нове→pending/done, перенесене перереєструвати' },
    { title: 'Лінки', detail: 'накопичити зміни у scripts/_recheck-linkchanges.json (фінальний апплай — окремо)' },
  ],
}

/* ── args ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
const BOOK = _a && _a.book ? String(_a.book) : ''
const KIND = (_a && _a.kind) || 'book'
const SELF = KIND === 'guide' ? 'guide' : 'book'
const STAGGER = Number(_a && _a.stagger) || 2000
const CONCURRENCY = Number(_a && _a.concurrency) || 4
const LIMIT = Number(_a && _a.limit) || 50
const CODE_AUDIT = !!(_a && _a.codeAudit)        // проходка суто по proj/math: аудит ЛОГІКИ + КОДУ (C/C++ для не-фронтенду); версії не чіпаємо
const INSERTS_ONLY = !!(_a && _a.insertsOnly) || CODE_AUDIT   // суто-вставковий прохід: версії НЕ чіпаємо, лише розподіл/перенос/аудит вставок
const UNITS_IN = (_a && Array.isArray(_a.units)) ? _a.units.filter((u) => u && u.slug && u.section) : null
if (!BOOK) throw new Error('args.book обовʼязковий')

const ROOT = 'E:\\develop\\courses'
const _M7 = require(`${ROOT}\\scripts\\lib\\manifest7.js`)
const BOOKDIR = _M7.bookDirOf(BOOK) || `${ROOT}\\root\\?\\${BOOK}`   // v7: вид випливає з книги
const MF = BOOK
const MFWIN = `${ROOT}\\${MF.replace(/\//g, '\\')}`
const CANON_EN = `${ROOT}\\AUTHORING.en.md`
const LINKFILE = `${ROOT}\\scripts\\_recheck-linkchanges-${BOOK}.json`   // per-book: паралельні батчі не б'ються за один файл
const MAX_TRIES = 30, RETRY_WAIT = 60000
const LIMIT_WAIT = 10 * 60 * 1000, LIMIT_MAX = 48

/* ── helpers (як у write-batch: null-streak детектор ліміту + пул зі стагером) ── */
let _nullStreak = 0
const NULL_STREAK_LIMIT = 4
async function callAgent(prompt, opts) {
  let tries = 0, limitWaits = 0
  while (true) {
    let r = null, err = null
    try { r = await agent(prompt, opts) } catch (e) { r = null; err = e }
    if (r != null) { _nullStreak = 0; return r }
    _nullStreak++
    const isLimit = (_nullStreak >= NULL_STREAK_LIMIT) ||
      (err && /session limit|usage limit|hit your|resets \d|quota|rate limit/i.test(String((err && err.message) || err)))
    if (isLimit) {
      if (limitWaits >= LIMIT_MAX) { log(`⛔ ліміт не відпустив (${opts && opts.label})`); return null }
      limitWaits++
      log(`⏳ ЛІМІТ — чекаю ${LIMIT_WAIT / 60000} хв [${limitWaits}/${LIMIT_MAX}] (${opts && opts.label})`)
      await new Promise((res) => setTimeout(res, LIMIT_WAIT)); _nullStreak = 0; continue
    }
    tries++
    if (tries >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді після ${MAX_TRIES} спроб`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}
async function staggered(items, fn) {
  const results = new Array(items.length)
  let next = 0
  async function worker() { while (next < items.length) { const i = next++; results[i] = await fn(items[i], i) } }
  const n = Math.min(CONCURRENCY, items.length)
  const workers = []
  for (let k = 0; k < n; k++) { workers.push(worker()); if (k < n - 1) await new Promise((r) => setTimeout(r, STAGGER)) }
  await Promise.all(workers)
  return results
}
function topicDirWin(section, slug) { return `${BOOKDIR}\\${slug}` }

/* ── схеми ── */
const UNITS = { type: 'object', additionalProperties: false, required: ['units'], properties: { units: { type: 'array', items: {
  type: 'object', additionalProperties: false, required: ['section', 'slug', 'title'],
  properties: { section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, scope: { type: 'string' } } } } } }

// один вердикт оцінювача
const INS_ACT = { type: 'object', additionalProperties: false, required: ['file', 'type', 'action'], properties: {
  file: { type: 'string' }, type: { type: 'string' },
  action: { type: 'string', enum: ['keep', 'inline-orphan', 'math-to-article', 'proj-to-api', 'rewrite', 'split', 'drop'] },
  newSlug: { type: 'string' }, newSection: { type: 'string' }, newBook: { type: 'string' }, note: { type: 'string' } } }
const VERDICT = { type: 'object', additionalProperties: false, required: ['versionAction', 'confidence', 'inserts'], properties: {
  basicExists: { type: 'boolean' }, detailedExists: { type: 'boolean' },
  basicWords: { type: 'number' }, detailedWords: { type: 'number' },
  basicIsFullArticle: { type: 'boolean' },                    // 2.1: базова насправді покриває тему повністю?
  versionAction: { type: 'string', enum: [
    'keep-both', 'write-basic', 'skip-basic', 'move-basic-to-detailed', 'write-detailed',
    'rewrite-basic', 'rewrite-detailed', 'rewrite-both'] },
  rewriteReasons: { type: 'array', items: { type: 'string' } },  // 2.5 логіка/нитка/вода
  inserts: { type: 'array', items: INS_ACT },
  linkChanges: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['from', 'to'], properties: { from: { type: 'string' }, to: { type: 'string' } } } },
  confidence: { type: 'number' }, note: { type: 'string' } } }
const DECIDE_RET = VERDICT     // 3-й агент повертає той самий шейп (фінальний розсуд)
const ACT_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: {
  ok: { type: 'boolean' }, linkChanges: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['from', 'to'], properties: { from: { type: 'string' }, to: { type: 'string' } } } },
  newTopics: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['book', 'section', 'slug', 'title', 'version'], properties: { book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, version: { type: 'string' } } } },
  newInserts: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['section', 'slug', 'file', 'type'], properties: { section: { type: 'string' }, slug: { type: 'string' }, file: { type: 'string' }, type: { type: 'string' } } } },
  note: { type: 'string' } } }
const REG_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } }
const MOVE_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: {
  ok: { type: 'boolean' }, moved: { type: 'array', items: { type: 'string' } },
  linkChanges: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['from', 'to'], properties: { from: { type: 'string' }, to: { type: 'string' } } } }, note: { type: 'string' } } }

/* ── ПОВНІ інлайн-правила для ОЦІНЮВАЧА (самодостатні — судити БЕЗ AUTHORING; пише-ж агент Дії читає AUTHORING сам) ── */
const RECHECK_RULES = `You judge an article against the NEW WRITING CANON. These checkpoints ARE the canon for the verdict — you do NOT open AUTHORING to judge (the ACTION agent reads it when it writes). Return verdict fields only.

VERSIONS (2.1). detailed is the PRIMARY version, always written; basic is a SHORT single-idea overview (one core thought, no second layer), optional. If BOTH exist and each fits its role → keep-both (unless 2.5 issues). Only detailed → basic is written ONLY when detailed is big AND a quick overview genuinely helps: detailed ≤3150 words → skip-basic (a basic would just duplicate); detailed clearly big/dense → write-basic. Only basic → is it ALREADY a complete article (full coverage, not a short overview)? yes → move-basic-to-detailed (it IS the detailed), then apply the size rule for whether to also write-basic; no (genuine short overview) → write-detailed. Word bands: basic 540–1440, detailed 1080–9000, catalog-detailed ceiling 14400, inserts 540–8100. HARD RULE (§3): a basic must be ≤ HALF of its detailed in prose words AND written in SIMPLER language with the SAME meaning (cut material — derivations, variations, edge cases, most examples — never the truth). A version whose SIZE is off but whose substance is fine is NOT by itself a reason to rewrite — bands guide the writer, they are not a recheck failure alone; the ONE exception is a basic longer than half its detailed: that one IS a violation (shrink the basic, or drop it → skip-basic).

INSERTS (2.2). ⚠️ STEP 1 — RECLASSIFY (a CORE recheck goal — do it RELIABLY; it is NOT restrained by the golden rule below, which only limits rewriting PROSE): for EVERY insert make a deliberate call, NEVER default to keep out of caution. A ⚙️proj that is actually an INTERFACE/REFERENCE — pinout, register map, protocol, public API / signatures, or how-to-drive/connect the part — → action "proj-to-api". A 🧮math that actually EXPLAINS a separate concept or theory (not pure topic-math) → action "math-to-article". Reclassify whenever the content fits the other type — this is exactly what recheck exists to fix; under-doing it is a FAILED verdict. STEP 2 — GOLDEN RULE «готове не переписуємо»: an already-written insert is NEVER rewritten for word-count/length. Rewrite (action "rewrite") ONLY if its SUBSTANCE is fundamentally wrong (wrong facts / wrong concept / outdated) — rare. ⚠️ For a ⚙️proj (code) insert, WRONG/MISSING mandatory code language IS a substance failure: if its code violates §5 (a non-web proj lacking the mandatory C/C++ per 2.6, or pseudocode / LaTeX / transliterated or broken tabs) → action "rewrite" (the code is the whole point of a proj — wrong language is substance, NOT length). Otherwise: keep, or MOVE (math-to-article / proj-to-api / split). Insert types: 📜hist (history/attribution) · 🔌comp (comparison/alternatives) · 🧮math (pure math of the topic) · ⚙️proj (worked implementation/algorithm) · 📋api (interface/reference: pinout/registers/protocol, or public API/signatures/how-to-call). Each insert should justify a DISTINCT angle that would bloat the main article — but a written one that is merely redundant is still "keep" unless truly pointless (then drop, rare). ORPHANED = the owner prose has NO inline ref-link to the insert file (it shows only in the top banner). Bash-grep the basic and detailed .md of the topic for each insert filename. Orphaned inserts → action "keep", LEAVE them banner-only (NOT critical; do NOT weave inline).

MATH insert (2.3). Must be PURELY mathematics of the topic — proof / worked example / problem / justification (algebra + geometry), no separate concept-teaching. If it actually EXPLAINS a separate concept or theory (a conceptual essay) → action "math-to-article" with newSlug + newSection + newBook. ⚠️ TARGET BOOK (math's home is the MATH book — do NOT scatter general math across subject books): if the essay is GENERAL, REUSABLE mathematics — a method / identity / theorem / transform / technique that other subjects also use (e.g. phasors, logarithms, central-limit, Fourier series, complex numbers, order-of-magnitude) → newBook:"math"; FIRST Bash-grep book/math/manifest.js for an existing matching slug and, if one exists, target IT (reuse that slug — do NOT create a second copy). ONLY when the article is genuinely ABOUT a subject-specific phenomenon that merely employs math (e.g. Boltzmann factor, load-line, Kutta-Joukowski lift, ENOB) → newBook = this same book. NEVER let one math concept become separate articles in two subject books. Genuine topic-math (stays an insert) → keep.

PROJ vs API (2.4). ⚙️proj = a worked implementation/algorithm the reader follows. 📋api = an INTERFACE/REFERENCE (pinout, register map, protocol, or public API — signatures and how-to-call, not a walked-through algorithm). A proj that is really a reference → action "proj-to-api". A single insert that CONFLATES two distinct things — a hardware map + a software API, OR an INTERFACE-reference + a worked APPLICATION-example — → action "split" (produce both focused inserts, keep both). Otherwise keep. Note: api (the interface reference) and proj (an application example) are complementary — a part often warrants BOTH; if one is clearly missing, flag it.

LOGIC & PROSE (2.5). Continuity: each paragraph/section follows from the previous — no gaps the reader must fill. Necessity before statement: a thing is motivated before it is named/used. Example illustrates, never carries the explanation. ONE line: a neighbouring/related topic is a link, not a new section. NO filler/water: every sentence adds. Sentence clarity: one thought per sentence, the mechanism before its term, no dense «каша». No closing recap/«підсумок» section. List concrete failures in rewriteReasons; only genuine, severe failures → versionAction rewrite-*.

METHOD & VOICE (§4). Feynman-style exposition: start from a concrete, physical/visual thing the reader already trusts, then generalise; make the reader SEE why it must be so, not just accept it. Explain by ESSENCE and mechanism, not by labels. No dumb-literal scaffolding headers («мета статті», «навіщо це», «висновок»). It should read like one mind explaining to another, not a spec sheet. Weak/watery/label-driven exposition that lost this → rewrite.

HISTORY (§7, for hist inserts). Attribution accurate and de-mythologised: separate ethnicity / nationality / birthplace / language / institution; credit real contributors; flag imperial/national myths; state evidential status (fact / contested / myth). A hist insert repeating a hero-myth or single-inventor myth without evidence → rewrite (substance wrong).

CODE & TABS (§5) (2.6). Every code example and «:::tabs» block. Language BY DOMAIN: embedded/hardware/registers/hot-path → C/C++; general/web/backend → stack languages (TS/Python/Go/Rust). In programming/algorithms & embedded, a NON-web proj (algorithm/data-structure/systems/registers/performance/memory/parallelism) → C or C++ is MANDATORY (main language OR one of the tabs); only PURELY client-side frontend is exempt. «:::tabs»: each tab an idiomatic, self-correct equivalent of the SAME example (NOT a mechanical transliteration); a tab that doesn't fit is dropped, not forced. Code real & correct (not pseudocode); formulas as Unicode in code blocks, never LaTeX. Check code INSIDE ⚙️proj inserts too, not only the article body. Violations (wrong/missing C/C++, transliterated/empty/broken tab, pseudocode, LaTeX): if the violating code is in the article BODY (basic/detailed) → rewriteReasons + rewrite that version; if it is in a ⚙️proj INSERT → give THAT insert the action "rewrite" (per 2.2, code-language is substance for a proj). ⚠️ BUILT-IN DEEP CHECK — for EVERY ⚙️proj and 🧮math insert ALSO verify its LOGIC, not just the code language: is the algorithm / mathematics actually CORRECT and complete — no wrong claim, off-by-one, invalid proof, hand-waved or missing step, a gap the reader would trip on? A logic flaw → action "rewrite" (fix the logic, keep the scope). WRONG LOGIC or WRONG/MISSING mandatory code in a ⚙️proj/🧮math insert IS a substance failure — it is NOT shielded by the golden rule 2.2; do NOT rubber-stamp proj/math inserts. (This is done in-line during the normal recheck, so no separate audit pass is needed for books that go through recheck.)

PREKNOWLIST (v6). A NEW article opens with a collapsed <preknowlist> under the H1 (prerequisites). Its absence on an otherwise-fine article is a minor note, not a rewrite trigger; when the action agent rewrites, it adds one.

OUTPUT of any rewrite/new article stays UKRAINIAN. Judge HONESTLY — that is the POINT of recheck: if the article genuinely falls short (real water, reasoning gaps, mis-classified inserts, wrong version structure, weak continuity, dense «каша», §5 code violations) → fix it (rewrite/move); if it genuinely meets the canon → keep it. Do NOT invent problems to justify a rewrite, and do NOT rubber-stamp mediocre work. A real recheck changes a fair share of articles; near-zero changes means too lax, mass-rewrites means invented problems.${KIND === 'guide' ? ' ⚠️ THIS BOOK IS A COURSE (guide): a step is CUMULATIVE — it builds on prior steps and may use sequence phrases («as we saw», «in the previous step», «we will see later»); do NOT flag those as violations. Judge continuity WITHIN the course thread (each step relies only on earlier steps).' : ''}`

/* ──────────────── ФАЗА 1 — СКАУТ ──────────────── */
let WORK = []
if (UNITS_IN) { WORK = UNITS_IN.slice(0, LIMIT); log(`Скаут (інлайн): ${WORK.length} тем`) }
else {
  phase('Скаут')
  const scout = await callAgent(
    (CODE_AUDIT
      ? `Знайди перші ${LIMIT} тем у маніфесті ${MFWIN}, що МАЮТЬ вставки proj АБО math (у рядку теми присутнє «proj: [» або «math: [»).
Схема: book/catalog — sections[]→topics[]; guide — modules[]→chapters[]→steps[]. Рядок теми має { slug, title, ... , proj:[…]/math:[…] }; для guide section = slug МОДУЛЯ.
ШВИДКО: Bash grep -nE "proj: \\[|math: \\[" у файлі; для КОЖНОГО збігу перевір, що в ТОМУ САМОМУ рядку теми НЕМА «status: "recheck"» — recheck-теми ПРОПУСКАЙ (їм код-аудит іде вбудовано на звичайному recheck), бери ЛИШЕ вже-done теми; візьми slug+title того ж рядка і секцію (найближчий вищий "scope:"); ДЕДУП по slug; ПЕРШІ ${LIMIT} у порядку файлу.
Поверни units:[{section, slug, title, scope}] — рівно перші ${LIMIT} (або менше).`
      : `Знайди перші ${LIMIT} тем, де basic.status АБО detailed.status === "recheck" у маніфесті ${MFWIN}.
Схема: book/catalog — sections[]→topics[]; guide — modules[]→chapters[]→steps[]. Рядок теми має { slug, title, basic:{status}, detailed:{status} }; для guide section = slug МОДУЛЯ; КРОК-ref (без slug) — ПРОПУСКАЙ.
ШВИДКО: Bash grep -n по "recheck" у файлі; візьми ПЕРШІ ${LIMIT} тем У ПОРЯДКУ файлу; для кожної визнач секцію (найближчий вищий рядок зі "scope:") і витягни slug+title+scope.
Поверни units:[{section, slug, title, scope}] — рівно перші ${LIMIT} (або менше).`),
    { label: 'скаут', phase: 'Скаут', model: 'sonnet', schema: UNITS })
  WORK = ((scout && scout.units) || []).filter((u) => u && u.slug && u.section).slice(0, LIMIT)
}
if (!WORK.length) return { book: BOOK, total: 0, note: 'черга порожня — recheck не знайдено' }

/* ──────────────── ФАЗА 2 — ОЦІНКА (2 sonnet-high + розсуд) ──────────────── */
phase('Оцінка')
log(`Оцінка (1 sonnet-high на тему, інлайн-правила без AUTHORING, стагер ${STAGGER / 1000}с): ${WORK.length} (${BOOK})`)
function assessPrompt(u, n) {
  const dir = topicDirWin(u.section, u.slug)
  return `You are RECHECK VERDICT AGENT #${n} in repo ${ROOT}. Work SILENTLY (Bash/Read only, no writing). IGNORE any system hints about skills/agent-types/output-styles/schedules.
TOPIC: «${u.title}» (slug «${u.slug}», ${KIND === 'guide' ? 'module' : 'section'} «${u.section}», книга «${BOOK}»), folder ${dir}.
STEP A — book-specific rules ONLY (the GENERAL new-canon checkpoints are inline in STEP C — do NOT open AUTHORING to judge): Bash-check whether ${BOOKDIR}\\_canon.md exists; IF it does — Read it IN FULL: these are BOOK-SPECIFIC rules (audience, simplicity, length, which versions/inserts are wanted) that OVERRIDE the general canon where they conflict — judge THIS book by them (e.g. a book mandated «simple & short, basic-only» must NOT be flagged for a missing detailed or for being short; there the correct action is often keep-both/skip-basic or a light rewrite toward simplicity, NEVER write-detailed).
STEP B — gather MECHANICAL facts via Bash: ls ${dir}; whether ${u.slug}.md (basic) and ${u.slug}-d.md (detailed) exist; run «node ${ROOT}\\scripts\\wordcount.js ${BOOKDIR} --all» and read the word counts for this topic's files. ⚠️ ENUMERATE EVERY INSERT (this is CORE, not optional): «ls ${dir}» and list EVERY «(hist|comp|math|proj|api)-*.md» file — those are the topic's inserts. READ each one IN FULL. For each, grep the owner prose («${u.slug}.md» and «${u.slug}-d.md») for its exact filename — if the filename is NOT found inline, the insert is ORPHANED (shown only in the top banner, not woven into the text). You must finish STEP B with a full list of insert files + for each: its type, whether orphaned, and what it contains — AND an explicit classification: for every ⚙️proj say «worked algorithm» or «interface/reference (pinout/register/protocol/API/how-to-drive → api)»; for every 🧮math say «pure topic-math» or «concept-essay (→ article)».${CODE_AUDIT ? ' (In a CODE_AUDIT you may SKIP the wordcount, the orphaned grep and reading the article — read ONLY the proj/math insert files.)' : ' Read the actual basic/detailed .md too.'}
STEP C — JUDGE per the checkpoints below and return a structured verdict. ${RECHECK_RULES}${KIND === 'catalog' ? '\n\n⚠️ CATALOG-SPECIFIC (§8) — for a HARDWARE part, 📋api and ⚙️proj are DIFFERENT and COMPLEMENTARY, and a part usually deserves BOTH; your job is to check whether BOTH are present/warranted, not to pick one:\n • 📋api = the INTERFACE itself — pinout / registers / protocol / addresses / how-to-connect-and-drive. The REFERENCE you look things up in; code here merely ILLUSTRATES the interface.\n • ⚙️proj = an APPLICATION EXAMPLE — a small purposeful project that USES the part end-to-end to accomplish something real. The hands-on demo you follow.\nDECISIVE (assessors chronically UNDER-convert to api): do NOT keep an insert as proj just because it «walks through a process» — showing HOW TO drive/read/address the part IS the interface (api), even as a walkthrough / diagnostic / «two approaches». A proj whose filename or H1 contains «api» → proj-to-api, ALWAYS.\nPER-INSERT DECISION: pure interface-mechanics → proj-to-api; a genuine application-project → keep proj; an insert that CONFLATES the interface AND a worked application → action "split" (→ api-<name> reference + proj-<name> example, keep BOTH). COMPLETENESS CHECK (the point «if there is an API, there must also be an example»): after your calls, if the part has an api but NO application-example proj — or a proj but no api reference — SAY SO explicitly in note (name what is missing); a well-documented part has both the reference and a hands-on example. When unsure for pure interface content → api.' : ''}${INSERTS_ONLY ? '\n\n⚠️ THIS IS AN INSERTS-ONLY PASS. Judge ONLY the inserts (checkpoints 2.2/2.3/2.4): enumerate EVERY insert file and give a per-insert action — keep / math-to-article / proj-to-api / rewrite (ONLY if substance is fundamentally wrong, never for length). ORPHANED (banner-only) inserts → keep, leave AS-IS (not critical, do NOT weave inline). The article VERSIONS are already final — set versionAction:"keep-both", leave rewriteReasons empty, propose NO version rewrite/move. Focus entirely on the inserts.' : ''}${CODE_AUDIT ? '\n\n⚠️ LEAN CODE+LOGIC AUDIT of ⚙️proj/🧮math inserts ONLY. Read JUST the ⚙️proj and 🧮math insert files — do NOT read the basic/detailed article body, do NOT run wordcount, do NOT check orphaned status (all irrelevant here). Reclassification (math→article, proj→api) is ALREADY settled during the earlier recheck of this topic — do NOT do it here; the ONLY actions are "keep" or "rewrite". For EVERY ⚙️proj and 🧮math insert, strictly check: (1) LOGIC — is the algorithm/math CORRECT, sound and complete? wrong claim / off-by-one / invalid proof / hand-waved or missing step / a gap the reader trips on → "rewrite" (fix it), note the flaw. (2) CODE (⚙️proj) — book «${BOOK}»: a NON-frontend proj (algorithm / data-structure / systems / performance / memory / concurrency) MUST have real correct C or C++ (main language OR one idiomatic tab); Python-only / JS-only / pseudocode / LaTeX / a transliteration where C/C++ is required → "rewrite" to real C/C++. hist/comp/api inserts → keep, do not touch. inserts[] MUST still list EVERY ⚙️proj/🧮math file with keep|rewrite + the flaw in note.' : ''}
Return the verdict object. ⚠️ inserts[] IS MANDATORY: it MUST contain ONE entry PER insert file you enumerated in STEP B — {file, type, action} — even when action is «keep» (then briefly say in note WHY it's fine as-is). Returning inserts:[] while ${dir} contains <type>-*.md files is a FAILED verdict, redo it. Actions: keep (fine as-is — OR orphaned/banner-only, which we LEAVE, not critical) / math-to-article (a math insert that actually EXPLAINS a separate concept → becomes its own book article: give newSlug + newSection) / proj-to-api (a proj that is really an interface/reference → rename to api) / split (one insert mixing a large hw map + large sw api) / rewrite (ONLY if substance fundamentally wrong, never for length). Also return versionAction, basic/detailed exists+words, basicIsFullArticle, rewriteReasons, linkChanges[] {from,to} for any move, confidence 0–1, note. Do NOT write or move anything — you only judge.`
}
// ОДИН вердикт на тему (v2=null ЗАВЖДИ): оцінка дешева, розсуд не потрібен — «1 агента вистачить»
const pairs = await staggered(WORK, (u, i) => Promise.all([
  callAgent(assessPrompt(u, 1), { label: `оцінка:${u.slug}`, phase: 'Оцінка', model: 'sonnet', effort: 'high', schema: VERDICT }),
  Promise.resolve(null),
]).then(([v1, v2]) => ({ u, v1, v2 })).catch(() => ({ u, v1: null, v2: null })))

// розсуд там, де основна дія розійшлась
function coreOf(v) { return v ? v.versionAction : null }
const DECIDED = []
for (const p of pairs) {
  const { u, v1, v2 } = p
  if (!v1 && !v2) { DECIDED.push({ u, verdict: null, agreed: false }); continue }
  const one = v1 || v2
  if (!v1 || !v2 || coreOf(v1) === coreOf(v2)) { DECIDED.push({ u, verdict: mergeVerdicts(v1, v2), agreed: true }); continue }
  // спірно — 3-й агент-розсуд бачить обидва вердикти
  const tie = await callAgent(
    `You are the TIE-BREAK verdict agent for topic «${u.title}» (${topicDirWin(u.section, u.slug)}) in repo ${ROOT}. Work SILENTLY.
Two prior verdicts DISAGREE on versionAction: #1=${JSON.stringify(coreOf(v1))}, #2=${JSON.stringify(coreOf(v2))}.
Read ${CANON_EN}, read the topic files (basic ${u.slug}.md / detailed ${u.slug}-d.md / inserts), and DECIDE. ${RECHECK_RULES}
Full verdict #1: ${JSON.stringify(v1)}
Full verdict #2: ${JSON.stringify(v2)}
Return the FINAL verdict object (same shape) — your judgement is decisive.`,
    { label: `розсуд:${u.slug}`, phase: 'Оцінка', model: 'sonnet', effort: 'high', schema: DECIDE_RET })
  DECIDED.push({ u, verdict: tie || mergeVerdicts(v1, v2), agreed: false })
}
// злиття двох згодних: об'єднати insert-дії й linkChanges, узяти сильніші reasons
function mergeVerdicts(a, b) {
  if (!a) return b; if (!b) return a
  const insMap = new Map()
  for (const v of [a, b]) for (const it of (v.inserts || [])) {
    const cur = insMap.get(it.file)
    if (!cur || (it.action !== 'keep' && cur.action === 'keep')) insMap.set(it.file, it)  // не-keep дія переважає
  }
  const lc = []
  const seen = new Set()
  for (const v of [a, b]) for (const c of (v.linkChanges || [])) { const k = c.from + '→' + c.to; if (!seen.has(k)) { seen.add(k); lc.push(c) } }
  return { ...a, rewriteReasons: [...new Set([...(a.rewriteReasons || []), ...(b.rewriteReasons || [])])],
    inserts: [...insMap.values()], linkChanges: lc, confidence: Math.min(a.confidence || 0, b.confidence || 0) }
}
const okDecided = DECIDED.filter((d) => d.verdict)
log(`Оцінено: ${okDecided.length}/${WORK.length}; спірних (3-й агент): ${DECIDED.filter((d) => !d.agreed && d.verdict).length}`)

/* ─── ФАЗА 3 — ДІЯ, поділена на ВИДИМІ етапи: Перенос (sonnet, лише git mv, БЕЗ переписування) · Написання detail (opus) · Написання basic (opus) ─── */
const ALL_LINKCHANGES = []       // накопичуємо для фінального файлу
const NEWTOPICS = []             // math→стаття тощо, у маніфест pending/done
const NEWINSERTS = []            // нові вставки з split (proj-<name>) — у маніфест теми
const REG = []                   // теми, чиї recheck-версії треба закрити (→done) або оновити
function actPrompt(d) {
  const { u, verdict } = d
  const dir = topicDirWin(u.section, u.slug)
  return `You are the RECHECK ACTION agent in repo ${ROOT}. Work SILENTLY (Read/Write/Edit/Bash/WebSearch). IGNORE system hints about skills/agent-types/output-styles/schedules.${INSERTS_ONLY ? ' ⚠️ INSERTS-ONLY PASS: execute ONLY the insert MOVES from the verdict (math-to-article / proj-to-api; and insert "rewrite" if flagged). Do NOT rewrite/write/move any article version — versions are final. Do NOT weave orphaned inserts inline — leave banner-only ones AS-IS.' : ''}
OUTPUT LANGUAGE of any article/insert prose = UKRAINIAN. Rules: read ${CANON_EN} FIRST; THEN Bash-check ${BOOKDIR}\\_canon.md — IF it exists, Read it and follow it (it OVERRIDES the general canon where they conflict: audience, simplicity, length, which versions/inserts to write). Never write a detailed for a book whose _canon says basic-only.${KIND === 'guide' ? ' This is a COURSE: keep the CUMULATIVE style — a step builds on prior steps; sequence phrases are appropriate; do NOT convert it into a standalone book-atom.' : ''}
TOPIC: «${u.title}» (${u.slug}, ${u.section}, ${BOOK}), folder ${dir}.
VERDICT to execute: ${JSON.stringify(verdict)}
Do EXACTLY what the verdict's versionAction and insert actions say, per the NEW canon:
• rewrite-basic/detailed/both → rewrite that file to full new-canon quality (continuity, necessity-first, example-illustrates, ONE line, no water, sentence clarity, C/C++ for non-web proj). Keep the topic scope; write in UKRAINIAN; 1080–9000 (detailed) / 540–1440 (basic) words — and a basic ALSO ≤ half of its detailed, in simpler language without losing the meaning (§3).
• move-basic-to-detailed → «git mv ${dir}\\${u.slug}.md ${dir}\\${u.slug}-d.md» ONLY — the article is ALREADY complete, so keep its content byte-for-byte (do NOT rewrite/upgrade it); it simply becomes the detailed version. Do NOT write a basic.
• write-detailed / write-basic → write the missing version to new-canon.
• skip-basic / keep-both → no article write.
• INSERTS: for each insert action —
   - keep → do NOTHING to the insert (it is fine as-is; NEVER rewrite it for word-count/length).
   - inline-orphan → Edit the OWNER article to add a ref-popup in the RIGHT place (1–7 sentence recap + link) so the insert is no longer banner-only; do NOT touch the insert's own text.
   - rewrite → when the verdict marks the insert's SUBSTANCE as fundamentally wrong (wrong facts/concept/outdated) OR its code violates §5 (a non-web proj missing the mandatory C/C++, or pseudocode / LaTeX / transliterated or broken tabs): rewrite that insert file to new-canon (Ukrainian) — for a code violation, fix the code to §5 (real, correct C/C++ where mandatory; idiomatic self-correct tabs), keeping the insert's scope. NEVER rewrite merely for length.
   - proj-to-api → «git mv ${dir}\\<proj-file> ${dir}\\api-<name>.md», adjust its H1 if needed; record linkChange {from:"${SELF}:${BOOK}/${u.slug}/<proj-file>", to:"${SELF}:${BOOK}/${u.slug}/api-<name>.md"}.
   - split → the insert CONFLATES an INTERFACE-reference AND a worked APPLICATION-example (or hw-map + sw-api); produce BOTH, keep both. «git mv ${dir}\\<file> ${dir}\\api-<name>.md» and TRIM it to ONLY the interface/reference content; then Write ${dir}\\proj-<name>.md with the APPLICATION/example content (self-contained, UKRAINIAN, §5-correct code); weave a ref to EACH into the owner prose. Record linkChange {from:"${SELF}:${BOOK}/${u.slug}/<file>", to:"${SELF}:${BOOK}/${u.slug}/api-<name>.md"} for the rename, and report the NEW insert in newInserts[] {section:"${u.section}", slug:"${u.slug}", file:"proj-<name>.md", type:"proj"}.
   - math-to-article → TARGET BOOK = verdict.newBook (default this book «${BOOK}» when absent). ⚠️ If newBook differs from «${BOOK}» (usually "math" for general math): FIRST Bash-grep book/<newBook>/manifest.js for <newSlug> — if that topic ALREADY EXISTS **and its detailed OR basic status is "done" (already WRITTEN — read the manifest line, verify)**, do NOT create a duplicate (skip article creation, do NOT add to newTopics), just delete the old math insert (see below) and record the cross-book linkChange. ⚠️ DATA-LOSS GUARD: **if <newSlug> EXISTS yet is "pending"/"empty" (an UNWRITTEN stub — no <newSlug>-d.md file on disk), do NOT delete the source and do NOT redirect to the empty stub — KEEP this math insert exactly as-is (no delete, no linkChange, leave it registered with its ref-links intact) and state in note that the target is an unwritten stub so reclassification is deferred.** If it does NOT exist, create the article at ${ROOT}\\book\\<newBook>\\<newSection>\\<newSlug>\\<newSlug>-d.md and add to newTopics[] with book:"<newBook>", version "detailed". (Same book → folder ${ROOT}\\book\\${BOOK}\\<newSection>\\..., newTopics book:"${BOOK}".) Article is UKRAINIAN new-canon. Then — ONLY in the create-new or target-already-"done" branches, NEVER when you KEPT the insert for an unwritten stub — delete the old math insert file (and any of its images) with a PLAIN filesystem delete — Bash «rm» / Remove-Item, NEVER «git rm» (and never «git add»/«git commit»): leave the removal UNSTAGED for the user (only «git mv» may touch git, per the user's rule) — and record linkChange {from:"${SELF}:${BOOK}/${u.slug}/<math-file>", to:"root:<newBook>/<newSlug>"}.
Do NOT touch the manifest (a later phase does). linkChanges[] — record ONLY genuine LINK-TARGET changes for INSERT MOVES: proj→api → {from:"${SELF}:${BOOK}/<slug>/<proj-file>", to:"${SELF}:${BOOK}/<slug>/api-<name>.md"}; math→article → {from:"${SELF}:${BOOK}/<slug>/<math-file>", to:"root:<newBook>/<newslug>"} (newBook may differ from this book — general math → "math"). ⚠️ A basic→detailed rename (slug.md → slug-d.md) needs NO linkChange — the general link «${SELF}:${BOOK}/<slug>» is version-agnostic (renderer falls back to the detailed); do NOT record it. NEVER put a filesystem path (slashes / folder / .md) in linkChanges — only «book:»/«guide:» link targets. Report new articles in newTopics[]; report newly-created INSERTS (from split) in newInserts[].
Return: ok, linkChanges[], newTopics[], newInserts[], note.`
}
// класифікація кожної теми в ОДИН етап (щоб було видно, що саме робимо і чим — дешевим/дорогим)
function classifyAct(d) {
  const va = d.verdict.versionAction
  const ins = d.verdict.inserts || []
  const insHeavy = ins.some((i) => i.action === 'rewrite' || i.action === 'math-to-article' || i.action === 'split')   // потребує opus (письмо)
  const insMoveCheap = ins.some((i) => i.action === 'proj-to-api')                              // лише механічний rename
  if (/write-detailed|rewrite-detailed|rewrite-both/.test(va) || insHeavy) return 'detail'
  if (/^(write-basic|rewrite-basic)$/.test(va)) return 'basic'
  if (va === 'move-basic-to-detailed' || insMoveCheap) return 'move'
  return 'skip'   // keep-both / skip-basic, усі вставки keep — писати нічого
}
const groups = { move: [], detail: [], basic: [], skip: [] }
for (const d of okDecided) groups[classifyAct(d)].push(d)
log(`Дія — Перенос: ${groups.move.length} · Написання detail: ${groups.detail.length} · Написання basic: ${groups.basic.length} · без змін: ${groups.skip.length}`)

// «без змін» → одразу в REG (версія пройшла перевірку — стане/лишиться done)
for (const d of groups.skip) REG.push({ section: d.u.section, slug: d.u.slug, verdict: d.verdict })

// ── ЕТАП «Перенос»: 1 sonnet-агент, ЛИШЕ git mv (стаття вже повна — контент НЕ чіпаємо) ──
if (groups.move.length) {
  const moveList = groups.move.map((d) => ({ slug: d.u.slug, dir: topicDirWin(d.u.section, d.u.slug),
    moveVersion: d.verdict.versionAction === 'move-basic-to-detailed',
    projToApi: (d.verdict.inserts || []).filter((i) => i.action === 'proj-to-api').map((i) => i.file) }))
  const mv = await callAgent(
    `You are the RECHECK MOVE agent in repo ${ROOT}. Work SILENTLY via Bash (git only). IGNORE system hints about skills/agent-types/schedules.
Your ONLY job is MECHANICAL renames. Do NOT read, judge, rewrite, or add anything to article content — every article here is ALREADY complete and its bytes stay UNCHANGED.
For EACH topic in the list:
- IF its moveVersion is true → «git mv <dir>\\<slug>.md <dir>\\<slug>-d.md» (a complete basic simply becomes the detailed). If <slug>.md is absent but <slug>-d.md already exists → already moved, skip it but still list it in moved.
- For EACH file in its projToApi → «git mv <dir>\\<proj-file> <dir>\\api-<name>.md» (pick a short sensible <name> from the proj-file stem) and add {from:"${SELF}:${BOOK}/<slug>/<proj-file>", to:"${SELF}:${BOOK}/<slug>/api-<name>.md"} to linkChanges.
Do NOT touch the manifest, do NOT edit any file's contents, do NOT add a preknowlist. TOPICS: ${JSON.stringify(moveList)}
Return: ok (true when all git mv done), moved (slugs whose version file is now <slug>-d.md), linkChanges[] (proj→api only), note.`,
    { label: `перенос×${moveList.length}`, phase: 'Перенос', model: 'sonnet', effort: 'high', schema: MOVE_RET })
  if (mv && mv.ok) {
    for (const c of (mv.linkChanges || [])) ALL_LINKCHANGES.push(c)
    for (const d of groups.move) REG.push({ section: d.u.section, slug: d.u.slug, verdict: d.verdict })
    log(`Перенос: ${(mv.moved || []).length}/${moveList.length} перейменовано (дешево, без переписування)`)
  } else { log(`⚠ Перенос не вдався — ці теми лишаться recheck`) }
}

// ── ЕТАПИ «Написання detail» / «Написання basic»: opus-max, по темі, паралельно (пул) ──
const toWrite = [...groups.detail.map((d) => ({ d, ph: 'Написання detail' })),
                 ...groups.basic.map((d) => ({ d, ph: 'Написання basic' }))]
const writeResults = await staggered(toWrite, (x) =>
  callAgent(actPrompt(x.d), { label: `${x.ph === 'Написання detail' ? 'detail' : 'basic'}:${x.d.u.slug}`, phase: x.ph, model: 'opus', effort: 'xhigh', schema: ACT_RET })
    .then((r) => ({ d: x.d, ok: !!(r && r.ok), linkChanges: (r && r.linkChanges) || [], newTopics: (r && r.newTopics) || [], newInserts: (r && r.newInserts) || [] }))
    .catch(() => ({ d: x.d, ok: false, linkChanges: [], newTopics: [], newInserts: [] })))
for (const r of writeResults) {
  if (!r.ok) continue
  for (const c of r.linkChanges) ALL_LINKCHANGES.push(c)
  for (const t of r.newTopics) NEWTOPICS.push(t)
  for (const ni of (r.newInserts || [])) NEWINSERTS.push(ni)
  REG.push({ section: r.d.u.section, slug: r.d.u.slug, verdict: r.d.verdict })
}
const writtenOk = writeResults.filter((r) => r.ok).length
log(`Написання: ${writtenOk}/${toWrite.length} ок; переносів ${groups.move.length}; зміни-лінків ${ALL_LINKCHANGES.length}; нових статей ${NEWTOPICS.length}`)

/* ──────────────── ФАЗА 5 — МАНІФЕСТ (серійно) ──────────────── */
// (переноси вставок робить етап «Перенос» (proj→api rename) або agent «Написання» (math→стаття/rewrite); окремої фази «Вставки» нема)
phase('Маніфест')
if (REG.length && !INSERTS_ONLY) {   // insertsOnly: версії вже done — статус не чіпаємо
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2) за підсумком recheck. Для КОЖНОЇ теми з переліку постав СТАТУСИ версій за її verdict.versionAction:
• keep-both / skip-basic / rewrite-* → відповідну версію(и), що ІСНУЮТЬ і доведені до канону, постав "done"; якщо skip-basic — basic лиши "empty" (не пишемо).
• move-basic-to-detailed → detailed:"done"; basic → "empty" (якщо не писали нову) або "done" (якщо написали нову коротку).
• write-detailed / write-basic → написану версію "done", другу — за її реальним станом ("empty" якщо не передбачена).
Правило: версія, яку agent реально довів/написав цього батчу, — "done"; recheck-версію, яку лишили без змін як норму, — теж "done" (перевірка пройдена). Edit точково, іншого не чіпай. ПЕРЕЛІК (з verdict): ${JSON.stringify(REG.map((r) => ({ section: r.section, slug: r.slug, versionAction: r.verdict.versionAction })))}
Поверни ok, count.`,
    { label: 'recheck→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
if (NEWTOPICS.length) {
  await callAgent(
    `Зареєструй НОВІ статті (винесені з math-вставок тощо) у ВІДПОВІДНОМУ book/<book>/manifest.js зі статусом версії "done" (вони вже написані). Для кожної {book,section,slug,title,version}: знайди/створи секцію, додай тему { slug, title, basic:{status: version==="basic"?"done":"empty"}, detailed:{status: version==="detailed"?"done":"empty"} }, НЕ дублюючи наявний slug. НОВІ: ${JSON.stringify(NEWTOPICS)}
Поверни ok, count.`,
    { label: 'нові-статті→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
// НОВІ вставки (зі split) → зареєструвати в темі
if (NEWINSERTS.length) {
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2) — НОВІ ВСТАВКИ, створені через split. Для КОЖНОЇ {section, slug, file, type}: знайди тему <slug> (секція <section>) і ДОДАЙ {file:"<file>", status:"done"} у масив її типу <type> (proj → proj:[], api → api:[], тощо; масив створи, якщо нема). НЕ дублюй уже наявний file. НОВІ ВСТАВКИ: ${JSON.stringify(NEWINSERTS)}
Поверни ok, count.`,
    { label: 'нові-вставки→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
// ПЕРЕНЕСЕНІ вставки → маніфест: прибрати зі СТАРОГО місця + додати в НОВЕ (усунення діри)
if (ALL_LINKCHANGES.length) {
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2) — ПЕРЕНЕСЕНІ ВСТАВКИ. Дано зміни-лінків {from,to}; кожна кодує перенос вставки. Для КОЖНОЇ:
• from = "${SELF}:${BOOK}/<slug>/<file>", де <file> — вставка (hist-/comp-/math-/proj-/api-*.md): знайди тему <slug> у маніфесті й ПРИБЕРИ <file> з масиву її типу (proj-*.md → з proj:[]; math-*.md → з math:[]; тощо). Файл на диску вже перенесено/видалено — маніфест мусить це відбити.
• to = "${SELF}:${BOOK}/<slug>/api-<name>.md" → це proj→api: ДОДАЙ {file:"api-<name>.md", status:"done"} у api:[] тієї ж теми (масив api створи, якщо нема).
• to = 2-сегментний "root:<book>/<newslug>" (без файла) → це math→стаття: нову статтю вже зареєстровано окремо; тут лише прибирання старої math-вставки (за пунктом from вище).
Edit ТОЧКОВО, зайвого не чіпай. ЗМІНИ: ${JSON.stringify(ALL_LINKCHANGES)}
Поверни ok, count.`,
    { label: 'переноси→маніфест', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}

/* ──────────────── ФАЗА 6 — ЛІНКИ (накопичити у файл; апплай — ОКРЕМО) ──────────────── */
phase('Лінки')
if (ALL_LINKCHANGES.length) {
  await callAgent(
    `Bash-задача: додай зміни-лінків у накопичувальний JSON ${LINKFILE}. Прочитай його (якщо нема — вважай []), додай нові елементи (масив {from,to}), прибери точні дублі, запиши назад форматованим JSON. НОВІ ЗМІНИ (${ALL_LINKCHANGES.length}): ${JSON.stringify(ALL_LINKCHANGES)}
НЕ застосовуй їх до контенту — лише допиши у файл (фінальний апплай окремим проходом). Поверни ok, count (скільки у файлі всього).`,
    { label: 'лінки→файл', phase: 'Лінки', model: 'sonnet', schema: REG_RET })
}

return { book: BOOK, kind: KIND, scouted: WORK.length, decided: okDecided.length,
  moved: groups.move.length, wroteDetail: groups.detail.length, wroteBasic: groups.basic.length, unchanged: groups.skip.length,
  written: writtenOk, linkChanges: ALL_LINKCHANGES.length, newArticles: NEWTOPICS.length, newInserts: NEWINSERTS.length }
