export const meta = {
  name: 'place-batch',
  description: 'Розкладка тем у нове дерево root/: 7 агентів (3 обізнані + 4 сліпі), кворум 4, посегментно',
  whenToUse: 'Перед переносом книги: вирішити вид/книгу/групу/розділ для кожної теми',
  phases: [
    { title: 'Розкладка', detail: '7 суджень на шматок: 3 бачать таблицю призначень, 4 ні' },
    { title: 'Тайбрейк', detail: 'лише там, де кворуму 4 не набралось' },
  ],
}

/* args: { chunks: ["scripts/migrate/chunks/book-electronics-1.json", ...] } */
const CHUNKS = (args && args.chunks) || []
if (!CHUNKS.length) throw new Error('args.chunks порожній — передай перелік файлів-шматків')

const RULES = `
ПРАВИЛА РОЗКЛАДКИ (обовʼязкові):

1) ВИД — рівно один із пʼяти:
   sci    — знання про те, ЩО Є: закон, явище, доведена теорема. Плюс прилади, що існують заради знання (еталон, шунт, колайдер).
   eng    — зроблене, щоб людина цим користувалась для СВОЇХ потреб: спосіб, домовленість, конструкція, структура даних, протокол.
   hw     — конкретна річ, яку можна купити: плата, модуль, давач, прилад.
   sys    — рукотворна система, до якої доречне питання «а в якій версії?»: ОС, мова та її стандарт, інструмент, формат.
   course — послідовна доріжка, де крок спирається на пройдене.
   Вирішує ПРИЗНАЧЕННЯ, не походження. Амперметр як принцип вимірювання → sci. Амперметр як товар → hw.
   Доповняльний код виглядає математикою, але це людська домовленість, яку могли укласти інакше → eng.

2) КНИГА (сегмент 2) — слуг латиницею, kebab-case, без цифр. Для sci це галузь науки (physics, math, chemistry),
   для eng — напрямок (electronics, programming, algorithms, communications), для hw — клас (sensors, boards, power),
   для sys — сама система (unix-linux, cpp-standards), для course — курс.

3) ГРУПА (сегмент 3) і РОЗДІЛ (сегмент 4) — слуги латиницею. Розділ необовʼязковий: якщо тема лежить
   прямо в групі, постав рівно ".". Група має бути живою (орієнтир 20–80 тем), розділ дрібніший (5–15).

4) Нову книгу/групу/розділ створювати МОЖНА й ТРЕБА, коли наявне не пасує. Але не плоди синонімів:
   якщо бачиш у таблиці призначень schoже за змістом — бери його, а не вигадуй сусіднє слово.
`
const SCHEMA = {
  type: 'object',
  required: ['placements'],
  properties: {
    placements: {
      type: 'array',
      items: {
        type: 'object',
        required: ['slug', 'kind', 'book', 'group', 'chapter'],
        properties: {
          slug:    { type: 'string' },
          kind:    { type: 'string', enum: ['sci', 'eng', 'hw', 'sys', 'course'] },
          book:    { type: 'string' },
          group:   { type: 'string' },
          chapter: { type: 'string' },
          bookTitle:    { type: 'string' },
          groupTitle:   { type: 'string' },
          chapterTitle: { type: 'string' },
          why:     { type: 'string' },
        },
      },
    },
  },
}

function prompt(file, informed, extra) {
  const head = informed
    ? `ПЕРШОЮ дією прочитай scripts/migrate/destinations.json — це перелік уже створених призначень у дереві root/.
Де наявне призначення пасує темі — бери його. Нове створюй лише коли нічого не пасує.`
    : `Суди САМОСТІЙНО, від змісту тем. Таблицю наявних призначень НЕ читай — твоє завдання дати незалежне судження.`
  return `${head}

Прочитай ${file}. Це шматок книги: перелік тем із назвою, поточним шляхом і scope секції, де вони зараз лежать.
Поточне місце — доказ, а не вирок: воно часто помилкове, саме тому ми й перекладаємо.

Для КОЖНОЇ теми зі списку поверни: slug (як у файлі), kind, book, group, chapter,
а також українські назви для показу: bookTitle, groupTitle, chapterTitle (для chapter="." лиши chapterTitle порожнім),
і why — одне речення, чому саме туди.
Пропускати теми не можна — скільки на вході, стільки й на виході.
${RULES}${informed ? (extra || '') : ''}`
}

/* злічування посегментно: кворум 4 із 7 на кожен сегмент окремо */
function tally(votes, slug) {
  /* кворум — строга більшість ЖИВИХ голосів, а не абсолютна 4:
     інакше при 4 живих протокол мовчки стає одностайністю */
  const need = Math.floor(votes.length / 2) + 1
  const out = { slug, need, alive: votes.length }
  const segs = ['kind', 'book', 'group', 'chapter']
  for (const s of segs) {
    const box = {}
    for (const v of votes) {
      const p = (v.placements || []).find(x => x.slug === slug)
      if (!p || !p[s]) continue
      let key = String(p[s]).trim().toLowerCase()
      if (s === 'chapter' && key === '') key = '.'          // порожній розділ = лежить у корені групи
      box[key] = (box[key] || 0) + 1
    }
    let best = null, n = 0
    for (const k of Object.keys(box)) if (box[k] > n) { best = k; n = box[k] }
    out[s] = n >= need ? best : null
    out[s + 'Votes'] = n
    out[s + 'Spread'] = Object.keys(box).length
  }
  // назви для показу: найчастіша серед тих, хто дав той самий слуг
  for (const pair of [['book', 'bookTitle'], ['group', 'groupTitle'], ['chapter', 'chapterTitle']]) {
    const seg = pair[0], tk = pair[1], box = {}
    for (const v of votes) {
      const p = (v.placements || []).find(x => x.slug === slug)
      if (!p || !p[tk]) continue
      if (out[seg] && String(p[seg] || '').trim().toLowerCase() !== out[seg]) continue
      box[p[tk]] = (box[p[tk]] || 0) + 1
    }
    let best = '', n = 0
    for (const k of Object.keys(box)) if (box[k] > n) { best = k; n = box[k] }
    out[tk] = best
  }
  return out
}
const results = []
/* Жива таблиця РІШЕНЬ цього прогону: destinations.json знімається один раз до батчу,
   тож без цього шматки 2..N судять, не знаючи нічого з шматка 1. */
