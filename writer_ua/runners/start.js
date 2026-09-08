#!/usr/bin/env node
/* ============================================================================
   start.js — ЗАПУСК БАТЧУ. Точка входу для людини.

   Зчіплює три речі й більше нічого не робить:

     orchestrator.js  черга, ліміт активних, стан, маніфест
     algorithm.js     десять етапів над однією одиницею
     ask-адаптер      чим саме кличемо агента

   ⛔ АДАПТЕР — ЄДИНЕ МІСЦЕ, ДЕ КОНВЕЄР ТОРКАЄТЬСЯ АГЕНТА. Ні оркестратор, ні алгоритм
   не знають, хто відповідає: Claude, Antigravity чи підробка на випробуванні. Тому
   весь конвеєр ганяється насухо за нуль токенів — і саме так у ньому знайшли те, що
   інакше коштувало б справжніх прогонів.

   Ужиток:
     node writer_ua/runners/start.js --book sf-apps --topic primitive-obsession
     node writer_ua/runners/start.js --book … --topic … --dry      показати завдання
     node writer_ua/runners/start.js --id <хеш>                     підняти обірваний
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const O = require("./orchestrator.js");
const { algorithm, finishBatch } = require("./algorithm.js");
const LOC = require("./local.js");
const P = require("./prompt.js");

/* ── адаптери ──────────────────────────────────────────────────────────────── */

/**
 * `--dry`: завдання складаються по-справжньому й лягають у теку батчу, але жодного
 * агента не викликано. Дає подивитися очима на те, що пішло б, і виміряти вагу блоків.
 */
function dryAsk(dir) {
  let n = 0;
  return async (prompt, label) => {
    const f = path.join(dir, `${String(++n).padStart(2, "0")}-${label.replace(/[^\p{L}\p{N}._-]+/gu, "-")}.txt`);
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(f, prompt, "utf8");
    /* Сухий прогін не може вигадати відповідь — і не вигадує: він спиняє одиницю
       одразу після першого завдання, лишивши його на диску. */
    throw Object.assign(new Error(`сухий прогін: завдання «${label}» складено й записано`), { dry: true });
  };
}

/**
 * Реальний адаптер підставляється ззовні: `--ask <модуль>`. Модуль дає або фабрику
 * `make(dir)` → ask, або готову `ask(prompt, label)`. Фабрика краща: тека в кожної
 * одиниці своя, а в пулі їх кілька воднораз.
 */
function loadAsk(spec) {
  if (!spec) return null;
  const m = require(path.resolve(spec));
  if (typeof m.make === "function") return m.make;
  const fn = typeof m === "function" ? m : m.ask;
  if (typeof fn !== "function") throw new Error(`${spec}: немає ні make(dir), ні ask(prompt, label)`);
  return () => fn;
}

/* ── розбір аргументів ─────────────────────────────────────────────────────── */

function args(argv) {
  const o = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) throw new Error(`не розумію: ${a}`);
    const k = a.slice(2);
    if (k === "dry") { o.dry = true; continue; }
    const v = argv[i + 1];
    if (v === undefined || v.startsWith("--")) throw new Error(`${a} без значення`);
    o[k] = v; i++;
  }
  return o;
}

/* ── прогін ────────────────────────────────────────────────────────────────── */

async function main(argv) {
  const o = args(argv);
  if (!o.id && (!o.book || (!o.topic && !o.topics)))
    throw new Error("потрібно --book <книга> --topic <тема>, або --id <хеш> для підняття");

  const rawTopics = o.topics ? o.topics.split(",") : (o.topic ? o.topic.split(",") : []);
  const topicList = rawTopics.map((s) => s.trim()).filter(Boolean);
  const units = o.book && topicList.length
    ? topicList.map((t) => LOC.unitOf(o.book, t, o.type || "article"))
    : [];
  const ask = loadAsk(o.ask);

  const say = (e) => {
    if (e.ev === "stage") console.log(`   · ${e.unit} → ${e.stage}`);
    else if (e.ev === "start") console.log(`▶ ${e.unit}  (активних ${e.active}, у черзі ${e.pending})`);
    else if (e.ev === "done") console.log(`✔ ${e.unit}`);
    else if (e.ev === "fail") console.log(`✖ ${e.unit}: ${e.message}`);
    else if (e.ev === "enqueue") console.log(`   + ${e.n} одиниць у чергу від ${e.unit}`);
    else if (e.ev === "refused") console.log(`   ⚠ стеля: відмовлено ${e.n}`);
    else if (e.ev === "wall") console.log(`⛔ стіна ліміту, у черзі лишилось ${e.pending}`);
    else if (e.ev === "restore") console.log(`↺ відновлено з теки: ${e.n}`);
    else if (e.ev === "pause") console.log(`⏸ ${e.unit} чекає на: ${e.for.join(", ")}`);
    else if (e.ev === "resume") console.log(`▶ ${e.unit} знову в черзі — те, чого чекала, готове`);
    else if (e.ev === "paused-left") console.log(`⏸ лишилось на паузі: ${e.n} — те, чого вони чекали, не завершилось`);
  };

  const report = await O.run({
    id: o.id, units,
    active: Number(o.active) || 4,
    stagger: o.stagger === undefined ? 2000 : Number(o.stagger),
    /* Стеля НОВИХ одиниць прогону: тема з фігурами на кожен розділ дає їх до 35, тож
       для пулу з десятка тем типових 200 замало — `--max 600`. Відмовлене видно в notes. */
    maxUnits: o.max === undefined ? undefined : Number(o.max),
    callTimeout: o.wait === undefined ? undefined : Number(o.wait),
    onEvent: say,
    algorithm: (unit, ctx) => {
      const dir = path.join(ctx.run.dir, unit.id.replace(/[^\w.-]+/g, "_"));
      return algorithm(unit, ctx, {
        ask: ask ? ask(dir) : dryAsk(dir),
        /* Написане конвеєром — готова робота: done, не recheck (автор, 08.09). */
        status: o.status || "done",
      });
    },
    /* Кінець батчу: кожна нова тема проти написаних вставок — запити в теці `_batch`. */
    finish: (done, { dir }) => {
      const d = path.join(dir, "_batch");
      return finishBatch(done, { ask: ask ? ask(d) : dryAsk(d) });
    },
  });

  console.log(`\nбатч ${report.id}`);
  console.log(`  теку прогону лишено: ${report.logs}`);
  console.log(`  зроблено ${report.done} · провалено ${report.failed} · пропущено ${report.skipped}`);
  if (report.notes.length) report.notes.forEach((n) => console.log(`  · ${n}`));
  if (report.checks && report.checks.length) {
    console.log(`\n  локальні перевірки — ${report.checks.length} одиниць із зауваженнями:`);
    for (const c of report.checks) {
      console.log(`  ▸ ${c.unit}`);
      c.rows.forEach((r) => console.log(`      ${r}`));
    }
  }
  console.log(`  маніфест: ${report.manifest}`);
  return report.failed || report.aborted ? 1 : 0;
}

if (require.main === module) {
  main(process.argv.slice(2))
    .then((c) => process.exit(c))
    .catch((e) => { console.error("start: " + e.message); process.exit(2); });
}
module.exports = { main, dryAsk };
