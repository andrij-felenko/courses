export const meta = {
  name: 'newtopics-round2',
  description: 'Друге коло: перевірити merge по СТАТТЯХ і вирішити move колегією з трьох',
  whenToUse: 'Після newtopics-judge.wf.js, коли треба надійніше за один вирок із назви.',
  phases: [
    { title: 'Merge', detail: 'по одному агенту на пару: читає статтю-ціль, каже — дубль чи ні' },
    { title: 'Move', detail: 'три незалежні судді на всі 17 тем, далі звіряємо' },
  ],
}

let _a = args
if (typeof _a === 'string') { try { _a = JSON.parse(_a) } catch (e) { _a = {} } }
_a = _a || {}
const ROOT = 'E:\\develop\\courses'
const DIR = `${ROOT}\\scripts\\_judge`

/* ---------- 1. MERGE: перечитати ---------- */
/* Перше коло судило з назви й слуга. Тут агент ЧИТАЄ статтю-ціль і питає інакше:
   чи справді нова тема нічого не додає до вже написаного. Там, де цілі ще нема на
   диску (сама щойно заведена), читати нічого — судимо з назв і сусідів, і агент
   мусить це сказати прямо, а не вдавати впевненість. */
phase('Merge')
const MERGE_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['id', 'verdict', 'reason'],
  properties: {
    id: { type: 'string' },
    verdict: { enum: ['merge', 'keep', 'unsure'] },
    covers: { type: 'boolean' },
    reason: { type: 'string' },
  },
}
const MERGE_IDS = _a.mergeIds || [
  'com-medium/antenna-diversity-systems', 'com-medium/masthead-poe-and-fiber',
  'sf-devices/alarm-flood-suppression-and-shelving', 'sf-ml/machine-ethics-safe-autonomy',
  'sys-dron/line-of-sight-stabilization', 'sys-dron/marine-steering-and-thrusters',
  'sys-dron/uav-flight-handover-protocol', 'sys-dron/whole-body-control',
]
const mergePrompt = (id) => `In ${DIR}\\pack2-merge.json find the ONE entry whose "id" is exactly «${id}».

A first pass, judging from titles alone, said this new topic duplicates an existing one
("target"). Check that properly.

• If "targetWritten" is true — READ the target article at the path in "targetFile". That is
  the ONLY article you may read. Then answer: does the written article ALREADY carry what
  the new topic's title promises, so that a separate article would repeat it?
• If "targetWritten" is false — the target is itself a newly queued topic with nothing
  written yet. Do NOT go looking for other files. Judge from the two titles and the chapter
  neighbours in "siblings", and say so in the reason.

Verdicts:
• merge  — the same concept; a second article would restate it. "covers": true.
• keep   — genuinely different: it names a mechanism, case or layer that the target does not
           cover, and a reader could want exactly it on its own.
• unsure — the material does not settle it.

Be concrete about WHAT is or is not covered — no verdict on a general feeling of closeness.
Two names can look alike and mean different things; the opposite happens too.

"reason" — UKRAINIAN, one clause, at most 18 words. Return id verbatim.`

const mergeOut = await pipeline(MERGE_IDS, (id) =>
  agent(mergePrompt(id), { label: `merge:${id.split('/')[1].slice(0, 26)}`, phase: 'Merge', schema: MERGE_SCHEMA, effort: 'high' })
)

/* ---------- 2. MOVE: колегія з трьох ---------- */
/* Три судді бачать те саме й вирішують незалежно. Перше коло тут провалилося не
   через слабке судження, а через мій промпт: він дозволяв назвати ВИД замість книги,
   і дев'ять із сімнадцяти так і зробили. Тепер книга обирається з поіменного реєстру. */
phase('Move')
const MOVE_SCHEMA = {
  type: 'object', additionalProperties: false, required: ['verdicts'],
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false, required: ['id', 'targetBook', 'reason'],
        properties: {
          id: { type: 'string' },
          targetBook: { type: 'string' },
          chapterHint: { type: 'string' },
          confidence: { enum: ['high', 'low'] },
          reason: { type: 'string' },
        },
      },
    },
  },
}
const movePrompt = (n) => `Read ONE file: ${DIR}\\pack2-move.json — and nothing else.

It holds "books" (EVERY book of the corpus: slug, kind, title, its groups) and "topics"
(17 topics that a first pass judged to be in the wrong book). For each topic decide WHICH
BOOK it belongs in.

THE KINDS:
• sci — a law, a phenomenon, a principle: why the world is so.
• eng — how it is done: an algorithm, a method, an engineering pattern.
• com — how it crosses distance: signal, modulation, frame, protocol.
• hw — what kind of thing this is: a class of component and its behaviour.
• sys — a man-made system that HAS VERSIONS ("in which version?" is a sensible question).
• cat — a concrete object you can buy (a board, a module, a part number).
• course — a sequential course; NEVER a destination for an atom.

RULES:
1. "targetBook" MUST be a slug from "books", exactly as written there. Never a kind name,
   never a book you did not see in that list. This is where the first pass failed: it
   answered "eng", which is thirteen books, and decided nothing.
2. If NO existing book fits — say so: put "targetBook": "NONE" and explain in one clause
   what kind of book would be needed. Do not force a topic into a book that merely looks
   near. A new book is created only by the author, never by us.
3. If the topic in fact belongs where it already is, put "targetBook": "STAY".
4. "chapterHint" — optional, the group/chapter of the target book you would put it in.
5. "confidence": "high" only when the book is obvious from the kind boundary; otherwise "low".

"reason" — UKRAINIAN, one clause, at most 18 words, saying what makes that book the right
one (not merely what makes the current one wrong).

Judge all 17. Return ids verbatim. You are judge #${n} of three deciding independently;
do not try to guess what the others would say.`

const moveOut = await parallel([1, 2, 3].map((n) => () =>
  agent(movePrompt(n), { label: `move:суддя-${n}`, phase: 'Move', schema: MOVE_SCHEMA, effort: 'high' })
))

/* ---------- звід ---------- */
const votes = {}
for (const r of moveOut.filter(Boolean))
  for (const v of (r.verdicts || [])) {
    const e = votes[v.id] = votes[v.id] || { id: v.id, picks: [] }
    e.picks.push({ book: v.targetBook, chapter: v.chapterHint || '', conf: v.confidence || '', reason: v.reason })
  }
const move = Object.values(votes).map((e) => {
  const tally = {}
  for (const p of e.picks) tally[p.book] = (tally[p.book] || 0) + 1
  const best = Object.entries(tally).sort((a, b) => b[1] - a[1])[0]
  return { id: e.id, winner: best ? best[0] : null, votes: best ? best[1] : 0, of: e.picks.length, unanimous: best && best[1] === e.picks.length, picks: e.picks }
})
const merged = mergeOut.filter(Boolean)
log(`Merge: ${merged.filter((m) => m.verdict === 'merge').length} підтверджено, ${merged.filter((m) => m.verdict === 'keep').length} спростовано · Move: одностайних ${move.filter((m) => m.unanimous).length}/${move.length}`)

return { merge: merged, move, moveJudges: moveOut.filter(Boolean).length }
