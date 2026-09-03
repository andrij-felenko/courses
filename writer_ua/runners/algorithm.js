#!/usr/bin/env node
/* ============================================================================
   algorithm.js — ВНУТРІШНІЙ РІВЕНЬ: десять етапів над ОДНІЄЮ одиницею.

   Оркестратор дає чергу й стан; цей файл робить із однієї одиниці один файл. Межа
   між ними тримається на трьох речах, які приходять у `ctx`:

     ctx.set(поле, значення)   заповнити етап — поле заповнене, етап пройдено
     ctx.call(мітка, fn)       ОДИН запит до агента, з межею очікування
     ctx.enqueue(одиниці)      докласти в чергу: вставки, код, базову

   ⛔ ЛОКАЛЬНЕ РОБИТЬСЯ ЛОКАЛЬНО. Підготовка, розмір, зібрання, операції в маніфест —
   у `local.js`, нуль токенів. Агента кличемо лише там, де потрібне судження.

   ПОРЯДОК ПЕРЕВІРОК: розмір (локально) → викладка (онлайн, до 7 кіл) → формули
   (онлайн, раз) → код C/C++ (онлайн, без тексту). Він не довільний: розмір перший, бо
   викладка — єдине повне перечитування, і судити нею недописаний текст означало б
   питати вдруге. Після перепису розмір НЕ перевіряється знову — інакше коло
   «дописали → переписали → знову мало».
   ========================================================================== */
"use strict";
const P = require("./prompt.js");
const R = require("./parse.js");
const LOC = require("./local.js");

const MAX_LAYOUT = 7;      // стеля кіл викладки; вичерпали — вважаємо написаною
const KEEP_SHARE = 0.75;   // скільки прози перепис МУСИТЬ зберегти; менше — це втрата, не правка
const MAX_SIZE_ROUNDS = 2; // скільки разів дописуємо за розміром

/**
 * Верхній наявний рівень із переліку «що можна додати» — і тільки він.
 * Рівні: 5 точно треба · 4 треба для розуміння · 3 для глибшого засвоєння ·
 * 2 засвоїмо простіше · 1 доповнює тему. Дописувати все підряд означало б
 * ростити статтю тим, що сам письменник поставив унизу.
 */
function topAdditions(list) {
  const top = (list || [])[0];
  if (!top) return "";
  return (list || []).filter((x) => x.level === top.level)
    .map((x) => `${x.level} | ${x.what}`).join("\n");
}

/** Обов'язкові блоки: немає — це помилка кроку, а не привід вгадувати. */
function need(res, tags, where) {
  const got = R.want(res, tags);
  if (got.missing.length) throw new Error(`${where}: у відповіді немає ${got.missing.join(", ")}`);
  return got.data;
}

/**
 * @param {object} unit  {book, slug, type, version, …} з local.unitOf
 * @param {object} ctx   від оркестратора: set/get/call/enqueue/state/run
 * @param {object} o     {ask, mentionRe, status}
 *        ask(prompt, label) → текст відповіді. Це ЄДИНЕ місце, де конвеєр торкається
 *        агента; чим саме він викликається — Claude, Antigravity, підробка — цей файл
 *        не знає й знати не повинен.
 */
