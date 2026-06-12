export const meta = {
  name: 'complete-module',
  description: 'Завершити модуль курсу embedded: Opus структурує кожен файл, Sonnet пише прозу, Sonnet вичитує. args = номер модуля (1–14).',
  phases: [
    { title: 'Скаут', detail: 'розбити чергу модуля на файли-одиниці (Sonnet)' },
    { title: 'Структура', detail: 'Opus планує каркас кожного файлу' },
    { title: 'Проза', detail: 'Sonnet пише текст + фігури за каркасом' },
    { title: 'Вичитка', detail: 'Sonnet: орфографія, слова, плавність — окремо на кожен файл' },
  ],
}

let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) {} }   // якщо дійшло як JSON-рядок ("4" або "{\"module\":4}")
if (_a && typeof _a === 'object') _a = (_a.module != null ? _a.module : _a.n)
const N = Number(_a)
if (!N || N < 1) throw new Error('Передай номер модуля: args = N (1–14)')
const ROOT = 'E:\\develop\\courses\\embedded'

/* ── Спільний канон (ІДЕНТИЧНИЙ префікс у всіх агентів → кеш; читати AUTHORING не треба) ── */
const CANON = `КАНОН (стисло; повне — ${ROOT}\\AUTHORING.md, але читати НЕ обов'язково):
• Українською, стиль Фейнмана: глибоко, від першопричин, інтуїція→деталі; без «як для 4-річного», без зайвого пафосу.
• Нумерація М.Р.Т: заголовки тем «## М.Р.Т Назва»; підписи фігур «Рис. М.Р.Т.k» (в історіях «Рис. М.Р.Тi.k»).
• Обсяги: тема — 2200–2600 слів прози (важкі — більше); вставка 🔌/🧮/⚙️ — 300–1000; історія 📜 — 2000–8000.
• Формули — Unicode у код-блоках (10⁻⁹, ε, ≈, ², ₀, ·), без LaTeX; десятковий роздільник — крапка.
• Біля важливих понять — рамка «> 🔧 Навіщо це»; worked-приклад — жирний підпис + код-блок з покроковим обчисленням.
• КОД у прикладах і ⚙️-вставках — реальний C/C++ (мова курсу, прошивка ESP32), НЕ псевдокод: короткий, коректний, компільований фрагмент.
• Двомовні терміни: «провідність (conductivity, σ)». Не забігати вперед (лише цей і попередні розділи); назад — «§М.Р.Т».
• Фігури — чистий Python → ./img/*.svg; кожна несе вагу. СПІЛЬНІ ПОМІЧНИКИ імпортуй, НЕ переписуй: на початку figs.py «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools')); from svgkit import *». Рамки з текстом — ЛИШЕ через textbox()/fitbox() зі svgkit (вони самі підганяють рамку під напис, текст не вилазить за межі). Після генерації переглянь SVG — усі написи в межах фігур.
• Плавність (§5/§17): кожен абзац і підрозділ — місток від попереднього; наскрізна нитка; перед завершенням перечитай суцільно.`

/* ── Схеми ── */
const UNITS = { type:'object', additionalProperties:false, required:['units'], properties:{ units:{ type:'array', items:{
  type:'object', additionalProperties:false, required:['chapter','kind','file','dir','brief','statusLines'],
  properties:{
    chapter:{type:'string'}, kind:{type:'string',enum:['chapter-main-new','chapter-main-append','extra']},
    file:{type:'string'}, dir:{type:'string'}, brief:{type:'string'},
    statusLines:{type:'array',items:{type:'string'}},
  } } } } }
const STRUCT = { type:'object', additionalProperties:false, required:['outline','figures'], properties:{
  outline:{type:'string', description:'markdown-каркас файлу: H1, вступ, кожна тема «## М.Р.Т Назва» з 3–6 пунктами що розкрити, де приклад, де рамки 🔧, перехресні §-лінки — БЕЗ прози'},
  figures:{type:'array', items:{ type:'object', additionalProperties:false, required:['id','shows'], properties:{
    id:{type:'string',description:'ім\'я svg, напр. fig-4-3-2-1-partition-table'}, caption:{type:'string'}, shows:{type:'string',description:'що саме показує і який висновок'} } } },
} }
const RET = { type:'object', additionalProperties:false, required:['ok','statusLines'], properties:{
  ok:{type:'boolean'}, statusLines:{type:'array',items:{type:'string'}}, files:{type:'array',items:{type:'string'}}, note:{type:'string'} } }

