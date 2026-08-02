# Writing Canon v6 (single canon for all books)

> Rules are in English; article/insert OUTPUT is written in **Ukrainian** (see §4 «Living Ukrainian»).

Writing rules are **here**. Plan/queue/statuses — in the book/course manifest (schema — §2). Scripts — in `scripts/`.

> **v5 → v6 (RULE changes; manifest schema UNCHANGED):** (1) every **new** article begins with a collapsed prerequisites block `<preknowlist>` — "what to know before reading" (§6); (2) `svgcheck.py` now also catches **text overlap** onto other text/lines (§5); (3) **code language — by domain, not always C/C++**; the same example in 2–5 languages — as `:::tabs` tabs (switcher on top, syntax highlighting) (§5); (4) **a new kind of book — `reference/` (reference books on man-made systems)**: behaves like `book/`, the same manifest schema with `type:"reference"`, linked with the `book:` prefix (§1–§2); (5) **the basic version — a hard rule on size and language**: at least **twice shorter** than its detailed (and 540–1440 words), written in **simpler language** without losing the meaning (§3). (6) **all word bands cut by 10%** (§3/§8) and **~10% fewer inserts** — the spin-out threshold is raised one notch (§3). **We don't touch what's already written** — apply only to new articles (and when old ones are next rewritten).

## §1 Structure — four folders

**`book/` — subject books.** An article sits in a **subject section** (manifest field `sections`), **without numbering**. **An article = EXACTLY ONE topic** (one concept, an **atom**). An article is **parallel** to all others: **self-contained, assumes nothing, reads on its own in any order**. It may link to another, but **uses no sequence phrases** («попередній/наступний розділ», «як ми бачили», «далі побачимо», «пригадаймо», «ми це проходили») and **does not rely on "already known"** — there is no order in the book. The `basic`/`detailed` versions — **both standalone**, differing only in depth (§3).

8 books: `electronics` (Electronics), `physics` (Physics), `math` (Mathematics), `programming` (Programming), `algorithms` (Algorithms), `communications` (Communications), `chemistry` (Chemistry), `philosophy` (Philosophy).

**`guide/` — instructional books (courses).** A course is a **sequence of steps** that **accumulates knowledge**: each step **builds on what came before, assumes prior knowledge, and deepens gradually**. This is **not a set of topics but a thread of immersion**; steps are numbered Module·Chapter·Step — **from the ORDER in the manifest** (not from a number in the slug). Each step is one of two:
- **`ref`** — a link to an existing `book/` article, **when the standalone atom covers the step as-is and nothing needs adding**;
- **the course's own article** — when a **cumulative angle** is needed: the same topic (or a combination of several), but presented **building on the previous steps and preparing the next ones**. We unpack it more deeply for learning, embed needed `book/` topics **as a popup insert** (§6), add **own inserts** (history/math/examples). File: `guide/<course>/<module-slug>/<slug>/<slug>.md` (folders by name, no numbers), together with its inserts and `img/`.

**IRON RULE (book ↔ guide), obeyed 100%:** if material **assumes "already known", makes sense only in sequence, or deepens step-by-step** — it's **`guide`, NEVER `book`**. If it's **a self-contained atom that reads fully on its own** — it's **`book`**. One topic may exist twice: standalone in `book/` and as a cumulative step in `guide/` (via `ref` or an own article). **Never put sequential/cumulative material in `book/`.**

Per-step decision: a standalone book atom covers it as-is → `ref`; need a cumulative angle / combination / bridge between steps → **the course's own article**. Build **only backward**; carry the thread **naturally, without forcing** it with filler connective sentences. `book/` articles are **not rewritten** for a course. A `ref` step may point into `catalog/` and `reference/` as well — all three kinds live in the same `__BOOKS__` (the first ref segment is the book's slug). 5 courses: `embedded`, `embedded-ultra`, `basic-chemistry`, `progarch`, `unix`.

**`catalog/` — catalog books.** Grouped **descriptions of concrete objects** (parts; later broader too). An entry **describes a concrete thing** rather than building a scientific idea. Behaves **like `book/`** (no order, basic+detailed versions, inserts `hist-`/`math-`/`proj-` — but **not** `comp-`, since the catalog itself is the component).

**Catalog families** — each a separate book `catalog/<family>`, a flat list of objects:
- **`sensors`** — sensors and measurement modules (including input/HMI: buttons, encoders, joysticks);
- **`power`** — power: regulators, converters, drivers, relays, charging, adapters;
- **`connect`** — radio and communications (data-transmission modules, RFID, IR);
- **`boards`** — compute boards (SBC/MCU/FPGA/flight) and expansion modules (memory, displays, storage, shields);
- **`actuators`** — actuation and signaling: motors, servos, steppers, fans, LEDs/buzzers/lasers;
- **`instruments`** — lab instruments and accessories (measurement, generation, ESD, prototyping, fabrication);
- **`components`** — generic passives and consumables: resistors/capacitors/transistors, connectors, cables, mechanics, solder.

**Where to place:** by the object's **primary function** (what it does). A bare chip — into the family closest by function. Create a new family **only** when an object fits none of the existing ones. (Create a family-book as needed — when the first object appears.)

