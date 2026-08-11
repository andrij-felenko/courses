export const meta = {
  name: 'review-batch',
  description: 'Перевірка й виправлення НЕЗАКОМІЧЕНИХ тем: один агент на теку. Механіка (textcheck: гомогліфи, LaTeX, русизми, текст у фігурах, SVG не в img/) + ЗВІРКИ зі змісту, що мають визначену відповідь (числа в прозі ↔ підпис фігури, стаття ↔ її вставка, перерахунок арифметики, подвійне означення поняття, підписи фігур ↔ текст, дати й імена через вебпошук) + МОВА КОДУ (17-cpp.js: C-блоки без пари C++ за §5 — лише перелічує у cppGaps, вкладок не пише: це авторська робота). Агент виправляє ЛИШЕ те, у чому певен; справжні суперечності піднімає окремим списком.',
  whenToUse: 'Після того, як статті написав інший ШІ або батч, і треба вичистити їх перед комітом.',
  phases: [
    { title: 'Перевірка', detail: 'по одному агенту на теку теми; пул задає concurrency' },
    { title: 'Звід', detail: 'зібрати ескалації й підсумки' },
  ],
}

/* args = { dirs: ["reference/unix-linux/devices/libata", …], concurrency?: 16, effort?: "high" } */
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const DIRS = Array.isArray(A.dirs) ? A.dirs.filter(Boolean) : []
const EFFORT = A.effort || 'high'
if (!DIRS.length) throw new Error('args.dirs обовʼязковий — перелік тек тем')

const ROOT = 'E:\\develop\\courses'

const PROMPT = (dir) => `Ти РЕДАКТОР у репозиторії книг ${ROOT}. Проза — українська. Працюй мовчки.
Твоя тека — і ТІЛЬКИ вона: ${ROOT}\\${dir.replace(/\//g, '\\')}

Спершу прочитай канон: ${ROOT}\\AUTHORING.md — §3 (версії, обсяги), §4 (ядро письма), §5 (формули, фігури), §6 (крос-посилання).
Формули — Unicode, БЕЗ LaTeX. Фігури — у підтеці img/, посилання від кореня репо: /reference/<книга>/<секція>/<тема>/img/<файл>.svg

═══ КРОК 1: МЕХАНІКА (виправляй сміливо) ═══
Запусти: node ${ROOT}\\scripts\\textcheck.js <твоя тека>
Виправ усе, що він показав:
• гомогліфи — латинська літера в кириличному слові (можна: textcheck <тека> --only 1 --apply)
• LaTeX у прозі — переклади в Unicode ($O(1)$ → \`O(1)\`, $\\frac{a}{b}$ → a/b, $\\sqrt{V}$ → √V,
  $\\mathbb{R}^N$ → \`ℝᴺ\`, $\\log_2 N$ → log₂N, $\\le$ → ≤, $N \\cdot V$ → N·V).
  Формула окремим рядком → \`\`\`-блок з Unicode. Якщо $ РОЗРИВАЄ речення — прочитай і віднови фразу.
• русизми — підстав правильне українське слово, читаючи речення. Якщо слово доречне — лишай.
• ТЕКСТ У ФІГУРАХ (клас 7) — описки й русизми всередині <text> у .svg правити так само.
• SVG НЕ В img/ — якщо .svg лежить поруч зі статтею, а не в img/: перенеси у img/,
  виправ посилання в .md на шлях від кореня репо, і виправ шлях запису у figs.py.
  Імена файлів — kebab-case (clock_tree.svg → clock-tree.svg).

═══ КРОК 2: ЗВІРКИ ЗІ ЗМІСТУ (у кожної є визначена відповідь) ═══
Прочитай статтю <slug>-d.md ПОВНІСТЮ, усі її вставки й підписи всіх фігур. Перевір:

1. ЧИСЛА в прозі проти чисел у ПІДПИСІ до фігури тієї ж статті. Розбіжність — дефект.
2. Твердження статті проти її ВСТАВКИ, на яку вона лінкує (особливо math-). Суперечність — дефект.
3. ПЕРЕРАХУЙ арифметику в робочих прикладах. Помилка — дефект.
4. Одне поняття означене ДВІЧІ по-різному (у статті й у вставці, або двічі в статті).
5. ПІДПИСИ Й СХЕМИ у фігурах проти тексту: чи не показує стрілка/каретка на інший елемент,
   ніж каже проза. Якщо у фігурі є ASCII-схема в код-блоці — перевір вирівнювання по колонках.
6. ДАТИ, ІМЕНА, ПРІОРИТЕТ винаходу в hist-вставках — звір ВЕБПОШУКОМ. Уважно з приписуванням:
   розділяй етнічність, громадянство, місце народження, інституцію; не приписуй імперії те,
   що зробили інші; винаходи бувають колективні — розрізняй «мав ідею», «опублікував теорію»,
   «побудував робочий зразок», «запатентував». Пиши стан доказовости, а не героїчний міф.

ВИПРАВЛЯЙ САМ те, у чому певен на 100% (арифметика, розбіжність чисел, зсунута каретка, дата).
НЕ ВИПРАВЛЯЙ, а ПІДНІМИ в escalations те, де два твердження конфліктують, а ти не можеш
довести, яке правильне. Не вгадуй — краще підняти.

═══ ЗАБОРОНЕНО ═══
• НЕ чіпай manifest.js · НЕ чіпай нічого поза своєю текою · НЕ роби git commit/add
• НЕ переписуй статтю й не дописуй нових розділів — ти редактор, не автор
• НЕ міняй обсяг заради обсягу

═══ КРОК 3: МОВА КОДУ — ТІЛЬКИ ПЕРЕЛІЧИТИ, НЕ ПИСАТИ ═══
Запусти: node ${ROOT}\\scripts\\checks\\17-cpp.js <твоя тека>
§5 канону: приклад мовою C завжди має сусідню вкладку C++ у тому самому :::tabs — обидві, не на вибір.
Код 0 — пропусти цей крок. Код 2 — скрипт перелічив C-блоки без пари. По КОЖНОМУ подивись сам блок і відсій ВИНЯТКИ §5:
  • простір ядра (#include <linux/…>, MODULE_LICENSE, збірка в .ko) — C++ там фізично не той інструмент;
  • приклад про сам C як мову (препроцесор, ABI, _Generic);
  • чужий заголовок, показаний як цитату;
  • переклад дав би різницю лише в рядках #include (сирий syscall(), ioctl() над POSIX-структурою).
Решту поклади у cppGaps рядками «<файл> блок #N — які ідіоми міняються» (malloc/free → контейнер чи unique_ptr,
close(fd) у goto out → RAII, char* + довжина → span/string_view, -1 та errno → виняток чи std::expected).
ВКЛАДКУ САМ НЕ ПИШЕШ: це авторська робота, не редакторська. Порожній cppGaps — теж відповідь.

═══ ПЕРЕВІРКА ПЕРЕД ЗВІТОМ ═══
node ${ROOT}\\scripts\\textcheck.js <тека>            → класи 1,2,3,7 мають бути 0
python ${ROOT}\\scripts\\svgcheck.py <тека> --links   → «із зауваженнями: 0», усі файли на місці

Поверни СТРОГО цей JSON.`