/* ── Скаут (Sonnet — механічний розбір) ── */
phase('Скаут')
const scout = await agent(
  `Знайди папку Модуля ${N} (block-${N}-…) і прочитай її _status.md та секцію Модуля ${N} у ${ROOT}\\PLAN.md (повні назви тем і шляхи папок розділів «block-${N}-…/folder/file.md»).
Збери ОДИНИЦІ РОБОТИ — усе зі статусом ⬜ у Модулі ${N}, згруповане по ФАЙЛАХ:
- розділ із ⬜-ТЕМАМИ («- ⬜ ${N}.Р.Т Назва») → одна одиниця: kind="chapter-main-new" якщо головний .md ще не існує, інакше "chapter-main-append". file=головний .md, dir=папка розділу, brief=перелік ⬜-тем із номерами й назвами, statusLines=ці ⬜-рядки тем.
- кожен ⬜ рядок ВСТАВКИ/ІСТОРІЇ (📜/🔌/🧮/⚙️, з іменем файлу в \`…\`) → одиниця kind="extra", file=те ім'я, dir=папка того ж розділу, brief=тип+назва+(до теми М.Р.Т), statusLines=[той рядок].
Поверни всі одиниці.`,
  { label:`scout:M${N}`, phase:'Скаут', model:'sonnet', schema:UNITS }
)
const units = (scout?.units || [])
log(`Модуль ${N}: ${units.length} файлів-одиниць`)

