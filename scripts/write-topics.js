export const meta = {
  name: 'write-topics',
  description: 'Написати/привести до канону статті-теми книги. Читає book/<book>/manifest.js (або catalog/<book>), бере теми зі статусом empty/update/recheck/deeper, пише <slug>.md (level=basic) або <slug>-d.md (detailed) за AUTHORING.md, перевіряє факти вебом, ставить status→done. args = {book, kind?:"book"|"catalog", section?, status?:[…], level?:"basic"|"detailed", limit?}',
  phases: [
    { title: 'Скаут', detail: 'прочитати маніфест книги, зібрати теми в роботу' },
    { title: 'Каркас', detail: 'Opus планує детальний скелет + claims на факт-чек' },
    { title: 'Факти', detail: 'веб-перевірка дат/імен/атрибуцій (лише за наявності claims)' },
    { title: 'Проза', detail: 'фінальний текст + фігури (svgcheck), без окремої вичитки' },
    { title: 'Статуси', detail: 'status відповідних тем → done у маніфесті (серіалізовано)' },
  ],
}

/* ── args ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = { book: _a } } }
const BOOK = _a && _a.book ? String(_a.book) : ''
const KIND = (_a && _a.kind) || 'book'           // book | catalog
const SECTION = (_a && _a.section) || ''          // фільтр за галуззю (slug)
const LEVEL = (_a && _a.level) || 'basic'         // basic → <slug>.md ; detailed → <slug>-d.md
const STATUSES = (_a && Array.isArray(_a.status) && _a.status.length) ? _a.status : ['empty', 'update', 'recheck', 'deeper']
const LIMIT = Number(_a && _a.limit) || 0
if (!BOOK) throw new Error('Передай args = {book:"electronics"[, kind, section, level, status, limit]}')

const ROOT = 'E:\\develop\\courses'
const ROOT_FS = 'E:/develop/courses'
const MF = `${KIND}/${BOOK}/manifest.js`         // відносний шлях маніфесту
const MAX_TRIES = 30, RETRY_WAIT = 60000

/* ── Канон (ІДЕНТИЧНИЙ префікс → кеш; повне — AUTHORING.md) ── */
const CANON = `КАНОН письма (стисло; повне — ${ROOT}\\AUTHORING.md):
• Стаття = тема, САМОДОСТАТНЯ, БЕЗ нумерації й БЕЗ фраз послідовності («попередній/наступний розділ», «як ми бачили», «далі побачимо», «пригадаймо») — у book порядку немає.
• Метод Фейнмана: глибоко, від першопричин; інтуїція й «ЧОМУ» → деталі; мотивацію давай, якщо є бодай легка потреба. Висновок будуй на очах у читача. Аналогії точні + де ламаються. Причинно-наслідкові ланцюжки, не списки. Поважай інтелект читача — без «як для малюків», без пафосу.
• Жива українська: лише справжні слова, без русизмів/кальок/канцеляриту/випадкової синонімії; один термін на поняття. Першоджерело назви в дужках при першій зустрічі: «атом (гр. átomos — неподільний)», «напруга (лат. tensio)».
• Плавність: кожен абзац — місток від попереднього; наскрізна нитка навіщо→інтуїція→деталі→приклад; перед кінцем перечитай суцільно й згладь стики.
• Обсяг прози (без код-блоків): базова <slug>.md — 1000–3500 слів; детальна <slug>-d.md — 2500–13000 (каталог — до 25000). Складність теми — критерій, не бажання скоротити.
• Формули — Unicode у код-блоках (10⁻⁹, ε, ≈, ², ₀, ·), без LaTeX; роздільник — крапка (3.3). Worked-приклад: жирний підпис-умова → код-блок із покроковим обчисленням → висновок. КОД — реальний C/C++ (прошивка), не псевдокод.
• Біля важливого поняття — рамка «> 🔧 **Навіщо це.**» (на матеріалі цієї теми).
• ГОЛОС: book-статті узагальнені — конкретну деталь/номер лише як приклад-згадку з лінком (на catalog/comp-), не будуй статтю на ній. Платформи-предмет (ESP32, ArduPilot) називати можна.
• ФІГУРИ: лише SVG, чистий Python без залежностей; генератор figs.py У ТЕЦІ ТЕМИ, вивід ./img/. На початку figs.py: «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *». Рамки з текстом — ЛИШЕ через textbox()/fitbox(). Кожна фігура несе вагу. Підключення: «![опис](/${KIND}/${BOOK}/<галузь>/<slug>/img/<file>.svg)» — шлях ВІД КОРЕНЯ РЕПО (з /); наступним рядком курсивом ЗВИЧАЙНИЙ опис (що показано і висновок), БЕЗ номера й БЕЗ «Рис.». Після генерації: «python ${ROOT}\\scripts\\svgcheck.py <тека-теми> --min-font 8», виправляй позначене, доки «із зауваженнями: 0».
• КРОС-ЛІНКИ — ЛИШЕ на справжні залежності (не на кожну згадку!). Оформлення: короткий конспект 1–7 речень «що саме треба знати» + ref-лінк, що відкриває попап: [текст](book:<книга>/<slug>) (базова) чи [текст](book:<книга>/<slug>/<slug>-d.md) (детальна) чи [текст](book:<книга>/<slug>/<type>-<name>.md) (вставка). Галузь у book:-лінку НЕ потрібна. Усю ціль НЕ переписуй. Якщо цілі ще нема — створи порожній файл у правильному місці, ЗАРЕЄСТРУЙ у маніфесті тієї книги зі status:"empty", і лінкуй на нього.
• ФАКТИ: будь-яке історичне/фактичне твердження (дата, ім'я, «хто перший», винахід, патент, походження) — ЛИШЕ за підтвердженими даними зі стадії «Факти»; познач статус доказовості. Не клей «російське», коли джерела дають точніше (українець, поляк, серб, єврей, грузин, вірменин, балт…); розрізняй ідею/теорію/реалізацію/систему/патент.
• НЕЙМИНГ slug-only; вставки <type>-<name>.md (type: hist/comp/math/proj); файл-вставка починається з H1 (можна з емодзі «# 📜 …»).
• МОВА ФІНАЛЬНА З ПЕРШОГО РАЗУ — окремої вичитки не буде.`

