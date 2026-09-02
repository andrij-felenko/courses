#!/usr/bin/env node
/* ============================================================================
   count.js — СКІЛЬКИ там слів, символів, рядків і коду. Звітує, НЕ судить.

   ⛔ Тут немає підлог, стель, смуг і слова «порушення». Показане число стає ціллю:
   поки в таблиці стояв орієнтир, детальні лягали в ±2% від нього, а коли орієнтир
   прибрали, письмо сповзло на нижній край смуги. Тому ця команда лише міряє;
   рішення, чи це замало, ухвалює людина — і ніхто інший.

   Проза міряється ситом `writer_ua/lib/text.js`: воно відкидає огорожі, таблиці,
   рядки-зображення і директиви `:::`. Директива — це посилання, яке стало на місце
   коду, а не текст; лишивши її в ліку, 53 219 рядків `:::` корпусу дали б близько
   163 тисяч фантомних слів рівно в тих файлах, де коду найбільше.

   Тому числа тут НЕ збігаються з `scripts/wordcount.js`, який рядки `:::` за прозу
   вважає, і це не поламка, а різні означення прози. Звіряючи, шукай різницю в
   директивах, а не помилку.

   Код — звідти ж: `langDirs` і `codeLines` (файли збірки й тести з ліку виключені,
   відбір за ІМЕНЕМ, не за розширенням). Тека, де крім них нічого немає, чесно
   показує 0 і дістає в таблиці зірочку — щоб «0» не читалося як «порожньо».

   Відбір — спільна мова з `find` і `status` (lib/units.js).
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const U = require("./lib/units.js");
const TXT = require("../lib/text.js");

const HELP = `
count — міряє прозу й код відібраних одиниць

  node writer_ua/local/count.js [кого] [вивід]

КОГО
  --addr a,b,c         адреси через кому
  (труба)              адреси по одній на рядок — вихід find --ids
  фільтри find         --book --kind --group --chapter --type --status
                       --not-status --slug --title --level --recode/--no-recode
                       --own/--ref --has-file/--no-file --has-code/--no-code

ВИВІД (взаємовиключні)
  (типово)             таблиця по одиницях
  --sum                тільки підсумок: скільки, медіана, чверті, край
  --json               повні записи

  --limit N            перші N рядків списку — таблиці або --json;
                       із --sum не поєднується: підсумок рахує все

КОЛОНКИ
  слова     проза за ситом _lib.proseWords (огорожі й ::: не рахуються;
            wordcount.js ::: рахує, тому там числа трохи більші — див. шапку)
  симв      символи прози тим самим ситом
  рядки     рядки файла, як він лежить
  фіг       підключених зображень
  огор      рядків коду, що ЩЕ лежить в огорожах (мало б виїхати у файли)
  код       рядки по теках мов: c=120 cpp=140
            * у теці лише файли збірки чи тести — у лік рядків вони не входять
`;

/* ── мірило ────────────────────────────────────────────────────────────────── */

/**
 * Символи прози й підключені зображення — тим самим ситом, що й слова в `_lib`:
 * ті самі рядки відкидаємо, ті самі лишаємо. Слова звідти приходять готовим
 * числом, а символів і фігур воно не рахує, тож сито доводиться повторити — але
 * дослівно, рядок у рядок, інакше колонки поруч міряли б різне.
 */
function proseCharsAndFigs(md) {
  let inCode = false, chars = 0, figs = 0;
  for (const line of md.split(/\r?\n/)) {
    const t = line.trim();
    if (/^```/.test(t)) { inCode = !inCode; continue; }
    if (inCode) continue;
    if (/^!\[/.test(t)) { figs++; continue; }
    if (/^:::/.test(t) || /^\|.*\|/.test(t)) continue;
    chars += [...line
      .replace(/`[^`]*`/g, " ")
      .replace(/!\[[^\]]*\]\([^)]*\)/g, " ")
      .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
      .replace(/^>\s*/, "").replace(/^[-*]\s+/, "").replace(/[*_#>`~]/g, " ")
      .trim()].length;
  }
  return { chars, figs };
}

