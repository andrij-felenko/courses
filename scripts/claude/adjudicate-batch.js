export const meta = {
  name: 'adjudicate-batch',
  description: 'Розсуд ескалацій ревʼю: агент на теку. Кожен ДОВОДИТЬ відповідь джерелом (вихідний код ядра, man, офіційна документація, вебпошук), тоді ПРАВИТЬ статтю. Питання про людей, дати й пріоритет винаходу — з розділенням етнічності/громадянства/інституції та зі станом доказовости. Що не доводиться — лишається відкритим із поясненням, чому.',
  whenToUse: 'Після review-batch, коли редактори підняли суперечності, яких самі не розвʼязали.',
  phases: [
    { title: 'Розсуд', detail: 'по агенту на теку; пошук → доказ → правка' },
    { title: 'Звід', detail: 'зібрати вироки й невирішене' },
  ],
}

/* args = { dirs: ["reference/…", …], effort? }
   Самі питання лежать на диску — scripts/_finish/_escalations.json — і кожен агент
   читає ЛИШЕ свій запис. Так args лишаються дрібними (34 КБ тексту не гнати через них). */
const A = (typeof args === 'string' ? JSON.parse(args) : args) || {}
const GROUPS = (Array.isArray(A.dirs) ? A.dirs.filter(Boolean) : []).map((d) => ({ dir: d }))
const EFFORT = A.effort || 'high'
if (!GROUPS.length) throw new Error('args.dirs обовʼязковий')

const ROOT = 'E:\\develop\\courses'

const PROMPT = (g) => `Ти АРБІТР у репозиторії книг ${ROOT}. Проза — українська. Працюй мовчки.
Твоя тека — і ТІЛЬКИ вона: ${ROOT}\\${g.dir.split('/').join('\\')}

Редактор уже вичистив тут механіку, але лишив питання, яких сам не розвʼязав.
Твоє завдання: ДОВЕСТИ відповідь джерелом і ВИПРАВИТИ статтю. Не «обрати правдоподібніше» — довести.

═══ ПИТАННЯ ═══
ПЕРШОЮ ДІЄЮ прочитай ${ROOT}\\scripts\\_finish\\_escalations.json — це масив
[{dir, items:[{what, a, b, checked}]}]. Знайди запис, де dir === "${g.dir}", і працюй
ЛИШЕ над його items. Записи інших тек тебе не стосуються — не читай і не чіпай їх.

═══ ЯК ДОВОДИТИ ═══
Черговість джерел: (1) вихідний код і Documentation/ ядра Linux · (2) man-сторінки, POSIX,
офіційні специфікації (NVMe, SCSI SPC, USB, PCI, DTS-біндинги) · (3) офіційна документація
проєкту · (4) вебпошук. Використовуй WebSearch/WebFetch — інтернет тобі доступний.
У правці лишай слід доказу: назву файлу ядра, номер розділу специфікації або посилання.

ЯКЩО ПИТАННЯ ПРО ЛЮДЕЙ, ДАТИ АБО ПРІОРИТЕТ ВИНАХОДУ:
• розділяй етнічність, громадянство, місце народження, мову, установу, державну приналежність;
• винахід майже завжди колективний — розрізняй «мав ідею» / «опублікував теорію» /
  «побудував робочий зразок» / «зробив придатну систему» / «запатентував і продав»;
• не приймай пріоритетну заяву на слово, шукай зустрічні свідчення;
• пиши СТАН ДОКАЗОВОСТИ: усталений факт · оспорювана атрибуція · правдоподібне, але недоведене · міф;
• не тягни на себе героїчних національних наративів у жоден бік.

ЯКЩО ПИТАННЯ ПРО ВЕРСІЮ ЯДРА: назви версію, у якій це так («у ядрах до 6.10 …, з 6.10 …»),
а не пиши безумовне твердження.

ЯКЩО ПИТАННЯ ПРО ОБСЯГ, ДУБЛЮВАННЯ ТЕМ або ФОРМУ БЛОКУ ПЕРЕДУМОВ:
це не твоя справа — познач у verdicts як "поза межами: <причина>" і НЕ чіпай. Виняток: якщо
блок передумов оформлено не тегом <preknowlist> — це механіка, приведи до §6 (див. AUTHORING.md).

ЯКЩО ВСТАВКИ ТЕМИ НЕ ЗГАДАНІ В ПРОЗІ — це дефект, і його треба виправити: постав ref-вставки
book:unix-linux/<тема>/<файл>.md у природних місцях тексту, кожну з коротким конспектом (§6).

═══ ЩО МОЖНА Й ЧОГО НЕ МОЖНА ═══
• Правити прозу, приклади коду, підписи фігур, сам SVG і figs.py — МОЖНА.
• Переписувати статтю цілком, дописувати нові розділи, міняти обсяг — НЕ МОЖНА.
• Чіпати manifest.js, чужі теки, git commit/add — НЕ МОЖНА.
• Якщо доказу не знайшов — НЕ ВГАДУЙ. Лиши як є, познач unresolved і напиши, чого бракує.

═══ ПЕРЕВІРКА ═══
node ${ROOT}\\scripts\\textcheck.js <тека>            → класи 1,2,3,7 = 0
python ${ROOT}\\scripts\\svgcheck.py <тека> --links   → «із зауваженнями: 0», усі файли на місці

Поверни СТРОГО цей JSON.`

const RET = {
  type: 'object', additionalProperties: false, required: ['dir', 'verdicts'],
  properties: {
    dir: { type: 'string' },
    verdicts: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['question', 'answer', 'source', 'fixed'],
        properties: {
          question: { type: 'string' },
          answer: { type: 'string' },
          source: { type: 'string' },
          fixed: { type: 'boolean' },
          status: { type: 'string' },
        },
      },
    },
    unresolved: { type: 'array', items: { type: 'string' } },
    gates: { type: 'string' },
  },
}

phase('Розсуд')
log(`тек на розсуд: ${GROUPS.length} (питання агенти беруть із scripts/_finish/_escalations.json)`)

const res = await parallel(GROUPS.map((g) => () =>
  agent(PROMPT(g), { label: `арб:${g.dir.split('/').pop()}`, phase: 'Розсуд', schema: RET, effort: EFFORT })))

phase('Звід')
const ok = res.filter(Boolean)
const all = ok.flatMap((r) => (r.verdicts || []).map((v) => ({ ...v, dir: r.dir })))

log(`вироків: ${all.length} · виправлено: ${all.filter((v) => v.fixed).length} · невирішених: ${ok.reduce((s, r) => s + (r.unresolved || []).length, 0)}`)

return {
  groups: GROUPS.length,
  done: ok.length,
  failed: GROUPS.length - ok.length,
  verdicts: all,
  fixedCount: all.filter((v) => v.fixed).length,
  outOfScope: all.filter((v) => /поза межами/i.test(v.status || '')).length,
  unresolved: ok.flatMap((r) => (r.unresolved || []).map((u) => `${r.dir}: ${u}`)),
}
