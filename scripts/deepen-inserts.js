export const meta = {
  name: 'deepen-inserts',
  description: 'Поглибити теми/вставки зі статусом deeper до Feynman-deep: ЧОМУ від першопричини, числовий приклад. Черга — з per-module manifest.js усіх книг (або однієї).',
  phases: [
    { title: 'Черга', detail: 'Пройти кореневі індекси книг → per-module manifest.js → зібрати записи зі статусом deeper' },
    { title: 'Поглиблення', detail: 'Opus читає файл, переписує Feynman-deep, пише назад' },
    { title: 'Статуси', detail: 'Перевести оброблені записи у done у відповідних manifest.js' },
  ],
}

/*
  args (необов'язково):
    {}                → усі 4 книги
    { book: "math" }  → лише одна книга (embedded|chem|math|components)
    { only: "slug" }  → лише записи, чий цільовий slug == only (по всіх книгах)
    { limit: N }      → обробити лише перші N записів черги
    число             → те саме, що { limit: N }
*/

const ROOT = 'E:/develop/courses'

/* Кореневі індекси книг. */
const BOOKS = {
  embedded:   { index: `${ROOT}/manifest.js`,      base: 'embedded/' },
  chem:       { index: `${ROOT}/manifest-chem.js`, base: 'chemistry/' },
  math:       { index: `${ROOT}/manifest-math.js`, base: 'math/' },
  components: { index: `${ROOT}/manifest-comp.js`, base: 'components/' },
}

let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) {} }
const LIMIT = typeof _a === 'number' ? _a : (_a && _a.limit ? Number(_a.limit) : 0)
const ONLY  = _a && _a.only ? String(_a.only) : ''
const BOOK  = _a && _a.book ? String(_a.book) : ''
if (BOOK && !BOOKS[BOOK]) throw new Error(`book має бути embedded|chem|math|components, а не "${BOOK}"`)
const bookKeys = BOOK ? [BOOK] : Object.keys(BOOKS)

const RETRY_WAIT = (_a && _a.retryWaitMs != null) ? Number(_a.retryWaitMs) : 60000
const MAX_TRIES  = (_a && _a.maxTries != null) ? Number(_a.maxTries) : 30
const SLEEP = (ms) => new Promise(res => { try { setTimeout(res, ms) } catch (e) { res() } })
async function callAgent(prompt, opts) {
  const tag = (opts && opts.label) || 'agent'
  for (let attempt = 1; ; attempt++) {
    let r = null
    try { r = await agent(prompt, opts) } catch (e) { r = null }
    if (r != null) { if (attempt > 1) log(`✅ ${tag}: відповів зі спроби ${attempt}`); return r }
    if (attempt >= MAX_TRIES) { log(`⛔ ${tag}: немає відповіді після ${MAX_TRIES} спроб — пропускаю`); return null }
    log(`⏳ ${tag}: сервер не відповів (${attempt}/${MAX_TRIES}) — повтор через ${Math.round(RETRY_WAIT / 1000)} с`)
    await SLEEP(RETRY_WAIT)
  }
}

/* Прочитати файл як текст. */
function readText(absPath, label) {
  return callAgent(
    `Read the file "${absPath}" and return its full content verbatim in field "content". If it does not exist, return content as empty string.`,
    { label, phase:'Черга', model:'sonnet',
      schema:{ type:'object', additionalProperties:false, required:['content'], properties:{ content:{type:'string'} } } }
  )
}
/* Виконати manifest у пісочниці (як bookbuild.js) — дістати реальні обʼєкти. */
function evalSandbox(src) {
  const win = { __MODREG__: [] }
  try { new Function('window', src)(win) } catch (e) { throw new Error('manifest не виконується: ' + e.message) }
  return win
}

/* Резолв цілі вставки/теми у абсолютний шлях файлу.
   - kind-вставка з локальним file «comp-x.md» → <base><chapterDir>/<file>
   - крос-шлях «../../../components/.../x.md» → нормалізуємо відносно <base><chapterDir>
   - тема (без file) → <base><chapterDir>/<main> (поглиблюємо головний файл розділу) */
function normalize(p) {
  const parts = p.split('/'); const out = []
  for (const seg of parts) {
    if (seg === '' || seg === '.') continue
    if (seg === '..') out.pop(); else out.push(seg)
  }
  return out.join('/')
}
function resolveTarget(base, chapterDir, file) {
  const baseDir = `${base}${chapterDir}`.replace(/\/$/, '')
  return `${ROOT}/${normalize(`${baseDir}/${file}`)}`
}

