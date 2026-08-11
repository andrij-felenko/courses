export const meta = {
  name: 'write-batch',
  description: 'Повний v6-батч в один прогін. ФАЗИ: (1) Скаут — набрати батч на LIMIT тем: СПЕРШУ detailed-pending, далі basic-pending добиває решту (кожна тема несе свій рівень; явний level примушує один рівень); (2) Детальні — opus-агенти пишуть ДЕТАЛЬНІ статті (основна версія §3) і кожен вирішує, чи варта тема базового огляду (needBasicSelf); (2б) Базові — opus-агенти пишуть базові: з черги скаута ПЛЮС додані етапом 2 (гейт §3: ≤½ детальної, простіша мова, інакше basic:empty). Автори лінкують свої вставки в прозі, вмісту вставок НЕ пишуть, нові залежні теми оголошують на будь-якому етапі; (3) Вставки — opus-агенти (стагер 2с; math/proj/api → effort xhigh, hist/comp → medium) пишуть зібрані вставки під ці статті; (4) Фігури — спершу ЛОКАЛЬНИЙ передгейт (одна команда svgcheck.py --links по всіх теках батчу), далі sonnet-high агенти доводять до «із зауваженнями: 0» ЛИШЕ теки з проблемами; автори SVG самі НЕ гейтять; (5) Маніфест — ЛОКАЛЬНИЙ патчер (scripts/manifest-patch.js): воркфлоу будує список операцій, один дешевий агент кладе його файлом і запускає скрипт — маніфест агентами НЕ читається й НЕ редагується (економія токенів). Жоден письменник маніфест НЕ чіпає. Усі фази письма — пулом щонайбільше CONCURRENCY(=4) агентів ОДНОЧАСНО (проти масових падінь на лімітах: валить макс. стільки, не весь фронт). args = {book, kind?:"book"|"catalog"|"reference"|"guide", level?:"basic"|"detailed" (пропусти → мішаний detailed-first), limit?:10, scope?, stagger?, concurrency?, units?}',
  phases: [
    { title: 'Канон', detail: 'перегенерувати AUTHORING.write.en.md — дослівний зріз канону для письменників (sonnet-low, 1 команда)' },
    { title: 'Скаут', detail: 'набрати LIMIT: ПРІОРИТЕТ detailed-pending, basic лише добиває решту (sonnet, grep)' },
    { title: 'Детальні', detail: 'opus: детальні статті (основна версія §3); кожен автор дивиться, чи базова вже є (тоді не чіпаємо), а як нема — каже, писати її на наступному етапі чи ставити empty; пул 4, стагер 2с' },
    { title: 'Базові', detail: 'opus: базові — з черги скаута + додані етапом «Детальні»; гейт §3 (≤½ детальної, простіша мова) на місці; пул 4, стагер 2с' },
    { title: 'Вставки', detail: 'opus: написати зібрані вставки; effort xhigh для math/proj/api, high для hist/comp; пул 4, стагер 2с' },
    { title: 'Фігури', detail: 'ЛОКАЛЬНИЙ передгейт svgcheck --links по всіх теках → sonnet-high лише там, де є що правити (до «0»), правкою figs.py; пул 4, стагер 2с' },
    { title: 'Маніфест', detail: 'ЛОКАЛЬНИЙ патчер scripts/manifest-patch.js: 1 дешевий агент кладе JSON-операції й запускає скрипт (маніфест агентом НЕ читається)' },
    { title: 'Контроль', detail: 'wordcount.js (§3-обсяг) + svgcheck.py по написаних теках; лише звіт, non-fatal' },
  ],
}

/* ── args ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
const BOOK = _a && _a.book ? String(_a.book) : ''
const KIND = (_a && _a.kind) || 'book'             // book | catalog | reference | guide (= назва теки верхнього рівня)
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
/* basicIsSole — книга пише ТІЛЬКИ базові (її `_canon.md` це приписує, `detailed:empty` там норма).
   Тоді гейт «чи потрібна базова» НЕ ЗАСТОСОВНИЙ: він увесь міряє базову ПРОТИ детальної, а її нема
   й не буде, тож останній пункт («детальної нема на диску → skipBasic») спрацьовував би завжди.
   Саме на цьому book/chemistry втратив 3 теми з 6: половина авторів послухалася `_canon.md`,
   половина — гейта. Прапорець прибирає гейт: базова тут і Є стаття. */
const BASIC_IS_SOLE = !!(_a && _a.basicIsSole)
const UNITS_IN = (_a && Array.isArray(_a.units)) ? _a.units.filter((u) => u && u.slug && u.section) : null
if (!BOOK) throw new Error('args.book обовʼязковий')

/* ── EFFORT за характером матеріалу (Opus 5) ── ЗНИЖЕНО НА ЩАБЕЛЬ (було xhigh/max → стало high/xhigh):
   ліміт сесії тримається довше, а якість письма на цих щаблях лишається робочою.
   Проза («текст») — 'high'.
   Формули й код («тверде») — 'xhigh': математика, фізичне виведення, робочий код і довідка-API, де
   коректність важить більше за ціну. Перемикається однією правкою списків нижче або через args. */
const EFFORT_TEXT = (_a && _a.effortText) || 'high'
const EFFORT_HARD = (_a && _a.effortHard) || 'xhigh'
// Книги/курси, де ядро СТАТТІ — формули, виведення або робочий код (стаття цілком іде на EFFORT_HARD).
// Решта (electronics, communications, chemistry, philosophy, каталоги…) — проза з вкрапленнями: EFFORT_TEXT,
// а їхня математика й код усе одно потраплять на 'xhigh' через math-/proj-/api-вставки.
const HARD_BOOKS = new Set((_a && Array.isArray(_a.hardBooks)) ? _a.hardBooks : ['math', 'physics', 'algorithms', 'programming'])
// Типи вставок, де ядро — математика або код: math (виведення/доведення), proj (робочий код), api (довідка/протокол).
// hist (історія) і comp (клас пристроїв) — проза.
const HARD_INSERTS = new Set((_a && Array.isArray(_a.hardInserts)) ? _a.hardInserts : ['math', 'proj', 'api'])
// hist/comp — чиста проза без формул і коду: там зайвий щабель мислення не додає якости, лише ціну.
// Тому «мʼякі» вставки йдуть на щабель НИЖЧЕ, ніж статті (EFFORT_TEXT), — це окремий важіль.
const EFFORT_SOFT_INSERT = (_a && _a.effortSoftInsert) || 'medium'
const effortForUnit = () => (HARD_BOOKS.has(BOOK) ? EFFORT_HARD : EFFORT_TEXT)
const effortForInsert = (ins) => (HARD_INSERTS.has(String(ins && ins.type)) ? EFFORT_HARD : EFFORT_SOFT_INSERT)

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
const LIMIT_WAIT = 10 * 60 * 1000, LIMIT_MAX = 48   // стара поведінка (abortOnLimit:false): спати 10 хв і повторювати
const PROBE_WAIT = 5 * 60 * 1000                    // контрольна пауза перед вироком «стіна» (див. callAgent)

// опційні правила книги/курсу/каталогу: якщо у корені є _canon.md — читаємо ПЕРШОЮ дією й тримаємось (перевага над загальним)
const RULESNOTE = `\n\n📕 ADDITIONAL RULES for this ${KIND === 'guide' ? 'course' : KIND === 'catalog' ? 'catalog book' : KIND === 'reference' ? 'reference book' : 'book'} (optional). AS YOUR FIRST ACTION, Bash-check whether the file ${ROOT}\\${KIND}\\${BOOK}\\_canon.md exists. IF IT DOES — READ it IN FULL and follow it strictly: these are rules specific to «${BOOK}» on top of the general canon (a running example, unified terms and names, the language of examples, stylistic conventions); where _canon refines the general rule — _canon WINS. IF the file is ABSENT — there are no additional rules for this book, write by the general canon.`

