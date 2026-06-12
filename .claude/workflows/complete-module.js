export const meta = {
  name: 'complete-module',
  description: 'Завершити модуль курсу embedded: Opus поглиблює скелет → веб-перевірка фактів → Sonnet пише фінальну прозу (🧮-математику — Opus; без окремої вичитки). args = номер модуля (1–14).',
  phases: [
    { title: 'Скаут', detail: 'розбити чергу модуля на файли-одиниці (Sonnet)' },
    { title: 'Каркас', detail: 'Opus планує і ПОГЛИБЛЮЄ скелет; важкі — двопрохідно (draft → критик)' },
    { title: 'Факти', detail: 'веб-перевірка дат/імен/атрибуцій (Opus — історії/першість, Sonnet — решта; лише за наявності claims)' },
    { title: 'Проза', detail: 'Sonnet пише фінальну якість одразу (🧮-вставки — Opus, Фейнман-глибоко); фігури звіряє svgcheck, без LLM-переогляду SVG' },
  ],
}

/* ── args: число / рядок "5" / JSON / {module|n [, limit]} ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) {} }
let N, LIMIT = 0, ONLY = '', RETRY_WAIT = 60000, MAX_TRIES = 30
if (_a && typeof _a === 'object') {
  N = Number(_a.module != null ? _a.module : _a.n); LIMIT = Number(_a.limit) || 0; ONLY = _a.only || ''
  if (_a.retryWaitMs != null) RETRY_WAIT = Number(_a.retryWaitMs)   // пауза між стуками (за умовч. 60 с)
  if (_a.maxTries != null) MAX_TRIES = Number(_a.maxTries)         // скінченний cap (за умовч. 30)
} else { N = Number(_a) }
if (!N || N < 1) throw new Error('Передай номер модуля: args = N (1–14) або {module:N, limit:K} для проби')
const ROOT = 'E:\\develop\\courses\\embedded'

/* ── Спільний канон (ІДЕНТИЧНИЙ префікс у всіх агентів → кеш; читати AUTHORING не треба) ── */
const CANON = `КАНОН (стисло; повне — ${ROOT}\\AUTHORING.md, читати НЕ обов'язково):
• Українською, стиль Фейнмана: глибоко, від першопричин, інтуїція→деталі; без «як для 4-річного», без пафосу. Жива мова — без кальок, русизмів, канцеляриту; один термін на поняття в межах файлу.
• Нумерація М.Р.Т: заголовки тем «## М.Р.Т Назва»; підписи фігур «Рис. М.Р.Т.k» (в історіях «Рис. М.Р.Тi.k»).
• Обсяги: тема — 2200–2600 слів прози (важкі — більше); вставка 🔌/🧮/⚙️ — 300–1000; історія 📜 — 2000–8000. Обсяг рахується без код-блоків.
• Формули — Unicode у код-блоках (10⁻⁹, ε, ≈, ², ₀, ·), без LaTeX; десятковий роздільник — крапка.
• Біля важливих понять — рамка «> 🔧 Навіщо це»; worked-приклад — жирний підпис + код-блок із покроковим обчисленням.
• КОД у прикладах і ⚙️-вставках — реальний C/C++ (прошивка ESP32), НЕ псевдокод: короткий, коректний, компільований фрагмент.
• Двомовні терміни: «провідність (conductivity, σ)». Не забігати вперед (лише цей і попередні розділи); назад — «§М.Р.Т».
• ФАКТИ: будь-яке історичне/фактичне твердження (дата, ім'я, «хто перший», винахід, патент, національність/походження) — ЛИШЕ за підтвердженими даними зі стадії «Факти». Якщо вони дали корекцію — пиши скориговано й познач статус доказовості (усталено / спірно / імперсько-національне обрамлення / міф). Не клей ярлик «російське», коли джерела дають точніше (українець, поляк, серб, єврей, грузин, вірменин, балт…); розрізняй ідею / теорію / робочу реалізацію / систему / патент.
• ФІГУРИ — чистий Python → ./img/*.svg, кожна несе вагу. Спільний kit імпортуй, НЕ переписуй: на початку figs.py «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools')); from svgkit import *». Рамки з текстом — ЛИШЕ через textbox()/fitbox() (вони ГАРАНТУЮТЬ вкладання — ширина/шрифт рахуються від напису). НЕ перечитуй SVG поодинці: після генерації звіряй геометрію скриптом «python ${ROOT}\\_tools\\svgcheck.py <тека-розділу> --min-font 8» і виправляй лише позначене (out-of-bounds / дрібний шрифт), доки не буде «із зауваженнями: 0».
• НЕЙМИНГ — slug-only: тека розділу <slug>/, головний <slug>.md, вставки <kind>-<name>.md (kind: hist/comp/math/proj). Номери М.Р.Т — лише в manifest/_status/PLAN, не в іменах.
• МАТЕМАТИКА — Фейнман-глибоко (§5/§16): 🧮-вставки й будь-яке матпояснення дають ЧОМУ від першопричини (чому вектор розкладається на незалежні складові, звідки |R|=√(Rx²+Ry²), чому паралелограм = додавання) — не констатацію формул.
• КРОС-ЛІНКИ (§18): де треба глибше поняття з ІНШОЇ книги — коротка згадка (1–2 речення) + лінк [текст](book:math/<slug>) або [текст](book:components/<slug>); повний матеріал inline НЕ дублюй. Якщо цілі ще нема — однаково лінкуй (рушій покаже стаб «в розробці»): slug бери з _status.md тієї книги (math/<section>/_status.md, components/<sector>/_status.md), а якщо потрібного поняття там нема — ДОДАЙ рядок-стаб «## Розділ M.R — Назва · \`<section>/<slug>/\`» (з наступним вільним M.R) у відповідний _status.md.
• МОВА — ФІНАЛЬНА З ПЕРШОГО РАЗУ: окремої вичитки не буде. Плавність (§5/§17): кожен абзац і підрозділ — місток від попереднього; наскрізна нитка; перед поверненням перечитай суцільно й виправ сам.`

