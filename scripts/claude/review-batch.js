export const meta = {
  name: 'review-batch',
  description: 'Людська ревізія тем, які написав Antigravity. Черга — теми зі статусом recheck (саме його ставить finish-batch: конвеєр свою частину зробив, людина ще не читала). Один редактор на тему: читає _canon.md книги, статтю й усі вставки, ганяє дешеву механіку (textcheck, svgcheck, 17-cpp) і судить те, чого локальні перевірки не бачать — збиті одиниці, вигадані імена інтерфейсів, переказ власних вставок, русизми повз словник, неідіоматичний C++. Виправляє те, у чому певен; суперечності піднімає в escalations. Наприкінці — recheck→done для тем, що пройшли.',
  whenToUse: 'Після того, як батч Antigravity закрився і теми стоять recheck — перед тим, як вважати їх готовими.',
  phases: [
    { title: 'Черга', detail: 'знайти теми зі статусом recheck (дешевий агент, grep по маніфесту)' },
    { title: 'Ревізія', detail: 'один редактор на тему; пул задає concurrency' },
    { title: 'Маніфест', detail: 'recheck→done для тем, що пройшли без ескалацій' },
    { title: 'Звід', detail: 'зібрати ескалації й підсумки' },
  ],
}

/* args = { book: "unix-linux", kind?: "reference"|"book"|"catalog"|"guide", limit?: 20,
            dirs?: [...], concurrency?: 4, effort?: "high", apply?: true } */
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const BOOK = A.book || ''
const KIND = A.kind || 'book'
const LIMIT = A.limit || 20
const EFFORT = A.effort || 'high'
const APPLY = A.apply !== false
const ROOT = 'E:\\develop\\courses'
if (!BOOK && !(Array.isArray(A.dirs) && A.dirs.length)) throw new Error('треба або args.book, або args.dirs')

/* ── Черга ───────────────────────────────────────────────────────────────────
   recheck ставить finish-batch на все, що написав Antigravity. Це і є вхід ревізії:
   написано й перевірено конвеєром, але людським оком не бачено. */
phase('Черга')
let DIRS = Array.isArray(A.dirs) ? A.dirs.filter(Boolean) : []
if (!DIRS.length) {
  const q = await agent(
    `Прочитай ${ROOT}\\${KIND}\\${BOOK}\\manifest.js і поверни перші ${LIMIT} тем, у яких detailed.status АБО basic.status === "recheck".
Тека теми — ${KIND}/${BOOK}/<slug секції>/<slug теми>. Перевір Bash-ом, що тека існує, і поверни лише наявні.
Нічого не змінюй, нічого не пиши.`,
    { label: 'черга:recheck', phase: 'Черга', model: 'sonnet', effort: 'low',
      schema: { type: 'object', additionalProperties: false, required: ['dirs'],
        properties: { dirs: { type: 'array', items: { type: 'string' } }, total: { type: 'number' } } } })
  DIRS = (q && q.dirs) || []
  log(`тем зі статусом recheck у черзі: ${DIRS.length}${q && q.total ? ` (усього в книзі ${q.total})` : ''}`)
}
if (!DIRS.length) return { dirs: 0, note: 'тем зі статусом recheck не знайдено' }

