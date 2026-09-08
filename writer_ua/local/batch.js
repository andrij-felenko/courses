#!/usr/bin/env node
/* ============================================================================
   batch.js — СТАН БАТЧУ ОДНИМ ПОГЛЯДОМ. Нуль токенів, нічого не пише.

   Відповідач конвеєра (людина чи агент) мусить бачити, де стоїть кожна одиниця й на
   які запити ще ніхто не відповів, — і не мусить для цього писати власних скриптів по
   теці `inwork/`. Це той самий погляд, що має оркестратор, лише без запуску.

   Ужиток:  node writer_ua/local/batch.js <хеш>            зведення по одиницях
            node writer_ua/local/batch.js <хеш> --pending  лише запити без відповіді
            node writer_ua/local/batch.js                  перелік батчів за часом
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const O = require("../runners/orchestrator.js");

const args = process.argv.slice(2);
const id = args.find((a) => !a.startsWith("--"));
const onlyPending = args.includes("--pending");

if (!id) {
  const dirs = fs.readdirSync(O.INWORK, { withFileTypes: true })
    .filter((d) => d.isDirectory() && /^[a-z0-9]{10}$/.test(d.name))
    .map((d) => ({ id: d.name, at: fs.statSync(path.join(O.INWORK, d.name)).mtimeMs }))
    .sort((a, b) => b.at - a.at);
  for (const d of dirs) {
    const st = O.readStates(path.join(O.INWORK, d.id));
    const books = [...new Set(st.map((s) => s.book).filter(Boolean))].join(", ");
    console.log(`${d.id}  ${new Date(d.at).toISOString().slice(0, 16).replace("T", " ")}  одиниць ${String(st.length).padStart(3)}  завершено ${String(st.filter((s) => s.done).length).padStart(3)}  з помилкою ${String(st.filter((s) => s.error).length).padStart(3)}  ${books}`);
  }
  process.exit(0);
}

const dir = path.join(O.INWORK, id);
if (!fs.existsSync(dir)) { console.error(`немає батчу ${id} у ${O.INWORK}`); process.exit(2); }

/* Запити без відповіді — по всіх теках одиниць і по `_batch/`. */
const pending = [];
(function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name);
    if (e.isDirectory()) walk(p);
    else if (e.name.endsWith(".ask.txt") && !fs.existsSync(p.replace(/\.ask\.txt$/, ".ans.txt")))
      pending.push(path.relative(O.INWORK, p).split(path.sep).join("/"));
  }
})(dir);

if (!onlyPending) {
  const states = O.readStates(dir).sort((a, b) => String(a.id).localeCompare(String(b.id)));
  const stageOf = (s) => { let last = "—"; for (const f of O.STAGES) if (s[f] !== null && s[f] !== undefined) last = f; return last; };
  for (const s of states) {
    const flag = s.done ? "✔" : s.error ? "✖" : "…";
    const err = s.error ? ` · ${String(s.error.message || s.error).slice(0, 90)}` : "";
    const sz = s.size ? ` · слів ${s.size.words}/${s.size.need}` : "";
    console.log(`${flag} ${String(s.id).padEnd(72)} ${String(s.type || "").padEnd(8)} ${stageOf(s).padEnd(9)} запитів ${String(s.calls || 0).padStart(3)}${sz}${err}`);
  }
  console.log(`\nодиниць ${states.length} · завершено ${states.filter((s) => s.done).length} · з помилкою ${states.filter((s) => s.error).length} · без відповіді запитів ${pending.length}`);
  /* Завершено батч чи ні — каже позначка, а не тиша в теці. */
  const mark = path.join(dir, "done.json");
  if (fs.existsSync(mark)) {
    let m = {}; try { m = JSON.parse(fs.readFileSync(mark, "utf8")); } catch { }
    console.log(`✅ БАТЧ ЗАВЕРШЕНО ${m.at ? m.at.slice(0, 16).replace("T", " ") : ""} — ${m.manifest || "маніфест записано"}`);
  } else console.log("⏳ батч не завершено: позначки done.json ще немає — запити ще будуть");
}
if (pending.length) {
  console.log(onlyPending ? "" : "\nчекають на відповідь:");
  for (const p of pending) console.log("  " + p);
} else if (onlyPending) console.log("запитів без відповіді немає");
