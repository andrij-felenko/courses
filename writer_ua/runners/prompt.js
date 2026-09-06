#!/usr/bin/env node
/* ============================================================================
   prompt.js — СКЛАДАННЯ ЗАВДАННЯ З ФАЙЛІВ ПРАВИЛ. Підстановка, а не зшивання.

   Правил у цьому файлі немає — жодного речення, адресованого агентові. Є лише те,
   ЗВІДКИ зібрати: який файл `rules/` у який запит. Кожен запит — набір блоків: дані
   (ціль, текст, списки) окремими тегами, наказ — `<ЩО ЗРОБИТИ>` із секцій «Треба
   зробити» потрібних файлів, контракт — `<ПОВЕРНИ>` із секцій «Треба отримати».
   Мапа «що з чого» — `rules/README.md`; вона й є специфікація цього файла.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const RULES = path.join(__dirname, "..", "rules");
const ASK = "Треба зробити", RET = "Треба отримати";

/* ── читання файлів правил ─────────────────────────────────────────────────── */

/** Секція markdown за заголовком другого рівня, без самого заголовка. */
function section(md, title) {
  for (const part of String(md).split(/^## /m).slice(1)) {
    const nl = part.indexOf("\n");
    if (part.slice(0, nl < 0 ? part.length : nl).trim() === title)
      return part.slice(nl + 1).trim();
  }
  return "";
}

const readRule = (name) => {
  const p = path.join(RULES, `${name}.md`);
  return fs.existsSync(p) ? fs.readFileSync(p, "utf8") : "";
};
const readType = (type, kind) => {
  const p = path.join(RULES, "types", `${type}-${kind}.md`);
  if (!fs.existsSync(p)) throw new Error(`немає правил: types/${type}-${kind}.md`);
  return fs.readFileSync(p, "utf8");
};

/** Накази названих файлів по порядку; файла нема — нічого не додається. */
const ask = (names) => names.map((n) => section(readRule(n), ASK)).filter(Boolean).join("\n\n");
/** Прибрати відступ код-блоку: контракт у файлі стоїть із чотирма пробілами, агентові — ні. */
const dedent = (s) => String(s || "").split("\n").map((l) => l.replace(/^ {4}/, "")).join("\n").trim();
/** Контракти названих файлів — лише з тих, що щось повертають. */
const ret = (names) => names.map((n) => dedent(section(readRule(n), RET))).filter(Boolean).join("\n");

/** Правила самої книги — `_canon.md` в її теці; де вони уточнюють загальне, перевага в них. */
function bookCanon(u) {
  const p = u && u.bookDir ? path.join(u.bookDir, "_canon.md") : "";
  if (!p || !fs.existsSync(p)) return "";
  return "ПРАВИЛА ЦІЄЇ КНИГИ. Там, де вони уточнюють загальне, перевага в них.\n\n"
    + fs.readFileSync(p, "utf8").trim();
}

/**
 * Файли виду й форми: невпорядкованим — `atom`; своєму виду — `kind-<вид>`, а хто свого
 * не має — `kind-book`; вставці — ще `insert`. Курс — єдиний послідовний вид, `atom` не бере.
 */
const kindFiles = (u) => {
  const own = `kind-${u.kind}`;
  const mine = fs.existsSync(path.join(RULES, `${own}.md`)) ? own : "kind-book";
  return [...(u.kind === "course" ? [] : ["atom"]), mine, ...(u.insert ? ["insert"] : [])];
};

/** Один наказ: канон книги → спільні файли → файл типу. */
const order = (u, names, typeKind) => [
  bookCanon(u), ask(names), typeKind ? section(readType(u.type, typeKind), ASK) : "",
].filter(Boolean).join("\n\n");
/** Один контракт: спільні файли → файл типу. */
const answer = (u, names, typeKind) => [
  ret(names), typeKind ? dedent(section(readType(u.type, typeKind), RET)) : "",
].filter(Boolean).join("\n");

/* Що бере кожен, хто пише прозу: протокол письма, тези (лише статті), спільні файли, вид. */
const PROSE = ["prose", "language", "links", "formulas", "figures", "code-in-text", "code-lang"];
const hasTheses = (u) => u.type === "article" || u.type === "basic";
const writers = (u) => [...(hasTheses(u) ? ["theses"] : []), ...PROSE, ...kindFiles(u)];

/* ── блоки ─────────────────────────────────────────────────────────────────── */

/** Однакові теги зливаються в один блок у порядку появи; порожній блок не друкується. */
function render(blocks) {
  const merged = [];
  for (const b of blocks) {
    if (!b || b.body === undefined || b.body === null || String(b.body).trim() === "") continue;
    const at = merged.find((x) => x.tag === b.tag);
    if (at) at.body += "\n\n" + String(b.body).trim();
    else merged.push({ tag: b.tag, body: String(b.body).trim() });
  }
  return merged.map((b) => `<${b.tag}>\n${b.body}\n</${b.tag}>`).join("\n\n");
}

/** Скільки важить кожен блок — щоб було видно, за що платиш. */
function weigh(blocks) {
  return blocks.filter((b) => b && String(b.body || "").trim())
    .map((b) => ({ tag: b.tag, chars: String(b.body).trim().length }))
    .sort((a, b) => b.chars - a.chars);
}

const KIND_NAME = { course: "курс", cat: "каталог", sys: "довідник" };
const kindName = (k) => KIND_NAME[k] || "книга";

/** Шапка: повний шлях словами, не машинна адреса. */
const head = (u, extra = []) => [
  `${kindName(u.kind)}: ${u.bookTitle}`,
  `тема: ${u.title}`,
  `тип: ${u.type}${u.version ? ` — ${u.version} версія статті` : ""}`,
  u.groupTitle
    ? (u.kind === "course"
      ? `де лежить: том «${u.groupTitle}» / розділ «${u.chapterTitle}»`
      : `де лежить: група «${u.groupTitle}» / розділ «${u.chapterTitle}»`)
    : null,
  u.type === "code" && u.lang ? `мова: ${u.lang}` : null,
  ...extra,
].filter(Boolean).join("\n");

const knows = (u) => (u.kind === "course" ? "ЩО ЧИТАЧ УЖЕ ПРОЙШОВ" : "ЩО ЧИТАЧ УЖЕ ЗНАЄ");

/* ── запити ────────────────────────────────────────────────────────────────── */

const P = {
  /** Етап 1 · ЦІЛЬ. */
  goal(u, { mentions, passed, linkable, about }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u) },
      { tag: "ЩО ЦЕ ЗА ВСТАВКА", body: about },
      { tag: "ЗГАДКИ В КОРПУСІ", body: mentions },
      { tag: knows(u), body: u.kind === "course" ? passed : "" },
      { tag: "КУДИ МОЖНА ЛІНКУВАТИ", body: u.type === "article" ? linkable : "" },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["goal", ...kindFiles(u)], "goals") },
      { tag: "ПОВЕРНИ", body: answer(u, ["goal"], "goals") },
    ]);
  },

  /** Етап 2 · СТРУКТУРА — лише детальній. */
  structure(u, { goal, shelf }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "КНИГИ, ГРУПИ Й РОЗДІЛИ КОРПУСУ", body: shelf },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["inserts"]) },
      { tag: "ПОВЕРНИ", body: answer(u, ["inserts"]) },
    ]);
  },

  /** Етап 3 · КАРКАС: рівень, розділи, глибина, групи, фігури. Базова — з детальної. */
  karkas(u, { goal, passed, inserts, detailed }) {
    const basic = u.type === "basic";
    const files = [...(basic ? [] : ["karkas"]), "prose", ...kindFiles(u), ...(u.type === "proj" ? ["code-lang"] : [])];
    return render([
      { tag: "ЗАВДАННЯ", body: head(u) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: knows(u), body: u.type === "article" ? passed : "" },
      { tag: "ВСТАВКИ ЦІЄЇ ТЕМИ", body: inserts },
      { tag: "ДЕТАЛЬНА СТАТТЯ", body: basic ? detailed : "" },
      { tag: "ЩО ЗРОБИТИ", body: order(u, files, "karkas") },
      { tag: "ПОВЕРНИ", body: answer(u, basic ? [] : ["karkas"], "karkas") },
    ]);
  },

  /** Етап 4 · ПИСЬМО — порція розділів. */
  write(u, { goal, level, depth, sections, theses, integrate, passed, linkable }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`рівень: ${level || "—"}`]) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "ГЛИБИНА", body: depth },
      { tag: knows(u), body: hasTheses(u) ? passed : "" },
      { tag: "МОЇ РОЗДІЛИ", body: sections },
      { tag: "ТЕЗИ ПОПЕРЕДНІХ РОЗДІЛІВ", body: theses },
      { tag: "ЩО ІНТЕГРУВАТИ", body: integrate },
      { tag: "КУДИ МОЖНА ЛІНКУВАТИ", body: linkable },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["mode-write", "scale", ...writers(u)], "rules") },
      { tag: "ПОВЕРНИ", body: answer(u, ["mode-write", ...(hasTheses(u) ? ["theses"] : [])]) },
    ]);
  },

  /** Етап 4 · ДОПИСУВАННЯ — один розділ, названим матеріалом, мірою з конвеєра. */
  extend(u, { goal, level, depth, section: sec, text, theses, add, floor, ceiling, integrate, linkable }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`рівень: ${level || "—"}`]) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "ГЛИБИНА", body: depth },
      { tag: "ЦЕЙ РОЗДІЛ", body: `${sec}\n\n${text}` },
      { tag: "ТЕЗИ ІНШИХ РОЗДІЛІВ", body: theses },
      { tag: "ЩО ДОДАТИ", body: add },
      { tag: "МІРА", body: `нового тексту — не менше ${floor} слів і не більше ${ceiling}` },
      { tag: "ЩО ІНТЕГРУВАТИ", body: integrate },
      { tag: "КУДИ МОЖНА ЛІНКУВАТИ", body: linkable },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["mode-extend", "scale", ...writers(u)], "rules") },
      { tag: "ПОВЕРНИ", body: answer(u, ["mode-write", ...(hasTheses(u) ? ["theses"] : [])]) },
    ]);
  },

  /** Етап 4 · СТИСНЕННЯ — один розділ, названим матеріалом. */
  compress(u, { goal, level, section: sec, text, theses, squeeze, by }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`рівень: ${level || "—"}`]) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "ЦЕЙ РОЗДІЛ", body: `${sec}\n\n${text}` },
      { tag: "ТЕЗИ ІНШИХ РОЗДІЛІВ", body: theses },
      { tag: "ЩО ЗЖАТИ", body: squeeze },
      { tag: "НАСКІЛЬКИ", body: `приблизно на ${by} слів` },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["mode-compress", "prose", "language", "formulas", ...kindFiles(u)], "rules") },
      { tag: "ПОВЕРНИ", body: answer(u, ["mode-compress"]) },
    ]);
  },

  /** Етап 5 · АНАЛІЗ — увесь текст, тези, ціль → оцінки й речення з фактами. */
  analysis(u, { goal, level, text, theses, groups, force }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`рівень: ${level || "—"}`]) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "ТЕКСТ", body: text },
      { tag: "ТЕЗИ", body: theses },
      { tag: "ГРУПИ РОЗДІЛІВ", body: groups },
      { tag: "ЧОГО БРАКУЄ", body: force ? "Тексту бракує багато — назви місця, де його дописати." : "" },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["mode-analysis", "prose"], "goals") },
      { tag: "ПОВЕРНИ", body: answer(u, ["mode-analysis"]) },
    ]);
  },

  /** Етап 5 · ФАКТИ — речення з фактами й формулами на веб-перевірку. */
  facts(u, { lines }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u) },
      { tag: "РЕЧЕННЯ", body: lines },
      { tag: "ЩО ЗРОБИТИ", body: ask(["facts-check"]) },
      { tag: "ПОВЕРНИ", body: ret(["facts-check"]) },
    ]);
  },

  /** Етап 4 · ВСТАВКА ЗОБРАЖЕННЯ, крок 1: у який розділ. */
  imageWhere(u, { text, what }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, ["крок: 1"]) },
      { tag: "ТЕКСТ", body: text },
      { tag: "ФІГУРА", body: what },
      { tag: "ЩО ЗРОБИТИ", body: ask(["mode-image", "figures"]) },
      { tag: "ПОВЕРНИ", body: ret(["mode-image"]) },
    ]);
  },

  /** Етап 4 · ВСТАВКА ЗОБРАЖЕННЯ, крок 2: поставити. */
  imagePlace(u, { text, section: sec, file, what }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, ["крок: 2", `розділ: ${sec}`, `файл: ${file}`]) },
      { tag: "ТЕКСТ", body: text },
      { tag: "ФІГУРА", body: what },
      { tag: "ЩО ЗРОБИТИ", body: ask(["mode-image", "figures"]) },
      { tag: "ПОВЕРНИ", body: ret(["mode-image"]) },
    ]);
  },

  /** Код · АРХІТЕКТУРА. */
  codeKarkas(u, { goal }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "ЩО РЕАЛІЗУВАТИ", body: u.about },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["code-lang"], "karkas") },
      { tag: "ПОВЕРНИ", body: answer(u, [], "karkas") },
    ]);
  },

  /** Код · ФАЙЛИ. */
  codeWrite(u, { goal, level, files, classes, structure }) {
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`рівень: ${level || "—"}`]) },
      { tag: "ЦІЛЬ", body: goal },
      { tag: "ФАЙЛИ", body: files },
      { tag: "КЛАСИ", body: classes },
      { tag: "СТРУКТУРА", body: structure },
      { tag: "ЩО ЗРОБИТИ", body: order(u, ["code-lang"], "rules") },
      { tag: "ПОВЕРНИ", body: answer(u, [], "rules") },
    ]);
  },

  /** Фігура · МАЛЮВАННЯ. Статті не бачить: що зображено — вирішив каркас. */
  figure(u, { goal, what, section: sec, file, level }) {
    const rules = readType("fig", "rules");
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`розділ: ${sec}`, `рівень: ${level || "—"}`, `файл: ${file}`]) },
      { tag: "ЦІЛЬ ТЕМИ", body: goal },
      { tag: "ЩО ЗОБРАЗИТИ", body: what },
      { tag: "ЩО ЗРОБИТИ", body: [bookCanon(u), section(rules, ASK)].filter(Boolean).join("\n\n") },
      { tag: "ПОВЕРНИ", body: section(rules, RET) },
    ]);
  },

  /** Фігура · ПЕРЕМАЛЮВАННЯ названих місць; задум той самий. */
  figureFix(u, { what, file, svg, issues, attempt }) {
    const rules = readType("fig", "rules");
    return render([
      { tag: "ЗАВДАННЯ", body: head(u, [`файл: ${file}`, attempt > 1 ? `спроба ${attempt}` : ""]) },
      { tag: "ЩО ЗОБРАЗИТИ", body: what },
      { tag: "ФІГУРА ЗАРАЗ", body: svg },
      { tag: "ЩО НЕ ТАК", body: issues },
      { tag: "ЩО ЗРОБИТИ", body: section(rules, ASK) },
      { tag: "ПОВЕРНИ", body: section(rules, RET) },
    ]);
  },

  /** Етап 8 · НОВА ТЕМА, запит 1: куди завести. */
  topicsCategory({ shelf, topic }) {
    return render([
      { tag: "КНИГИ, ГРУПИ Й РОЗДІЛИ КОРПУСУ", body: shelf },
      { tag: "ТЕМА", body: topic },
      { tag: "ЩО ЗРОБИТИ", body: ask(["topics-category"]) },
      { tag: "ПОВЕРНИ", body: ret(["topics-category"]) },
    ]);
  },

  /** Етап 8 · НОВА ТЕМА, запит 2: є вже чи нова. */
  topicsDedupe({ existing, topic }) {
    return render([
      { tag: "ТЕМИ ЦІЄЇ КАТЕГОРІЇ", body: existing },
      { tag: "ТЕМА", body: topic },
      { tag: "ЩО ЗРОБИТИ", body: ask(["topics-dedupe"]) },
      { tag: "ПОВЕРНИ", body: ret(["topics-dedupe"]) },
    ]);
  },

  /** Етап 8 · НОВА ТЕМА, запит 3: дубль чи розвести назви. */
  topicsRename({ existing, ours, reason }) {
    return render([
      { tag: "НАЯВНА ТЕМА", body: existing },
      { tag: "НАШЕ МІСЦЕ", body: ours },
      { tag: "ЧОМУ ЗІСТАВИЛИ", body: reason },
      { tag: "ЩО ЗРОБИТИ", body: ask(["topics-rename"]) },
      { tag: "ПОВЕРНИ", body: ret(["topics-rename"]) },
    ]);
  },
};

module.exports = { ...P, render, weigh, section, readType, readRule, ask, ret, head, bookCanon, kindFiles, writers };
