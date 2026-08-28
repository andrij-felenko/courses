type Option = {
  name: string;
  availPct: number;                 // СИРА доступність, % — для обмеження
  scores: Record<string, number>;   // бали 0..5 — для суми вподобань
};

const W: Record<string, number> = { вартість: 5, доступність: 4, швидкодія: 3, безпека: 4 };

const options: Option[] = [
  { name: "A: один регіон",  availPct: 99.0,  scores: { вартість: 5, доступність: 1, швидкодія: 5, безпека: 4 } },
  { name: "B: мультирегіон", availPct: 99.95, scores: { вартість: 2, доступність: 5, швидкодія: 4, безпека: 4 } },
];

const weightedSum = (o: Option) =>
  Object.keys(W).reduce((s, k) => s + W[k] * o.scores[k], 0);

// ── Наївно: доступність — просто одна з ваг, поріг «розчинено» в сумі ──
console.log("наївна зважена сума (обмеження як м'яка вага):");
for (const o of [...options].sort((a, b) => weightedSum(b) - weightedSum(a)))
  console.log(`  ${o.name}  сума = ${weightedSum(o)}`);

// ── Чесно: спершу фільтр твердого порога, тоді сума серед дійсних ──
const FLOOR = 99.9; // доступність ≥ 99.9% — закон, не вподобання
const feasible = options.filter((o) => o.availPct >= FLOOR);
const best = feasible.reduce((a, b) => (weightedSum(b) > weightedSum(a) ? b : a));
console.log("\nчесно (фільтр порога, тоді сума серед дійсних):");
for (const o of options)
  console.log(
    o.availPct >= FLOOR
      ? `  ${o.name}  дійсний, сума = ${weightedSum(o)}`
      : `  ${o.name}  ВІДСІЯНО (${o.availPct.toFixed(2)}% < ${FLOOR}%)`,
  );
console.log(`  → вибір: ${best.name}`);
