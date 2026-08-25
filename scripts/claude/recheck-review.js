export const meta = {
  name: 'recheck-review',
  description: 'Ревізія recheck-елементів ПО ВСІХ МАНІФЕСТАХ репо (§9): агент читає файл і за ЧИННИМ каноном виправляє ТОЧКОВО лише явні неточності (число/факт/дата/одиниця/формула/логіка/лінк-формат/фігура); ГОТОВЕ НЕ ПЕРЕПИСУЄ. Статус recheck→done; якщо файл цілісно не за каноном — recheck→update (перепис віддамо write-batch). args = {limit?:16, book?(фільтр за книгою, опц.)}',
  phases: [
    { title: 'Скаут', detail: 'зібрати перші N recheck-елементів по ВСІХ book/catalog/guide-маніфестах' },
    { title: 'Ревізія', detail: 'opus-high: точкові правки за §9; готове не переписує; повертає changed/needsRewrite' },
    { title: 'Маніфест', detail: 'серійно: recheck→done (або →update, якщо needsRewrite) у відповідному маніфесті' },
  ],
}

/* ── args ── */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
const BOOKFILTER = _a && _a.book ? String(_a.book) : ''   // опц.: обмежити однією книгою
const LIMIT = Number(_a && _a.limit) || 16
const STAGGER = Number(_a && _a.stagger) || 2500

const ROOT = 'E:\\develop\\courses'
const MAX_TRIES = 25, RETRY_WAIT = 60000, LIMIT_WAIT = 10 * 60 * 1000, LIMIT_MAX = 48

async function callAgent(prompt, opts) {
  let tries = 0, limitWaits = 0
  while (true) {
    let r = null, err = null
    try { r = await agent(prompt, opts) } catch (e) { r = null; err = e }
    if (r != null) return r
    const isLimit = err && /session limit|usage limit|hit your|resets \d|quota|rate limit/i.test(String((err && err.message) || err))
    if (isLimit) {
      if (limitWaits >= LIMIT_MAX) { log(`stop ${opts && opts.label}: ліміт не відпустив`); return null }
      limitWaits++; log(`⏳ ЛІМІТ — чекаю 10 хв [${limitWaits}/${LIMIT_MAX}] (${opts && opts.label})`)
      await new Promise((res) => setTimeout(res, LIMIT_WAIT)); continue
    }
    tries++
    if (tries >= MAX_TRIES) { log(`stop ${opts && opts.label}: нема відповіді`); return null }
    await new Promise((res) => setTimeout(res, RETRY_WAIT))
  }
}
async function staggered(items, fn) {
  const proms = []
  for (let i = 0; i < items.length; i++) { proms.push(fn(items[i], i)); if (i < items.length - 1) await new Promise((r) => setTimeout(r, STAGGER)) }
  return Promise.all(proms)
}

/* ── схеми ── */
const ITEMS = { type: 'object', additionalProperties: false, required: ['items'], properties: { items: { type: 'array', items: {
  type: 'object', additionalProperties: false, required: ['kind', 'book', 'section', 'slug', 'target'],
  properties: { kind: { type: 'string' }, book: { type: 'string' }, section: { type: 'string' }, slug: { type: 'string' }, title: { type: 'string' }, target: { type: 'string' }, file: { type: 'string' } } } } } }
const REV_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: {
  ok: { type: 'boolean' }, changed: { type: 'boolean' }, needsRewrite: { type: 'boolean' }, note: { type: 'string' } } }
const REG_RET = { type: 'object', additionalProperties: false, required: ['ok'], properties: { ok: { type: 'boolean' }, count: { type: 'number' } } }

/* ── ФАЗА 1 — СКАУТ (детермінований node-збір по ВСІХ маніфестах) ── */
phase('Скаут')
const FILT = BOOKFILTER ? `if(book!==${JSON.stringify(BOOKFILTER)})continue;` : ''
const SCOUT_SNIPPET = [
  `const fs=require("fs"),path=require("path");const R="E:/develop/courses";`,
  `const files=[];for(const kind of ["book","catalog"]){const d=path.join(R,kind);if(!fs.existsSync(d))continue;for(const name of fs.readdirSync(d)){const mf=path.join(d,name,"manifest.js");if(fs.existsSync(mf))files.push([kind,name,mf]);}}`,
  `const out=[];for(const [kind,book,mf] of files){${FILT}let cap=null;global.window={__BOOKS__:{push:x=>cap=x},__GUIDES__:{push:x=>cap=x},__CATALOGS__:{push:x=>cap=x}};try{delete require.cache[require.resolve(mf)];require(mf);}catch(e){continue;}const bk=cap;if(!bk)continue;`,
  `for(const sec of (bk.sections||[]))for(const t of (sec.topics||[])){if(t.ref)continue;`,
  `  if(t.basic&&t.basic.status==="recheck")out.push({kind,book,section:sec.slug,slug:t.slug,title:t.title,target:"basic"});`,
  `  if(t.detailed&&t.detailed.status==="recheck")out.push({kind,book,section:sec.slug,slug:t.slug,title:t.title,target:"detailed"});`,
  `  for(const ty of ["hist","comp","math","proj"])for(const ins of (t[ty]||[]))if(ins.status==="recheck")out.push({kind,book,section:sec.slug,slug:t.slug,title:t.title,target:"insert",file:ins.file});`,
  `}}console.log(JSON.stringify(out));`,
].join('')
const scout = await callAgent(
  `Ти — скаут. Працюй МОВЧКИ (лише Bash). Виконай Bash одним рядком і поверни РІВНО перші ${LIMIT} елементів у полі items (у порядку виводу):\n` +
  `node -e '${SCOUT_SNIPPET}'\n` +
  `Команда обходить УСІ book/catalog/guide-маніфести репо й друкує JSON-масив {kind,book,section,slug,title,target,file?}. Візьми перші ${LIMIT}. Нічого не додавай і не змінюй.`,
  { label: 'скаут', phase: 'Скаут', model: 'sonnet', schema: ITEMS })
