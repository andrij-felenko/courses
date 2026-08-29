const fs = require('fs');
const path = require('path');
const L = require('./checks/_lib.js');

// We will construct the entire detailed article with complete depth.
const text = fs.readFileSync('scripts/detailed_builder/sec1_huge.md', 'utf8') + '\n\n' +
             fs.readFileSync('scripts/detailed_builder/sec2_huge.md', 'utf8');

console.log('Current words:', L.proseWords(text));
