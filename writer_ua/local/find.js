#!/usr/bin/env node
/* ============================================================================
   find.js — ПОШУК одиниць корпусу. Читає, не пише. Нуль токенів.

   Мова відбору спільна зі `status` (writer_ua/local/lib/units.js), тож обидві
   команди склеюються трубою, а запис лишається окремою явною дією:

     find --book embedded --status deeper --has-code          таблиця для очей
     find --book embedded --status deeper --ids | status …    список для труби

   ⛔ Ця команда НІЧОГО не змінює. Усе, що вона вміє, — показати й порахувати.
   ========================================================================== */
"use strict";
const U = require("./lib/units.js");

const HELP = `
find — пошук тем, версій і вставок за параметрами

  node writer_ua/local/find.js [фільтри] [вивід]

ВІДБІР
  --kind sci,course       вид книги
  --book embedded,unix    книга (слуг)
  --group <слуг,…>        група в маніфесті
  --chapter <слуг,…>      розділ у маніфесті
  --type detailed,proj    basic detailed hist comp math proj api
  --status deeper,pending done pending empty update deeper recheck
  --not-status done       усе, крім названого
  --slug "i2c-*"          слуг теми; * дозволена
  --title "черга"         підрядок назви, без регістру
  --level 3 | 2-4 | 3-    рівень (лише там, де він проставлений)
  --recode | --no-recode  прапорець переписування коду
  --own | --ref           власна стаття / вказівник на чужу
  --has-file | --no-file  чи лежить .md на диску
  --has-code | --no-code  чи є поруч тека коду

ВИВІД (взаємовиключні: --ids --json --count --by)
  (типово)                таблиця
  --ids                   адреси по одній на рядок — вхід для status
  --json                  повні записи
  --count                 лише число
  --by <поле>             згрупувати й порахувати: book kind status type group level
  --limit N               перші N рядків; з --count і --by не поєднується

ПОВТОР
  перелічний прапорець повторюється в об'єднання:
    --status done --status recheck    ⇒ done АБО recheck
  --slug --title --level мають одне значення, тож повтор — помилка

АДРЕСА
  embedded/cherha-oflainu:detailed     версія
  embedded/cherha-oflainu:proj-queue   вставка
  вказівник (--ref) адреси НЕ має: статусу в нього немає, писати нічого
`;

const BY_FIELDS = ["book", "kind", "status", "type", "group", "level"];

/* ── вивід ─────────────────────────────────────────────────────────────────── */

/* Ріжемо по кодових точках, як і міряємо: у назвах трапляються емодзі, і зріз по
   кодових одиницях UTF-16 розвалив би сурогатну пару на два калічні символи. */
const shorten = (s, n) => {
  const cp = [...s];
  return cp.length <= n ? s : cp.slice(0, n - 1).join("") + "…";
};

function table(units) {
  if (!units.length) return "нічого не знайшлося";
  const rows = units.map((u) => [
    U.addrOf(u) ?? `→ ${u.ref}`,                    // вказівник адреси не має — показуємо ціль
    u.status || (u.ref ? "ref" : ""),
    u.level == null ? "" : String(u.level),
    u.recode ? "recode" : "",
    shorten(u.title || "", 44),
  ]);
  const head = ["адреса", "статус", "рів", "", "назва"];
  const w = head.map((h, i) => Math.max(h.length, ...rows.map((r) => [...r[i]].length)));
  const line = (r) => r.map((c, i) => c + " ".repeat(w[i] - [...c].length)).join("  ").trimEnd();
  return [line(head), w.map((n) => "─".repeat(n)).join("  "), ...rows.map(line)].join("\n");
}

function group(units, field) {
  const key = (u) => ({
    book: u.book, kind: u.kind, status: u.status || (u.ref ? "ref" : "—"),
    type: u.insert || u.part || "—", group: u.group,
    level: u.level == null ? "—" : String(u.level),
  })[field];
  const counts = new Map();
  for (const u of units) { const k = key(u) ?? "—"; counts.set(k, (counts.get(k) || 0) + 1); }
  const rows = [...counts].sort((a, b) => b[1] - a[1]);
  if (!rows.length) return "";
  const w = Math.max(...rows.map(([k]) => [...k].length));
  return rows.map(([k, n]) => k + " ".repeat(w - [...k].length) + "  " + String(n).padStart(5)).join("\n");
}