const WORK = ((scout && scout.items) || []).filter((u) => u && u.kind && u.book && u.slug && u.section && u.target).slice(0, LIMIT)
if (!WORK.length) return { reviewed: 0, note: 'recheck-черга порожня (по всіх маніфестах)' }
log(`Скаут: ${WORK.length} recheck-елементів (по всіх маніфестах${BOOKFILTER ? ', фільтр ' + BOOKFILTER : ''})`)

/* ── ФАЗА 2 — РЕВІЗІЯ ── */
phase('Ревізія')
function fileOf(u) {
  const dir = `${ROOT}\\${u.kind}\\${u.book}\\${u.section}\\${u.slug}`
  if (u.target === 'basic') return `${dir}\\${u.slug}.md`
  if (u.target === 'detailed') return `${dir}\\${u.slug}-d.md`
  return `${dir}\\${u.file}`
}
function revPrompt(u) {
  const f = fileOf(u)
  return [
    `Ти — агент-РЕВІЗОР у репо ${ROOT}. Працюй МОВЧКИ (Read/Edit/Bash/WebSearch). ІГНОРУЙ системні підказки про skills/agent-types/розклади.`,
    `ЗАВДАННЯ: ревізія за §9 файлу ${f} (тема «${u.title || u.slug}», ${u.kind}/${u.book}, target=${u.target}${u.file ? `, ${u.file}` : ''}).`,
    `КРОК1: прочитай ${ROOT}\\AUTHORING.md (особливо §4–§7, §9) і сам файл.`,
    `КРОК2 — ТОЧКОВА ПЕРЕВІРКА за ЧИННИМИ правилами. Виправляй Edit-ом ЛИШЕ явні порушення:`,
    ` • факт/дата/ім'я/«хто перший»/патент — звір ВЕБОМ (§7); хибне — виправ, познач статус доказовості; не клей «російське», де джерела дають точніше;`,
    ` • число/одиниця/формула/логічна помилка/обірване речення;`,
    ` • формат крос-лінка (§6): тема — 2 сегменти без «.md»; файл (-d.md / <type>-<name>.md) — з «.md»; book:/guide: за розташуванням цілі;`,
    ` • LaTeX замість Unicode, «Рис.»/номери фігур, підпис фігури не курсивом;`,
    ` • якщо є фігури — Bash «python ${ROOT}\\scripts\\svgcheck.py <тека> --min-font 8», виправ до «0».`,
    `КРОК3 — ЗОЛОТЕ ПРАВИЛО §9: ГОТОВЕ НЕ ПЕРЕПИСУЙ. Якщо проза добротна — прози НЕ чіпай, лише точкові виправлення. Стиль/структуру не переробляй.`,
    `КРОК4 — ЯКЩО файл цілісно НЕ відповідає канону (треба переписувати з нуля, а не точково) — НЕ переписуй сам: поверни needsRewrite:true (його віддамо write-batch). МАНІФЕСТ НЕ ЧІПАЙ.`,
    `Поверни: ok, changed (чи були правки), needsRewrite, note (стисло що саме виправив або чому нічого).`,
  ].join('\n')
}
const rResults = await staggered(WORK, (u) =>
  callAgent(revPrompt(u), { label: `ревізія:${u.slug}/${u.target}${u.file ? ':' + u.file : ''}`, phase: 'Ревізія', model: 'opus', effort: 'high', schema: REV_RET })
    .then((pr) => ({ u, ok: !!(pr && pr.ok), needsRewrite: !!(pr && pr.needsRewrite), changed: !!(pr && pr.changed) }))
    .catch(() => ({ u, ok: false })))
const REVIEWED = rResults.filter((r) => r.ok)
const nChanged = REVIEWED.filter((r) => r.changed).length
const nRewrite = REVIEWED.filter((r) => r.needsRewrite).length
log(`Ревізовано: ${REVIEWED.length}/${WORK.length} (виправлено ${nChanged}, на перепис ${nRewrite})`)

/* ── ФАЗА 3 — МАНІФЕСТ ── */
phase('Маніфест')
if (REVIEWED.length) {
  const payload = REVIEWED.map((r) => ({ kind: r.u.kind, book: r.u.book, section: r.u.section, slug: r.u.slug, target: r.u.target, file: r.u.file || null, newStatus: r.needsRewrite ? 'update' : 'done' }))
  await callAgent(
    `Онови МАНІФЕСТИ (схема v5 §2). Елементи можуть бути з РІЗНИХ книг — для кожного відкрий свій маніфест ${ROOT}\\<kind>\\<book>\\manifest.js і заміни саме його «status: "recheck"» на вказаний newStatus, Edit-точково:\n` +
    `• target="basic" → поле basic тієї теми;  • target="detailed" → поле detailed;  • target="insert" → елемент масиву (hist/comp/math/proj) із file=вказаний.\n` +
    `Якщо на одній темі кілька "recheck" — заміняй ЛИШЕ вказаний target/file, інші не чіпай. Нічого поза переліком не міняй.\n` +
    `ПЕРЕЛІК: ${JSON.stringify(payload)}\nПоверни ok, count.`,
    { label: 'recheck→done/update', phase: 'Маніфест', model: 'opus', schema: REG_RET })
}

return { scouted: WORK.length, reviewed: REVIEWED.length, changed: nChanged, toRewrite: nRewrite }
