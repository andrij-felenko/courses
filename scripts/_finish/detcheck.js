// Який зараз detailed-статус у 13 написаних тем кожної книги + скільки батч поставить у чергу.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';
const PAY = __dirname;   // payload-*.json / args-*.json лежать поруч, у scripts/_finish/

for (const book of ['algorithms', 'math', 'electronics']) {
  const w = { __BOOKS__: [] };
  new Function('window', fs.readFileSync(path.join(REPO, 'book', book, 'manifest.js'), 'utf8'))(w);
  const T = new Map();
  for (const s of w.__BOOKS__[0].sections || []) for (const t of s.topics || []) T.set(t.slug, t);

  const p = JSON.parse(fs.readFileSync(path.join(PAY, `payload-${book}.json`), 'utf8'));
  const a = JSON.parse(fs.readFileSync(path.join(PAY, `args-${book}.json`), 'utf8'));
  const queued = new Set((a.detailed || []).map(d => d.slug));

  const cnt = {};
  const lines = [];
  for (const u of p.units) {
    const t = T.get(u.slug);
    const st = t && t.detailed ? t.detailed.status : '???';
    cnt[st] = (cnt[st] || 0) + 1;
    lines.push(`    ${u.slug.padEnd(32)} detailed=${String(st).padEnd(8)} ${queued.has(u.slug) ? '← батч поставить pending' : ''}`);
  }
  console.log(`${book.toUpperCase()}  (у args.detailed: ${queued.size})  статуси: ${JSON.stringify(cnt)}`);
  lines.forEach(l => console.log(l));
  console.log();
}