/* ── Схеми ── */
const UNITS = { type:'object', additionalProperties:false, required:['units'], properties:{ units:{ type:'array', items:{
  type:'object', additionalProperties:false, required:['chapter','kind','file','dir','brief','statusLines'],
  properties:{
    chapter:{type:'string'}, kind:{type:'string',enum:['chapter-main-new','chapter-main-append','extra']},
    file:{type:'string'}, dir:{type:'string'}, brief:{type:'string'},
    statusLines:{type:'array',items:{type:'string'}},
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

const RET = { type:'object', additionalProperties:false, required:['ok','statusLines'], properties:{
  ok:{type:'boolean'}, statusLines:{type:'array',items:{type:'string'}}, files:{type:'array',items:{type:'string'}}, note:{type:'string'} } }

const isHistory = (u) => /history/i.test(u.file) || /📜/.test(u.brief || '')
const isMath = (u) => /^math-/.test(u.file || '') || /🧮/.test(u.brief || '')   // 🧮-вставки пишемо Opus-глибоко

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

/* ── Промпти ── */
function structPrompt(u){
  const head = `${CANON}\n\nТи OPUS — ГОЛОВНИЙ АРХІТЕКТОР. Цей скелет визначає глибину й коректність майбутнього тексту — тут НЕ економ: розкрий механізми до першопричин, спроєктуй сильні worked-приклади з конкретними числами, познач КОЖНЕ фактичне твердження у claims. Пиши ЛИШЕ структуру (не прозу).`
  if (u.kind==='chapter-main-append')
    return `${head}\nПрочитай ЛИШЕ заголовки наявного ${ROOT}\\${u.dir}\\${u.file} (Grep «^## », не читай усю прозу), щоб не дублювати. Нові теми: ${u.brief}. Для КОЖНОЇ нової теми: «## М.Р.Т Назва» + 4–7 пунктів (інтуїція→механізм→деталь→пастка), worked-приклад зі сценарієм і числами, місця рамок 🔧, §-лінки; познач, що вставляється ПЕРЕД «> ▶️ Далі». figures — для нових тем. claims — усі дати/імена/першості/числа на перевірку.`
  if (u.kind==='chapter-main-new')
    return `${head}\nНовий розділ ${u.dir}\\${u.file}. Теми: ${u.brief}. outline: H1 розділу, вступ-мотивація, кожна тема «## М.Р.Т Назва» з 4–7 пунктами (інтуїція→механізм→деталь→пастка), worked-приклад зі сценарієм і числами, рамки 🔧, §-лінки, і «> ▶️ Далі …» в кінці. figures — повний перелік (кожна несе вагу). claims — усі факти на перевірку.`
  return `${head}\nФайл-вставка ${u.dir}\\${u.file}: ${u.brief}. Каркас за типом (📜 §10 — заголовки за оповіддю, хронологія, дійові особи; 🔌 §16 — клас пристрою→блок-схема→розпіновка→підключення→«перший байт»→граблі→варіації; 🧮 — означення→інтуїція→апарат→де в курсі; ⚙️ — задача→ідея→РОБОЧИЙ C/C++→складність/пастки на МК). figures 0–2. claims — усі дати/імена/першості/винаходи/числа (для 📜 — практично кожне історичне твердження).`
}

function refinePrompt(u, st){
  return `${CANON}\n\nТи OPUS — РЕЦЕНЗЕНТ СКЕЛЕТА розділу «${u.file}». Ось чернетка:\n\nOUTLINE:\n${st.outline}\n\nFIGURES: ${JSON.stringify(st.figures)}\nCLAIMS: ${JSON.stringify(st.claims)}\n\nПОГЛИБ її, не роздуваючи обсяг: де пояснення поверхове — додай ланку механізму до першопричини; де worked-приклад слабкий — заміни конкретнішим із числами; додай пропущені типові пастки й перехресні §-лінки; перевір, що КОЖНА тема має інтуїцію→механізм→деталь→пастку і що кожна фігура реально несе думку; додай у claims будь-які пропущені факти. Поверни ПОВНИЙ покращений STRUCT (той самий формат).`
}

function factPrompt(u, st){
  return `${CANON}\n\nТи — ПЕРЕВІРНИК ФАКТІВ. Перевір КОЖНЕ твердження ВЕБ-ПОШУКОМ (WebSearch/WebFetch — завантаж інструмент за потреби), перш ніж це піде в книгу. Не вигадуй: чого не підтвердив — unverifiable. Якщо веб-інструменти недоступні — познач це в guidanceForProse, спирайся ЛИШЕ на впевнене знання, а решту став unverifiable (хай проза обережно це обходить).\nТВЕРДЖЕННЯ:\n${JSON.stringify(st.claims)}\n\nДисципліна атрибуції (обов'язково): розділяй етнічність / громадянство / місце народження / мову / інституцію / імперську приналежність — не клей ярлик «російське», коли джерела дають точніше (українець, поляк, серб, єврей, грузин, вірменин, балт…); якщо ідентичність змішана чи непевна — скажи прямо. Пильнуй імперське «поглинання» (російсько-радянські наративи; фабрикації кампанії першості 1948–53 — Кряковутной, Артамонов тощо). Винаходи колективні: розрізняй «мав ідею» / «опублікував теорію» / «зробив робочу реалізацію» / «створив систему» / «запатентував»; не приймай «ми перші подумали» без доказів. Не врівноважуй слабку пропаганду проти сильних доказів, але й не ховай серйозну наукову незгоду.\nДля кожного твердження дай: status, correctedText (як саме подати прозі — дати, точні імена/ідентичність, статус доказовості), sources (надійні URL — первинні чи якісні вторинні). Додай guidanceForProse: стисло що ствердити і яких міфів не повторювати.`
}

function prosePrompt(u, st, facts){
  const figDir = (u.kind==='extra') ? `окремий ${ROOT}\\${u.dir}\\figs-${u.file.replace('.md','')}.py` : `${ROOT}\\${u.dir}\\figs.py (нові функції, НЕ ламай наявних)`
  const factBlock = facts
    ? `\n\nПЕРЕВІРЕНІ ФАКТИ (вживай ЛИШЕ їх для дат/імен/першостей; де status=corrected/myth/national-or-imperial-framing — пиши за correctedText і познач статус; unverifiable — обережне формулювання або пропуск):\n${JSON.stringify(facts.findings)}\nВКАЗІВКИ: ${facts.guidanceForProse}`
    : `\n\n(Фактичних тверджень на перевірку не було — пиши технічно точно.)`
  const role = isMath(u)
    ? 'Ти OPUS — пишеш ПОВНУ, ФІНАЛЬНУ прозу 🧮-математичної вставки Фейнман-глибоко (ЧОМУ від першопричини, не констатація формул), за скелетом від архітектора.'
    : 'Ти SONNET — пишеш ПОВНУ, ФІНАЛЬНУ прозу за готовим скелетом від архітектора.'
  const base = `${CANON}\n\n${role} Окремої вичитки НЕ БУДЕ: мова, плавність і єдиний термін — одразу, фінальної якості. Дотримуйся скелета й обсягів канону.\n\nСКЕЛЕТ:\n${st.outline}\n\nФІГУРИ (реалізуй усі): ${JSON.stringify(st.figures)}${factBlock}`
  const fig = `\nФігури: ${figDir} — на початку імпортуй спільний kit (import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools')); from svgkit import *), рамки з текстом лише через textbox()/fitbox(). УНІКАЛЬНІ імена svg у ./img/, ЗАПУСТИ скрипт (python …), тоді звір геометрію: «python ${ROOT}\\_tools\\svgcheck.py ${ROOT}\\${u.dir} --min-font 8» — якщо є зауваження, підправ figs.py (viewBox/координати/шрифт) і перегенеруй, доки «із зауваженнями: 0». НЕ перечитуй SVG поодинці. Підключи в текст «![підпис](img/fig-….svg)» + «*Рис. М.Р.Т.k. …*».`
  if (u.kind==='chapter-main-append')
    return `${base}${fig}\nДОПИШИ нові теми у наявний ${ROOT}\\${u.dir}\\${u.file} ПЕРЕД фінальним «> ▶️ Далі …» (він лишається останнім); решту файлу НЕ чіпай. Перед поверненням перечитай дописане суцільно.\nПоверни ok, statusLines=${JSON.stringify(u.statusLines)}, files.`
  if (u.kind==='chapter-main-new')
    return `${base}${fig}\nСтвори ${ROOT}\\${u.dir}\\${u.file} цілком за скелетом. Перед поверненням перечитай суцільно.\nПоверни ok, statusLines=${JSON.stringify(u.statusLines)}, files.`
  return `${base}${fig}\nСтвори файл-вставку ${ROOT}\\${u.dir}\\${u.file} (H1: історія «# 📜 …», інша вставка «# …»). Перед поверненням перечитай суцільно.\nПоверни ok, statusLines=${JSON.stringify(u.statusLines)}, files.`
}

/* ── Скаут (Sonnet — механічний розбір черги) ── */
phase('Скаут')
const scout = await callAgent(
  `Знайди папку Модуля ${N} (block-${N}-…) і прочитай її _status.md та секцію Модуля ${N} у ${ROOT}\\PLAN.md (повні назви тем і шляхи папок розділів «block-${N}-…/folder/file.md»).
Збери ОДИНИЦІ РОБОТИ — усе зі статусом ⬜ у Модулі ${N}, згруповане по ФАЙЛАХ:
- розділ із ⬜-ТЕМАМИ («- ⬜ ${N}.Р.Т Назва») → одна одиниця: kind="chapter-main-new" якщо головний .md ще не існує, інакше "chapter-main-append". file=головний .md, dir=папка розділу, brief=перелік ⬜-тем із номерами й назвами, statusLines=ці ⬜-рядки тем.
- кожен ⬜ рядок ВСТАВКИ/ІСТОРІЇ (📜/🔌/🧮/⚙️, з іменем файлу в \`…\`) → одиниця kind="extra", file=те ім'я, dir=папка того ж розділу, brief=тип+назва+(до теми М.Р.Т), statusLines=[той рядок].
Поверни всі одиниці.`,
  { label:`scout:M${N}`, phase:'Скаут', model:'sonnet', schema:UNITS }
)
const allUnits = (scout?.units || [])
let queue = ONLY ? allUnits.filter(u => (u.file || '').includes(ONLY) || (u.dir || '').includes(ONLY)) : allUnits
if (LIMIT > 0) queue = queue.slice(0, LIMIT)
const units = queue
log(`Модуль ${N}: ${allUnits.length} файлів-одиниць${(ONLY || LIMIT) ? ` — ПРОБА: ${units.length} (only=${ONLY || '—'}, limit=${LIMIT || '—'})` : ''}. Конвеєр: Каркас(Opus; важкі двопрохідно) → Факти(веб, за claims) → Проза(Sonnet, без окремої вичитки).`)

log(`Стійкість сервера: якщо не відповідає — повтор кожні ${Math.round(RETRY_WAIT / 1000)} с, до ${MAX_TRIES} спроб на агента.`)

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
  if (!sf || !sf.st) return { ok:false, statusLines:u.statusLines, note:'каркас не вдався' }
  const pr = await callAgent(prosePrompt(u, sf.st, sf.facts), { label:`проза:${u.file}`, phase:'Проза', model:isMath(u) ? 'opus' : 'sonnet', schema:RET })
  if (pr && pr.ok) return { ok:true, statusLines:u.statusLines, files:pr.files }
  return { ok:false, statusLines:u.statusLines, note:(pr && pr.note) || 'проза не вдалася' }
}

/* ── Конвеєр без бар'єрів: кожен файл проходить усі стадії незалежно ── */
const results = await pipeline(
  units,
  (u)      => buildSkeleton(u),
  (st, u)  => factStage(st, u),
  (sf, u)  => proseStage(sf, u),
)

const all = results.filter(Boolean)
const done = all.filter(r => r.ok)
const failed = all.filter(r => !r.ok)
const doneLines = done.flatMap(r => r.statusLines || [])
const failedLines = failed.flatMap(r => r.statusLines || [])
log(`Модуль ${N}: готово ${done.length}/${units.length}; рядків ⬜→🟢: ${doneLines.length}; провалів: ${failed.length}. Скелет поглиблено: ${deepened}; факт-чек: Opus ${factOpus} + Sonnet ${factSonnet}, без claims ${factSkipped}.`)
return { module:N, total:units.length, done:done.length, failed:failed.length, doneLines, failedLines,
         deepened, factOpus, factSonnet, factSkipped, failedNotes: failed.map(f => f.note).slice(0, 20) }
