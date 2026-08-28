// ── Фіксований операційний податок на КОЖЕН окремо-розгортуваний сервіс ──────
//    (інженер-години на місяць, НЕ залежать від трафіку)
const OPS_PER_SVC = 6 + 5 + 8 + 5;   // конвеєр · дашборди · чергування · патчі = 24 год
const TEAM_HOURS = 6 * 160;          // 6 інженерів × 160 продуктивних год
const Z99 = 2.326;                   // 99-й перцентиль стандартної нормалі

interface Hop { p50: number; p99: number; fail: number; }
const NET: Hop = { p50: 1.0, p99: 15.0, fail: 0.002 };   // RPC-стрибок у датацентрі
const MEM: Hop = { p50: 0.002, p99: 0.002, fail: 0.0 };  // виклик у пам'яті ≈ 2 мкс

interface Arch { name: string; services: number; hot: Hop[]; }

const opsSurface = (a: Arch): number => a.services * OPS_PER_SVC;

function lognorm(h: Hop): [number, number] {
  const mu = Math.log(h.p50);
  const sigma = h.p99 > h.p50 ? Math.log(h.p99 / h.p50) / Z99 : 0;   // 0 для виклику в пам'яті
  return [mu, sigma];
}

// p50 і p99 УСЬОГО шляху = сума незалежних стрибків (Фентон–Вілкінсон):
// середні додаються, дисперсії додаються — а хвіст ні.
function pathLatency(a: Arch): [number, number] {
  let M = 0, V = 0;
  for (const h of a.hot) {
    const [mu, s] = lognorm(h);
    M += Math.exp(mu + (s * s) / 2);                          // середнє стрибка
    V += (Math.exp(s * s) - 1) * Math.exp(2 * mu + s * s);    // дисперсія стрибка
  }
  if (M === 0) return [0, 0];
  const sig2 = Math.log(1 + V / (M * M));   // σ² суми: росте як корінь, не лінійно
  const muS = Math.log(M) - sig2 / 2;
  const s = Math.sqrt(sig2);
  return [Math.exp(muS), Math.exp(muS + Z99 * s)];
}

const pathAvail = (a: Arch): number =>
  a.hot.reduce((p, h) => p * (1 - h.fail), 1);               // добуток успіхів на стрибках

const newFailureModes = (a: Arch): number =>
  a.hot.filter((h) => h.fail > 0).length;

const fmtMs = (x: number): string =>
  x < 1 ? `${Math.round(x * 1000)} мкс` : `${x.toFixed(1)} мс`;

const mono: Arch =    { name: "моноліт (1 деплой)",      services: 1, hot: [MEM, MEM, MEM] };
const full: Arch =    { name: "повний розкол (9)",        services: 9, hot: [NET, NET, NET] };
const partial: Arch = { name: "моноліт + телеметрія (2)", services: 2, hot: [MEM, MEM, MEM] };

for (const a of [mono, full, partial]) {
  const [p50, p99] = pathLatency(a);
  console.log(
    `${a.name}  сервісів=${a.services}  ops=${opsSurface(a)} год  ` +
    `команда=${((opsSurface(a) / TEAM_HOURS) * 100).toFixed(0)}%  ` +
    `p50=${fmtMs(p50)}  p99=${fmtMs(p99)}  ` +
    `доступність=${(pathAvail(a) * 100).toFixed(3)}%  +відмов=${newFailureModes(a)}`,
  );
}

// ── Крива окупності: коли ВЛАСНИЙ драйвер контексту переважує частку премії ──
const ENG_HOUR = 80;                     // $ за інженер-годину, повністю навантажена
const PREMIUM = OPS_PER_SVC * ENG_HOUR;  // $/міс — чиста операційка одного сервісу
const C_FULL = 350;                      // повна репліка моноліта (усі модулі в пам'яті)
const C_SLICE = 110;                     // тонка репліка одного контексту

function worthSplit(peakReplicas: number): [boolean, number, number] {
  const keep = peakReplicas * C_FULL;
  const split = PREMIUM + peakReplicas * C_SLICE;
  return [split < keep, keep, split];
}
const breakevenReplicas = (): number => PREMIUM / (C_FULL - C_SLICE);

console.log(`\nпремія=$${PREMIUM}/міс  поріг=${breakevenReplicas().toFixed(1)} повних реплік`);
const contexts: [string, number][] = [
  ["телеметрія (запис 40k)", 12], ["твін", 1], ["керування", 1],
  ["ідентичність", 0], ["білінг", 0],
];
for (const [name, u] of contexts) {
  const [ok, keep, split] = worthSplit(u);
  console.log(`  ${name}: драйвер=${u}  тримати=$${keep}  винести=$${split}  ` +
    `→ ${ok ? "ВИНОСИТИ" : "тримати"}`);
}
