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
// Повні правила з AUTHORING.md §§5–8,11,16,19 — застосовуємо як до теми, не як до вставки.
const CANON = `КАНОН поглиблення для довідникових книг math/ і components/ (AUTHORING.md §§5–8,11,16,19):

═══ СТАТУС: ЦЕ ТЕМА КНИГИ-ДОВІДНИКА, А НЕ ВСТАВКА ═══
Файл живе у standalone-книзі (math/ або components/).
Правила — як для повноцінної теми курсу, НЕ як для 🔌/🧮-вставки (300-800 сл).

ОБСЯГ (§2/§19):
• Вимірюємо ПРОЗУ — без код-блоків, таблиць і підписів «*Рис.*».
• Діапазон: мінімум 1800–2500 · звичайна 2500–4500 · важка до ~9000.
• Де саме — визначає складність ТЕМИ, не бажання скоротити.
  Проста довідкова стаття (e-series, packages) → ближче до мінімуму.
  Складна фізика (gate-driver, fuel-gauge, wall-adapter) → 3000–5000+.
• Не стискати. Повнота понад стислість; токенів не шкодувати.

СТИЛЬ ФЕЙНМАНА (§5):
• Спершу інтуїція й «ЧОМУ», потім деталі. Аналогії точні — і показуй, де аналогія ламається.
• Мотивація: чому питання виникло, яку проблему розв'язуємо — перед кожним ключовим поняттям.
• НЕ «Шотткі має ~0.4 В», а «Шотткі має ~0.4 В, бо метал-напівпровідник не накопичує дірковий заряд,
  тому нема дифузійного потенціалу PN-переходу — лише контактна різниця у ~0.3–0.4 В».
• Причинно-наслідкові ланцюжки: A → тому B → звідси C. Не списки тверджень.
• Граничні випадки та типові пастки — завжди з механізмом, не просто «обережно».

ПЛАВНІСТЬ (§5/§17 — виконувати ОДРАЗУ, не окремим проходом):
• Кожен підрозділ і абзац — міст від попереднього: зв'язка «ми з'ясували X — тепер постає Y».
• Наскрізний ланцюжок: навіщо → інтуїція → деталі → приклад.
• Перед завершенням файлу — перечитай суцільно й згладь різкі стики.

ПРАКТИЧНІСТЬ (§6):
• Біля кожного важливого поняття — рамка «> 🔧 **Навіщо це.**»: для чого це в реальній embedded-розробці.
• Застосування реальні, але лише в межах вже введеного матеріалу курсу.

МАТЕМАТИКА (§7):
• БЕЗ LaTeX. У тексті — Unicode: 10⁻⁹, ε, ≈, ×, ·, ², ₀, Δ, α, σ, μ, ω.
• Покрокові обчислення і ключові формули — у фенсованих код-блоках із вирівнюванням по «=».
• Десятковий роздільник — крапка (3.3), як у даташитах.
• Формул рівно стільки, скільки потрібно; якщо формула є — вона використовується в розрахунку.

ДВОМОВНІ ТЕРМІНИ (§8):
• Ключові терміни при першому введенні: «провідність (conductivity, σ)».
• Мета: читач упізнає слово в даташиті.

WORKED EXAMPLE (§11):
• Мінімум ОДИН числовий worked-приклад: реальний сценарій з курсу embedded, конкретні числа.
• Оформлення: **жирний заголовок-умова** → код-блок із покроковим обчисленням → висновок.
• Якщо є код — C/C++ (прошивка ESP32), не псевдокод.

ГОЛОС (§3/§16):
• Загально й абстрактно — не прив'язуватися до конкретних залізних плат і не називати part numbers.
• ESP32 і ArduPilot називати можна.
• Виняток для comp/-файлів (§16): канонічні сімейства називати можна — «TP4056-клас», «DW01+8205-клас», «L298-клас» — але без прив'язки до конкретних ревізій плат.
• Жодних розділів-зведень і тем-переказів (§5): кожна секція — нова змістовна думка, не резюме сказаного.

ЗАБОРОНЕНО:
• Прибирати наявний вміст — лише РОЗШИРЮЙ і ПОГЛИБЛЮЙ.
• Змінювати H1-заголовок, emoji або blockquote-посилання на embedded-курс.
• Додавати нові H2-секції поза існуючою структурою файлу.
• Константація без пояснення — завжди «…, бо…».
• Генерувати нові SVG/figs.py — фігури не чіпаємо.

МОВА:
• Українська, жива і точна. Без кальок, русизмів, канцеляриту.
• Один термін на поняття в межах файлу.`

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