**`reference/` — reference books.** They describe **a system or technology made by people** — an operating system, a language and its standards, a tool, a format, a protocol stack. This is **not a branch of science**: there is no "how the world is built" here, there is "how this thing is built and how to use it". Behaves **like `book/`**: sections (`sections`) → topic-atoms (`topics`), **no order and no numbering**, `basic`/`detailed` versions, the same inserts, the same manifest schema (§2). Opened by the reader as `read.html?book=<slug>`, linked with the **`book:`** prefix (there is no separate `reference:` prefix — same as for the catalog).

**book ↔ reference — where the line runs.** Ask **whether the topic would exist without the people who made it**:
- **`book/`** — the subject of **science or engineering theory**: a law, a phenomenon, a principle, an algorithm, a pattern. The truth doesn't depend on a version or a vendor (Ohm's law, CRC, a B-tree, the scheduler as an idea).
- **`reference/`** — the subject of **a concrete man-made system**: something someone designed, which has versions, releases, standards, syntax and proper names (POSIX signals, `std::move`, CMake target properties). Ask "in which version?" — if the question makes sense, it's `reference/`.
- Borderline material goes in **twice**: the principle into `book/`, its embodiment in the system into `reference/`, and they link to each other.
- **Not to be confused with `catalog/`:** the catalog describes **a thing you can buy** (a board, a module, a part); a reference book — **an intangible system** (an OS, a language, a tool).

5 reference books: `unix-linux` (Unix and Linux), `cpp-standards` (C++ standards), `build-systems` (Build systems), `media-vision` (GStreamer and OpenCV), `qgroundcontrol` (QGroundControl).

**Qt/QML — deliberately outside the corpus.** Neither a separate book nor topics: in `reference/qgroundcontrol` we describe the subsystems of the application itself (Vehicle, FactSystem, links, plan, map, video), not the framework they stand on. The rule is permanent, not temporary.

**`comp-` (insert) ↔ `catalog/` — mandatory decision procedure.** For each device/unit ask three questions in turn:
1. Can you **fully explain this thing without naming any concrete product, model, family, or part number** — by the operating principle alone?
2. Is this description (behavior, purpose, way of hooking it up) **the same** for any manufacturer and any implementation?
3. Does the behavior **follow directly from the science of one specific article** as its deepening?

- **All three "yes" → `comp-<name>.md` beside that article** (generalized, no part numbers — typical pinout/wiring, typical class-wide pitfalls).
- **Any "no" → `catalog/`**: the thing is defined by a concrete product/model/part number, and its details are specific to it and not derivable from the general principle.

Check test: if versions from different manufacturers would need **different articles** — it's `catalog/` (an article per product); if **one** article covers all implementations — it's `comp-`.

## §2 Naming, numbering, manifest

**Naming — slug-only** (ASCII, **no numbers**): `book/<book>/<section>/<slug>/<slug>.md`; likewise `catalog/…`, `reference/…`, `guide/…`. Detailed — `<slug>-d.md`; inserts — `<type>-<name>.md`. Slug collisions — with a minimal qualifier.

**Numbering:** `book/`, `catalog/` and `reference/` — **no numbers** (not in folders, not in text, not in figure captions). `guide/` **is numbered** Module · Chapter · Step — **from the ORDER of elements in the manifest** (the engine counts from position; not from a number field, not in the slug), so inserting a new one **does not break** numbering; a module without chapters — Module · Step.

**The manifest is the single source** of navigation, plan, queue, statuses. **One manifest per book/course**; we don't invent new fields outside the schema.

**book** — `book/<book>/manifest.js`, registers `window.__BOOKS__.push({…})`:
```js
{ type:"book", slug, title,
  sections:[ { slug, title, scope,              // section = subject section
    topics:[ { slug, title,
               basic:    { status },            // basic version — its OWN status (§9)
               detailed: { status },            // detailed version — its OWN status (§9)
               hist:[ {file:"hist-<name>.md", status} ],   // 📜 inserts — array per type
               comp:[ {file:"comp-<name>.md", status} ],   // 🔌 inserts
               math:[ {file:"math-<name>.md", status} ],   // 🧮 inserts
               proj:[ {file:"proj-<name>.md", status} ],   // ⚙️ inserts
               api:[ {file:"api-<name>.md", status} ] } ] } ] }   // 📋 inserts
```
**catalog** — `catalog/<book>/manifest.js`, **the same schema** with `type:"catalog"` (without the `comp` array).

**reference** — `reference/<book>/manifest.js`, **the same schema** with `type:"reference"`; pushes into the same `window.__BOOKS__`, `section` = a section of the reference book (not a "branch of science"), the remaining fields and statuses — as in book. The registry — `window.REFERENCE_BOOKS` in `books-index.js`.

