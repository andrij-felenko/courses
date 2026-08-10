const { execSync } = require('child_process');

const diff = execSync('git diff book/math/manifest.js', { cwd: 'E:/develop/courses', encoding: 'utf8' });

const addedLines = diff.split('\n').filter(l => l.startsWith('+') && !l.startsWith('+++'));

let addedTopics = [];
let addedInserts = [];

let currentTopic = null;

addedLines.forEach(line => {
  const slugMatch = line.match(/"slug":\s*"([^"]+)"/);
  if (slugMatch) {
    addedTopics.push(slugMatch[1]);
  }
  const fileMatch = line.match(/"file":\s*"([^"]+)"/);
  if (fileMatch) {
    addedInserts.push(fileMatch[1]);
  }
});

console.log(`Added/Modified topics in diff: ${addedTopics.length}`);
console.log(JSON.stringify(addedTopics, null, 2));

console.log(`\nAdded/Modified insert files in diff: ${addedInserts.length}`);
console.log(JSON.stringify(addedInserts, null, 2));
