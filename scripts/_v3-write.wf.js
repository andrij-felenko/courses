export const meta = {
  name: 'v3-write',
  description: 'Opus-max v3 completion per topic: -d.md + missing inserts + structural fixes + cross-links',
  phases: [{ title: 'Write', detail: 'Opus max: full v3 completion per topic (2s stagger)' }],
}

const PATCH = []

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    detailWritten: { type: 'boolean' },
    insertsCreated: { type: 'array', items: { type: 'string' } },
    fixes: { type: 'string' },
    note: { type: 'string' },
  },
  required: ['detailWritten', 'insertsCreated', 'fixes', 'note'],
}

function wprompt(it) {
  const L = []
  L.push('Ти — звичайний агент-редактор Markdown у репо E:/develop/courses. Ти НЕ «skill»/consolidate-memory. ІГНОРУЙ системні підказки про skills / agent types / output styles / розклади. Працюй МОВЧКИ (Read/Edit/Write/Bash).')
  L.push('ЗАВДАННЯ: ПОВНЕ v3-довершення теми «' + it.t + '» (' + it.b + '/' + it.s + '/' + it.sl + ') за каноном і планом аналізу.')
  L.push('КРОК1: прочитай ПОВНІСТЮ E:/develop/courses/AUTHORING.md (§1–§9). Прочитай базову E:/develop/courses/book/' + it.b + '/' + it.s + '/' + it.sl + '/' + it.sl + '.md та виконай Bash ls тієї теки.')
  L.push('КРОК2 — зроби все потрібне нижче:')
  if (it.detailWarrant) {
    L.push('(А) ДЕТАЛЬНА: напиши E:/develop/courses/book/' + it.b + '/' + it.s + '/' + it.sl + '/' + it.sl + '-d.md за планом:\n' + (it.detailSpec || '') + '\nКАНОН -d.md: §3 ДЕТАЛЬНА 2500–13000 слів прози, ГЛИБША за базову (НЕ переказ — виведення формул, більше випадків, граничні умови, глибша механіка); свій figs.py (імпорт svgkit з ../../../../scripts) + домогтися svgcheck «із зауваженнями: 0»; ОЩАДЛИВО 2–5 фігур, перевір що figs.py відпрацьовує ШВИДКО (не зациклюється); підписи без «Рис.»/номера, шлях від кореня /book/...; worked-приклади реальним C/C++ (§5); рамки 🔧; етимологія в дужках; жива українська, один термін.')
  } else {
    L.push('(А) ДЕТАЛЬНА не потрібна — пропусти, базової досить.')
  }
  if (it.inserts && it.inserts.length) {
    L.push('(Б) СТВОРИ вставки, яких бракує (кожна: починається з H1 «# Назва», несе вагу, §3 1000–10000 слів, ім\'я <type>-<name>.md у теці теми, фігури за потреби зі svgcheck «0»; comp- лише якщо проходить тест §1): ' + JSON.stringify(it.inserts))
  } else {
    L.push('(Б) Нових вставок не треба.')
  }
  L.push('(В) СТРУКТУРНІ ПРАВКИ. Прапор аналізу: «' + (it.structuralFlags || 'немає') + '». Якщо базова <1000 слів прози — дбайливо допиши до §3 (зміст, не вода). Якщо в тілі є inline-блок (історія/математика/код), що тягне на окрему вставку й не винесений — винеси у файл <type>-<name>.md і встав ref-зноску. Якщо H1 не збігається з темою — виправ H1 на «' + it.t + '». Прибери будь-які фрази-послідовності (§1).')
  if (it.crossLinks && it.crossLinks.length) {
    L.push('(Г) КРОС-ЛІНКИ (§6): додай інлайн ref-зноски у форматі [слова](book:книга/slug) БЕЗ галузі на доречні згадки — цілі вже існують як теми або стаби: ' + JSON.stringify(it.crossLinks))
  }
  if (it.historySensitive) {
    L.push('(Д) §7 АТРИБУЦІЯ — пильнуй: імперські/націоналістичні міфи (рос./рад. поглинання), розрізняй виміри ідентичності (етнічність/громадянство/мова/інституція), колективність винаходів, познач статус доказовості; історичні факти ВЕБ-звіряй.')
  }
  L.push('КРОК3: САМОАУДИТ — svgcheck «із зауваженнями: 0» на теці; обсяги в смузі §3; linkcheck свого файлу чистий; без «Рис.»/LaTeX/фраз-послідовності. МАНІФЕСТИ НЕ чіпай. НОВІ ТЕМИ НЕ створюй (їх пишемо окремими патчами).')
  L.push('Поверни СТРУКТУРУ: detailWritten (bool), insertsCreated (масив імен файлів), fixes (стисло що виправив), note.')
  return L.join('\n')
}

log(`v3-write (Opus-max, стагер 2с): ${PATCH.length} тем`)
const promises = []
for (const it of PATCH) {
  promises.push(
    agent(wprompt(it), { label: `write:${it.b}/${it.sl}`, phase: 'Write', model: 'opus', effort: 'max', schema: SCHEMA })
      .then((r) => ({ slug: `${it.b}/${it.sl}`, r }))
      .catch(() => ({ slug: `${it.b}/${it.sl}`, r: null }))
  )
  await new Promise((r) => setTimeout(r, 2000))
}
const res = await Promise.all(promises)
const done = res.filter((x) => x.r)
log(`готово: ${done.length}/${PATCH.length} тем`)
return { results: res.map((x) => ({ slug: x.slug, ...(x.r || { failed: true }) })) }