/* ── Канон письма (загальні правила; повне — AUTHORING.md) ── */
const CANON = `WRITING CANON (condensed; full — ${ROOT}\\AUTHORING.write.en.md). ⚠️ OUTPUT LANGUAGE: the article/insert prose is written in UKRAINIAN — the rules below are in English, the text you produce is Ukrainian (see «Living Ukrainian»).
• Feynman method: deep, from first causes; intuition and «WHY» → details; give motivation whenever there is even a slight need. Build the conclusion before the reader's eyes. Analogies precise + where they break. Cause-and-effect chains, not lists. Respect the reader's intelligence — no «as if for toddlers», no pathos. Do NOT meta-comment the style (don't explain in the text WHY you write this way) — just write in it.
• CONTINUITY AND CLARITY (§4): each link reachable from the previous in ONE step (a skipped «obvious» step is a hole the reader falls through); NECESSITY BEFORE STATEMENT — lead from the problem/cause so it could not be otherwise; EXAMPLE ILLUSTRATES, doesn't carry (remove the code — the «why» remains); ONE LINE — depth goes DEEP, a neighbouring concept = sentence+link, not a section; NO FILLER — every sentence about the SUBJECT, not about the text/its depth/honesty/route; no closing recap. SENTENCE CLARITY: one thought per sentence, don't nest clauses; name a term AFTER its mechanism, not before; symmetric things in parallel structure.
• Living Ukrainian (the prose OUTPUT is Ukrainian): real words only, no russicisms/calques/officialese/random synonymy; one term per concept. Source of the name in parentheses at first encounter: «атом (гр. átomos — неподільний)».
• Flow: each paragraph a bridge from the previous; through-line why→intuition→details→example; before the end reread as a whole and smooth the seams.
• VERSIONS basic vs detailed (§3) — READ THIS, it is widely mis-done: detailed (-d.md) is THE full standalone article of the topic — always written, full depth. basic (.md, 500–1200 words) is a SHORT overview of the SAME topic (one core thread, ~half-a-minute read), NOT a separate article, NOT a subset, NOT «part 1» to the detailed's «part 2». a basic is needed RARELY — the default for a topic is basic:empty, and a basic is an exception you must justify. THE GATE — four "yes" answers and no disqualifier, decided WITH THE FINISHED DETAILED IN HAND: (1) SIZE, THREE ZONES on the detailed's PROSE — under 2250 words: NO basic · over 4000 words: a basic IS NEEDED unless signs 2–4 disqualify · 2250–4000: the meaning decides, i.e. signs 2–4 must all say yes. A ±10% TOLERANCE applies to these thresholds and to every band below — quality outweighs the number; (2) ONE CORE THREAD — you can state the topic's cause-and-effect core in ONE sentence and it stands without any of the parts you would drop; if the essence is a LIST of equal-weight things (variants, modes, fields, commands, steps), a shortened list is not an overview but a truncated reference — no basic; (3) THERE IS SOMETHING TO DROP — at least half of the detailed is derivations, variations, edge cases, examples; a skeleton detailed where every paragraph carries a new necessary fact does not compress, you would have to cut truth; (4) THE DETAILED IS NOT AN ENTRY POINT ITSELF — if its first two-three paragraphs already give the picture, the reader already has the entry. UNCONDITIONAL DISQUALIFIERS at any size: the topic is reference-like (core = API/protocol/format/parameter set/table); the topic is narrow, existing only as a detail of a bigger one. A 50/50 HESITATION MEANS NO. HARD SIZE RULE: a basic MUST be at least TWICE shorter than its detailed (basic_words ≤ detailed_words ÷ 2) AND within 500–1200 words (±10% tolerance, §3). If you cannot compress the gist to half the detailed without gutting it, the topic does not need a basic. Never inflate the detailed to «reach» the ratio and never pad the basic up to 600 words. LANGUAGE OF A BASIC — SIMPLER, the meaning IDENTICAL: simpler words and shorter sentences, less jargon and formalism, the term named AFTER its mechanism; you cut MATERIAL (derivations, variations, edge cases, most examples), NOT the truth — «almost right» simplifications that must later be unlearned are forbidden (better an honest «we take this as given, see the link»). Simpler ≠ infantile: no baby talk, no condescension. Test: a reader of the basic alone says CORRECT things about the topic, merely fewer of them.
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

/* ── СТІНА ЛІМІТУ: не пересиджуємо, а ПРИБИВАЄМО прогін ──────────────────────────────────────
   Було: 10-хв паузи × 48 (до 8 год). Насправді 2026-08-02 це дало 285 мертвих агентів із 382 —
   кожен устигав прочитати канон і теку, впертись у стіну й померти. Тепер перша ж стіна ставить
   прапорець WALL: нові агенти НЕ стартують, фази письма згортаються, прогін завершується з
   aborted:true. Що встигло — лишається на диску; чим його підняти, каже фінальний лог.
   Вимкнути (повернути стару поведінку з пересиджуванням) — args {abortOnLimit:false}. */
let WALL = null                      // { label, at } — перша стіна, що зупинила прогін
const ABORT_ON_LIMIT = !(_a && _a.abortOnLimit === false)

async function callAgent(prompt, opts) {
  if (WALL) return null              // стіна вже стоїть — навіть не починаємо
  let tries = 0, limitWaits = 0
  while (true) {
    let r = null, err = null
    try { r = await agent(prompt, opts) } catch (e) { r = null; err = e }
    if (r != null) { _nullStreak = 0; return r }
    _nullStreak++
    const emsg = String((err && err.message) || err || '')
    const isLimit = (_nullStreak >= NULL_STREAK_LIMIT) ||
      /session limit|usage limit|hit your|resets \d|quota|rate limit/i.test(emsg)
    if (isLimit) {
      if (ABORT_ON_LIMIT) {
        // Один контрольний удар: `_nullStreak` спрацьовує і на короткому збої, тож перш ніж
        // прибивати прогін, чекаємо PROBE_WAIT і пробуємо ще раз. Відповів — це було блимання;
        // мовчить удруге — це стіна, і далі молотити немає сенсу.
        if (limitWaits < 1) {
          limitWaits++
          log(`⏳ схоже на ліміт (${opts && opts.label}) — контрольна пауза ${PROBE_WAIT / 60000} хв і ОДНА повторна спроба`)
          await new Promise((res) => setTimeout(res, PROBE_WAIT))
          _nullStreak = 0
          continue
        }
        if (!WALL) {
          WALL = { label: (opts && opts.label) || '?', at: emsg.slice(0, 120) }
          log(`⛔ СТІНА ЛІМІТУ на «${WALL.label}» — після контрольної спроби тиша. Прогін ЗУПИНЯЮ, нові агенти не стартують.`)
          log(`   Написане лишається на диску. Стан підняти локально: node scripts\\batch-state.js --book ${BOOK} --kind ${KIND}`)
        }
        return null
      }
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
      // ⚠️ Під стіною ліміту цикл НЕ переривається, а швидко стікає: callAgent під WALL повертає null
      // МИТТЄВО (агента не породжує), тож fn дає результат правильної форми з ok:false.
      // Раніше тут стояв `if (WALL) break` — і масив лишався РІДКИМ. `.filter()` дірки пропускає,
      // тому фаза «Фігури» бачила порожній svgBad і рапортувала «усі 0 зауважень», нічого не полагодивши.
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
  ok: { type: 'boolean' }, skipBasic: { type: 'boolean' }, files: { type: 'array', items: { type: 'string' } }, note: { type: 'string' },
  inserts: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'type', 'brief'], properties: { file: { type: 'string' }, type: { type: 'string' }, brief: { type: 'string' } } } },
  newTopics: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['kind', 'book', 'section', 'slug', 'title'], properties: { kind: { type: 'string' }, book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, needDetailed: { type: 'boolean' } } } },
  needDetailedSelf: { type: 'boolean' },
  needBasicSelf: { type: 'boolean' },          // ЛИШЕ від автора ДЕТАЛЬНОЇ: чи варта тема базового огляду (етап 3)
  basicExists: { type: 'boolean' },            // ЛИШЕ від автора ДЕТАЛЬНОЇ: базова ВЖЕ на диску → не чіпаємо ні файл, ні статус
  deeperTargets: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['book', 'slug'], properties: { book: { type: 'string' }, slug: { type: 'string' } } } } } }
// newTopics і у вставці: вона лінкує за тим самим §6, отже так само може спертися на тему, якої ще
// нема. Без цього поля оголосити її не було чим — ref у прозі є, теми в маніфесті нема, лінк битий.
const INS_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, file: { type: 'string' }, note: { type: 'string' }, newTopics: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['kind', 'book', 'section', 'slug', 'title'], properties: { kind: { type: 'string' }, book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, needDetailed: { type: 'boolean' } } } } } }
const REG_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } }
// фаза «Маніфест»: агент повертає ще й підсумкові рядки локального патчера
const MFP_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' }, note: { type: 'string' } } }
const CTRL_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, problems: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'issue'], properties: { file: { type: 'string' }, issue: { type: 'string' } } } } } }

/* ──────────────── ЕТАП 0 — ЗРІЗ КАНОНУ (дешево, 1 агент) ────────────────
   AUTHORING.write.en.md — дослівний канон БЕЗ схем маніфесту й опису конвеєра (їх письменник не
   застосовує). Регенеруємо на старті КОЖНОГО прогону, щоб зріз не відстав від AUTHORING.en.md:
   інакше агенти читали б застарілі правила, а це рівно та шкода, якої ми уникаємо. */
phase('Канон')
await callAgent(
  `Механічна дія, нічого не пиши й не аналізуй. Bash: «node ${ROOT}\\scripts\\make-writer-canon.js».
