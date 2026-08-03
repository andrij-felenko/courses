#!/usr/bin/env node
/**
 * svgfix-prep.js — ЛОКАЛЬНА підготовка завдань на правку фігур.
 *
 * Ідея: на сервер (агентам) відправляти ЛИШЕ те, що потребує судження — сам код фігури
 * й перелік зауважень. Усе інше робимо тут: запуск svgcheck, розбір зауважень, пошук
 * потрібної функції у figs.py, вирізання її тексту.
 *
 * Було (агент сам усе з'ясовував): ~231 КБ транскрипта на теку — він читав figs.py цілком,
 * усі згенеровані SVG і навіть код самого svgcheck.
 *
 *   node scripts/svgfix-prep.js --dirs <json зі списком тек> [--out scripts/_svgfix]
 *
 * Кладе по файлу-завданню на теку: <out>/<i>.task.md і індекс <out>/index.json.
 */
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');

const ROOT = path.resolve(__dirname, '..');
const argv = process.argv.slice(2);
const arg = (n, d) => { const i = argv.indexOf('--' + n); return i >= 0 ? argv[i + 1] : d };
const OUT = path.join(ROOT, arg('out', 'scripts/_svgfix'));
const DIRS_FILE = arg('dirs');
if (!DIRS_FILE) { console.error('потрібен --dirs <json>'); process.exit(1) }

const dirs = JSON.parse(fs.readFileSync(path.resolve(ROOT, DIRS_FILE), 'utf8'))
  .map((x) => (typeof x === 'string' ? x : x.dir));

/** Зауваження по теці: {svgFile → [рядки зауважень]}. svgcheck виходить НЕнульовим кодом — це норма. */
function checkDir(d) {
  let out = '';
  try { out = execFileSync('python', [path.join(ROOT, 'scripts/svgcheck.py'), d], { cwd: ROOT, encoding: 'utf8' }) }
  catch (e) { out = (e.stdout || '') + (e.stderr || '') }
  const map = new Map();
  for (const l of out.split(/\r?\n/)) {
    const m = l.match(/^WARN\s+(?:.*[\\/])?img[\\/](\S+\.svg):\s*(.+)$/);
    if (!m) continue;
    if (!map.has(m[1])) map.set(m[1], []);
    map.get(m[1]).push(m[2].trim());
  }
  return map;
}

/** figs.py → [{name, start, end, src, svgs:[…]}] за межами top-level `def`. */
function functions(src) {
  const lines = src.split(/\r?\n/);
  const starts = [];
  lines.forEach((l, i) => { if (/^def\s+\w+\s*\(/.test(l)) starts.push(i) });
  return starts.map((s, k) => {
    const e = k + 1 < starts.length ? starts[k + 1] : lines.length;
    const body = lines.slice(s, e).join('\n');
    const svgs = [...body.matchAll(/["']([\w-]+\.svg)["']/g)].map((m) => m[1]);
    return { name: (lines[s].match(/^def\s+(\w+)/) || [])[1], start: s + 1, end: e, src: body, svgs };
  });
}

const KIT = `Доступні помічники svgkit (імпортовані в figs.py через *): text(x,y,s,size=,color=,anchor=,bold=,italic=),
multiline(...), fit_font(s,max_w,size,bold,min_size=9), textbox(x,y,w,h,s,...), fitbox(x,y,w,h,s,size=,pad=),
line(x1,y1,x2,y2,...), poly(...), rect(x,y,w,h,...), circle(cx,cy,r,...), arrow(...) через marker "arrow",
plus/minus(cx,cy,r), render(path, w, h, *frags, title=None). Кольори-константи: LINE, MUTED, BG, NEG тощо.`;

fs.mkdirSync(OUT, { recursive: true });
for (const f of fs.readdirSync(OUT)) fs.unlinkSync(path.join(OUT, f));

const index = [];
let skipped = 0, figsTotal = 0, bytes = 0;
dirs.forEach((d, i) => {
  const figsPath = path.join(ROOT, d, 'figs.py');
  if (!fs.existsSync(figsPath)) { skipped++; return }
  const warns = checkDir(d);
  if (!warns.size) { skipped++; return }
  const src = fs.readFileSync(figsPath, 'utf8');
  const fns = functions(src);
  const blocks = [];
  for (const [svg, issues] of warns) {
    const fn = fns.find((x) => x.svgs.includes(svg));
    if (!fn) continue;                                  // фігуру малює не top-level def — пропускаємо
    if (!blocks.some((b) => b.name === fn.name)) blocks.push({ ...fn, issues: [] });
    const b = blocks.find((x) => x.name === fn.name);
    b.issues.push(`${svg}: ${issues.join(' ; ')}`);
  }
  if (!blocks.length) { skipped++; return }
  figsTotal += blocks.length;

  const body = [
    `# Правка фігур: ${d}`, '',
    `Файл-джерело: \`${d}/figs.py\`. SVG у \`img/\` — ПОХІДНІ, їх не чіпай і НЕ читай.`, '',
    KIT, '',
    '## Що виправити', '',
    ...blocks.map((b) => [
      `### функція \`${b.name}\` (рядки ${b.start}–${b.end})`,
      'Зауваження гейта:',
      ...b.issues.map((s) => `- ${s}`),
      '', '```python', b.src, '```', '',
    ].join('\n')),
  ].join('\n');
  const file = path.join(OUT, `${String(i).padStart(3, '0')}.task.md`);
  fs.writeFileSync(file, body, 'utf8');
  bytes += body.length;
  index.push({ i, dir: d, figs: figsPath.replace(/\//g, '\\'), task: path.relative(ROOT, file).replace(/\//g, '\\'), fns: blocks.map((b) => b.name) });
});

fs.writeFileSync(path.join(OUT, 'index.json'), JSON.stringify(index, null, 1), 'utf8');
console.log(`завдань: ${index.length} (пропущено ${skipped}) · функцій до правки: ${figsTotal}`);
console.log(`сумарно тексту на сервер: ${Math.round(bytes / 1024)} КБ · у середньому ${Math.round(bytes / Math.max(1, index.length) / 1024 * 10) / 10} КБ на теку`);
console.log(`індекс: ${path.relative(ROOT, path.join(OUT, 'index.json'))}`);
