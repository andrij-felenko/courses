export const meta = {
  name: 'newtopics-inserts',
  description: 'Дописати як вставки ті теми, чий батько ВЖЕ написаний — файл вставки + лінк у прозі батька',
  whenToUse: 'Після суду, коли вирок insert і батьківська стаття існує на диску.',
  phases: [{ title: 'Вставки', detail: 'один агент на вставку: читає батька, пише вставку, вшиває лінк' }],
}

let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
_a = _a || {}
const ROOT = 'E:\\develop\\courses'
const PACK = `${ROOT}\\scripts\\_judge\\pack2-insert.json`
const IDS = _a.ids || []
if (!IDS.length) { log('нема ids'); return { done: 0 } }

const SCHEMA = {
  type: 'object', additionalProperties: false, required: ['id', 'ok', 'note'],
  properties: {
    id: { type: 'string' }, ok: { type: 'boolean' },
    file: { type: 'string' }, type: { enum: ['hist', 'comp', 'math', 'proj', 'api'] },
    words: { type: 'number' }, linked: { type: 'boolean' }, note: { type: 'string' },
  },
}

/* Агент не читає канон: тип вставки, смуга обсягу й синтаксис лінка — тут, і це все,
   що йому треба. Канон коштував би ~15 тис. вхідних токенів на кожного. */
const RULES = `
INSERT TYPES (pick the ONE that fits the material):
• hist — how the idea was born and evolved: the problem that forced it, the dead ends.
• comp — a generalised class of device/chip: principle, pinout, hook-up, class pitfalls.
• math — the mathematical companion: NOT a dry academic proof, but the derivation that
  makes the mechanism click, with the meaning of every symbol.
• proj — algorithm / code / implementation: task → idea → working code → traps. Not a bare
  snippet with two comments.
• api  — the structural reference: calls, fields, flags, parameters, tables.

FORM: the file starts with an H1 (an emoji is allowed: «# 📜 Назва»); the title and the
first sentence themselves say WHAT this is and WHY. Length 400–5000 words of prose, and it
must carry weight — not a retelling of the parent article, not banality.

LANGUAGE: the prose is UKRAINIAN, living and precise. No russicisms, no calques, no
officialese, one term per concept.
`

phase('Вставки')
const prompt = (id) => `In ${PACK} find the ONE entry whose "id" is exactly «${id}».

This was queued as a separate TOPIC, but a judge ruled it is really a sub-step / mode /
derivation belonging INSIDE its parent article. Turn it into an insert of that parent.

STEP 1 — read the parent article: the path is in "parentFile". Read it fully. That is the
only article you read. You must know what it already says, so the insert ADDS instead of
repeating, and so you can hang the link where the thought actually needs it.

STEP 2 — write the insert file into the parent's folder, named "<type>-<name>.md" where
<name> is a short ASCII slug of your own choosing (2–4 words, hyphenated, specific enough
that nothing later collides with it).
${RULES}
STEP 3 — link it from the parent's PROSE, exactly once, at the place where the reader would
want it. Syntax, verbatim:
    [текст посилання](root:<book>/<parentSlug>/<type>-<name>.md)
The link text is normal Ukrainian words inside the sentence — not a bare file name, and not
a «див. також» dangling at the end of a paragraph. Change NOTHING else in the parent: no
restructuring, no rewriting of neighbouring sentences beyond the few words that carry the
link.

STEP 4 — count the prose words of what you wrote (Bash «wc -w» is fine as a rough check)
and report honestly: file, type, words, linked.

The topic entry itself is NOT yours to touch — the manifest is patched locally afterwards.
Do not edit any .json.

Return: id (verbatim), ok, file, type, words, linked, note (one clause, UKRAINIAN).`

const out = await pipeline(IDS, (id) =>
  agent(prompt(id), { label: `вставка:${id.split('/')[1].slice(0, 28)}`, phase: 'Вставки', schema: SCHEMA, effort: 'high' })
)

const ok = out.filter((r) => r && r.ok)
log(`Вставок написано ${ok.length}/${IDS.length}` + (ok.length ? ` · без лінка: ${ok.filter((r) => !r.linked).length}` : ''))
return { done: ok.length, of: IDS.length, results: out.filter(Boolean) }
