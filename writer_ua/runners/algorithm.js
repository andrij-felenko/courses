#!/usr/bin/env node
/* ============================================================================
   algorithm.js — ВНУТРІШНІЙ РІВЕНЬ: десять етапів над ОДНІЄЮ одиницею.

   Тут лише виконання алгоритму, етап за етапом; правила для агента — у `rules/`. Оркестратор
   дає чергу й стан, цей файл робить із однієї одиниці один файл. Через `ctx` приходить:

     ctx.set(поле, значення)   заповнити етап; null — етап треба пройти знову
     ctx.call(мітка, fn)       ОДИН запит до агента, з межею очікування
     ctx.enqueue(одиниці)      докласти в чергу: вставки, код, фігури, базову
     ctx.isDone(id)            чи завершена інша одиниця

   Локальне робиться локально: підготовка, розмір, рахунок дописування, офлайн-сита,
   збірка — `local.js`, нуль токенів. Агента кличемо лише там, де потрібне судження.
   Жодного речення для агента тут немає — усі накази у файлах `rules/`, збирає `prompt.js`.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const P = require("./prompt.js");
const R = require("./parse.js");
const LOC = require("./local.js");
const MF = require("../lib/manifest.js");
const DUP = require("../lib/dupes.js");
const FRM = require("../checkers/formulas.js");

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
const GROUPS = { 1: 2, 2: 3, 3: 5 };   // груп письма за рівнем, коли каркас їх не дав; 5 на рівні 3 — автор
const IMP = { "висока": 3, "середня": 2, "низька": 1 };

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
 * План дописування: розділи в порядку рівня важливості (5→1), а між рівними — за
 * важливістю розділу з каркаса; беремо стільки, скільки треба, щоб підлоги покрили
 * дефіцит, — інших не чіпаємо. Кожен обраний дістає щонайменше свою підлогу, решта
 * дефіциту ділиться пропорційно, стеля — вчетверо більша за підлогу.
 */