/** Одна одиниця: числа й нічого крім них. Файла немає — так і кажемо. */
function measure(u) {
  const file = U.fileOf(u);
  const row = { addr: U.addrOf(u), title: u.title, status: u.status ?? null, level: u.level ?? null, file };
  if (!file || !fs.existsSync(file)) return { ...row, exists: false, words: 0, chars: 0, lines: 0, figs: 0, fenced: 0, code: [], codeLines: 0 };

  const md = fs.readFileSync(file, "utf8");
  const words = TXT.proseWords(md);
  const { chars, figs } = proseCharsAndFigs(md);
  const code = TXT.langDirs(path.dirname(file), path.basename(file))
    .map((d) => ({ lang: d.lang, ...TXT.codeLines(d.dir) }));

  return {
    ...row, exists: true,
    words, chars,
    lines: md.replace(/\r\n?/g, "\n").replace(/\n+$/, "").split("\n").length,
    figs, fenced: TXT.fencedCode(md),
    code, codeLines: code.reduce((s, c) => s + c.lines, 0),
  };
}

/* ── підсумок ──────────────────────────────────────────────────────────────── */

const quantile = (sorted, q) => {
  if (!sorted.length) return 0;
  const i = (sorted.length - 1) * q, lo = Math.floor(i), hi = Math.ceil(i);
  return lo === hi ? sorted[lo] : Math.round(sorted[lo] + (sorted[hi] - sorted[lo]) * (i - lo));
};

function summary(rows) {
  const live = rows.filter((r) => r.exists);
  const out = [`одиниць: ${rows.length}   з файлом: ${live.length}   без файла: ${rows.length - live.length}`];
  if (!live.length) return out.join("\n");

  for (const [name, key] of [["слова", "words"], ["символи", "chars"], ["рядки", "lines"]]) {
    const v = live.map((r) => r[key]).sort((a, b) => a - b);
    out.push(`${name.padEnd(9)} медіана ${String(quantile(v, 0.5)).padStart(6)}   ` +
      `чверті ${quantile(v, 0.25)}–${quantile(v, 0.75)}   край ${v[0]}–${v[v.length - 1]}   ` +
      `разом ${v.reduce((s, x) => s + x, 0)}`);
  }
  const withCode = live.filter((r) => r.code.length);
  if (withCode.length) {
    const byLang = new Map();
    for (const r of withCode) for (const c of r.code) {
      const p = byLang.get(c.lang) || { lines: 0, files: 0, units: 0 };
      p.lines += c.lines; p.files += c.files; p.units++; byLang.set(c.lang, p);
    }
    out.push(`\nз кодом: ${withCode.length}`);
    for (const [lang, p] of [...byLang].sort((a, b) => b[1].lines - a[1].lines))
      out.push(`  ${lang.padEnd(8)} ${String(p.lines).padStart(7)} рядків  ${String(p.files).padStart(5)} файлів  у ${p.units} одиницях`);
  }
  const fenced = live.filter((r) => r.fenced);
  if (fenced.length)
    out.push(`\nще в огорожах: ${fenced.reduce((s, r) => s + r.fenced, 0)} рядків у ${fenced.length} одиницях`);
  return out.join("\n");
}

/* ── таблиця ───────────────────────────────────────────────────────────────── */

/* Правило ліку не міняємо (файли збірки й тести з нього виключені навмисно), але й
   не брешемо: тека, де крім них нічого немає, дала б голий `make=0` — читається як
   «порожня», хоч на диску файл лежить. Зірочка й розшифровка в HELP. */
const codeCell = (c) => `${c.lang}=${c.lines}` + (!c.files && (c.build || c.tests) ? "*" : "");

function table(rows) {
  const cells = rows.map((r) => [
    r.addr,
    r.exists ? String(r.words) : "—",
    r.exists ? String(r.chars) : "—",
    r.exists ? String(r.lines) : "—",
    r.figs ? String(r.figs) : "",
    r.fenced ? String(r.fenced) : "",
    r.code.map(codeCell).join(" "),
  ]);
  const head = ["адреса", "слова", "симв", "рядки", "фіг", "огор", "код"];
  const num = [false, true, true, true, true, true, false];
  const w = head.map((h, i) => Math.max([...h].length, ...cells.map((r) => [...r[i]].length)));
  const line = (r) => r.map((c, i) => {
    const pad = " ".repeat(w[i] - [...c].length);
    return num[i] ? pad + c : c + pad;
  }).join("  ").trimEnd();
  return [line(head), w.map((n) => "─".repeat(n)).join("  "), ...cells.map(line)].join("\n");
}

/* ── головне ───────────────────────────────────────────────────────────────── */

/**
 * Один файл вставки, зареєстрований у маніфесті під двома типами, приходить із
 * фільтра двома одиницями з ОДНАКОВОЮ адресою. Файл один — і виміряти його треба
 * один раз, інакше його слова двічі входять у підсумок, і число бреше. Через
 * `--addr` така одиниця пропускається зовсім (`byAddrs` вважає адресу
 * неоднозначною), тож рівняємося на менше: беремо першу, а про ваду ДАНИХ
 * попереджаємо переліком — як `warnDupes` у find.
 */