/* ── helpers ── */
async function callAgent(prompt, opts) {
  for (let a = 1; a <= MAX_TRIES; a++) {
    let r = null
    try { r = await agent(prompt, opts) } catch (e) { r = null }
    if (r != null) return r
    if (a >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді після ${MAX_TRIES} спроб`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}
function readFile(absPath, label) {
  return callAgent(`Read the file "${absPath}" and return its full content verbatim in field "content". If it does not exist, return content:"" and exists:false.`,
    { label, phase: 'Скаут', schema: { type: 'object', additionalProperties: false, required: ['content'], properties: { content: { type: 'string' }, exists: { type: 'boolean' } } } })
}

/* ── схеми ── */
const UNITS = { type: 'object', additionalProperties: false, required: ['units'], properties: { units: { type: 'array', items: {
  type: 'object', additionalProperties: false, required: ['section', 'slug', 'title', 'status'],
  properties: { section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, status: { type: 'string' }, scope: { type: 'string' } } } } } }
const STRUCT = { type: 'object', additionalProperties: false, required: ['outline', 'claims'], properties: {
  outline: { type: 'string', description: 'ДЕТАЛЬНИЙ md-каркас: H1, вступ-мотивація, підрозділи з 4–7 пунктами (інтуїція→механізм→деталь→пастка), КОНКРЕТНИЙ worked-приклад зі сценарієм і числами, місця рамок 🔧, потрібні фігури (опис), справжні залежності → ref-лінки — БЕЗ прози' },
  figures: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'shows'], properties: { file: { type: 'string' }, shows: { type: 'string' } } } },
  claims: { type: 'array', items: { type: 'string' } } } }
const FACTS = { type: 'object', additionalProperties: false, required: ['guidanceForProse'], properties: {
  guidanceForProse: { type: 'string' }, items: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['claim', 'status', 'correctedText'], properties: { claim: { type: 'string' }, status: { type: 'string' }, correctedText: { type: 'string' }, sources: { type: 'array', items: { type: 'string' } } } } } } }
const RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, files: { type: 'array', items: { type: 'string' } }, note: { type: 'string' } } }

/* ── Скаут ── */
phase('Скаут')
const mf = await readFile(`${ROOT}\\${MF.replace(/\//g, '\\')}`, 'маніфест')
if (!mf || !mf.content) return { book: BOOK, error: 'маніфест не прочитано' }
const scout = await callAgent(
  `${CANON}\n\nОсь маніфест ${MF}:\n\n${mf.content}\n\nПоверни units — ВСІ теми (sections[].topics[]) зі status ∈ [${STATUSES.join(', ')}]${SECTION ? ` і лише з галузі "${SECTION}"` : ''}. Для кожної: section (slug галузі), slug, title, status, scope (з її section).`,
  { label: 'скаут', phase: 'Скаут', model: 'opus', schema: UNITS })
let work = (scout && scout.units) || []
if (SECTION) work = work.filter((u) => u.section === SECTION)
work = work.filter((u) => STATUSES.includes(u.status))
if (LIMIT) work = work.slice(0, LIMIT)
if (!work.length) return { book: BOOK, total: 0, note: 'черга порожня' }
log(`У роботі: ${work.length} тем (${LEVEL})`)

function fileFor(u) { return LEVEL === 'detailed' ? `${u.slug}-d.md` : `${u.slug}.md` }
function dirFor(u) { return `${KIND}/${BOOK}/${u.section}/${u.slug}` }

/* ── Каркас → Факти → Проза (pipeline) ── */
const done = []
const results = await pipeline(work,
  (u) => callAgent(
    `${CANON}\n\nТи OPUS — плануєш скелет ${LEVEL}-статті «${u.title}» (тема «${u.slug}», галузь «${u.section}», книга «${BOOK}»). Scope галузі: ${u.scope || ''}.\n${u.status === 'recheck' || u.status === 'update' || u.status === 'deeper' ? `Спершу прочитай наявний ${ROOT}\\${dirFor(u).replace(/\//g, '\\')}\\${fileFor(u)} (якщо є) і визнач, що бракує/виправити за КАНОНОМ.` : 'Стаття нова.'}\nДай outline (детальний каркас за §4), figures (кожна несе вагу), claims (усі дати/імена/першості/числа на веб-перевірку).`,
    { label: `каркас:${u.slug}`, phase: 'Каркас', model: 'opus', schema: STRUCT }),
  (st, u) => {
    if (!st) return null
    const claims = (st.claims || []).filter(Boolean)
    if (!claims.length) return { st, facts: null }
    return callAgent(
      `${CANON}\n\nТи — ПЕРЕВІРНИК ФАКТІВ. Перевір КОЖНЕ твердження ВЕБ-ПОШУКОМ (WebSearch/WebFetch — завантаж за потреби). Чого не підтвердив — status unverifiable. Дисципліна атрибуції: розрізняй етнічність/громадянство/місце/мову/інституцію/імперську приналежність; пильнуй імперське поглинання; винаходи колективні. Поверни items (claim, status, correctedText, sources) і guidanceForProse.\nТВЕРДЖЕННЯ:\n${JSON.stringify(claims)}`,
      { label: `факти:${u.slug}`, phase: 'Факти', model: 'sonnet', schema: FACTS }).then((facts) => ({ st, facts }))
  },
  (sf, u) => {
    if (!sf || !sf.st) return null
    const dirWin = `${ROOT}\\${dirFor(u).replace(/\//g, '\\')}`
    const factTxt = sf.facts ? `\nФАКТИ (зважай): ${JSON.stringify(sf.facts)}` : ''
    const isMath = u.section && /math|матем/i.test(u.section)
    return callAgent(
      `${CANON}\n\nТи пишеш ФІНАЛЬНУ ${LEVEL}-статтю за скелетом. Створи/перепиши файл ${dirWin}\\${fileFor(u)} цілком.${factTxt}\nСКЕЛЕТ:\n${sf.st.outline}\nФІГУРИ: ${JSON.stringify(sf.st.figures || [])}\nЗгенеруй потрібні фігури (figs.py у теці теми, svgcheck до «0 зауважень»). Перед поверненням перечитай суцільно й згладь стики. Поверни ok, files.`,
      { label: `проза:${u.slug}`, phase: 'Проза', model: isMath ? 'opus' : 'sonnet', schema: RET }).then((pr) => {
        if (pr && pr.ok) { done.push(u); return { ok: true, slug: u.slug } }
        return { ok: false, slug: u.slug, note: pr && pr.note }
      })
  })

/* ── Статуси: серіалізовано в маніфесті → done ── */
phase('Статуси')
if (done.length) {
  const slugs = done.map((u) => u.slug)
  await callAgent(
    `Онови маніфест ${ROOT}\\${MF.replace(/\//g, '\\')}: для тем зі slug ∈ ${JSON.stringify(slugs)} зміни їх поле status на "done" (Edit точково, не чіпай решту). Поверни ok та count змінених.`,
    { label: 'статуси→done', phase: 'Статуси', schema: { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } } })
}
const okN = results.filter((r) => r && r.ok).length
return { book: BOOK, level: LEVEL, total: work.length, done: okN, failed: work.length - okN }
