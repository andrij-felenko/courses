// Яка НОРМА detailed-статусу в кожній книзі? Щоб рішення по 24 темах спиралось на дані, а не на здогад.
// Рахуємо ЛИШЕ теми з basic.status === "done" (написані) — незаписані нічого не кажуть про норму.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';

for (const book of ['communications', 'algorithms', 'programming', 'math', 'electronics']) {
  const w = { __BOOKS__: [] };
  new Function('window', fs.readFileSync(path.join(REPO, 'book', book, 'manifest.js'), 'utf8'))(w);
  const cnt = {};
  let doneN = 0;
  for (const s of w.__BOOKS__[0].sections || []) {
    for (const t of s.topics || []) {
      if (!t.basic || t.basic.status !== 'done') continue;
      doneN++;
      const d = t.detailed ? t.detailed.status : '???';
      cnt[d] = (cnt[d] || 0) + 1;
    }
  }
  const pct = (k) => doneN ? ((cnt[k] || 0) / doneN * 100).toFixed(0) + '%' : '—';
  console.log(`${book.padEnd(15)} готових basic: ${String(doneN).padStart(4)}   detailed: ` +
    `done ${String(cnt.done || 0).padStart(3)} (${pct('done').padStart(4)})  ` +
    `pending ${String(cnt.pending || 0).padStart(3)} (${pct('pending').padStart(4)})  ` +
    `empty ${String(cnt.empty || 0).padStart(4)} (${pct('empty').padStart(4)})  ` +
    `інше ${doneN - (cnt.done || 0) - (cnt.pending || 0) - (cnt.empty || 0)}`);
}
