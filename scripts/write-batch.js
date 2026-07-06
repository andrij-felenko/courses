export const meta = {
  name: 'write-batch',
  description: 'Повний v5-батч в один прогін. ФАЗИ: (1) Скаут — знайти перші N pending тем за level; (2) Статті — opus-max агенти (стагер 2с), кожен пише ОДНУ статтю (проза+фігури+ref-лінки на свої вставки й нові залежні теми), лінки генерує в прозі, а вміст вставок НЕ пише — лише повертає їх список; (3) Вставки — opus-max агенти (стагер 2с) пишуть зібрані вставки під ці статті; (4) Маніфест — серійно: статті→done, вставки→done, нові теми→pending. Жоден письменник маніфест НЕ чіпає. args = {book, kind?:"book"|"catalog"|"guide", level?:"basic"|"detailed", limit?:10, scope?, stagger?, units?}',
  phases: [
    { title: 'Скаут', detail: 'знайти перші N pending тем за level (sonnet, grep)' },
    { title: 'Статті', detail: 'opus-max: одна стаття на агента + список своїх вставок і нових тем; стагер 2с' },
    { title: 'Вставки', detail: 'opus-max: написати зібрані вставки під ці статті; стагер 2с' },
    { title: 'Маніфест', detail: 'серійно: статті→done, вставки→done, нові теми→pending, детальні→pending' },
    { title: 'Контроль', detail: 'wordcount.js (§3-обсяг) + svgcheck.py по написаних теках; лише звіт, non-fatal' },
  ],
}

