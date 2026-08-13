#!/usr/bin/env node
/* ============================================================================
   gate.js — ОДИН вимикач конвеєра: тема готова чи ні.

   Ужиток:
     node scripts/checks/gate.js <тека теми> [--quiet]
     node scripts/checks/gate.js --batch scripts/_finish/_batch-<книга>.json
     node scripts/checks/gate.js --topics <тека> <тека> …
     …  [--cache]    пропускати теми, що не змінилися з минулого зеленого прогону
     …  [--status]   лише сказати, хто зелений, за журналом — НЕ запускаючи перевірок

   Коди виходу:
     0 — ГОТОВО: усі 17 перевірок дали 0. Тільки в цьому стані тему можна
         вважати написаною (і аж потім, наприкінці батчу, вписати в маніфест).
     1 — Є РОБОТА: перелічено, які перевірки й що саме просять.
     4 — ЗАСТІЙ: коло минуло, а ні файли теми, ні вироки не змінились. Означає,
         що агенти крутяться намарне — оркестратор мусить втрутитись, а не
         запускати те саме тринадцятий раз.
     3 — ужиток.

   ЧОМУ ЦЕ СКІНЧЕННО. Кожне коло або міняє текст теми, або додає вирок — і те,
   й те міняє підпис кола. Однаковий підпис двічі поспіль означає, що коло
   нічого не зробило: далі крутити немає сенсу, це вже не робота, а зациклення.

   КОЛО ДОПИСУЄТЬСЯ, ЛИШЕ КОЛИ ПІДПИС ЗМІНИВСЯ. Інакше лічильник кіл рахував би
   не роботу, а запуски: `finish-batch` ганяє гейт по всьому батчу, і кожна його
   ходка додавала +1 колу КОЖНІЙ темі. Так тема доїжджала до стелі у 12 кіл,
   жодного разу не бувши виправленою. Застій це не ламає: однаковий підпис і далі
   означає застій, просто більше не роздуває лічильник.

   --cache — ЧОМУ ЦЕ БЕЗПЕЧНО. Чотирнадцять перевірок читають ЛИШЕ теку теми й
   вироки по ній. Не змінився вміст теки і не додалося вироків — їхній результат
   змінитися не може, бо входи ті самі, а скрипти детерміновані. Тому при збігу
   ключа (вміст теки + кількість вироків) вони пропускаються, а три перевірки, що
   залежать від стану ПОЗА текою (03 — цілі картинок, 05 — цілі лінків і маніфести,
   16 — маніфест теми й черга нових тем), ганяються ЗАВЖДИ. У кеш лягає лише
   ЗЕЛЕНИЙ результат: тема, яка не пройшла, кешу не отримує ніколи.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");
const { execSync } = require("child_process");
const L = require("./_lib.js");

const argv = process.argv.slice(2);
const QUIET = argv.includes("--quiet");
const CACHE = argv.includes("--cache");
const STATUS = argv.includes("--status");   // лише читання журналу, нічого не запускаємо
/* Стеля кіл. Кожне коло — це новий спавн суддів і ремонтника, тобто повна фіксована ціна
   ще раз. Дві теми з трьох закриваються за одне-два кола; тема, якій треба більше, майже
   завжди чекає рішення людини, а не ще одного заходу тих самих агентів. Тому за замовчуванням
   стеля 2, а не 12: дешевше показати людині, ніж крутити коло вчетверте. */
const MAX_ROUNDS = Number(process.env.CHECKS_MAX_ROUNDS || 2);
const here = __dirname;
const CHECKS = fs.readdirSync(here).filter((f) => /^\d\d-.*\.js$/.test(f)).sort();
/* залежать від стану ПОЗА текою теми — кешу не підлягають ніколи */
const ALWAYS = new Set(["03-figures.js", "05-links.js", "16-promises.js"]);

function topics() {
  const bi = argv.indexOf("--batch");
  if (bi >= 0) {
    const p = argv[bi + 1];
    const j = JSON.parse(fs.readFileSync(p, "utf8"));
    const list = Array.isArray(j) ? j : (j.topics || j.units || []);
    return list.map((x) => (typeof x === "string" ? x : x.dir)).filter(Boolean);
  }
  const ti = argv.indexOf("--topics");
  if (ti >= 0) return argv.slice(ti + 1).filter((a) => !a.startsWith("--"));
  const one = argv.find((a) => !a.startsWith("--"));
  return one ? [one] : [];
}

const RAW = topics();
const DIRS = RAW.map((d) => L.resolveDir(d) || d);   // шлях приймаємо і від cwd, і від кореня репо
if (!DIRS.length) {
  console.error("Ужиток: node scripts/checks/gate.js <тека теми> | --batch <файл.json> | --topics <тека>…");
  process.exit(L.USAGE);
}

/* ── замок на прогін по батчу ────────────────────────────────────────────────
   Повний прогін — це 17 перевірок × кількість тем, тобто сотні запусків node.
   Два таких одночасно не подвоюють швидкість, а ділять машину: заміряно на
   живому прогоні — п'ять паралельних прогонів, і одна тема замість ~30 секунд
   іде 55. Тому другий прогін не стартує, а каже, хто вже працює.               */