/* ── Промпти стадій ── */
function structPrompt(u){
  const head = `${CANON}\n\nТи OPUS — АРХІТЕКТОР. Сплануй ТОЧНИЙ каркас одного файлу (НЕ пиши прозу — лише структуру: що саме має бути написано).`
  if (u.kind==='chapter-main-append')
    return `${head}\nСпершу прочитай наявний ${ROOT}\\${u.dir}\\${u.file} (щоб не дублювати — план лише для НОВИХ тем). Нові теми: ${u.brief}. Для кожної нової теми дай у outline: «## М.Р.Т Назва» + 3–6 пунктів що розкрити (інтуїція→механізм→деталі), worked-приклад (умова), де рамка 🔧, перехресні §-лінки; познач, що вставляється ПЕРЕД «> ▶️ Далі». У figures — які фігури потрібні новим темам і що кожна показує.`
  if (u.kind==='chapter-main-new')
    return `${head}\nНовий розділ ${u.dir}\\${u.file}. Теми: ${u.brief}. outline: H1 розділу, вступ-мотивація (про що), і кожна тема «## М.Р.Т Назва» з 3–6 пунктами що розкрити, worked-приклад, рамки 🔧, перехресні §-лінки, і рядок «> ▶️ Далі …» в кінці. figures — повний перелік фігур з тим, що кожна показує (кожна несе вагу).`
  return `${head}\nФайл-вставка ${u.dir}\\${u.file}: ${u.brief}. Сплануй каркас за типом (📜 історія §10 — заголовки за темами оповіді; 🔌 §16 — клас пристрою→блок-схема→розпіновка→підключення→«перший байт»→граблі→варіації; 🧮 — означення→інтуїція→апарат→де в курсі; ⚙️ — задача→ідея→РОБОЧИЙ КОД C/C++ (не псевдокод)→складність/пастки на МК). figures — 0–2 за потреби.`
}
function prosePrompt(u, st){
  const figDir = (u.kind==='extra') ? `окремий ${ROOT}\\${u.dir}\\figs-${u.file.replace('.md','')}.py` : `${ROOT}\\${u.dir}\\figs.py (нові функції, НЕ ламай наявних)`
  const base = `${CANON}\n\nТи SONNET — пишеш ПОВНУ прозу за готовим каркасом від архітектора. Дотримуйся каркаса й обсягів канону, став плавність одразу.\n\nКАРКАС:\n${st.outline}\n\nФІГУРИ (реалізуй усі): ${JSON.stringify(st.figures)}`
  const fig = `\nФігури: ${figDir} — на початку імпортуй спільний kit (import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools')); from svgkit import *), НЕ переписуй примітиви; рамки з текстом лише через textbox()/fitbox() (текст не вилазить). УНІКАЛЬНІ імена svg у ./img/, і ЗАПУСТИ скрипт (python …). Підключи в текст «![підпис](img/fig-….svg)» + «*Рис. М.Р.Т.k. …*».`
  if (u.kind==='chapter-main-append')
    return `${base}${fig}\nДОПИШИ нові теми у наявний ${ROOT}\\${u.dir}\\${u.file} ПЕРЕД фінальним «> ▶️ Далі …» (він лишається останнім); решту файлу НЕ чіпай.\nПоверни ok, statusLines=${JSON.stringify(u.statusLines)}, files.`
  if (u.kind==='chapter-main-new')
    return `${base}${fig}\nСтвори ${ROOT}\\${u.dir}\\${u.file} цілком за каркасом.\nПоверни ok, statusLines=${JSON.stringify(u.statusLines)}, files.`
  return `${base}${fig}\nСтвори файл-вставку ${ROOT}\\${u.dir}\\${u.file} (H1: історія «# 📜 …», інша вставка «# …»).\nПоверни ok, statusLines=${JSON.stringify(u.statusLines)}, files.`
}
function polishPrompt(u){
  return `Ти SONNET — КОРЕКТОР. Відкрий ${ROOT}\\${u.dir}\\${u.file} і виправ ЛИШЕ мову:
1) орфографія й пунктуація; 2) невдалі слова — кальки, русизми, канцелярит, недоречні англіцизми, випадкова синонімія (один термін на поняття в межах файлу); 3) ПЛАВНІСТЬ — містки між абзацами й темами, перехідні речення, без різких стрибків.
СУВОРО НЕ МІНЯЙ: зміст, факти, формули, числа, worked-приклади, фігури й підписи, заголовки (## М.Р.Т), callout-и (🔧/📜/🔌/🧮/⚙️/▶️), посилання. Це шліфування мови, не переписування. Запиши назад той самий файл.
Поверни ok, statusLines=${JSON.stringify(u.statusLines)}.`
}

/* ── Конвеєр: Структура(Opus) → Проза(Sonnet) → Вичитка(Sonnet); кожен файл незалежно ── */
const results = await pipeline(
  units,
  (u) => agent(structPrompt(u), { label:`структура:${u.file}`, phase:'Структура', model:'opus', schema:STRUCT }),
  (st, u) => st ? agent(prosePrompt(u, st), { label:`проза:${u.file}`, phase:'Проза', model:'sonnet', schema:RET })
                : { ok:false, statusLines:u.statusLines, note:'структура не вдалася' },
  (pr, u) => {
    if (!pr || !pr.ok) return { ok:false, statusLines:u.statusLines, note:(pr&&pr.note)||'проза не вдалася' }
    return agent(polishPrompt(u), { label:`вичитка:${u.file}`, phase:'Вичитка', model:'sonnet', schema:RET })
      .then(p => ({ ok:true, statusLines:u.statusLines, polished:!!(p&&p.ok), files:pr.files }))
  }
)

const all = results.filter(Boolean)
const done = all.filter(r => r.ok)
const failed = all.filter(r => !r.ok)
const doneLines = done.flatMap(r => r.statusLines || [])
const failedLines = failed.flatMap(r => r.statusLines || [])
const unpolished = done.filter(r => !r.polished).length
log(`Модуль ${N}: готово ${done.length}/${units.length}; рядків ⬜→🟢: ${doneLines.length}; без вичитки: ${unpolished}; провалів: ${failed.length}`)
return { module:N, total:units.length, done:done.length, failed:failed.length, doneLines, failedLines, failedNotes: failed.map(f=>f.note).slice(0,20) }