/* ── args ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
const BOOK = _a && _a.book ? String(_a.book) : ''
const KIND = (_a && _a.kind) || 'book'             // book | catalog | guide
const SELF = KIND === 'guide' ? 'guide' : 'book'   // префікс лінка на ВЛАСНУ книгу/курс (§6: ціль у курсі → guide:)
const LEVEL = (_a && _a.level) || 'basic'          // basic → <slug>.md ; detailed → <slug>-d.md
const VER = LEVEL === 'detailed' ? 'detailed' : 'basic'
const SCOPE = (_a && _a.scope) || ''
const STAGGER = Number(_a && _a.stagger) || 2000   // мс між запусками агентів
const LIMIT = Number(_a && _a.limit) || 10
const UNITS_IN = (_a && Array.isArray(_a.units)) ? _a.units.filter((u) => u && u.slug && u.section) : null
if (!BOOK) throw new Error('args.book обовʼязковий')

const ROOT = 'E:\\develop\\courses'
const MF = `${KIND}/${BOOK}/manifest.js`
const MFWIN = `${ROOT}\\${MF.replace(/\//g, '\\')}`
const MAX_TRIES = 30, RETRY_WAIT = 60000
const LIMIT_WAIT = 10 * 60 * 1000, LIMIT_MAX = 48   // ліміт сесії: спати 10 хв і повторювати (до ~8 год) — пауза до ресету, не фейл

/* ── Канон письма (загальні правила; повне — AUTHORING.md) ── */
const CANON = `КАНОН письма (стисло; повне — ${ROOT}\\AUTHORING.md):
• Метод Фейнмана: глибоко, від першопричин; інтуїція й «ЧОМУ» → деталі; мотивацію давай, якщо є бодай легка потреба. Висновок будуй на очах у читача. Аналогії точні + де ламаються. Причинно-наслідкові ланцюжки, не списки. Поважай інтелект читача — без «як для малюків», без пафосу. НЕ мета-коментуй стиль (не пояснюй у тексті, ЧОМУ пишеш саме так) — просто пиши в ньому.
• Жива українська: лише справжні слова, без русизмів/кальок/канцеляриту/випадкової синонімії; один термін на поняття. Першоджерело назви в дужках при першій зустрічі: «атом (гр. átomos — неподільний)».
• Плавність: кожен абзац — місток від попереднього; наскрізна нитка навіщо→інтуїція→деталі→приклад; перед кінцем перечитай суцільно й згладь стики.
• Формули — Unicode у код-блоках (10⁻⁹, ε, ≈, ², ₀, ·), без LaTeX; роздільник — крапка (3.3). Worked-приклад: жирний підпис-умова → код-блок із покроковим обчисленням → висновок. КОД — реальний C/C++ (прошивка), не псевдокод.
• Біля важливого поняття — рамка «> 🔧 **Навіщо це.**» (на матеріалі цієї теми).
• ФІГУРИ: лише SVG, чистий Python без залежностей; figs.py У ТЕЦІ ТЕМИ, вивід ./img/. На початку figs.py: «import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..','..','..','..','scripts')); from svgkit import *». Рамки з текстом — ЛИШЕ через textbox()/fitbox(). ОЩАДЛИВО 2–5, кожна несе вагу; ПЕРЕВІР що figs.py відпрацьовує ШВИДКО (не зациклюється). Підключення «![опис](/${KIND}/${BOOK}/<секція>/<slug>/img/<file>.svg)» — від кореня репо (з /); підпис курсивом БЕЗ номера й «Рис.». Після генерації: «python ${ROOT}\\scripts\\svgcheck.py <тека-теми> --min-font 8» — виправляй, доки «із зауваженнями: 0» (v6: ловить і НАКЛАДАННЯ тексту — напис має бути поза чужими лініями й написами). ЩОБ УНИКНУТИ накладань: розставляй підписи з ЗАПАСОМ (ширші колонки/клітини, більший viewBox), не втискай довгі рядки поруч, лінії веди повз написи; накладання ОБОВʼЯЗКОВО усунь ДО 0, а не лишай.
• ФАКТИ: будь-яке історичне/фактичне твердження (дата, ім'я, «хто перший», винахід, патент, походження) — ВЕБ-ЗВІР ТУТ ЖЕ (WebSearch/WebFetch); познач статус доказовості. Не клей «російське», коли джерела дають точніше (українець, поляк, серб, єврей, грузин, вірменин, балт…); розрізняй ідею/теорію/реалізацію/систему/патент.
• КРОС-ЛІНКИ — ЛИШЕ на справжні залежності (не на кожну згадку!): короткий конспект 1–7 речень «що треба знати» + ref-попап. Ціль у книзі → book:<книга>/<slug>[/<file>]; ціль у курсі → guide:<курс>/<slug>[/<file>]. Галузі в лінку нема (2 сегменти + опц. файл). ПРАВИЛО «.md»: лінк на ТЕМУ/КРОК — 2 сегменти БЕЗ «.md» (напр. guide:embedded/pymavlink); лінк на ФАЙЛ (детальна <slug>-d.md чи вставка <type>-<name>.md) — 3-й сегмент З «.md». Усю ціль НЕ переписуй.
• НЕЙМИНГ slug-only; вставка — <type>-<name>.md (type ∈ hist/comp/math/proj); файл-вставка починається з H1 (можна з емодзі «# 📜 …»).
• МОВА ФІНАЛЬНА З ПЕРШОГО РАЗУ — окремої вичитки не буде.`

const KINDNOTE = KIND === 'guide'
  ? `\n\n⚠️ ЦЕ КУРС (guide), НЕ book-атом. Стаття курсу КУМУЛЯТИВНА — СПИРАЄТЬСЯ на пройдені кроки, ПРИПУСКАЄ вже відоме, поступово ПОГЛИБЛЮЄ. Фрази послідовності («як ми бачили», «у попередньому кроці», «далі побачимо») — ДОРЕЧНІ; нитку веди природно (спирайся ЛИШЕ назад), без натягування. Потрібні book-теми ВМОНТОВУЙ попапом (ref на book:), не переписуй. Власні теми/вставки курсу лінкуй guide:<курс>/...\n\n📕 КАНОН КУРСУ (опційний). ПЕРШОЮ ДІЄЮ Bash-перевір, чи є файл ${ROOT}\\${KIND}\\${BOOK}\\_canon.md. ЯКЩО Є — ПРОЧИТАЙ його ПОВНІСТЮ і суворо тримайся: наскрізний приклад курсу (сутності, стан на кожній версії, ухвалені на розвилках рішення й ЧОМУ), єдині терміни й імена. Будь-яку згадку спільного прикладу узгоджуй із каноном — НІЧОГО в прикладі не вигадуй усупереч йому (це те, що робить наскрізний приклад ЗВʼЯЗНИМ між статтями різних агентів). ЯКЩО файлу НЕМА — пиши як звичайно (у цього курсу канону нема).`
  : `\n\nЦе book-атом: САМОДОСТАТНЯ стаття, БЕЗ нумерації й БЕЗ фраз послідовності («попередній/наступний розділ», «як ми бачили», «далі побачимо») — у книзі порядку немає. Узагальнено: конкретну деталь/номер лише як приклад-згадку з лінком (catalog/comp-), не будуй статтю на ній.`

