const t0 = performance.now();                    // мс від timeOrigin
// ... робота ...
const elapsedMs = performance.now() - t0;

const deadline = performance.now() + 30_000;
const left = () => Math.max(0, deadline - performance.now());

const stamp = Date.now();                        // момент за календарем

// Node.js: цілі наносекунди, без утрати точності на float
const n0 = process.hrtime.bigint();
const elapsedNs = process.hrtime.bigint() - n0;
