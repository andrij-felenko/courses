// 30 статей на диску зі статусом != done, а наші батчі — 26 (math 13 + electronics 13).
// Хто решта 4? Знайти поіменно зі статусом і розміром.
const fs = require('fs');
const path = require('path');
const REPO = 'E:\\develop\\courses';
const BOOKS = ['communications', 'algorithms', 'programming', 'math', 'electronics'];

const TOPIC = new Map();
for (const b of BOOKS) {
  const w = { __BOOKS__: [] };
  new Function('window', fs.readFileSync(path.join(REPO, 'book', b, 'manifest.js'), 'utf8'))(w);
  for (const s of w.__BOOKS__[0].sections || []) for (const t of s.topics || []) TOPIC.set(`${b}/${t.slug}`, { ...t, section: s.slug });
}
// наші 13 на книгу — зі скаутів ОРИГІНАЛЬНИХ журналів
const WF = 'C:\\Users\\andri\\.claude\\projects\\E--develop-courses\\6752e8fc-d288-48e2-9bc9-49d8a8c1c78a\\subagents\\workflows';
const RUNS = { communications: 'wf_733c29c7-cb1', algorithms: 'wf_2582bc1c-4b0', math: 'wf_a94e7a56-553', electronics: 'wf_562b6642-f12', programming: 'wf_8cb7a918-6b1' };
const OURS = new Set();
for (const [b, run] of Object.entries(RUNS)) {
  for (const l of fs.readFileSync(path.join(WF, run, 'journal.jsonl'), 'utf8').split(/\r?\n/).filter(Boolean)) {
    const e = JSON.parse(l);
    if (e.type === 'result' && e.result && e.result.units) { for (const u of e.result.units) OURS.add(`${b}/${u.slug}`); break; }
  }
}

for (const book of BOOKS) {
  const root = path.join(REPO, 'book', book);
  for (const sec of fs.readdirSync(root, { withFileTypes: true })) {
    if (!sec.isDirectory()) continue;
    for (const top of fs.readdirSync(path.join(root, sec.name), { withFileTypes: true })) {
      if (!top.isDirectory()) continue;
      const slug = top.name;
      const art = path.join(root, sec.name, slug, slug + '.md');
      if (!fs.existsSync(art)) continue;
      const t = TOPIC.get(`${book}/${slug}`);
      const st = t ? t.basic.status : '(ТЕМИ В МАНІФЕСТІ НЕМА)';
      if (st === 'done') continue;
      const words = (fs.readFileSync(art, 'utf8').match(/\S+/g) || []).length;
      const ours = OURS.has(`${book}/${slug}`);
      console.log(`${ours ? '  наш ' : '⚠ ЧУЖИЙ'} ${book}/${sec.name}/${slug}`.padEnd(66) + ` статус=${st.padEnd(8)} слів=${words}`);
    }
  }
}