// додатковий нахил для книг про код: поряд з історією не забувай proj/math (алгоритм/код)
const INSERT_BIAS = (BOOK === 'programming' || BOOK === 'algorithms')
  ? `\n • (книга про ${BOOK === 'algorithms' ? 'алгоритми' : 'програмування'}) Історію лишай, де вона повчальна. Поряд, КОЛИ тема алгоритмічна/структурна/системна, зваж proj (робочий C/C++ чи алгоритм із покроковим розбором і складністю) і math (виведення, аналіз O(…), інваріанти, доведення коректності): для таких тем код і математика — осердя книги, тож якщо матеріал справді є — не лишай його лише в прозі, винось у вставку. Усе за контекстом теми, НЕ заради кількості.`
  : ''

/* ── helpers ── */
async function callAgent(prompt, opts) {
  let tries = 0, limitWaits = 0
  while (true) {
    let r = null, err = null
    try { r = await agent(prompt, opts) } catch (e) { r = null; err = e }
    if (r != null) return r
    const isLimit = err && /session limit|usage limit|hit your|resets \d|quota|rate limit/i.test(String((err && err.message) || err))
    if (isLimit) {                                   // ліміт сесії: пауза до відновлення, не молотити й не кидати
      if (limitWaits >= LIMIT_MAX) { log(`⛔ ліміт не відпустив за ${LIMIT_MAX} спроб (${opts && opts.label})`); return null }
      limitWaits++
      log(`⏳ ЛІМІТ СЕСІЇ — чекаю ${LIMIT_WAIT / 60000} хв до відновлення й повторю [${limitWaits}/${LIMIT_MAX}] (${opts && opts.label})`)
      await new Promise((res) => setTimeout(res, LIMIT_WAIT))
      continue
    }
    tries++
    if (tries >= MAX_TRIES) { log(`⛔ ${opts && opts.label}: нема відповіді після ${MAX_TRIES} спроб`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}
async function staggered(items, fn) {           // запуск зі стагером STAGGER, тоді Promise.all
  const proms = []
  for (let i = 0; i < items.length; i++) {
    proms.push(fn(items[i], i))
    if (i < items.length - 1) await new Promise((r) => setTimeout(r, STAGGER))
  }
  return Promise.all(proms)
}
function topicDirWin(section, slug) { return `${ROOT}\\${KIND}\\${BOOK}\\${section}\\${slug}` }

/* ── схеми ── */
const UNITS = { type: 'object', additionalProperties: false, required: ['units'], properties: { units: { type: 'array', items: {
  type: 'object', additionalProperties: false, required: ['section', 'slug', 'title'],
  properties: { section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, scope: { type: 'string' } } } } } }
const ART_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: {
  ok: { type: 'boolean' }, files: { type: 'array', items: { type: 'string' } }, note: { type: 'string' },
  inserts: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'type', 'brief'], properties: { file: { type: 'string' }, type: { type: 'string' }, brief: { type: 'string' } } } },
  newTopics: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['kind', 'book', 'section', 'slug', 'title'], properties: { kind: { type: 'string' }, book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, needDetailed: { type: 'boolean' } } } },
  needDetailedSelf: { type: 'boolean' },
  deeperTargets: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['book', 'slug'], properties: { book: { type: 'string' }, slug: { type: 'string' } } } } } }
const INS_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, file: { type: 'string' }, note: { type: 'string' } } }
const REG_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } }
const CTRL_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, problems: { type: 'array', items: { type: 'object', additionalProperties: false, required: ['file', 'issue'], properties: { file: { type: 'string' }, issue: { type: 'string' } } } } } }