/* ── Фаза: зібрати чергу deeper з усіх потрібних книг ── */
phase('Черга')

const queue = []   // { book, base, manifestPath, modSlug, key, keyKind, slug, filePath }
for (const bk of bookKeys) {
  const B = BOOKS[bk]
  const idxRead = await readText(B.index, `idx:${bk}`)
  if (!idxRead || !idxRead.content) { log(`⚠️ індекс ${bk} недоступний — пропускаю книгу`); continue }
  let idxWin
  try { idxWin = evalSandbox(idxRead.content) } catch (e) { log(`⚠️ ${bk}: ${e.message}`); continue }
  const mods = idxWin.BOOK_MODULES || []
  const base = (idxWin.BOOK_META && idxWin.BOOK_META.basePath) || B.base

  for (const entry of mods) {
    let mod = null, manifestPath = null, modSlug = null
    if (typeof entry === 'string') {
      const slug = entry.replace(/\/manifest\.js$/, '').replace(/\/$/, '')
      manifestPath = `${ROOT}/${base}${entry}`
      const pm = await readText(manifestPath, `pm:${bk}/${slug}`)
      if (!pm || !pm.content) continue
      try { mod = (evalSandbox(pm.content).__MODREG__ || [])[0] } catch (e) { continue }
      modSlug = (mod && mod.slug) || slug
    } else {
      mod = entry; modSlug = entry.slug
      manifestPath = `${ROOT}/${base}${entry.slug}/manifest.js`   // inline-модуль ще не винесений; deeper там неможливий (нема topics), просто пропустимо
    }
    if (!mod || !mod.chapters) continue

    for (const ch of mod.chapters) {
      const chapterDir = ch.dir || `${modSlug}/${ch.slug || ''}`
      const main = ch.main || ''
      for (const t of (ch.topics || [])) {
        if (!t || t.status !== 'deeper') continue
        // тема (без kind/file) → головний файл розділу; вставка → її file
        const file = t.file || main
        if (!file) continue
        const filePath = resolveTarget(base, chapterDir, file)
        const slug = (t.file || main).split('/').at(-1).replace(/\.md$/, '')
        queue.push({
          book: bk, base, manifestPath, modSlug,
          key: t.file ? t.file : (t.mrt || ''),        // ключ для статусу: file для вставки, mrt для теми
          keyKind: t.file ? 'file' : 'mrt',
          slug, filePath, title: t.title || '',
        })
      }
    }
  }
}

let work = queue
if (ONLY) {
  work = work.filter(it => it.slug === ONLY)
  log(`Режим only="${ONLY}": знайдено ${work.length} записів`)
} else if (LIMIT) {
  work = work.slice(0, LIMIT)
  log(`Обробляємо ${work.length} з ${queue.length} записів (limit=${LIMIT})`)
} else {
  log(`Книги: ${bookKeys.join(', ')}. Записів зі статусом deeper: ${work.length}`)
}
if (!work.length) { log('Черга порожня — немає записів зі статусом deeper'); return { done: 0, note: 'нема deeper' } }

