// Emit compact args for write-batch.js. Briefs stay in the payload file (agents fetch them).
// Cross-book newTopics are STRIPPED (they'd edit another book's manifest concurrently -> lost update)
// and parked in cross-book.json for one serial registration after all batches finish.
const fs = require('fs');
const path = require('path');
const BOOK = process.argv[2];
const p = require(`./payload-${BOOK}.json`);
const briefFile = path.join(__dirname, `payload-${BOOK}.json`);

const own = p.newTopics.filter(t => (t.book || BOOK) === BOOK);
const cross = p.newTopics.filter(t => (t.book || BOOK) !== BOOK);

const args = {
  book: p.book,
  kind: 'book',
  level: 'basic',
  limit: p.units.length,
  skipArticles: p.onDisk,          // list of slugs whose .md already exists -> not rewritten
  briefFile,
  units: p.units,
  inserts: p.inserts.map(i => ({ file: i.file, type: i.type, section: i.section, topicSlug: i.topicSlug, topicTitle: i.topicTitle })),
  insertsDone: p.insertsDone,   // already on disk: register in manifest, do NOT rewrite
  newTopics: own,
  detailed: p.detailed,
};
fs.writeFileSync(path.join(__dirname, `args-${BOOK}.json`), JSON.stringify(args), 'utf8');

// accumulate cross-book topics for later
const xf = path.join(__dirname, 'cross-book.json');
const acc = fs.existsSync(xf) ? JSON.parse(fs.readFileSync(xf, 'utf8')) : [];
for (const t of cross) if (!acc.some(a => a.book === t.book && a.slug === t.slug)) acc.push({ ...t, from: BOOK });
fs.writeFileSync(xf, JSON.stringify(acc, null, 1), 'utf8');

console.log(`${BOOK}: bytes ${JSON.stringify(args).length} | units ${args.units.length} | skip ${args.skipArticles.length} | write ${args.units.length - args.skipArticles.length} | inserts ${args.inserts.length} | newTopics(own) ${own.length} | cross parked ${cross.length}`);