/* ──────────────── ФАЗА 1 — СКАУТ ──────────────── */
let WORK = []
if (UNITS_IN) {
  WORK = UNITS_IN.slice(0, LIMIT)
  log(`Скаут (інлайн): ${WORK.length} тем`)
} else {
  phase('Скаут')
  const scout = await callAgent(
    `Знайди перші ${LIMIT} тем зі статусом «${VER}.status: "pending"» у маніфесті ${MFWIN}.
Схема: book/catalog — sections[]→topics[]; guide (v6) — modules[]→chapters[]→steps[]. В ОБОХ формах рядок секції/модуля містить "scope:", а тема/крок — { slug, title, basic:{status}, detailed:{status} } одним рядком; для guide поверни section = slug МОДУЛЯ. КРОК-ref (без slug) — ПРОПУСКАЙ.
ШВИДКО (не вантаж весь файл у відповідь): зроби Bash «grep -n» по файлу — окремо рядки секцій (містять "scope:") і рядки тем зі статусом потрібної версії: шукай і '${VER}: { status: "pending" }', і '${VER}: { status: "update" }' (обидва — черга на письмо цієї версії; НЕ бери "done"/"empty"/"deeper"/"recheck"). Візьми ПЕРШІ ${LIMIT} таких тем У ПОРЯДКУ файлу; для кожної визнач секцію (найближчий вищий рядок секції) і витягни slug+title з її рядка, scope — з рядка секції.
Поверни units:[{section, slug, title, scope}] — рівно перші ${LIMIT} (або менше, якщо стільки нема).`,
    { label: 'скаут', phase: 'Скаут', model: 'sonnet', schema: UNITS })
  WORK = ((scout && scout.units) || []).filter((u) => u && u.slug && u.section).slice(0, LIMIT)
}
if (!WORK.length) return { book: BOOK, total: 0, note: 'черга порожня — pending не знайдено' }