function plan(deficit, parts, k) {
  const bySec = new Map();
  for (const p of parts) for (const a of p.add || []) {
    const sec = a.section == null ? p.group[0] : a.section;
    if (!p.group.includes(sec)) continue;
    const cur = bySec.get(sec);
    if (!cur || a.level > cur.level) bySec.set(sec, { section: sec, level: a.level, items: [a.what], part: p });
    else if (a.level === cur.level) cur.items.push(a.what);
  }
  const imp = (sec) => IMP[String(((k.sections || []).find((s) => s.n === sec) || {}).importance || "").toLowerCase()] || 0;
  const secs = [...bySec.values()].sort((a, b) => (b.level - a.level) || (imp(b.section) - imp(a.section)));
  if (!secs.length) return [];
  const chosen = [];
  let sum = 0;
  for (const s of secs) { chosen.push(s); sum += FLOOR[s.level]; if (sum >= deficit) break; }
  const extra = Math.max(0, deficit - sum);
  return chosen.map((s) => {
    const f = FLOOR[s.level];
    return { ...s, floor: Math.min(f * CEIL_X, Math.round(f + extra * (f / sum))), ceiling: f * CEIL_X };
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
/* Перша група тез не має — і їй сказано прямо, чому: читач ще нічого не знає (автор, 07.09). */
const NOTHING_YET = "нічого — це початок статті: читач ще нічого не знає";

/** Усі теми, які ця одиниця назвала новими: етап 2, письмо, винесене стисненням. Без повторів. */
function namedTopics(st, parts, ctx) {
  const seen = new Set();
  return [...(st.newTopics || []), ...parts.flatMap((p) => p.newTopics || []), ...((ctx.get("size") || {}).splitOff || [])]
    .filter((t) => t && t.slug && !seen.has(t.slug) && seen.add(t.slug));
}

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

/**
 * Офлайн-сита етапу 5, що повертають на дописування: розділ плану без тексту чи майже
 * порожній, формули в LaTeX, непарні роздільники. Кожна знахідка — пункт рівня 5 для свого
 * розділу; дописування його й закриває.
 */
function offline(parts) {
  const items = [];
  for (const p of parts) {
    const secs = LOC.splitSections(p.text);
    if (secs.length !== p.group.length) {
      items.push({ part: p, section: p.group[0], what: `у тексті розділів ${secs.length}, а в плані ${p.group.length}: кожен розділ плану — окремий H2 із власним текстом` });
      continue;
    }
    secs.forEach((s, i) => {
      const sec = p.group[i];
      if (words(s.body) < 40) items.push({ part: p, section: sec, what: "розділ майже порожній — розкрий те, що для нього заплановано" });
      const t = [s.head, s.body].join("\n");
      const ban = FRM.banned(t).length, del = FRM.delimiters(t).length;
      if (ban) items.push({ part: p, section: sec, what: `формули записано LaTeX (${ban}): перепиши їх за правилом формул — інлайн-код або код-блок` });
      if (del) items.push({ part: p, section: sec, what: `непарні роздільники формул (${del}): перепиши формули за правилом формул` });
    });
  }
  return items;
}

/** Групи письма, коли каркас їх не дав: рівномірно, кількістю за рівнем. */
function groupsFor(level, secs) {
  const n = secs.length;
  const g = Math.max(1, Math.min(n, GROUPS[level] || GROUPS[2]));
  const out = [];
  for (let i = 0; i < g; i++) out.push(secs.slice(Math.floor(i * n / g), Math.floor((i + 1) * n / g)).map((s) => s.n));
  return out.filter((x) => x.length);
}

/* ── фігури ────────────────────────────────────────────────────────────────── */

const figId = (u, f) => `${u.book}/${u.slug}:${f.file.replace(/^img\//, "").replace(/\.svg$/, "")}`;

/** Усі фігури теми: каркасні плюс названі письмом — і при переписуванні вони лишаються. */
const allFigs = (k) => [...(k.figs || []), ...(k.extra || [])];

/** Додати фігури, названі письмом, до теми — з іменами, без повторів. */
function addFigs(k, named) {
  const have = new Set(allFigs(k).map((f) => f.file));
  const fresh = LOC.figNames([...allFigs(k), ...named]).slice(allFigs(k).length).filter((f) => !have.has(f.file));
  k.extra = [...(k.extra || []), ...fresh];
  return fresh;
}

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

/** Що письмо має інтегрувати: вставки з адресами, фігури без місця, директиви на код. */
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

/** Сам код проєкту — текстом, усіма мовами: письмо на ньому базується. */
const codeText = (u, code) => [...new Set((code || []).map((c) => String(c.lang || "").toLowerCase()))]
  .map((lang) => LOC.codeText(u, lang)).filter(Boolean).join("\n\n");

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
      mentions: prep.mentions, passed, about: u.about || (basic ? detailed : ""),
    }), "ціль"));
    ctx.set("goal", { text: need(res, ["ЦІЛЬ"], "ціль")["ЦІЛЬ"] });
  }
  const goal = ctx.get("goal");

  /* ── 2 · СТРУКТУРА · агент — лише детальна ─────────────────────────────── */
  if (article && !ctx.get("structure")) {
    const res = await ctx.call("структура", () => ask(P.structure(u, { goal: goal.text, books: LOC.books() }), "структура"));
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

  /* ── 3 · КАРКАС · агент: рівень, розділи, глибина, групи, передумови, фігури ── */
  if (!ctx.get("karkas")) {
    const res = await ctx.call("каркас", () => ask(P.karkas(u, {
      goal: goal.text, passed, detailed, known: LOC.linkable(u),
      inserts: st.inserts.map((x) => `${x.insert}-${x.name}: ${x.about}`).join("\n"),
    }), "каркас"));
    const b = R.blocks(res);
    const secs = R.sections(b["РОЗДІЛИ"] || b["КРОКИ"] || b["ПОДІЇ"] || "");
    if (!secs.length) throw new Error("каркас: не повернув жодного розділу");
    const lv = num(b["РІВЕНЬ"]);
    const level = lv >= 1 && lv <= 3 ? lv : null;
    const rawFigs = R.figures(b["ФІГУРИ"] || "");
    const groups = R.groups(b["ГРУПИ"] || "").filter((g) => g.every((n) => secs.some((s) => s.n === n)));
    const k = {
      level, sections: secs, depth: b["ГЛИБИНА"] || "",
      /* Групи мають бути; не дав каркас — ділимо самі, кількістю за рівнем. */
      groups: groups.length ? groups : groupsFor(level, secs),
      /* Передумови — усім типам, і базовій (автор, 07.09). */
      preknow: R.preknow(b["ПЕРЕДУМОВИ"] || ""),
      /* Базова бере фігури з детальної — готові файли; малювати їй нічого. */
      figs: basic ? rawFigs.map((f) => ({ ...f, file: f.what.replace(/^.*?(img\/)/, "img/"), fromDetailed: true }))
        : LOC.figNames(rawFigs),
      extra: [],
      code: u.type === "proj" ? R.code(b["КОД"] || "") : [],
    };
    ctx.set("karkas", k);
    /* Фігури й код — у чергу тут; фігури нічого не затримують, код чекає лише проєкт. */
    const more = [...codeUnitsOf(u, k.code, k.level), ...figUnitsOf(u, k.figs, goal, k.level)];
    if (more.length) ctx.enqueue(more);
  }
  const k = ctx.get("karkas");
  const codeUnits = codeUnitsOf(u, k.code, k.level);
  const preknowText = (k.preknow || []).map((x) => `${x.title} — ${x.addr}${x.why ? " — " + x.why : ""}`).join("\n");

  /* ⏸ Проєкт пояснює код, якого ще нема, — тож спить, доки код не напишуть. */
  if (u.type === "proj" && !ctx.get("sections")) {
    const waitFor = codeUnits.map((c) => c.id).filter((id) => !ctx.isDone(id));
    if (waitFor.length)
      throw Object.assign(new Error(`чекає на код: ${waitFor.join(", ")}`), { pause: true, waitFor });
  }

  /* Спільне для кожного письма: ціль, рівень, глибина, передумови, адреси (з майбутніми
     темами етапу 2 — лінк ставиться вже, етап 8 його виправить), сам код проєкту. */
  const common = () => ({
    goal: goal.text, level: k.level, depth: k.depth, preknow: preknowText, passed,
    linkable: [LOC.linkable(u), ...(st.newTopics || []).map((t) => `${t.title} — root:new/${t.slug}`)].filter(Boolean).join("\n"),
    code: u.type === "proj" ? codeText(u, k.code) : "",
  });
  const usedFigs = (parts) => new Set(allFigs(k).filter((f) => assemble(parts).includes(f.file)).map((f) => f.file));
  const nameNew = (parts) => {
    const fresh = addFigs(k, parts.flatMap((p) => p.newFigs || []));
    if (fresh.length) { ctx.set("karkas", k); ctx.enqueue(figUnitsOf(u, fresh, goal, k.level)); }
  };
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
          theses: written.length ? thesesText(written) : NOTHING_YET,
          integrate: integrateList(u, st.inserts, allFigs(k), used, k.code),
        }), `письмо ${g.join(",")}`));
        const d = need(res, ["ТЕКСТ"], `письмо ${g.join(",")}`);
        const b = R.blocks(res);
        for (const f of allFigs(k)) if (d["ТЕКСТ"].includes(f.file)) used.add(f.file);
        const part = { group: g, text: d["ТЕКСТ"], theses: [], add: [], squeeze: [], newTopics: [], newFigs: [] };
        refresh(part, null, b);
        written.push(part);
      }
      ctx.set("sections", written);
      nameNew(written);
    }
    parts = ctx.get("sections");

    /* ── 5 · РОЗМІР І ОФЛАЙН-СИТА · локально → дописування / стиснення ─── */
    if (!ctx.get("size")) {
      let s = LOC.size(assemble(parts), u.type, k.level);
      let rounds = 0, forced = false, sieve = 0;
      const pending = () => {
        const items = offline(parts);
        for (const it of items) {
          const have = (it.part.add || []).some((a) => a.what === it.what);
          if (!have) it.part.add = [...(it.part.add || []), { section: it.section, level: 5, what: it.what }];
        }
        return items.length;
      };
      while ((s.words < s.need || (sieve = pending()) > 0) && rounds < MAX_EXTEND) {
        const deficit = Math.max(0, s.need - s.words);
        let todo = plan(deficit, parts, k);
        /* Бракує понад третину або нема названого — аналіз мусить показати місця. */
        if ((!todo.length && deficit > 0) || (!forced && s.need && deficit / s.need > FORCE_SHORT)) {
          forced = true;
          const res = await ctx.call(`де дописати ${rounds + 1}`, () => ask(P.analysis(u, {
            goal: goal.text, level: k.level, text: assemble(parts), theses: thesesText(parts),
            groups: k.groups.map((g) => g.join(", ")).join("\n"), force: true,
          }), `де дописати ${rounds + 1}`));
          for (const w of R.bySection(R.blocks(res)["ДЕ ДОПИСАТИ"] || "")) {
            const p = parts.find((x) => x.group.includes(w.section)) || parts[0];
            p.add = [...(p.add || []), { section: w.section == null ? p.group[0] : w.section, level: 5, what: w.text }];
          }
          todo = plan(deficit, parts, k);
        }
        if (!todo.length) break;
        for (const t of todo) {
          const ref = sectionOf(t.part, t.section);
          const before = sectionText(ref);
          const res = await ctx.call(`дописування ${t.section}`, () => ask(P.extend(u, {
            ...common(), section: planOf(k, t.section), text: before,
            theses: thesesText(parts, t.section), add: t.items.map((x) => `${t.section} | ${t.level} | ${x}`).join("\n"),
            floor: t.floor, ceiling: t.ceiling,
            integrate: integrateList(u, st.inserts, allFigs(k), usedFigs(parts), k.code),
          }), `дописування ${t.section}`));
          const d = need(res, ["ТЕКСТ"], "дописування");
          if (!keeps(before, d["ТЕКСТ"])) continue;   // з'їло написане — лишаємо як було
          putSection(t.part, ref, d["ТЕКСТ"]);
          refresh(t.part, t.section, R.blocks(res));
        }
        nameNew(parts);
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
            goal: goal.text, level: k.level, section: planOf(k, q.section), text: sectionText(ref),
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
      ctx.set("size", { ...s, rounds, squeezed, forced, sieve: offline(parts).length, stillShort: s.words < s.need, stillOver: s.over, cantCut, splitOff });
    }

    /* ── 5 · АНАЛІЗ · агент: оцінки; шість і нижче — з нуля, до трьох разів ── */
    const an = ctx.get("analysis") || { rewrites: 0, history: [], done: false };
    if (an.done) break;
    const res = await ctx.call(`аналіз ${an.rewrites + 1}`, () => ask(P.analysis(u, {
      goal: goal.text, level: k.level, text: assemble(parts), theses: thesesText(parts),
      groups: k.groups.map((g) => g.join(", ")).join("\n"), force: false,
    }), `аналіз ${an.rewrites + 1}`));
    const b = need(res, ["ОЦІНКА"], "аналіз");
    const all = R.blocks(res);
    const score = num(b["ОЦІНКА"]);
    if (!Number.isFinite(score)) throw new Error("аналіз: оцінка не число");
    const groups = R.scores(all["ОЦІНКИ"] || "");
    const facts = [...R.lines(all["ІСТОРІЯ"] || ""), ...R.lines(all["ФОРМУЛИ"] || "")].filter((x) => !R.empty(x));
    const history = [...an.history, score];
    if (score >= PASS_SCORE || an.rewrites >= MAX_REWRITE) {
      ctx.set("analysis", { done: true, score, groups, facts, rewrites: an.rewrites, history, forced: score < PASS_SCORE });
      break;
    }
    /* Забудь усе, що писав: етап 4 із самого початку. Фігури лишаються — вони до теми. */
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
    const figs = allFigs(k);
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

  /* ── 6 · ЛІНКИ НА НОВІ ТЕМИ · названі, а лінка в тексті нема — як фігури без місця ── */
  if (!ctx.get("links")) {
    const placed = [], unplaced = [];
    for (const t of namedTopics(st, parts, ctx)) {
      const addr = `root:new/${t.slug}`;
      if (assemble(parts).includes(addr)) continue;
      const topic = [t.title, t.about].filter(Boolean).join(" — ");
      const r1 = await ctx.call(`лінк куди ${t.slug}`, () => ask(P.linkWhere(u, { text: assemble(parts), topic }), `лінк куди ${t.slug}`));
      const sec = numOr(R.blocks(r1)["РОЗДІЛ"], null);
      const part = parts.find((p) => sec != null && p.group.includes(sec)) || parts[0];
      const r2 = await ctx.call(`лінк постав ${t.slug}`, () => ask(P.linkPlace(u, { text: part.text, section: sec == null ? part.group[0] : sec, addr, topic }), `лінк постав ${t.slug}`));
      const txt = String(R.blocks(r2)["ТЕКСТ"] || "").trim();
      if (txt.includes(addr) && keeps(part.text, txt)) { part.text = txt; placed.push(t.slug); }
      else unplaced.push(t.slug);
    }
    ctx.set("sections", parts);
    ctx.set("links", { placed, unplaced });
  }

  /* ── 8 · НОВІ ТЕМИ · зведення: куди (за правилами розміщення), чи є, чи розвести ── */
  if (!ctx.get("topics")) {
    const named = namedTopics(st, parts, ctx);
    const ops = [], links = {}, notes = [];
    const shelfText = named.length ? LOC.shelf() : "";
    for (const t of named) {
      const desc = [t.title, t.about, t.where ? `інтуїтивно: ${t.where}` : ""].filter(Boolean).join("\n");
      const r1 = await ctx.call(`тема куди ${t.slug}`, () => ask(P.topicsCategory({ shelf: shelfText, topic: desc }), `тема куди ${t.slug}`));
      const b1 = R.blocks(r1);
      let book = String(b1["КНИГА"] || "").trim().toLowerCase();
      let group = String(b1["ГРУПА"] || "").trim().toLowerCase();
      let chapter = String(b1["РОЗДІЛ"] || "").trim().toLowerCase();
      const newGroup = R.place(b1["НОВА ГРУПА"]), newChapter = R.place(b1["НОВИЙ РОЗДІЛ"]);
      let bk = MF.books().get(book) ? MF.loadBook(MF.bookDirOf(book)) : null;
      if (!bk) {
        /* Книгу заводить лише автор — тема лягає поруч із нашою, і це видно у звіті. */
        notes.push(`${t.slug}: книга «${book}» не з переліку — покладено поруч із темою${b1["ЧОМУ"] ? ` (чому: ${b1["ЧОМУ"]})` : ""}`);
        book = u.book; group = u.group; chapter = u.chapter;
        bk = MF.loadBook(MF.bookDirOf(book));
      }
      /* Групу й розділ — можна завести самому, з назвою і тим, що сюди лягає. */
      if (!bk.groups.has(group)) {
        if (newGroup && newGroup.slug === group) {
          ops.push({ op: "group", book, slug: group, title: newGroup.title, scope: newGroup.scope });
          const ch = newChapter && newChapter.slug === chapter ? newChapter : { slug: group, title: newGroup.title };
          ops.push({ op: "chapter", book, group, slug: ch.slug, title: ch.title });
          chapter = ch.slug;
          notes.push(`${t.slug}: нова група «${group}» — ${newGroup.title}`);
        } else {
          notes.push(`${t.slug}: група «${group}» не з переліку й не заведена — покладено поруч із темою`);
          group = u.group; chapter = u.chapter;
        }
      } else {
        const chapters = ((bk.groups.get(group) || { data: {} }).data.chapters || []).map((c) => c.slug);
        if (!chapters.includes(chapter)) {
          if (newChapter && newChapter.slug === chapter) {
            ops.push({ op: "chapter", book, group, slug: chapter, title: newChapter.title });
            notes.push(`${t.slug}: новий розділ «${chapter}» — ${newChapter.title}`);
          } else {
            const fallback = group === u.group ? u.chapter : chapters[0];
            if (fallback) { notes.push(`${t.slug}: розділ «${chapter}» не з переліку — покладено в «${fallback}»`); chapter = fallback; }
          }
        }
      }
      const existing = LOC.chapterTopics(book, group, ops.some((x) => x.op === "chapter" && x.slug === chapter) ? null : chapter);
      const hints = DUP.hints(t.slug, book);
      const r2 = await ctx.call(`тема чи є ${t.slug}`, () => ask(P.topicsDedupe({
        existing: existing.map((x) => `${x.slug} — ${x.title}`).join("\n") || "(розділ порожній)",
        hints: hints.join("\n"), topic: desc,
      }), `тема чи є ${t.slug}`));
      const v = R.verdict(R.blocks(r2)["ВЕРДИКТ"]);
      const fresh = () => {
        ops.push({ op: "topic", book, slug: t.slug, title: t.title, group, chapter, basic: "empty", detailed: "pending" });
        links[t.slug] = `root:${book}/${t.slug}`;
      };
      const known = v.kind === "є" && (existing.some((x) => x.slug === v.slug) || LOC.chapterTopics(book, group).some((x) => x.slug === v.slug));
      if (known) {
        const r3 = await ctx.call(`тема розвести ${t.slug}`, () => ask(P.topicsRename({
          existing: `${v.slug}: ${LOC.topicHead(book, v.slug)}`,
          ours: LOC.linkContext(assemble(parts), t.slug) || desc,
          reason: `«${t.title}» і «${v.slug}» названо як одне поняття`,
        }), `тема розвести ${t.slug}`));
        const b3 = R.blocks(r3);
        if (R.verdict(b3["ВЕРДИКТ"]).kind === "різні") {
          for (const n of R.names(b3["НАЗВИ"] || "")) {
            if (n.slug === t.slug) t.title = n.title;
            /* Чинну назву написаної теми не міняють; незаписану — можна. */
            if (n.slug === v.slug) {
              if (LOC.isDuplicate(book, v.slug).written) notes.push(`${v.slug}: назву написаної теми не чіпаємо; запропоновано «${n.title}»`);
              else ops.push({ op: "retitle", book, slug: v.slug, title: n.title });
            }
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
    const file = LOC.writeArticle(u, assemble(parts), k.preknow);
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

/* ── кінець батчу ──────────────────────────────────────────────────────────── */

const escRe = (s) => String(s).replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/**
 * Перед заведенням нових тем — чи не є котрась із них уже написаною вставкою цього батчу.
 * Етап 8 цього бачити не може: на момент письма статті вставка ще може бути не написана
 * (автор, 07.09). Дубль — тему не заводимо, а лінк у написаному переводимо на вставку;
 * група чи розділ, заведені лише під цю тему, без неї не заводяться.
 *
 * `done` — завершені одиниці оркестратора: {unit, state}; стан має get/set по етапах.
 */
async function finishBatch(done, o = {}) {
  const ask = o.ask;
  if (typeof ask !== "function") throw new Error("немає ask() — нічим питати агента");
  const notes = [], merged = [];
  const fileOf = (d) => { const a = d.state && d.state.get("assembly"); return a && a.file ? a.file : ""; };
  const inserts = done
    .filter((d) => d.unit && d.unit.insert && fileOf(d))
    .map((d) => ({ unit: d.unit, file: fileOf(d), addr: `root:${d.unit.book}/${d.unit.slug}/${d.unit.file}`, head: LOC.fileHead(fileOf(d)) }));
  if (!inserts.length) return { checked: 0, merged, notes };
  const list = inserts.map((i) => `${i.addr} — вставка теми «${i.unit.title}»: ${i.head}`).join("\n");
  let checked = 0;
  for (const { unit, state } of done) {
    if (!state) continue;
    const ops = state.get("ops") || [];
    const topics = ops.filter((op) => op && op.op === "topic");
    if (!topics.length) continue;
    let keep = ops;
    for (const op of topics) {
      const addr = `root:${op.book || unit.book}/${op.slug}`;
      let text = "";
      try { text = fs.readFileSync(path.join(MF.ROOT, fileOf({ state })), "utf8"); } catch { }
      const where = LOC.aroundLink(text, addr);
      checked++;
      const res = await ask(P.topicsInsert({
        inserts: list,
        topic: [op.title, where ? `де стаття на неї посилається: ${where}` : ""].filter(Boolean).join("\n"),
      }), `тема чи вставка ${op.slug}`);
      const hit = String(R.blocks(res)["ВСТАВКА"] || "").trim();
      const ins = R.empty(hit) ? null : inserts.find((i) => hit.includes(i.addr) || hit.includes(i.unit.file));
      if (!ins) continue;
      keep = keep.filter((x) => x !== op);
      merged.push({ unit: unit.id, topic: op.slug, insert: ins.addr });
      notes.push(`${unit.id}: нова тема «${op.slug}» — те саме, що вставка ${ins.addr}; тему не заводимо, лінк переведено`);
      /* Лінк — у всіх написаних файлах батчу, де він стоїть. */
      const re = new RegExp(`\\(${escRe(addr)}(?=[)#])`, "g");
      for (const d of done) {
        const f = fileOf(d);
        if (!f) continue;
        const p = path.join(MF.ROOT, f);
        let s = ""; try { s = fs.readFileSync(p, "utf8"); } catch { continue; }
        if (!re.test(s)) continue;
        re.lastIndex = 0;
        fs.writeFileSync(p, s.replace(re, `(${ins.addr}`), "utf8");
      }
    }
    if (keep !== ops) {
      const used = (field, slug) => keep.some((x) => x.op === "topic" && x[field] === slug);
      keep = keep.filter((x) => !((x.op === "group" && !used("group", x.slug)) || (x.op === "chapter" && !used("chapter", x.slug))));
      state.set("ops", keep);
    }
  }
  return { checked, merged, notes };
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
  algorithm, finishBatch, codeAlgorithm, codeUnitsOf, figAlgorithm, figUnitsOf, figId, plan, offline, groupsFor,
  MAX_EXTEND, MAX_COMPRESS, MAX_REWRITE, MAX_FIG_ROUNDS, PASS_SCORE, FLOOR, CEIL_X, GROUPS,
};
