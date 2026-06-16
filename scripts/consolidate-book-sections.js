export const meta = {
  name: 'consolidate-book-sections',
  description: 'Згрупувати дрібні розділи кожної книги у МЕНШЕ сильних розділів із підрозділами — зберігаючи всі області й точність, без filler.',
  phases: [
    { title: 'Групування', detail: 'експерт групує поточні розділи у ~8-14 сильних із підрозділами' },
    { title: 'Баланс',     detail: 'критик звіряє повноту (нічого не загублено), відсутність filler, рівновагу' },
  ],
}

const ROOT = 'E:/develop/courses'
const BOOKS = [
  { slug: 'physics',        title: 'Фізика' },
  { slug: 'math',           title: 'Математика' },
  { slug: 'chemistry',      title: 'Хімія' },
  { slug: 'electronics',    title: 'Електроніка' },
  { slug: 'programming',    title: 'Програмування' },
  { slug: 'communications', title: "Зв'язок" },
  { slug: 'algorithms',     title: 'Алгоритми' },
  { slug: 'philosophy',     title: 'Філософія' },
]

const RULES = `ПРАВИЛА КОНСОЛІДАЦІЇ:
• Ціль — МЕНШЕ розділів, але СИЛЬНІШИХ: кожен верхній розділ — велика, цілісна, самодостатня область предмета (зазвичай 8–14 розділів на книгу).
• ЗБЕРЕГТИ ТОЧНІСТЬ: кожен поточний (дрібний) розділ стає ПІДРОЗДІЛОМ і потрапляє РІВНО в один сильний розділ. Нічого не загубити, нічого не дублювати, нічого не вигадати нового понад наявне.
• ЖОДНОГО filler: заборонені розділи «Інше», «Різне», «Основи», «Додатково», «Загальне». Кожен сильний розділ — конкретна змістовна область.
• Межі чіткі (MECE), ваги розділів приблизно рівні; групуй за природною спорідненістю, у логічному порядку.
• Назви — українською, ясні; slug — ascii-kebab. Сильному розділу дай scope (1 речення).`

const GROUPS = {
  type: 'object', additionalProperties: false, required: ['groups'],
  properties: { groups: { type: 'array', items: {
    type: 'object', additionalProperties: false, required: ['slug', 'title', 'members'],
    properties: {
      slug: { type: 'string' }, title: { type: 'string' }, scope: { type: 'string' },
      members: { type: 'array', items: {
        type: 'object', additionalProperties: false, required: ['slug', 'title'],
        properties: { slug: { type: 'string' }, title: { type: 'string' }, scope: { type: 'string' } } } },
    } } } } }

function groupPrompt(b) {
  return `${RULES}\n\nТи — методист книги-предмета «${b.title}».\nПрочитай файл "${ROOT}/book/${b.slug}/manifest.js" — у ньому масив поточних розділів (поле sections: кожен має slug, title, scope). Їх ЗАБАГАТО.\nЗгрупуй ці поточні розділи у МЕНШЕ сильних розділів (ціль 8–14). Кожен сильний розділ містить members — ті поточні розділи, що в нього входять (як підрозділи). Усі поточні розділи мусять потрапити РІВНО в один сильний; жоден не загубити й не продублювати. Збережи slug/title кожного підрозділу як є.\nПоверни groups (slug, title, scope, members:[{slug,title,scope}]).`
}

function critiquePrompt(b, draft, count) {
  return `${RULES}\n\nКнига «${b.title}». У ВХІДНОМУ manifest було ${count} поточних розділів. Ось чернетка консолідації:\n${JSON.stringify(draft.groups.map(g => ({ g: g.title, members: g.members.map(m => m.slug) })), null, 1)}\n\nЗвір як критик: (1) ПОВНОТА — чи всі ${count} поточних розділів увійшли РІВНО раз (порахуй; познач загублені/подвоєні); (2) FILLER — чи немає розділу-смітника; (3) РІВНОВАГА Й СИЛА — чи розділи цілісні й приблизно рівні, чи їх 8–14; (4) межі чіткі. Виправ вади.\nПоверни ПОВНУ виправлену консолідацію groups (той самий формат), щоб усі ${count} підрозділів були збережені.`
}

phase('Групування')
log(`Консолідую розділи ${BOOKS.length} книг`)

const results = await pipeline(
  BOOKS,
  (b) => agent(groupPrompt(b), { label: `group:${b.slug}`, phase: 'Групування', schema: GROUPS }).then(d => ({ b, draft: d })),
  (x) => {
    if (!x || !x.draft) return null
    const count = x.draft.groups.reduce((s, g) => s + (g.members ? g.members.length : 0), 0)
    return agent(critiquePrompt(x.b, x.draft, count), { label: `balance:${x.b.slug}`, phase: 'Баланс', schema: GROUPS })
      .then(c => ({ slug: x.b.slug, title: x.b.title, groups: (c && c.groups && c.groups.length) ? c.groups : x.draft.groups }))
  }
)

const books = results.filter(Boolean)
books.forEach(b => log(`  ${b.slug}: ${b.groups.length} сильних розділів, ${b.groups.reduce((s, g) => s + (g.members ? g.members.length : 0), 0)} підрозділів`))

return { books: books.map(b => ({ slug: b.slug, title: b.title, groups: b.groups })) }
