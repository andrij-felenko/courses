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
const { algorithm } = require("./algorithm.js");
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

/** Реальний адаптер підставляється ззовні: `--ask <модуль>` з функцією (prompt,label). */
function loadAsk(spec) {
  if (!spec) return null;
  const m = require(path.resolve(spec));
  const fn = typeof m === "function" ? m : m.ask;
  if (typeof fn !== "function") throw new Error(`${spec}: немає ask(prompt, label)`);
  return fn;
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
  if (!o.id && (!o.book || !o.topic))
    throw new Error("потрібно --book <книга> --topic <тема>, або --id <хеш> для підняття");

  const units = o.book && o.topic ? [LOC.unitOf(o.book, o.topic, o.type || "article")] : [];
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
  };

  const report = await O.run({
    id: o.id, units,
    active: Number(o.active) || 4,
    stagger: o.stagger === undefined ? 2000 : Number(o.stagger),
    onEvent: say,
    algorithm: (unit, ctx) => algorithm(unit, ctx, {
      ask: ask || dryAsk(path.join(ctx.run.dir, unit.id.replace(/[^\w.-]+/g, "_"))),
      status: o.status || "recheck",
    }),
  });

  console.log(`\nбатч ${report.id}`);
  console.log(`  теку прогону лишено: ${report.logs}`);
  console.log(`  зроблено ${report.done} · провалено ${report.failed} · пропущено ${report.skipped}`);
  if (report.notes.length) report.notes.forEach((n) => console.log(`  · ${n}`));
  console.log(`  маніфест: ${report.manifest}`);
  return report.failed || report.aborted ? 1 : 0;
}

if (require.main === module) {
  main(process.argv.slice(2))
    .then((c) => process.exit(c))
    .catch((e) => { console.error("start: " + e.message); process.exit(2); });
}
module.exports = { main, dryAsk };
