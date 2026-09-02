#!/usr/bin/env node
/* ============================================================================
   status.js — ЗМІНА статусу, рівня і прапорця `recode`. Єдина команда, що пише.

   Мова відбору спільна з `find` (lib/units.js), тож обидві склеюються трубою:

     find --book embedded --status deeper --has-code --ids | status --set recheck
     status --addr embedded/cherha-oflainu:detailed --set done --apply

   ТРИ ЗАПОБІЖНИКИ, і всі три навмисні:

   1. ⛔ Типово це СУХИЙ прогін. Без `--apply` нічого не пишеться — лише показується,
      що змінилося б. Пошук ганяють недбало, а тут одруківка у фільтрі означала б
      мовчазний перепис сотень одиниць.
   2. Маніфест пишеться ЛИШЕ через `writer_ua/lib/manifest.js` — один модуль на весь
      конвеєр. Тут — жодного власного запису JSON.
   3. Спосіб відбору задає НАЯВНІСТЬ джерела адрес, а не кількість адрес у ньому.
      Порожня труба — це «адрес не надійшло», а не «адрес не давали»: інакше
      `find … --ids | status --book X --set recheck --apply` при нулі знахідок
      мовчки провалювався б на фільтр і переписував усю книгу.

   ⚠️ ЩО САМЕ СТАНЕТЬСЯ, СУДИТЬ ПИСАР МАНІФЕСТУ, А НЕ МИ. Тутешній `change()` вирішує лише,
   кого взяти в план і що ми маємо на увазі; наслідки показує звіт від
   `MF.applyOps(dry:true)` — ті самі операції, що потім і запишуться. Доти вивід був
   власним переказом чужих правил і розходився з ними мовчки (класичний приклад —
   рівень: маніфест тримає його тільки при статусі `deeper`, на інших стирає, тому
   `--set-level` при іншому статусі попереджає).
   ========================================================================== */
"use strict";
const fs = require("fs");
const U = require("./lib/units.js");
const MF = require("../lib/manifest.js");

const HELP = `
status — зміна статусу, рівня і прапорця recode

  node writer_ua/local/status.js [що міняти] [кого] [--apply]

ЩО МІНЯТИ
  --set <статус>       done pending empty update deeper recheck
  --if <статус>        змінити, ЛИШЕ якщо зараз саме цей (інакше пропустити)
  --set-level N | none рівень 1–5; маніфест тримає його тільки при deeper
  --set-recode on|off  борг «код ще не переписаний як проєкт»

Прапорці запису названо --set-* навмисно: --level і --recode — це ФІЛЬТРИ спільної
мови відбору, і однакове ім'я для «відібрати за» й «записати» рано чи пізно
перепише не те. Приклад: --level 3 --set-level 4

КОГО
  --addr a,b,c         адреси через кому
  (труба)              адреси по одній на рядок — вихід find --ids
                       порожня труба = «адрес не надійшло», а НЕ «візьми фільтри»
  фільтри find         --book --kind --group --chapter --type --status
                       --not-status --slug --title --level --recode/--no-recode
                       --own/--ref --has-file/--no-file --has-code/--no-code

ЗАПИС
  (типово)             сухий прогін: показує, що змінилося б
  --apply              записати
  --quiet              без подетального переліку змін (пропущене показується завжди)

Хоч одне з --set/--set-level/--set-recode обов'язкове: команда, яка нічого не міняє,
це find, і він уже є.
`;

/* ── вхід ──────────────────────────────────────────────────────────────────── */


/* ── план ──────────────────────────────────────────────────────────────────── */

/**
 * Що ми МАЄМО НА УВАЗІ для цієї одиниці. `null` — нічого, така в план не йде.
 * Це намір і тільки намір: присуд виносить писар маніфесту нижче.
 */
function change(u, want) {
  const to = want.set ?? u.status;
  const curLevel = u.level ?? null;
  const curRecode = !!u.recode;
  const nextLevel = want.level === undefined ? curLevel : want.level;
  const nextRecode = want.recode === undefined ? curRecode : want.recode;

  /* Рівень маніфест тримає лише при deeper — інакше він однаково зникне,
     і показувати його як зміну означало б обіцяти те, чого не станеться. */
  const levelKept = to === "deeper" ? nextLevel : null;

  if (u.status === to && curLevel === levelKept && curRecode === nextRecode) return null;
  return { from: u.status, to, level: levelKept, recode: nextRecode };
}

/** Одна операція писаря маніфесту на одиницю: версія — `status`, вставка — `insert`. */
function opOf(u, ch, ifStatus) {
  const common = { level: ch.level, recode: ch.recode };
  if (u.insert) return { op: "insert", slug: u.slug, type: u.insert, file: u.file, status: ch.to, ...common };
  if (ifStatus) return { op: "status-if", slug: u.slug, ver: u.part, from: ifStatus, to: ch.to, ...common };
  return { op: "status", slug: u.slug, ver: u.part, status: ch.to, ...common };
}

