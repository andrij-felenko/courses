export const meta = {
  name: 'write-inserts',
  description: 'Написати/привести до канону вставки книги (hist/comp/math/proj). Читає book/<book>/manifest.js, бере вставки {file,status} зі status ∈ empty/update/recheck/deeper, пише <type>-<name>.md за AUTHORING.md (H1-заголовок, 1000–10000 слів), перевіряє факти, ставить їх status→done. args = {book, kind?:"book"|"catalog", section?, type?:"hist"|"comp"|"math"|"proj", status?:[…], limit?}',
  phases: [
    { title: 'Скаут', detail: 'прочитати маніфест, зібрати вставки в роботу' },
    { title: 'Факти', detail: 'веб-перевірка (надто для 📜 — кожне історичне твердження)' },
    { title: 'Проза', detail: 'фінальний текст вставки + фігури' },
    { title: 'Статуси', detail: 'status вставок → done у маніфесті' },
  ],
}

let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = { book: _a } } }
const BOOK = _a && _a.book ? String(_a.book) : ''
const KIND = (_a && _a.kind) || 'book'
const SECTION = (_a && _a.section) || ''
const TYPE = (_a && _a.type) || ''                 // hist|comp|math|proj — фільтр
const STATUSES = (_a && Array.isArray(_a.status) && _a.status.length) ? _a.status : ['empty', 'update', 'recheck', 'deeper']
const LIMIT = Number(_a && _a.limit) || 0
if (!BOOK) throw new Error('Передай args = {book:"electronics"[, kind, section, type, status, limit]}')

const ROOT = 'E:\\develop\\courses'
const MF = `${KIND}/${BOOK}/manifest.js`
const MAX_TRIES = 30, RETRY_WAIT = 60000
const TYPES = ['hist', 'comp', 'math', 'proj']

const CANON = `КАНОН вставок (стисло; повне — ${ROOT}\\AUTHORING.md):
• Вставка — окрема міні-стаття у теці теми; несе вагу (НЕ переказ теми/банальність); 1000–10000 слів (дуже багато → поділити на кілька).
• Файл починається з H1: історія «# 📜 Назва», 🔌 «# Назва», 🧮 «# Назва», ⚙️ «# Назва» (рушій бере H1 як заголовок попапу).
• Шаблон за типом:
  – 📜 hist: як НАРОДИЛОСЯ поняття — що бентежило, хто, суперечки, дійові особи; заголовки підрозділів = назви тем («### Бурштин і перша загадка статики»), НЕ «Питання 1»; історія ЗАВЖДИ справжня (легенди позначай легендами); двомовні імена.
  – 🔌 comp: клас пристрою → блок-схема → типова розпіновка → підключення (живлення/шина/рівні) → «перший байт» → типові граблі → варіації класу.
  – 🧮 math: означення → інтуїція → формальний апарат → де в темі працює; глибина Фейнмана — ЧОМУ від першопричини, не констатація формул.
  – ⚙️ proj: задача → ідея → РОБОЧИЙ C/C++ (прошивка, не псевдокод) → складність і пастки.
• Метод Фейнмана, жива українська (без русизмів/кальок/канцеляриту; один термін на поняття; першоджерело назви в дужках), плавність (місток від абзацу до абзацу; перечитати суцільно).
• Формули — Unicode у код-блоках (без LaTeX), роздільник крапка. Worked-приклад: жирний підпис → код-блок із обчисленням → висновок.
• ФІГУРИ: лише SVG, чистий Python (figs.py у теці теми, ./img/); svgkit імпортуй; рамки лише textbox()/fitbox(); підключення «![опис](/${KIND}/${BOOK}/<галузь>/<slug>/img/<file>.svg)» від кореня репо; підпис — звичайний опис без номера й «Рис.»; після генерації svgcheck до «0 зауважень».
• КРОС-ЛІНКИ — лише на справжні залежності: короткий конспект 1–7 речень + [текст](book:<книга>/<slug>) (попап); ціль не переписуй; якщо цілі нема — створи порожній файл + зареєструй у маніфесті status:"empty".
• ФАКТИ — лише підтверджені вебом; познач статус доказовості; не клей «російське», коли точніше (українець/поляк/серб/єврей/грузин/вірменин/балт…); розрізняй ідею/теорію/реалізацію/систему/патент.
• МОВА ФІНАЛЬНА З ПЕРШОГО РАЗУ.`

