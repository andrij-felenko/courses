interface Decision {
  name: string;
  cod: number;   // вартість зволікання, €/тиждень
  dur: number;   // тривалість розбору, тижнів
}

// Сумарна зважена вартість очікування Σ CoD_j · C_j.
function waitingCost(order: Decision[]): number {
  let week = 0, total = 0;
  for (const d of order) {
    week += d.dur;              // тиждень готовності цього рішення
    total += d.cod * week;      // усе зволікання, що набігло до нього
  }
  return total;
}

// спадання відношення CoD/тривалість — правило Сміта
const wsjfOrder = (ds: Decision[]): Decision[] =>
  [...ds].sort((a, b) => b.cod / b.dur - a.cod / a.dur);

const board: Decision[] = [
  { name: "телеметрія",     cod: 4000, dur: 2 },
  { name: "автентифікація", cod: 1500, dur: 1 },
  { name: "білінг",         cod: 6000, dur: 6 },
];

const best = wsjfOrder(board);
const loud = [...board].sort((a, b) => b.cod - a.cod);   // спершу найбільша CoD

console.log(best.map((d) => d.name), waitingCost(best));  // …, 66500
console.log(loud.map((d) => d.name), waitingCost(loud));  // …, 81500
