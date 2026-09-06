#!/usr/bin/env node
/* ============================================================================
   algorithm.js — ВНУТРІШНІЙ РІВЕНЬ: десять етапів над ОДНІЄЮ одиницею.

   Специфікація — `../ALGORITHM.md`, словами автора; тут лише її виконання. Оркестратор
   дає чергу й стан, цей файл робить із однієї одиниці один файл. Через `ctx` приходить:

     ctx.set(поле, значення)   заповнити етап; null — етап треба пройти знову
     ctx.call(мітка, fn)       ОДИН запит до агента, з межею очікування
     ctx.enqueue(одиниці)      докласти в чергу: вставки, код, фігури, базову
     ctx.isDone(id)            чи завершена інша одиниця

   Локальне робиться локально: підготовка, розмір, рахунок дописування, збірка, сита —
   `local.js`, нуль токенів. Агента кличемо лише там, де потрібне судження. Жодного
   речення для агента тут немає — усі накази у файлах `rules/`, збирає їх `prompt.js`.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const P = require("./prompt.js");
const R = require("./parse.js");
const LOC = require("./local.js");
const MF = require("../lib/manifest.js");

const MAX_EXTEND = 5;        // кіл дописування — стільки разів намагаємось добити рівень
const MAX_COMPRESS = 5;      // кіл стиснення, дзеркально
const MAX_REWRITE = 3;       // переписувань з нуля; на третьому приймаємо як є
const MAX_FIG_ROUNDS = 4;    // перемальовувань фігури за геометрією
const PASS_SCORE = 7;        // оцінка аналізу: сім і вище — етап пройдено
const FLOOR = { 5: 300, 4: 300, 3: 250, 2: 250, 1: 150 };   // підлога дописування на розділ
const CEIL_X = 4;            // стеля дописування — вчетверо більша за підлогу
const FORCE_SHORT = 1 / 3;   // бракує понад третину — аналіз мусить назвати, де дописати
const BASIC_OVER = 1.5;      // детальна довша за стелю базової в півтора раза → базова обов'язкова
const KEEP_SHARE = 0.9;      // відповідь, що з'їла більше десятої частини прози, не приймається

/** Обов'язкові блоки: немає — це помилка кроку, а не привід вгадувати. */
function need(res, tags, where) {
  const got = R.want(res, tags);
  if (got.missing.length) throw new Error(`${where}: у відповіді немає ${got.missing.join(", ")}`);
  return got.data;
}

const words = (text) => LOC.size(text, "article", 2).words;
const assemble = (parts) => LOC.assemble(parts.map((p) => p.text));
const num = (s) => Number((String(s || "").match(/\d+/) || [])[0]);
const numOr = (s, d) => (Number.isFinite(num(s)) ? num(s) : d);

/* ── дописування: скільки і в який розділ ─────────────────────────────────── */

/**
 * План дописування за рівнями важливості: розділи з найвищим наявним рівнем беруть усе,
 * і лише коли їхньої стелі на дефіцит не вистачає, додається наступний рівень. Кожен
 * обраний дістає щонайменше свою підлогу, решта дефіциту ділиться пропорційно, стеля —
 * вчетверо більша за підлогу.
 */
function plan(deficit, parts) {
  const bySec = new Map();
  for (const p of parts) for (const a of p.add || []) {
    const sec = a.section == null ? p.group[0] : a.section;
    if (!p.group.includes(sec)) continue;
    const cur = bySec.get(sec);
    if (!cur || a.level > cur.level) bySec.set(sec, { section: sec, level: a.level, items: [a.what], part: p });
    else if (a.level === cur.level) cur.items.push(a.what);
  }
  const secs = [...bySec.values()].sort((a, b) => b.level - a.level);
  if (!secs.length) return [];
  const chosen = [];
  let cap = 0, lvl = null;
  for (const s of secs) {
    if (lvl !== null && s.level < lvl && cap >= deficit) break;
    lvl = s.level;
    chosen.push(s);
    cap += FLOOR[s.level] * CEIL_X;
  }
  const sumF = chosen.reduce((a, s) => a + FLOOR[s.level], 0);
  const extra = Math.max(0, deficit - sumF);
  return chosen.map((s) => {
    const f = FLOOR[s.level];
    return { ...s, floor: Math.min(f * CEIL_X, Math.round(f + extra * (f / sumF))), ceiling: f * CEIL_X };
  });
}

