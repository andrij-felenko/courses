export const meta = {
  name: 'complete-module',
  description: 'Завершити модуль будь-якої книги: Opus поглиблює скелет → веб-перевірка фактів → Sonnet пише фінальну прозу (🧮-математику — Opus; без окремої вичитки). args = {book, module} або номер модуля (book="embedded").',
  phases: [
    { title: 'Скаут', detail: 'прочитати кореневий індекс + per-module manifest.js, зібрати одиниці зі статусом empty/update' },
    { title: 'Каркас', detail: 'Opus планує і ПОГЛИБЛЮЄ скелет; важкі — двопрохідно (draft → критик)' },
    { title: 'Факти', detail: 'веб-перевірка дат/імен/атрибуцій (Opus — історії/першість, Sonnet — решта; лише за наявності claims)' },
    { title: 'Проза', detail: 'Sonnet пише фінальну якість одразу (🧮-вставки — Opus, Фейнман-глибоко); фігури звіряє svgcheck, без LLM-переогляду SVG' },
    { title: 'Статуси', detail: 'переставити status відповідних записів у per-module manifest.js на done' },
  ],
}

/* ── args: число / рядок "5" / JSON / {book, module|n [, limit, only]} ──
   book ∈ embedded|chem|math|components ; module = n. Голе число → book="embedded". */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) {} }
let BOOK = 'embedded', N, LIMIT = 0, ONLY = '', RETRY_WAIT = 60000, MAX_TRIES = 30
if (_a && typeof _a === 'object') {
  if (_a.book) BOOK = String(_a.book)
  N = Number(_a.module != null ? _a.module : _a.n); LIMIT = Number(_a.limit) || 0; ONLY = _a.only || ''
  if (_a.retryWaitMs != null) RETRY_WAIT = Number(_a.retryWaitMs)   // пауза між стуками (за умовч. 60 с)
  if (_a.maxTries != null) MAX_TRIES = Number(_a.maxTries)         // скінченний cap (за умовч. 30)
} else { N = Number(_a) }
if (!N || N < 1) throw new Error('Передай модуль: args = N (book="embedded") або {book, module:N, limit:K} для проби')

const ROOT = 'E:\\develop\\courses'
const ROOT_FS = 'E:/develop/courses'   // прямі слеші для шляхів усередині скрипта

/* Кореневі індекси книг: base-тека + файл-індекс. */
const BOOKS = {
  embedded:   { index: `${ROOT_FS}/manifest.js`,      base: 'embedded/' },
  chem:       { index: `${ROOT_FS}/manifest-chem.js`, base: 'chemistry/' },
  math:       { index: `${ROOT_FS}/manifest-math.js`, base: 'math/' },
  components: { index: `${ROOT_FS}/manifest-comp.js`, base: 'components/' },
}
const BK = BOOKS[BOOK]
if (!BK) throw new Error(`book має бути embedded|chem|math|components, а не "${BOOK}"`)