const PROMPT = (dir) => `Ти РЕДАКТОР у репозиторії книг ${ROOT}. Проза — українська. Працюй мовчки.
Твоя тека — і ТІЛЬКИ вона: ${ROOT}\\${dir.replace(/\//g, '\\')}

Цю тему написав інший ШІ. Вона вже пройшла сімнадцять машинних перевірок — тому шукай НЕ те,
що ловить скрипт, а те, що скрипт пропускає. Нижче перелічено рівно ті класи, на яких він
провалювався в бою.

═══ 0. ПРАВИЛА, ЗА ЯКИМИ СУДИШ ═══
• ${ROOT}\\AUTHORING.md — §3 (версії, обсяги), §4 (ядро письма), §5 (формули, фігури), §6 (лінки).
• ${ROOT}\\${KIND}\\${BOOK}\\_canon.md — ЯКЩО ФАЙЛ Є, прочитай його ПЕРШИМ. Це правила саме цієї
  книги, і там, де вони уточнюють загальний канон, суди за ними. Немає файлу — суди за AUTHORING.
• ОБСЯГ: Antigravity пише за піднятими смугами — детальна орієнтир 2950–3650, api- 1600–3200,
  решта вставок ×1.30. НЕ став «замало» за канонними числами: вони не про цей текст.

═══ 1. МЕХАНІКА (дешево, виправляй сміливо) ═══
node ${ROOT}\\scripts\\textcheck.js <тека>        → гомогліфи, LaTeX, русизми, текст у фігурах
python ${ROOT}\\scripts\\svgcheck.py <тека> --links → геометрія фігур, усі підключені на місці
Виправ усе, що показали. Формули — Unicode, БЕЗ LaTeX. Фігури — лише в img/, шлях від кореня репо.
SVG правиться в figs.py і перегенеровується, а не редагується руками.

═══ 2. ЧОГО СКРИПТ НЕ БАЧИТЬ — головна робота ═══
Прочитай детальну ПОВНІСТЮ, усі вставки й підписи фігур. Шукай:

1. ЗБИТІ ОДИНИЦІ Й ПОРЯДКИ. Найдорожча помилка цього корпусу. «200 мікросекунд за період у
   100 мікросекунд» там, де насправді мілісекунди; мегабайти замість мебібайтів; відсоток від
   іншої бази. Пропорція може бути правильною, а одиниця — ні. Перерахуй кожен приклад до кінця.

2. ІМЕНА, ЯКИХ НЕ ІСНУЄ. Директива, метод, прапорець, файл чи опція, вигадані за аналогією з
   наявними, — читач іде з ними в консоль. Кожну назву інтерфейсу, якої ти не пам'ятаєш ТОЧНО,
   звір із документацією або man-сторінкою (вебпошук), а не з відчуттям «схоже на правду».
   Реальний приклад із цього корпусу: у статті стояла unit-директива systemd, якої немає.

3. СТАТТЯ ПЕРЕКАЗУЄ ВЛАСНІ ВСТАВКИ. Написано hist- — і та сама історія ще раз стисло в статті;
   написано proj- — і той самий код у двох файлах. Ознака: абзац статті й абзац вставки можна
   поміняти місцями без утрати. Це не глибина, це рахунок за друге читання того самого.
   У статті лишається речення з лінком, розгортання — у вставці.

4. ЗАХІД, ЯКИЙ АНОНСУЄ ЗАМІСТЬ ПОЯСНЮВАТИ. «Ця стаття розкриває…», «спершу розглянемо…»,
   переказ заголовка іншими словами. §4: перший абзац — конкретна ситуація, де без цього
   механізму щось ламається, з іменами й числами. Тест: викресли перший абзац — стаття щось
   утратила? Ні — це був підпис.

5. РУСИЗМИ Й КАЛЬКИ ПОВЗ СЛОВНИК. textcheck ловить список, а не мову. Реально прослизали:
   «однако», «проектирования», «запущенного», «створимого», «планивальник», «басейни потоків»
   (thread pools), «Випромінюється» про сигнал, «у проміжності», «протиборство» не в тому роді.
   Читай очима, а не грепом.

6. C++, ЯКИЙ НЕ ІДІОМАТИЧНИЙ. Вкладка cpp є, але всередині C з \`std::cout\`. Або тонше:
   \`string_view::data()\` передають у C-API, що чекає нуль-термінований рядок; \`malloc/free\`
   замість контейнера; \`goto out\` замість RAII. Пиши в cppGaps — сам не переписуй.

7. ФІГУРА СУПЕРЕЧИТЬ ТЕКСТУ. Число в підписі проти числа в прозі; стрілка показує на інший
   елемент, ніж каже речення; у дереві на схемі бракує рівня, який стаття називає обов'язковим.

8. ДАТИ, ІМЕНА, ПРІОРИТЕТ — вебпошуком. Розділяй етнічність, громадянство, місце народження,
   інституцію; не приписуй імперії зробленого іншими; розрізняй «мав ідею» / «опублікував» /
   «побудував робочий зразок» / «запатентував». Пиши стан доказовости, а не героїчний міф.
   Транслітерація імен — теж факт: Tejun Heo — кореєць, а не «Тейдзюн».

ВИПРАВЛЯЙ САМ те, у чому певен на 100% (арифметика, одиниця, дата, русизм, зсунуте посилання).
ПІДНІМИ в escalations те, де два твердження конфліктують, а довести не можеш. Не вгадуй.

═══ 3. МОВА КОДУ — ПЕРЕЛІЧИТИ, НЕ ПИСАТИ ═══
node ${ROOT}\\scripts\\checks\\17-cpp.js <тека>
Код 0 — пропусти. Інакше по кожному C-блоку без пари відсій ВИНЯТКИ §5: простір ядра
(#include <linux/…>, MODULE_LICENSE) · приклад про сам C як мову · чужий заголовок як цитата ·
переклад дав би різницю лише в #include. Решту — у cppGaps рядками «<файл> блок #N — які ідіоми
міняються». Вкладку САМ НЕ ПИШЕШ: це авторська робота.

═══ ЗАБОРОНЕНО ═══
• НЕ чіпай manifest.js — статуси переставить окремий крок · НЕ виходь за свою теку
• НЕ роби git commit/add · НЕ переписуй статтю наново й не дописуй розділів — ти редактор
• НЕ лікуй обсяг чи ясність скороченням · НЕ запускай gate.js (він уже відпрацював, це дорого)

═══ ПЕРЕД ЗВІТОМ ═══
node ${ROOT}\\scripts\\textcheck.js <тека>            → класи 1,2,3,7 мають бути 0
python ${ROOT}\\scripts\\svgcheck.py <тека> --links   → «із зауваженнями: 0», усі файли на місці

ok = true лише тоді, коли ти вважаєш тему готовою до статусу done: помилок не лишилось, а те,
що лишилось, — у escalations. Поверни СТРОГО цей JSON.`