const decided = {}
function remember(p) {
  if (!p.kind || !p.book || !p.group) return
  const k = (decided[p.kind] = decided[p.kind] || {})
  const b = (k[p.book] = k[p.book] || {})
  const g = (b[p.group] = b[p.group] || { title: p.groupTitle || p.group, chapters: {} })
  if (p.chapter && p.chapter !== '.') g.chapters[p.chapter] = p.chapterTitle || p.chapter
}
function decidedText() {
  const kinds = Object.keys(decided)
  if (!kinds.length) return ''
  const L = ['', 'УЖЕ ВИРІШЕНО В ЦЬОМУ ПРОГОНІ (бери звідси, якщо пасує; не вигадуй синонімів):']
  for (const k of kinds) for (const b of Object.keys(decided[k])) {
    L.push('  ' + k + '/' + b)
    for (const g of Object.keys(decided[k][b])) {
      const ch = Object.keys(decided[k][b][g].chapters)
      L.push('     ' + g + (ch.length ? '  розділи: ' + ch.join(', ') : ''))
    }
  }
  return L.join(String.fromCharCode(10))
}

for (const file of CHUNKS) {
  phase('Розкладка')
  log(`шматок ${file}`)

  const thunks = []
  for (let i = 0; i < 3; i++) thunks.push(() =>
    agent(prompt(file, true, decidedText()), { label: `obiznanyi-${i + 1}`, phase: 'Розкладка', schema: SCHEMA, effort: 'medium' }))
  for (let i = 0; i < 4; i++) thunks.push(() =>
    agent(prompt(file, false, ''), { label: `slipyi-${i + 1}`, phase: 'Розкладка', schema: SCHEMA, effort: 'medium' }))

  const votes = (await parallel(thunks)).filter(Boolean)
  if (votes.length < 4) { log(`✖ ${file}: живих суджень ${votes.length} із 7 — кворум неможливий, шматок пропущено`); continue }

  const slugs = []
  for (const v of votes) for (const p of v.placements || []) if (slugs.indexOf(p.slug) < 0) slugs.push(p.slug)

  const tallied = slugs.map(s => tally(votes, s))
  /* Посегментний кворум може зібрати адресу, якої не пропонував ЖОДЕН агент
     (голоси eng/physics x3, sci/physics x1, sci/optics x3 -> "кворум" sci/physics від одного).
     Така адреса не рішення, а артефакт лічби — женемо її на тайбрейк. */
  for (const t of tallied) {
    if (!t.kind || !t.book || !t.group || !t.chapter) continue
    const proposed = votes.some(v => (v.placements || []).some(p => p.slug === t.slug &&
      String(p.kind || '').trim().toLowerCase() === t.kind &&
      String(p.book || '').trim().toLowerCase() === t.book &&
      String(p.group || '').trim().toLowerCase() === t.group &&
      (String(p.chapter || '.').trim().toLowerCase() || '.') === t.chapter))
    if (!proposed) { t.synthetic = true; t.chapter = null }
  }
  const unresolved = tallied.filter(t => !t.kind || !t.book || !t.group || !t.chapter)
  log(`${file}: тем ${tallied.length}, з кворумом ${tallied.length - unresolved.length}, на тайбрейк ${unresolved.length}`)

  if (unresolved.length) {
    phase('Тайбрейк')
    const fixed = await parallel(unresolved.map(t => () => {
      const opts = votes.map(v => (v.placements || []).find(x => x.slug === t.slug)).filter(Boolean)
        .map(p => `${p.kind}/${p.book}/${p.group}/${p.chapter}  — ${p.why || ''}`)
      return agent(
`Сім суджень розійшлися щодо теми «${t.slug}» із ${file}.
Прочитай scripts/migrate/destinations.json і сам файл шматка, знайди цю тему, і обери ОДНЕ місце.
Ось що запропонували:
${opts.join('\n')}

Уже узгоджене (не міняй, якщо стоїть): kind=${t.kind || '?'} book=${t.book || '?'} group=${t.group || '?'} chapter=${t.chapter || '?'}
Поверни рівно один запис для цієї теми.
${RULES}`,
        { label: `taybreik:${t.slug}`, phase: 'Тайбрейк', schema: SCHEMA, effort: 'high' })
        .then(r => { const p = (r && r.placements || [])[0]; return p ? Object.assign({}, t, p, { tiebreak: true }) : t })
    }))
    fixed.filter(Boolean).forEach(f => { const i = tallied.findIndex(x => x.slug === f.slug); if (i >= 0) tallied[i] = f })
  }

  tallied.forEach(remember)
  results.push({ file, placements: tallied })
}

const total = results.reduce((n, r) => n + r.placements.length, 0)
log(`готово: шматків ${results.length}, тем розкладено ${total}`)
return { results }