/* ── Канон для поглиблення (тип «нормальна учбова книга»: embedded/math/components) ── */
const CANON = `КАНОН поглиблення для книг типу «нормальна учбова книга» (${ROOT}/AUTHORING.md §§1–3,5):

═══ СТАТУС: ЦЕ ПОВНОЦІННА ТЕМА/ВСТАВКА КУРСУ ═══
Файл живе у textbook-книзі (embedded / math / components).
Глибина — Фейнман-deep (повний textbook), НЕ скорочений конспект.

ОБСЯГ (§2):
• Вимірюємо ПРОЗУ — без код-блоків, таблиць і підписів «*Рис.*».
• Тема: мінімум 1800–2500 · звичайна 2500–4500 · важка до ~9000. Вставка 🔌 — 300–800; 🧮/⚙️ — 300–1000.
• Де саме — визначає складність ТЕМИ, не бажання скоротити. Складна фізика → ближче до верхньої межі.
• Не стискати. Повнота понад стислість; токенів не шкодувати. Приріст обсягу йде на ПЛАВНІСТЬ, а не на щільніші тези.

СТИЛЬ ФЕЙНМАНА (§1):
• Спершу інтуїція й «ЧОМУ», потім деталі. Аналогії точні — і показуй, де аналогія ламається.
• Мотивація: чому питання виникло, яку проблему розв'язуємо — перед кожним ключовим поняттям.
• НЕ «Шотткі має ~0.4 В», а «Шотткі має ~0.4 В, бо метал-напівпровідник не накопичує дірковий заряд,
  тому нема дифузійного потенціалу PN-переходу — лише контактна різниця у ~0.3–0.4 В».
• Причинно-наслідкові ланцюжки: A → тому B → звідси C. Не списки тверджень.
• Граничні випадки та типові пастки — завжди з механізмом, не просто «обережно».

ПЛАВНІСТЬ (§1 — виконувати ОДРАЗУ, не окремим проходом):
• Кожен підрозділ і абзац — міст від попереднього: зв'язка «ми з'ясували X — тепер постає Y».
• Наскрізний ланцюжок: навіщо → інтуїція → деталі → приклад.
• Перед завершенням файлу — перечитай суцільно й згладь різкі стики.

ПРАКТИЧНІСТЬ (§1):
• Біля кожного важливого поняття — рамка «> 🔧 **Навіщо це.**»: для чого це в реальній embedded-розробці.
• Застосування реальні, але лише в межах вже введеного матеріалу курсу.

МАТЕМАТИКА (§1):
• БЕЗ LaTeX. У тексті — Unicode: 10⁻⁹, ε, ≈, ×, ·, ², ₀, Δ, α, σ, μ, ω.
• Покрокові обчислення і ключові формули — у фенсованих код-блоках із вирівнюванням по «=».
• Десятковий роздільник — крапка (3.3), як у даташитах. Якщо формула є — вона використовується в розрахунку.

ДВОМОВНІ ТЕРМІНИ (§3):
• Ключові терміни при першому введенні: «провідність (conductivity, σ)» — щоб читач упізнав слово в даташиті.

WORKED EXAMPLE (§1):
• Мінімум ОДИН числовий worked-приклад: реальний сценарій з курсу embedded, конкретні числа.
• Оформлення: **жирний заголовок-умова** → код-блок із покроковим обчисленням → висновок. Код — C/C++ (ESP32), не псевдокод.

ГОЛОС (§3):
• Загально й абстрактно — не прив'язуватися до конкретних плат, не називати part numbers. ESP32 і ArduPilot можна.
• Виняток для 🔌-вставок/components (§3): канонічні сімейства називати можна — «TP4056-клас», «L298-клас» — без прив'язки до ревізій плат.
• Жодних розділів-зведень і тем-переказів: кожна секція — нова змістовна думка.

ЗАБОРОНЕНО:
• Прибирати наявний вміст — лише РОЗШИРЮЙ і ПОГЛИБЛЮЙ.
• Змінювати H1-заголовок, emoji або blockquote-посилання на курс.
• Константація без пояснення — завжди «…, бо…».
• Генерувати нові SVG/figs.py — фігури не чіпаємо.

МОВА:
• Українська, жива і точна. Без кальок, русизмів, канцеляриту. Один термін на поняття в межах файлу.`

/* ── Фаза поглиблення ── */
phase('Поглиблення')

