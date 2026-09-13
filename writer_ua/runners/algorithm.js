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
/* Фігур — за обсягом (автор, 11.09): одна на 750 слів статті, API — одна на 500. У каркасі
   обсяг — норма типу за рівнем, у письмі — вже написане. Без міри каталог дістав 118 SVG на
   тему, а фіг-одиниці — 447 із 516 у батчі. */
const FIG_PER = { default: 750, api: 500 };
const figCap = (u, total) => Math.floor(Math.max(0, total || 0) / (u.type === "api" ? FIG_PER.api : FIG_PER.default));
/** Не більше стелі — перші в порядку каркаса. */
const capFigs = (figs, cap) => (figs || []).slice(0, Math.max(0, cap));
/* Розмір — до меншого краю (автор, 11.09): норма типу за рівнем — ціль; дописуємо лише коли
   бракує помітно, стискаємо вже від чверті понад норму, а не від стелі. На живому: перший
   прохід давав 4–6 норм, стиснення цілило в стелю по 187–503 слова за коло і зупинялось. */
const SHORT_OK = 0.85;       // менше 85 % норми — дописуємо; інакше коротше — добре
const OVER_X = 1.25;         // понад норму на чверть — стискаємо до норми
/* Стелі автора (14.09), яких агентові не кажуть — перелік іде за важливістю, решту ріжемо самі. */
const PART_MAX = 1500;            // слів на одну порцію письма — не більше
const MAX_NEW_TOPICS = 7;         // нових тем на одиницю
const MAX_INSERTS_PER_TYPE = 3;   // вставок на кожен тип
const MAX_ITEMS_PER_SECTION = 3;  // абзаців дописування на розділ за коло
/* Теми, названі одиницями цього прогону, — щоб «чи є» бачив і їх: маніфест пишеться в кінці
   батчу, і сім одиниць заводили сім назв одного поняття. Ключ — id прогону. */
const NAMED_IN_RUN = new Map();
/** Реєстр прогону; при першому зверненні — засіяти зі станів на диску, бо підняття батчу
    починає з порожньої пам'яті, а маніфест ще не записаний. */