**guide** — `guide/<course>/manifest.js`, registers `window.__GUIDES__.push({…})`. Schema v6 (form unchanged from v5) — **modules → chapters → steps**; **order in the arrays = numbering** (Module i · Chapter i.j · Step i.j.k; a module without chapters — Module i · Step i.j), which the engine counts from position — we hardcode numbers nowhere, inserting a new step doesn't break numbering (the `n` field is purely informational):
```js
{ type:"guide", slug, title,
  modules:[ { n, slug, title, scope:"",            // MODULE (slug without number; keep scope:"" — a module-row marker for the scout scripts)
    chapters:[ { title, steps:[                    // CHAPTER — title only (numbered by position within the module)
      { slug, title, basic:{status}, detailed:{status},             // course's own article (shape as book)
        hist:[…], comp:[…], math:[…], proj:[…], api:[…] }
    | { ref:"<book>/<section>/<slug>", title } ] } ] } ] }           // OR a pointer-step to a book article (3 segments)
```
A step is **either the course's own article** (basic/detailed/inserts, statuses §9; file `guide/<course>/<module-slug>/<slug>/<slug>.md`, folders by NAME without numbers — **the step's folder lives in its module's folder**, so moving a step between modules = `git mv` of the folder + fixing the absolute `/guide/...` figure paths), **or a `ref`** to a book atom (when a standalone covers the step). Numbering lives **only** in the manifest order.
Fields: **each version (`basic`, `detailed`) has its own `status`** (enum §9); a version is **available to the reader ⟺ its status is `done`**. The `hist`/`comp`/`math`/`proj`/`api` arrays — inserts by type, element = `{file, status}`. Note: a `ref` in the guide MANIFEST — **3 segments `<book>/<section>/<slug>`** (the engine uses the first + last segments); `book:`/`guide:` links IN ARTICLE TEXT — **2 segments** as before (§6). The legacy `sections→topics` form (2-segment refs) is kept by the engine and scripts as a fallback; **all courses are already in the current form**, and we write new content only in it.

## §3 Versions and inserts

**Two versions of completeness** (completeness is in the file name). This describes the **character** of a version — how to think about it — and is **NOT** a template section for the text (no headings like «Ціль» etc.):
- **`<slug>.md` — basic.** A **very short** text that gives **a sense of what the topic is**: read in ~half a minute — you have the picture, enough to grasp the essence. One core, fast. **Fewer examples**; relies on **fewer inserts** (≈half as many as the full account — **except the historical `hist-`**, apt here too). **540–1440 words AND at least TWICE SHORTER than its detailed** (the hard size rule below).
- **`<slug>-d.md` — detailed.** **The full version — sit down and understand it completely, no gaps.** This is **NOT** an overload of terms and **NOT** excess complexity, but **completeness in depth while staying understandable**: the same living delivery, just carried to the bottom. **1080–9000 words** (catalog — up to 14400, §8).

**Detailed is the main version, we ALWAYS write it.** `-d.md` — the topic's full article, present for every topic. **We write the basic AS NEEDED, and that need is rare.** A topic's default is **`basic:empty`**; a basic is an exception you must justify, not a habitual second file. That is: detailed — always; basic — only when it **adds** (a quick overview of a large topic), doesn't duplicate.

**THE BASIC GATE: four "yes" answers and no disqualifier.** The decision is made **with the finished detailed in hand** (§9), never in advance. Write a basic ONLY when **all four** signs hold:

1. **Size.** The detailed is longer than **~3300 words**. Shorter, and the basic comes out as a retelling, and the ½ ratio won't hold: for a 3000-word detailed the basic would have to fit into 1500, which is nearly the same article.
2. **One core thread.** You can state the topic's cause-and-effect core in **one sentence**, and it stands **without any** of the parts you would drop. If the essence of the topic is a **list of equal-weight things** (variants, modes, fields, commands, steps of a procedure), do **NOT** write a basic: a shortened list is not an overview, it is a truncated reference.
3. **There is something to drop.** At least **half** of the detailed is derivations, variations, edge cases, examples — material a basic may legitimately **skip**. A skeleton detailed, where every paragraph carries a new necessary fact, does not compress: you would have to cut truth.
4. **The detailed is not an entry point by itself.** If the detailed's first two or three paragraphs already give the picture of the topic, the reader **already has** the entry — a basic would only duplicate it.

**Unconditional disqualifiers** (they hold at any size): the topic is **reference-like** — its core is an API, a protocol, a format, a set of parameters, a table · the topic is **narrow**, existing only as a detail of a bigger one · the detailed **isn't written yet** (you don't decide the basic without it).

**A 50/50 hesitation means NO.** The gate's default is "no". The cost of "we didn't write a basic" is one extra step into the detailed for the reader; the cost of "we wrote a needless one" is a second text about the same thing that must be kept in sync with the first from then on.

**HARD SIZE RULE: a basic is ≤ half of its detailed.** Two limits hold **at the same time**, both mandatory:

```
basic:  540 ≤ words ≤ 1440        AND        words(basic) ≤ words(detailed) ÷ 2
```

We count **prose** (no code blocks, figures, tables, markup) — exactly the way `node scripts/wordcount.js <book-folder> --all` measures it: in its «ПАРИ базова↔детальна» block it prints the pair, the ratio and the basic's ceiling, and a `✖ ПОРУШЕННЯ` row is a **violation, not a warning**. What to do when it doesn't fit:
1. **First cut the basic** — it is almost always longer than needed: a second layer, variations, edge cases and derivations do **not** belong in a basic; their place is the detailed.
2. **Still doesn't fit after cutting — don't write the basic at all** (`basic:empty`, §9). "It can't be compressed to half without gutting the essence" means exactly one thing: the topic **does not need** a basic, not that the limit may be stretched.
3. **Never inflate the detailed** to "reach" the ratio, and don't pad the basic with water up to 540 words — the detailed's size is dictated by the topic, not by arithmetic.

The rule is symmetric to sign 1 of the gate ("the detailed is ≲3300 → we don't write a basic"): for a 3000-word detailed the basic would have to fit into 1500 — which is nearly a retelling, which is why we don't write it.