async function algorithm(unit, ctx, o = {}) {
  const ask = o.ask;
  if (typeof ask !== "function") throw new Error("немає ask() — нічим питати агента");
  const u = unit;

  /* Код — своя дорога: ціль → архітектура → файли. Прози в нього немає, і етапи розміру
     й викладки йому нічого не сказали б. */
  if (u.type === "code") return codeAlgorithm(u, ctx, o);

  /* ── 1 · ПІДГОТОВКА · локально ─────────────────────────────────────────── */
  if (!ctx.get("prep")) {
    const dup = LOC.isDuplicate(u.book, u.slug);
    if (dup.written) throw new Error(`тема вже написана — це дубль, писати нічого`);
    ctx.set("prep", {
      /* ⚠️ Ключ пошуку — ЦІЛА назва теми, а не перше її слово. З першим словом
         «Одержимість примітивами» ловила «одержимість простотою» з історії Arduino:
         пошук за словом дає омонім, і чим коротше слово, тим більше шуму. */
      mentions: LOC.mentions(u, o.mentionRe || LOC.titleRe(u.title)),
      neighbours: LOC.neighbours(u),
      preknow: LOC.preknow(u),
      dupeHints: dup.hints,
    });
  }
  const prep = ctx.get("prep");
  const passed = prep.preknow || LOC.preknow(u);

  /* ── 2 · ЦІЛЬ · агент ──────────────────────────────────────────────────── */
  if (!ctx.get("goal")) {
    const res = await ctx.call("ціль", () => ask(P.goal(u, { mentions: prep.mentions }), "ціль"));
    const d = need(res, ["ЦІЛЬ"], "ціль");
    const lv = R.blocks(res)["РІВЕНЬ"];
    ctx.set("goal", { text: d["ЦІЛЬ"], level: lv ? parseInt(lv, 10) || null : null });
  }
  const goal = ctx.get("goal");

  /* ── 3 · КАРКАС · агент ────────────────────────────────────────────────── */
  if (!ctx.get("karkas")) {
    const res = await ctx.call("каркас", () => ask(P.karkas(u, {
      goal: goal.text, level: goal.level,
      preknow: passed, books: LOC.books(),
    }), "каркас"));
    const b = R.blocks(res);
    const secs = R.sections(b["РОЗДІЛИ"] || b["КРОКИ"] || b["ПОДІЇ"] || b["ВАРІАНТИ"] || "");
    if (!secs.length) throw new Error("каркас: не повернув жодного пункту");
    ctx.set("karkas", {
      sections: secs,
      groups: R.groups(b["ГРУПИ"] || "").length ? R.groups(b["ГРУПИ"]) : [secs.map((s) => s.n)],
      opory: R.lines(b["ОПОРИ"] || ""),
      missingTopics: R.lines(b["БРАКУЄ ТЕМ"] || ""),
      inserts: R.inserts(b["ВСТАВКИ"] || ""),
      code: R.code(b["КОД"] || ""),
    });
  }
  const k = ctx.get("karkas");

  /* Вставки типу 2 і код — окремі одиниці; вони стають у ту саму чергу батчу.
     Тип 1 у статтю не входить: він іде в нові теми на етап 8. Тип 3 лишається
     парою речень у тексті й одиницею не стає. */
  const codeUnits = codeUnitsOf(u, k);
  if (!ctx.get("sections")) {
    /* Код — ПЕРШИМ у чергу: на нього чекає ця сама стаття, а вставки не чекає ніхто. */
    const more = [...codeUnits];
    for (const ins of k.inserts.filter((x) => x.kind === 2))
      more.push({
        ...LOC.unitOf(u.book, u.slug, ins.insert, "", ins.name ? `${ins.insert}-${ins.name}` : ""),
        about: ins.about, section: ins.section,
      });
    if (more.length) ctx.enqueue(more);

    /* ⏸ ПАУЗА НА КОД. Проза посилається на файли, яких ще немає, тож писати її зараз
       означало б обіцяти читачеві те, чого не бачив і сам письменник. Одиниця віддає
       своє місце в пулі й стає знову в чергу, щойно код буде написано. */
    const waitFor = codeUnits.map((c) => c.id).filter((id) => !ctx.isDone(id));
    if (waitFor.length)
      throw Object.assign(new Error(`чекає на код: ${waitFor.join(", ")}`), { pause: true, waitFor });
  }

  /* ── 4 · ПИСЬМО · агенти, групами ──────────────────────────────────────── */
  if (!ctx.get("sections")) {
    const written = [];
    let theses = [];
    for (const g of k.groups) {
      const mine = k.sections.filter((s) => g.includes(s.n));
      /* ⚠️ ІМ'Я ВСТАВКИ Й СПРАВЖНІ ШЛЯХИ КОДУ — В ЗАВДАННЯ, А НЕ САМ ЛИШЕ ОПИС. Письменник
         мусить поставити на них лінк і директиву, а вигадати адресу він не може: діставши
         тільки «про що», він написав `hist-information-hiding.md` там, де вставка зветься
         `hist-enforced-hiding.md`, і лінк вийшов битий. Код на цей момент уже на диску —
         пауза для того й стоїть, — тож перелічуємо реальні файли. */
      const bound = [...k.inserts.filter((x) => x.kind === 2 && g.includes(x.section))
        .map((x) => {
          const file = x.name ? `${x.insert}-${x.name}.md` : `${x.insert}-${u.slug}.md`;
          return `розділ ${x.section}: вставка «${x.about}»\n` +
            `  інтегрувати як вставку, лінк рівно такий: root:${u.book}/${u.slug}/${file}`;
        }),
      ...k.code.filter((c) => g.includes(c.section)).map((c) => {
        const files = LOC.codeFiles(u, c.lang);
        return `розділ ${c.section}: код ${c.lang} — ${c.what}\n` +
          (files.length
            ? `  інтегрувати директивами «:::code <шлях>», шляхи рівно такі:\n${files.map((f) => `    ${f}`).join("\n")}`
            : `  файлів ще немає — не посилайся на них`);
      })].join("\n");

      const res = await ctx.call(`письмо ${g.join(",")}`, () => ask(P.write(u, {
        goal: goal.text, level: goal.level,
        sections: mine.map((s) => `${s.n} | важливість: ${s.importance} | ${s.text}`).join("\n"),
        theses: theses.join("\n"), inserts: bound, passed, linkable: LOC.linkable(u),
      }), `письмо ${g.join(",")}`));

      const d = need(res, ["ТЕКСТ"], `письмо ${g.join(",")}`);
      const b = R.blocks(res);
      theses = theses.concat(R.lines(b["ТЕЗИ"] || ""));
      written.push({
        group: g, text: d["ТЕКСТ"], theses: R.lines(b["ТЕЗИ"] || ""),
        deeper: b["ЧИ ГЛИБШЕ"] || "", full: b["ЧИ ПОВНО"] || "",
        add: R.additions(b["ЩО ДОДАТИ"] || ""),
        squeeze: R.empty(b["ЩО ЗЖАТИ"]) ? "" : b["ЩО ЗЖАТИ"],
        newTopics: R.empty(b["НОВІ ТЕМИ"]) ? [] : R.lines(b["НОВІ ТЕМИ"]),
      });
    }
    ctx.set("sections", written);
  }
  let parts = ctx.get("sections");

  /* ── 5 · РОЗМІР · локально → дописування ───────────────────────────────── */
  if (!ctx.get("size")) {
    let rounds = 0, s = LOC.size(LOC.assemble(parts.map((p) => p.text)), u.type, goal.level);
    while (s.shortBy > 0 && rounds < MAX_SIZE_ROUNDS) {
      /* ⚠️ Дописуємо не «до числа», а НАЗВАНИМ матеріалом — і беремо з нього рівно
         найважливіше: письменник ранжує, що можна додати, від 5 до 1, а сюди йде лише
         верхній рівень із наявних. Дописали його — наступне коло візьме той, що став
         верхнім тепер. Так обсяг росте від «точно треба» вниз, а не абичим.
         Нема чого назвати — рахуємо як пройдене; за домовленістю це рідкість, бо
         порожнім перелік не буває. */
      const hungry = parts.filter((p) => (p.add || []).length);
      if (!hungry.length) break;
      for (const p of hungry) {
        const res = await ctx.call(`дописування ${p.group.join(",")}`, () => ask(P.extend(u, {
          goal: goal.text, level: goal.level,
          section: p.group.join(", "), text: p.text,
          neighbours: parts.filter((x) => x !== p).flatMap((x) => x.theses).join("\n"),
          add: topAdditions(p.add), howMuch: s.shortBy > 40 ? "повністю" : "трохи",
        }), `дописування ${p.group.join(",")}`));
        const d = need(res, ["ТЕКСТ"], "дописування");
        const b = R.blocks(res);
        p.text = d["ТЕКСТ"];
        p.theses = R.lines(b["ТЕЗИ"] || p.theses.join("\n"));
        p.add = R.additions(b["ЩО ДОДАТИ"] || "");
        p.squeeze = R.empty(b["ЩО ЗЖАТИ"]) ? "" : b["ЩО ЗЖАТИ"];
      }
      rounds++;
      s = LOC.size(LOC.assemble(parts.map((x) => x.text)), u.type, goal.level);
    }

    /* ── стиснення: дзеркало дописування ─────────────────────────────────────
       Перевищили стелю — стискаємо НАЗВАНИМ матеріалом, тим, що письменник сам
       поклав у «Що зжати». Нема чого назвати — лишаємо як є: сліпе обрубання по
       числу думати не вміє й рве нитку посередині. Факт лягає в стан і в лог. */
    let squeezed = 0;
    while (s.over && squeezed < MAX_SIZE_ROUNDS) {
      const fat = parts.filter((p) => p.squeeze);
      if (!fat.length) break;
      for (const p of fat) {
        const res = await ctx.call(`стиснення ${p.group.join(",")}`, () => ask(P.compress(u, {
          goal: goal.text, level: goal.level,
          section: p.group.join(", "), text: p.text,
          neighbours: parts.filter((x) => x !== p).flatMap((x) => x.theses).join("\n"),
          squeeze: p.squeeze, howMuch: s.words > s.ceiling * 1.4 ? "суттєво" : "трохи",
        }), `стиснення ${p.group.join(",")}`));
        const d = need(res, ["ТЕКСТ"], "стиснення");
        const b = R.blocks(res);
        p.text = d["ТЕКСТ"];
        p.theses = R.lines(b["ТЕЗИ"] || p.theses.join("\n"));
        p.squeeze = R.empty(b["ЩО ЗЖАТИ"]) ? "" : b["ЩО ЗЖАТИ"];
      }
      squeezed++;
      s = LOC.size(LOC.assemble(parts.map((x) => x.text)), u.type, goal.level);
    }
    ctx.set("size", { ...s, rounds, squeezed, stillOver: s.over, nothingToSqueeze: s.over && !parts.some((p) => p.squeeze) });
    ctx.set("sections", parts);
  }

  /* ── 6 · ВИКЛАДКА · агент, до 7 кіл ────────────────────────────────────── */
  if (!ctx.get("layout")) {
    let attempt = 0, ok = false, why = [], shrank = null;
    while (attempt < MAX_LAYOUT) {
      const text = LOC.assemble(parts.map((p) => p.text));
      const res = await ctx.call(`викладка ${attempt + 1}`, () => ask(P.layout(u, {
        goal: goal.text, level: goal.level, text,
      }), `викладка ${attempt + 1}`));
      const b = R.blocks(res);
      if (R.yes(b["ОК"])) { ok = true; break; }
      why = R.defects(b["НЕ ТАК"] || "");
      if (!why.length) { ok = true; break; }
      attempt++;
      const rw = await ctx.call(`перепис ${attempt}`, () => ask(P.rewrite(u, {
        goal: goal.text, paragraphs: text, attempt,
        defect: why.map((d) => `${d.where} :: ${d.why}`).join("\n"),
      }), `перепис ${attempt}`));
      const d = need(rw, ["ТЕКСТ"], "перепис");

      /* ⛔ ЗАСТАВА ПРОТИ З'ЇДЕНОГО ТЕКСТУ. Відповідь перепису замінює СТАТТЮ ЦІЛКОМ, тож
         короткий переказ замість тексту знищує написане мовчки. Один раз це вже сталося:
         2080 слів прози до перепису, 616 після. Перевірка локальна й коштує нуль — просто
         рахуємо прозу до й після; втратив чверть — це не правка, а втрата, і ми її не
         приймаємо: лишається попередній текст, коло ладу спиняється, випадок іде в лог. */
      const was = LOC.size(text, u.type, goal.level).words;
      const now = LOC.size(d["ТЕКСТ"], u.type, goal.level).words;
      if (now < was * KEEP_SHARE) {
        shrank = { was, now, share: Math.round((now / was) * 100) };
        break;                        // текст лишається попередній, неторканий
      }

      parts = [{ group: parts.flatMap((p) => p.group), text: d["ТЕКСТ"], theses: parts.flatMap((p) => p.theses), add: "" }];
      ctx.set("sections", parts);
    }
    /* Вичерпали спроби — вважаємо написаною, і випадок іде в лог помилок батчу.
       З'їдений перепис — те саме: текст лишається останній цілий, а `shrank` каже, на
       чому спинились і скільки прози втратив би текст, якби відповідь прийняли. */
    ctx.set("layout", { ok, attempts: attempt, why: ok ? [] : why, gaveUp: !ok || !!shrank, shrank });
  }

  /* ── 7 · ФОРМУЛИ · агент, один раз ─────────────────────────────────────── */
  if (!ctx.get("formulas") && (u.type === "article" || u.type === "math")) {
    const text = LOC.assemble(parts.map((p) => p.text));
    const lines = text.split("\n").filter((l) => /[=≈]\s*[-\d]/.test(l)).slice(0, 60).join("\n");
    if (lines) {
      const res = await ctx.call("формули", () => ask(P.formulas(u, { lines }), "формули"));
      ctx.set("formulas", R.lines(R.blocks(res)["ЗАМІНИ"] || ""));
    } else ctx.set("formulas", []);
  }

  /* ── 7б · КОД C і C++ · агент, тексту не бачить ─────────────────────────── */
  if (!ctx.get("code") && k.code.length) {
    const langs = [...new Set(k.code.map((c) => c.lang))].join(", ");
    const res = await ctx.call("код c/c++", () => ask(P.codeLangs(u, { dir: u.dir, langs }), "код c/c++"));
    const b = R.blocks(res);
    const want = [];
    if (R.yes(b["C"])) want.push("c");
    if (R.yes(b["CPP"])) want.push("cpp");
    ctx.set("code", { c: b["C"] || "", cpp: b["CPP"] || "", want });
    /* «Так» → код на цю мову стає ОКРЕМОЮ одиницею в черзі батчу. */
    if (want.length) ctx.enqueue(want.map((l) => ({
      ...LOC.unitOf(u.book, u.slug, "code", ""),
      id: `${u.book}/${u.slug}:code-${l}`, type: "code", lang: l,
      about: `те саме, що вже є мовами ${langs}, — мовою ${l}`,
      carrier: u.file.replace(/\.md$/, ""), parent: u.id,
    })));
  }

  /* ── 8 · ВІДКЛАДЕНЕ ────────────────────────────────────────────────────── */
  if (!ctx.get("deferred")) {
    ctx.set("deferred", {
      newTopics: [
        ...k.inserts.filter((x) => x.kind === 1).map((x) => `${x.about} (назвав каркас)`),
        ...parts.flatMap((p) => (p.newTopics || []).map((t) => `${t} (назвав письменник)`)),
        ...k.missingTopics.map((t) => `${t} (назвав каркас, з переліку книг)`),
      ],
      basicNeeded: null,   // рішення про базову — окремим кроком батчу
    });
  }

  /* ── 9 · ЗІБРАННЯ · локально ───────────────────────────────────────────── */
  if (!ctx.get("figures")) {
    const file = LOC.writeArticle(u, LOC.assemble(parts.map((p) => p.text)));
    ctx.set("figures", { file });
  }

  /* ── 10 · ОПЕРАЦІЇ В МАНІФЕСТ ──────────────────────────────────────────── */
  if (!ctx.get("ops")) ctx.set("ops", LOC.ops(u, o.status || "recheck"));

  return { file: ctx.get("figures").file, ops: ctx.get("ops") };
}

