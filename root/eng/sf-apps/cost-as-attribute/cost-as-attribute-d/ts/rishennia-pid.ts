// [ймовірність, вартість крихкого, вартість стійкого] за сценаріями, тис. $
const scenarios: [string, number, number, number][] = [
  ["низьке",    0.3,  8, 12],
  ["очікуване", 0.5, 10, 14],
  ["високе",    0.2, 60, 22], // крихкий падає й тягне аварійні витрати
];
const expFragile = scenarios.reduce((s, [, p, f]) => s + p * f, 0);
const expRobust  = scenarios.reduce((s, [, p, , r]) => s + p * r, 0);
const worstFragile = Math.max(...scenarios.map(([, , f]) => f));
const worstRobust  = Math.max(...scenarios.map(([, , , r]) => r));
console.log(`очікувана: крихкий=${expFragile.toFixed(1)} стійкий=${expRobust.toFixed(1)}`);
console.log(`найгірша:  крихкий=${worstFragile} стійкий=${worstRobust}`);
