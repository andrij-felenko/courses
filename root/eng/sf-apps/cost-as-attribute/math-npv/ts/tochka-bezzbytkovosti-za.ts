const annuityFactor = (r: number, n: number): number =>
  r === 0 ? n : (1 - (1 + r) ** -n) / r;

// Знайти r*, за якої A(r*) = targetA. A спадає з r → бісекція надійна.
function solveRate(targetA: number, n: number, lo = 1e-9, hi = 5.0): number {
  for (let i = 0; i < 100; i++) {
    const mid = (lo + hi) / 2;
    if (annuityFactor(mid, n) > targetA) lo = mid; // A завелика → ставка замала
    else hi = mid;                                 // A замала  → ставка завелика
  }
  return (lo + hi) / 2;
}

// «будувати» = «купити»:  150 + 20·A = 60·A  ⟹  A = 3.75
const rStar = solveRate(3.75, 5);
console.log(`r* = ${rStar.toFixed(4)}  (${(rStar * 100).toFixed(1)} %)`); // 0.1042 (10.4 %)