/* ── Спільний канон (ІДЕНТИЧНИЙ префікс у всіх агентів → кеш; читати AUTHORING не треба) ── */
const CANON = `КАНОН (стисло; повне — ${ROOT}\\AUTHORING.md, читати НЕ обов'язково):
• Українською, стиль Фейнмана: глибоко, від першопричин, інтуїція→деталі; без «як для 4-річного», без пафосу. Жива мова — без кальок, русизмів, канцеляриту; один термін на поняття в межах файлу.
• Нумерація М.Р.Т: заголовки тем «## М.Р.Т Назва»; підписи фігур «Рис. М.Р.Т.k» (в історіях «Рис. М.Р.Тi.k»).
• Обсяги (без код-блоків): тема — мінімум 1800–2500, звичайна 2500–4500, важка до ~9000 (складність теми — критерій, не бажання скоротити); вставка 🔌 — 300–800, 🧮/⚙️ — 300–1000; історія 📜 — 2000–8000.
• Формули — Unicode у код-блоках (10⁻⁹, ε, ≈, ², ₀, ·), без LaTeX; десятковий роздільник — крапка.
• Біля важливих понять — рамка «> 🔧 Навіщо це»; worked-приклад — жирний підпис + код-блок із покроковим обчисленням.
• КОД у прикладах і ⚙️-вставках — реальний C/C++ (прошивка ESP32), НЕ псевдокод: короткий, коректний, компільований фрагмент.
• Двомовні терміни: «провідність (conductivity, σ)». Не забігати вперед (лише цей і попередні розділи); назад — «§М.Р.Т». Кінець розділу (остання тема) — «> ▶️ Далі: …» без пояснення змісту.
• ГОЛОС (§3): загально й абстрактно; НЕ прив'язувати до конкретних залізних плат і не називати part numbers — узагальнено «давач відстані», «драйвер мотора». ESP32 і ArduPilot називати можна.
• ФІГУРИ — стиль SVG (§1): білий фон; «+» червоний, «−» синій; поле зелене; стрілки через marker; шрифт sans-serif.
• ІСТОРІЯ 📜 (§5): заголовки — назви тем («### Бурштин і перша загадка статики»), НЕ «Питання 0/1…»; щедро — до кожного розділу кілька; якщо «нема» — копати глибше; тільки справжня історія, не вигадана.
• ФАКТИ: будь-яке історичне/фактичне твердження (дата, ім'я, «хто перший», винахід, патент, національність/походження) — ЛИШЕ за підтвердженими даними зі стадії «Факти». Якщо вони дали корекцію — пиши скориговано й познач статус доказовості (усталено / спірно / імперсько-національне обрамлення / міф). Не клей ярлик «російське», коли джерела дають точніше (українець, поляк, серб, єврей, грузин, вірменин, балт…); розрізняй ідею / теорію / робочу реалізацію / систему / патент.
• ФІГУРИ — чистий Python → ./img/*.svg, кожна несе вагу. Спільний kit імпортуй, НЕ переписуй: на початку figs.py «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts')); from svgkit import *». Рамки з текстом — ЛИШЕ через textbox()/fitbox() (вони ГАРАНТУЮТЬ вкладання — ширина/шрифт рахуються від напису). НЕ перечитуй SVG поодинці: після генерації звіряй геометрію скриптом «python ${ROOT}\\scripts\\svgcheck.py <тека-розділу> --min-font 8» і виправляй лише позначене (out-of-bounds / дрібний шрифт), доки не буде «із зауваженнями: 0».
• НЕЙМИНГ — slug-only: тека розділу <slug>/, головний <slug>.md, вставки <kind>-<name>.md (kind: hist/comp/math/proj). Номери М.Р.Т — лише в manifest, не в іменах.
• МАТЕМАТИКА — Фейнман-глибоко (§3/§5): 🧮-вставки й будь-яке матпояснення дають ЧОМУ від першопричини (чому вектор розкладається на незалежні складові, звідки |R|=√(Rx²+Ry²), чому паралелограм = додавання) — не констатацію формул.
• КРОС-ЛІНКИ (§3): де треба глибше поняття з ІНШОЇ книги — коротка згадка (1–2 речення) + лінк [текст](book:math/<slug>) або [текст](book:components/<slug>); повний матеріал inline НЕ дублюй. Якщо цілі ще нема — однаково лінкуй (рушій покаже стаб «в розробці»): slug бери з manifest тієї книги, а якщо потрібного поняття там нема — ДОДАЙ topic-стаб у відповідний per-module manifest.js.
• СТАТУСИ (manifest): done — готово; empty — не почато; update — є текст, треба переписати; deeper — є текст, треба поглибити.
• МОВА — ФІНАЛЬНА З ПЕРШОГО РАЗУ: окремої вичитки не буде. Плавність (§1): кожен абзац і підрозділ — місток від попереднього; наскрізна нитка; перед поверненням перечитай суцільно й виправ сам.`

/* ── Схеми ── */
const UNITS = { type:'object', additionalProperties:false, required:['units'], properties:{ units:{ type:'array', items:{
  type:'object', additionalProperties:false, required:['chapter','kind','file','dir','brief','keys'],
  properties:{
    chapter:{type:'string'}, kind:{type:'string',enum:['chapter-main-new','chapter-main-append','extra']},
    file:{type:'string'}, dir:{type:'string'}, brief:{type:'string'},
    keys:{type:'array',items:{type:'string'},description:'ключі записів manifest на перевід у done: для тем — mrt-номери, для вставки — її file'},
  } } } } }