Скрипт перегенерує ${ROOT}\\AUTHORING.write.en.md зі свіжого AUTHORING.en.md і надрукує рядок-підсумок.
Поверни ok (true ⟺ команда відпрацювала без помилки) і note (той рядок-підсумок).`,
  { label: 'зріз канону', phase: 'Канон', model: 'sonnet', effort: 'low', schema: MFP_RET })

/* ──────────────── ЕТАП 1 — СКАУТ (ПРІОРИТЕТ: detailed; basic лише добиває) ──────────────── */
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
Схема: book/catalog/reference — sections[]→topics[]; guide (v6) — modules[]→chapters[]→steps[]. В ОБОХ формах рядок секції/модуля містить "scope:", а тема/крок — { slug, title, basic:{status}, detailed:{status} } одним рядком; для guide поверни section = slug МОДУЛЯ. КРОК-ref (без slug) — ПРОПУСКАЙ.
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
  log(`Скаут: ${WORK.length}/${LIMIT} тем — детальних ${WORK.filter((u) => u.level === 'detailed').length} (пріоритет), базових ${WORK.filter((u) => u.level === 'basic').length} (добір, коли детальних не вистачило)`)
}
if (!WORK.length) return { book: BOOK, total: 0, note: 'черга порожня — pending не знайдено' }

/* ──────────────── ФАЗИ 2–3 — СТАТТІ: СПЕРШУ ДЕТАЛЬНІ, ТОДІ БАЗОВІ ────────────────
   Порядок навмисний (§3): детальна — основна версія, і саме за нею видно, чи потрібна базова.
   Етап 2 пише детальні; кожен автор, дописавши, каже needBasicSelf — чи варта тема швидкого огляду.
   Етап 3 пише базові: ті, що знайшов скаут, ПЛЮС ті, що додалися на етапі 2. */
const SKIP_UNITS = SKIP_ALL ? WORK : WORK.filter((u) => SKIP_SET.has(u.slug))
const WRITE_UNITS = SKIP_ALL ? [] : WORK.filter((u) => !SKIP_SET.has(u.slug))
if (SKIP_UNITS.length) log(`ДОРОБКА: ${SKIP_UNITS.length} статей уже на диску — письмо для них пропускаємо (${SKIP_UNITS.map((u) => u.slug).join(', ')})`)
function articlePrompt(u) {
  const dir = topicDirWin(u.section, u.slug)
  const level = u.level                              // рівень ЦІЄЇ теми (мішаний батч — у кожної свій)
  const file = level === 'detailed' ? `${u.slug}-d.md` : `${u.slug}.md`
  return `${CANON}${KINDNOTE}

