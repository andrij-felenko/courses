export const meta = {
  name: 'recheck-audit',
  description: 'Аудит статей зі статусом recheck: привести до канону AUTHORING.md, перевірити крос-лінки, перейменувати фігури на slug-only. Контент теми не міняє.',
  phases: [
    { title: 'Audit', detail: 'один під-агент на тему (+її вставки): конформність §5/§6, фігури, лінки' },
  ],
}

/*__EMBED__*/

/* args = {
     book:    "algorithms",
     topics:  [ { section, slug, title, levels, inserts:{hist?:[{file,status}], comp?, math?, proj?} }, ... ],  // батч (<=5)
     index:   { <book>: [<slug>,...], ... },   // усі наявні topic-slug-и (валідація book:-лінків)
     titles:  { "<book>/<slug>": "<title>" },
   }
   Кожен під-агент РЕДАГУЄ файли теми напряму (стаття, вставки, git mv фігур) — вони ізольовані по темі.
   Жоден під-агент НЕ чіпає manifest.js (спільний файл). Стаби й статуси ставить головна сесія за звітами. */

const A = (typeof EMBED !== 'undefined' && EMBED) ? EMBED
        : (typeof args === 'string') ? JSON.parse(args) : (args || {})
log(`payload source=${(typeof EMBED !== 'undefined' && EMBED) ? 'EMBED' : 'args'}; book=${A.book}; topics=${(A.topics || []).length}`)
const book = A.book
const topics = A.topics || []
const index = A.index || {}

const REPORT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  required: ['slug', 'levelsActual', 'fixes', 'accuracyFixes', 'figuresRenamed', 'linksFound', 'linksAdded', 'missingTargets', 'deeperTargets', 'insertsAudited', 'proposedStatus', 'notes'],
  properties: {
    slug: { type: 'string' },
    levelsActual: {
      type: 'object', additionalProperties: false,
      required: ['basicExists', 'detailedExists', 'basicWords', 'manifestLevels', 'levelsMatch'],
      properties: {
        basicExists: { type: 'boolean' },
        detailedExists: { type: 'boolean' },
        basicWords: { type: 'integer' },
        manifestLevels: { type: ['array', 'null'], items: { type: 'string' } },
        levelsMatch: { type: 'boolean' },
      },
    },
    fixes: { type: 'array', items: { type: 'string' }, description: 'Застосовані правки канону (що саме й де).' },
    accuracyFixes: { type: 'array', items: { type: 'string' }, description: 'Виправлені ЯВНІ змістові неточності (число/факт/дата/одиниця/назва/формула/логіка): що було → що стало. Порожньо, якщо таких не було.' },
    figuresRenamed: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['from', 'to'], properties: { from: { type: 'string' }, to: { type: 'string' } } } },
    linksFound: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['target', 'valid', 'detailed'], properties: { target: { type: 'string' }, valid: { type: 'boolean' }, detailed: { type: 'boolean', description: 'true якщо лінк на детальну версію <slug>-d.md' } } } },
    deeperTargets: { type: 'array', description: 'Цілі, на які посилаються як на детальну (-d.md) версію — головна сесія перевірить наявність і за потреби поставить deeper.', items: { type: 'object', additionalProperties: false, required: ['book', 'slug'], properties: { book: { type: 'string' }, slug: { type: 'string' } } } },
    linksAdded: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['target', 'where'], properties: { target: { type: 'string' }, where: { type: 'string' } } } },
    missingTargets: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        required: ['book', 'slug', 'suggestedSection', 'title', 'reason'],
        properties: {
          book: { type: 'string' }, slug: { type: 'string' },
          suggestedSection: { type: 'string' }, title: { type: 'string' }, reason: { type: 'string' },
        },
      },
    },
    insertsAudited: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'fixes', 'proposedStatus'], properties: { file: { type: 'string' }, fixes: { type: 'array', items: { type: 'string' } }, proposedStatus: { type: 'string', enum: ['done', 'update', 'deeper', 'empty', 'recheck'] } } } },
    proposedStatus: { type: 'string', enum: ['done', 'update', 'deeper', 'recheck'] },
    notes: { type: 'string' },
  },
}