/* ── вивід ─────────────────────────────────────────────────────────────────── */

function show(plan) {
  const rows = plan.map(({ u, ch }) => [
    U.addrOf(u),
    `${ch.from} → ${ch.to}`,
    ch.level == null ? "" : `рів ${ch.level}`,
    ch.recode !== !!u.recode ? (ch.recode ? "+recode" : "−recode") : "",
  ]);
  const w = [0, 1, 2, 3].map((i) => Math.max(...rows.map((r) => [...r[i]].length)));
  return rows.map((r) => r.map((c, i) => c + " ".repeat(w[i] - [...c].length)).join("  ").trimEnd()).join("\n");
}

/**
 * Порожній план буває з різних причин, і «усі вже такі» — лише одна з них.
 * Одне повідомлення на всі випадки казало людині неправду про її ж відбір.
 */
function whyEmpty(units, refs, byIf, ifStatus, want, ambiguous) {
  if (!units.length && refs.length) return `нічого міняти — усі відібрані (${refs.length}) є вказівниками: статусу вони не мають`;
  if (!units.length && ambiguous) return `нічого міняти — усі адреси (${ambiguous}) неоднозначні, вище видно які`;
  if (!units.length) return "нічого міняти — за цим відбором нічого не відібралося";
  if (ifStatus && byIf === units.length) return `нічого міняти — статусу «${ifStatus}» немає в жодної з відібраних (${units.length})`;
  if (want.level != null && !units.some((u) => (want.set ?? u.status) === "deeper"))
    return "нічого міняти — рівень маніфест тримає лише при deeper, а серед відібраних такого статусу немає";
  return "нічого міняти — усі відібрані вже такі";
}

/* ── головне ───────────────────────────────────────────────────────────────── */