/* ── код як одиниця ────────────────────────────────────────────────────────── */

/**
 * Одиниці коду з каркаса: по одній на МОВУ, бо тека мови — корінь проєкту, і два
 * рядки каркаса на одну мову — це два файли одного проєкту, а не два проєкти.
 * Носій — файл статті, що на код посилається: саме він дає ім'я теці.
 */
function codeUnitsOf(u, k) {
  const byLang = new Map();
  for (const c of k.code || []) {
    const lang = String(c.lang || "").trim().toLowerCase();
    if (!lang) continue;
    if (!byLang.has(lang)) byLang.set(lang, []);
    byLang.get(lang).push(`розділ ${c.section}: ${c.what}`);
  }
  return [...byLang.entries()].map(([lang, what]) => ({
    ...LOC.unitOf(u.book, u.slug, "code", ""),
    id: `${u.book}/${u.slug}:code-${lang}`,
    type: "code", lang, about: what.join("\n"),
    carrier: u.file.replace(/\.md$/, ""), parent: u.id,
  }));
}

/**
 * Дорога коду: ціль → архітектура → файли на диск. Ті самі поля стану, що й у
 * статті, — «sections» тут це файли, «figures» — що записано. У маніфест код не
 * йде: його реєструє посилання `:::code` у прозі, тож `ops` порожні НАВМИСНО.
 */
