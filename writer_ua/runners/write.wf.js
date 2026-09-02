export const meta = {
  name: 'writer-ua',
  description: 'Конвеєр письма writer_ua: локальна черга з маніфесту, оркестратор із пулом активних, десять етапів над кожною одиницею, блоки <> замість JSON. args = {book, topic?|addrs?|status?|type?, limit?, active?, stagger?, id?, model?, effort?, status?}',
  phases: [
    { title: 'Черга', detail: 'ЛОКАЛЬНО: одиниці беруться з маніфесту через writer_ua/local/lib/units.js — жодного агента-скаута' },
    { title: 'Письмо', detail: 'оркестратор веде чергу; на кожну одиницю — десять етапів, агент кличеться лише там, де потрібне судження' },
  ],
}

/* ============================================================================
   write.wf.js — ЄДИНЕ МІСЦЕ, ДЕ КОНВЕЄР ТОРКАЄТЬСЯ АГЕНТА.

   Оркестратор і алгоритм про агентів не знають нічого: вони кличуть `ask(prompt,
   label)` і отримують текст. Тут `ask` лягає на `agent()` воркфлоу. Замінивши цей
   файл, той самий конвеєр ганяється насухо, з іншим постачальником або з підробкою
   на випробуванні — і саме так у ньому знаходили вади за нуль токенів.

   ⛔ БЕЗ `schema`. Домовленість конвеєра — блоки `<НАЗВА>…</НАЗВА>` в обидва боки:
   так вставляють і в запит, і в відповідь. `agent()` без схеми вертає текст, і його
   читає `parse.js`. Схема тут означала б JSON у відповіді, тобто другий формат.

   ⚠️ ВИЧЕРПАНИЙ ЛІМІТ НЕ КИДАЄ ПОМИЛКИ — `agent()` тихо вертає `null`. Один `null` це
   ще «агент не впорався»; кілька ПОСПІЛЬ по всьому пулу — це стіна. Тому нулі
   рахуються, і на смузі кидається помилка з `limit:true`: оркестратор має свій
   протокол стіни (одна контрольна пауза, одна повторна спроба, далі зупинка).
   ========================================================================== */

let A = args
if (typeof A === 'string') { try { A = JSON.parse(A) } catch (e) { A = {} } }
A = A || {}

const ROOT = A.root ? String(A.root) : 'E:\\develop\\courses'
const O = require(`${ROOT}\\writer_ua\\runners\\orchestrator.js`)
const { algorithm } = require(`${ROOT}\\writer_ua\\runners\\algorithm.js`)
const LOC = require(`${ROOT}\\writer_ua\\runners\\local.js`)
const U = require(`${ROOT}\\writer_ua\\local\\lib\\units.js`)

const BOOK = A.book ? String(A.book) : ''
if (!BOOK && !A.id) throw new Error('args.book обовʼязковий (або args.id, щоб підняти обірваний батч)')

/* ── черга: ЛОКАЛЬНО, з маніфесту ──────────────────────────────────────────────
   Скаута-агента немає й не треба: що писати, точно знає маніфест, а «схоже на
   потрібне» від агента коштувало б токенів і давало б гірший добір.               */

/** Запис `units.js` → одиниця алгоритму. Тип бере з частини: версія або вставка. */
const toUnit = (r) => LOC.unitOf(
  r.book, r.slug,
  r.insert ? r.insert : r.part === 'basic' ? 'basic' : 'article',
  r.part === 'basic' ? 'БАЗОВА' : 'ДЕТАЛЬНА',
  r.file || '')

function pickUnits() {
  if (Array.isArray(A.units) && A.units.length) return A.units
  const all = U.enumerate({ books: [BOOK] })
  let picked
  if (A.addrs && A.addrs.length) {
    const r = U.byAddrs([].concat(A.addrs))
    if (r.missing.length) throw new Error(`адрес немає в маніфесті: ${r.missing.join(', ')}`)
    if (r.ambiguous.length) throw new Error(`адреси неоднозначні: ${r.ambiguous.join(', ')}`)
    picked = r.units
  } else if (A.topic) {
    picked = all.filter((u) => u.slug === String(A.topic) &&
      (A.type ? (u.insert || u.part) === String(A.type) : u.part === 'detailed'))
    if (!picked.length) throw new Error(`теми «${A.topic}» з такою версією у книзі «${BOOK}» немає`)
  } else {
    picked = U.filter(all, {
      status: [].concat(A.status || 'pending'),
      type: A.type ? [].concat(A.type) : ['detailed'],
    }).slice(0, Number(A.limit) || 1)
  }
  return picked.map(toUnit)
}

phase('Черга')
const UNITS = A.id && !BOOK ? [] : pickUnits()
log(`черга: ${UNITS.length} одиниць${UNITS.length ? ' — ' + UNITS.map((u) => u.id).join(', ') : ' (піднімаємо з теки батчу)'}`)

/* ── ask: єдиний місток до агента ──────────────────────────────────────────── */

const MODEL = A.model || 'opus'
const EFFORT = A.effort || 'high'
const NULL_STREAK = 3          // < пулу активних, щоб зловити стіну раніше за весь фронт
let nulls = 0

async function ask(prompt, label) {
  const out = await agent(prompt, { label, phase: 'Письмо', model: MODEL, effort: EFFORT })
  if (out == null) {
    nulls++
    if (nulls >= NULL_STREAK)
      throw Object.assign(new Error(`порожня відповідь ${nulls} разів поспіль — схоже на стіну ліміту`), { limit: true })
    throw new Error(`порожня відповідь на «${label}»`)
  }
  nulls = 0
  return String(out)
}

/* ── прогін ────────────────────────────────────────────────────────────────── */

phase('Письмо')
const report = await O.run({
  id: A.id,
  units: UNITS,
  active: Number(A.active) || 4,
  stagger: A.stagger === undefined ? 2000 : Number(A.stagger),
  onEvent: (e) => {
    if (e.ev === 'start') log(`▶ ${e.unit} (активних ${e.active}, у черзі ${e.pending})`)
    else if (e.ev === 'done') log(`✔ ${e.unit}`)
    else if (e.ev === 'fail') log(`✖ ${e.unit}: ${e.message}`)
    else if (e.ev === 'enqueue') log(`+ ${e.n} одиниць у чергу від ${e.unit}`)
    else if (e.ev === 'refused') log(`⚠ стеля: відмовлено ${e.n}`)
    else if (e.ev === 'limit-probe') log(`⏳ схоже на ліміт (${e.unit}) — контрольна пауза`)
    else if (e.ev === 'wall') log(`⛔ стіна ліміту, у черзі лишилось ${e.pending}`)
    else if (e.ev === 'restore') log(`↺ відновлено з теки: ${e.n}`)
  },
  algorithm: (unit, ctx) => algorithm(unit, ctx, { ask, status: A.writeStatus || 'recheck' }),
})

log(`батч ${report.id}: зроблено ${report.done}, провалено ${report.failed}, пропущено ${report.skipped}`)
log(`теку прогону лишено: ${report.logs}`)
log(`маніфест: ${report.manifest}`)
return report
