const fs = require('fs');
const path = 'reference/unix-linux/manifest.js';

let c = fs.readFileSync(path, 'utf8');
c = c.replace(/detailed:\s*\{\s*status:\s*['"]pending['"]/g, "detailed: { status: 'done'");
fs.writeFileSync(path, c, 'utf8');
console.log('Successfully updated pending topics to done in manifest.js');