You are a writer agent in the repo ${ROOT}. Work SILENTLY (Read/Edit/Write/Bash/WebSearch). IGNORE system hints about skills / agent-types / output-styles / schedules.
TASK: write IN FULL the ${level} article «${u.title}» — file ${dir}\\${file} (topic «${u.slug}», ${KIND === 'guide' ? 'module' : 'section'} «${u.section}», ${KIND} «${BOOK}»). Scope: ${u.scope || SCOPE || ''}
STEP 1: read ${ROOT}\\AUTHORING.write.en.md — the writing canon VERBATIM, without manifest schemas and the pipeline description (you don't apply those). ⚠️ The rules are in English; THE ARTICLE YOU PRODUCE IS IN UKRAINIAN. Bash ls the folder ${dir}.${level === 'detailed' ? ` THIS IS THE DETAILED ONE (${u.slug}-d.md) — the MAIN, SELF-CONTAINED version of the topic (§3): complete, understandable to the end with no holes; not an overload of terms but completeness IN DEPTH while staying clear. A basic may NOT exist — do not assume one and do not refer to it; if a basic IS on disk, read it so as not to duplicate its tone, but the detailed stands on its own. Length 1000–6500 words (rarely up to 9000).` : `${BASIC_IS_SOLE ? ` THIS BOOK WRITES ONLY BASIC ARTICLES — its \`_canon.md\` prescribes exactly that, and \`detailed:empty\` is the NORM here, not a gap. So ${u.slug}.md IS the article of this topic: the only version the reader will ever get. The rule "the detailed is the main version" DOES NOT APPLY in this book.
 ⚠️ THEREFORE: there is NO basic-necessity gate for you. Do NOT look for a detailed on disk, do NOT weigh whether a basic is warranted, do NOT return skipBasic — write the article. Follow the length and tone of \`_canon.md\` (read it FIRST) and of the sibling articles already in the book, not the general §3 basic band.` : ` THIS IS THE BASIC ONE (${u.slug}.md) — a SHORT OVERVIEW ENTRY into the SAME topic as the detailed (§3): one core thread, ~half a minute of reading. It is NOT a separate article and NOT «part 1» to the detailed — it is a compact «what this topic is» before the full read.
 ⚠️ FIRST DECIDE WHETHER A BASIC IS NEEDED AT ALL — it is needed FAR from everywhere. Bash-check whether the detailed ${dir}\\${u.slug}-d.md is on disk and measure it («wc -w»). THE GATE:
   • FOUR "YES" ANSWERS AND NO DISQUALIFIER; a topic's default is basic:empty, a basic is an exception you MUST justify. (1) SIZE — THREE ZONES on the detailed's PROSE: under 2250 words → NO basic · over 4000 words → a basic IS NEEDED, write it unless signs 2–4 disqualify · 2250–4000 → the meaning decides: signs 2–4 must ALL say yes, hesitation → no. ±10% TOLERANCE on these thresholds. (2) ONE CORE THREAD: you can state the topic's cause-and-effect core in ONE sentence and it stands without ANY of the parts you would drop; if the essence of the topic is a LIST of equal-weight things (variants, modes, fields, commands, steps of a procedure), do NOT write a basic: a shortened list is not an overview but a truncated reference. (3) THERE IS SOMETHING TO DROP: at least HALF of the detailed is derivations, variations, edge cases, examples; a skeleton detailed, where every paragraph carries a new necessary fact, does not compress — you would have to cut truth. (4) THE DETAILED IS NOT AN ENTRY POINT ITSELF: if its first 2–3 paragraphs already give the picture of the topic, the reader ALREADY has the entry.
   • UNCONDITIONAL DISQUALIFIERS (at any size): the topic is REFERENCE-LIKE (core = API/protocol/format/parameter set/table) · the topic is NARROW, existing only as a detail of a bigger one. ⚠️ "REFERENCE-LIKE" JUDGES THE CORE OF THIS ARTICLE, NOT THE KIND OF BOOK: a conceptual topic keeps its right to a basic even inside a ${KIND} book — reading this as "${KIND} book → no basics" is FORBIDDEN and is exactly what emptied the level (4 basics per 519 topics). A 50/50 HESITATION → do NOT write: "we didn't write one" costs the reader a single step into the detailed, "we wrote a needless one" is a second text about the same thing that must be kept in sync from then on.
   • If even one sign fails OR a disqualifier fires → do NOT write the basic. Do NOT create the file; return ok:true, skipBasic:true, note:"<which sign failed / which disqualifier>". The Manifest phase will set basic:empty.
   • HARD SIZE RULE: if you DO write the basic — it MUST be at least TWICE SHORTER than the detailed (basic_words ≤ detailed_words ÷ 2) AND within 500–1200 words (±10% tolerance, §3). If it doesn't compress to half the detailed without gutting the essence → the topic doesn't need a basic → skipBasic:true. Do NOT inflate the detailed to reach the ratio and do NOT pad the basic with water up to 600 words. Once written — VERIFY with Bash («wc -w» on both files) and cut the basic until it fits into half.
   • THE BASIC'S LANGUAGE IS SIMPLER, THE MEANING IDENTICAL (§3): simpler words, shorter sentences, less jargon and formalism, the term named AFTER its mechanism. You cut MATERIAL (derivations, variations, edge cases, most examples), NOT truth: "almost right" simplifications that must later be unlearned are FORBIDDEN — better an honest "we take this as given" + a link. Simpler ≠ infantile (no baby talk, no condescension). Test: someone who read ONLY the basic says CORRECT things about the topic — merely fewer of them.
   • The detailed is NOT on disk yet → skipBasic:true. A basic is decided ONLY with the finished detailed in hand (signs 1 and 3 cannot be checked without it); we do not guess in advance.`}`}
STEP 2 — WRITE the article file in full (§3–§5): ${level === 'detailed' ? 'DETAILED 1000–6500 words (rarely up to 9000), TYPICAL 2100–2600 — 6500 is the ceiling you almost never approach; over it — only a rare topic that truly demands it, up to 9000, not a target; land near 2100–2600 unless the topic genuinely earns more. Completeness IN DEPTH along ONE thread, every gap filled (not sideways onto neighbours)' : 'BASIC (only if STEP 1 did not yield skipBasic) 500–1200 words AND ≤ half the detailed, in SIMPLER language without losing meaning (§3) — a fast atom: one core thread, no second layer, no duplication of the detailed'}; Feynman; continuity (no gaps); necessity before statement; the example illustrates, doesn't carry; LIVING UKRAINIAN PROSE; worked examples in the language dictated by the domain (§5, NOT always C/C++; in programming/algorithms a non-web proj → C/C++ mandatory); 🔧 boxes; etymology in parentheses; your own figures (figs.py in the folder, RUN it — SVG into img/; tidy layout with margin; the svg gate to «0» is done by a SEPARATE pipeline step on Sonnet-high, you do NOT run svgcheck); facts — web-verified (§7).
 • **(v6) THE «BEFORE READING» BLOCK.** Immediately UNDER the H1 put a collapsed block \`<preknowlist>…</preknowlist>\` — a bullet list of ref links to PREREQUISITES (what one must know, without which the article makes no sense), each line = a link + briefly «what exactly to know». The links are 2-segment, to a TOPIC (\`book:<book>/<slug>\` or \`guide:<course>/<slug>\`, mirrored per §6), only WEIGHTY prerequisites. The list text itself is in UKRAINIAN. ${KIND === 'guide' ? 'COURSE: include only prerequisites from OUTSIDE the course OR not yet passed along the thread — do NOT add what the course already covered earlier.' : 'book/catalog: all genuine prerequisites (the article is standalone).'} If a prerequisite topic does not exist in the repo yet — treat it as a dependency (add it to newTopics, STEP 3).${KIND === 'catalog' ? `
 • **(§8) CATALOG — A CONCRETE OBJECT.** You describe this very thing (board/module/instrument/part): the reader must RECOGNIZE it, understand what it does and how it is built, how to connect/use it and what to beware of. Pick the sections YOURSELF to fit the device's nature; part numbers/models ARE appropriate (this is a catalog). NO sequence phrases. CATALOG LINKS — ALWAYS the book: prefix (the families live in __BOOKS__): a topic book:FAMILY/slug; an insert book:FAMILY/slug/TYPE-name.md. There is NO catalog: prefix, and do not use a catalog path link in the parentheses — only the book: popup.
 • **(§8) A BOARD/MODULE WITH A SCHEMATIC — MANDATORY.** If the thing has a device schematic OR a wiring schematic: (a) draw BOTH SVG figures — the schematic + the PIN-BY-PIN wiring (svgcheck 0); (b) describe them (power, levels, pull-ups, what goes where); (c) give the API in an api insert — add to inserts[] { file:"api-<name>.md", type:"api", brief:"API/reference: pinout+registers+protocol (hardware) and/or library/typical calls + working C/C++, pitfalls" }. Without these three a board/module article is INCOMPLETE. Bare passives/consumables (resistors, wires, solder) — no schematic/API, briefly by purpose.
 • **(§8) A FAMILY — LINK, DON'T REPEAT.** If the product belongs to a line of several variants (a shared vendor/architecture/history — ESP32, Arduino, RPi, the KY series…) — do NOT retell the shared history/architecture HERE. Put a ref popup to the family OVERVIEW article book:<family>/<family-slug> (e.g. book:boards/esp32-family) for the shared part and describe ONLY this product's specifics. No family topic exists — add to newTopics { kind:"catalog", book:"<family>", section:"<section>", slug:"<family-slug>", title:"Родина …" } (title in Ukrainian) and put a ref to it.` : ''}
STEP 3 — LINKS AND LISTS (the key part for the pipeline):
 • YOUR OWN INSERTS (a low decision threshold, but CONTEXTUAL — as many as the topic asks for). If the topic contains a sub-block worth unfolding separately (the history of its birth / a mathematical derivation / a code project / an algorithm walkthrough / a component class) — spin it out as an insert instead of squeezing it into the article. Hesitating «is it worth its own insert» — rather DO it, BUT the threshold is RAISED one notch (−10% inserts): a hesitation of exactly 50/50 → do NOT spin it out (leave it as a sentence in the article), and from this topic's candidate set DROP THE WEAKEST — the one whose layer adds least. There is NO quota on the count: put as many as the topic's logic asks for (one topic — no inserts at all, another — several of different types, when each is genuinely needed: hist/math/proj complement one another). Do NOT add for the sake of a number. The bar is quality: each carries its own layer, not a retelling of the article. Do NOT write the insert's content here. Instead: (a) place in the prose a ref popup [текст](${SELF}:${BOOK}/${u.slug}/<type>-<name>.md) — the link MUST carry the «.md» extension (without it the engine won't open it) — with a 1–7 sentence summary; (b) add it to inserts:[{file:"<type>-<name>.md", type:"hist|comp|math|proj|api", brief:"2–4 sentences: what exactly the insert must cover"}]. The NEXT phase will write it. ⚠️ EVERY insert you ref'd in the prose MUST be in inserts[] with the SAME file name — no ref without an entry (otherwise the file won't be created → a broken link).${KIND === 'catalog' ? ' (catalog — no comp-.)' : ''}${INSERT_BIAS}
 • NEW DEPENDENT TOPICS — PROACTIVELY, DO NOT RELY ON THE PLAN. The course/book plan is NOT 100% exhaustive — it is WHILE WRITING that you see best what is missing. Before finishing, go over the WEIGHTY concepts the article ASSUMES known or LEANS ON, and for each CHECK whether it exists in the repo: Bash grep by slug/title in ${ROOT}\\book\\*\\manifest.js and ${ROOT}\\guide\\*\\manifest.js (a finished one OR a pending/empty stub is enough). If a weighty concept is NOWHERE — that is a GAP in the plan: do NOT route around it (don't avoid the mention and don't leave bare inline text without a ref!), but REGISTER the topic — put a ref (book:<book>/<slug> or guide:<course>/<slug>) and add it to newTopics:[{kind,book,section,slug,title,needDetailed}] (title in UKRAINIAN). For book — a REAL existing section that fits best (a new section only if none of the existing ones fit); for guide — a module. If you link to the EXPLICIT DETAILED of a new topic (…/detail, rare) — needDetailed:true. A link to an insert file — with «.md». Do NOT create the file (the Manifest phase will register it; it filters duplicates). The bar is weight (§6): a genuine dependency without which the topic makes no sense, NOT every passing mention. Better to register one stub too many than to leave a hidden gap.${level === 'basic' ? `
 • THE DETAILED VERSION OF THIS TOPIC (§3, LOW THRESHOLD). Judge: does the topic have a REAL second layer — formula derivations, a protocol/algorithm, a many-sided architecture/hardware, many edge cases? If, while writing the basic, you were COMPRESSING material — set needDetailedSelf:true (the detailed will be queued). A simple reference/overview/narrow note — needDetailedSelf:false.` : ''}
${level === 'detailed' ? ` • DOES THIS TOPIC NEED A BASIC (§3) — YOU decide, because only you see the finished detailed.
   1) FIRST Bash-check whether a basic is ALREADY on disk: ${dir}\\${u.slug}.md. IF IT IS — set basicExists:true, needBasicSelf:false and do NOTHING with it: don't rewrite it, don't propose writing it; its manifest status won't be touched either. The decision ends there.
   2) IF THERE IS NO BASIC — run the §3 GATE. THE DEFAULT IS "NO"; needBasicSelf:true only when ALL FOUR signs hold and no disqualifier fired:
      (1) SIZE — THREE ZONES. Bash «wc -w» on ${dir}\\${u.slug}-d.md (prose; code blocks and markup inflate wc, so discount them by eye):
          • under 2250 words → needBasicSelf:false: a short detailed is itself the entry into the topic.
          • over 4000 words → the topic NEEDS a basic: set needBasicSelf:true unless signs 2–4 or a disqualifier kill it. Here "needed", not "allowed" — do not default to no.
          • 2250–4000 → the meaning decides: needBasicSelf:true only if signs 2–4 ALL hold; hesitation → false.
          • ±10% TOLERANCE on both thresholds (§3): 2100 words against the 2250 floor is a legitimate basic if the content asks for one. Quality outweighs the number.
          NEVER inflate the detailed to cross a zone boundary — the topic dictates the size, not the arithmetic.
      (2) ONE CORE THREAD — you can state the topic's cause-and-effect core in ONE sentence and it stands without ANY of the parts you would drop. If the essence of the topic is a LIST of equal-weight things (variants, modes, fields, commands, steps of a procedure), that is a disqualifier: a shortened list is not an overview but a truncated reference.
      (3) THERE IS SOMETHING TO DROP — at least HALF of your detailed is derivations, variations, edge cases, examples (material a basic may legitimately skip). If the detailed is a dense skeleton where every paragraph carries a new necessary fact, it does not compress: you would have to cut truth.
      (4) THE DETAILED IS NOT AN ENTRY POINT ITSELF — if your own first 2–3 paragraphs already give the picture of the topic, the reader ALREADY has the entry and a basic would only duplicate it.
      UNCONDITIONAL DISQUALIFIERS at any size: the topic is REFERENCE-LIKE (core = API/protocol/format/parameter set/table) · the topic is NARROW, existing only as a detail of a bigger one.
      ⚠️ "REFERENCE-LIKE" IS ABOUT THE CORE OF THIS ARTICLE, NOT ABOUT THE KIND OF BOOK. Ask: is the core of THIS topic an enumeration (API, fields, flags, error codes, a parameter table)? Do NOT ask whether the book is a ${KIND} book. «The scheduler: how the kernel divides time» has a cause-and-effect through-line and does NOT trip it, even inside a reference book; «The ioctl set of subsystem X» does. Reading it as "${KIND} book → basics never apply" is FORBIDDEN: measured 2026-08-09, that misreading left 4 basics across 519 reference/catalog topics while 30–36% of them passed sign 1 on size.
      A 50/50 HESITATION → needBasicSelf:false. "We didn't write a basic" costs the reader one step into the detailed; "we wrote a needless one" is a second text about the same thing that must be kept in sync from then on.
   3) If even one sign fails or a disqualifier fired — needBasicSelf:false, and name WHICH ONE in note: the topic will be marked basic:empty. This is the normal and MOST FREQUENT outcome.