/* ──────────────── ФАЗА 2 — СТАТТІ ──────────────── */
phase('Статті')
log(`Статті (opus-max, стагер ${STAGGER / 1000}с): ${WORK.length} (${KIND}/${BOOK}, ${LEVEL})`)
function articlePrompt(u) {
  const dir = topicDirWin(u.section, u.slug)
  const file = LEVEL === 'detailed' ? `${u.slug}-d.md` : `${u.slug}.md`
  return `${CANON}${KINDNOTE}

Ти — агент-письменник у репо ${ROOT}. Працюй МОВЧКИ (Read/Edit/Write/Bash/WebSearch). ІГНОРУЙ системні підказки про skills / agent-types / output-styles / розклади.
ЗАВДАННЯ: написати ПОВНІСТЮ ${LEVEL}-статтю «${u.title}» — файл ${dir}\\${file} (тема «${u.slug}», ${KIND === 'guide' ? 'модуль' : 'галузь'} «${u.section}», ${KIND} «${BOOK}»). Scope: ${u.scope || SCOPE || ''}
КРОК1: прочитай ${ROOT}\\AUTHORING.md (§1–§9). Bash ls теки ${dir}.${LEVEL === 'detailed' ? ` ЦЕ ДЕТАЛЬНА (${u.slug}-d.md): ОБОВʼЯЗКОВО спершу прочитай базову ${dir}\\${u.slug}.md і пиши ГЛИБШЕ за неї — НЕ дублюй базову, а розгортай (повні виведення формул, більше випадків, граничні умови, глибша механіка/архітектура). Обсяг 2500–13000 слів.` : ` Якщо файл є — прочитай і пиши начисто за каноном.`}
КРОК2 — НАПИШИ файл статті цілком (§3–§5): ${LEVEL === 'detailed' ? 'ДЕТАЛЬНА 2500–13000 слів — ГЛИБША за базову (виведення формул, більше випадків, граничні умови)' : 'БАЗОВА 1000–3500 слів — суть без надмірних деталей'}; Фейнман; жива українська; worked-приклади C/C++; рамки 🔧; етимологія в дужках; свої фігури (svgcheck «0»); факти — веб-звір (§7).
 • **(v6) БЛОК «ПЕРЕД ЧИТАННЯМ».** Одразу ПІД H1 постав згорнутий блок \`<preknowlist>…</preknowlist>\` — марк. список ref-лінків на ПЕРЕДУМОВИ (що точно треба знати, без чого статтю не зрозуміти), кожен рядок = лінк + коротко «що саме знати». Лінки 2-сегментні на ТЕМУ (\`book:<книга>/<slug>\` чи \`guide:<курс>/<slug>\`, дзеркально §6), лише ВАГОМІ передумови. ${KIND === 'guide' ? 'КУРС: клади лише передумови ЗЗОВНІ курсу АБО ще не пройдені по нитці — те, що курс уже дав раніше, НЕ додавай.' : 'book/catalog: усі справжні передумови (стаття standalone).'} Якщо тема-передумова ще не існує в репо — обробляй як залежність (додай у newTopics, КРОК3).${KIND === 'catalog' ? `
 • **(§8) КАТАЛОГ — КОНКРЕТНИЙ ОБʼЄКТ.** Описуєш саме цю річ (плату/модуль/прилад/деталь): читач має УПІЗНАТИ її, зрозуміти що робить і як влаштована, як підʼєднати/використати й чого стерегтися. Секції добирай САМ під природу пристрою; партномери/моделі ДОРЕЧНІ (це каталог). БЕЗ фраз послідовності. ЛІНКИ каталогу — ЗАВЖДИ префікс book: (родини в __BOOKS__): тема book:РОДИНА/slug; вставка book:РОДИНА/slug/ТИП-назва.md. Префікса catalog: НЕ існує, і шлях-лінк у дужках-catalog НЕ вживай — тільки book:-попап.
 • **(§8) ПЛАТА/МОДУЛЬ ЗІ СХЕМОЮ — ОБОВʼЯЗКОВО.** Якщо річ має схему устрою АБО схему підключення: (а) зобрази ОБИДВІ SVG-фігури — принципову схему + розводку ПІН-У-ПІН (svgcheck 0); (б) опиши їх (живлення, рівні, підтяжки, що куди); (в) дай API у proj-вставці — додай у inserts[] { file:"proj-<name>.md", type:"proj", brief:"API: бібліотека/типові виклики, як підключити й керувати в коді, робочий C/C++, пастки" }. Без цих трьох board/модуль-стаття НЕПОВНА. Голі пасиви/розхідники (резистори, дроти, припій) — без схеми/API, коротко за призначенням.
 • **(§8) РОДИНА — ЛІНКУЙ, НЕ ПОВТОРЮЙ.** Якщо продукт належить до лінійки з кількох варіантів (спільний виробник/архітектура/історія — ESP32, Arduino, RPi, KY-серія…) — НЕ переказуй спільну історію/архітектуру ТУТ. Постав ref-попап на ОГЛЯДОВУ статтю родини book:<родина>/<family> (напр. book:boards/esp32-family) по спільне й опиши ЛИШЕ специфіку цього продукту. Нема family-топіка — додай у newTopics { kind:"catalog", book:"<родина>", section:"<секція>", slug:"<family>", title:"Родина …" } (і постав на нього ref).` : ''}
КРОК3 — ЛІНКИ Й СПИСКИ (головне для конвеєра):
 • ВЛАСНІ ВСТАВКИ (низький поріг рішення, але КОНТЕКСТНО — скільки просить тема). Якщо в темі є під-блок, який можна корисно розгорнути окремо (історія народження / математика-виведення / код-проєкт / розбір алгоритму / клас-компонент) — винеси його вставкою, а не стискай у статті. Вагаєшся «варте окремої вставки чи ні» — радше РОБИ. НОРМИ на кількість НЕМА: скільки просить логіка теми — стільки й став (одна тема — жодної вставки, інша — кілька різних типів, коли кожна справді потрібна: hist/math/proj доповнюють одне одного). Заради числа НЕ додавай. Межа — якість: кожна несе окремий шар, не переказ статті. НЕ пиши вміст вставки тут. Натомість: (а) встав у прозі ref-зноску-попап [текст](${SELF}:${BOOK}/${u.slug}/<type>-<name>.md) — лінк ОБОВʼЯЗКОВО з розширенням «.md» (без нього рушій не відкриє) — з конспектом 1–7 речень; (б) додай її в inserts:[{file:"<type>-<name>.md", type:"hist|comp|math|proj", brief:"2–4 речення: що саме вставка має покрити"}]. Її напише НАСТУПНА фаза. ⚠️ КОЖНА вставка, на яку ти поставив ref у прозі, МУСИТЬ бути в inserts[] з ТИМ САМИМ іменем файлу — жодного ref без запису (інакше файл не створять → битий лінк).${KIND === 'catalog' ? ' (catalog — без comp-.)' : ''}${INSERT_BIAS}
 • НОВІ ЗАЛЕЖНІ ТЕМИ. Якщо стаття справді спирається на тему, якої ЩЕ НЕМА в репо — постав ref (book:<книга>/<slug> або guide:<курс>/<slug>) і додай у newTopics:[{kind,book,section,slug,title,needDetailed}]. Якщо лінкуєш на ДЕТАЛЬНУ нової теми (…-d.md) — став needDetailed:true. Лінк на файл — ЗАВЖДИ з «.md». Файл НЕ створюй.${LEVEL === 'basic' ? `
 • ДЕТАЛЬНА ВЕРСІЯ ЦІЄЇ ТЕМИ (§3, НИЗЬКИЙ ПОРІГ). Оціни: чи має тема РЕАЛЬНИЙ другий шар — виведення формул, протокол/алгоритм, багатогранна архітектура/залізо, багато граничних випадків? Якщо, пишучи базову, ти СТИСКАВ матеріал — постав needDetailedSelf:true (детальну поставлять у чергу). Проста довідка/огляд/вузька замітка — needDetailedSelf:false.` : ''}
 • DEEPER-ЦІЛІ (§6). Якщо лінкуєш на ДЕТАЛЬНУ («…-d.md») теми, що ВЖЕ Є в репо, але має лише базову, — додай ту тему в deeperTargets:[{book,slug}] (щоб її детальну поставили в чергу). Лінк лишай на -d.md.
 • МАНІФЕСТ НЕ ЧІПАЙ. Вставки САМ не пиши (це фаза 3).
КРОК4 — САМОАУДИТ: svgcheck «0»; обсяг у смузі §3; без LaTeX/«Рис.»; ${KIND === 'guide' ? 'нитка курсу доречна (лише назад)' : 'самодостатньо, без фраз послідовності'}.
Поверни: ok, files (стаття+фігури), inserts (свої вставки на фазу 3), newTopics (нові залежні теми на реєстрацію), needDetailedSelf (чи варта ця тема детальної, §3), deeperTargets (наявні теми, ref-нуті як -d.md, §6), note.`
}
const aResults = await staggered(WORK, (u) =>
  callAgent(articlePrompt(u), { label: `стаття:${u.slug}`, phase: 'Статті', model: 'opus', effort: 'max', schema: ART_RET })
    .then((pr) => ({ u, ok: !!(pr && pr.ok), inserts: (pr && pr.inserts) || [], newTopics: (pr && pr.newTopics) || [], needDetailedSelf: !!(pr && pr.needDetailedSelf), deeperTargets: (pr && pr.deeperTargets) || [], note: pr && pr.note }))
    .catch(() => ({ u, ok: false, inserts: [], newTopics: [], needDetailedSelf: false, deeperTargets: [] })))
