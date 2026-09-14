#!/usr/bin/env node
/* ============================================================================
   dryrun.js — СУХИЙ ПРОГІН УСЬОГО АЛГОРИТМУ З ПІДРОБНИМ АГЕНТОМ. Нуль токенів.

   Кожен запит дістає відповідь, зібрану з його ж контракту <ПОВЕРНИ>: підробка дивиться,
   які теги просять, і заповнює їх правдоподібним вмістом. Так проходяться всі етапи
   1–10 і всі дороги — дописування, стиснення, переписування з нуля, факти, вставка
   фігури, зведення нових тем, — і ловляться помилки виконання та розриви між тим, що
   просить контракт, і тим, що читає алгоритм. Файли пишуться в `inwork/_smoke/`.

   Ужиток:  node writer_ua/checkers/dryrun.js
            SCORE=5  — перша оцінка аналізу низька: переписування з нуля
            NEWGROUP=1 — етап 8 заводить нову групу за відповіддю
            SHORT=1  — письмо крихітне: бракує понад третину, аналіз називає місця
            SHORTINS=1 — історія коротка: абзац у тексті, одиниці вставки нема
            DUMP=письмо — надрукувати перший запит, чия мітка так починається
            OVER=1   — письмо величезне: стиснення названим
            TYPE=hist|proj|basic — вставка, проєкт (пауза на код), базова
   ========================================================================== */
"use strict";
const path = require("path");
const fs = require("fs");
const ROOT = path.join(__dirname, "..", "..");
const A = require(ROOT + "/writer_ua/runners/algorithm.js");
const LOC = require(ROOT + "/writer_ua/runners/local.js");
const MF = require(ROOT + "/writer_ua/lib/manifest.js");

const OUT = path.join(ROOT, "inwork", "_smoke");   // під коренем репо: шляхи в конвеєрі відносні від нього; inwork у .gitignore
fs.rmSync(OUT, { recursive: true, force: true });
fs.mkdirSync(OUT, { recursive: true });

/* тема з pending детальною */
let book = null, t = null;
for (const [slug, b] of MF.books()) {
  if (b.kind !== "sci" && b.kind !== "eng") continue;
  const bk = MF.loadBook(b.bookDir);
  const unwritten = (x) => !fs.existsSync(path.join(b.bookDir, x.slug, `${x.slug}-d.md`)) && !fs.existsSync(path.join(b.bookDir, x.slug, `${x.slug}.md`));
  const c = bk && MF.allTopics(bk).find((x) => x.own && unwritten(x));
  if (c) { book = slug; t = c; break; }
}
if (!t) throw new Error("ненаписаної теми нема ніде");
const TYPE = process.env.TYPE || "article";
const u = TYPE === "article" ? { ...LOC.unitOf(book, t.slug), dir: OUT }
  : TYPE === "basic" ? { ...LOC.unitOf(book, t.slug, "basic", "базова"), dir: OUT }
  : { ...LOC.unitOf(book, t.slug, TYPE, "", `${TYPE}-probe`), dir: OUT, about: "Опис вставки з етапу 2: про що вона." };
if (TYPE === "basic") fs.writeFileSync(path.join(OUT, `${t.slug}-d.md`), `# ${t.title}\n\n## Розділ 1\n\nтекст детальної.\n\n![с](img/state-transitions.svg)\n`, "utf8");
console.log("одиниця:", u.id, "→", OUT);

const words = (n, seed) => Array.from({ length: n }, (_, i) => ["механізм", "стан", "перехід", "автомат", "читач", "тому", "звідси", "правило", "приклад", "межа"][(i * 7 + seed) % 10]).join(" ");
let calls = 0;
const log = [];
const MODE = { score: Number(process.env.SCORE || 8), short: !!process.env.SHORT, over: !!process.env.OVER };
let analyses = 0;

