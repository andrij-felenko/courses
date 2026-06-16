export const meta = {
  name: 'migrate-chemistry',
  description: 'Крок 5 (Хімія): розбити розділи на теми-файли book/chemistry/<галузь>/<slug>/<slug>.md (основа), вступи розділів → містки guide/basic-chemistry, прибрати курс-навігацію. Агент на модуль.',
  phases: [{ title: 'Розбір', detail: 'агент модуля розбиває розділи на теми + містки' }],
}

const ROOT = 'E:/develop/courses'
const MODULES = ['m1-atoms', 'm2-bonds', 'm3-reactions', 'm4-inorganic', 'm5-organic', 'm6-counting']

const RET = {
  type: 'object', additionalProperties: false, required: ['topics'],
  properties: {
    topics: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['mrt', 'branch', 'slug', 'path'],
      properties: { mrt: { type: 'string' }, branch: { type: 'string' }, slug: { type: 'string' }, path: { type: 'string' } } } },
    bridges: { type: 'array', items: {
      type: 'object', additionalProperties: false, required: ['chapter', 'path'],
      properties: { chapter: { type: 'string' }, title: { type: 'string' }, path: { type: 'string' } } } },
    note: { type: 'string' },
  },
}

phase('Розбір')
const results = await pipeline(MODULES, (mod) => agent(
  `Ти мігруєш Модуль «${mod}» книги «Хімія» у нову структуру book/ + guide/. Це ПЕРЕНЕСЕННЯ вмісту (не переписування прози).

КРОК 1 — маршрут. Прочитай "${ROOT}/book/chemistry/manifest.js". Знайди ВСІ теми, чий origin починається з "chemistry/${mod}/". Для кожної з origin "chemistry/${mod}/<rDir>#<mrt>" дістаєш: branch (slug галузі, у якій тема лежить у маніфесті), slug (теми), rDir (тека розділу), mrt.

КРОК 2 — по кожному розділу "${ROOT}/chemistry/${mod}/<rDir>/<rDir>.md":
  (a) Прочитай файл. Він має заголовок "# Розділ …", вступ, і секції "## М.Р.Т Назва".
  (b) Для КОЖНОЇ секції ## М.Р.Т: за mrt знайди її branch+slug (крок 1). Запиши вміст секції (від її "## " до наступного "## " або кінця) у файл "${ROOT}/book/chemistry/<branch>/<slug>/<slug>.md" — це ОСНОВНИЙ варіант (basic). Перший рядок зроби "# <Назва теми>" (з маніфесту). Решту вмісту секції лиши ЯК Є (проза, формули, рамки 🏠/🧪/📜, посилання на фігури "img/…" — НЕ чіпай). Прибери з теми рядок "> ▶️ Далі: …", якщо він у цій секції.
  (c) Вступ розділу (рядок "# Розділ …" і абзаци ДО першої "## ") — це курсовий МІСТОК. Запиши його у "${ROOT}/guide/basic-chemistry/bridges/${mod}__<rDir>.md" (заголовок "# <назва розділу>"). Це поясн­ення для курсу, не для книги.
  (d) Внутрішні посилання на інші теми/розділи (../…, §X.Y) лиши як є поки (полагодимо окремо).
НЕ видаляй старих файлів. figs.py та img/ НЕ чіпай (фігури перенесе скрипт за номером M-R-T).

Поверни topics:[{mrt,branch,slug,path}] (усі написані теми) і bridges:[{chapter:rDir,title,path}].`,
  { label: `chem:${mod}`, phase: 'Розбір', schema: RET }
).then(r => ({ mod, ...(r || { topics: [] }) })))

const ok = results.filter(Boolean)
let topics = 0, bridges = 0
ok.forEach(r => { topics += (r.topics || []).length; bridges += (r.bridges || []).length; log(`  ${r.mod}: тем ${(r.topics || []).length}, містків ${(r.bridges || []).length}`) })
log(`РАЗОМ: тем ${topics}, містків ${bridges}`)
return { modules: ok.length, topics, bridges, routed: ok.flatMap(r => (r.topics || []).map(t => ({ ...t, mod: r.mod }))) }