function namedInRun(ctx) {
  const runId = (ctx.run && ctx.run.id) || "";
  if (NAMED_IN_RUN.has(runId)) return NAMED_IN_RUN.get(runId);
  const reg = new Map();
  const dir = ctx.run && ctx.run.dir;
  if (dir && fs.existsSync(dir)) for (const f of fs.readdirSync(dir)) {
    if (!f.endsWith(".json")) continue;
    let s; try { s = JSON.parse(fs.readFileSync(path.join(dir, f), "utf8")); } catch { continue; }
    for (const op of ((s && s.topics) || {}).ops || []) if (op && op.op === "topic" && op.slug && !reg.has(op.slug)) reg.set(op.slug, { title: op.title, book: op.book });
  }
  NAMED_IN_RUN.set(runId, reg);
  return reg;
}
/* Етап 2 відповідає на п'ять питань — по одному на тип вставки (автор, 08.09); блоки з `inserts.md`. */
const INSERT_QUESTIONS = ["ЧИ Є ІСТОРІЯ", "ЧИ Є МАТЕМАТИКА", "ЧИ Є ПРОЄКТ", "ЧИ Є КОМПОНЕНТ", "ЧИ Є API"];

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
    if (!cur || a.level > cur.level) bySec.set(sec, { section: sec, level: a.level, items: [a], part: p });
    else if (a.level === cur.level) cur.items.push(a);
  }
  const imp = (sec) => IMP[String(((k.sections || []).find((s) => s.n === sec) || {}).importance || "").toLowerCase()] || 0;
  const secs = [...bySec.values()].sort((a, b) => (b.level - a.level) || (imp(b.section) - imp(a.section)));
  if (!secs.length) return [];
  const chosen = [];
  let sum = 0;
  for (const s of secs) { chosen.push(s); sum += FLOOR[s.level]; if (sum >= deficit) break; }
  const extra = Math.max(0, deficit - sum);
  return chosen.map((s) => {
    /* Нема дефіциту — нема й підлоги: сито за формули чи порожній розділ не привід дописати
       300 слів у статтю, що вже в 2–5 разів довша за норму. */
    const f = deficit > 0 ? FLOOR[s.level] : 0;
    return { ...s, floor: Math.min(f * CEIL_X, Math.round(f + extra * (sum ? f / sum : 0))), ceiling: f * CEIL_X };
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
  const t = cleanText(text).trim();
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

/* Вставки тез не пишуть (theses.md), тож їхні порції 2–5 не бачили попередніх — звідси одне
   й те саме двічі-тричі в hist і proj. Замість тез — заголовок і перше речення кожного вже
   написаного розділу, механічно. */
function digestText(parts) {
  return parts.flatMap((p) => LOC.splitSections(p.text)).map((s) => {
    const first = String(s.body || "").split(/\n+/).map((x) => x.trim()).find((x) => x && !/^[!:`|>#*_-]/.test(x)) || "";
    const sent = (first.match(/^[^.!?]*[.!?]/) || [first])[0];
    return `${String(s.head || "").replace(/^##\s*/, "")} — ${sent}`.trim();
  }).filter((x) => x !== "—").join("\n");
}

/* Рядок плану («6 | важливість: висока | …») у ТЕКСТ повертають і письмо, і стиснення; у файлі
   він ставав абзацом, а заголовок під ним — другим таким самим H2. Розбір його не бере. */
const cleanText = (t) => String(t || "").replace(/^\d+\s*\|\s*(?:важливість\s*:\s*)?(?:висока|середня|низька)\s*\|[^\n]*\n?/gim, "");

/** Норми обсягу типу за рівнем і міра фігур — каркасові, щоб рівень обирали з числом перед очима. */
function normsText(u) {
  const b = LOC.BANDS[u.type === "article" ? "detail" : u.type] || LOC.BANDS.detail;
  const per = u.type === "api" ? FIG_PER.api : FIG_PER.default;
  if (u.type === "basic") return `до ${b[0]} слів`;
  return `рівень 1 — до ${b[0]} слів, 2 — до ${b[1]}, 3 — до ${b[2]}; фігур — одна на ${per} слів: ` +
    `${Math.floor(b[0] / per)}, ${Math.floor(b[1] / per)} і ${Math.floor(b[2] / per)} відповідно`;
}

/** Фігура базової з каркаса: ім'я з другої колонки чи перше слово опису, завжди під `img/`. */
function basicFigFile(f) {
  const raw = String(f.name || String(f.what || "").trim().split(/\s+/)[0] || "").replace(/[`"'«»]/g, "").replace(/^.*?img\//, "").replace(/\.svg$/i, "");
  return `img/${raw}.svg`;
}

/** Усі теми, які ця одиниця назвала новими: етап 2, письмо, винесене стисненням. Без повторів. */
function namedTopics(st, parts, ctx) {
  const seen = new Set();
  return [...(st.newTopics || []), ...parts.flatMap((p) => p.newTopics || []), ...((ctx.get("size") || {}).splitOff || [])]
    .filter((t) => t && t.slug && !seen.has(t.slug) && seen.add(t.slug));
}

/** Прийняти нову версію розділу лише коли вона не з'їла написане. */
const keeps = (before, after) => words(after) >= words(before) * KEEP_SHARE;

/* ── абзаци ─────────────────────────────────────────────────────────────────
   Дописування й розставлення працюють абзацом (автор, 14.09): межа — порожній рядок, але не
   всередині огорожі коду; абзац називають його першими словами. */
function paragraphsOf(body) {
  const out = []; let cur = [], fence = false;
  for (const l of String(body || "").split("\n")) {
    if (/^```/.test(l)) fence = !fence;
    if (!fence && !l.trim()) { if (cur.length) { out.push(cur.join("\n")); cur = []; } continue; }
    cur.push(l);
  }
  if (cur.length) out.push(cur.join("\n"));
  return out;
}
const normWords = (s) => String(s || "").toLowerCase().replace(/[«»"“”'`*_#\[\]()]/g, " ").replace(/\s+/g, " ").trim();
/** Абзац за його першими словами; нема збігу — -1. */
function findParagraph(paras, anchor) {
  const a = normWords(anchor);
  if (!a) return -1;
  const i = paras.findIndex((p) => normWords(p).startsWith(a));
  if (i >= 0) return i;
  const head = a.split(" ").slice(0, 4).join(" ");
  return head.length >= 8 ? paras.findIndex((p) => normWords(p).includes(head)) : -1;
}
const firstWords = (p, n = 6) => String(p || "").replace(/^[#>*\-\s`]+/, "").split(/\s+/).slice(0, n).join(" ");
/** Абзац, у який не можна ні дописати речення, ні вставити після нього прозу як продовження. */
const notProse = (p) => /^(```|!\[|:::|\||<)/.test(String(p || "").trim());

/** Оновити оцінки розділу після дописування чи стиснення — старі рядки про нього геть. */
/**
 * Розділ, названий заголовком, → номер: за H2 порції в порядку її групи. Писар ставить у
 * `{розділ}` заголовок, не номер (923 із 2 312 рядків «ЩО ДОДАТИ»); без цього рівень 5 ставав
 * 1, а «НОВІ SVG» відкидались цілком.
 */
function titleResolver(part) {
  const heads = LOC.splitSections(part.text).map((s, i) => [String(s.head || "").replace(/^##\s*/, "").trim().toLowerCase(), part.group[i]]);
  return (title) => {
    const c = String(title || "").trim().toLowerCase().replace(/[«»"“”]/g, "");
    if (!c) return null;
    const h = heads.find(([x]) => x && (x === c || x.startsWith(c) || c.startsWith(x) || (c.length > 12 && x.includes(c))));
    return h && h[1] != null ? h[1] : null;
  };
}

function refresh(part, sec, b) {
  const own = (x) => (x.section == null ? part.group[0] : x.section) === sec;
  const bySec = titleResolver(part);
  const fix = (x) => (x.section == null && x.title ? { ...x, section: bySec(x.title) } : x);
  part.add = [...(part.add || []).filter((a) => !own(a)), ...R.additions(b["ЩО ДОДАТИ"] || "").map(fix)];
  part.squeeze = [...(part.squeeze || []).filter((q) => !own(q)), ...R.bySection(b["ЩО ЗЖАТИ"] || "").map(fix)];
  const th = R.bySection(b["ТЕЗИ"] || "").map(fix);
  if (th.length) part.theses = [...(part.theses || []).filter((t) => !own(t)), ...th];
  part.newTopics = [...(part.newTopics || []), ...R.topics(b["НОВІ ТЕМИ"] || "")];
  part.newFigs = [...(part.newFigs || []), ...R.figures(b["НОВІ SVG"] || "").map(fix)];
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
      /* Абзацом цього не полагодити — лише нотатка; дописування його не бере (kind: skip). */
      items.push({ part: p, section: p.group[0], kind: "skip", what: `у тексті розділів ${secs.length}, а в плані ${p.group.length}: кожен розділ плану — окремий H2 із власним текстом` });
      continue;
    }
    secs.forEach((s, i) => {
      const sec = p.group[i];
      if (words(s.body) < 40) items.push({ part: p, section: sec, kind: "new", anchor: "", what: "розділ майже порожній — розкрий те, що для нього заплановано" });
      const t = [s.head, s.body].join("\n");
      const ban = FRM.banned(t).length, del = FRM.delimiters(t).length;
      /* Формулу лагодять у її абзаці: поглибити = повернути той самий абзац, переписаний. */
      const bad = paragraphsOf(s.body).find((x) => FRM.banned(x).length || FRM.delimiters(x).length);
      const anchor = bad ? firstWords(bad) : "";
      if (ban) items.push({ part: p, section: sec, kind: "deepen", anchor, what: `формули записано LaTeX (${ban}): перепиши їх у цьому абзаці за правилом формул — інлайн-код або код-блок; нового тексту не додавай` });
      if (del) items.push({ part: p, section: sec, kind: "deepen", anchor, what: `непарні роздільники формул (${del}): перепиши формули в цьому абзаці за правилом формул; нового тексту не додавай` });
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
  /* Стеля та сама, що в каркасі, перерахована за написаним: понад неї письмо фігур не додає. */
  const room = Math.max(0, (k.figCap == null ? Infinity : k.figCap) - allFigs(k).length);
  const pick = capFigs(named, room);
  const fresh = LOC.figNames([...allFigs(k), ...pick]).slice(allFigs(k).length).filter((f) => !have.has(f.file));
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
    rows.push(`фігура — ${f.what}\n  рядок: ![{що показано і що з неї видно}](${f.file}) — шлях рівно цей, у дужках твої слова`);
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
    /* Вставки — з п'яти відповідей, по одній на тип (і зі старого списку, якщо трапиться);
       рядок «нема: чому» розбір відкидає сам. Одне ім'я двічі — одна вставка. */
    const seenIns = new Set(), perType = {};
    const inserts = R.inserts([...INSERT_QUESTIONS, "ВСТАВКИ"].map((t) => b[t] || "").join("\n"))
      .filter((x) => { const k = `${x.insert}-${x.name}`; return !seenIns.has(k) && seenIns.add(k); })
      /* Каталог і є компонентом — `comp` йому не заводять (structure.md: «у каталозі — без
         comp»). Питання агентові ставиться всім видам, тож відповідь відкидаємо тут: на
         живому каталог дістав 11 comp-вставок за один батч. */
      .filter((x) => !(u.kind === "cat" && x.insert === "comp"))
      /* Стеля — три на тип (автор, 14.09): перелік іде за важливістю, решту відсіюємо самі. */
      .filter((x) => (perType[x.insert] = (perType[x.insert] || 0) + 1) <= MAX_INSERTS_PER_TYPE);
    const st = { inserts, newTopics: R.topics(b["НОВІ ТЕМИ"] || ""), basic: R.yes(b["БАЗОВА"]) };
    ctx.set("structure", st);
    /* Вставки — у чергу одразу, паралельно: стаття на них не чекає. Назву вставки дав етап 2 —
       вона стає її заголовком (автор, 14.09); без назви — назва теми, як досі. */
    if (st.inserts.length)
      ctx.enqueue(st.inserts.map((x) => ({
        ...LOC.unitOf(u.book, u.slug, x.insert, "", `${x.insert}-${x.name}`), ...(x.title ? { title: x.title } : {}), about: x.about, parent: u.id,
      })));
  }
  const st = ctx.get("structure") || { inserts: [], newTopics: [], basic: false };

  /* ── 3 · КАРКАС · агент: рівень, розділи, глибина, групи, передумови, фігури ── */
  if (!ctx.get("karkas")) {
    const res = await ctx.call("каркас", () => ask(P.karkas(u, {
      goal: goal.text, passed, detailed, known: LOC.linkable(u), norms: normsText(u),
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
      /* Каркас базової називає їх і голим ім'ям (`2 | name.svg`); шлях завжди `img/<ім'я>` —
         без цього три базові з чотирьох мали биті фігури (16 за батч). */
      figs: basic ? rawFigs.map((f) => ({ ...f, file: basicFigFile(f), fromDetailed: true }))
        : LOC.figNames(capFigs(rawFigs, Math.max(1, figCap(u, LOC.size("", u.type, level).need)))),
      /* Хоч одна — завжди: норма 600 слів ділила на 750 у нуль і відкидала весь план каркаса. */
      figCap: Math.max(1, figCap(u, LOC.size("", u.type, level).need)),
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
    /* Міра фігур — за написаним, але не за роздутим: до стиснення текст буває в 2–5 разів
       довший за норму, і письмо додавало б фігур під обсяг, який далі зріжуть. */
    k.figCap = Math.max(k.figCap || 0, figCap(u, Math.min(words(assemble(parts)), LOC.size("", u.type, k.level).need * OVER_X)));
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
      /* ⛔ ПИСАР ЗНАЄ МІРУ. Доти обсяг знали лише етап розміру й дописувач, а письмо — ні:
         перший прохід давав 11 000 слів на норму 4 000, і п'ять кіл стиснення нічого не
         зрізали («не ріжеться»). Норма типу за рівнем (BANDS) ділиться між порціями за
         кількістю розділів — орієнтир, не лічильник. */
      const band = LOC.size("", u.type, k.level);
      for (const g of k.groups) {
        const mine = k.sections.filter((s) => g.includes(s.n));
        const res = await ctx.call(`письмо ${g.join(",")}`, () => ask(P.write(u, {
          ...common(),
          sections: mine.map((s) => `${s.n} | важливість: ${s.importance} | ${s.text}`).join("\n"),
          words: { part: Math.min(PART_MAX, Math.round(band.need * mine.length / Math.max(1, k.sections.length))), all: band.need, ceiling: band.ceiling },
          theses: written.length ? (thesesText(written) || digestText(written)) : NOTHING_YET,
          integrate: integrateList(u, st.inserts, allFigs(k), used, k.code),
        }), `письмо ${g.join(",")}`));
        const d = need(res, ["ТЕКСТ"], `письмо ${g.join(",")}`);
        const b = R.blocks(res);
        for (const f of allFigs(k)) if (d["ТЕКСТ"].includes(f.file)) used.add(f.file);
        const part = { group: g, text: cleanText(d["ТЕКСТ"]), theses: [], add: [], squeeze: [], newTopics: [], newFigs: [] };
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
        const items = offline(parts).filter((it) => it.kind !== "skip");
        for (const it of items) {
          const have = (it.part.add || []).some((a) => a.what === it.what);
          if (!have) it.part.add = [...(it.part.add || []), { section: it.section, level: 5, kind: it.kind, anchor: it.anchor, what: it.what }];
        }
        return items.length;
      };
      while ((s.words < s.need * SHORT_OK || (sieve = pending()) > 0) && rounds < MAX_EXTEND) {
        const deficit = s.words < s.need * SHORT_OK ? Math.max(0, s.need - s.words) : 0;
        let todo = plan(deficit, parts, k);
        /* Бракує понад третину або нема названого — аналіз мусить показати місця. */
        if ((!todo.length && deficit > 0) || (!forced && s.need && deficit / s.need > FORCE_SHORT)) {
          forced = true;
          const res = await ctx.call(`де дописати ${rounds + 1}`, () => ask(P.analysis(u, {
            goal: goal.text, level: k.level, text: assemble(parts), theses: thesesText(parts),
            groups: k.groups.map((g) => g.join(", ")).join("\n"), force: true,
          }), `де дописати ${rounds + 1}`));
          for (const w of R.bySection(R.blocks(res)["ДЕ ДОПИСАТИ"] || "")) {
            if (w.section == null && w.title) for (const x of parts) { const n = titleResolver(x)(w.title); if (n != null) { w.section = n; break; } }
            const p = parts.find((x) => x.group.includes(w.section)) || parts[0];
            p.add = [...(p.add || []), { section: w.section == null ? p.group[0] : w.section, level: 5, kind: w.kind, anchor: w.anchor, what: w.text }];
          }
          todo = plan(deficit, parts, k);
        }
        if (!todo.length) break;
        /* ⛔ ДОПИСУЄМО АБЗАЦАМИ, НЕ РОЗДІЛАМИ (автор, 14.09): поглибити названий абзац — даємо
           старий, дістаємо новий і замінюємо; новий абзац — дістаємо його й ставимо після
           названого. Розділ не переписується і не віддається наново. */
        for (const t of todo) {
          const ref = sectionOf(t.part, t.section);
          for (const it of t.items.slice(0, MAX_ITEMS_PER_SECTION)) {
            if (it.kind === "skip") continue;
            const paras = paragraphsOf(ref.secs[ref.i].body);
            if (!paras.length) paras.push("");
            let idx = findParagraph(paras, it.anchor);
            const kind = it.kind === "deepen" && idx >= 0 ? "deepen" : "new";
            if (idx < 0) idx = paras.length - 1;
            const paragraph = paras[idx];
            const res = await ctx.call(`дописування ${t.section}`, () => ask(P.extend(u, {
              ...common(), section: planOf(k, t.section), text: sectionText(ref), paragraph,
              how: kind === "deepen" ? "поглибити цей абзац — повернути його ж, розгорнутий тим, що названо"
                : "новий абзац після цього — повернути лише новий абзац, без сусідів",
              add: `${t.level} | ${it.what}`, theses: thesesText(parts, t.section),
              integrate: integrateList(u, st.inserts, allFigs(k), usedFigs(parts), k.code),
            }), `дописування ${t.section}`));
            const para = cleanText(need(res, ["АБЗАЦ"], "дописування")["АБЗАЦ"]).trim();
            if (!para) continue;
            if (kind === "deepen") { if (words(para) < words(paragraph) * KEEP_SHARE) continue; paras[idx] = para; }
            else paras.splice(idx + 1, 0, para);
            ref.secs[ref.i].body = paras.join("\n\n");
            t.part.text = LOC.joinSections(ref.secs);
          }
          /* Названі пункти цього розділу зняті — і зроблені, і ті, що не вдалося: інакше коло за колом те саме. */
          t.part.add = (t.part.add || []).filter((a) => !t.items.includes(a));
        }
        nameNew(parts);
        rounds++;
        s = LOC.size(assemble(parts), u.type, k.level);
      }

      let squeezed = 0;
      const cantCut = [], splitOff = [], refused = new Set();
      const over = () => s.words > s.need * OVER_X;
      while (over() && squeezed < MAX_COMPRESS) {
        let fat = parts.flatMap((p) => (p.squeeze || []).map((q) => ({ part: p, section: q.section == null ? p.group[0] : q.section, what: q.text })))
          .filter((q) => q.part.group.includes(q.section) && !refused.has(q.section));
        /* Писар нічого не назвав, а стаття довша за норму — стискаємо всі розділи за загальним
           іменем зайвого: доти порожній список означав «стискати нічого», і 11 490 слів на
           норму 1 800 приймались без жодного кола. Розділ, що вже відмовив, не чіпаємо. */
        if (!fat.length)
          fat = parts.flatMap((p) => p.group.filter((sec) => !refused.has(sec)).map((sec) => ({ part: p, section: sec, what: "повтори, переказ сусідніх розділів і вставок, переліки заради повноти" })));
        if (!fat.length) break;
        const by = Math.ceil((s.words - s.need) / fat.length);
        const roundStart = s.words;
        for (const q of fat) {
          const ref = sectionOf(q.part, q.section);
          const before = sectionText(ref);
          /* Просити зрізати більше, ніж розділ має, — відмова: «розділ 550, зрізати 517». Не
             більше ніж 40 % розділу за коло; решта — наступним колом. */
          const cut = Math.max(20, Math.min(by, Math.round(words(before) * 0.4)));
          const res = await ctx.call(`стиснення ${q.section}`, () => ask(P.compress(u, {
            goal: goal.text, level: k.level, section: planOf(k, q.section), text: before,
            theses: thesesText(parts, q.section), squeeze: q.what, by: cut,
          }), `стиснення ${q.section}`));
          const d = need(res, ["ТЕКСТ"], "стиснення");
          const b = R.blocks(res);
          /* Відповідь, що не коротша (5 виросли, 10 без змін за батч), — відмова розділу. */
          if (words(d["ТЕКСТ"]) >= words(before)) { refused.add(q.section); cantCut.push(`розділ ${q.section}: повернуто не коротше`); continue; }
          putSection(q.part, ref, d["ТЕКСТ"]);
          q.part.squeeze = (q.part.squeeze || []).filter((x) => (x.section == null ? q.part.group[0] : x.section) !== q.section);
          for (const x of R.bySection(b["ЩО ЗЖАТИ"] || "")) q.part.squeeze.push({ section: q.section, text: x.text });
          if (!R.empty(b["НЕ РІЖЕТЬСЯ"])) { cantCut.push(`розділ ${q.section}: ${b["НЕ РІЖЕТЬСЯ"]}`); refused.add(q.section); q.part.squeeze = q.part.squeeze.filter((x) => x.section !== q.section); }
          splitOff.push(...R.topics(b["ОКРЕМА ТЕМА"] || ""));
        }
        squeezed++;
        s = LOC.size(assemble(parts), u.type, k.level);
        /* Коло, що зрізало менше 5 %, наступним не стане кращим — спиняємо, не палимо кола. */
        if (s.words > roundStart * 0.95) break;
      }
      ctx.set("sections", parts);
      ctx.set("size", { ...s, rounds, squeezed, forced, sieve: offline(parts).length, stillShort: s.words < s.need * SHORT_OK, stillOver: over(), cantCut, splitOff });
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

  /* ── 6 · РОЗСТАВЛЕННЯ · фігури й лінки без місця — один запит (автор, 14.09) ─── */
  if (!ctx.get("figures") || !ctx.get("links")) {
    const figs = allFigs(k);
    const text0 = assemble(parts);
    const figsLeft = figs.filter((f) => !text0.includes(f.file));
    const named = namedTopics(st, parts, ctx).slice(0, MAX_NEW_TOPICS);
    const linksLeft = named.filter((t) => !text0.includes(`root:new/${t.slug}`));
    const placedF = [], placedL = [];
    /* Рядок відповіді → розділ, абзац; правку робить `make(paras, idx)`. */
    const put = (row, make) => {
      if (row.length < 3) return false;
      let sec = numOr(row[1], null);
      if (sec == null) for (const x of parts) { const n = titleResolver(x)(row[1]); if (n != null) { sec = n; break; } }
      const part = parts.find((p) => sec != null && p.group.includes(sec)) || parts[0];
      const ref = sectionOf(part, sec == null ? part.group[0] : sec);
      const paras = paragraphsOf(ref.secs[ref.i].body);
      if (!paras.length) paras.push("");
      let idx = findParagraph(paras, row[2]);
      if (idx < 0) idx = paras.length - 1;
      if (!make(paras, idx)) return false;
      ref.secs[ref.i].body = paras.join("\n\n");
      part.text = LOC.joinSections(ref.secs);
      return true;
    };
    if (figsLeft.length || linksLeft.length) {
      const res = await ctx.call("розставити", () => ask(P.place(u, {
        text: text0,
        figures: figsLeft.map((f) => `${f.file} — ${f.what}`).join("\n"),
        links: linksLeft.map((t) => `root:new/${t.slug} — ${t.title}${t.about ? ": " + t.about : ""}`).join("\n"),
      }), "розставити"));
      const b = R.blocks(res);
      for (const row of R.cols(b["МІСЦЯ ФІГУР"] || "")) {
        const f = figsLeft.find((x) => row[0] && (x.file === row[0] || x.file.endsWith("/" + row[0]) || row[0].endsWith(x.file)));
        if (!f || placedF.includes(f.file)) continue;
        const cap = (row[3] || f.what || "").replace(/^\*+|\*+$/g, "").trim();
        if (put(row, (paras, idx) => { paras.splice(idx + 1, 0, `![${cap}](${f.file})\n*${cap}*`); return true; })) placedF.push(f.file);
      }
      for (const row of R.cols(b["МІСЦЯ ЛІНКІВ"] || "")) {
        const t = linksLeft.find((x) => row[0] && row[0].includes(x.slug));
        if (!t || placedL.includes(t.slug)) continue;
        const addr = `root:new/${t.slug}`;
        let sentence = row.slice(3).join(" | ").trim();
        if (!sentence) continue;
        if (!sentence.includes(addr)) sentence = sentence.replace(/[.\s]*$/, "") + ` — [${t.title}](${addr}).`;
        if (put(row, (paras, idx) => { if (notProse(paras[idx])) return false; paras[idx] = paras[idx].replace(/\s*$/, "") + " " + sentence; return true; })) placedL.push(t.slug);
      }
    }
    ctx.set("sections", parts);
    ctx.set("figures", {
      all: figs.map((f) => f.file), placed: placedF, unplaced: figsLeft.map((f) => f.file).filter((x) => !placedF.includes(x)),
      pending: figs.filter((f) => !f.fromDetailed).map((f) => figId(u, f)).filter((id) => !ctx.isDone(id)),
    });
    ctx.set("links", { placed: placedL, unplaced: linksLeft.map((t) => t.slug).filter((x) => !placedL.includes(x)) });
  }

  /* ── 8 · НОВІ ТЕМИ · три запити на статтю: куди, чи є, розвести (автор, 14.09) ──── */
  if (!ctx.get("topics")) {
    const namedAll = namedTopics(st, parts, ctx);
    const named = namedAll.slice(0, MAX_NEW_TOPICS);
    const ops = [], links = {}, notes = [];
    /* Понад стелю — відсіяно разом із лінками на них, щоб не лишити битих. */
    for (const t of namedAll.slice(MAX_NEW_TOPICS)) {
      notes.push(`${t.slug}: понад стелю ${MAX_NEW_TOPICS} нових тем — відсіяно`);
      for (const p of parts) p.text = LOC.unlink(p.text, `root:new/${t.slug}`);
    }
    const reg = namedInRun(ctx);
    const desc = (t) => [t.slug, t.title, t.about, t.where ? `інтуїтивно: ${t.where}` : ""].filter(Boolean).join(" | ");
    const low = (x) => String(x || "").trim().toLowerCase();
    if (named.length) {
      /* 1 · КУДИ — усі теми одним запитом. Нова тема — атом; курс у переліку — лише свій, і
         лише для того, що тримається на його нитці (CLAUDE.md; автор, 14.09). */
      const r1 = await ctx.call("теми куди", () => ask(P.topicsCategory({
        shelf: LOC.shelf({ skipKinds: ["course"], keep: [u.book] }), topics: named.map(desc).join("\n"),
      }), "теми куди"));
      const b1 = R.blocks(r1);
      const where = new Map();
      for (const c of R.cols(b1["ТЕМИ"] || "")) if (c.length >= 4 && c[0]) where.set(low(c[0]), { book: low(c[1]), group: low(c[2]), chapter: low(c[3]), why: c[4] || "" });
      const newGroups = R.cols(b1["НОВА ГРУПА"] || "").filter((c) => c.length >= 3).map((c) => ({ book: low(c[0]), slug: low(c[1]), title: c[2], scope: c[3] || "" }));
      const newChapters = R.cols(b1["НОВИЙ РОЗДІЛ"] || "").filter((c) => c.length >= 4).map((c) => ({ book: low(c[0]), group: low(c[1]), slug: low(c[2]), title: c[3] }));
      const target = new Map();
      const opKey = (o) => [o.op, o.book, o.group || "", o.slug].join("/");
      const pushOp = (o) => { if (!ops.some((x) => opKey(x) === opKey(o))) ops.push(o); };
      for (const t of named) {
        const w = where.get(t.slug) || {};
        let book = w.book, group = w.group, chapter = w.chapter;
        let bk = MF.books().get(book) ? MF.loadBook(MF.bookDirOf(book)) : null;
        if (!bk || ((MF.books().get(book) || {}).kind === "course" && book !== u.book)) {
          /* Книгу заводить лише автор; чужий курс — не ціль. Тема лягає поруч із нашою. */
          notes.push(`${t.slug}: книга «${book || "—"}» не з переліку — покладено поруч із темою${w.why ? ` (чому: ${w.why})` : ""}`);
          book = u.book; group = u.group; chapter = u.chapter;
          bk = MF.loadBook(MF.bookDirOf(book));
        }
        /* Групу й розділ — можна завести самому, з назвою і тим, що сюди лягає. */
        if (!bk.groups.has(group)) {
          const ng = newGroups.find((g) => g.book === book && g.slug === group);
          if (ng) {
            pushOp({ op: "group", book, slug: group, title: ng.title, scope: ng.scope });
            const nc = newChapters.find((c) => c.book === book && c.group === group && c.slug === chapter);
            const ch = nc || { slug: group, title: ng.title };
            pushOp({ op: "chapter", book, group, slug: ch.slug, title: ch.title });
            chapter = ch.slug;
            notes.push(`${t.slug}: нова група «${group}» — ${ng.title}`);
          } else {
            /* «Поруч із темою» — це наша книга ЦІЛКОМ, не чужа книга з нашою групою. */
            notes.push(`${t.slug}: група «${group}» у книзі «${book}» не з переліку й не заведена — покладено поруч із темою`);
            book = u.book; group = u.group; chapter = u.chapter;
            bk = MF.loadBook(MF.bookDirOf(book));
          }
        } else {
          const chapters = ((bk.groups.get(group) || { data: {} }).data.chapters || []).map((c) => c.slug);
          if (!chapters.includes(chapter)) {
            const nc = newChapters.find((c) => c.book === book && c.group === group && c.slug === chapter);
            if (nc) { pushOp({ op: "chapter", book, group, slug: chapter, title: nc.title }); notes.push(`${t.slug}: новий розділ «${chapter}» — ${nc.title}`); }
            else {
              const fallback = book === u.book && group === u.group ? u.chapter : chapters[0];
              if (fallback) { notes.push(`${t.slug}: розділ «${chapter}» не з переліку — покладено в «${fallback}»`); chapter = fallback; }
            }
          }
        }
        target.set(t.slug, { book, group, chapter });
      }

      /* 2 · ЧИ Є — один запит на книгу, проти всієї книги (дубль живе будь-де) і проти тем,
         названих іншими одиницями цього батчу. Власна тема статті — не збіг. */
      const byBook = new Map();
      for (const t of named) { const b = target.get(t.slug).book; (byBook.get(b) || byBook.set(b, []).get(b)).push(t); }
      const verdict = new Map();
      for (const [book, ts] of byBook) {
        const inBook = LOC.bookTopics(book).filter((x) => !(book === u.book && x.slug === u.slug));
        const fromBatch = [...reg.entries()]
          .filter(([s, x]) => x.book === book && !ts.some((t) => t.slug === s) && !inBook.some((y) => y.slug === s))
          .map(([s, x]) => ({ slug: s, title: `${x.title} (названо в цьому батчі)` }));
        const existing = [...inBook, ...fromBatch];
        const hints = ts.flatMap((t) => DUP.hints(t.slug, book).map((h) => `${t.slug}: ${h}`));
        const r2 = await ctx.call(`теми чи є ${book}`, () => ask(P.topicsDedupe({
          existing: existing.map((x) => `${x.slug} — ${x.title}`).join("\n") || "(тем ще немає)",
          hints: hints.join("\n"), topics: ts.map(desc).join("\n"),
        }), `теми чи є ${book}`));
        for (const c of R.cols(R.blocks(r2)["ВЕРДИКТИ"] || "")) {
          if (c.length < 2) continue;
          const slug = low(c[2] || "").replace(/^є\s*/, "");
          verdict.set(low(c[0]), { kind: /^є/i.test(c[1]) ? "є" : "нова", slug, fromBatch: fromBatch.some((x) => x.slug === slug) });
        }
      }

      /* 3 · РОЗВЕСТИ — усі пари одним запитом. */
      const pairs = [];
      for (const t of named) {
        const v = verdict.get(t.slug) || { kind: "нова" };
        const w = target.get(t.slug);
        if (v.kind !== "є" || !v.slug) continue;
        if (v.fromBatch) { links[t.slug] = `root:${reg.get(v.slug).book}/${v.slug}`; notes.push(`${t.slug} — те саме, що ${v.slug}, названа в цьому батчі; лінк переведено`); t.resolved = true; continue; }
        if (LOC.bookTopics(w.book).some((x) => x.slug === v.slug)) { pairs.push({ t, v, w }); continue; }
        /* «є | слуг», якого в книзі нема: тема може жити в іншій книзі — тоді лінк туди; нема ніде — нова. */
        const where2 = [...MF.books()].find(([, b]) => { const x = MF.loadBook(b.bookDir); return x && MF.findTopic(x, v.slug); });
        if (where2) { links[t.slug] = `root:${where2[0]}/${v.slug}`; notes.push(`${t.slug} — те саме, що ${where2[0]}/${v.slug} в іншій книзі; лінк переведено`); t.resolved = true; }
        else notes.push(`${t.slug}: відповідач назвав збіг «${v.slug}», якого немає ніде — заведено як нову`);
      }
      if (pairs.length) {
        const r3 = await ctx.call("теми розвести", () => ask(P.topicsRename({
          pairs: pairs.map(({ t, v, w }) => `${t.slug} ↔ ${v.slug}\n  наявна: ${LOC.topicHead(w.book, v.slug)}\n  наша: ${LOC.linkContext(assemble(parts), t.slug) || desc(t)}`).join("\n\n"),
        }), "теми розвести"));
        const rv = new Map();
        for (const c of R.cols(R.blocks(r3)["ВЕРДИКТИ"] || "")) if (c.length >= 2) rv.set(low(c[0]), c);
        for (const { t, v, w } of pairs) {
          const c = rv.get(t.slug);
          if (c && /^різн/i.test(c[1])) {
            if (c[2]) t.title = c[2];
            /* Чинну назву написаної теми не міняють; незаписану — можна. */
            if (c[3]) {
              if (LOC.isDuplicate(w.book, v.slug).written) notes.push(`${v.slug}: назву написаної теми не чіпаємо; запропоновано «${c[3]}»`);
              else pushOp({ op: "retitle", book: w.book, slug: v.slug, title: c[3] });
            }
          } else { links[t.slug] = `root:${w.book}/${v.slug}`; notes.push(`${t.slug} — те саме, що ${v.slug}; лінк переведено`); t.resolved = true; }
        }
      }
      for (const t of named) {
        if (t.resolved) continue;
        const w = target.get(t.slug);
        pushOp({ op: "topic", book: w.book, slug: t.slug, title: t.title, group: w.group, chapter: w.chapter, basic: "empty", detailed: "pending" });
        links[t.slug] = `root:${w.book}/${t.slug}`;
        reg.set(t.slug, { title: t.title, book: w.book });
      }
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
    const unfenced = LOC.unfenceDirectives(abs);
    const fixed = LOC.fixFences(abs);
    const fen = { ...LOC.checkFences(abs), moved, unfenced, fixed };
    const pending = (ctx.get("figures") || {}).pending || [];
    /* Базова бере фігури детальної, які ще можуть малюватись, — за лінками її не судимо. */
    const svg = LOC.checkFigures(u.dir, { links: !pending.length && !basic });
    ctx.set("assembly", { file, formulas: frm, fences: fen, svg: { ...svg, pending } });
  }

  /* ── 10 · ЗАВЕРШЕННЯ · операції в маніфест, базова ─────────────────────── */
  if (!ctx.get("ops")) {
    const ops = [...LOC.ops(u, o.status || "done"), ...((ctx.get("topics") || {}).ops || [])];
    if (article && !u.insert) {
      const total = words(fs.readFileSync(path.join(MF.ROOT, ctx.get("assembly").file), "utf8"));
      const needBasic = total > LOC.BANDS.basic[3] * BASIC_OVER || !!st.basic;
      /* ⛔ ЛИШЕ З `empty` У `pending`, А НЕ БЕЗУМОВНО. Операції всіх одиниць лягають у
         маніфест разом наприкінці, у порядку черги; при піднятті батчу базова стоїть у
         черзі ПЕРЕД детальною (за іменем файла стану), і безумовний «pending» детальної
         затирав щойно записаний «done» базової. Заміряно: три базові hw-motion з готовими
         файлами лишились pending. */
      ops.push(needBasic
        ? { op: "status-if", slug: u.slug, ver: "basic", from: "empty", to: "pending" }
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

  /* ⛔ ЛІНКИ root:new/ — ПІСЛЯ ВСІХ ОДИНИЦЬ. Етап 8 підставляє адресу лише темам, які назвала
     та сама одиниця; тему, яку назвала сусідня (детальна — для свого api), у файлі лишало як
     root:new/… — битий лінк у готовій статті (mg90s, 09.09). Тут — усі написані файли батчу
     проти тем, заведених цим батчем, і проти маніфестів. */
  const batchAddr = {};
  for (const d of done) for (const op of (d.state && d.state.get("ops")) || [])
    if (op && op.op === "topic" && op.slug) batchAddr[String(op.slug).toLowerCase()] = `root:${op.book || d.unit.book}/${op.slug}`;
  const addrOf = (slug) => {
    if (batchAddr[slug]) return batchAddr[slug];
    for (const [bs, b] of MF.books()) { const x = MF.loadBook(b.bookDir); if (x && MF.findTopic(x, slug)) return `root:${bs}/${slug}`; }
    return "";
  };
  let swept = 0, requeued = 0;
  const dangling = [];
  for (const d of done) {
    const f = fileOf(d);
    if (!f) continue;
    const p = path.join(MF.ROOT, f);
    let s = ""; try { s = fs.readFileSync(p, "utf8"); } catch { continue; }
    const map = {};
    for (const m of s.matchAll(/root:new\/([a-z0-9][a-z0-9-]*)/gi)) {
      const slug = m[1].toLowerCase();
      if (slug in map) continue;
      const a = addrOf(slug);
      if (a) map[slug] = a; else dangling.push(`${f}: ${slug}`);
    }
    if (Object.keys(map).length) { fs.writeFileSync(p, LOC.resolveLinks(s, map), "utf8"); swept += Object.keys(map).length; }
    /* ⛔ ЛІНК НА ВЛАСНУ ВСТАВКУ, ЯКОЇ НЕМА. Стаття лінкує вставки з плану до того, як їх
       написано; впала одиниця вставки лінк не знімає — 28 битих лінків у progarch за ніч
       тиші. Тут: вставка своєї теми без файла → у маніфест `pending`, щоб черга її дописала;
       лінк лишається — адреса правильна. */
    if (d.unit && !d.unit.insert && d.state) {
      const ops = d.state.get("ops") || [];
      const re = new RegExp(`\\(root:${escRe(d.unit.book)}/${escRe(d.unit.slug)}/((?:hist|comp|math|proj|api)-[a-z0-9-]+)\\.md[)#]`, "g");
      const added = [];
      for (const m of s.matchAll(re)) {
        const file = `${m[1]}.md`;
        if (fs.existsSync(path.join(MF.ROOT, "root", d.unit.kind || "", d.unit.book, d.unit.slug, file)) || fs.existsSync(path.join(d.unit.dir || "", file))) continue;
        if (ops.some((o) => o && o.op === "insert" && o.file === file) || added.includes(file)) continue;
        added.push(file);
        ops.push({ op: "insert", slug: d.unit.slug, type: m[1].split("-")[0], file, status: "pending" });
      }
      if (added.length) { d.state.set("ops", ops); requeued += added.length; notes.push(`${d.unit.id}: вставки без файла → pending: ${added.join(", ")}`); }
    }
  }
  if (swept) notes.push(`лінків root:new/ переведено на адреси: ${swept}`);
  if (requeued) notes.push(`вставок повернуто в чергу (лінк є, файла нема): ${requeued}`);
  for (const x of [...new Set(dangling)]) notes.push(`лінк root:new/ без теми: ${x}`);

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
    let text = "";
    try { text = fs.readFileSync(path.join(MF.ROOT, fileOf({ state })), "utf8"); } catch { }
    /* Усі нові теми статті — одним запитом (автор, 14.09): 310 запитів по одній дали 0 збігів. */
    const rows = topics.map((op) => {
      const where = LOC.aroundLink(text, `root:${op.book || unit.book}/${op.slug}`);
      return `${op.slug} | ${op.title}${where ? ` | де стаття на неї посилається: ${where}` : ""}`;
    });
    checked += topics.length;
    const res = await ask(P.topicsInsert({ inserts: list, topics: rows.join("\n") }), `теми чи вставки ${unit.id}`);
    const hits = new Map();
    for (const c of R.cols(R.blocks(res)["ЗБІГИ"] || "")) if (c.length >= 2) hits.set(String(c[0]).trim().toLowerCase(), c.slice(1).join(" | "));
    for (const op of topics) {
      const hit = hits.get(String(op.slug).toLowerCase());
      const ins = hit ? inserts.find((i) => hit.includes(i.addr) || hit.includes(i.unit.file)) : null;
      if (!ins) continue;
      const addr = `root:${op.book || unit.book}/${op.slug}`;
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
      const prev = iss.join("\n");
      const res = await ctx.call(`фігура-лад ${rounds}`, () => ask(P.figureFix(u, {
        what: u.about, file: u.figFile, svg, issues: iss.join("\n"), attempt: rounds,
      }), `фігура-лад ${rounds}`));
      const d = need(res, ["SVG"], "перемальовування");
      if (!wholeSvg(d["SVG"])) break;
      svg = d["SVG"];
      file = LOC.writeFigure(u, u.figFile, svg);
      iss = LOC.checkFigure(u, u.figFile);
      /* Те саме зауваження після перемальовування далі не зникне: 17 фігур за батч горіли
         по 2–4 кола на одному «лінія перетинає текст». */
      if (iss.join("\n") === prev) break;
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