async function callAgent(prompt, opts) {
  for (let a = 1; a <= MAX_TRIES; a++) {
    let r = null
    try { r = await agent(prompt, opts) } catch (e) { r = null }
    if (r != null) return r
    if (a >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}
function readFile(absPath, label) {
  return callAgent(`Read the file "${absPath}" and return its full content verbatim in field "content". If it does not exist, return content:"" and exists:false.`,
    { label, phase: 'Скаут', schema: { type: 'object', additionalProperties: false, required: ['content'], properties: { content: { type: 'string' }, exists: { type: 'boolean' } } } })
}

const UNITS = { type: 'object', additionalProperties: false, required: ['units'], properties: { units: { type: 'array', items: {
  type: 'object', additionalProperties: false, required: ['section', 'topicSlug', 'type', 'file', 'status'],
  properties: { section: { type: 'string' }, topicSlug: { type: 'string' }, topicTitle: { type: 'string' }, type: { type: 'string' }, file: { type: 'string' }, status: { type: 'string' } } } } } }
const RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, files: { type: 'array', items: { type: 'string' } }, note: { type: 'string' } } }

phase('Скаут')
const mf = await readFile(`${ROOT}\\${MF.replace(/\//g, '\\')}`, 'маніфест')
if (!mf || !mf.content) return { book: BOOK, error: 'маніфест не прочитано' }
const scout = await callAgent(
  `${CANON}\n\nОсь маніфест ${MF}:\n\n${mf.content}\n\nПоверни units — УСІ вставки з масивів hist/comp/math/proj кожної теми, де елемент {file,status} має status ∈ [${STATUSES.join(', ')}]${TYPE ? ` і type="${TYPE}"` : ''}${SECTION ? ` і галузь="${SECTION}"` : ''}. Для кожної: section (slug галузі), topicSlug, topicTitle, type (hist|comp|math|proj), file, status.`,
  { label: 'скаут', phase: 'Скаут', model: 'opus', schema: UNITS })
let work = (scout && scout.units) || []
work = work.filter((u) => TYPES.includes(u.type) && STATUSES.includes(u.status) && (!TYPE || u.type === TYPE) && (!SECTION || u.section === SECTION))
if (LIMIT) work = work.slice(0, LIMIT)
if (!work.length) return { book: BOOK, total: 0, note: 'черга порожня' }
log(`Вставок у роботі: ${work.length}`)

function dirWin(u) { return `${ROOT}\\${KIND}\\${BOOK}\\${u.section}\\${u.topicSlug}` }

const done = []
const results = await pipeline(work,
  (u) => {
    const factNote = u.type === 'hist' ? ' Перевір ВЕБОМ кожне історичне твердження (дати/імена/першість/походження).' : ' Перевір вебом усі факти/числа, якщо є.'
    return callAgent(
      `${CANON}\n\nТи пишеш ФІНАЛЬНУ вставку типу «${u.type}» — файл ${dirWin(u)}\\${u.file} (тема «${u.topicTitle || u.topicSlug}», галузь «${u.section}», книга «${BOOK}»).${u.status !== 'empty' ? ` Спершу прочитай наявний файл і виправ/поглиби за КАНОНОМ.` : ' Вставка нова.'}${factNote}\nДотримуйся шаблону типу «${u.type}». Згенеруй потрібні фігури (figs.py у теці теми, svgcheck до «0»). Перечитай суцільно. Поверни ok, files.`,
      { label: `${u.type}:${u.file}`, phase: 'Проза', model: (u.type === 'math' || u.type === 'hist') ? 'opus' : 'sonnet', schema: RET })
      .then((pr) => { if (pr && pr.ok) { done.push(u); return { ok: true, file: u.file } } return { ok: false, file: u.file, note: pr && pr.note } })
  })

phase('Статуси')
if (done.length) {
  const files = done.map((u) => u.file)
  await callAgent(
    `Онови маніфест ${ROOT}\\${MF.replace(/\//g, '\\')}: у масивах hist/comp/math/proj для елементів {file,status} зі file ∈ ${JSON.stringify(files)} зміни status на "done" (Edit точково). Поверни ok, count.`,
    { label: 'статуси→done', phase: 'Статуси', schema: { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } } })
}
const okN = results.filter((r) => r && r.ok).length
return { book: BOOK, total: work.length, done: okN, failed: work.length - okN }