const STRUCT = { type:'object', additionalProperties:false, required:['outline','figures','claims'], properties:{
  outline:{type:'string', description:'ДЕТАЛЬНИЙ md-каркас файлу: H1, вступ, кожна тема «## М.Р.Т Назва» з 4–7 пунктами (інтуїція→механізм→деталь→типова пастка), КОНКРЕТНИЙ worked-приклад зі сценарієм і числами для обчислення, де рамки 🔧, перехресні §-лінки — БЕЗ прози'},
  figures:{type:'array', items:{ type:'object', additionalProperties:false, required:['id','shows'], properties:{
    id:{type:'string',description:'ім\'я svg, напр. fig-5-3-2-1-name'}, caption:{type:'string'}, shows:{type:'string',description:'що саме показує і який висновок'} } } },
  claims:{type:'array', description:'фактичні твердження, які треба перевірити ПЕРЕД письмом; порожньо для суто технічних тем', items:{
    type:'object', additionalProperties:false, required:['text','type','sensitive'], properties:{
      text:{type:'string'}, type:{type:'string',enum:['date','attribution','priority','quantity','event','quote','other']},
      sensitive:{type:'boolean',description:'true, якщо атрибуція/першість/національність/винахід — потребує особливо уважної перевірки'},
      whatToCheck:{type:'string'} } } },
} }

const FACTS = { type:'object', additionalProperties:false, required:['findings','guidanceForProse'], properties:{
  findings:{type:'array', items:{ type:'object', additionalProperties:false, required:['claim','status','correctedText'], properties:{
    claim:{type:'string'}, status:{type:'string',enum:['settled','contested','national-or-imperial-framing','plausible-unproven','myth','corrected','unverifiable']},
    correctedText:{type:'string',description:'як саме подати прозі — з датами, точними іменами/ідентичністю, статусом доказовості'},
    sources:{type:'array',items:{type:'string'}}, note:{type:'string'} } } },
  guidanceForProse:{type:'string',description:'стисло: що ствердити, чого уникнути, які міфи не повторювати'},
} }

const RET = { type:'object', additionalProperties:false, required:['ok'], properties:{
  ok:{type:'boolean'}, files:{type:'array',items:{type:'string'}}, note:{type:'string'} } }

const isHistory = (u) => /history|hist-/i.test(u.file) || /📜/.test(u.brief || '')
const isMath = (u) => /^math-|\/math-/.test(u.file || '') || /🧮/.test(u.brief || '')   // 🧮-вставки пишемо Opus-глибоко

/* ── Стійкість до недоступності сервера ──────────────────────────────────────
   agent() сам кілька разів ретраїть тимчасові помилки й повертає null лише як
   термінальну поразку. callAgent() додає правило «стукати поки не відповість»:
   на null чекає RETRY_WAIT і кличе знову, до MAX_TRIES спроб.
   Cap СКІНЧЕННИЙ навмисне: вічний ретрай на детермінованому збої (напр. схема,
   яку модель не може задовольнити) завис би назавжди й не дав би конвеєру
   завершитись. setTimeout — глобал Bun; на resume не виконується (кеш віддає
   результат одразу), тож сумісно з відновленням. ── */
const SLEEP = (ms) => new Promise(res => { try { setTimeout(res, ms) } catch (e) { res() } })
async function callAgent(prompt, opts) {
  const tag = (opts && opts.label) || 'agent'
  for (let attempt = 1; ; attempt++) {
    let r = null
    try { r = await agent(prompt, opts) } catch (e) { r = null }
    if (r != null) { if (attempt > 1) log(`✅ ${tag}: відповів зі спроби ${attempt}`); return r }
    if (attempt >= MAX_TRIES) { log(`⛔ ${tag}: немає відповіді після ${MAX_TRIES} спроб — пропускаю`); return null }
    log(`⏳ ${tag}: сервер не відповів (спроба ${attempt}/${MAX_TRIES}) — стукаю знову через ${Math.round(RETRY_WAIT / 1000)} с`)
    await SLEEP(RETRY_WAIT)
  }
}

/* ── Читання структури з manifest (детермінований розбір, без LLM-парсингу JS) ──
   Кореневий індекс задає window.BOOK_META + window.BOOK_MODULES (масив рядків
   "<slug>/manifest.js" або inline-обʼєктів). Per-module файл робить
   window.__MODREG__.push({...}). Виконуємо обидва в пісочниці через new Function
   (та сама техніка, що в bookbuild.js) і дістаємо реальні обʼєкти. */