` : ''} • DEEPER TARGETS (§6). If you point an EXPLICIT DETAILED link («…/detail», rare — mainly a ref from a course) at a topic that ALREADY EXISTS in the repo but has only a basic — add that topic to deeperTargets:[{book,slug}] (so its detailed gets queued). Leave the link on /detail.
 • DO NOT TOUCH THE MANIFEST. Do NOT write the inserts yourself (that is a separate stage).
STEP 4 — SELF-AUDIT: figures generated (figs.py run, SVG in img/; the svg gate to «0» is a separate Sonnet step, not yours); length within the §3 band; no LaTeX and no «Рис.»; ${KIND === 'guide' ? "the course thread is apt (backwards only)" : 'self-contained, no sequence phrases'}; the prose is LIVING UKRAINIAN.
Return: ok, skipBasic (ONLY for a basic: true ⟺ you did NOT write the basic because it would duplicate the detailed — no file created; §3), files (article+figures), inserts (your inserts for the «Вставки» stage), newTopics (new dependent topics to register), ${level === 'detailed' ? 'basicExists (a basic is already on disk → we change nothing) and needBasicSelf (the §3 GATE above — four signs, default "no"; name the failing sign in note), ' : 'needDetailedSelf (is this topic worth a detailed, §3), '}deeperTargets (existing topics linked as /detail, §6), note.`
}
// Списки з args (доробка) — стартова база; далі ДОДАЄМО те, що повернуть агенти дописаних статей.
const DETAILED_NEED = (DETAILED_IN || []).map((d) => ({ book: d.book || BOOK, slug: d.slug }))
let doneArticles = SKIP_UNITS.slice()
let INSERTS = (INSERTS_IN || []).slice()
let NEWTOPICS = (NEWTOPICS_IN || []).slice()
let BASIC_EMPTY = []            // базову навмисно НЕ пишемо (дублювала б детальну) → basic:empty у маніфесті
let BASIC_REQUEUE = []          // базова була в черзі етапу 3, але агент не впорався → basic лишається/стає pending