function buildPrompt(t) {
  const tb = t.book || book
  const dir = `book/${tb}/${t.section}/${t.slug}`
  const insertList = Object.entries(t.inserts || {}).flatMap(([k, arr]) => (arr || []).map(x => `${dir}/${x.file} (${k})`))
  return `Ти проводиш АУДИТ "recheck" однієї статті проєкту courses та її вставок. Статус recheck (AUTHORING.md §9) = «передивитися за чинними правилами й ПРИВЕСТИ У ВІДПОВІДНІСТЬ» — і ФОРМУ, і ЗМІСТ.
КОНТЕНТ статті/вставок МОЖНА й ТРЕБА правити/переписувати ТАМ, ДЕ ВІН ПОРУШУЄ AUTHORING.md — саме для цього й існує recheck. Конкретно став під сумнів і виправляй за §4: метод Фейнмана (спершу інтуїція й «ЧОМУ», від першопричини; висновок будуємо на очах читача); причинно-наслідкові ланцюжки «A→тому B→звідси C» замість сухих списків; плавність (кожен абзац — місток від попереднього, наскрізна нитка навіщо→інтуїція→деталі→приклад); жива українська (без русизмів/кальок/канцеляриту/недоречних англіцизмів, лише справжні слова, один термін на поняття); першоджерело назв нових понять (мова-корінь у дужках). Також §5 (формули Unicode не LaTeX; worked-приклади реальним C/C++) і §7 (факти/дати/атрибуція — лише перевірені; за потреби WebSearch; уникати імперських міфів і єдиноосібних «першовідкривачів»).
МЕЖА: те, що вже ВІДПОВІДАЄ канону й написане добре — НЕ чіпай (не переписуй заради переписування). Міняй лише реальні порушення/неточності. Кожну ЗМІСТОВУ правку (стильову-за-§4 чи фактичну) клади в accuracyFixes[] стисло (що→на що).

КАНОН — повний текст нижче (керуйся ним; окремо AUTHORING.md НЕ читай):
══════════ AUTHORING.md ══════════
${A.canon || '(канон не вбудовано — прочитай AUTHORING.md у корені репо)'}
══════════ кінець канону ══════════

ТЕМА: ${tb}/${t.section}/${t.slug} — «${t.title}»
Тека: ${dir}
Базова стаття:   ${dir}/${t.slug}.md
Детальна (якщо є): ${dir}/${t.slug}-d.md
Вставки за маніфестом: ${insertList.length ? insertList.join('; ') : '(немає)'}
Маніфестні levels: ${JSON.stringify(t.levels)}
Фігури — у ${dir}/img/ . Один img/ ділять стаття + її вставки.

ЩО ЗРОБИТИ (правки роби напряму через Edit; фігури перейменовуй через git mv у Bash; manifest.js НЕ ЧІПАЙ):

A. КОНФОРМНІСТЬ КАНОНУ (зміст не міняти, лише форму):
   1. §5 підписи фігур: ПРИБРАТИ префікс «Рис.»/«Рисунок»/«Fig.» і будь-які номери. Підпис = звичайний опис курсивом наступним рядком після картинки, без номера.
   2. §5 посилання на фігуру: шлях ВІД КОРЕНЯ репо з ведучим «/»: «/${dir}/img/<file>». Виправ відносні «img/...» та «./img/...».
   3. §5+§2 імена файлів фігур: перейменуй НУМЕРОВАНІ (напр. fig-49-3-1-pipeline.svg, fig-3-9-1-1-sources.svg, fig-r09-0-2-weekend.svg) на slug-only без номерів — узявши описовий «хвіст» імені (pipeline.svg, sources.svg, weekend.svg). Перейменовуй через «git mv». ОНОВИ КОЖНЕ посилання ![..](/${dir}/img/<old>) на нове ім'я — у статті ТА в усіх вставках цієї теми (img/ спільний). Колізії імен — мінімальний кваліфікатор (напр. blur-box.svg). Якщо figs.py у теці теми існує — онови й у ньому імена; якщо ні (фігури статичні) — генератор не потрібен.
   4. §5 формули: ЖОДНОГО LaTeX ($...$, \\frac, \\(, \\[, \\times). Якщо є — переклади на Unicode (× · ² ₀ ε Δ σ ω → ≈ ≤ ≥) у тексті, а покрокові обчислення — у моноширинний код-блок, вирівняний по «=». Роздільник дробу — крапка.
   5. §1 фрази послідовності: у book/ ПОРЯДКУ НЕМАЄ. Прибери/переформулюй «попередній/наступний розділ», «як ми (вже) бачили», «далі/нижче побачимо», «пригадаймо», «ми це проходили», «раніше ми…», «у наступному розділі». Зроби формулювання самодостатнім, зміст збережи.
   6. §4 першоджерело назв: уводячи НОВЕ поняття вперше, дай у дужках мову-джерело й корінь (лат./гр./англ.): «атом (гр. átomos — неподільний)». Додавай лише там, де поняття справді ВВОДИТЬСЯ і етимології бракує; не засмічуй.
   7. §4 зміст і голос (за розширеним мандатом угорі): приведи у відповідність до §4 — метод Фейнмана, причинно-наслідкова нитка, плавність, жива українська. Русизми/кальки/канцелярит/випадкову синонімію — виправляй; один термін на поняття; де ПОЯСНЕННЯ порушує метод/плавність — перепиши той фрагмент (не весь файл). Що вже компліантне — не чіпай.
      ВИНЯТОК — НАСКРІЗНІ КНИГО-РІВНЕВІ ТЕРМІНИ: якщо термін уживається в БАГАТЬОХ темах і крос-лінкований (напр. русизм «дребезг» для контактів — він і в назві теми, і в десятках статей), НЕ міняй його в одній темі — це зламає «один термін на поняття» МІЖ статтями. Познач такий термін у notes для централізованої заміни головною сесією, лиши як є.
   8. §3 зворотні картки: у ВСТАВКАХ видали навігаційні футери-повернення до батьківської теми. ДВІ форми: (а) блок-цитати «> 🔗 Тема, до якої належить…», «> ▶️ До теми», «> ↩️ Назад до…»; (б) кінцеві H3-списки «### Пов'язане», «### Пов'язані історії», «### Related», «### Див. також» — список лінків наприкінці файлу, де є повернення на батьківську тему. Видаляй ВЕСЬ такий футер. Інлайн-лінки на теми В ТІЛІ тексту лишай. Якщо якийсь лінк із футера несе унікальний зміст, якого немає в тілі — вплети його як інлайн-лінк у відповідне речення тіла, але самого футера-навігації не лишай.
   9. Старі курсові §-номери: прибери ЗАЛИШКОВІ посилання-номери виду «§X.Y» чи «§X.Y.Z» (слід старої embedded-нумерації — у book/ курсу й розділів НЕМАЄ, тож номер беззмістовний). Шукай НЕ лише в прозі, а Й У КОМЕНТАРЯХ КОДУ — там вони ховаються найчастіше (напр. «// плавний пуск (§4.7.5)», «// узгоджено з §4.7.3»). Прибери тег/дужку з номером, лишивши зрозумілий опис; якщо поряд був справжній інлайн book:-лінк — його лишай. Те саме всередині тексту SVG-фігур, якщо трапиться.

B. ВЕРСІЇ (basic vs detailed): встанови, які файли РЕАЛЬНО є (${t.slug}.md / ${t.slug}-d.md), порахуй слова базової (без код-блоків). Звірся з маніфестними levels ${JSON.stringify(t.levels)} і познач, чи збігається (levelsMatch). НЕ вигадуй відсутню версію.

C. КРОС-ЛІНКИ (§6 — головне):
   • Знайди в статті ТА вставках усі лінки виду book:<предмет>/<slug> (і book:<предмет>/<slug>/<file>.md).
   • Валідуй кожен за наявним індексом (нижче). Якщо <slug> Є в index[<предмет>] → valid. Якщо НЕМАЄ → це missingTarget: НЕ створюй стаб (його зробить головна сесія), лінк ЛИШИ на місці, додай запис у missingTargets з полями {book:<предмет>, slug, suggestedSection (галузь тієї книги, куди логічно лягає), title (людяна укр. назва), reason}.
   • Справжні ЗАЛЕЖНОСТІ без лінка: якщо стаття СПИРАЄТЬСЯ на інше поняття (читач без нього не зрозуміє), а лінка нема — додай ІНЛАЙН-лінк [слова](book:<предмет>/<slug>) (НЕ картку-міст — у book/ лише інлайн-попап). Якщо ціль існує в індексі — лінкуй на неї. Якщо НЕ існує — обери коректний slug, додай інлайн-лінк на нього І додай missingTarget (щоб головна сесія створила стаб). Лінкуй ЛИШЕ справжні залежності, не кожну згадку (§6 — не ліс лінків).
   • Відносні .md-лінки → book:-форма (§6 попап), КРІМ одного випадку: тизер-картка у БАЗОВІЙ статті на ВЛАСНУ вставку ЦІЄЇ Ж теми (рядок виду «> 🧮/📜/🔌/⚙️ …[текст](<type>-<name>.md)», де файл — зареєстрована вставка цієї теми) — її ЛИШАЙ bare-relative: це усталений механізм прив'язки тизера, рушій рендерить обидві форми однаково, тож НЕ конвертуй і НЕ рахуй за правку. Усі інші .md-лінки (на вставки/статті ІНШИХ тем, insert→insert, на детальну версію) — переводь на book:-форму.
   • Версія в лінку: якщо лінк указує на ДЕТАЛЬНУ версію (book:<предмет>/<slug>/<slug>-d.md) — у linksFound постав detailed=true і додай ціль у deeperTargets {book,slug}; для базових статей і лінків на вставки detailed=false. Чи існує та детальна версія — НЕ перевіряй сам; рішення про статус deeper ухвалить головна сесія (§6/§9).
   • Наявні коректні інлайн-лінки НЕ перетворюй на картки.

ІНДЕКС наявних topic-slug-ів (для валідації book:-цілей):
${JSON.stringify(index)}

D. ВСТАВКИ: пройди ту саму конформність (A) по кожній вставці теми. Признач кожній proposedStatus (зазвичай done; deeper/update якщо є реальна змістова діра — лише познач, не дописуй контент).

ПОВЕРНИ структурований звіт (StructuredOutput) рівно за схемою: slug, levelsActual, fixes[], accuracyFixes[], figuresRenamed[], linksFound[] (з полем detailed), linksAdded[], missingTargets[], deeperTargets[], insertsAudited[], proposedStatus (для теми: done якщо все приведено; deeper/update якщо побачив реальну змістову проблему — лише сигнал), notes (стисло: що лишилось спірним). Сам текст редагуй у файлах; у звіт клади ОПИС, не вміст.`
}

phase('Audit')
log(`recheck-аудит: книга «${book}», батч ${topics.length} тем`)

const STAGGER_MS = 2500   // запуск агентів із розривом ~2.5с (анти-rate-limit; setTimeout у сендбоксі працює)
const MAX_TRIES = 2, RETRY_WAIT = 60000   // 1 повтор (сталий rate-limit retry-ями не лікується — лікується ПАУЗОЮ між батчами + меншим батчем)
async function agentRetry(prompt, opts) {
  for (let a = 1; a <= MAX_TRIES; a++) {
    let r = null
    try { r = await agent(prompt, opts) } catch (e) { r = null }
    if (r != null) return r
    if (a >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді після ${MAX_TRIES} спроб`); return null }
    await new Promise(res => setTimeout(res, RETRY_WAIT))
  }
}
const reports = await parallel(
  topics.map((t, i) => async () => {
    if (i) await new Promise(r => setTimeout(r, i * STAGGER_MS))
    return agentRetry(buildPrompt(t), { label: `recheck:${(t.book || book)}/${t.slug}`, phase: 'Audit', schema: REPORT_SCHEMA })
  })
)

return { book, count: topics.length, reports: reports.filter(Boolean) }