const RET = {
  type: 'object', additionalProperties: false, required: ['dir', 'ok'],
  properties: {
    dir: { type: 'string' },
    ok: { type: 'boolean' },
    mech: {
      type: 'object', additionalProperties: false,
      properties: {
        homoglyphs: { type: 'number' }, latex: { type: 'number' },
        russianisms: { type: 'number' }, svgText: { type: 'number' }, svgMoved: { type: 'number' },
      },
    },
    contentFixed: { type: 'array', items: { type: 'string' } },
    cppGaps: { type: 'array', items: { type: 'string' } },
    escalations: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['what', 'a', 'b'],
        properties: {
          what: { type: 'string' }, a: { type: 'string' }, b: { type: 'string' },
          checked: { type: 'string' },
        },
      },
    },
    gates: { type: 'string' },
    note: { type: 'string' },
  },
}

phase('Перевірка')
log(`тек на перевірку: ${DIRS.length}`)

const res = await parallel(DIRS.map((d) => () =>
  agent(PROMPT(d), { label: `рев:${d.split('/').pop()}`, phase: 'Перевірка', schema: RET, effort: EFFORT })))

phase('Звід')
const ok = res.filter(Boolean)
const esc = ok.flatMap((r) => (r.escalations || []).map((e) => ({ ...e, dir: r.dir })))
const sum = (k) => ok.reduce((s, r) => s + ((r.mech && r.mech[k]) || 0), 0)

const cppGaps = ok.flatMap((r) => (r.cppGaps || []).map((x) => `${r.dir}: ${x}`))

log(`готово: ${ok.length}/${DIRS.length} · ескалацій: ${esc.length} · C без пари C++: ${cppGaps.length}`)

return {
  dirs: DIRS.length,
  done: ok.length,
  failed: DIRS.length - ok.length,
  mech: {
    homoglyphs: sum('homoglyphs'), latex: sum('latex'),
    russianisms: sum('russianisms'), svgText: sum('svgText'), svgMoved: sum('svgMoved'),
  },
  contentFixed: ok.flatMap((r) => (r.contentFixed || []).map((x) => `${r.dir}: ${x}`)),
  cppGaps,
  escalations: esc,
  notOk: ok.filter((r) => !r.ok).map((r) => ({ dir: r.dir, note: r.note })),
}
