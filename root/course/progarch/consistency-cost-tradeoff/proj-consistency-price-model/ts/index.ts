type Guarantee = "кінцева" | "сесійна" | "причинна" | "лінеаризовність";

// множник податку відносно повної (лінеаризовної) строгості:
// нелінійна ціна зі спектра — сесійна ~8% повної, причинна ~30%, лінеаризовність — 100%
const FACTOR: Record<Guarantee, number> = {
  "кінцева": 0.0, "сесійна": 0.08, "причинна": 0.30, "лінеаризовність": 1.0,
};

type Anomaly = "самолікується" | "свій-запис" | "причинний-лад" | "єдиний-лад";

// найслабша гарантія, що прибирає даний рід аномалії
const NEEDS: Record<Anomaly, Guarantee> = {
  "самолікується": "кінцева",          // відстало й само вирівнялось
  "свій-запис":    "сесійна",          // read-your-writes: бачити власну зміну одразу
  "причинний-лад": "причинна",         // наслідок не випереджає причину
  "єдиний-лад":    "лінеаризовність",  // безпека / гроші: один глобальний порядок
};

const LAT_EUR_PER_S = 0.5;   // € за секунду сукупного доданого чекання
const MSG_EUR = 0.02;        // € за одне крос-регіон-повідомлення

interface Item {
  name: string;
  pAnom: number;     // P(аномалія) на операцію
  harmEur: number;   // шкода однієї аномалії, €
  opsS: number;      // операцій/сек
  rttMs: number;     // крос-регіон RTT, мс
  replicas: number;  // скільки реплік координувати
  anomaly: Anomaly;  // рід неконсистентності
}

const harmPerS = (it: Item): number => it.pAnom * it.harmEur * it.opsS;

const fullTaxPerS = (it: Item): number => {
  const latency = (it.rttMs / 1000) * it.opsS * LAT_EUR_PER_S;
  const traffic = it.opsS * (it.replicas - 1) * MSG_EUR;
  return latency + traffic;
};

interface Row {
  name: string; harmS: number; fullTaxS: number;
  score: number; call: string; why: string; hot: boolean;
}

function verdict(it: Item, hotHarm = 1000, hotTax = 100): Row {
  const harm = harmPerS(it);
  const full = fullTaxPerS(it);
  const need = NEEDS[it.anomaly];
  const fixTax = full * FACTOR[need];           // податок ЩАБЛЯ, що прибирає аномалію
  const score = full ? harm / full : Infinity;  // «тиск»: ліва частина ÷ права

  let call: string, why: string;
  if (need === "кінцева") {
    call = "кінцева";
    why = "аномалія самолікується — координувати нема чого";
  } else if (fixTax < harm) {
    call = `тримати строго: ${need}`;
    why = `${need} коштує ${fixTax.toFixed(1)} €/с < шкода ${harm.toFixed(0)} €/с`;
  } else {
    call = "терпіти / змінити гру";
    why = `навіть ${need} (${fixTax.toFixed(1)} €/с) дорожча за шкоду ${harm.toFixed(0)} €/с`;
  }
  const hot = harm > hotHarm && fixTax > hotTax;
  return { name: it.name, harmS: harm, fullTaxS: full, score, call, why, hot };
}

const rank = (items: Item[]): Row[] =>
  items.map((it) => verdict(it)).sort((a, b) => b.score - a.score);

// ── дані Digital Homes ──
const DH: Item[] = [
  { name: "замок дверей",      pAnom: 0.005, harmEur: 800,     opsS: 8,      rttMs: 90, replicas: 3, anomaly: "єдиний-лад" },
  { name: "білінг (підсумок)", pAnom: 0.01,  harmEur: 200,     opsS: 2000,   rttMs: 90, replicas: 5, anomaly: "єдиний-лад" },
  { name: "твін: обігрівач",   pAnom: 0.08,  harmEur: 0.5,     opsS: 3000,   rttMs: 90, replicas: 3, anomaly: "свій-запис" },
  { name: "presence «онлайн»", pAnom: 0.15,  harmEur: 0.002,   opsS: 50000,  rttMs: 90, replicas: 3, anomaly: "самолікується" },
  { name: "телеметрія",        pAnom: 0.20,  harmEur: 0.00005, opsS: 500000, rttMs: 90, replicas: 3, anomaly: "самолікується" },
];

const rpad = (x: number, n: number, d: number) => x.toFixed(d).padStart(n);

console.log(`${"дані DH".padEnd(20)}${"шкода €/с".padStart(11)}${"повний под. €/с".padStart(16)}${"тиск".padStart(7)}  вердикт`);
console.log("-".repeat(74));
for (const r of rank(DH)) {
  const flag = r.hot ? "   🔥 звузити зону" : "";
  console.log(`${r.name.padEnd(20)}${rpad(r.harmS, 11, 1)}${rpad(r.fullTaxS, 16, 0)}${rpad(r.score, 7, 2)}  ${r.call}${flag}`);
  console.log(`${"".padEnd(20)}  └ ${r.why}`);
}