function readText(absPath, label) {
  return callAgent(
    `Read the file "${absPath}" and return its full content verbatim in field "content". If it does not exist, return content as empty string and exists=false.`,
    { label, phase:'Скаут', model:'sonnet',
      schema:{ type:'object', additionalProperties:false, required:['content'], properties:{ content:{type:'string'}, exists:{type:'boolean'} } } }
  )
}
function evalSandbox(src) {
  const win = { __MODREG__: [] }
  try { new Function('window', src)(win) } catch (e) { throw new Error('manifest не виконується: ' + e.message) }
  return win
}

/* ── Скаут: знайти slug модуля N і зібрати одиниці empty/update ── */
phase('Скаут')

const idxRead = await readText(BK.index, `read-index:${BOOK}`)
if (!idxRead) throw new Error('індекс книги недоступний')
const idxWin = evalSandbox(idxRead.content)
const modList = idxWin.BOOK_MODULES || []
const basePath = (idxWin.BOOK_META && idxWin.BOOK_META.basePath) || BK.base

/* Запис модуля N в індексі: або рядок "<slug>/manifest.js" → читаємо per-module,
   або inline-обʼєкт {n, slug, chapters} (legacy: ще не винесений у власний файл). */
let modSlug = null, modManifestPath = null, moduleObj = null
for (const entry of modList) {
  if (typeof entry === 'string') {
    const slug = entry.replace(/\/manifest\.js$/, '').replace(/\/$/, '')
    // зчитуємо per-module, щоб дізнатися n
    const pmRead = await readText(`${ROOT_FS}/${basePath}${entry}`, `peek:${slug}`)
    if (!pmRead || !pmRead.content) continue
    let win
    try { win = evalSandbox(pmRead.content) } catch (e) { continue }
    const mod = (win.__MODREG__ || [])[0]
    if (mod && Number(mod.n) === N) {
      modSlug = mod.slug || slug; modManifestPath = `${ROOT_FS}/${basePath}${entry}`; moduleObj = mod; break
    }
  } else if (entry && Number(entry.n) === N) {
    modSlug = entry.slug; moduleObj = entry
    modManifestPath = `${ROOT_FS}/${basePath}${entry.slug}/manifest.js`   // де він житиме, коли стане per-module
    break
  }
}
if (!moduleObj) throw new Error(`Модуль ${N} не знайдено в індексі книги "${BOOK}" (${BK.index})`)
if (!moduleObj.chapters || !moduleObj.chapters.length)
  throw new Error(`Модуль ${N} (${modSlug}) ще не має chapters[] у manifest — спершу скелетуй структуру`)

log(`Книга "${BOOK}", Модуль ${N} = «${moduleObj.title || modSlug}» (slug ${modSlug}); manifest: ${modManifestPath}`)

/* Чи існує головний файл розділу (для chapter-main-new vs append). */
async function chapterMainExists(dir, main) {
  const r = await readText(`${ROOT_FS}/${basePath}${dir}/${main}`, `exists:${main}`)
  return !!(r && r.content && r.content.trim().length > 0)
}

const NEED = new Set(['empty', 'update'])
const SPEC = new Set(['comp', 'math', 'proj'])   // не-історичні вставки (як у bookbuild)
const units = []