const doneArticles = aResults.filter((r) => r.ok).map((r) => r.u)
const INSERTS = aResults.filter((r) => r.ok).flatMap((r) => r.inserts.map((i) => ({ ...i, section: r.u.section, topicSlug: r.u.slug, topicTitle: r.u.title })))
const NEWTOPICS = aResults.filter((r) => r.ok).flatMap((r) => r.newTopics)
// §3/§6 — детальні версії у чергу: власна тема (needDetailedSelf, лише коли пишемо basic) + deeper-цілі (ref на -d.md наявних тем)
const DETAILED_NEED = []
if (LEVEL === 'basic') for (const r of aResults) if (r.ok && r.needDetailedSelf) DETAILED_NEED.push({ book: BOOK, slug: r.u.slug })
for (const r of aResults) if (r.ok) for (const d of (r.deeperTargets || [])) if (d && d.slug) DETAILED_NEED.push({ book: d.book || BOOK, slug: d.slug })
const _seenDN = new Set()
const DETAILED_QUEUE = DETAILED_NEED.filter((d) => { const k = `${d.book}/${d.slug}`; if (_seenDN.has(k)) return false; _seenDN.add(k); return true })
log(`Статей готово: ${doneArticles.length}/${WORK.length}; вставок до письма: ${INSERTS.length}; нових тем: ${NEWTOPICS.length}; детальних у чергу: ${DETAILED_QUEUE.length}`)