/**
 * Один файл вставки, зареєстрований у маніфесті під двома типами, дає дві одиниці з
 * ОДНАКОВОЮ адресою — і `status` за такою адресою вибирав би навмання. Форма адреси
 * лишається як обіцяно в README, а вада даних стає гучною: попереджаємо, не падаємо.
 */
function warnDupes(units) {
  const seen = new Set(), dupes = new Set();
  for (const u of units) {
    const a = U.addrOf(u);
    if (a === null) continue;
    if (seen.has(a)) dupes.add(a); else seen.add(a);
  }
  if (dupes.size)
    console.error(`find: увага — повторені адреси (${dupes.size}): ${[...dupes].join(", ")}`);
}

/* ── головне ───────────────────────────────────────────────────────────────── */

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h")) { console.log(HELP.trim()); return 0; }

  const { flags, rest } = U.parseArgs(argv);
  const out = { ids: false, json: false, count: false, by: null, limit: 0 };
  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--ids") out.ids = true;
    else if (a === "--json") out.json = true;
    else if (a === "--count") out.count = true;
    else if (a === "--by") { out.by = rest[++i]; if (!out.by) throw new Error("--by без поля"); }
    else if (a === "--limit") {
      const n = Number(rest[++i]);
      if (!Number.isInteger(n) || n <= 0) throw new Error("--limit хоче ціле додатне");
      out.limit = n;
    } else throw new Error(`невідомий прапорець: ${a}`);
  }

  /* Прихований пріоритет між --ids/--json/--count/--by мовчки викидав те, що просили,
     тож суперечка тепер падає, а не розв'язується за спиною. */
  const modes = [["--ids", out.ids], ["--json", out.json], ["--count", out.count], ["--by", !!out.by]]
    .filter(([, on]) => on).map(([name]) => name);
  if (modes.length > 1) throw new Error(`разом не можна: ${modes.join(" ")} — вивід один`);
  if (out.by && !BY_FIELDS.includes(out.by)) throw new Error(`--by ${out.by}: такого поля немає (${BY_FIELDS.join(" ")})`);
  if (out.limit && (out.count || out.by)) throw new Error("--limit із --count чи --by не працює — вони рахують усе");

  U.validate(flags);
  let units = U.filter(U.enumerate({ kinds: flags.kinds, books: flags.books }), flags);

  const key = (u) => u.slug ?? u.ref ?? "";            // вказівник слуга не має, сортуємо за ціллю
  units.sort((a, b) =>
    a.book.localeCompare(b.book) || key(a).localeCompare(key(b)) ||
    String(a.part).localeCompare(String(b.part)));

  warnDupes(units);

  if (out.count) { console.log(units.length); return 0; }
  if (out.by) { const s = group(units, out.by); if (s) console.log(s); return 0; }

  const total = units.length;
  if (out.limit) units = units.slice(0, out.limit);

  if (out.json) console.log(JSON.stringify(units.map((u) => ({
    addr: U.addrOf(u), book: u.book, kind: u.kind, slug: u.slug, part: u.part,
    type: u.insert || u.part, group: u.group, chapter: u.chapter, title: u.title,
    status: u.status ?? null, level: u.level ?? null, recode: !!u.recode,
    ref: u.ref || null, file: U.fileOf(u),
  })), null, 1));
  else if (out.ids) {
    let skipped = 0;
    for (const u of units) {
      const a = U.addrOf(u);
      if (a === null) { skipped++; continue; }          // вказівник не адресується — у трубу не йде
      console.log(a);
    }
    if (skipped) console.error(`find: ${skipped} вказівників пропущено — вони не адресуються`);
  } else {
    console.log(table(units));
    console.log(units.length === total ? `\n${total}` : `\n${units.length} з ${total}`);
  }
  return 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("find: " + e.message); process.exit(2); }
}
module.exports = { main };
