// В analog/digital норма неоднозначна (33/36%). Чи корелює detailed-статус із РОЗМІРОМ базової?
// Якщо так — розмір наших 3 тем (transistor-switch, pwm, gpio) підкаже відповідь.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';

function words(f) {
  if (!fs.existsSync(f)) return 0;
  let t = fs.readFileSync(f, 'utf8');
  t = t.replace(/```[\s\S]*?```/g, ' ').replace(/<[^>]+>/g, ' ').replace(/!\[[^\]]*\]\([^)]*\)/g, ' ').replace(/\[([^\]]*)\]\([^)]*\)/g, '$1');
  return (t.match(/[\p{L}\p{N}][\p{L}\p{N}'’-]*/gu) || []).length;
}
const med = (a) => { if (!a.length) return 0; const s = [...a].sort((x, y) => x - y); return s[s.length >> 1]; };

const w = { __BOOKS__: [] };
new Function('window', fs.readFileSync(path.join(REPO, 'book', 'electronics', 'manifest.js'), 'utf8'))(w);
const OURS = new Set(['transistor-switch', 'pwm', 'gpio']);

for (const sec of ['analog', 'digital']) {
  const s = (w.__BOOKS__[0].sections || []).find(x => x.slug === sec);
  const pend = [], emp = [], ours = [];
  for (const t of s.topics || []) {
    if (!t.basic || t.basic.status !== 'done') continue;
    const n = words(path.join(REPO, 'book', 'electronics', sec, t.slug, t.slug + '.md'));
    if (!n) continue;
    if (OURS.has(t.slug)) { ours.push([t.slug, n, t.detailed && t.detailed.status]); continue; }
    const d = t.detailed ? t.detailed.status : '';
    if (d === 'pending' || d === 'done') pend.push(n); else if (d === 'empty') emp.push(n);
  }
  console.log(`── ${sec} ──`);
  console.log(`   МАЮТЬ детальну (${pend.length}):  медіана ${med(pend)}w   [${Math.min(...pend)}–${Math.max(...pend)}]`);
  console.log(`   БЕЗ детальної (${emp.length}):   медіана ${med(emp)}w   [${Math.min(...emp)}–${Math.max(...emp)}]`);
  for (const [sl, n, d] of ours) {
    const above = n > med(emp) && n >= med(pend);
    console.log(`   ► НАША ${sl.padEnd(18)} ${String(n).padStart(4)}w  (зараз ${d})  ${above ? '→ у діапазоні тих, що МАЮТЬ детальну' : '→ радше як ті, що без'}`);
  }
  console.log();
}
