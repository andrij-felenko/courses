interface Tactic {
  name: string;
  du: Record<string, number>;      // приріст корисності ΔU по сценаріях
  cost: number;                    // зусилля + податок-складності + експлуатація
}

const benefit = (t: Tactic, weight: Record<string, number>, mu: number): number =>
  Object.entries(weight)
    .reduce((sum, [s, w]) => sum + (t.du[s] ?? 0) * w, 0) * mu;

const roi = (t: Tactic, weight: Record<string, number>, mu: number): number =>
  (benefit(t, weight, mu) - t.cost) / t.cost;

function pickUnderBudget(
  tactics: Tactic[], weight: Record<string, number>, mu: number, budget: number,
): { chosen: string[]; spent: number } {
  // сортуємо за ROI спадно, беремо жадібно, доки вистачає бюджету
  const ranked = [...tactics].sort((a, b) => roi(b, weight, mu) - roi(a, weight, mu));
  const chosen: string[] = [];
  let spent = 0;
  for (const t of ranked) {
    if (roi(t, weight, mu) <= 0) continue;   // збиткову — ніколи
    if (spent + t.cost <= budget) {
      chosen.push(t.name);
      spent += t.cost;
    }
  }
  return { chosen, spent };
}

const weight = { пік: 0.40, відмова: 0.35, провайдер: 0.25 };
const tactics: Tactic[] = [
  { name: "кеш+репліки",   du: { пік: 60, відмова: 20 },               cost: 30 },
  { name: "синхронне",     du: { пік: -6, відмова: 60 },               cost: 40 },
  { name: "шар-провайдер", du: { провайдер: 50 },                      cost: 12 },
  { name: "мікросервіси",  du: { пік: 50, відмова: 10, провайдер: 35 }, cost: 150 },
];
console.log(pickUnderBudget(tactics, weight, 3.0, 45));
// { chosen: [ 'шар-провайдер', 'кеш+репліки' ], spent: 42 }