for (const ch of moduleObj.chapters) {
  const topics = ch.topics || []
  const dir = ch.dir || `${modSlug}/${ch.slug || ''}`
  const main = ch.main || ''

  // ОДИНИЦЯ ПИСЬМА: теми (записи без kind) зі статусом empty/update.
  const themeTopics = topics.filter(t => t && !t.kind && NEED.has(t.status))
  // Розділ також може мати власний status empty/update (увесь головний файл).
  const chapterNeeds = NEED.has(ch.status)
  if (themeTopics.length || (chapterNeeds && topics.filter(t => t && !t.kind).length)) {
    const themes = themeTopics.length ? themeTopics : topics.filter(t => t && !t.kind)
    const exists = main ? await chapterMainExists(dir, main) : false
    const brief = themes.map(t => `${t.mrt} ${t.title}${t.scope ? ' — ' + t.scope : ''}`).join('\n')
    units.push({
      chapter: `${ch.n}. ${ch.title || ''}`,
      kind: exists ? 'chapter-main-append' : 'chapter-main-new',
      file: main, dir,
      brief: (ch.scope ? `Scope розділу: ${ch.scope}\nТеми:\n` : 'Теми:\n') + brief,
      keys: themes.map(t => t.mrt),       // ключі для статусів — mrt-номери
      _chapterStatus: chapterNeeds,        // чи переводити і сам розділ у done
      _chapterN: ch.n,
    })
  }

  // ОДИНИЦІ-ВСТАВКИ: кожен insert-topic (має kind) зі статусом empty/update.
  for (const t of topics) {
    if (!t || !t.kind) continue
    if (!NEED.has(t.status)) continue
    if (!(t.kind === 'hist' || SPEC.has(t.kind))) continue
    const tag = t.kind === 'hist' ? '📜' : t.kind === 'math' ? '🧮' : t.kind === 'proj' ? '⚙️' : '🔌'
    units.push({
      chapter: `${ch.n}. ${ch.title || ''}`,
      kind: 'extra',
      file: t.file, dir,
      brief: `${tag} ${t.title || ''}${t.at ? ` (до ${t.at})` : ''}`,
      keys: [t.file],
    })
  }
}

let queue = ONLY ? units.filter(u => (u.file || '').includes(ONLY) || (u.dir || '').includes(ONLY)) : units
if (LIMIT > 0) queue = queue.slice(0, LIMIT)
const work = queue
log(`Модуль ${N}: ${units.length} файлів-одиниць (empty/update)${(ONLY || LIMIT) ? ` — ПРОБА: ${work.length} (only=${ONLY || '—'}, limit=${LIMIT || '—'})` : ''}. Конвеєр: Каркас(Opus; важкі двопрохідно) → Факти(веб, за claims) → Проза(Sonnet, без окремої вичитки).`)
log(`Стійкість сервера: якщо не відповідає — повтор кожні ${Math.round(RETRY_WAIT / 1000)} с, до ${MAX_TRIES} спроб на агента.`)

if (!work.length) return { book:BOOK, module:N, total:0, done:0, failed:0, note:'черга порожня — усе done або поза empty/update' }

/* ── Промпти ── */
function structPrompt(u){
  const head = `${CANON}\n\nТи OPUS — ГОЛОВНИЙ АРХІТЕКТОР. Цей скелет визначає глибину й коректність майбутнього тексту — тут НЕ економ: розкрий механізми до першопричин, спроєктуй сильні worked-приклади з конкретними числами, познач КОЖНЕ фактичне твердження у claims. Пиши ЛИШЕ структуру (не прозу).`
  if (u.kind==='chapter-main-append')
    return `${head}\nПрочитай ЛИШЕ заголовки наявного ${ROOT}\\${basePath.replace(/\//g,'\\')}${u.dir.replace(/\//g,'\\')}\\${u.file} (Grep «^## », не читай усю прозу), щоб не дублювати. Нові теми:\n${u.brief}\nДля КОЖНОЇ нової теми: «## М.Р.Т Назва» + 4–7 пунктів (інтуїція→механізм→деталь→пастка), worked-приклад зі сценарієм і числами, місця рамок 🔧, §-лінки; познач, що вставляється ПЕРЕД «> ▶️ Далі». figures — для нових тем. claims — усі дати/імена/першості/числа на перевірку.`
  if (u.kind==='chapter-main-new')
    return `${head}\nНовий розділ ${u.dir}\\${u.file}.\n${u.brief}\noutline: H1 розділу, вступ-мотивація, кожна тема «## М.Р.Т Назва» з 4–7 пунктами (інтуїція→механізм→деталь→пастка), worked-приклад зі сценарієм і числами, рамки 🔧, §-лінки, і «> ▶️ Далі …» в кінці. figures — повний перелік (кожна несе вагу). claims — усі факти на перевірку.`
  return `${head}\nФайл-вставка ${u.dir}\\${u.file}: ${u.brief}. Каркас за типом (📜 §5 — заголовки за оповіддю, хронологія, дійові особи; 🔌 §5 — клас пристрою→блок-схема→розпіновка→підключення→«перший байт»→граблі→варіації; 🧮 — означення→інтуїція→апарат→де в курсі; ⚙️ — задача→ідея→РОБОЧИЙ C/C++→складність/пастки на МК). figures 0–2. claims — усі дати/імена/першості/винаходи/числа (для 📜 — практично кожне історичне твердження).`
}