function dedupe(units) {
  const seen = new Set(), dupes = new Set(), out = [];
  for (const u of units) {
    const a = U.addrOf(u);
    if (a !== null) {                                     // вказівник адреси не має — його не зводимо
      if (seen.has(a)) { dupes.add(a); continue; }
      seen.add(a);
    }
    out.push(u);
  }
  if (dupes.size)
    console.error(`count: увага — повторені адреси зведено до однієї (${dupes.size}): ${[...dupes].join(", ")}`);
  return out;
}

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h")) { console.log(HELP.trim()); return 0; }

  const { flags, rest } = U.parseArgs(argv);
  let addrs = null, sum = false, json = false, limit = 0;
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--sum") sum = true;
    else if (a === "--json") json = true;
    else if (a === "--addr") {
      if (addrs) throw new Error("--addr двічі");
      const v = rest[++i];
      if (v === undefined || v.startsWith("--")) throw new Error("--addr без значення");
      addrs = v.split(",").map((s) => s.trim()).filter(Boolean);
      if (!addrs.length) throw new Error("--addr порожній");
    } else if (a === "--limit") {
      const n = Number(rest[++i]);
      if (!Number.isInteger(n) || n <= 0) throw new Error("--limit хоче ціле додатне");
      limit = n;
    } else throw new Error(`невідомий прапорець: ${a}`);
  }
  if (sum && json) throw new Error("разом не можна: --sum --json — вивід один");
  /* `--limit` ріже СПИСОК — таблицю чи --json, однаково. Підсумок списком не є: він
     рахує все, і зрізати його нічим, тож пара --sum --limit це не «перші N», а
     непорозуміння — краще впасти, ніж мовчки викинути прапорець (так і було). */
  if (sum && limit) throw new Error("--limit із --sum не працює — підсумок рахує все, різати нічого");

  /* Джерело адрес — за наявністю, не за кількістю: порожня труба це «нічого не
     надійшло», а не «візьми фільтри». Той самий запобіжник, що й у status. */
  const pipe = U.stdinAddrs();
  if (addrs && pipe.given && pipe.addrs.length) throw new Error("адреси й труба разом — вибери щось одне");
  const addrMode = !!addrs || pipe.given;
  const hasFilters = Object.keys(flags).length > 0;

  let units;
  if (addrMode) {
    if (hasFilters) throw new Error("адреси й фільтри разом — вибери щось одне");
    const src = addrs || pipe.addrs;
    if (!src.length) { console.log("адрес не надійшло — міряти нічого"); return 0; }
    const got = U.byAddrs(src);
    if (got.ambiguous.length)
      console.error(`count: неоднозначних адрес пропущено (${got.ambiguous.length}): ` +
        got.ambiguous.slice(0, 5).map((a) => `${a.addr} (${a.types.join(", ")})`).join(", "));
    /* Просили поміряти адресу, якої немає, — це помилка виклику, а не порожній
       результат. Код 2, як у status на тому самому byAddrs. */
    if (got.missing.length) {
      console.error(`count: не знайшлося (${got.missing.length}): ${got.missing.slice(0, 5).join(", ")}${got.missing.length > 5 ? " …" : ""}`);
      return 2;
    }
    units = got.units;
  } else if (hasFilters) {
    U.validate(flags);
    units = dedupe(U.filter(U.enumerate({ kinds: flags.kinds, books: flags.books }), flags));
  } else throw new Error("кого міряти — дай --addr, трубу з find --ids або фільтри");

  const refs = units.filter((u) => u.slug == null);
  if (refs.length) console.error(`count: ${refs.length} вказівників пропущено — власного файла вони не мають`);
  units = units.filter((u) => u.slug != null);
  if (!units.length) { console.log("міряти нічого"); return 0; }

  units.sort((a, b) => a.book.localeCompare(b.book) || a.slug.localeCompare(b.slug) ||
    String(a.part).localeCompare(String(b.part)));

  const rows = units.map(measure);
  if (sum) { console.log(summary(rows)); return 0; }

  const shown = limit ? rows.slice(0, limit) : rows;
  if (json) { console.log(JSON.stringify(shown, null, 1)); return 0; }
  console.log(table(shown));
  console.log("\n" + summary(rows));
  if (limit && rows.length > limit) console.log(`\nпоказано ${limit} з ${rows.length}`);
  return 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("count: " + e.message); process.exit(2); }
}
module.exports = { main, measure };
