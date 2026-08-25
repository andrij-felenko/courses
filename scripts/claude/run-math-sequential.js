const { execSync } = require('child_process');
const path = require('path');

const ROOT = 'E:\\develop\\courses';
const TOTAL_RUNS = 10;

console.log(`================================================================`);
console.log(`🚀 SEQUENTIAL 10-TOPIC RUNNER FOR BOOK: MATH`);
console.log(`Target: root/sci/math-* | Count: 10 topics | Single Execution Mode`);
console.log(`================================================================\n`);

for (let i = 1; i <= TOTAL_RUNS; i++) {
  console.log(`\n================================================================`);
  console.log(`▶️ RUN ${i} OF ${TOTAL_RUNS} FOR BOOK: MATH`);
  console.log(`================================================================`);

  try {
    const cmd = `node ${path.join(ROOT, 'scripts', 'write-single-topic.js')} "{\\"book\\":\\"math\\",\\"kind\\":\\"book\\"}"`;
    console.log(`Executing: ${cmd}\n`);
    execSync(cmd, { cwd: ROOT, stdio: 'inherit' });
    console.log(`\n✓ Run ${i}/${TOTAL_RUNS} completed successfully.`);
  } catch (e) {
    console.error(`\n✖ Run ${i}/${TOTAL_RUNS} encountered an issue: ${e.message}`);
  }
}

console.log(`\n================================================================`);
console.log(`🎉 ALL 10 SEQUENTIAL RUNS COMPLETED FOR BOOK: MATH`);
console.log(`================================================================`);