function refinePrompt(u, st){
  return `${CANON}\n\nТи OPUS — РЕЦЕНЗЕНТ СКЕЛЕТА розділу «${u.file}». Ось чернетка:\n\nOUTLINE:\n${st.outline}\n\nFIGURES: ${JSON.stringify(st.figures)}\nCLAIMS: ${JSON.stringify(st.claims)}\n\nПОГЛИБ її, не роздуваючи обсяг: де пояснення поверхове — додай ланку механізму до першопричини; де worked-приклад слабкий — заміни конкретнішим із числами; додай пропущені типові пастки й перехресні §-лінки; перевір, що КОЖНА тема має інтуїцію→механізм→деталь→пастку і що кожна фігура реально несе думку; додай у claims будь-які пропущені факти. Поверни ПОВНИЙ покращений STRUCT (той самий формат).`
}

function factPrompt(u, st){
  return `${CANON}\n\nТи — ПЕРЕВІРНИК ФАКТІВ. Перевір КОЖНЕ твердження ВЕБ-ПОШУКОМ (WebSearch/WebFetch — завантаж інструмент за потреби), перш ніж це піде в книгу. Не вигадуй: чого не підтвердив — unverifiable. Якщо веб-інструменти недоступні — познач це в guidanceForProse, спирайся ЛИШЕ на впевнене знання, а решту став unverifiable (хай проза обережно це обходить).\nТВЕРДЖЕННЯ:\n${JSON.stringify(st.claims)}\n\nДисципліна атрибуції (обов'язково): розділяй етнічність / громадянство / місце народження / мову / інституцію / імперську приналежність — не клей ярлик «російське», коли джерела дають точніше (українець, поляк, серб, єврей, грузин, вірменин, балт…); якщо ідентичність змішана чи непевна — скажи прямо. Пильнуй імперське «поглинання» (російсько-радянські наративи; фабрикації кампанії першості 1948–53 — Кряковутной, Артамонов тощо). Винаходи колективні: розрізняй «мав ідею» / «опублікував теорію» / «зробив робочу реалізацію» / «створив систему» / «запатентував»; не приймай «ми перші подумали» без доказів. Не врівноважуй слабку пропаганду проти сильних доказів, але й не ховай серйозну наукову незгоду.\nДля кожного твердження дай: status, correctedText (як саме подати прозі — дати, точні імена/ідентичність, статус доказовості), sources (надійні URL — первинні чи якісні вторинні). Додай guidanceForProse: стисло що ствердити і яких міфів не повторювати.`
}

