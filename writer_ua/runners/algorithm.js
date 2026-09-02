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
const MAX_SIZE_ROUNDS = 2; // скільки разів дописуємо за розміром

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
      dupeHints: dup.hints,
    });
  }
  const prep = ctx.get("prep");

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
      preknow: LOC.preknow(u), books: LOC.books(),
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
  if (!ctx.get("sections")) {
    const more = [];
    for (const ins of k.inserts.filter((x) => x.kind === 2))
      more.push({ ...LOC.unitOf(u.book, u.slug, ins.insert, ""), about: ins.about, section: ins.section });
    for (const c of k.code)
      more.push({ ...LOC.unitOf(u.book, u.slug, "code", ""), id: `${u.book}/${u.slug}:code-${c.lang.toLowerCase()}`, lang: c.lang, about: c.what, section: c.section });
    if (more.length) ctx.enqueue(more);
  }

  /* ── 4 · ПИСЬМО · агенти, групами ──────────────────────────────────────── */
  if (!ctx.get("sections")) {
    const written = [];
    let theses = [];
    for (const g of k.groups) {
      const mine = k.sections.filter((s) => g.includes(s.n));
      const bound = [...k.inserts.filter((x) => x.kind === 2 && g.includes(x.section))
        .map((x) => `розділ ${x.section}: вставка «${x.about}» — інтегрувати як вставку`),
      ...k.code.filter((c) => g.includes(c.section))
        .map((c) => `розділ ${c.section}: код ${c.lang} — інтегрувати посиланням на файли`)].join("\n");

      const res = await ctx.call(`письмо ${g.join(",")}`, () => ask(P.write(u, {
        goal: goal.text, level: goal.level,
        sections: mine.map((s) => `${s.n} | важливість: ${s.importance} | ${s.text}`).join("\n"),
        theses: theses.join("\n"), inserts: bound,
      }), `письмо ${g.join(",")}`));

      const d = need(res, ["ТЕКСТ"], `письмо ${g.join(",")}`);
      const b = R.blocks(res);
      theses = theses.concat(R.lines(b["ТЕЗИ"] || ""));
      written.push({
        group: g, text: d["ТЕКСТ"], theses: R.lines(b["ТЕЗИ"] || ""),
        deeper: b["ЧИ ГЛИБШЕ"] || "", full: b["ЧИ ПОВНО"] || "",
        add: R.empty(b["ЩО ДОДАТИ"]) ? "" : b["ЩО ДОДАТИ"],
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
      /* ⚠️ Пастка: дописуємо не «до числа», а НАЗВАНИМ матеріалом. Нема чого назвати —
         рахуємо як пройдене й більше сюди не повертаємось. */
      const hungry = parts.filter((p) => p.add);
      if (!hungry.length) break;
      for (const p of hungry) {
        const res = await ctx.call(`дописування ${p.group.join(",")}`, () => ask(P.extend(u, {
          goal: goal.text, level: goal.level,
          section: p.group.join(", "), text: p.text,
          neighbours: parts.filter((x) => x !== p).flatMap((x) => x.theses).join("\n"),
          add: p.add, howMuch: s.shortBy > 40 ? "повністю" : "трохи",
        }), `дописування ${p.group.join(",")}`));
        const d = need(res, ["ТЕКСТ"], "дописування");
        const b = R.blocks(res);
        p.text = d["ТЕКСТ"];
        p.theses = R.lines(b["ТЕЗИ"] || p.theses.join("\n"));
        p.add = R.empty(b["ЩО ДОДАТИ"]) ? "" : b["ЩО ДОДАТИ"];
      }
      rounds++;
      s = LOC.size(LOC.assemble(parts.map((x) => x.text)), u.type, goal.level);
    }
    ctx.set("size", { ...s, rounds });
    ctx.set("sections", parts);
  }

  /* ── 6 · ВИКЛАДКА · агент, до 7 кіл ────────────────────────────────────── */
  if (!ctx.get("layout")) {
    let attempt = 0, ok = false, why = [];
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
      parts = [{ group: parts.flatMap((p) => p.group), text: d["ТЕКСТ"], theses: parts.flatMap((p) => p.theses), add: "" }];
      ctx.set("sections", parts);
    }
    /* Вичерпали спроби — вважаємо написаною, і випадок іде в лог помилок батчу. */
    ctx.set("layout", { ok, attempts: attempt, why: ok ? [] : why, gaveUp: !ok });
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
      id: `${u.book}/${u.slug}:code-${l}`, lang: l, about: `код мовою ${l}`,
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

module.exports = { algorithm, MAX_LAYOUT, MAX_SIZE_ROUNDS };