const LOCK = path.join(L.ROOT, "scripts", "_finish", "_gate.lock");
function alive(pid) { try { process.kill(pid, 0); return true; } catch { return false; } }
function takeLock() {
  try {
    const j = JSON.parse(fs.readFileSync(LOCK, "utf8"));
    if (alive(j.pid) && Date.now() - j.at < 3 * 3600e3) {
      console.error(`\n✖ прогін по батчу вже йде: pid ${j.pid}, тем ${j.topics}, стартував ${new Date(j.at).toLocaleTimeString()}`);
      console.error(`  Другий паралельно не пришвидшить — вони поділять машину. Дочекайся або зніми той процес.`);
      console.error(`  Якщо той процес мертвий: видали ${path.relative(L.ROOT, LOCK)}`);
      process.exit(1);
    }
  } catch { }
  fs.mkdirSync(path.dirname(LOCK), { recursive: true });
  fs.writeFileSync(LOCK, JSON.stringify({ pid: process.pid, at: Date.now(), topics: DIRS.length }), "utf8");
  const drop = () => { try { const j = JSON.parse(fs.readFileSync(LOCK, "utf8")); if (j.pid === process.pid) fs.unlinkSync(LOCK); } catch { } };
  process.on("exit", drop);
  process.on("SIGINT", () => { drop(); process.exit(130); });
}

/* ── --status: хто готовий, без жодного запуску ─────────────────────────────
   Питання «які теми вже зелені» відповідається з журналу вироків: там лежать
   підпис останнього кола й кеш зеленого прогону. Ганяти заради цього 17 перевірок
   на тему — це та сама тиснява, тільки написана циклом.                        */
if (STATUS) {
  let ready = 0;
  for (const dir of DIRS) {
    const vdir = path.join(L.ROOT, "scripts", "_finish", "_verdicts", L.topicKey(dir));
    let rounds = [], cache = null;
    try { rounds = JSON.parse(fs.readFileSync(path.join(vdir, "_rounds.json"), "utf8")); } catch { }
    try { cache = JSON.parse(fs.readFileSync(path.join(vdir, "_gate-cache.json"), "utf8")); } catch { }
    const last = rounds[rounds.length - 1] || "";
    const codes = (last.split("|")[1] || "");
    const green = /^0*$/.test(codes) && codes.length > 0;
    if (green) ready++;
    console.log(`  ${green ? "✓ зелена " : cache ? "· кеш є  " : "· у роботі"}  кіл ${String(rounds.length).padStart(2)}  ${codes ? "коди " + codes : "журналу нема"}   ${dir}`);
  }
  console.log(`\nзелених за журналом: ${ready} із ${DIRS.length}   (це ЧИТАННЯ журналу, перевірки не запускались)`);
  process.exit(ready === DIRS.length ? 0 : 1);
}
if (DIRS.length > 1 && !process.env.GATE_LOCK_INHERITED) takeLock();

