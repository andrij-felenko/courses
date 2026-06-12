export const meta = {
  name: 'deepen-inserts',
  description: 'Поглибити math/ і comp/ вставки до Feynman-deep: 800+ слів, ЧОМУ від першопричини, числовий приклад. Читає чергу ⬜ з DEEPENING.md.',
  phases: [
    { title: 'Черга', detail: 'Парсить DEEPENING.md — відбирає ⬜ файли з issues' },
    { title: 'Поглиблення', detail: 'Opus читає файл, переписує Feynman-deep, пише назад' },
    { title: 'Звіт', detail: 'Оновлює статуси в DEEPENING.md' },
  ],
}

/*
  args (необов'язково):
    число          → обробити N файлів з початку черги
    { limit: N }   → те саме
    { only: "slug" } → лише один конкретний slug
*/

const ROOT = 'E:/develop/courses'
const DEEPENING_PATH = `${ROOT}/DEEPENING.md`

// ─── Парсинг DEEPENING.md ────────────────────────────────────────────────────
// Формат рядків таблиці: | ⬜ | `comp/passive/peltier` | issues text |
// або:                   | ⬜ | `math/discrete-logic/superposition` | issues text |

phase('Черга')

const queueData = await agent(
  `Read the file "${DEEPENING_PATH}".

Find all table rows where the first cell contains "⬜" (the white square emoji).
Each such row has 3 cells: status | path | issues.
The path cell contains a backtick-quoted slug like \`comp/passive/peltier\` or \`math/number-systems/e-series\`.
The issues cell has a semicolon-separated description of what needs improving.

Return a JSON object with field "items" — array of objects, each with:
  - "path": the slug string (without backticks), e.g. "comp/passive/peltier"
  - "issues": the full issues text from that row

Include ALL rows with ⬜ status. Preserve the exact path slug.`,
  {
    label: 'parse-deepening-md',
    phase: 'Черга',
    schema: {
      type: 'object',
      required: ['items'],
      properties: {
        items: {
          type: 'array',
          items: {
            type: 'object',
            required: ['path', 'issues'],
            properties: {
              path: { type: 'string' },
              issues: { type: 'string' },
            },
          },
        },
      },
    },
  }
)

if (!queueData || !queueData.items.length) {
  log('Черга порожня — всі файли поглиблені або DEEPENING.md не знайдено')
  return { done: 0 }
}

// Resolve path slug → absolute file path on disk
// comp/passive/peltier     → E:/develop/courses/components/passive/peltier/peltier.md
// math/discrete-logic/sup  → E:/develop/courses/math/discrete-logic/superposition/superposition.md
const resolve = (pathSlug) => {
  const parts = pathSlug.split('/')
  if (parts[0] === 'comp') {
    return `${ROOT}/components/${parts[1]}/${parts[2]}/${parts[2]}.md`
  }
  // math/sector/slug
  return `${ROOT}/${parts[0]}/${parts[1]}/${parts[2]}/${parts[2]}.md`
}

let queue = queueData.items.map(item => ({
  ...item,
  slug: item.path.split('/').at(-1),
  filePath: resolve(item.path),
}))

// Apply args limits
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) {} }
const LIMIT = typeof _a === 'number' ? _a : (_a && _a.limit ? Number(_a.limit) : 0)
const ONLY  = _a && _a.only ? String(_a.only) : ''

if (ONLY) {
  queue = queue.filter(it => it.slug === ONLY || it.path === ONLY)
  log(`Режим only="${ONLY}": знайдено ${queue.length} файлів`)
} else if (LIMIT) {
  queue = queue.slice(0, LIMIT)
  log(`Обробляємо ${queue.length} з ${queueData.items.length} файлів (limit=${LIMIT})`)
} else {
  log(`Файлів у черзі: ${queue.length}`)
}

if (!queue.length) return { done: 0, note: 'only/limit відфільтрував усе' }