let dumped = false;
function fake(prompt, label) {
  calls++;
  /* DUMP=<початок мітки> — надрукувати перший такий запит цілком: видно, що саме їде агентові. */
  if (process.env.DUMP && !dumped && String(label).startsWith(process.env.DUMP)) { dumped = true; console.log(`
──── запит «${label}» ────
${prompt}
──── кінець ────`); }
  log.push(label);
  const tags = [...prompt.slice(prompt.indexOf("<ПОВЕРНИ>")).matchAll(/<([А-ЯІЇЄҐA-Z][^<>\n]*?)>/g)].map((m) => m[1].trim());
  const need = new Set(tags.filter((x) => x !== "ПОВЕРНИ"));
  const file = (prompt.match(/файл: (\S+)/) || [])[1] || "img/fig-1.svg";
  const sec = (prompt.match(/розділ: (\d+)/) || [])[1] || "1";
  const out = [];
  const put = (tag, body) => { if (need.has(tag)) out.push(`<${tag}>\n${body}\n</${tag}>`); };
  put("ЦІЛЬ", "Читач має зрозуміти, як автомат читає слово і чому станів вистачає. " + words(30, 1) + ".");
  put("ПЕРЕДУМОВИ", "Скінченні автомати — root:computability/finite-automata — що таке стан і перехід");
  put("ВСТАВКИ", "hist-automata-birth | Як народилась ідея автомата: яка задача, хто, чому саме так. " + words(20, 2) + ".");
  /* П'ять питань етапу 2: одна історія, решта — «нема: чому» (розбір їх відкидає). */
  put("ЧИ Є ІСТОРІЯ", "hist-automata-birth | Як народилась ідея автомата: яка задача, хто, чому саме так. " + words(20, 2) + ".");
  put("ЧИ Є МАТЕМАТИКА", "нема: обрахунків у темі немає");
  put("ЧИ Є ПРОЄКТ", TYPE === "proj" ? "нема" : "нема: реалізації окремо не треба");
  put("ЧИ Є КОМПОНЕНТ", "нема: класу пристрою за темою не стоїть");
  put("ЧИ Є API", "нема: інтерфейсу немає");
  put("НОВІ ТЕМИ", "regular-grammar-probe | Регулярна граматика | computability / computation-models | Що таке регулярна граматика і як вона породжує мову.");
  put("БАЗОВА", "ні");
  put("РІВЕНЬ", "2");
  put("РОЗДІЛИ", "1 | Назва розділу 1 | важливість: висока | Що ламається без автомата: " + words(20, 3) + ".\n2 | Назва розділу 2 | важливість: середня | Як автомат читає слово: " + words(20, 4) + ".\n3 | Назва розділу 3 | важливість: низька | Де межа: " + words(20, 5) + ".");
  put("ГЛИБИНА", "До детермінованих автоматів; недетерміновані лише називаємо.");
  put("ФОРМА ВСТАВОК", TYPE === "article" ? (process.env.SHORTINS ? "hist-automata-birth | коротка | 1" : "hist-automata-birth | повна") : "");
  put("ГРУПИ", "1, 2\n3");
  if (/ФІГУРИ БЕЗ МІСЦЯ|ТЕМИ БЕЗ ЛІНКА/.test(prompt)) {
    /* Розставлення: кожній фігурі й темі без місця — розділ, абзац (перші слова), підпис чи речення. */
    const figsLeft = [...(prompt.match(/<ФІГУРИ БЕЗ МІСЦЯ>([\s\S]*?)<\/ФІГУРИ БЕЗ МІСЦЯ>/) || ["", ""])[1].matchAll(/^(\S+\.svg)/gm)].map((x) => x[1]);
    const topicsLeft = [...(prompt.match(/<ТЕМИ БЕЗ ЛІНКА>([\s\S]*?)<\/ТЕМИ БЕЗ ЛІНКА>/) || ["", ""])[1].matchAll(/^(root:new\/\S+)/gm)].map((x) => x[1]);
    put("МІСЦЯ ФІГУР", figsLeft.map((f) => `${f} | 2 | ${words(3, 2)} | Стрілки показують, куди веде кожен символ.`).join("\n"));
    put("МІСЦЯ ЛІНКІВ", topicsLeft.map((a) => `${a} | 1 | ${words(3, 1)} | Про це окремо — [регулярна граматика](${a}).`).join("\n"));
  } else put("ФІГУРИ", TYPE === "basic" ? "2 | img/state-transitions.svg" : "2 | state-transitions | Схема переходів між станами: кола й стрілки, вхід і два стани.");
  put("КОД", TYPE === "proj" ? "python | реалізація автомата, що читає слово" : "");
  if (need.has("АБЗАЦ")) {
    const para = (prompt.match(/<АБЗАЦ>\n([\s\S]*?)\n<\/АБЗАЦ>/) || ["", ""])[1].trim();
    put("АБЗАЦ", /поглибити/.test((prompt.match(/<ЯК>\n([\s\S]*?)\n<\/ЯК>/) || ["", ""])[1]) ? `${para} ${words(120, 5)}.` : `${words(140, 6)}.`);
  }
  if (need.has("ТЕКСТ")) {
    if (/крок: 2/.test(prompt)) {
      const src = prompt.slice(prompt.indexOf("<ТЕКСТ>") + 7, prompt.indexOf("</ТЕКСТ>")).trim();
      const addr = (prompt.match(/адреса: (\S+)/) || [])[1];   // лінк на нову тему — інакше фігура
      put("ТЕКСТ", addr
        ? src + `\n\nПро це окремо — [регулярна граматика](${addr}).`
        : src + `\n\n![схема переходів](${file})\n*Стрілки показують, куди веде кожен символ.*`);
    } else if (/<ЦЕЙ РОЗДІЛ>/.test(prompt)) {
      const head = (prompt.match(/<ЦЕЙ РОЗДІЛ>\n\d+[^\n]*\n\n(## [^\n]*)/) || [])[1] || "## Розділ";
      const n2 = /<НАСКІЛЬКИ>/.test(prompt) ? 900 : 700;   // стиснення повертає коротше
      put("ТЕКСТ", `${head}\n\n${words(n2, 9)}. У 1969 році щось сталося. ${words(n2, 11)}.`);
    } else {
      const secs = [...prompt.matchAll(/^(\d+) \| (?:[^|\n]+\| )?важливість: [^|]+\| /gm)].map((m) => m[1]);
      const n1 = MODE.short ? 120 : MODE.over ? 4000 : 450;
      put("ТЕКСТ", secs.map((n, i) => `## Розділ ${n}\n\n${words(n1, i + 1)}. ${i === 0 ? "У 1969 році щось сталося. " : ""}${words(150, i + 20)}.`).join("\n\n"));
    }
  }
  put("ЩО ЗЖАТИ", MODE.over ? "1 | повтори прикладів\n2 | зайві варіації" : "");
  put("ЩО ДОДАТИ", "1 | 5 | новий після «У 1969 році» | розкрити, чому станів скінченно\n2 | 3 | поглибити «Розділ 2» | приклад слова, яке не приймається");
  put("ТЕЗИ", "1 | сказано, що ламається без автомата\n2 | сказано, як читається слово");
  put("НОВІ SVG", "");
  if (need.has("БАЛИ")) {
    /* Бали за критеріями: перший аналіз — сума MODE.score, далі 8; розкладаємо по стелях. */
    const maxes = [["нитка", 3], ["захід", 1], ["фігури", 1], ["формули", 1], ["код", 1], ["від потреби", 1], ["нове з наявного", 1], ["без повторів", 1], ["мова", 1]];
    let left = analyses++ === 0 ? MODE.score : 8;
    put("БАЛИ", maxes.map(([n, m]) => { const v = Math.min(m, left); left -= v; return `${n} | ${v} | ${v ? "є" : "бракує"}`; }).join("\n"));
  }
  put("ІСТОРІЯ", "У 1969 році щось сталося.");
  put("ФОРМУЛИ", "");
  put("ДЕ ДОПИСАТИ", "1 | новий після «У 1969 році» | не розкрито, чому станів скінченно\n3 | новий після «Розділ 3» | межа лише названа");
  put("ЗАМІНИ", "У 1969 році щось сталося. :: У 1943 році щось сталося.");
  put("РОЗДІЛ", /КНИГИ, ГРУПИ/.test(prompt) ? "no-such-chapter" : sec);   // навмисно чужий слуг: перевірка захисту
  put("КНИГА", book);
  put("ГРУПА", process.env.NEWGROUP ? "probe-group" : u.group);
  put("ЧОМУ", "бо це про мову, а не про машину");
  put("НОВА ГРУПА", process.env.NEWGROUP ? `${book} | probe-group | Проба групи | Сюди все, що про пробу.` : "");
  put("НОВИЙ РОЗДІЛ", "");
  put("ВЕРДИКТ", "нова");
  put("НАЗВИ", "");
  /* Пакетний етап 8: усі теми з блоку НОВІ ТЕМИ — по рядку. */
  const newTopics = [...(prompt.match(/<НОВІ ТЕМИ>\n([\s\S]*?)\n<\/НОВІ ТЕМИ>/) || ["", ""])[1].matchAll(/^([a-z0-9-]+) \|/gm)].map((x) => x[1]);
  put("ТЕМИ", newTopics.map((s) => `${s} | ${book} | ${process.env.NEWGROUP ? "probe-group" : u.group} | no-such-chapter | бо це про мову, а не про машину`).join("\n"));
  put("ВЕРДИКТИ", newTopics.map((s) => `${s} | нова`).join("\n"));
  put("ЗБІГИ", "");
  put("SVG", "<svg></svg>");
  return out.join("\n\n");
}

/* ctx у пам'яті */
const state = {};
const enq = [];
const ctx = {
  set: (f, v) => { state[f] = v === undefined ? null : v; return ctx; },
  get: (f) => state[f] === undefined ? null : state[f],
  call: (label, fn) => Promise.resolve().then(fn),
  enqueue: (more) => { enq.push(...more); return more.length; },
  isDone: () => false,
};

(async () => {
  try {
    const r = await A.algorithm(u, ctx, { ask: fake, status: "done" });
    console.log("\n── результат ──");
    console.log("файл:", r.file);
    console.log("ops:", JSON.stringify(r.ops));
    console.log("запитів:", calls);
    console.log("порядок:", log.join(" → "));
    console.log("у чергу:", enq.map((x) => x.id).join(", "));
    const s = state;
    console.log("\nsize:", JSON.stringify({ words: s.size.words, need: s.size.need, rounds: s.size.rounds, forced: s.size.forced, stillShort: s.size.stillShort }));
    console.log("analysis:", JSON.stringify({ score: s.analysis.score, rewrites: s.analysis.rewrites, facts: s.analysis.facts }));
    console.log("facts:", JSON.stringify(s.facts));
    console.log("figures:", JSON.stringify(s.figures));
    console.log("links:", JSON.stringify(s.links));
    console.log("topics:", JSON.stringify(s.topics));
    console.log("assembly:", JSON.stringify(s.assembly).slice(0, 300));
    const txt = fs.readFileSync(path.join(ROOT, r.file), "utf8");
    console.log("\nфайл: слів", LOC.size(txt, "article", 2).words, "· H1:", (txt.match(/^# /gm) || []).length, "· H2:", (txt.match(/^## /gm) || []).length,
      "· 1943:", txt.includes("1943"), "· фігура:", txt.includes("img/state-transitions.svg"), "· root:new:", txt.includes("root:new"),
      "· лінк на нову тему:", txt.includes("/regular-grammar-probe)"), "· preknowlist:", txt.includes("<preknowlist>"));
  } catch (e) {
    if (e.pause) { console.log("\n⏸ ПАУЗА, чекає:", e.waitFor.join(", "), "· у чергу:", enq.map((x) => x.id).join(", ")); return; }
    console.log("\n⛔ ВПАЛО:", e.stack);
    console.log("порядок:", log.join(" → "));
    console.log("стан:", Object.keys(state).filter((k) => state[k] !== null).join(", "));
  }
})();