/** Один етап письма: пул агентів, збір усього, що вони повернули. */
async function runArticles(units, phaseName) {
  if (!units.length) return { wrote: [], skipped: [], failed: [] }
  phase(phaseName)
  log(`${phaseName} (opus effort=${effortForUnit()} — «${BOOK}» ${HARD_BOOKS.has(BOOK) ? 'формули/код' : 'проза'}, стагер ${STAGGER / 1000}с): ${units.length} тем (${KIND}/${BOOK})`)
  const res = await staggered(units, (u) =>
    callAgent(articlePrompt(u), { label: `${u.level === 'detailed' ? 'детальна' : 'базова'}:${u.slug}`, phase: phaseName, model: 'opus', effort: effortForUnit(), schema: ART_RET })
      .then((pr) => ({ u, ok: !!(pr && pr.ok), skipBasic: !!(pr && pr.skipBasic), inserts: (pr && pr.inserts) || [], newTopics: (pr && pr.newTopics) || [], needBasicSelf: !!(pr && pr.needBasicSelf), basicExists: !!(pr && pr.basicExists), needDetailedSelf: !!(pr && pr.needDetailedSelf), deeperTargets: (pr && pr.deeperTargets) || [], note: pr && pr.note }))
      .catch(() => ({ u, ok: false, skipBasic: false, inserts: [], newTopics: [], needBasicSelf: false, basicExists: false, needDetailedSelf: false, deeperTargets: [] })))
  const okR = res.filter((r) => r.ok)
  const skipped = okR.filter((r) => r.skipBasic && r.u.level === 'basic')     // файл НЕ створено
  const wrote = okR.filter((r) => !(r.skipBasic && r.u.level === 'basic'))
  const failed = res.filter((r) => !r.ok)
  doneArticles = doneArticles.concat(wrote.map((r) => r.u))
  BASIC_EMPTY = BASIC_EMPTY.concat(skipped.map((r) => r.u))
  INSERTS = INSERTS.concat(wrote.flatMap((r) => r.inserts.map((i) => ({ ...i, section: r.u.section, topicSlug: r.u.slug, topicTitle: r.u.title }))))
  NEWTOPICS = NEWTOPICS.concat(wrote.flatMap((r) => r.newTopics))             // §6: нові теми зʼявляються на БУДЬ-ЯКОМУ етапі
  for (const r of wrote) if (r.u.level === 'basic' && r.needDetailedSelf) DETAILED_NEED.push({ book: BOOK, slug: r.u.slug })
  for (const r of wrote) for (const d of (r.deeperTargets || [])) if (d && d.slug) DETAILED_NEED.push({ book: d.book || BOOK, slug: d.slug })
  log(`${phaseName}: дописано ${wrote.length}/${units.length}${skipped.length ? `; базових пропущено (дублювали б детальну → empty): ${skipped.length}` : ''}${failed.length ? `; не вдалося: ${failed.length}` : ''}`)
  return { wrote, skipped, failed }
}

/* ЕТАП 2 — ДЕТАЛЬНІ */
const D_UNITS = WRITE_UNITS.filter((u) => u.level === 'detailed')
const dRes = await runArticles(D_UNITS, 'Детальні')

/* ЕТАП 3 — БАЗОВІ. Рішення етапу 2 має РІВНО три виходи (§3):
     • базова ВЖЕ написана (basicExists) → НЕ чіпаємо нічого: ні файла, ні статусу, ні черги;
     • базової нема й вона потрібна (needBasicSelf) → у чергу цього ж прогону, етап 3 її пише;
     • базової нема й вона не потрібна → basic:empty (лише якщо стояло pending — інших статусів не рухаємо). */
const B_UNITS = WRITE_UNITS.filter((u) => u.level === 'basic').map((u) => ({ ...u, level: 'basic' }))
const _seenB = new Set(B_UNITS.map((u) => `${u.section}/${u.slug}`))
const BASIC_FROM_DETAILED = [], BASIC_KEPT = []
for (const r of dRes.wrote) {
  if (r.basicExists) { BASIC_KEPT.push(r.u); continue }                       // написана — не чіпаємо
  const k = `${r.u.section}/${r.u.slug}`
  if (r.needBasicSelf && !_seenB.has(k)) { _seenB.add(k); const unit = { ...r.u, level: 'basic' }; B_UNITS.push(unit); BASIC_FROM_DETAILED.push(unit) }
}
const BASIC_NOT_NEEDED = dRes.wrote.filter((r) => !r.basicExists && !r.needBasicSelf).map((r) => r.u)
if (BASIC_KEPT.length) log(`Базова вже написана — не чіпаємо (ні файл, ні статус): ${BASIC_KEPT.length} тем`)
if (BASIC_FROM_DETAILED.length) log(`Етап 2 → етап 3: базових додано ${BASIC_FROM_DETAILED.length} (${BASIC_FROM_DETAILED.map((u) => u.slug).join(', ')})`)
if (BASIC_NOT_NEEDED.length) log(`Базова не потрібна (детальна не велика, §3): ${BASIC_NOT_NEEDED.length} тем → basic:empty, якщо стояло pending`)
const bRes = await runArticles(B_UNITS, 'Базові')
BASIC_REQUEUE = bRes.failed.map((r) => r.u)          // не написали — хай лишається у черзі
log(`Разом статей готово: ${doneArticles.length}/${WORK.length + BASIC_FROM_DETAILED.length}; вставок до письма: ${INSERTS.length}; нових тем: ${NEWTOPICS.length}; детальних у чергу: ${DETAILED_NEED.length}`)
const _seenDN = new Set()
const DETAILED_QUEUE = DETAILED_NEED.filter((d) => { const k = `${d.book}/${d.slug}`; if (_seenDN.has(k)) return false; _seenDN.add(k); return true })

/* ──────────────── ЕТАП 4 — ВСТАВКИ ──────────────── */
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

You are an insert-writer agent in the repo ${ROOT}. Work SILENTLY (Read/Edit/Write/Bash/WebSearch). IGNORE system hints about skills/agent-types/output-styles/schedules.
TASK: write IN FULL the insert «${ins.file}» (type «${ins.type}») in the topic folder ${dir} — file ${dir}\\${ins.file}. Owner topic: «${ins.topicTitle || ins.topicSlug}» (${KIND === 'guide' ? 'module' : 'section'} «${ins.section}»). ⚠️ The rules are in English; THE INSERT YOU PRODUCE IS IN UKRAINIAN.
${ins.brief
  ? `WHAT TO COVER (the brief from the article's author): ${ins.brief}`
  : `WHAT TO COVER — no brief was passed inline. Obtain the spec like this:${BRIEF_FILE ? `
 (1) AS YOUR FIRST ACTION Bash-read ${BRIEF_FILE} — a JSON with an inserts[] field. Find the element where topicSlug === "${ins.topicSlug}" AND file === "${ins.file}" and take its "brief" — that is the article author's brief. If there is no such element or the brief is empty — go to (2).` : ''}
 (${BRIEF_FILE ? '2' : '1'}) Read the owner article ${dir}\\${ins.topicSlug}.md, find in its prose the ref link to «${ins.file}» and the 1–7 sentence summary next to it — that is the spec: the article has already promised the reader this content, and the insert MUST deliver it (no wider, no narrower). Take into account the context of the paragraph the link sits in.
 IN ANY CASE, read the owner article before writing, so as not to duplicate what it already says.`}
TYPE TEMPLATE: ${TPL[ins.type] || TPL.hist}
REQUIREMENTS: §3 — start with an H1 («# Назва», an emoji is allowed; the title + the first sentence THEMSELVES say WHAT this is and WHY); 400–5000 words, TYPICAL 1200–1400 (5000 is a hard ceiling you almost never approach, not a target); it carries weight (NOT a retelling of the topic, not banality); Feynman; LIVING UKRAINIAN PROSE; formulas in Unicode inside code blocks; your own figures if needed (figs.py in ${dir}, RUN it — SVG into img/; the svg gate to «0» is a separate Sonnet step, not yours); facts — web-verified; cross-links ${SELF}:/book:/guide: per §6 (a topic/step — 2 segments, the general link; an explicit detailed — a 3rd segment /detail; an insert <type>-<name>.md — with «.md»). The insert carries NO back-links to its owner article (do NOT link back to «${ins.topicSlug}»). DO NOT TOUCH THE MANIFEST.
 • NEW DEPENDENT TOPICS — same as for an article author (§6). If you lean on a weighty concept that is NOT IN THE REPO (Bash-grep by slug/title in ${ROOT}\\book\\*\\manifest.js and ${ROOT}\\guide\\*\\manifest.js — a pending/empty stub is enough), do NOT route around the mention and do NOT leave bare text without a ref: put a ref (book:<book>/<slug>) and add the topic to newTopics:[{kind,book,section,slug,title,needDetailed}] (title in UKRAINIAN) — take a REAL existing section that fits best. Do NOT create the file (the «Маніфест» phase will register it; it filters duplicates). The bar is a genuine dependency without which the insert makes no sense, NOT every passing mention.
Return: ok, file, note, newTopics (new dependent topics to register; [] if none).`
}
if (INSERTS.length) {
  const _hard = INSERTS.filter((i) => HARD_INSERTS.has(String(i.type))).length
  log(`Вставки (opus, стагер ${STAGGER / 1000}с): ${INSERTS.length} — формули/код (${[...HARD_INSERTS].join('/')}) на effort=${EFFORT_HARD}: ${_hard}; проза (hist/comp) на effort=${EFFORT_SOFT_INSERT}: ${INSERTS.length - _hard}`)
}
const iResults = INSERTS.length
  ? await staggered(INSERTS, (ins) =>
      callAgent(insertPrompt(ins), { label: `вставка:${ins.topicSlug}/${ins.file}`, phase: 'Вставки', model: 'opus', effort: effortForInsert(ins), schema: INS_RET })
        .then((pr) => ({ ins, ok: !!(pr && pr.ok), newTopics: (pr && pr.newTopics) || [] }))
        .catch(() => ({ ins, ok: false, newTopics: [] })))
  : []