**The basic's language is simpler; the meaning and the understanding are the same.** A basic differs from the detailed in **size and apparatus, not in truth**. It is shorter because there is **less material**, not because it is "shallower": what is said is said **correctly and completely**.
- **Simpler words, shorter sentences.** An everyday word instead of a learned one where it is precise; less jargon, less formalism, fewer nested clauses. Name a term **after the mechanism** (§4) — first what happens, then what it is called; every term used is either explained here or is in the `preknowlist` (§6).
- **Cut the material, not the truth.** Drop derivations, variations, edge cases, secondary mechanisms and most examples — keep the **cause and the main mechanism**. "Almost right" simplifications that later have to be unlearned are **forbidden**: better to say honestly "we take this as given here" (§4, honest depth boundary) and give a link, than to give a convenient falsehood.
- **Not "as if for toddlers"** (§4): simpler is not more infantile. No baby talk, no pathos, no condescension — just clearer.
- *Test:* someone who has read **only the basic** says **correct things about the topic — merely fewer of them**. If after the detailed they have to **unlearn** something — the basic lied, rewrite it.

**Inserts are shared by both versions** (they belong to the topic, not a version): basic and detailed take the same insert files, the basic just **uses fewer** of them; the historical `hist-` — the same for both.

Manifest (§2): each version has its own `status` — `basic:{status}`, `detailed:{status}`. **`pending` = needs writing** (exactly what the writing scripts pick up) · **`empty` = not needed** · **`done` = written and available to the reader**. Detailed — the main queue (`pending`→`done`); basic — `empty` when the detailed is short (a duplicate), or `pending` when a large topic is worth a quick overview. **A new topic is ALWAYS registered as `basic:{status:"empty"}` + `detailed:{status:"pending"}`** (§6): the detailed goes into the queue, and the basic is decided once the detailed exists.

**Inserts — subtopics, separate `.md` files in the topic's folder**, five types by the prefix `<type>-<name>.md` (in `catalog/` — without `comp`):
- 📜 `hist-` — **history**: how the concept was born (what puzzled, who, the disputes); always real.
- 🔌 `comp-` — **component**: a **generalized** class of device/chip (typical pinout, wiring, class-wide pitfalls) — **no part numbers**; concrete models/products go into `catalog/` (criterion — §1).
- 🧮 `math-` — **PURELY the math of this topic:** a proof, an example, a problem, the mathematical essence and justification — **algebraically and geometrically**. Concrete math worked out for the topic, **NOT** a conceptual essay. **If it is actually an EXPLANATION of a topic** (a separate concept/theory) — it's **not an insert but a new article** (a math concept → the `math` book; another domain → its own book) + a ref link; in the math insert only the math remains. *Test:* math worked out FOR the topic (proof/example/problem/justification)? — an insert. A separate concept that must be learned and explained? — an article + link, not an insert.
- ⚙️ `proj-` — **algorithm/code**: task → idea → working code → traps. Language — **by domain** (§5): embedded/hardware → C/C++; general/web → the stack's languages, several languages via `:::tabs` tabs when needed.
- 📋 `api-` — **interface/reference ("what sticks out"):** the contract to connect or call. Software — the public API, signatures, parameters, errors, CLI/config; hardware — pin-by-pin wiring, registers, protocol, levels. Structural reference (tables/signatures), not a narrative. **A shared name for both domains, but do NOT mix:** if a topic needs both hardware and software — **two separate `api-` files** (e.g. `api-wiring.md` + `api-lib.md`), not one mixed. **`comp` vs `api`:** `comp` — a generalized *class* of device (how such a thing works in general, no part numbers); `api` — the concrete *contract* (signatures/pinout/registers of this specific thing or library).

**Insert length — 540–8100 words** by density; if there's a lot of material — **split into several**. The registry in the manifest — **separate by type**.