function prosePrompt(u, st, facts){
  const dirWin = `${ROOT}\\${basePath.replace(/\//g,'\\')}${u.dir.replace(/\//g,'\\')}`
  const figDir = (u.kind==='extra') ? `окремий ${dirWin}\\figs-${u.file.replace('.md','')}.py` : `${dirWin}\\figs.py (нові функції, НЕ ламай наявних)`
  const factBlock = facts
    ? `\n\nПЕРЕВІРЕНІ ФАКТИ (вживай ЛИШЕ їх для дат/імен/першостей; де status=corrected/myth/national-or-imperial-framing — пиши за correctedText і познач статус; unverifiable — обережне формулювання або пропуск):\n${JSON.stringify(facts.findings)}\nВКАЗІВКИ: ${facts.guidanceForProse}`
    : `\n\n(Фактичних тверджень на перевірку не було — пиши технічно точно.)`
  const role = isMath(u)
    ? 'Ти OPUS — пишеш ПОВНУ, ФІНАЛЬНУ прозу 🧮-математичної вставки Фейнман-глибоко (ЧОМУ від першопричини, не констатація формул), за скелетом від архітектора.'
    : 'Ти SONNET — пишеш ПОВНУ, ФІНАЛЬНУ прозу за готовим скелетом від архітектора.'
  const base = `${CANON}\n\n${role} Окремої вичитки НЕ БУДЕ: мова, плавність і єдиний термін — одразу, фінальної якості. Дотримуйся скелета й обсягів канону.\n\nСКЕЛЕТ:\n${st.outline}\n\nФІГУРИ (реалізуй усі): ${JSON.stringify(st.figures)}${factBlock}`
  const fig = `\nФігури: ${figDir} — на початку імпортуй спільний kit (import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts')); from svgkit import *), рамки з текстом лише через textbox()/fitbox(). УНІКАЛЬНІ імена svg у ./img/, ЗАПУСТИ скрипт (python …), тоді звір геометрію: «python ${ROOT}\\scripts\\svgcheck.py ${dirWin} --min-font 8» — якщо є зауваження, підправ figs.py (viewBox/координати/шрифт) і перегенеруй, доки «із зауваженнями: 0». НЕ перечитуй SVG поодинці. Підключи в текст «![підпис](img/fig-….svg)» + «*Рис. М.Р.Т.k. …*».`
  if (u.kind==='chapter-main-append')
    return `${base}${fig}\nДОПИШИ нові теми у наявний ${dirWin}\\${u.file} ПЕРЕД фінальним «> ▶️ Далі …» (він лишається останнім); решту файлу НЕ чіпай. Перед поверненням перечитай дописане суцільно.\nПоверни ok, files.`
  if (u.kind==='chapter-main-new')
    return `${base}${fig}\nСтвори ${dirWin}\\${u.file} цілком за скелетом. Перед поверненням перечитай суцільно.\nПоверни ok, files.`
  return `${base}${fig}\nСтвори файл-вставку ${dirWin}\\${u.file} (H1: історія «# 📜 …», інша вставка «# …»). Перед поверненням перечитай суцільно.\nПоверни ok, files.`
}

/* ── Лічильники для звіту (де реально пішла робота) ── */
let factOpus = 0, factSonnet = 0, factSkipped = 0, deepened = 0

/* Стадія 1: скелет. Важкі одиниці (цілий розділ) — двопрохідно: чернетка Opus → критик Opus поглиблює. */
async function buildSkeleton(u){
  const draft = await callAgent(structPrompt(u), { label:`каркас:${u.file}`, phase:'Каркас', model:'opus', schema:STRUCT })
  if (!draft) return null
  const heavy = (u.kind === 'chapter-main-new' || u.kind === 'chapter-main-append')
  if (!heavy) return draft
  const deep = await callAgent(refinePrompt(u, draft), { label:`каркас+:${u.file}`, phase:'Каркас', model:'opus', schema:STRUCT })
  if (deep) deepened++
  return deep || draft
}

/* Стадія 2: факти. Лише якщо є claims. Opus — історії/чутливе (атрибуція/першість), Sonnet — решта. */
async function factStage(st, u){
  if (!st) return { st:null, facts:null }
  const claims = st.claims || []
  if (!claims.length) { factSkipped++; return { st, facts:null } }
  const sensitive = isHistory(u) || claims.some(c => c && c.sensitive)
  const fmodel = sensitive ? 'opus' : 'sonnet'
  if (sensitive) factOpus++; else factSonnet++
  const facts = await callAgent(factPrompt(u, st), { label:`факти:${u.file}`, phase:'Факти', model:fmodel, schema:FACTS })
  return { st, facts }
}

/* Стадія 3: проза (фінальна якість, без окремої вичитки). */
async function proseStage(sf, u){
  if (!sf || !sf.st) return { ok:false, unit:u, note:'каркас не вдався' }
  const pr = await callAgent(prosePrompt(u, sf.st, sf.facts), { label:`проза:${u.file}`, phase:'Проза', model:isMath(u) ? 'opus' : 'sonnet', schema:RET })
  if (pr && pr.ok) return { ok:true, unit:u, files:pr.files }
  return { ok:false, unit:u, note:(pr && pr.note) || 'проза не вдалася' }
}

/* ── Конвеєр без бар'єрів: кожен файл проходить усі стадії незалежно ── */
const results = await pipeline(
  work,
  (u)      => buildSkeleton(u),
  (st, u)  => factStage(st, u),
  (sf, u)  => proseStage(sf, u),
)

const all = results.filter(Boolean)
const done = all.filter(r => r.ok)
const failed = all.filter(r => !r.ok)

