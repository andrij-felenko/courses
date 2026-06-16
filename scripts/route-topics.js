export const meta = {
  name: 'route-topics',
  description: 'Крок 4: маршрутизувати 908 наявних тем до галузей нових книг — терсна назва + порожнє посилання (origin). Агент на зріз інвентаря.',
  phases: [{ title: 'Маршрутизація', detail: 'агент прив\'язує теми зрізу до книга+галузь, пише out-файл' }],
}

const ROOT = 'E:/develop/courses'
const ASSIGN = [
  'emb-block-1', 'emb-block-2', 'emb-block-3', 'emb-block-4', 'emb-block-5', 'emb-block-6', 'emb-block-7', 'emb-block-x',
  'chemistry', 'math', 'components',
]

const GUIDE = `КУДИ МАРШРУТУВАТИ (8 книг-предметів; повна таксономія галузей — у ${ROOT}/scripts/_taxonomy.json):
• physics — фізичні явища й закони (заряд, поле, струм-як-фізика, магнетизм, ЕМ-хвилі, шум, напівпровідники-фізика, термо).
• electronics — прилади/схеми/компоненти/вимірювання/живлення/плати/СЕНСОРИ-як-пристрої.
• programming — архітектура ЕОМ (логічна), прошивка/МК/RTOS/драйвери/ОС, мови, мережеве/графічне ПЗ, периферія.
• algorithms — обчислювальні процедури: структури даних, графи, DSP-реалізація, керування-реалізація, ML, зір, планування, крипто-алгоритми, стиснення.
• communications — протоколи/шини/радіо-застосування/модуляція/антени/мережі-протоколи.
• math — математичні поняття (числа, аналіз, лінійна, статистика, перетворення-теорія).
• chemistry — хімія (для зрізу chemistry: вступні теми → найближча галузь дисципліни).
• philosophy — поки порожня, сюди НЕ маршрутувати.
ПРИНЦИП меж: явище→physics; прилад/сенсор→electronics; процедура/алгоритм→algorithms; прошивка/архітектура→programming; протокол/радіо→communications; математика→math.`

const RET = {
  type: 'object', additionalProperties: false, required: ['written', 'count'],
  properties: { written: { type: 'string' }, count: { type: 'number' }, note: { type: 'string' } },
}

phase('Маршрутизація')
const results = await pipeline(ASSIGN, (key) => agent(
  `${GUIDE}

Прочитай свій зріз тем: "${ROOT}/scripts/_route/${key}.json" (масив; кожна тема має origin, title, і chapter/section/sector-контекст).
Прочитай таксономію галузей: "${ROOT}/scripts/_taxonomy.json".

ЗАВДАННЯ: для КОЖНОЇ теми зрізу признач:
  • book — slug книги-предмета (physics/math/chemistry/electronics/programming/communications/algorithms);
  • branch — slug галузі В МЕЖАХ цієї книги (бери з таксономії; має існувати);
  • title — ТЕРСНА назва теми, 1-2 слова (з наявного title витисни суть: «Сила між зарядами: закон Кулона» → «Закон Кулона» або «Кулон»; «Родини діодів» → «Діоди»);
  • slug — ascii-kebab від title;
  • origin — лиши як є (мітка походження для перенесення файлів).
Нічого не загубити: КОЖНА тема зрізу має бути в результаті рівно раз.

Запиши результат-масив [{origin, book, branch, slug, title}] у файл "${ROOT}/scripts/_route/out-${key}.json" (інструментом Write, валідний JSON).
Поверни written="${key}", count=скільки тем, note (стисло, які книги-галузі вийшли).`,
  { label: `route:${key}`, phase: 'Маршрутизація', schema: RET }
).then(r => ({ key, ...(r || { count: 0 }) })))

const ok = results.filter(Boolean)
const total = ok.reduce((s, r) => s + (r.count || 0), 0)
ok.forEach(r => log(`  ${r.key}: ${r.count}`))
log(`РАЗОМ маршрутизовано: ${total}`)
return { assignments: ok.length, total, perAssign: ok.map(r => ({ key: r.key, count: r.count })) }
