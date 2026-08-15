#!/usr/bin/env node
/* ============================================================================
   review-dryrun.js — прогнати воркфлоу ревізії НАСУХО: без агентів, без токенів.

   ЧОМУ. 2026-08-15 прогін на 140 тем упав за 21 мілісекунду: усі 140 агентів
   дістали `dir is not defined`. Причина — перейменований параметр, на який
   лишилось посилання всередині шаблонного рядка. `node --check` таке НЕ ловить:
   синтаксис бездоганний, помилка виникає лише коли рядок збирають. А збирають
   його вже в бою.

   Тут воркфлоу виконується по-справжньому, але agent/parallel/phase/log —
   заглушки. Промпти будуються, отже кожен ReferenceError у них вилазить одразу.

     node scripts/claude/review-dryrun.js [--show]      (--show друкує промпт)
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..", "..");
const SHOW = process.argv.includes("--show");
const SCRIPT = path.join(ROOT, "scripts", "claude", "review-batch.js");

const src = fs.readFileSync(SCRIPT, "utf8").replace(/^export const meta = /m, "const meta = ");

/* Вхід — форма, у якій воркфлоу справді запускають: і рядки, і {dir,files}. */
const ARGS = {
  book: "unix-linux", kind: "reference", effort: "medium", round2: false, apply: false,
  dirs: [
    { dir: "reference/unix-linux/devices/dm-crypt", files: ["dm-crypt-d.md", "api-crypt-target.md", "figs.py"] },
    "reference/unix-linux/devices/udev-rules",
  ],
};

const prompts = [];
const stub = {
  agent: async (prompt, opts) => {
    prompts.push({ label: (opts && opts.label) || "?", prompt });
    /* повертаємо правдоподібну відповідь, щоб дійти до кінця скрипта */
    if (opts && opts.schema && opts.schema.properties && opts.schema.properties.dirs)
      return { dirs: ARGS.dirs.map((d) => (typeof d === "string" ? d : d.dir)) };
    return { dir: "reference/unix-linux/devices/dm-crypt", ok: true, fixes: [], logic: ["проба"] };
  },
  parallel: async (thunks) => Promise.all(thunks.map((t) => t())),
  pipeline: async (items, ...stages) => items,
  phase: () => { },
  log: () => { },
  budget: { total: null, spent: () => 0, remaining: () => Infinity },
};

(async () => {
  let out;
  try {
    const fn = new Function("args", "agent", "parallel", "pipeline", "phase", "log", "budget",
      `return (async () => {\n${src}\n})()`);
    out = await fn(ARGS, stub.agent, stub.parallel, stub.pipeline, stub.phase, stub.log, stub.budget);
  } catch (e) {
    console.error("✖ ВОРКФЛОУ ВПАВ БИ В БОЮ: " + e.message);
    if (e.stack) console.error(String(e.stack).split("\n").slice(1, 4).join("\n"));
    process.exit(1);
  }

  const editor = prompts.find((p) => /^рев:/.test(p.label));
  if (!editor) { console.error("✖ жодного промпта редактора не зібрано — черга не дійшла до Ревізії"); process.exit(1); }

  /* Що мусить бути в промпті, інакше редактор працюватиме не за правилами */
  const must = [
    ["тека теми", /Твоя тека — і ТІЛЬКИ вона: E:/],
    ["список файлів", /Файли в ній/],
    ["заборона Edit", /Edit і Write тобі ЗАБОРОНЕН/],
    ["формат замін", /old — ДОСЛІВНА цитата/],
    ["--also у newtopic", /--also </],
    ["бюджет кроків", /Бюджет на тему/],
  ];
  const missing = must.filter(([, re]) => !re.test(editor.prompt)).map(([n]) => n);
  const stale = [...editor.prompt.matchAll(/\$\{[^}]+\}/g)].map((m) => m[0]);

  console.log(`промптів зібрано: ${prompts.length}   (редакторів: ${prompts.filter((p) => /^рев:/.test(p.label)).length})`);
  console.log(`промпт редактора: ${Math.round(editor.prompt.length / 4)} токенів, ${editor.prompt.split("\n").length} рядків`);
  console.log(`результат воркфлоу: ${JSON.stringify(Object.keys(out || {}))}`);
  if (stale.length) console.log(`⚠ нерозгорнуті підстановки: ${stale.join(", ")}`);
  if (missing.length) { console.log("✖ у промпті БРАКУЄ: " + missing.join(", ")); process.exit(1); }
  console.log("✓ промпт зібрано повністю, підстановки розгорнуті");
  if (SHOW) console.log("\n" + "─".repeat(70) + "\n" + editor.prompt);
})();