const RET = {
  type: 'object', additionalProperties: false, required: ['dir', 'ok'],
  properties: {
    dir: { type: 'string' },
    ok: { type: 'boolean' },
    mech: {
      type: 'object', additionalProperties: false,
      properties: {
        homoglyphs: { type: 'number' }, latex: { type: 'number' },
        russianisms: { type: 'number' }, svgText: { type: 'number' }, svgFigures: { type: 'number' },
      },
    },
    contentFixed: { type: 'array', items: { type: 'string' } },
    unitsFixed: { type: 'array', items: { type: 'string' } },
    namesChecked: { type: 'array', items: { type: 'string' } },
    duplication: { type: 'array', items: { type: 'string' } },
    cppGaps: { type: 'array', items: { type: 'string' } },
    escalations: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['what', 'a', 'b'],
        properties: { what: { type: 'string' }, a: { type: 'string' }, b: { type: 'string' }, checked: { type: 'string' } },
      },
    },
    gates: { type: 'string' },
    note: { type: 'string' },
  },
}

phase('Ревізія')
log(`тем на ревізію: ${DIRS.length}`)
const res = await parallel(DIRS.map((d) => () =>
  agent(PROMPT(d), { label: `рев:${d.split('/').pop()}`, phase: 'Ревізія', schema: RET, effort: EFFORT })))

const ok = res.filter(Boolean)
const passed = ok.filter((r) => r.ok && !(r.escalations || []).length).map((r) => r.dir)

/* ── Маніфест ────────────────────────────────────────────────────────────────
   Єдине місце, де ревізія торкається статусів: тема, яку редактор пройшов і не лишив
   ескалацій, переходить recheck → done. Усе інше лишається recheck і чекає людини. */
phase('Маніфест')
let manifest = 'пропущено'
if (APPLY && passed.length) {
  const ops = passed.map((d) => d.split('/').pop())
  const r = await agent(
    `Постав detailed → done для цих тем у ${ROOT}\\${KIND}\\${BOOK}\\manifest.js: ${ops.join(', ')}.
Тільки через node ${ROOT}\\scripts\\manifest-patch.js "${KIND}/${BOOK}/manifest.js" --ops <файл.json>
(операції {"op":"status","slug":"…","ver":"detailed","status":"done"}; для тем, де basic теж recheck,
додай таку саму операцію з ver:"basic" — перевір статус у маніфесті, не вгадуй).
Файл операцій поклади у ${ROOT}\\scripts\\_finish\\_review-ops-${BOOK}.json.
Спершу прожени БЕЗ --apply і покажи вивід, тоді з записом. Руками маніфест не редагуй.`,
    { label: 'маніфест:recheck→done', phase: 'Маніфест', model: 'sonnet', effort: 'low',
      schema: { type: 'object', additionalProperties: false, required: ['out'],
        properties: { out: { type: 'string' }, changed: { type: 'number' } } } })
  manifest = (r && r.out) || 'без відповіді'
} else if (!passed.length) manifest = 'жодна тема не пройшла чисто — статуси не чіпали'

phase('Звід')
const esc = ok.flatMap((r) => (r.escalations || []).map((e) => ({ ...e, dir: r.dir })))
const sum = (k) => ok.reduce((s, r) => s + ((r.mech && r.mech[k]) || 0), 0)
const flat = (k) => ok.flatMap((r) => (r[k] || []).map((x) => `${r.dir}: ${x}`))
log(`пройшли чисто: ${passed.length}/${DIRS.length} · ескалацій: ${esc.length}`)

return {
  dirs: DIRS.length,
  reviewed: ok.length,
  failed: DIRS.length - ok.length,
  passedToDone: passed.length,
  mech: {
    homoglyphs: sum('homoglyphs'), latex: sum('latex'), russianisms: sum('russianisms'),
    svgText: sum('svgText'), svgFigures: sum('svgFigures'),
  },
  unitsFixed: flat('unitsFixed'),
  namesChecked: flat('namesChecked'),
  duplication: flat('duplication'),
  contentFixed: flat('contentFixed'),
  cppGaps: flat('cppGaps'),
  escalations: esc,
  stillRecheck: ok.filter((r) => !r.ok || (r.escalations || []).length).map((r) => ({ dir: r.dir, note: r.note })),
  manifest,
}