async function codeAlgorithm(u, ctx, o) {
  const ask = o.ask;

  if (!ctx.get("prep")) ctx.set("prep", { carrier: u.carrier, lang: u.lang, about: u.about });

  if (!ctx.get("goal")) {
    const res = await ctx.call("ціль", () => ask(P.goal(u, { mentions: "" }), "ціль"));
    const d = need(res, ["ЦІЛЬ"], "ціль");
    const lv = R.blocks(res)["РІВЕНЬ"];
    ctx.set("goal", { text: d["ЦІЛЬ"], level: lv ? parseInt(lv, 10) || null : null });
  }
  const goal = ctx.get("goal");

  if (!ctx.get("karkas")) {
    const res = await ctx.call("архітектура", () => ask(P.karkas(u, {
      goal: goal.text, level: goal.level, preknow: "", books: "",
    }), "архітектура"));
    const b = R.blocks(res);
    const files = R.lines(b["ФАЙЛИ"] || "");
    if (!files.length) throw new Error("архітектура: не повернула жодного файла");
    ctx.set("karkas", { files, classes: R.lines(b["КЛАСИ"] || ""), structure: b["СТРУКТУРА"] || "" });
  }
  const k = ctx.get("karkas");

  if (!ctx.get("sections")) {
    const res = await ctx.call("код", () => ask(P.codeWrite(u, {
      goal: goal.text, level: goal.level,
      files: k.files.join("\n"), classes: k.classes.join("\n"), structure: k.structure,
    }), "код"));
    const files = R.files(res);
    if (!files.length) throw new Error("код: у відповіді немає жодного блоку <ФАЙЛ>");
    ctx.set("sections", files);
  }

  if (!ctx.get("figures")) ctx.set("figures", { files: LOC.writeCode(u, ctx.get("sections")) });
  if (!ctx.get("ops")) ctx.set("ops", []);
  return { files: ctx.get("figures").files, ops: [] };
}

module.exports = { algorithm, codeAlgorithm, codeUnitsOf, MAX_LAYOUT, MAX_SIZE_ROUNDS };
