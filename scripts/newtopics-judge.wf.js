export const meta = {
  name: 'newtopics-judge',
  description: 'Оцінити теми, заведені ревізією Antigravity: чи в тему, чи варті окремої статті',
  whenToUse: 'Після newtopics-audit.js + newtopics-judge-prep.js, перед тим як лишати нові теми в черзі.',
  phases: [{ title: 'Суд', detail: 'один агент на пакет: вирок на кожну тему' }],
}

/* Агент НЕ читає ні репо, ні канон — усе потрібне лежить у його пакеті (нові теми,
   сусіди по розділу, локальні ознаки). Канон коштував би ~15 тис. вхідних токенів
   на агента й нічого не додав би: судимо межі видів і роздрібнення, а це двадцять
   рядків правил. Читати заборонено й тому, що інакше агент піде гуляти корпусом. */
let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
_a = _a || {}
const ROOT = 'E:\\develop\\courses'
const DIR = _a.dir || `${ROOT}\\scripts\\_judge`
const PACKS = _a.packs || ['sys-dron', 'ph-mechanics', 'hw-motion', 'sf-algorithms', 'com-signal', 'sf-devices',
  'hvist-cat', 'hvist-com', 'hvist-eng', 'hvist-hw', 'hvist-sci', 'hvist-sys']

const RULES = `
WHAT EACH KIND OF BOOK IS FOR (the boundary you judge against):
• sci — a law, a phenomenon, a principle. Why the world is the way it is.
• eng — how it is done: an algorithm, a pattern, an engineering method.
• com — how it crosses distance: signal, modulation, frame, protocol.
• hw — what kind of thing this is: a component class and its behaviour.
• sys — a man-made system that HAS VERSIONS. If "in which version?" is a sensible
  question, it belongs here; if it is a law or a principle, it does not.
• cat — a concrete object you can buy: a board, a module, a part number.

WHAT DESERVES A TOPIC OF ITS OWN (the anti-fragmentation rule of this repo):
• A topic is a self-standing engineering concept WITH ITS OWN READER — someone who
  would search for exactly this and read it alone.
• NOT a topic: an intermediate mathematical transformation, a local change of
  coordinates, a sub-step of an algorithm, one field of a protocol, one mode of a
  device. Those are inserts (math-/proj-/api-) or sections inside the parent article.
• NOT a topic: a re-slicing of a concept that already exists under another name.
• A book article is an ATOM: self-contained, no order, no "as we saw earlier".
`

const SCHEMA = {
  type: 'object', additionalProperties: false, required: ['verdicts'],
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['id', 'verdict', 'reason'],
        properties: {
          id: { type: 'string' },
          verdict: { enum: ['keep', 'merge', 'move', 'insert', 'drop', 'unsure'] },
          target: { type: 'string' },
          reason: { type: 'string' },
        },
      },
    },
  },
}

phase('Суд')
const prompt = (name) => `Read ONE file and judge what is in it: ${DIR}\\pack-${name}.json

Do NOT read anything else. Not the repo, not the canon, not any article. Everything you
need is in that file. If the file alone does not settle a case, the verdict is "unsure" —
that is a real, expected answer, not a failure. Do not guess to look decisive.

The file has:
• "chapters" — the chapters these new topics landed in, each with "existing": the topics
  ALREADY in that chapter, as "slug — title". This is the neighbourhood you judge against.
• "topics" — the NEW ones, each with: id, book, chapter, slug, title,
  "mentionsInBookProse" (in how many of the book's .md files the two rarest stems of the
  title co-occur — a WEAK hint: 0 can mean the concept is absent from what is written, but
  in a small book it means little), "similarNearby" (mechanically detected look-alikes —
  a hint, not a verdict; a nested slug is often a legitimately different concept),
  "localFlags".
${RULES}
For EVERY topic in "topics" return exactly one verdict:
• keep   — a self-standing concept, in the right book, worth its own article.
• merge  — the same concept already exists here; put the existing slug in "target".
• move   — a real topic, but the WRONG KIND of book; put the target book slug in "target"
           (choose from the kinds above; name the book only if you are sure it exists).
• insert — real material, but a sub-step / transformation / one field or mode: it belongs
           inside a parent article as an insert; put the parent slug in "target".
• drop   — not material for this corpus at all.
• unsure — the file does not let you decide.

"reason" — ONE clause, UKRAINIAN, at most 15 words, saying WHY. No restating the title.
Judge every topic; return them all; ids verbatim from the file.`

const results = await pipeline(
  PACKS.map((p) => p),
  (p) => agent(prompt(p), { label: `суд:${p}`, phase: 'Суд', schema: SCHEMA, effort: 'high' })
    .then((r) => (r ? { pack: p, verdicts: r.verdicts || [] } : { pack: p, verdicts: [], failed: true }))
)

const all = results.filter(Boolean).flatMap((r) => r.verdicts.map((v) => ({ ...v, pack: r.pack })))
const by = {}
for (const v of all) by[v.verdict] = (by[v.verdict] || 0) + 1
log(`Вироків ${all.length}: ` + Object.entries(by).map(([k, n]) => `${k} ${n}`).join(' · '))

return {
  total: all.length,
  counts: by,
  failedPacks: results.filter((r) => r && r.failed).map((r) => r.pack),
  verdicts: all,
}
