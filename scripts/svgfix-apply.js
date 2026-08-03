#!/usr/bin/env node
/**
 * svgfix-apply.js — ЛОКАЛЬНЕ застосування правок фігур, які повернули агенти.
 *
 * Агент не чіпає репо: він кладе виправлені функції у <out>/<i>.fix.py. Тут ми їх вклеюємо
 * у figs.py замість однойменних, перегенеровуємо SVG і МІРЯЄМО. Стало не краще — повний відкат.
 *
 *   node scripts/svgfix-apply.js [--out scripts/_svgfix]
 */
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const arg = (n, d) => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : d };
const OUT = path.join(ROOT, arg('out', 'scripts/_svgfix'));
const index = JSON.parse(fs.readFileSync(path.join(OUT, 'index.json'), 'utf8'));

function warnCount(d) {
  let out = '';
  try { out = execFileSync('python', [path.join(ROOT, 'scripts/svgcheck.py'), d], { cwd: ROOT, encoding: 'utf8' }) }
  catch (e) { out = (e.stdout || '') + (e.stderr || '') }
  const m = out.match(/із зауваженнями:\s*(\d+)/);
  return m ? Number(m[1]) : null;
}

/** Розбити текст на top-level def-блоки: {name → {start, end}} за рядками. */
function defRanges(src) {
  const lines = src.split(/\r?\n/);
  const starts = [];
  lines.forEach((l, i) => { if (/^def\s+\w+\s*\(/.test(l)) starts.push(i) });
  const map = new Map();
  starts.forEach((s, k) => {
    const name = (lines[s].match(/^def\s+(\w+)/) || [])[1];
    map.set(name, { start: s, end: k + 1 < starts.length ? starts[k + 1] : lines.length });
  });
  return { lines, map };
}

let applied = 0, better = 0, same = 0, worse = 0, noFix = 0, badSplice = 0, fixedWarns = 0;
const wins = [], losses = [];
for (const t of index) {
  const fixFile = path.join(OUT, String(t.i).padStart(3, '0') + '.fix.py');
  if (!fs.existsSync(fixFile)) { noFix++; continue }
  const figsPath = path.join(ROOT, t.dir, 'figs.py');
  const orig = fs.readFileSync(figsPath, 'utf8');
  const fixSrc = fs.readFileSync(fixFile, 'utf8').replace(/^```(?:python)?\s*$/gm, '');
  const { map: newMap, lines: newLines } = defRanges(fixSrc);
  if (!newMap.size) { badSplice++; continue }

  let cur = orig;
  let spliced = 0;
  for (const [name, r] of newMap) {
    const { lines, map } = defRanges(cur);
    const old = map.get(name);
    if (!old) continue;                                   // такої функції в оригіналі нема — пропускаємо
    const block = newLines.slice(r.start, r.end);
    while (block.length && !block[block.length - 1].trim()) block.pop();
    cur = lines.slice(0, old.start).concat(block, '', lines.slice(old.end)).join('\n');
    spliced++;
  }
  if (!spliced) { badSplice++; continue }

  const abs = path.join(ROOT, t.dir), imgDir = path.join(abs, 'img');
  const before = warnCount(t.dir);
  const backup = {};
  if (fs.existsSync(imgDir)) for (const f of fs.readdirSync(imgDir)) if (f.endsWith('.svg')) backup[f] = fs.readFileSync(path.join(imgDir, f));
  fs.writeFileSync(figsPath, cur, 'utf8');
  let ok = true;
  try { execFileSync('python', ['figs.py'], { cwd: abs, stdio: 'ignore', timeout: 90000 }) } catch (e) { ok = false }
  const after = ok ? warnCount(t.dir) : null;
  applied++;
  if (ok && after !== null && after < before) { better++; fixedWarns += before - after; wins.push(`${t.dir} (${before}→${after})`) }
  else {
    if (!ok || after === null) worse++; else if (after === before) same++; else { worse++ }
    losses.push(`${t.dir} (${before}→${ok && after !== null ? after : 'помилка'})`);
    fs.writeFileSync(figsPath, orig, 'utf8');
    for (const f of Object.keys(backup)) fs.writeFileSync(path.join(imgDir, f), backup[f]);
  }
}
console.log(`завдань в індексі: ${index.length} · відповідей від агентів: ${applied + badSplice} · без відповіді: ${noFix} · не вклеїлось: ${badSplice}`);
console.log(`ПОКРАЩАЛО: ${better} тек — мінус ${fixedWarns} зауважень · без зміни: ${same} · гірше/помилка (відкочено): ${worse}`);
if (wins.length) console.log('\n' + wins.slice(0, 20).map((s) => '  ✓ ' + s).join('\n'));
if (losses.length) console.log('\n' + losses.slice(0, 10).map((s) => '  ✗ ' + s).join('\n'));