// ─── Канон для поглиблення (math/ і components/ книги) ───────────────────────
const CANON = `КАНОН поглиблення для довідникових книг math/ і components/:

ЦІЛЬ: Feynman-deep — читач розуміє ЧОМУ, а не просто ЗНАЄ ЩО.

ОБОВ'ЯЗКОВО:
• 800–1200 слів прози (без урахування код-блоків і таблиць).
• На кожне ключове твердження — пояснення першопричини: з якої фізики/математики воно випливає.
  НЕ «Шотткі має ~0.4 В», а «Шотткі має ~0.4 В, бо метал-напівпровідник не накопичує дірковий заряд,
  тому нема дифузійного потенціалу PN-переходу».
• Мінімум ОДИН числовий worked-приклад, прив'язаний до реального сценарію з курсу embedded
  (конкретний компонент, реальні числа, покроковий розрахунок).
• Причинно-наслідкові ланцюжки: A → тому B → звідси C. Не списки тверджень.
• Граничні випадки або типова пастка — завжди пояснена механізмом, не просто «обережно».

ЗАБОРОНЕНО:
• Прибирати наявний вміст (лише РОЗШИРЮЙ і ПОГЛИБЛЮЙ).
• Змінювати заголовки секцій або emoji у заголовку.
• Додавати нові секції поза існуючою структурою.
• LaTeX. Формули — Unicode у символьних рядках або у фенсованих блоках.
• Константація без пояснення («X залежить від Y» — завжди «X залежить від Y, бо...»).

СТИЛЬ:
• Українська мова, жива і точна. Без кальок і канцеляриту.
• Двомовні терміни при першому введенні: «провідність (conductivity, σ)».
• Посилання на теми курсу — через §М.Р.Т або назву розділу в дужках.`

// ─── Фаза поглиблення ────────────────────────────────────────────────────────
phase('Поглиблення')

const results = await pipeline(
  queue,

  // Стадія 1: Читаємо поточний файл
  async (item) => {
    const read = await agent(
      `Read the file "${item.filePath}" and return its full markdown content verbatim.
If the file does not exist, return content as empty string and wordCount as 0.`,
      {
        label: `read:${item.slug}`,
        phase: 'Поглиблення',
        schema: {
          type: 'object',
          required: ['content', 'wordCount'],
          properties: {
            content: { type: 'string' },
            wordCount: { type: 'number', description: 'approximate word count excluding code blocks' },
          },
        },
      }
    )
    if (!read) return null
    return { ...item, currentContent: read.content, currentWordCount: read.wordCount }
  },

  // Стадія 2: Поглиблюємо (Opus) + пишемо назад
  async (item, originalItem) => {
    if (!item) return null

    await agent(
      `${CANON}

ФАЙЛ ДЛЯ ПОГЛИБЛЕННЯ: "${originalItem.filePath}"
ПОТОЧНИЙ ВМІСТ (≈${item.currentWordCount} слів):

${item.currentContent}

КОНКРЕТНІ ПРОБЛЕМИ ЦЬОГО ФАЙЛУ (з аудиту):
${originalItem.issues}

ЗАВДАННЯ:
Перепиши або розшир цей файл, усунувши всі перелічені проблеми.
Кожну пропущену «ЧОМУ» — додай. Числовий приклад — додай якщо відсутній.
Збережи всі існуючі секції, заголовок, emoji, blockquote-посилання.

Після завершення — запиши результат у файл "${originalItem.filePath}" за допомогою інструменту Write.
Пиши одразу фінальну якість: окремої вичитки не буде.`,
      {
        label: `deepen:${originalItem.slug}`,
        phase: 'Поглиблення',
        model: 'opus',
      }
    )

    log(`✅ ${originalItem.path}`)
    return { path: originalItem.path, slug: originalItem.slug, done: true }
  }
)

// ─── Звіт і оновлення DEEPENING.md ──────────────────────────────────────────
phase('Звіт')

const done = results.filter(Boolean).filter(r => r.done)
const failed = results.filter(r => !r || !r.done)

if (done.length) {
  // Оновити статуси ⬜ → 🟢 для завершених файлів у DEEPENING.md
  const donePaths = done.map(r => r.path)
  await agent(
    `Read the file "${DEEPENING_PATH}".
For each of these paths, find the table row that contains that path (in backticks)
and change the "⬜" status cell to "🟢".
Paths to mark done: ${JSON.stringify(donePaths)}
Write the updated file back to "${DEEPENING_PATH}".`,
    { label: 'update-deepening-md', phase: 'Звіт' }
  )
}

log(`\n═══ ПІДСУМОК ═══`)
log(`✅ Поглиблено: ${done.length}`)
log(`❌ Пропущено/помилка: ${failed.length}`)
if (done.length) log(`Файли: ${done.map(r => r.path).join(', ')}`)

return {
  done: done.length,
  failed: failed.length,
  files: done.map(r => r.path),
}
