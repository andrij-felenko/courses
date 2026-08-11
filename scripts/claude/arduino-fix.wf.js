export const meta = {
  name: 'arduino-fix',
  description: 'Розардуїнити приклади: пояснення від загальної електроніки + код під ESP-IDF/STM32 поруч з Arduino',
  whenToUse: 'Коли scripts/arduinocheck.js показує файли «ЛИШЕ ARDUINO» / «ВКЛАДКА-ОДИНАК» / «ПРОЗА ЧЕРЕЗ ARDUINO».',
  phases: [
    { title: 'Черга', detail: 'один дешевий агент читає scripts/_arduino-only.json і віддає список' },
    { title: 'Код', detail: 'до кожного Arduino-блоку — вкладки ESP-IDF і STM32 HAL + розардуїнена рамка пояснення' },
    { title: 'Проза', detail: 'файли без коду: пояснення від загальної електроніки, Arduino — як приклад' },
    { title: 'Контроль', detail: 'локальний arduinocheck по корпусу' },
  ],
}

/* ---------------------------------------------------------------------------
   Чому правила ІНЛАЙНОМ, а не читанням AUTHORING.write.en.md: канон — ~15 тис.
   вхідних токенів, і його читав би КОЖЕН зі 172 агентів (≈2.6 млн лише на це).
   Тут завдання вузьке й повністю описується двадцятьма рядками — беремо їх.
   --------------------------------------------------------------------------- */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
_a = _a || {}
const ROOT = 'E:\\develop\\courses'
const CONCURRENCY = _a.concurrency || 4
const LIMIT = _a.limit || 0                       // 0 = усі
const ABORT_ON_LIMIT = _a.abortOnLimit !== false
let WALL = null

const RULES = `
PLATFORM RULE (this is the whole point of the task):
• An MCU example is never "for Arduino". Arduino is ONE embodiment, not the subject.
• The explanation leads from GENERAL ELECTRONICS: first what is true for any MCU (an
  interrupt-capable pin, a timer, a bus, a register, a pull-up), and only then what it is
  called in a particular environment. A reader on STM32 or ESP32 must recognise their own
  task, not translate it from someone else's.
• Arduino is NOT deleted. It stays, usually first — it is often the clearest way in.
  The fix is that it must not be the ONLY one.
• Fence tags name the PLATFORM, not the language: \`arduino\`, \`esp-idf\`, \`stm32\`
  (also \`stm32-ll\`, \`zephyr\`, \`pico-sdk\`, \`avr\`, \`micropython\`). Three tabs tagged
  \`c\` would all render as "C" and tell the reader nothing.

MINIMAL-EDIT RULE (equally important — this is a FINISHED article, not a draft):
• Touch ONLY what is Arduino-bound. Prose that is already platform-neutral stays
  byte-for-byte identical.
• Do NOT restructure, do NOT re-order sections, do NOT rewrite the opening, do NOT touch
  figures, image links, <preknowlist>, or cross-links.
• Do NOT inflate the article. The added tabs are the same size as the Arduino block.
`

/* ---------- 1. Черга ---------- */
phase('Черга')
const QUEUE_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['code', 'prose'],
  properties: {
    code: { type: 'array', items: { type: 'string' } },
    prose: { type: 'array', items: { type: 'string' } },
  },
}
const q = await agent(
  `Read ${ROOT}\\scripts\\_arduino-only.json (a JSON array of objects with fields "file" and "verdict").\n` +
  `Return two lists of the "file" values, verbatim, no path rewriting:\n` +
  `  code  — every entry whose verdict is "only" OR "tabs"\n` +
  `  prose — every entry whose verdict is "prose"\n` +
  `Do not read anything else. Do not omit or truncate entries.`,
  { label: 'черга', phase: 'Черга', schema: QUEUE_SCHEMA, effort: 'low' }
)
if (!q) { log('Черга не зібралася — виходжу'); return { aborted: true, reason: 'queue' } }

let CODE = q.code || [], PROSE = q.prose || []
if (LIMIT) { CODE = CODE.slice(0, LIMIT); PROSE = PROSE.slice(0, Math.max(0, LIMIT - CODE.length)) }
log(`Черга: код ${CODE.length} · проза ${PROSE.length} (пул ${CONCURRENCY})`)

/* ---------- спільний виклик із стіною ліміту ---------- */
const isLimit = (e) => /session limit|usage limit|rate.?limit|quota/i.test(String((e && e.message) || e))
async function call(prompt, opts) {
  if (WALL) return null
  try { return await agent(prompt, opts) } catch (e) {
    if (!isLimit(e)) return null
    if (ABORT_ON_LIMIT) {
      if (!WALL) { WALL = opts.label; log(`⛔ СТІНА ЛІМІТУ на «${opts.label}» — нові агенти не стартують. Підняти: node scripts/arduinocheck.js`) }
      return null
    }
    return null
  }
}

const RESULT_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['ok', 'note'],
  properties: {
    ok: { type: 'boolean' }, note: { type: 'string' },
    proseEdits: { type: 'number' }, tabsAdded: { type: 'number' },
    skipped: { type: 'number' }, gateClean: { type: 'boolean' },
  },
}

