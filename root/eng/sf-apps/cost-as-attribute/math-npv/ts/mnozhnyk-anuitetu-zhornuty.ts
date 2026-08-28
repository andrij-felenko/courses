// Теперішня вартість суми fv, яку заплатять/отримають через n років.
const pv = (fv: number, r: number, n: number): number => fv / (1 + r) ** n;

// flows[t] — потік у рік t (t = 0, 1, 2, …). Зводить усе до сьогодні.
const npv = (flows: number[], r: number): number =>
  flows.reduce((acc, cf, t) => acc + cf / (1 + r) ** t, 0);

// A(r) = Σ 1/(1+r)^t за t = 1..n — замкнутий вигляд, без циклу.
function annuityFactor(r: number, n: number): number {
  if (r === 0) return n;            // границя: дисконтувати нічого
  return (1 - (1 + r) ** -n) / r;
}

// Рівний потік 60 тис. на рік п'ять років під 10 % — одним множенням:
console.log(60 * annuityFactor(0.10, 5));   // 227.45 тис.