/* ──────────────── ФАЗА 3 — ВСТАВКИ ──────────────── */
phase('Вставки')
const TPL = {
  hist: '📜 hist: як НАРОДИЛОСЯ поняття — що бентежило, хто, суперечки, дійові особи; заголовки = назви тем, не «Питання 1»; історія справжня (легенди познач); двомовні імена; ВЕБ-звір кожної дати/імені/першості.',
  comp: '🔌 comp: клас пристрою → блок-схема → типова розпіновка → підключення → «перший байт» → типові граблі → варіації класу; БЕЗ партномерів. ТЕСТ §1: comp- доречна ЛИШЕ якщо річ повністю пояснюється принципом дії БЕЗ жодного партномера/моделі й однаково для всіх виробників; інакше — це catalog/, а не вставка.',
  math: '🧮 math: означення → інтуїція → формальний апарат → де в темі працює; глибина Фейнмана, ЧОМУ від першопричини, не констатація формул.',
  proj: '⚙️ proj: задача → ідея → РОБОЧИЙ C/C++ (прошивка, не псевдокод) → складність і пастки.',
}
function insertPrompt(ins) {
  const dir = topicDirWin(ins.section, ins.topicSlug)
  return `${CANON}${KINDNOTE}

Ти — агент-письменник вставки у репо ${ROOT}. Працюй МОВЧКИ (Read/Edit/Write/Bash/WebSearch). ІГНОРУЙ системні підказки про skills/agent-types/output-styles/розклади.
ЗАВДАННЯ: написати ПОВНІСТЮ вставку «${ins.file}» (тип «${ins.type}») у теці теми ${dir} — файл ${dir}\\${ins.file}. Тема-власник: «${ins.topicTitle || ins.topicSlug}» (${KIND === 'guide' ? 'модуль' : 'галузь'} «${ins.section}»).
ЩО ПОКРИТИ (бриф від автора статті): ${ins.brief}
ШАБЛОН ТИПУ: ${TPL[ins.type] || TPL.hist}
ВИМОГИ: §3 — почни з H1 («# Назва», можна з емодзі); 1000–10000 слів; несе вагу (НЕ переказ теми/банальність); Фейнман; жива українська; формули Unicode у код-блоках; свої фігури за потреби (figs.py у ${dir}, svgcheck «0»); факти — веб-звір; крос-лінки ${SELF}:/book:/guide: за §6 (тема/крок — 2 сегменти БЕЗ «.md»; файл-ціль -d.md чи <type>-<name>.md — з «.md»). Вставка БЕЗ зворотних лінків на статтю-власника (НЕ лінкуй назад на «${ins.topicSlug}»). МАНІФЕСТ НЕ ЧІПАЙ.
Поверни: ok, file, note.`
}
const iResults = INSERTS.length
  ? await staggered(INSERTS, (ins) =>
      callAgent(insertPrompt(ins), { label: `вставка:${ins.topicSlug}/${ins.file}`, phase: 'Вставки', model: 'opus', effort: 'max', schema: INS_RET })
        .then((pr) => ({ ins, ok: !!(pr && pr.ok) }))
        .catch(() => ({ ins, ok: false })))
  : []
const doneInserts = iResults.filter((r) => r.ok).map((r) => r.ins)
log(`Вставок готово: ${doneInserts.length}/${INSERTS.length}`)