**Add inserts EAGERLY when the topic calls for them — a low decision threshold (mirroring `-d.md`), but the decision is CONTEXTUAL.** When you hesitate "spin a sub-block out as a separate insert or leave it in the article" — rather **spin it out**; don't reject a needed insert out of excessive strictness. **Calibration: ~10% FEWER inserts.** The threshold is raised one notch: when the hesitation is genuinely **50/50 — don't spin it out** (leave it as a sentence in the article, with a ref link to an existing target if there is one), and from a topic's set of candidates **drop the weakest** — the one whose layer adds least. This trims marginal inserts, not needed ones: everything the topic would be poorer without stays. **There is no norm for "how many inserts per topic"** — as many as the topic's logic asks for: one topic does without any, another naturally pulls several different types (a birth history, a mathematical derivation, and a code example **complement one another** when each is genuinely needed — in architecture, e.g., a decision's history and an algorithm example are equally apt). We do **not** add an insert for the sake of count. The boundary — **context and quality**: each insert **carries a separate layer** (the birth of a concept, a derivation, a working algorithm, the breakdown of a device class), not a retelling of the article or a banality.

**Insert structure for the parser:** the file begins with an **H1 heading** (`# Назва`, optionally with an emoji `# 📜 Назва`) — the engine takes it as the popup title. **An insert self-justifies:** the heading and first sentence must, **on their own**, without the parent article, say WHAT this is and WHY to open it (what can't be understood without it) — in the reader's language, not a jargon label; a bare term in the heading won't do. The insert is **registered in the manifest** (the array of its type, §2) and **mentioned in the text** by a ref-insert (§6). The insert **contains no back-navigation cards** («🔗 Тема, до якої…», «▶️ До теми» etc.) — it's opened as a popup from the topic, so a back-link is superfluous; inline links to other topics in the body text — allowed. If a return genuinely carries content — format it as a **regular insert**, not as a navigation card.

## §4 Writing core

**Method (Feynman — deep, from first causes).**
- First **intuition and the "WHY"**, then the details. We give motivation **if there's even a slight need**; we skip it only where there is **definitely none**.
- The goal of motivation (and of history, if any): **to show, briefly and engagingly, the real reason** it was begun — so the reader sees the true essence.
- We **build the conclusion before the reader's eyes**, not announce it ready-made.
- Analogies are **precise** — and we show **where they break**.
- The account — **cause-and-effect chains** «A → тому B → звідси C», not lists; traps and edge cases — with the mechanism.
- No retellings or recaps — each unit carries a **new thought**.
- **Don't meta-comment on style:** don't explain in the text WHY we write this way — just write in this style.

**Continuity and clarity (substance + self-test).**
1. **Continuity (no gaps).** The article is a single chain: each new link is reachable from the previous one by a single step the reader takes on their own. Everything you use in the thread, first build in the text (the preknowlist — only prerequisites from OUTSIDE). A step that's "obvious" to you and thus skipped is exactly where the reader falls through; a skipped link is not economy but a hole, and closing holes is the book's purpose.
   → *Test:* read as someone who has only the preknowlist; at each transition — "am I making this step from the single previous one?". No — insert an intermediate link.
2. **Necessity before assertion.** The skeleton is causal necessity: what problem makes the concept inevitable and why the solution must be as it is. Lead from the cause so the reader feels "it couldn't have been otherwise"; open on tension (a question/riddle), not on an abstract thesis.
   → *Test:* does the reader meet the problem before the solution and could guess its shape? No — rearrange.
3. **The example illustrates, doesn't carry.** A concrete example/code makes an **already-built** thought tangible; the logical "why" stands on its own.
   → *Test:* remove all examples/code — is the "why" still clear? No — it rested on the example, rebuild from the logic.
4. **One thread, no sprawl.** One line to one conclusion. Depth goes **into** the thread (fill every gap), not **sideways** onto neighbors: an adjacent concept, a comparison, a tangential theory — a sentence + a ref link, not its own section.
   → *Test:* name the article's single question and its single main sentence; a section that unfolds a neighbor is a separate atom behind a link.
5. **An honest depth boundary.** If you take a rule without derivation — say so and why the derivation isn't needed here. A silent stop = a hole; a named one = a closed door that's trusted.
   → *Test:* is everything used-but-not-derived either built earlier, in the preknowlist, or explicitly "taken as given, because…"?
6. **No filler, by function.** Every sentence moves the **subject** forward. A sentence whose subject is the text itself (its depth, honesty, superiority over other accounts), the reader's route, or an announcement of structure, does not move the subject. The ending does not retell what was said: either a new synthesis, or none.
   → *Test:* is the subject the topic, or the text / its virtues? Not the topic — cut it. Does the ending contain something new? No — delete it.
7. **Sentential clarity.** One thought — one sentence; don't nest subordinate clauses inside one another. Name the term **AFTER** the mechanism, not before (first show WHAT happens, then name it in one word). Symmetric things — with **parallel construction** (so the mirroring is visible).
   → *Test:* a sentence you must reread to untangle its clauses — break into steps, one vector per sentence.

**Smoothness (right away, not as a separate pass).**
- The transition between thoughts — **natural and logical**, and **not through empty connective sentences just for show** (they tear the simplicity of perception and annoy).
- The through-line: **why → intuition → details → example**.
- Before finishing the file, **reread it whole** and smooth the seams.
- Thread test: you rearranged the paragraphs and nothing broke — it's a heap, rewrite.

**Living Ukrainian (accessibility + source origin).**
- Accessible, **like a good lecturer**: clear, but **without condescension** — not as if to little kids. We respect the reader's intellect (without the pathos of «відчуй це!»).
- Only **real words** — none invented/distorted/calqued; no russicisms, no bureaucratese, no out-of-place anglicisms, no accidental synonymy. **One term per concept** within a file.
- **Source origin of a name:** when introducing a new concept, give in parentheses the source language and root — Latin/Greek (or English, if that's the origin). For **all** books.
- Sentence test: read it aloud in your head — **if a living person wouldn't say it that way, rephrase**.

## §5 Formulas, examples, figures

**Formulas.** **NO LaTeX** (the renderer doesn't show it) — Unicode in the text: `10⁻⁹, ε, ≈, ×, ·, ², ₀, Δ, σ, ω, →, ⇄`. Step-by-step computations and key formulas — in **monospace code blocks**, aligned on `=`. The separator is a **dot** (`3.3`). Exactly as many formulas as needed; if there's a formula, it's **used**.

**Worked example.** **A bold caption-premise** → a code block with a **step-by-step computation** → a conclusion. The code is real and correct, **not pseudocode**.

**Code language — by domain, NOT always C/C++.** C/C++ is mandatory only where the subject dictates it: **embedded/firmware, registers, hardware, basic algorithms with an emphasis on speed**. For **general programming / web / backend** write in the languages that actually live there (JS/TS, Python, Go, Rust, Java…). The language must be **truthful to the example**: domain-locked code (MCU registers, syscalls) stays in one language; a general idea, correct in several languages, **may be shown in several**.

**Language choice — a weighted score (which language to write).** For each code example, rate every candidate language **0–10** by aptness right here — **from all sides**: how naturally and instructively the example reads in it in this domain **and how efficient it is for this task** (speed, memory, concurrency) — **not by the language's popularity**. Where the example is about performance, the system level, concurrency, or a hot path — performance languages (C/C++/Rust/Go/Zig) get a **higher raw score**, even if TS/Python are more popular for general code; where the example is about domain expressiveness / a DTO / a script — the reverse. Multiply by a coefficient: **C++ and TypeScript — ×1.5**, other languages — ×1. Write in those whose product is **> 5** (several — as `:::tabs` tabs, each idiomatic; one — a regular code block). Example: C++ with a raw 4 → 4·1.5 = 6 (**we write it**); Python with 4 → 4 (**no**). This way C++/TS appear more often — but **only where they truly fit**: a low raw score even ×1.5 won't rescue (we don't write registers in Python, nor a DTO in assembly). The coefficient tips things at the margin, it doesn't force what's inapt.

**C/C++ in `programming` and `algorithms` — mandatory, except pure frontend.** In the `proj` examples of these two books **C or C++ is mandatory** (as the main language or at least one of the `:::tabs` tabs) — **everywhere except pure client-side frontend** (browser UI, DOM, components, styles). **Backend and servers are under the rule too:** a high-load server in C++ is apt, so a server/system/compute/algorithmic `proj` gets C/C++ by default. The exception is only the client frontend, which we write in the stack's languages without coercion.

**Several languages at once — `:::tabs` tabs.** When the same example is equally apt in 2–5 languages (typical in books for a broad programming audience), wrap the fences in a container — the engine gives a **tab switcher on top**, shared across the whole page (the choice is remembered). **EACH tab is an independently correct, idiomatic equivalent of this exact example, not a mechanical transliteration.** A language that doesn't fit the example well is **dropped, not dragged in**. Syntax (the language in the fence-info gives the tab name):
````
:::tabs
```py
def add(a, b): return a + b
```
```js
const add = (a, b) => a + b;
```
:::
````
One language (no tabs needed) — **a regular code block with the language in the fence** (` ```py `), and the language turns on syntax highlighting.

**Figures.**
- Only **SVG**, **pure Python with no dependencies** (no matplotlib); the generator `figs.py` **in the topic's folder**, output to `./img/`.
- `svgkit` from `scripts/` — **import, don't rewrite**; a box with text — **only** via `textbox()/fitbox()`.
- **Every figure carries weight** (a nontrivial idea hard to convey in words); banal decorations — better none at all.
- A reference to a figure — **a path from the repo root** (with `/`): `![опис](/book/<book>/<section>/<slug>/img/<file>.svg)`. **No file name and no numbers in the text.**
- **The caption is a plain description** (what's shown and the takeaway), **with no number and no «Рис.»**, in italics on the next line.
- After generation — `scripts/svgcheck.py`; fix what's flagged until «із зауваженнями: 0». The check is **purely local** (no agents, no tokens) and catches everything that gets in the way of **understanding** the figure: too-small font · **text↔text** · **a line or contour cutting through a label** — `line`, `polyline`, `polygon`, `path` and the **borders** of `rect`/`circle`/`ellipse` · **a label clipped by the canvas edge** (classic: a long string with `text-anchor="end"`) · **blocks partially colliding** with one another · `--links` — whether every svg referenced in the topic's `.md` actually exists. Text inside **its own** `textbox()/fitbox()` box and nested panels — the norm, not a violation; figures with `<g transform=…>` are deliberately skipped (shifted coordinates — better silent than inventing intersections).
- **Who runs the svg gate.** The result requirement (svgcheck «0») is unchanged. A **local pre-gate** runs first: one `svgcheck.py … --links` command over all the batch's folders filters out the clean ones — an agent is called **only** where there is something to fix. Beyond that, **in the batch writing pipeline (`write-batch.js`) the final svg gate is done by a separate step on Sonnet-high** (the "Figures" phase): the author of the article/insert only **generates** the figures (meaningful, with a tidy layout) and **runs `figs.py`**, while bringing `svgcheck.py` to «0» (by editing the `figs.py` layout — spreading captions apart, widening cells/viewBox, routing lines away; **the figure's content does not change**) is handled by a separate sonnet-high agent per folder. In **manual** writing (outside the pipeline) the author brings it to zero themselves, as before.

**Practicality.** Beside an important concept — a box `> 🔧 **Навіщо це.**`: what it's for in real development, **on the material of this topic**.

## §6 Cross-references and popups

**Mentioned something concrete and weighty — give a footnote.** Not every mention (otherwise a forest of links), but if a **concrete, sufficiently weighty** concept/phenomenon/topic surfaces in the text — add a **linking sentence + a footnote-insert** (popup) to it. The rest (passing, minor mentions) — without a link.

Format — a **ref-insert**: a short synopsis of **1–7 sentences** "what exactly to know" (only what the article can't be understood without) + a ref link that opens a **popup**. Do **not** rewrite the whole target. The target of a ref-insert:
- **another article** — `book:<book>/<slug>` — **the general link (default)**: the renderer opens the basic, or the detailed if no basic exists; **explicitly detailed** (rare) — `book:<book>/<slug>/detail`;
- **an insert of this topic** — `book:<book>/<slug>/<type>-<name>.md`.
- **a course article/step** — `guide:<course>/<slug>` (general) / `guide:<course>/<slug>/detail` (explicitly detailed) / `guide:<course>/<slug>/<type>-<name>.md` (insert) — **mirroring `book:`**, the same popup mechanics.

**Rule (always):** target in `book/` → `book:`; target in `guide/` (a course step) → `guide:`. No `book:` for what's been moved into a course, and vice versa.

**The popup is self-standing.** An insert (and another topic/detailed) the engine opens as a **separate file at its own path**, **regardless of the owner article's status**: an insert from a topic whose basic is still `pending`/`empty` **opens anyway** (only its folder is needed). An article (main/detailed), by contrast, shows a «у розробці» stub until its status is `done`.

The section isn't needed in the path. **Default — the general link `book:<book>/<slug>`** (almost always): the renderer substitutes the available version itself — the basic, or the detailed if no basic exists. **Use the explicit detailed `/detail` RARELY — mainly in a ref FROM A COURSE**, when the step genuinely wants the full version despite an existing basic. **If a `/detail` ref points to a topic that only has a basic — mark the target topic `deeper` in the manifest** (the detailed needs writing); the link stays on `/detail`.

**The target doesn't exist yet — we create it and ref it in advance.** The target is either a **topic-article** or a **supporting insert** (history/example/math/device — `<type>-<name>.md`):
1. Determine the **right place** (a topic — book + section; an insert — the topic's folder).
2. Create an **empty file** (the topic's md or `<type>-<name>.md`).
3. Register it in the manifest: a topic — **`basic:{status:"empty"}` + `detailed:{status:"pending"}`** (the **detailed** goes into the queue — it is the main version, §3; the basic is decided AFTER the detailed: if it turns out large, then `basic:pending`). An insert — `pending` in the array of its type. **Never give a new topic `basic:pending`.**
4. Place the ref — the popup will show a stub, and **pull in the text** once it's filled.

Where there's a genuine dependency — **no dangling mentions without a ref**.

**The plan is not the final truth; we catch gaps DURING writing.** Don't assume the manifest already contains all the needed topics — it's precisely while writing that you best see what the plan didn't foresee. Go over the weighty concepts the article **assumes known** or **relies on**, and check whether such a topic exists in the repo (grep across the `book/` and `guide/` manifests; either ready or a stub is enough). If a weighty concept **exists nowhere** — that's a **gap in the plan**, not a reason to silently avoid the mention or leave a bare inline without a ref: **create the topic** (a `pending` stub) and place a ref, as in the procedure above. The threshold is weight (a genuine dependency without which the topic can't be understood), not every passing mention. **Better an extra stub than a silent hole.** (In the `write-batch.js` pipeline this is the article author's `newTopics` field; the "Manifest" phase registers the new as `pending` and filters out duplicates.)

### "Before reading" — the `preknowlist` block (v6, mandatory in EVERY new article)

Immediately **under the H1** — a list of **prerequisites**, collapsed by default: what you **definitely need to know, without which the article can't be understood** (read-before-to-understand). This is not a retelling of the topic but an **entry threshold**. Format — the `<preknowlist>` tag with a bulleted list of ref links (§6 mechanics, mirrored `book:`/`guide:`), each with a short "what exactly to know" on one line:

```
# Заголовок статті

<preknowlist>
- [Закон Ома](book:electronics/ohm-law) — напруга = струм · опір, базовий зв'язок величин.
- [Похідна](book:math/derivative) — миттєва швидкість зміни величини.
</preknowlist>

<основний текст статті…>
```

The engine renders the block as a **collapsed `<details>` at the top** of the article (a click expands the prerequisites list). Rules:
- **book / catalog / reference:** list **all genuine prerequisites** — the article is standalone, the reader may know nothing prior.
- **guide (course):** list **only what is OUTSIDE the course or not yet covered** along its sequence; prerequisites the course **already gave earlier** — do **NOT** add (the course's thread provided them — otherwise the block duplicates what's been covered).
- Links — **only weighty prerequisites** (not "everything tangential"); §6 mirroring (target in book → `book:`, in a course → `guide:`).
- **Only for NEW articles.** Already-written ones without the block — **we don't touch**; the block is added when an article is rewritten.

## §7 Historical facts and attribution

- Any historical/factual claim (a date, a name, "who was first", an invention, a patent, an origin) — **only on verified data** (a web check). History is always **real**; mark legends as legends.
- **Distinguish the dimensions of identity**: ethnicity / citizenship / birthplace / language / institution / imperial affiliation. Don't label something "Russian" when the sources give something more precise (Ukrainian, Pole, Serb, Jew, Georgian, Armenian, Balt…); if mixed or uncertain — **say so plainly**.
- Watch for **imperial absorption** (Russian-Soviet narratives; the fabrications of the 1948–53 priority campaign — Kryakutnoy's balloon, Artamonov's bicycle).
- Inventions are **collective**: distinguish idea / theory / working implementation / system / patent; don't accept "we thought of it first" without evidence (radio — Tesla, Marconi, Popov, Hertz, Lodge, Bose).
- Always **mark the evidential status**: settled · contested · imperial-national framing · plausible-but-unproven · myth.

## §8 Technical voice and catalog

**The `book` ↔ `guide` ↔ `catalog` boundary.**
- `book/` articles — **generalized**: a concrete part/number may be given **only as an example-mention with a link** (to `catalog/`/`comp-`), but **don't build the article on it**.
- `guide/` articles — **may be based on concrete parts/components** (a course is applied).
- Platforms that are the very subject of study (ESP32, ArduPilot) may be named even in `book/`.

**Catalog.** We write **freely, without an imposed list of sections**. The guide is a **general model**: describe the object so the reader **recognizes it, understands what it does and how it's built, how to use/connect it, and what to beware of**. You pick the concrete sections **yourself, to fit the device's nature**; the detailed version **covers everything needed to actually work with it**. Length: basic — as §3; **the catalog detailed — up to 14400 words** (above the §3 ceiling, because it's sometimes needed); more — **split into several parts**.

**A board/module in the catalog — schematic, wiring, API (mandatory, v6).** If a catalog object is a **board or module** that has an **internal schematic** (how it's built inside) or a **wiring diagram** (how to connect it to an MCU/power), the article **MUST**: (1) **depict** both as SVG figures (§5) — the schematic and the **pin-by-pin** wiring layout; (2) **describe** them (what goes where and why, power, levels, pull-ups); (3) provide an **API insert `api-<name>.md`** — how to use it in code: library / typical calls, a **working C/C++ example**, typical traps. Without these three a board/module article is **incomplete**.

**A product family — factor out the common, link, don't repeat (v6).** If an object belongs to a **line/family** of several variants sharing common ground (manufacturer, architecture, history, a common pinout/toolchain — e.g. ESP32/Espressif, Arduino, Raspberry Pi, the KY series), create a **FAMILY overview article** (a separate catalog topic `<family>-family` / `<series>-series` in the same family/section). It holds the **common part**: history (`hist-`), the shared architecture that unites the variants, how to choose; deep science it links into `book/`/`guide/`. A concrete product **links to its family** (a ref popup `book:<family>/<family>`) for the common part and describes **ONLY ITS OWN** (differences, specifics) — it does **not** repeat the family history. No overview yet — create it (`newTopics`, `pending`). This way all variants of a line share one common article instead of duplication.

There are no subject/audience-specific rules in the canon — **how to write a specific book is dictated by whoever sets the task**.

**Optional per-book rules file — `<book-folder>/_canon.md`.** If the root of a book/course/catalog/reference book holds a `_canon.md` (`book/<book>/_canon.md`, `guide/<course>/_canon.md`, `catalog/<family>/_canon.md`, `reference/<ref>/_canon.md`) — these are **additional rules for it specifically** on top of this general canon: a running example, unified terms and names, the language of examples, style conventions. The writer (both articles and inserts) **reads it as the first action**, if it exists, and holds to it strictly — where `_canon` refines the general, **`_canon` takes precedence**. **No file → there are no additional rules for this book/course/catalog/reference book**, we write by the general canon. (Technically `write-batch` checks for the file before writing each topic.)

## §9 Statuses, process, hygiene

**Statuses (enum in the manifest, for EACH `basic`/`detailed` version and EACH insert):** `done` (written, canon, available to the reader) · **`pending`** (**needs writing** — exactly what the writing scripts pick up) · **`empty`** (**does NOT need writing** — the version/insert isn't envisaged) · `update` (rewrite) · `deeper` (deepen; in particular — the topic is linked to as the detailed `/detail`, §6) · `recheck` (review against the current rules; **clear inaccuracies** — a number/fact/date/unit/formula/logic — we fix pointwise, but **we don't rewrite what's done**). We change it **right in the manifest** immediately after an edit. *(v4→v5 change: `empty` used to mean "not started" — now that's `pending`; `empty` = "not needed".)*

**Process.** We take the **very first** `pending`/`update`/`deeper`/`recheck` (specifically **`pending`** — the writing queue; we do NOT take `empty`, that's "not needed"). **One version = one move** (text + figures + the version's status → `done`). A large step we **delegate to a subagent** with full paths; to the main loop session — only a short report.

**Order within a batch — detailed first, then basics.** The queue is filled with **priority on `detailed`**; `basic` is taken only when there aren't enough detailed ones. We write **all the detailed ones first**, and only with the finished detailed in hand do we decide **whether it needs a basic**. There are exactly three outcomes: the basic **already exists** → **change nothing** (neither the file nor the status); the basic **is missing and is needed** (the detailed is large, §3) → write it in the next stage; the basic **is missing and is not needed** (the detailed is short/narrow) → `basic:empty`, and only if it was `pending` (other statuses are left alone). Only then do we write the basics: **those the scout found, plus those added after the detailed ones**. After that — inserts, the local figure gate, the manifest. **New dependent topics (§6) may appear at ANY stage** — from an article or from an insert; all of them are registered as `basic:empty` + `detailed:pending`.

**Parallelism.** The manifest is **one per book/course/catalog/reference book** → isolation **by book**: several `/loop`s run in parallel only if each is in **its own** book/course. Do **not** run two `/loop`s on one book (a shared manifest → conflict). Work only in your own book's manifest.

**Discipline.** **Follow instructions exactly — always.** Do **not** change agreed or finished structure/content **on your own**, and don't touch what you were asked not to touch. See a way to improve — **ask first** (about structure and content), don't do it yourself.

**Hygiene.** **Do NOT commit** without being asked. Renaming — **`git mv`**. **Parallel agents — in a POOL (at most ~4 AT ONCE; default 4, configurable), with a ~2–3 s stagger** (via `setTimeout`): the stagger spreads the wave against the rate limit, and the pool caps the **front** — when the session limit runs out, at most a few agents fall, not the whole batch together (otherwise — a retry storm of dozens of restarts and the loss of an entire run). The ceiling is 4 (not 3) — because at start/handoff in flight it's sometimes one fewer, so 4 keeps effectively 3–4. Scripts — universal, in `scripts/`. Before bumping versions — `node --check` the changed JS.