/* ---------- 2. Код ---------- */
phase('Код')
const codePrompt = (f) => `FILE (edit in place): ${ROOT}\\${f.replace(/\//g, '\\')}

This article's runnable example exists ONLY for Arduino. Fix that, and nothing else.
${RULES}
STEP 1 — read the file.

STEP 2 — de-Arduino the FRAMING. Find sentences that state an Arduino-specific fact as if
it were the general truth ("вихід дає 5 В", "пін 2 вміє переривання", "у setup() налаштовуємо").
Rewrite so the general fact comes first and Arduino is named as the concrete case. Keep it
short — you are re-hanging sentences, not rewriting paragraphs.

STEP 3 — for EVERY Arduino code block, give it company:
  • wrap it in \`:::tabs\` … \`:::\` if it is not already inside such a group;
  • retag the Arduino fence as \`\`\`arduino ;
  • add \`\`\`esp-idf — ESP-IDF: gpio_config/gpio_set_level, esp_err_t, ESP_LOG*, FreeRTOS
    (xTaskCreate/vTaskDelay), driver headers (driver/gpio.h, driver/i2c.h, …);
  • add \`\`\`stm32 — STM32 HAL: HAL_GPIO_WritePin/ReadPin, HAL_Delay, HAL_I2C_*/HAL_SPI_*,
    handles (I2C_HandleTypeDef …). Use \`\`\`stm32-ll or bare registers instead when the point
    of the example is exactly the register level.
  • Each tab does THE SAME job, written the way that platform is ACTUALLY written — not a
    line-by-line transliteration of the sketch. Same length as the Arduino block.
  • CORRECTNESS OVER CLEVERNESS: right headers, right function names, right argument order.
    If unsure of an API, use the form you are sure of instead of inventing a plausible one.
  • SKIP a block if translating it is meaningless — it is not MCU code (a shell session, a
    formula, a data dump, a register table, pseudocode). Count those in "skipped".

STEP 4 — VERIFY yourself: run
    node ${ROOT}\\scripts\\arduinocheck.js ${f.split('/').slice(0, -1).join('/')}
This file must no longer be listed under "ЛИШЕ ARDUINO" or "ВКЛАДКА-ОДИНАК". If it still is,
fix and re-run. Report the honest outcome in gateClean — do NOT claim success you did not see.

The article's prose is UKRAINIAN; keep it Ukrainian, including comments inside the new code.
Return: ok, proseEdits, tabsAdded, skipped, gateClean, note (one line, Ukrainian).`

const codeResults = await pipeline(
  CODE.map((f, i) => ({ f, i })),
  ({ f, i }) => call(codePrompt(f), {
    label: `код:${f.split('/').slice(-1)[0]}`, phase: 'Код',
    schema: RESULT_SCHEMA, effort: 'high',
  }).then((r) => (r ? { ...r, file: f } : null))
)

/* ---------- 3. Проза ---------- */
phase('Проза')
const prosePrompt = (f) => `FILE (edit in place): ${ROOT}\\${f.replace(/\//g, '\\')}

This article has no Arduino code, but its EXPLANATION leans on Arduino and only on Arduino —
the reader on another MCU is left translating. Fix the framing. Nothing else.
${RULES}
STEP 1 — read the file.
STEP 2 — find every place where Arduino (or a board name: Uno, Nano, Mega, "скетч",
"Arduino IDE") carries the explanation, and re-hang it: the general electronics fact first,
Arduino named as one concrete environment. Where a name differs across environments, say so
in passing ("у Arduino це \`attachInterrupt\`, в ESP-IDF — \`gpio_isr_handler_add\`, у STM32 HAL
— \`HAL_GPIO_EXTI_Callback\`") — one clause, not a new section.
This is NOT a licence to add an empty promise like "на STM32 так само". Either name the
concrete difference or leave the sentence general.
STEP 3 — VERIFY: run
    node ${ROOT}\\scripts\\arduinocheck.js ${f.split('/').slice(0, -1).join('/')}
This file must no longer be listed under "ПРОЗА ЧЕРЕЗ ARDUINO". Report honestly in gateClean.

Ukrainian prose stays Ukrainian. Return: ok, proseEdits, gateClean, note (one line, Ukrainian).`

const proseResults = await pipeline(
  PROSE.map((f, i) => ({ f, i })),
  ({ f }) => call(prosePrompt(f), {
    label: `проза:${f.split('/').slice(-1)[0]}`, phase: 'Проза',
    schema: RESULT_SCHEMA, effort: 'medium',
  }).then((r) => (r ? { ...r, file: f } : null))
)

/* ---------- 4. Контроль (локальний, 0 токенів моделі на аналіз) ---------- */
phase('Контроль')
await call(
  `Run exactly these two commands and return their tail output verbatim in "note":\n` +
  `  node ${ROOT}\\scripts\\arduinocheck.js\n` +
  `  node ${ROOT}\\scripts\\linkcheck.js\n` +
  `Do not read or edit any file. Do not fix anything. ok=true if both ran.`,
  { label: 'контроль', phase: 'Контроль', schema: RESULT_SCHEMA, effort: 'low' }
)

const cOK = codeResults.filter((r) => r && r.ok), pOK = proseResults.filter((r) => r && r.ok)
const dirty = [...cOK, ...pOK].filter((r) => r.gateClean === false).map((r) => r.file)
log(`Код ${cOK.length}/${CODE.length} · проза ${pOK.length}/${PROSE.length}` + (dirty.length ? ` · гейт не чистий у ${dirty.length}` : ''))

return {
  aborted: !!WALL, wall: WALL || undefined,
  code: { done: cOK.length, of: CODE.length },
  prose: { done: pOK.length, of: PROSE.length },
  tabsAdded: cOK.reduce((s, r) => s + (r.tabsAdded || 0), 0),
  skippedBlocks: cOK.reduce((s, r) => s + (r.skipped || 0), 0),
  gateDirty: dirty,
  failed: [...codeResults, ...proseResults].filter((r) => !r || !r.ok).length,
}