/* ── Статуси: переставити записи готових одиниць у per-module manifest.js на done ──
   Збираємо ключі: для тем — mrt-номери, для вставок — їхній file; за потреби — і
   chapter-level status. Детермінована рядкова заміна status у тому самому
   обʼєкті записи (шукаємо «...mrt: "X.Y.Z" ... status: "empty|update"...» / file).
   Перезаписуємо файл через Write. ── */
phase('Статуси')
let statusChanged = 0
if (done.length) {
  const mkeys = []           // mrt-ключі тем
  const fkeys = []           // file-ключі вставок
  const chN = new Set()      // n розділів, чий chapter-level status теж у done
  for (const r of done) {
    const u = r.unit
    for (const k of (u.keys || [])) {
      if (u.kind === 'extra') fkeys.push(k); else mkeys.push(k)
    }
    if (u._chapterStatus && u._chapterN != null) chN.add(String(u._chapterN))
  }

  const pmRead = await readText(modManifestPath, `read-manifest:${modSlug}`)
  if (!pmRead || !pmRead.content) {
    log(`⚠️ не зміг прочитати ${modManifestPath} — статуси НЕ оновлено (одиниці написані)`)
  } else {
    let src = pmRead.content
    const esc = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const setDone = (re) => { let n = 0; src = src.replace(re, (m, pre) => { n++; return pre + 'done' }); return n }

    // Теми: «mrt: "X" ... status: "empty|update"» (status іде ПІСЛЯ mrt у записі).
    for (const mrt of mkeys) {
      const re = new RegExp('(mrt:\\s*"' + esc(mrt) + '"[\\s\\S]{0,160}?status:\\s*")(?:empty|update)', 'g')
      statusChanged += setDone(re)
    }
    // Вставки: ключ — file. У записі вставки status може стояти до або після file,
    // тому пробуємо обидва порядки в межах одного обʼєкта (file ... status / status ... file).
    for (const f of fkeys) {
      const a = new RegExp('(file:\\s*"' + esc(f) + '"[\\s\\S]{0,200}?status:\\s*")(?:empty|update)', 'g')
      let n = setDone(a)
      if (!n) {
        const b = new RegExp('(status:\\s*")(?:empty|update)("[\\s\\S]{0,200}?file:\\s*"' + esc(f) + '")')
        let m = 0; src = src.replace(b, (mm, p1, p3) => { m++; return p1 + 'done' + p3 }); n = m
      }
      statusChanged += n
    }
    // Chapter-level: «n: <N> ... status: "empty|update"» до першого topics:[ (щоб не зачепити теми).
    for (const n of chN) {
      const re = new RegExp('(n:\\s*"?' + esc(n) + '"?,[\\s\\S]{0,400}?status:\\s*")(?:empty|update)', 'g')
      statusChanged += setDone(re)
    }

    if (statusChanged && src !== pmRead.content) {
      await callAgent(
        `Write the following EXACT content to the file "${modManifestPath}" (overwrite). Return ok=true.\n\n<<<FILE>>>\n${src}\n<<<END>>>`,
        { label:`write-manifest:${modSlug}`, phase:'Статуси', model:'sonnet',
          schema:{ type:'object', additionalProperties:false, required:['ok'], properties:{ ok:{type:'boolean'} } } }
      )
      log(`Статуси в ${modManifestPath}: переставлено ${statusChanged} записів → done.`)
    } else {
      log(`⚠️ у ${modManifestPath} не знайдено записів для переводу (ключі могли не збігтися) — перевір вручну.`)
    }
  }
}

log(`Книга "${BOOK}", Модуль ${N}: готово ${done.length}/${work.length}; провалів: ${failed.length}; статусів→done: ${statusChanged}. Скелет поглиблено: ${deepened}; факт-чек: Opus ${factOpus} + Sonnet ${factSonnet}, без claims ${factSkipped}.`)
return {
  book:BOOK, module:N, slug:modSlug, total:work.length, done:done.length, failed:failed.length,
  statusChanged, deepened, factOpus, factSonnet, factSkipped,
  doneFiles: done.map(r => r.unit.file),
  failedNotes: failed.map(f => `${f.unit && f.unit.file}: ${f.note}`).slice(0, 20),
}