/** Розділ усередині тексту групи: за H2 і порядком номерів; не розбилось — увесь текст. */
function sectionOf(part, sec) {
  const secs = LOC.splitSections(part.text);
  const i = part.group.indexOf(sec);
  if (secs.length === part.group.length && i >= 0) return { secs, i };
  return { secs: [{ head: "", body: part.text }], i: 0 };
}
function putSection(part, ref, text) {
  const t = String(text || "").trim();
  const m = /^(## [^\n]*)\n([\s\S]*)$/.exec(t);
  ref.secs[ref.i] = m ? { head: m[1], body: m[2].trim() } : { head: ref.secs[ref.i].head, body: t };
  part.text = LOC.joinSections(ref.secs);
}
const sectionText = (ref) => [ref.secs[ref.i].head, ref.secs[ref.i].body].filter(Boolean).join("\n\n");

const planOf = (k, sec) => {
  const s = k.sections.find((x) => x.n === sec);
  return s ? `${s.n} | важливість: ${s.importance} | ${s.text}` : String(sec);
};
const thesesText = (parts, except) => parts.flatMap((p) => p.theses || [])
  .filter((t) => except == null || t.section !== except)
  .map((t) => `${t.section == null ? "" : t.section + " | "}${t.text}`).join("\n");

/** Прийняти нову версію розділу лише коли вона не з'їла написане. */
const keeps = (before, after) => words(after) >= words(before) * KEEP_SHARE;

/** Оновити оцінки розділу після дописування чи стиснення — старі рядки про нього геть. */
function refresh(part, sec, b) {
  const own = (x) => (x.section == null ? part.group[0] : x.section) === sec;
  part.add = [...(part.add || []).filter((a) => !own(a)), ...R.additions(b["ЩО ДОДАТИ"] || "")];
  part.squeeze = [...(part.squeeze || []).filter((q) => !own(q)), ...R.bySection(b["ЩО ЗЖАТИ"] || "")];
  const th = R.bySection(b["ТЕЗИ"] || "");
  if (th.length) part.theses = [...(part.theses || []).filter((t) => !own(t)), ...th];
  part.newTopics = [...(part.newTopics || []), ...R.topics(b["НОВІ ТЕМИ"] || "")];
  part.newFigs = [...(part.newFigs || []), ...R.figures(b["НОВІ SVG"] || "")];
}

/* ── фігури ────────────────────────────────────────────────────────────────── */

const figId = (u, f) => `${u.book}/${u.slug}:${f.file.replace(/^img\//, "").replace(/\.svg$/, "")}`;

/** Усі фігури теми з іменами: спершу каркасні, тоді названі письмом — імена сталі. */
const allFigs = (k, parts) => LOC.figNames([...(k.figs || []), ...(parts || []).flatMap((p) => p.newFigs || [])]);

function figUnitsOf(u, figs, goal, level) {
  return (figs || []).filter((f) => !f.fromDetailed).map((f) => ({
    ...LOC.unitOf(u.book, u.slug, "fig", ""),
    id: figId(u, f), type: "fig", figFile: f.file, section: f.section, about: f.what,
    goal: (goal && goal.text) || "", level: level || null, parent: u.id,
  }));
}

/* ── код ───────────────────────────────────────────────────────────────────── */

/** Одиниці коду з каркаса проєкту: по одній на мову; тека мови — корінь проєкту. */
function codeUnitsOf(u, code, level) {
  const byLang = new Map();
  for (const c of code || []) {
    const lang = String(c.lang || "").trim().toLowerCase();
    if (!lang) continue;
    if (!byLang.has(lang)) byLang.set(lang, []);
    byLang.get(lang).push(c.what);
  }
  return [...byLang.entries()].map(([lang, what]) => ({
    ...LOC.unitOf(u.book, u.slug, "code", ""),
    id: `${u.book}/${u.slug}:code-${lang}`,
    type: "code", lang, level, about: what.join("\n"),
    carrier: u.file.replace(/\.md$/, ""), parent: u.id,
  }));
}

/** Що письмо має інтегрувати: вставки з адресами, фігури без місця, файли коду. */
function integrateList(u, inserts, figs, used, code) {
  const rows = [];
  for (const x of inserts || [])
    rows.push(`вставка ${x.insert}-${x.name} — ${x.about}\n  лінк рівно такий: root:${u.book}/${u.slug}/${x.insert}-${x.name}.md`);
  for (const f of figs || []) if (!used.has(f.file))
    rows.push(`фігура — ${f.what}\n  постав рівно так: ![що показано і що з неї видно](${f.file})`);
  for (const c of code || []) {
    const files = LOC.codeFiles(u, c.lang);
    if (files.length) rows.push(`код ${c.lang} — ${c.what}\n${files.map((f) => `  :::code ${f}`).join("\n")}`);
  }
  return rows.join("\n\n");
}

const readDetailed = (u) => {
  try { return fs.readFileSync(path.join(u.dir, `${u.slug}-d.md`), "utf8"); } catch { return ""; }
};

/* ── алгоритм прози: стаття, базова, вставки ───────────────────────────────── */

async function algorithm(unit, ctx, o = {}) {
  const ask = o.ask;
  if (typeof ask !== "function") throw new Error("немає ask() — нічим питати агента");
  const u = unit;
  if (u.type === "code") return codeAlgorithm(u, ctx, o);
  if (u.type === "fig") return figAlgorithm(u, ctx, o);

  const article = u.type === "article", basic = u.type === "basic";
  const detailed = basic ? readDetailed(u) : "";
  if (basic && !detailed) throw new Error("базова без детальної: спершу пишеться детальна");

  /* ── 1 · ПІДГОТОВКА · локально ─────────────────────────────────────────── */
  if (!ctx.get("prep")) {
    const dup = LOC.isDuplicate(u.book, u.slug);
    if (dup.written && article) throw new Error("тема вже написана — це дубль, писати нічого");
    ctx.set("prep", {
      mentions: LOC.mentions(u, o.mentionRe || LOC.titleRe(u.title)),
      passed: LOC.preknow(u),
      dupeHints: dup.hints,
    });
  }
  const prep = ctx.get("prep");
  const passed = prep.passed || "";

  /* ── 1 · ЦІЛЬ · агент ──────────────────────────────────────────────────── */
  if (!ctx.get("goal")) {
    const res = await ctx.call("ціль", () => ask(P.goal(u, {
      mentions: prep.mentions, passed, linkable: LOC.linkable(u),
      about: u.about || (basic ? detailed : ""),
    }), "ціль"));
    const d = need(res, ["ЦІЛЬ"], "ціль");
    ctx.set("goal", { text: d["ЦІЛЬ"], preknow: article ? R.preknow(R.blocks(res)["ПЕРЕДУМОВИ"] || "") : [] });
  }
  const goal = ctx.get("goal");

  /* ── 2 · СТРУКТУРА · агент — лише детальна ─────────────────────────────── */
  if (article && !ctx.get("structure")) {
    const res = await ctx.call("структура", () => ask(P.structure(u, { goal: goal.text, shelf: LOC.shelf() }), "структура"));
    const b = R.blocks(res);
    const st = { inserts: R.inserts(b["ВСТАВКИ"] || ""), newTopics: R.topics(b["НОВІ ТЕМИ"] || ""), basic: R.yes(b["БАЗОВА"]) };
    ctx.set("structure", st);
    /* Вставки — у чергу одразу, паралельно: стаття на них не чекає. */
    if (st.inserts.length)
      ctx.enqueue(st.inserts.map((x) => ({
        ...LOC.unitOf(u.book, u.slug, x.insert, "", `${x.insert}-${x.name}`), about: x.about, parent: u.id,
      })));
  }
  const st = ctx.get("structure") || { inserts: [], newTopics: [], basic: false };

  /* ── 3 · КАРКАС · агент ────────────────────────────────────────────────── */
  if (!ctx.get("karkas")) {
    const res = await ctx.call("каркас", () => ask(P.karkas(u, {
      goal: goal.text, passed, detailed,
      inserts: st.inserts.map((x) => `${x.insert}-${x.name}: ${x.about}`).join("\n"),
    }), "каркас"));
    const b = R.blocks(res);
    const secs = R.sections(b["РОЗДІЛИ"] || b["КРОКИ"] || b["ПОДІЇ"] || "");
    if (!secs.length) throw new Error("каркас: не повернув жодного розділу");
    const lv = num(b["РІВЕНЬ"]);
    const rawFigs = R.figures(b["ФІГУРИ"] || "");
    const k = {
      level: lv >= 1 && lv <= 3 ? lv : null,
      sections: secs, depth: b["ГЛИБИНА"] || "",
      groups: R.groups(b["ГРУПИ"] || "").length ? R.groups(b["ГРУПИ"]) : [secs.map((s) => s.n)],
      /* Базова бере фігури з детальної — готові файли; малювати їй нічого. */
      figs: basic ? rawFigs.map((f) => ({ ...f, file: f.what.replace(/^.*?(img\/)/, "img/"), fromDetailed: true }))
        : LOC.figNames(rawFigs),
      code: u.type === "proj" ? R.code(b["КОД"] || "") : [],
    };
    ctx.set("karkas", k);
    /* Фігури й код — у чергу тут; фігури нічого не затримують, код чекає лише проєкт. */
    const more = [...codeUnitsOf(u, k.code, k.level), ...figUnitsOf(u, k.figs, goal, k.level)];
    if (more.length) ctx.enqueue(more);
  }
  const k = ctx.get("karkas");
  const codeUnits = codeUnitsOf(u, k.code, k.level);

  /* ⏸ Проєкт пояснює код, якого ще нема, — тож спить, доки код не напишуть. */
  if (u.type === "proj" && !ctx.get("sections")) {
    const waitFor = codeUnits.map((c) => c.id).filter((id) => !ctx.isDone(id));
    if (waitFor.length)
      throw Object.assign(new Error(`чекає на код: ${waitFor.join(", ")}`), { pause: true, waitFor });
  }

  const common = () => ({ goal: goal.text, level: k.level, depth: k.depth, linkable: LOC.linkable(u) });
  let parts;

  /* ── 4–5 · ПИСЬМО → РОЗМІР → АНАЛІЗ, по колу переписування ────────────── */
  for (;;) {
    /* ── 4 · ПИСЬМО · агенти, порціями ─────────────────────────────────── */
    if (!ctx.get("sections")) {
      const written = [];
      const used = new Set();
      for (const g of k.groups) {
        const mine = k.sections.filter((s) => g.includes(s.n));
        const res = await ctx.call(`письмо ${g.join(",")}`, () => ask(P.write(u, {
          ...common(),
          sections: mine.map((s) => `${s.n} | важливість: ${s.importance} | ${s.text}`).join("\n"),
          theses: thesesText(written), passed,
          integrate: integrateList(u, st.inserts, k.figs, used, k.code),
        }), `письмо ${g.join(",")}`));
        const d = need(res, ["ТЕКСТ"], `письмо ${g.join(",")}`);
        const b = R.blocks(res);
        for (const f of k.figs) if (d["ТЕКСТ"].includes(f.file)) used.add(f.file);
        const part = { group: g, text: d["ТЕКСТ"], theses: [], add: [], squeeze: [], newTopics: [], newFigs: [] };
        refresh(part, null, b);
        written.push(part);
      }
      ctx.set("sections", written);
      /* Фігури, названі письмом, — теж у чергу, тим самим ходом. */
      const extra = allFigs(k, written).slice(k.figs.length);
      if (extra.length) ctx.enqueue(figUnitsOf(u, extra, goal, k.level));
    }
    parts = ctx.get("sections");

    /* ── 5 · РОЗМІР · локально → дописування / стиснення ───────────────── */
    if (!ctx.get("size")) {
      let s = LOC.size(assemble(parts), u.type, k.level);
      let rounds = 0, forced = false;
      while (s.words < s.need && rounds < MAX_EXTEND) {
        const deficit = s.need - s.words;
        let todo = plan(deficit, parts);
        /* Бракує понад третину або нема названого — аналіз мусить показати місця. */
        if (!todo.length || (!forced && deficit / s.need > FORCE_SHORT)) {
          forced = true;
          const res = await ctx.call(`де дописати ${rounds + 1}`, () => ask(P.analysis(u, {
            ...common(), text: assemble(parts), theses: thesesText(parts),
            groups: k.groups.map((g) => g.join(", ")).join("\n"), force: true,
          }), `де дописати ${rounds + 1}`));
          for (const w of R.bySection(R.blocks(res)["ДЕ ДОПИСАТИ"] || "")) {
            const p = parts.find((x) => x.group.includes(w.section)) || parts[0];
            p.add = [...(p.add || []), { section: w.section == null ? p.group[0] : w.section, level: 5, what: w.text }];
          }
          todo = plan(deficit, parts);
          if (!todo.length) break;
        }
        for (const t of todo) {
          const ref = sectionOf(t.part, t.section);
          const before = sectionText(ref);
          const res = await ctx.call(`дописування ${t.section}`, () => ask(P.extend(u, {
            ...common(), section: planOf(k, t.section), text: before,
            theses: thesesText(parts, t.section), add: t.items.map((x) => `${t.section} | ${t.level} | ${x}`).join("\n"),
            floor: t.floor, ceiling: t.ceiling,
            integrate: integrateList(u, st.inserts, allFigs(k, parts), new Set(allFigs(k, parts).filter((f) => assemble(parts).includes(f.file)).map((f) => f.file)), k.code),
          }), `дописування ${t.section}`));
          const d = need(res, ["ТЕКСТ"], "дописування");
          if (!keeps(before, d["ТЕКСТ"])) continue;   // з'їло написане — лишаємо як було
          putSection(t.part, ref, d["ТЕКСТ"]);
          refresh(t.part, t.section, R.blocks(res));
        }
        rounds++;
        s = LOC.size(assemble(parts), u.type, k.level);
      }

      let squeezed = 0;
      const cantCut = [], splitOff = [];
      while (s.over && squeezed < MAX_COMPRESS) {
        const fat = parts.flatMap((p) => (p.squeeze || []).map((q) => ({ part: p, section: q.section == null ? p.group[0] : q.section, what: q.text })))
          .filter((q) => q.part.group.includes(q.section));
        if (!fat.length) break;
        const by = Math.ceil((s.words - s.ceiling) / fat.length);
        for (const q of fat) {
          const ref = sectionOf(q.part, q.section);
          const res = await ctx.call(`стиснення ${q.section}`, () => ask(P.compress(u, {
            ...common(), section: planOf(k, q.section), text: sectionText(ref),
            theses: thesesText(parts, q.section), squeeze: q.what, by,
          }), `стиснення ${q.section}`));
          const d = need(res, ["ТЕКСТ"], "стиснення");
          const b = R.blocks(res);
          putSection(q.part, ref, d["ТЕКСТ"]);
          q.part.squeeze = (q.part.squeeze || []).filter((x) => (x.section == null ? q.part.group[0] : x.section) !== q.section);
          for (const x of R.bySection(b["ЩО ЗЖАТИ"] || "")) q.part.squeeze.push({ section: q.section, text: x.text });
          if (!R.empty(b["НЕ РІЖЕТЬСЯ"])) { cantCut.push(`розділ ${q.section}: ${b["НЕ РІЖЕТЬСЯ"]}`); q.part.squeeze = q.part.squeeze.filter((x) => x.section !== q.section); }
          splitOff.push(...R.topics(b["ОКРЕМА ТЕМА"] || ""));
        }
        squeezed++;
        s = LOC.size(assemble(parts), u.type, k.level);
      }
      ctx.set("sections", parts);
      ctx.set("size", { ...s, rounds, squeezed, forced, stillShort: s.words < s.need, stillOver: s.over, cantCut, splitOff });
      const extra = allFigs(k, parts).slice(k.figs.length).filter((f) => !ctx.isDone(figId(u, f)));
      if (extra.length) ctx.enqueue(figUnitsOf(u, extra, goal, k.level));
    }

    /* ── 5 · АНАЛІЗ · агент: оцінки; шість і нижче — з нуля, до трьох разів ── */
    const an = ctx.get("analysis") || { rewrites: 0, history: [], done: false };
    if (an.done) break;
    const res = await ctx.call(`аналіз ${an.rewrites + 1}`, () => ask(P.analysis(u, {
      ...common(), text: assemble(parts), theses: thesesText(parts),
      groups: k.groups.map((g) => g.join(", ")).join("\n"), force: false,
    }), `аналіз ${an.rewrites + 1}`));
    const b = R.blocks(res);
    const score = numOr(b["ОЦІНКА"], NaN);
    const groups = R.scores(b["ОЦІНКИ"] || "");
    const facts = [...R.lines(b["ІСТОРІЯ"] || ""), ...R.lines(b["ФОРМУЛИ"] || "")].filter((x) => !R.empty(x));
    const history = [...an.history, Number.isFinite(score) ? score : null];
    const pass = !Number.isFinite(score) || score >= PASS_SCORE;
    if (pass || an.rewrites >= MAX_REWRITE) {
      ctx.set("analysis", { done: true, score, groups, facts, rewrites: an.rewrites, history, forced: !pass });
      break;
    }
    /* Забудь усе, що писав: етап 4 із самого початку. */
    ctx.set("analysis", { done: false, rewrites: an.rewrites + 1, history });
    ctx.set("sections", null);
    ctx.set("size", null);
  }
  const an = ctx.get("analysis");

  /* ── 5 · ФАКТИ · агент: веб-перевірка речень, заміна на місці ──────────── */
  if (!ctx.get("facts")) {
    const lines = an.facts || [];
    let reps = [];
    if (lines.length) {
      const res = await ctx.call("факти", () => ask(P.facts(u, { lines: lines.join("\n") }), "факти"));
      reps = R.replacements(R.blocks(res)["ЗАМІНИ"] || "");
    }
    let applied = 0;
    for (const p of parts) for (const r of reps)
      if (p.text.includes(r.from)) { p.text = p.text.split(r.from).join(r.to); applied++; }
    ctx.set("sections", parts);
    ctx.set("facts", { asked: lines.length, returned: reps.length, applied });
  }

  /* ── 6 · ФІГУРИ · поставити ті, що лишились без місця ──────────────────── */
  if (!ctx.get("figures")) {
    const figs = allFigs(k, parts);
    const placed = [], unplaced = [];
    for (const f of figs) {
      if (assemble(parts).includes(f.file)) continue;
      const r1 = await ctx.call(`фігура куди ${f.file}`, () => ask(P.imageWhere(u, { text: assemble(parts), what: f.what }), `фігура куди ${f.file}`));
      const sec = numOr(R.blocks(r1)["РОЗДІЛ"], f.section);
      const part = parts.find((p) => p.group.includes(sec)) || parts[0];
      const r2 = await ctx.call(`фігура постав ${f.file}`, () => ask(P.imagePlace(u, { text: part.text, section: sec, file: f.file, what: f.what }), `фігура постав ${f.file}`));
      const t = String(R.blocks(r2)["ТЕКСТ"] || "").trim();
      if (t.includes(f.file) && keeps(part.text, t)) { part.text = t; placed.push(f.file); }
      else unplaced.push(f.file);
    }
    ctx.set("sections", parts);
    ctx.set("figures", {
      all: figs.map((f) => f.file), placed, unplaced,
      pending: figs.filter((f) => !f.fromDetailed).map((f) => figId(u, f)).filter((id) => !ctx.isDone(id)),
    });
  }

  /* ── 8 · НОВІ ТЕМИ · зведення: куди, чи є, чи розвести назви ──────────── */
  if (!ctx.get("topics")) {
    const seen = new Set();
    const named = [...(st.newTopics || []), ...parts.flatMap((p) => p.newTopics || []), ...((ctx.get("size") || {}).splitOff || [])]
      .filter((t) => t && t.slug && !seen.has(t.slug) && seen.add(t.slug));
    const ops = [], links = {}, notes = [];
    const shelfText = named.length ? LOC.shelf() : "";
    for (const t of named) {
      const desc = [t.title, t.about, t.where ? `інтуїтивно: ${t.where}` : ""].filter(Boolean).join("\n");
      const r1 = await ctx.call(`тема куди ${t.slug}`, () => ask(P.topicsCategory({ shelf: shelfText, topic: desc }), `тема куди ${t.slug}`));
      const b1 = R.blocks(r1);
      let book = String(b1["КНИГА"] || "").trim().toLowerCase();
      let group = String(b1["ГРУПА"] || "").trim().toLowerCase();
      let chapter = String(b1["РОЗДІЛ"] || "").trim().toLowerCase();
      const bk = MF.books().get(book) ? MF.loadBook(MF.bookDirOf(book)) : null;
      if (!bk || !bk.groups.has(group)) {
        notes.push(`${t.slug}: категорія «${book}/${group}» не з переліку — покладено поруч із темою`);
        book = u.book; group = u.group; chapter = u.chapter;
      }
      /* Розділ теж лише з переліку: чужий слуг завів би в маніфесті новий розділ. */
      const chapters = ((MF.loadBook(MF.bookDirOf(book)).groups.get(group) || { data: {} }).data.chapters || []).map((c) => c.slug);
      if (!chapters.includes(chapter)) {
        const fallback = group === u.group ? u.chapter : chapters[0];
        if (fallback) { notes.push(`${t.slug}: розділ «${chapter}» не з переліку — покладено в «${fallback}»`); chapter = fallback; }
      }
      const existing = LOC.chapterTopics(book, group, chapter);
      const r2 = await ctx.call(`тема чи є ${t.slug}`, () => ask(P.topicsDedupe({
        existing: existing.map((x) => `${x.slug} — ${x.title}`).join("\n") || "(розділ порожній)", topic: desc,
      }), `тема чи є ${t.slug}`));
      const v = R.verdict(R.blocks(r2)["ВЕРДИКТ"]);
      const fresh = () => {
        ops.push({ op: "topic", book, slug: t.slug, title: t.title, group, chapter, basic: "empty", detailed: "pending" });
        links[t.slug] = `root:${book}/${t.slug}`;
      };
      if (v.kind === "є" && existing.some((x) => x.slug === v.slug)) {
        const r3 = await ctx.call(`тема розвести ${t.slug}`, () => ask(P.topicsRename({
          existing: `${v.slug}: ${LOC.topicHead(book, v.slug)}`,
          ours: LOC.linkContext(assemble(parts), t.slug) || desc,
          reason: `«${t.title}» і «${v.slug}» названо як одне поняття`,
        }), `тема розвести ${t.slug}`));
        const b3 = R.blocks(r3);
        if (R.verdict(b3["ВЕРДИКТ"]).kind === "різні") {
          for (const n of R.names(b3["НАЗВИ"] || "")) {
            if (n.slug === v.slug) ops.push({ op: "retitle", book, slug: v.slug, title: n.title });
            if (n.slug === t.slug) t.title = n.title;
          }
          fresh();
        } else { links[t.slug] = `root:${book}/${v.slug}`; notes.push(`${t.slug} — те саме, що ${v.slug}; лінк переведено`); }
      } else fresh();
    }
    for (const p of parts) p.text = LOC.resolveLinks(p.text, links);
    ctx.set("sections", parts);
    ctx.set("topics", { ops, links, notes, named: named.map((t) => t.slug) });
  }

  /* ── 9 · МЕХАНІЧНА ЗБІРКА · локально ───────────────────────────────────── */
  if (!ctx.get("assembly")) {
    const file = LOC.writeArticle(u, assemble(parts), goal.preknow);
    const abs = path.join(MF.ROOT, file);
    const frm = LOC.fixFormulas(abs);
    const moved = LOC.decamp(abs);
    const fen = { ...LOC.checkFences(abs), moved };
    const pending = (ctx.get("figures") || {}).pending || [];
    const svg = LOC.checkFigures(u.dir, { links: !pending.length });
    ctx.set("assembly", { file, formulas: frm, fences: fen, svg: { ...svg, pending } });
  }

  /* ── 10 · ЗАВЕРШЕННЯ · операції в маніфест, базова ─────────────────────── */
  if (!ctx.get("ops")) {
    const ops = [...LOC.ops(u, o.status || "recheck"), ...((ctx.get("topics") || {}).ops || [])];
    if (article && !u.insert) {
      const total = words(fs.readFileSync(path.join(MF.ROOT, ctx.get("assembly").file), "utf8"));
      const needBasic = total > LOC.BANDS.basic[3] * BASIC_OVER || !!st.basic;
      ops.push(needBasic
        ? { op: "status", slug: u.slug, ver: "basic", status: "pending" }
        : { op: "status-if", slug: u.slug, ver: "basic", from: "pending", to: "empty" });
      if (needBasic) ctx.enqueue([{ ...LOC.unitOf(u.book, u.slug, "basic", "базова"), parent: u.id }]);
    }
    ctx.set("ops", ops);
  }

  return { file: ctx.get("assembly").file, ops: ctx.get("ops") };
}

/* ── фігура як одиниця ─────────────────────────────────────────────────────── */

const wholeSvg = (s) => /<svg[\s>]/i.test(String(s || "")) && /<\/svg>/i.test(String(s || ""));

/** Намалювати → зміряти локально → перемалювати назване. У маніфест не йде. */
async function figAlgorithm(u, ctx, o) {
  const ask = o.ask;
  if (!ctx.get("prep")) ctx.set("prep", { file: u.figFile, section: u.section, what: u.about });
  if (!ctx.get("sections")) {
    const res = await ctx.call("фігура", () => ask(P.figure(u, {
      goal: u.goal, what: u.about, section: u.section, file: u.figFile, level: u.level,
    }), "фігура"));
    const d = need(res, ["SVG"], "фігура");
    if (!wholeSvg(d["SVG"])) throw new Error("фігура: у відповіді не цілий svg-файл");
    ctx.set("sections", { svg: d["SVG"] });
  }
  if (!ctx.get("figures")) {
    let svg = ctx.get("sections").svg;
    let file = LOC.writeFigure(u, u.figFile, svg);
    let iss = LOC.checkFigure(u, u.figFile), rounds = 0;
    while (iss.length && rounds < MAX_FIG_ROUNDS) {
      rounds++;
      const res = await ctx.call(`фігура-лад ${rounds}`, () => ask(P.figureFix(u, {
        what: u.about, file: u.figFile, svg, issues: iss.join("\n"), attempt: rounds,
      }), `фігура-лад ${rounds}`));
      const d = need(res, ["SVG"], "перемальовування");
      if (!wholeSvg(d["SVG"])) break;
      svg = d["SVG"];
      file = LOC.writeFigure(u, u.figFile, svg);
      iss = LOC.checkFigure(u, u.figFile);
    }
    ctx.set("figures", { file, issues: iss, rounds });
  }
  if (!ctx.get("ops")) ctx.set("ops", []);
  return { file: ctx.get("figures").file, ops: [] };
}

/* ── код як одиниця ────────────────────────────────────────────────────────── */

/** Ціль → архітектура → файли на диск. У маніфест не йде: його реєструє директива в прозі. */
async function codeAlgorithm(u, ctx, o) {
  const ask = o.ask;
  if (!ctx.get("prep")) ctx.set("prep", { carrier: u.carrier, lang: u.lang, about: u.about });
  if (!ctx.get("goal")) {
    const res = await ctx.call("ціль", () => ask(P.goal(u, { mentions: "", about: u.about }), "ціль"));
    ctx.set("goal", { text: need(res, ["ЦІЛЬ"], "ціль")["ЦІЛЬ"] });
  }
  const goal = ctx.get("goal");
  if (!ctx.get("karkas")) {
    const res = await ctx.call("архітектура", () => ask(P.codeKarkas(u, { goal: goal.text }), "архітектура"));
    const b = R.blocks(res);
    const files = R.lines(b["ФАЙЛИ"] || "");
    if (!files.length) throw new Error("архітектура: не повернула жодного файла");
    const lv = num(b["РІВЕНЬ"]);
    ctx.set("karkas", { level: lv >= 1 && lv <= 3 ? lv : u.level || null, files, classes: R.lines(b["КЛАСИ"] || ""), structure: b["СТРУКТУРА"] || "" });
  }
  const k = ctx.get("karkas");
  if (!ctx.get("sections")) {
    const res = await ctx.call("код", () => ask(P.codeWrite(u, {
      goal: goal.text, level: k.level,
      files: k.files.join("\n"), classes: k.classes.join("\n"), structure: k.structure,
    }), "код"));
    const files = R.files(res);
    if (!files.length) throw new Error("код: у відповіді немає жодного блоку <ФАЙЛ>");
    ctx.set("sections", files);
  }
  if (!ctx.get("assembly")) ctx.set("assembly", { files: LOC.writeCode(u, ctx.get("sections")) });
  if (!ctx.get("ops")) ctx.set("ops", []);
  return { files: ctx.get("assembly").files, ops: [] };
}

module.exports = {
  algorithm, codeAlgorithm, codeUnitsOf, figAlgorithm, figUnitsOf, figId, plan,
  MAX_EXTEND, MAX_COMPRESS, MAX_REWRITE, MAX_FIG_ROUNDS, PASS_SCORE, FLOOR, CEIL_X,
};
