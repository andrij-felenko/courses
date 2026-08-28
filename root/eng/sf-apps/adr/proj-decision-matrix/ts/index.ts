// Матриця рішення, яка звітує про власну хиткість.

type Criterion = { readonly name: string; readonly weight: number }; // ×1..×5; зарубка = 1

type Option = {
  readonly name: string;
  readonly scores: readonly number[];  // 1..5 за кожним критерієм
  readonly meets: readonly boolean[];  // так/ні за кожною ВИМОГОЮ — не оцінка, а вирок
};

const total = (o: Option, crits: readonly Criterion[]): number =>
  crits.reduce((sum, c, i) => sum + c.weight * o.scores[i], 0);

const rejected = (o: Option, reqs: readonly string[]): string[] =>
  reqs.filter((_, i) => !o.meets[i]);

const diff = (a: Option, b: Option): number[] => a.scores.map((s, i) => s - b.scores[i]);

function duel(winner: Option, rival: Option, crits: readonly Criterion[]) {
  const d = diff(winner, rival);
  const margin = crits.reduce((sum, c, i) => sum + c.weight * d[i], 0);
  const swing = d.reduce((sum, di) => sum + Math.abs(di), 0);      // Σ|dᵢ| — ціна зарубки
  const stance = crits.map((c, i) => c.weight - Math.sign(d[i]));  // найгірша УЗГОДЖЕНА незгода
  return { margin, swing, notches: swing === 0 ? Infinity : margin / swing, stance };
}

function oat(winner: Option, rival: Option, crits: readonly Criterion[], lo = 1, hi = 5) {
  const d = diff(winner, rival);
  const margin = crits.reduce((sum, c, i) => sum + c.weight * d[i], 0);
  return crits.map((c, i) => {
    if (d[i] === 0) return { name: c.name, tie: null, note: "не розрізняє варіанти" };
    const tie = c.weight - margin / d[i];
    const pct = ((tie - c.weight) / c.weight) * 100;
    const note =
      tie >= lo && tie <= hi
        ? `зміна ${pct > 0 ? "+" : ""}${pct.toFixed(0)}%`
        : `поза шкалою ×${lo}..×${hi}`;
    return { name: c.name, tie, note };
  });
}

const product = <T,>(grids: readonly T[][]): T[][] =>
  grids.reduce<T[][]>((acc, g) => acc.flatMap((p) => g.map((v) => [...p, v])), [[]]);

function sweep(opts: readonly Option[], crits: readonly Criterion[], lo = 1, hi = 5) {
  const grids = crits.map((c) =>
    [c.weight - 1, c.weight, c.weight + 1].filter((w) => w >= lo && w <= hi),
  );
  const wins = new Map<string, number>();
  let ties = 0;
  let n = 0;
  for (const ws of product(grids)) {
    const variant = crits.map((c, i) => ({ ...c, weight: ws[i] }));
    const totals = opts.map((o) => ({ name: o.name, t: total(o, variant) }));
    const best = Math.max(...totals.map((x) => x.t));
    const leaders = totals.filter((x) => x.t === best);
    n++;
    if (leaders.length === 1) wins.set(leaders[0].name, (wins.get(leaders[0].name) ?? 0) + 1);
    else ties++;
  }
  return { wins, ties, n };
}

const CRITS: Criterion[] = [
  { name: "зчеплення служб", weight: 3 },
  { name: "затримка", weight: 2 },
  { name: "проста експлуатація", weight: 2 },
  { name: "стійкість до збою", weight: 3 },
];

// Вимога з розділу «Контекст»: оформлення НЕ має падати, коли склад недоступний.
const REQS = ["оформлення живе, коли склад недоступний"];

const OPTS: Option[] = [
  //                          зчепл. затр. експл. стійк.        вимога
  { name: "синхр. виклик", scores: [2, 5, 5, 2], meets: [false] },
  { name: "черга подій", scores: [5, 3, 2, 5], meets: [true] },
  { name: "спільна табл.", scores: [1, 4, 4, 2], meets: [true] },
];
