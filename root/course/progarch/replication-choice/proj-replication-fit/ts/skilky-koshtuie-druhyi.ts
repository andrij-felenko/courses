function expectedConflictsPerHour(homes: number, wPerHomeHr: number, oneWayMs: number, pCross: number): number {
  const lam   = wPerHomeHr / 3600;          // записів/с в ОДИН ключ
  const delta = oneWayMs / 1000;            // с — одностороння затримка реплікації
  const pGap  = 1 - Math.exp(-lam * delta); // P(сусідні записи ближче за Δ)
  return homes * wPerHomeHr * pCross * pGap;
}

// Детермінований ГПВЧ, щоб Монте-Карло відтворювалося (Math.random не сідиться).
function mulberry32(seed: number): () => number {
  return () => {
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function simulateOneHome(wPerHr: number, oneWayMs: number, pCross: number, hours: number, seed = 1): number {
  const rng = mulberry32(seed);
  const lam = wPerHr / 3600, delta = oneWayMs / 1000, end = hours * 3600;
  let t = 0, prevT: number | null = null, prevLdr: number | null = null, conflicts = 0;
  for (;;) {
    t += -Math.log(rng()) / lam;                        // експоненційний проміжок
    if (t > end) break;
    const ldr = prevLdr === null
      ? (rng() < 0.5 ? 0 : 1)
      : (rng() < pCross ? 1 - prevLdr : prevLdr);
    if (prevT !== null && ldr !== prevLdr && t - prevT < delta) conflicts++;
    prevT = t; prevLdr = ldr;                            // різні писарі + в межах Δ → близнюк
  }
  return conflicts;
}

const HOMES = 500_000, W = 120;               // пів мільйона домів; активний дім — запис раз на 30 с
console.log("один лідер (серіалізує):     ", 0);
console.log("мультилідер, дім-пін (p=0):  ", Math.round(expectedConflictsPerHour(HOMES, W, 80, 0)));
for (const dms of [20, 80, 150])
  console.log(`наївний active-active Δ=${dms}мс:`, Math.round(expectedConflictsPerHour(HOMES, W, dms, 0.5)));

const mc = simulateOneHome(W, 80, 0.5, 200_000) / 200_000;
const an = expectedConflictsPerHour(1, W, 80, 0.5);
console.log(`звірка  MC=${mc.toFixed(5)}  аналітика=${an.toFixed(5)}  конфл/дім·год`);