function main(argv) {
  if (argv.includes("--help") || argv.includes("-h")) { console.log(HELP.trim()); return 0; }

  const { flags, rest } = U.parseArgs(argv);
  const want = {}; let ifStatus = null, addrs = null, apply = false, quiet = false;

  const need = (i) => {
    const v = rest[i + 1];
    if (v === undefined || v.startsWith("--")) throw new Error(`${rest[i]} без значення`);
    return v;
  };
  const once = (k) => { if (want[k] !== undefined) throw new Error(`--${k} двічі`); };

  for (let i = 0; i < rest.length; i++) {
    const a = rest[i];
    if (a === "--set") { once("set"); want.set = need(i); i++; }
    else if (a === "--if") { if (ifStatus) throw new Error("--if двічі"); ifStatus = need(i); i++; }
    else if (a === "--set-level") {
      once("level"); const v = need(i); i++;
      if (v === "none") want.level = null;
      else {
        const n = Number(v);
        if (!Number.isInteger(n) || n < 1 || n > 5) throw new Error("--set-level хоче 1–5 або none");
        want.level = n;
      }
    } else if (a === "--set-recode") {
      once("recode"); const v = need(i); i++;
      if (v !== "on" && v !== "off") throw new Error("--set-recode хоче on або off");
      want.recode = v === "on";
    } else if (a === "--addr") {
      if (addrs) throw new Error("--addr двічі");
      addrs = String(need(i)).split(",").map((s) => s.trim()).filter(Boolean); i++;
      /* Порожній `--addr ""` — це одруківка, а не «усі»: мовчки прийняти його
         означало б піти далі з нулем адрес під виглядом заданого відбору. */
      if (!addrs.length) throw new Error("--addr порожній — жодної адреси в ньому немає");
    } else if (a === "--apply") apply = true;
    else if (a === "--quiet") quiet = true;
    else throw new Error(`невідомий прапорець: ${a}`);
  }

  if (want.set === undefined && want.level === undefined && want.recode === undefined)
    throw new Error("нічого міняти — потрібне хоч одне з --set / --set-level / --set-recode");
  if (want.set !== undefined && !U.STATUSES.includes(want.set))
    throw new Error(`невідомий статус: ${want.set}`);
  if (ifStatus && !U.STATUSES.includes(ifStatus))
    throw new Error(`невідомий статус: ${ifStatus}`);

  /* ── кого ── */
  const pipe = U.stdinAddrs();
  const hasFilters = Object.keys(flags).length > 0;
  /* Джерело адрес одне: труба, у яку хтось уже налив, замість `--addr` не «уточнює
     відбір», а мовчки скасовує його — тож це суперечка, а не пріоритет. */
  if (addrs && pipe.addrs.length) throw new Error("адреси й труба разом — вибери щось одне");
  const addrMode = !!addrs || pipe.given;
  const byAddr = addrs || pipe.addrs;

  /* Джерело адрес є, адрес у ньому нуль — міняти нема чого, і крапка. Фільтри тут
     не рятівна запаска: саме на них порожня труба й провалювалася. */
  if (addrMode && !byAddr.length) { console.log("адрес не надійшло — міняти нічого"); return 0; }

  let units, missing = [], ambiguous = [];
  if (addrMode) {
    if (hasFilters) throw new Error("адреси й фільтри разом — вибери щось одне");
    ({ units, missing, ambiguous } = U.byAddrs(byAddr));
  } else if (hasFilters) {
    U.validate(flags);
    units = U.filter(U.enumerate({ kinds: flags.kinds, books: flags.books }), flags);
  } else throw new Error("кого міняти — дай --addr, трубу з find --ids або фільтри");

  /* Вада ДАНИХ на одній адресі не привід кинути решту труби — показуємо й ідемо далі. */
  if (ambiguous.length)
    console.error(`status: неоднозначних адрес пропущено (${ambiguous.length}): `
      + ambiguous.slice(0, 5).map((a) => `${a.addr} (${a.types.join(", ")})`).join("; ")
      + (ambiguous.length > 5 ? " …" : ""));

  if (missing.length) {
    console.error(`status: не знайшлося (${missing.length}): ${missing.slice(0, 5).join(", ")}${missing.length > 5 ? " …" : ""}`);
    return 2;
  }
  const refs = units.filter((u) => u.slug == null);
  if (refs.length) console.error(`status: ${refs.length} вказівників пропущено — статусу вони не мають`);
  units = units.filter((u) => u.slug != null);

  /* ── намір ── */
  const plan = []; let byIf = 0;
  for (const u of units) {
    if (ifStatus && u.status !== ifStatus) { byIf++; continue; }
    const ch = change(u, want);
    if (ch) plan.push({ u, ch });
  }

  /* Попередження висить на РІВНІ, а не на `--set`: `--set-level 3` без `--set` теж
     мовчки випаровувався, бо статус одиниці лишався не-deeper. */
  if (want.level != null) {
    if (want.set !== undefined && want.set !== "deeper")
      console.error(`status: увага — рівень маніфест тримає лише при deeper, при «${want.set}» він не збережеться`);
    else if (want.set === undefined) {
      const n = units.filter((u) => u.status !== "deeper").length;
      if (n) console.error(`status: увага — рівень маніфест тримає лише при deeper: у ${n} ${n === 1 ? "одиниці" : "одиницях"} з відібраних статус інший, там він не збережеться`);
    }
  }

  if (!plan.length) { console.log(whyEmpty(units, refs, byIf, ifStatus, want, ambiguous.length)); return 0; }

  /* ── операції, по книзі: маніфест один на книгу ── */
  const byBook = new Map();
  for (const { u, ch } of plan) {
    if (!byBook.has(u.book)) byBook.set(u.book, { dir: u.bookDir, ops: [] });
    byBook.get(u.book).ops.push(opOf(u, ch, ifStatus));
  }
  const run = (dry) => {
    const acc = { changed: 0, skipped: [], errors: [] };
    for (const [book, { dir, ops }] of byBook) {
      const rep = MF.applyOps(dir, ops, { dry });
      acc.changed += rep.changed;
      rep.skipped.forEach((s) => acc.skipped.push(`${book}: ${s}`));
      rep.errors.forEach((e) => acc.errors.push(`${book}: ${e}`));
    }
    return acc;
  };

  /* Ті самі операції спершу насухо — щоб показане було звітом писаря маніфесту, а не нашим
     переказом його правил. Запис іде другим прогоном і звітує вже за себе. */
  const dry = run(true);
  if (!quiet) console.log(show(plan));
  const rep = apply ? run(false) : dry;

  /* Непорожній `skipped` — це РОЗХОДЖЕННЯ наміру зі звітом писаря маніфесту, тобто
     найцінніше у виводі. Тому з переліком причин і тому попри `--quiet`. */
  if (rep.skipped.length) {
    console.log(`\nпропущено (нічого не змінює): ${rep.skipped.length}`);
    rep.skipped.slice(0, 12).forEach((s) => console.log(`   · ${s}`));
    if (rep.skipped.length > 12) console.log(`   … і ще ${rep.skipped.length - 12}`);
  }

  console.log(apply
    ? `\nзаписано: ${rep.changed} ${byBook.size === 1 ? "у 1 книзі" : `у ${byBook.size} книгах`}`
    : `\nсухий прогін: ${rep.changed} — щоб записати, додай --apply`);

  if (rep.errors.length) { rep.errors.forEach((e) => console.error("status: " + e)); return 1; }
  return 0;
}

if (require.main === module) {
  try { process.exit(main(process.argv.slice(2))); }
  catch (e) { console.error("status: " + e.message); process.exit(2); }
}
module.exports = { main };