const results = await pipeline(
  work,

  // Стадія 1: читаємо поточний файл
  async (item) => {
    const read = await callAgent(
      `Read the file "${item.filePath}" and return its full markdown content verbatim in "content" and approximate prose word count (excluding code blocks) in "wordCount". If the file does not exist, content="" and wordCount=0.`,
      { label: `read:${item.slug}`, phase: 'Поглиблення', model:'sonnet',
        schema:{ type:'object', additionalProperties:false, required:['content','wordCount'],
          properties:{ content:{type:'string'}, wordCount:{type:'number'} } } }
    )
    if (!read) return null
    if (!read.content || !read.content.trim()) { log(`⚠️ ${item.book}:${item.slug} — файл порожній/відсутній (${item.filePath}); пропускаю`); return null }
    return { ...item, currentContent: read.content, currentWordCount: read.wordCount }
  },

  // Стадія 2: поглиблюємо (Opus) + пишемо назад
  async (item, originalItem) => {
    if (!item) return null
    const r = await callAgent(
      `${CANON}

ФАЙЛ ДЛЯ ПОГЛИБЛЕННЯ: "${originalItem.filePath}"
ПОТОЧНИЙ ВМІСТ (≈${item.currentWordCount} слів):

${item.currentContent}

ЗАВДАННЯ:
Поглиб цей файл до Фейнман-deep: кожну пропущену «ЧОМУ» — додай від першопричини; де бракує числового worked-прикладу — додай реальний сценарій із конкретними числами; де є константація без причини — доточи механізм; згладь плавність переходів.
Збережи всі існуючі секції, H1-заголовок, emoji, blockquote-посилання на курс. НЕ прибирай наявний вміст — лише розширюй і поглиблюй. Фігури/SVG не чіпай.

Після завершення — запиши результат у файл "${originalItem.filePath}" через інструмент Write. Пиши одразу фінальну якість: окремої вичитки не буде. Поверни ok=true.`,
      { label: `deepen:${originalItem.slug}`, phase: 'Поглиблення', model:'opus',
        schema:{ type:'object', additionalProperties:false, required:['ok'], properties:{ ok:{type:'boolean'}, note:{type:'string'} } } }
    )
    if (!r || !r.ok) { log(`❌ ${originalItem.book}:${originalItem.slug} — поглиблення не вдалося`); return null }
    log(`✅ ${originalItem.book}:${originalItem.slug}`)
    return { ...originalItem, done: true }
  }
)

/* ── Фаза: статуси deeper → done у відповідних per-module manifest.js ──
   Групуємо готові записи за manifestPath, у кожному файлі точково замінюємо
   status:"deeper" → status:"done" у тому самому обʼєкті запису (ключ: file для
   вставки, mrt для теми; враховуємо обидва порядки status↔file). ── */
phase('Статуси')

const done = results.filter(Boolean).filter(r => r.done)
const failed = work.length - done.length

const byManifest = new Map()
for (const r of done) {
  if (!byManifest.has(r.manifestPath)) byManifest.set(r.manifestPath, [])
  byManifest.get(r.manifestPath).push(r)
}

let statusChanged = 0
const esc = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
for (const [manifestPath, items] of byManifest) {
  const pm = await readText(manifestPath, `read-manifest:${manifestPath.split('/').at(-2)}`)
  if (!pm || !pm.content) { log(`⚠️ не зміг прочитати ${manifestPath} — статуси цього модуля не оновлено`); continue }
  let src = pm.content
  const before = src
  for (const it of items) {
    if (it.keyKind === 'file') {
      const f = it.key
      const a = new RegExp('(file:\\s*"' + esc(f) + '"[\\s\\S]{0,200}?status:\\s*")deeper', 'g')
      let n = 0; src = src.replace(a, (m, pre) => { n++; return pre + 'done' })
      if (!n) {
        const b = new RegExp('(status:\\s*")deeper("[\\s\\S]{0,200}?file:\\s*"' + esc(f) + '")', 'g')
        src = src.replace(b, (m, p1, p3) => { n++; return p1 + 'done' + p3 })
      }
      statusChanged += n
    } else {
      const mrt = it.key
      const re = new RegExp('(mrt:\\s*"' + esc(mrt) + '"[\\s\\S]{0,160}?status:\\s*")deeper', 'g')
      let n = 0; src = src.replace(re, (m, pre) => { n++; return pre + 'done' })
      statusChanged += n
    }
  }
  if (src !== before) {
    await callAgent(
      `Write the following EXACT content to the file "${manifestPath}" (overwrite). Return ok=true.\n\n<<<FILE>>>\n${src}\n<<<END>>>`,
      { label:`write-manifest:${manifestPath.split('/').at(-2)}`, phase:'Статуси', model:'sonnet',
        schema:{ type:'object', additionalProperties:false, required:['ok'], properties:{ ok:{type:'boolean'} } } }
    )
  } else {
    log(`⚠️ у ${manifestPath} жоден ключ не збігся — статуси не змінено (перевір вручну)`)
  }
}

log(`\n═══ ПІДСУМОК ═══`)
log(`✅ Поглиблено: ${done.length}; статусів deeper→done: ${statusChanged}`)
log(`❌ Пропущено/помилка: ${failed}`)
if (done.length) log(`Файли: ${done.map(r => `${r.book}:${r.slug}`).join(', ')}`)

return {
  done: done.length,
  failed,
  statusChanged,
  files: done.map(r => ({ book: r.book, slug: r.slug, path: r.filePath })),
}