function contentHash(dir) {
  const h = crypto.createHash("sha1");
  const walk = (d) => {
    for (const e of fs.readdirSync(d, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      if (e.name === "__pycache__") continue;
      const p = path.join(d, e.name);
      if (e.isDirectory()) walk(p);
      else if (/\.(md|svg|py)$/.test(e.name)) h.update(e.name + ":" + fs.readFileSync(p));
    }
  };
  walk(dir);
  return h.digest("hex").slice(0, 16);
}

function runCheck(file, dir) {
  try {
    const out = execSync(`node "${path.join(here, file)}" "${dir}"`, { maxBuffer: 32 * 1024 * 1024, timeout: 300000, killSignal: "SIGKILL" }).toString();
    return { code: 0, out };
  } catch (e) {
    return { code: e.status || 1, out: ((e.stdout || "") + (e.stderr || "")).toString() };
  }
}

/* ── кеш зеленої теми ──────────────────────────────────────────────────────── */
function vdirOf(dir) { return path.join(L.ROOT, "scripts", "_finish", "_verdicts", L.topicKey(dir)); }
function verdictCount(vdir) {
  let n = 0;
  if (fs.existsSync(vdir)) for (const f of fs.readdirSync(vdir)) if (/^\d\d\.json$/.test(f)) n += Object.keys(JSON.parse(fs.readFileSync(path.join(vdir, f), "utf8"))).length;
  return n;
}
const cacheFile = (vdir) => path.join(vdir, "_gate-cache.json");
function loadCache(vdir) { try { return JSON.parse(fs.readFileSync(cacheFile(vdir), "utf8")); } catch { return null; } }
function saveCache(vdir, key) {
  fs.mkdirSync(vdir, { recursive: true });
  fs.writeFileSync(cacheFile(vdir), JSON.stringify({ key, ready: true }, null, 2), "utf8");
}

const MARK = { 0: "✓ ПРОЙДЕНО", 1: "✖ ДЕФЕКТИ", 2: "◆ ПОТРІБЕН ВИРОК", 3: "! УЖИТОК" };
let anyWork = false, anyStall = false;
const summary = [];

for (const dir of DIRS) {
  if (!fs.existsSync(dir)) { console.error(`нема теки: ${dir}`); process.exit(L.USAGE); }
  console.log(`\n════════ ${dir} ════════`);

  const vdir = vdirOf(dir);
  const vcount = verdictCount(vdir);
  const ch = contentHash(dir);
  const ckey = ch + "|v" + vcount;
  const cached = CACHE && (loadCache(vdir) || {}).key === ckey;

  const res = (cached ? CHECKS.filter((f) => ALWAYS.has(f)) : CHECKS).map((f) => ({ f, ...runCheck(f, dir) }));
  if (cached) console.log(`  ⏭ кеш: ні теку, ні вироки не чіпали з минулого зеленого прогону — ${CHECKS.length - ALWAYS.size} перевірок пропущено, ${ALWAYS.size} прогнано`);

  res.forEach((r) => {
    const tail = r.out.split(/\r?\n/).filter((l) => l.trim()).slice(-1)[0] || "";
    console.log(`  ${MARK[r.code] || ("? " + r.code)}`.padEnd(22) + r.f.padEnd(18) + (r.code ? tail.slice(0, 90) : ""));
    if (!QUIET && r.code === 1) {
      r.out.split(/\r?\n/).filter((l) => /^\s{2}\d+\./.test(l)).slice(0, 6).forEach((l) => console.log("        " + l.trim().slice(0, 160)));
    }
  });

  const defects = res.filter((r) => r.code === 1);
  const judge = res.filter((r) => r.code === 2);
  const ready = !defects.length && !judge.length;

  /* підпис кола: вміст теми + коди ВСІХ перевірок + кількість вироків.
     Пропущені кешем зараховуємо нулями — вони й були нулями, інакше кешу не було б. */
  const codeOf = (f) => { const r = res.find((x) => x.f === f); return r ? r.code : 0; };
  const sig = ch + "|" + CHECKS.map(codeOf).join("") + "|v" + vcount;

  const roundsFile = path.join(vdir, "_rounds.json");
  let rounds = [];
  try { rounds = JSON.parse(fs.readFileSync(roundsFile, "utf8")); } catch { }
  /* Рахуємо кола ЦЬОГО тексту, а не всі за життя теми: правка міняє contentHash, отже
     після кожного ремонту лічильник починається спочатку. Два кола на НЕЗМІННОМУ тексті
     означають, що судді відпрацювали, а зрушення нема — далі рішення людини. */
  const roundsNow = rounds.filter((x) => x.startsWith(ch + "|")).length;
  const overRounds = !ready && roundsNow >= MAX_ROUNDS;
  const stalled = !ready && (overRounds || (rounds.length && rounds[rounds.length - 1] === sig));
  if (rounds[rounds.length - 1] !== sig) {          // коло — це ЗМІНА, а не запуск
    rounds.push(sig);
    fs.mkdirSync(vdir, { recursive: true });
    fs.writeFileSync(roundsFile, JSON.stringify(rounds.slice(-20), null, 2), "utf8");
  }
  if (ready && !cached) saveCache(vdir, ckey);

  console.log(`\n  коло ${rounds.length} (на цьому тексті ${roundsNow}/${MAX_ROUNDS}) · дефектів ${defects.length} · чекають вироку ${judge.length}` + (ready ? "  →  ГОТОВО" : ""));
  if (stalled) {
    anyStall = true;
    console.log(`  ⚠ СТОП: ${overRounds ? `кіл на незмінному тексті ${roundsNow} при стелі ${MAX_ROUNDS} — далі рішення людини` : "підпис кола не змінився: ні текст, ні вироки не зрушили"}`);
    console.log(`    Не запускай те саме знову: розберись, чому агент нічого не змінив, або познач тему на розсуд людини.`);
  }
  if (!ready) {
    anyWork = true;
    console.log(`  далі: ` + [...defects, ...judge].map((r) => `node scripts/checks/${r.f} "${dir}"`).join("  ·  "));
  }
  summary.push({ dir, ready, defects: defects.length, judge: judge.length, round: rounds.length, stalled });
}

if (DIRS.length > 1) {
  console.log(`\n════════ ПІДСУМОК БАТЧУ ════════`);
  summary.forEach((s) => console.log(`  ${s.ready ? "✓ готово " : "· у роботі"}  коло ${String(s.round).padStart(2)}  дефектів ${s.defects} · вироків чекає ${s.judge}${s.stalled ? "  ⚠ ЗАСТІЙ" : ""}   ${s.dir}`));
  const done = summary.filter((s) => s.ready).length;
  console.log(`\n  готових тем: ${done} із ${summary.length}`);
  if (done === summary.length) console.log(`  → усі теми пройшли всі 17 перевірок. Аж ТЕПЕР можна правити маніфест:\n    node scripts/antigravity/finish-batch.js --book <книга> --kind <вид> --apply`);
}

process.exit(anyStall ? 4 : anyWork ? 1 : 0);
