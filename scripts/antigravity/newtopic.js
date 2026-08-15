#!/usr/bin/env node
/* ============================================================================
   newtopic.js — покласти НОВУ ТЕМУ В ЧЕРГУ. Маніфесту НЕ чіпає й письма НЕ починає.

   Ужиток:
     node scripts/antigravity/newtopic.js --book unix-linux --kind reference \
          --section devices --slug nvme-namespaces --title "Простори імен NVMe" \
          --why "стаття про block-device-model посилається на це поняття" [--from <тека>]
     node scripts/antigravity/newtopic.js --book unix-linux --list

   ЧОМУ ТАК. Тему, яку помітили посеред письма, не можна ні заводити в маніфест
   одразу (маніфест правиться ОДИН раз, наприкінці батчу), ні кидатися писати
   негайно (батч тоді не закінчується ніколи, а черга росте швидше, ніж її
   розбирають). Тому вона лягає в чергу на диск і чекає кінця батчу.

   Дублі: скрипт питає manifest-patch.js у режимі --dry, і той сам каже, чи є
   в книзі близький слуг. Список дублів — не заборона, а привід зупинитись і
   вирішити: нова тема чи розділ у наявній.
   ========================================================================== */
"use strict";
const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");

const argv = process.argv.slice(2);
const val = (n) => { const i = argv.indexOf("--" + n); return i >= 0 ? argv[i + 1] : null; };
const has = (n) => argv.includes("--" + n);

const BOOK = val("book");
if (!BOOK) { console.error("Ужиток: node scripts/antigravity/newtopic.js --book <книга> --kind <вид> --section <секція> --slug <слуг> --title <назва> --why <навіщо>"); process.exit(3); }

const QDIR = path.join("scripts", "_finish");
const QFILE = path.join(QDIR, `_ag-newtopics-${BOOK}.json`);
const load = () => { try { return JSON.parse(fs.readFileSync(QFILE, "utf8")); } catch { return []; } };

if (has("list")) {
  const q = load();
  if (!q.length) { console.log(`черга нових тем для ${BOOK} порожня`); process.exit(0); }
  console.log(`\nчерга нових тем — ${BOOK} (${q.length}):`);
  q.forEach((t, i) => console.log(`  ${i + 1}. [${t.section}] ${t.slug} — ${t.title}\n     навіщо: ${t.why}${t.from ? "\n     звідки: " + t.from : ""}`));
  console.log(`\nу маніфест вони підуть наприкінці батчу: node scripts/antigravity/finish-batch.js --book ${BOOK} --kind <вид> --apply`);
  process.exit(0);
}

const KIND = val("kind") || "book";
const SECTION = val("section");
const SLUG = val("slug");
const TITLE = val("title");
const WHY = val("why");
const FROM = val("from") || "";
for (const [n, v] of [["kind", KIND], ["section", SECTION], ["slug", SLUG], ["title", TITLE], ["why", WHY]])
  if (!v) { console.error(`бракує --${n}`); process.exit(3); }
if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(SLUG)) { console.error(`слуг має бути kebab-case без номерів: ${SLUG}`); process.exit(3); }

const MF = path.join(KIND, BOOK, "manifest.js");
if (!fs.existsSync(MF)) { console.error(`нема маніфесту: ${MF}`); process.exit(3); }

/* уже є в маніфесті? */
const mfSrc = fs.readFileSync(MF, "utf8");
if (new RegExp(`slug\\s*:\\s*["']${SLUG}["']`).test(mfSrc)) {
  console.log(`тема «${SLUG}» уже є в маніфесті ${MF} — у чергу не кладемо`);
  process.exit(0);
}

/* уже в черзі? */
const q = load();
if (q.some((t) => t.slug === SLUG)) {
  console.log(`тема «${SLUG}» уже в черзі ${QFILE} — нічого не змінено`);
  process.exit(0);
}

/* що скаже manifest-patch про схожі слуги (нічого не пишемо: --dry) */
const op = JSON.stringify([{ op: "topic", section: SECTION, slug: SLUG, title: TITLE, basic: "empty", detailed: "pending" }]);
const tmp = path.join(QDIR, `_ag-dupecheck-${BOOK}.json`);
fs.mkdirSync(QDIR, { recursive: true });
fs.writeFileSync(tmp, op, "utf8");
let dryOut = "";
try { dryOut = execSync(`node scripts/manifest-patch.js "${MF}" --ops "${tmp}" --dry`).toString(); }
catch (e) { dryOut = ((e.stdout || "") + (e.stderr || "")).toString(); }
try { try { fs.unlinkSync(tmp); } catch {} } catch {}
const dupes = dryOut.split(/\r?\n/).filter((l) => /•/.test(l)).map((l) => l.trim());
if (/МОЖЛИВІ ДУБЛІ/.test(dryOut)) {
  console.log(`\n⚠ МОЖЛИВІ ДУБЛІ ПОНЯТТЯ — глянь, перш ніж заводити нову тему:`);
  dupes.forEach((d) => console.log(`   ${d}`));
  console.log(`   Якщо це те саме поняття — не заводь тему, а допиши наявну.`);
}

q.push({ section: SECTION, slug: SLUG, title: TITLE, why: WHY, from: FROM, kind: KIND, dupes, queuedAt: new Date().toISOString() });
fs.writeFileSync(QFILE, JSON.stringify(q, null, 2), "utf8");
console.log(`\n✓ у черзі: [${SECTION}] ${SLUG} — ${TITLE}`);
console.log(`  файл: ${QFILE}  (тем у черзі: ${q.length})`);
console.log(`  маніфест НЕ змінено, письмо НЕ запущено — так і має бути.`);
