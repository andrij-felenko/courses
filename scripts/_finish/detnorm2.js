// electronics: 41% empty — норма нерівна по галузях. Яка вона САМЕ в галузях наших 13 тем?
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';
const OURS = { 'power-electronics': ['hot-swap','power-oring','soa-power-devices','sic-mosfet-power','psrr','ldo-stability','linear-regulator-types','quick-charge','apple-charging-protocol','high-side-level-shift'], analog: ['transistor-switch','pwm'], digital: ['gpio'] };

const w = { __BOOKS__: [] };
new Function('window', fs.readFileSync(path.join(REPO, 'book', 'electronics', 'manifest.js'), 'utf8'))(w);

for (const s of w.__BOOKS__[0].sections || []) {
  const done = (s.topics || []).filter(t => t.basic && t.basic.status === 'done');
  if (!done.length) continue;
  const cnt = {};
  for (const t of done) { const d = t.detailed ? t.detailed.status : '???'; cnt[d] = (cnt[d] || 0) + 1; }
  const pend = cnt.pending || 0, emp = cnt.empty || 0, dn = cnt.done || 0;
  const mark = OURS[s.slug] ? ` ← НАША ГАЛУЗЬ (${OURS[s.slug].length} наших тем)` : '';
  const pct = done.length ? Math.round(((pend + dn) / done.length) * 100) : 0;
  console.log(`${s.slug.padEnd(20)} done:${String(done.length).padStart(4)}  pending ${String(pend).padStart(3)} · done ${String(dn).padStart(2)} · empty ${String(emp).padStart(3)}   → мають детальну: ${String(pct).padStart(3)}%${mark}`);
}