/* ──────────────── ФАЗА 4 — МАНІФЕСТ (серійно) ──────────────── */
phase('Маніфест')
if (doneArticles.length) {
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2 — статус ПЕР-ВЕРСІЙНИЙ): для тем зі slug ∈ ${JSON.stringify(doneArticles.map((u) => u.slug))} зміни ${VER}.status на "done" (Edit точково — саме поле "${VER}" тієї теми; іншу версію й решту не чіпай). Поверни ok, count.`,
    { label: 'статті→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
if (doneInserts.length) {
  const payload = doneInserts.map((i) => ({ section: i.section, topicSlug: i.topicSlug, type: i.type, file: i.file }))
  await callAgent(
    `Онови маніфест ${MFWIN} (схема v6 §2): зареєструй НАПИСАНІ вставки як ГОТОВІ. Для кожної знайди тему за (section, topicSlug) і додай у масив свого типу елемент { file, status: "done" } (масив type створи, якщо його ще нема; НЕ дублюй, якщо вже є — лише постав status:"done"). Edit точково. ВСТАВКИ: ${JSON.stringify(payload)}\nПоверни ok, count.`,
    { label: 'вставки→done', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}
if (NEWTOPICS.length) {
  await callAgent(
    `Зареєструй НОВІ залежні теми зі статусом "pending" у ВІДПОВІДНИХ маніфестах (схема v6 §2) за kind+book (book/<book>/manifest.js | catalog/<book>/manifest.js | guide/<course>/manifest.js). Для кожної знайди section за її slug і Edit-точково додай { slug, title, basic:{status:"pending"}, detailed:{status: needDetailed ? "pending" : "empty"} }, НЕ дублюючи наявне (спершу перевір, чи вже є такий slug). Якщо section відсутня — створи. НОВІ ТЕМИ: ${JSON.stringify(NEWTOPICS)}\nПоверни ok, count.`,
    { label: 'нові→pending', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}

if (DETAILED_QUEUE.length) {
  await callAgent(
    `Постав детальні версії В ЧЕРГУ (§3/§6). Для кожної {book,slug} з переліку: у ВІДПОВІДНОМУ маніфесті book/<book>/manifest.js знайди тему за slug і ЯКЩО її detailed.status === "empty" — Edit-точково зміни на "pending" (треба написати -d.md). Якщо detailed вже "pending"/"done"/"deeper"/"update" — НЕ чіпай. basic та інші теми НЕ чіпай. Не дублюй. ПЕРЕЛІК: ${JSON.stringify(DETAILED_QUEUE)}\nПоверни ok, count.`,
    { label: 'детальні→pending', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}

/* ──────────────── ФАЗА 5 — КОНТРОЛЬ (§3-обсяг + фігури; лише звіт) ──────────────── */
let PROBLEMS = []
const _cdirs = new Set()
for (const u of doneArticles) _cdirs.add(`${u.section}/${u.slug}`)
for (const i of doneInserts) _cdirs.add(`${i.section}/${i.topicSlug}`)
const DONE_DIRS = [..._cdirs]
if (DONE_DIRS.length) {
  phase('Контроль')
  const ctrl = await callAgent(
    `Ти — агент-контролер якості у репо ${ROOT}. Працюй МОВЧКИ (лише Bash). НІЧОГО НЕ ПИШИ й НЕ ПРАВ — тільки перевір і звітуй.
Цей батч написав теми (${KIND}/${BOOK}), теки (відносно кореня репо): ${JSON.stringify(DONE_DIRS.map((d) => `${KIND}/${BOOK}/${d}`))}
ПЕРЕВІРКА 1 — ОБСЯГ §3: Bash «node ${ROOT}\\scripts\\wordcount.js ${KIND}/${BOOK} --all». У виводі знайди ЛИШЕ файли з ТЕК цього батчу, що позначені як поза смугою (замало/забагато слів за §3: базова 1000–3500, детальна 2500–13000, вставка 1000–10000).
ПЕРЕВІРКА 2 — ФІГУРИ: для КОЖНОЇ теки батчу зроби Bash «python ${ROOT}\\scripts\\svgcheck.py ${ROOT}\\${KIND}\\${BOOK}\\<секція>\\<slug> --min-font 8» і знайди фігури «із зауваженнями» (не 0).
Поверни problems:[{file, issue}] — лише РЕАЛЬНІ порушення у теках цього батчу (порожньо, якщо все гаразд). НЕ виправляй.`,
    { label: 'контроль', phase: 'Контроль', model: 'sonnet', schema: CTRL_RET })
  PROBLEMS = (ctrl && ctrl.problems) || []
  if (PROBLEMS.length) { log(`⚠️ Контроль знайшов ${PROBLEMS.length} проблем(и):`); for (const p of PROBLEMS) log(`   • ${p.file}: ${p.issue}`) }
  else log(`Контроль: обсяг §3 і фігури — без зауважень`)
}

const okN = doneArticles.length
return { book: BOOK, kind: KIND, level: LEVEL, scouted: WORK.length, articles: okN, articlesFailed: WORK.length - okN, inserts: doneInserts.length, insertsFailed: INSERTS.length - doneInserts.length, newTopics: NEWTOPICS.length, detailedQueued: DETAILED_QUEUE.length, problems: PROBLEMS }