// нові теми, оголошені ВСТАВКАМИ, — у ту саму чергу на реєстрацію, що й з статей
NEWTOPICS = NEWTOPICS.concat(iResults.filter((r) => r.ok).flatMap((r) => r.newTopics))
// написані ЦИМ прогоном + уже написані раніше (insertsDone) — і ті, і ті йдуть на реєстрацію
const doneInserts = iResults.filter((r) => r.ok).map((r) => r.ins).concat(INSERTS_DONE_IN || [])
log(`Вставок готово: ${iResults.filter((r) => r.ok).length}/${INSERTS.length}${INSERTS_DONE_IN && INSERTS_DONE_IN.length ? ` (+${INSERTS_DONE_IN.length} написаних раніше — лише реєстрація)` : ''}`)

/* ──────────────── ЕТАП 5 — ФІГУРИ (локальний svgcheck + правки) ──────────────── */
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
КРОК1 — ОДНА ЛОКАЛЬНА КОМАНДА (нічого не читай і не грепай руками): «python ${ROOT}\\scripts\\svgcheck.py ${dir} --min-font 8 --links». Скрипт САМ звіряє .md-підключення з img/ і перевіряє геометрію (шрифт, текст↔текст, лінія/контур↔текст, напис за полотном, зіткнення блоків). Читай ЛИШЕ його вивід:
 (а) «SVG перевірено: 0» і жодного MISS — фігур тут не передбачено: поверни ok:true, fixed:0, note:"нема фігур".
 (б) «із зауваженнями: 0» і жодного MISS — ok:true, fixed:0, БІЛЬШЕ НІЧОГО НЕ РОБИ (не відкривай файлів).
 (в) є WARN, а img/ порожній чи figs.py не запускався — «python figs.py» (з теки ${dir}), тоді знову ту саму команду; далі КРОК2.
 (г) ⚠️ рядки «MISS <md>: підключено img/<файл>, а файлу НЕМА» — стаття обіцяє фігуру, якої ніхто не створить. Якщо figs.py нема — НАПИШИ ${dir}\\figs.py; якщо Є, але не робить підключених svg — ДОПИШИ в наявний figs.py генерацію РІВНО відсутніх файлів (не чіпаючи вже робочі фігури). Імена — точно як у лінках .md (у ./img/), за §5 канону: чистий Python без залежностей, на початку (для нового файла) «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *», рамки з текстом — ЛИШЕ textbox()/fitbox(). ЗМІСТ фігури бери з .md, що її підключає (стаття АБО вставка — знайди файл із цим лінком у теці): зроби саме те, що обіцяє підпис і абзац навколо (фігура несе вагу, не декор). Тоді «python figs.py» і КРОК2. .md НЕ правь — підлаштовуй фігури під нього.
КРОК2 (лише якщо є зауваження): відкрий ${dir}\\figs.py і ПРАВ РОЗКЛАДКУ, не зміст — розсунь підписи (ширші клітини/колонки, більший viewBox), веди лінії ПОВЗ написи, не втискай довгі рядки поруч, скороти/переанкори написи, що вилазять за полотно (довгий рядок із text-anchor="end" біля лівого краю), рознеси блоки, що налазять; рамки з текстом — ЛИШЕ через textbox()/fitbox() зі svgkit (він у ${ROOT}\\scripts). Зміст/сенс фігури НЕ міняй. Скрипт друкує КООРДИНАТИ проблеми — правь саме там, не перебудовуй фігуру.
КРОК3: «python figs.py» (з ${dir}), тоді знову ту саму перевірку. Повторюй КРОК2–3, доки «із зауваженнями: 0» (щонайбільше ${SVG_TRIES} ітерацій). НЕ чіпай .md статті, вставки й маніфест — ЛИШЕ figs.py та img/.
Поверни: ok (true ⟺ кінцево «0 зауважень» або фігур нема), fixed (скільки фігур виправив), note (що зробив; якщо не довів до 0 — яке зауваження лишилось і де).`
}
let svgResults = []
if (FIG_DIRS.length) {
  // ПЕРЕДГЕЙТ — один дешевий агент проганяє ЛОКАЛЬНИЙ svgcheck по ВСІХ теках батчу однією командою
  // і каже, які теки взагалі мають проблему. Чисті теки далі не йдуть: дорогий sonnet-фіксер
  // запускається лише там, де є що правити (раніше агент відкривався на кожну теку — марні токени).
  const PRE_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, bad: { type: 'array', items: { type: 'string' } }, note: { type: 'string' } } }
  const dirsSh = FIG_DIRS.map((d) => `"${ROOT.replace(/\\/g, '/')}/${KIND}/${BOOK}/${d}"`).join(' ')
  const pre = await callAgent(
    `Ти — передгейт фігур. Зроби РІВНО ОДИН Bash-виклик і НІЧОГО не читай:
for d in ${dirsSh}; do echo "== $d"; python "${ROOT.replace(/\\/g, '/')}/scripts/svgcheck.py" "$d" --min-font 8 --links; done
У виводі кожен блок «== <шлях>» закінчується рядком «SVG перевірено: N; із зауваженнями: M». Поверни bad — масив тек у форматі «<секція>/<slug>» (останні два сегменти шляху) для тих блоків, де M > 0 АБО є рядок «MISS». Теки з «із зауваженнями: 0» і без MISS у bad НЕ клади. note — один рядок підсумку.`,
    { label: `передгейт svg ×${FIG_DIRS.length}`, phase: 'Фігури', model: 'sonnet', effort: 'low', schema: PRE_RET })
  const badSet = new Set((pre && Array.isArray(pre.bad) ? pre.bad : FIG_DIRS).map(String))
  const FIG_TARGETS = pre && Array.isArray(pre.bad) ? FIG_DIRS.filter((d) => badSet.has(d)) : FIG_DIRS
  log(`SVG-передгейт (локальний svgcheck): ${FIG_DIRS.length} тек → правити ${FIG_TARGETS.length}${pre && pre.note ? ` (${String(pre.note).slice(0, 160)})` : ''}`)
  if (FIG_TARGETS.length) {
    log(`SVG-гейт (sonnet high, стагер ${STAGGER / 1000}с): ${FIG_TARGETS.length} тек`)
    svgResults = await staggered(FIG_TARGETS, (d) =>
      callAgent(svgPrompt(d), { label: `svg:${d}`, phase: 'Фігури', model: 'sonnet', effort: 'high', schema: SVG_RET })
        .then((pr) => ({ d, ok: !!(pr && pr.ok), fixed: (pr && pr.fixed) || 0, note: pr && pr.note }))
        .catch(() => ({ d, ok: false, fixed: 0 })))
  }
  const svgFixed = svgResults.reduce((s, r) => s + (r.fixed || 0), 0)
  const svgBad = svgResults.filter((r) => !r.ok)
  log(`SVG-гейт: тек ${FIG_DIRS.length} (правилось ${FIG_TARGETS.length}), виправлено фігур ${svgFixed}${svgBad.length ? `; НЕ доведено до 0: ${svgBad.map((r) => r.d).join(', ')}` : '; усі «0 зауважень»'}`)
}

/* ──────────────── ЕТАП 6 — МАНІФЕСТ (локальний патчер, БЕЗ читання маніфесту агентом) ────────────────
   Раніше тут працювали 5 opus-агентів: кожен ЧИТАВ маніфест (60+ КБ) і робив точкові Edit-и — десятки
   тисяч токенів на суто механічну роботу. Тепер воркфлоу сам будує список операцій, а єдиний дешевий
   агент лише кладе його файлом і запускає scripts/manifest-patch.js: патчер детермінований,
   ідемпотентний і сам валідує результат (не парситься → не пише). */
phase('Маніфест')
const OPS = new Map()                                   // «kind/book/manifest.js» → операції
const pushOp = (rel, op) => { if (!OPS.has(rel)) OPS.set(rel, []); OPS.get(rel).push(op) }
for (const u of doneArticles) pushOp(MF, { op: 'status', slug: u.slug, ver: u.level, status: 'done' })
for (const u of BASIC_EMPTY) pushOp(MF, { op: 'status', slug: u.slug, ver: 'basic', status: 'empty' })   // §3: базова дублювала б детальну
// етап 2 сказав «базова не потрібна» (детальна не велика) — знімаємо базову з черги, якщо вона там стояла
for (const u of BASIC_NOT_NEEDED) pushOp(MF, { op: 'status-if', slug: u.slug, ver: 'basic', from: 'pending', to: 'empty' })
// базова була в черзі етапу 3, але агент не впорався — хай лишається у черзі на наступний прогін
for (const u of BASIC_REQUEUE) pushOp(MF, { op: 'status-if', slug: u.slug, ver: 'basic', from: 'empty', to: 'pending' })
for (const i of doneInserts) pushOp(MF, { op: 'insert', slug: i.topicSlug, section: i.section, type: i.type, file: i.file, status: 'done' })
for (const t of NEWTOPICS) {                            // §3/§6: нова тема — ЗАВЖДИ basic:empty + detailed:pending
  const rel = `${t.kind || 'book'}/${t.book}/manifest.js`
  pushOp(rel, { op: 'topic', section: t.section, slug: t.slug, title: t.title || t.titleHint || t.slug })
  // …КРІМ книг, що пишуть лише базові: там detailed:empty — норма за їхнім `_canon.md`, і тема,
  // заведена як detailed:pending, стала б у чергу, якої в цій книзі не існує. Перевертаємо пару.
  if (BASIC_IS_SOLE && (t.book === BOOK || !t.book)) {
    pushOp(rel, { op: 'status', slug: t.slug, ver: 'detailed', status: 'empty' })
    pushOp(rel, { op: 'status', slug: t.slug, ver: 'basic', status: 'pending' })
  }
}
for (const d of DETAILED_QUEUE) pushOp(`book/${d.book}/manifest.js`, { op: 'status-if', slug: d.slug, ver: 'detailed', from: 'empty', to: 'pending' })

if (OPS.size) {
  const jobs = [...OPS.entries()].map(([rel, ops], i) => ({
    rel, ops, file: `${ROOT}\\scripts\\_mfops-${BOOK}-${i}.json`,
    mf: `${ROOT}\\${rel.replace(/\//g, '\\')}`,
  }))
  const total = jobs.reduce((s, j) => s + j.ops.length, 0)
  log(`Маніфест (локальний патчер): ${total} операцій у ${jobs.length} маніфест(ах) — агент лише кладе JSON і запускає скрипт`)
  const r = await callAgent(
    `Ти — механічний виконавець. НЕ читай і НЕ редагуй маніфести — усе зробить локальний скрипт.
Для КОЖНОГО завдання нижче: (1) Write-ом поклади JSON-масив ops ДОСЛІВНО у вказаний файл (нічого не міняй у тексті, не перекладай, не переформульовуй назви); (2) Bash: «node ${ROOT}\\scripts\\manifest-patch.js <manifest> --ops <файл>».
Скрипт сам знаходить теми, ставить статуси, реєструє вставки й додає нові теми (basic:empty + detailed:pending), пропускає вже наявне й валідує маніфест — якщо він друкує «✖», просто перекажи це у note.
ЗАВДАННЯ:
${jobs.map((j, k) => `${k + 1}) файл ops: ${j.file}\n   маніфест: ${j.mf}\n   ops: ${JSON.stringify(j.ops)}`).join('\n')}
Поверни ok (true ⟺ усі команди відпрацювали), count (скільки операцій застосовано за звітами скрипта), note (рядки-підсумки скрипта; ✖-помилки, якщо були).`,
    { label: `маніфест-патч ×${total}`, phase: 'Маніфест', model: 'sonnet', effort: 'low', schema: MFP_RET })
  log(`Маніфест: застосовано ${(r && r.count) || 0}/${total} операцій${r && r.note ? ` — ${String(r.note).slice(0, 300)}` : ''}`)
}

/* ──────────────── ЕТАП 7 — КОНТРОЛЬ (§3-обсяг, пари база↔деталь, фігури; лише звіт) ──────────────── */
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
ПЕРЕВІРКА 1 — ОБСЯГ §3: Bash «node ${ROOT}\\scripts\\wordcount.js ${KIND}/${BOOK} --all». У виводі знайди ЛИШЕ файли з ТЕК цього батчу, що позначені як поза смугою (замало/забагато слів за §3: базова 500–1200, детальна 1000–6500, вставка 400–5000; допуск ±10%, у виводі це «~» — не порушення). ОКРЕМО подивись блок «ПАРИ базова↔детальна»: рядок «✖ ПОРУШЕННЯ» для теми ЦЬОГО батчу — це порушення заліза §3 (базова МУСИТЬ бути ≤ ½ прози своєї детальної); занось його у problems як issue «базова >½ детальної (NN%) — скоротити базову або basic:empty».
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
const PLANNED = WORK.length + BASIC_FROM_DETAILED.length     // скаут + базові, додані етапом «Детальні»
if (WALL) {
  log(`⛔ ПРОГІН ОБІРВАНО СТІНОЮ ЛІМІТУ (на «${WALL.label}»). Написане — на диску, але фази «Фігури» й «Маніфест» НЕ відпрацювали:`)
  log(`   1) node scripts\\batch-state.js --book ${BOOK} --kind ${KIND}          → що готове / чого бракує + payload на доробку`)
  log(`   2) node scripts\\batch-state.js --book ${BOOK} --kind ${KIND} --apply  → зареєструвати написане в маніфесті (локально, без агентів)`)
  log(`   Відновлювати прогін — лише за твоєю командою, свіжим батчем зі скриптовим payload.`)
}
return { aborted: !!WALL, wall: WALL || undefined, book: BOOK, kind: KIND, level: FORCE_LEVEL || 'mixed', byLevel: { detailed: doneArticles.filter((u) => u.level === 'detailed').length, basic: doneArticles.filter((u) => u.level === 'basic').length }, scouted: WORK.length, basicFromDetailed: BASIC_FROM_DETAILED.length, basicKept: BASIC_KEPT.length, articles: okN, articlesFailed: Math.max(0, PLANNED - okN - BASIC_EMPTY.length), basicSkipped: BASIC_EMPTY.length, basicNotNeeded: BASIC_NOT_NEEDED.length, inserts: insWritten, insertsRegisteredOnly: (INSERTS_DONE_IN || []).length, insertsFailed: INSERTS.length - insWritten, newTopics: NEWTOPICS.length, detailedQueued: DETAILED_QUEUE.length, svgFixed: svgFixedTotal, svgUnresolved, problems: PROBLEMS }
