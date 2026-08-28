type Curve = (weeks: number) => number;          // P(схибив) від тижнів розвідки

function expDecay(p0: number, tCal: number, pCal: number): Curve {
  const tau = -tCal / Math.log(pCal / p0);        // з pCal = p0·e^(−tCal/τ)
  return (t) => p0 * Math.exp(-t / tau);
}

interface Trade {
  delayWeek: number;   // вартість зволікання, €/тиждень
  fixCost: number;     // ціна виправлення, €
  pWrong: Curve;       // P(схибив) від тижнів чекання
}

interface Game {
  weeks: number;       // тижнів на сам хід «зміни гру» (скелет)
  fixCost: number;     // у скільки впаде ціна виправлення за інтерфейсом
  pWrong: number;      // P(схибив) на пізнішому, вимірянному рішенні
}

const totalCost = (t: number, tr: Trade): number =>
  tr.delayWeek * t + tr.pWrong(t) * tr.fixCost;

function optimalWait(tr: Trade, tMax = 24, step = 0.01): [number, number] {
  let bestT = 0, bestC = totalCost(0, tr);
  for (let i = 1; i <= Math.round(tMax / step); i++) {
    const t = i * step;
    const c = totalCost(t, tr);
    if (c < bestC) { bestT = t; bestC = c; }
  }
  return [bestT, bestC];
}

type Plan = { label: string; weeks: number; cost: number };

function recommend(tr: Trade, game?: Game, weak = 0.05) {
  const now = totalCost(0, tr);
  const [tStar, cStar] = optimalWait(tr);
  const plans: Plan[] = [
    { label: "вирішити зараз", weeks: 0, cost: now },
    { label: `чекати до LRM (t*=${tStar.toFixed(2)} тиж)`, weeks: tStar, cost: cStar },
  ];
  if (game) {
    const g = tr.delayWeek * game.weeks + game.pWrong * game.fixCost;
    plans.push({ label: "змінити гру", weeks: game.weeks, cost: g });
  }
  const best = plans.reduce((a, b) => (b.cost < a.cost ? b : a));
  const thin = now - cStar < weak * now;          // дно ледь нижче за «вирішити зараз»?
  return { best, plans, tStar, saving: now - cStar, thin };
}

// ── Digital Homes: де зберігати телеметрію ──────────────────────────────────
const dh: Trade = {
  delayWeek: 4000, fixCost: 60000,
  pWrong: expDecay(0.5, 6, 0.2),                  // зараз монетка; за 6 тиж → 0.2
};
const game: Game = { weeks: 1, fixCost: 8000, pWrong: 0.15 };

const { best, plans, saving, thin } = recommend(dh, game);

console.log("Digital Homes — телеметрія: чекати чи вирішувати?\n");
const rows = [...plans, { label: "чекати 6 тиж (наївно)", weeks: 6, cost: totalCost(6, dh) }];
for (const p of rows)
  console.log(`  ${p.label.padEnd(32)}${p.weeks.toFixed(1).padStart(5)} тиж   ${p.cost.toFixed(0).padStart(8)} €`);
console.log(`\n  ПРИПИС: ${best.label.toUpperCase()}  →  ${best.cost.toFixed(0)} €`);
if (thin) {
  console.log(`  timing-важіль слабкий: оптимальне чекання економить лише ${saving.toFixed(0)} € ` +
    `— дно U-кривої майже впритул до «вирішити зараз».`);
  console.log("  зволікання й помилка дорогі водночас → шукай структурний хід.");
}
