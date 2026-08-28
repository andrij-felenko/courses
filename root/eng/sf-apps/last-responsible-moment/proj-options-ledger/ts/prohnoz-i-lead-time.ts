// Знімок: для кожного сигналу — вікно останніх щотижневих замірів.
type Window = Record<string, number[]>;   // signal → [найдавніший … найновіший]

const latest = (xs: number[]): number => xs[xs.length - 1];

// Нахил (одиниць за тиждень) методом найменших квадратів по вікну.
function slopePerWeek(xs: number[]): number {
  const n = xs.length;
  if (n < 2) return 0;
  const meanX = (n - 1) / 2;                      // тижні 0…n-1
  const meanY = xs.reduce((a, b) => a + b, 0) / n;
  let num = 0, den = 0;
  for (let i = 0; i < n; i++) {
    num += (i - meanX) * (xs[i] - meanY);
    den += (i - meanX) ** 2;
  }
  return den === 0 ? 0 : num / den;
}

// Прогноз на L тижнів наперед — лінійна екстраполяція краю вікна.
const project = (xs: number[], leadWeeks: number): number =>
  latest(xs) + slopePerWeek(xs) * leadWeeks;

const past = (v: number, thr: number, dir: Dir): boolean =>
  dir === "rising" ? v >= thr : v <= thr;

// Зводимося на ФАКТІ (arm по latest), стріляємо за ПРОГНОЗОМ (fire по project).
function isArmed(t: Trigger, w: Window): boolean {
  const hit = t.conditions.map(c => {
    const xs = w[c.signal];
    return xs?.length ? past(latest(xs), c.armAt, c.dir) : false;
  });
  return t.mode === "all" ? hit.every(Boolean) : hit.some(Boolean);
}

function isFiring(t: Trigger, w: Window): boolean {
  const hit = t.conditions.map(c => {
    const xs = w[c.signal];
    return xs?.length ? past(project(xs, t.leadWeeks), c.fireAt, c.dir) : false;
  });
  return t.mode === "all" ? hit.every(Boolean) : hit.some(Boolean);
}
