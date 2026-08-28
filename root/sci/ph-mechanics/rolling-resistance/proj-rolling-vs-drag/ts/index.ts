const G = 9.81;              // м/с², прискорення вільного падіння
const RHO = 1.225;           // кг/м³, повітря за 15 °C і 101.3 кПа

interface Vehicle {
  name: string;
  mass: number;   // кг
  cRR: number;    // безрозмірний коефіцієнт опору коченню
  cdA: number;    // C_d·A — «аеродинамічний переріз», м²
}

/** Швидкість (м/с), на якій опір повітря зрівнюється з опором коченню. */
function crossoverSpeed(m: number, cRR: number, cdA: number, rho = RHO): number {
  return Math.sqrt((2 * cRR * m * G) / (rho * cdA));
}

/** Частка повітря в повному опорі на швидкості v (м/с). */
function aeroShare(v: number, vStar: number): number {
  const ratio = (v / vStar) ** 2;            // F_повітря / F_кочення
  return ratio / (1 + ratio);
}

/** C_rr(v) = c0 + c1·v + c2·v² (форма моделі SAE J2452).
 *  null — перетину немає взагалі: кочення дорожчає не повільніше. */
function crossoverSpeedVar(
  m: number, c0: number, c1: number, c2: number, cdA: number, rho = RHO,
): number | null {
  const a = 0.5 * rho * cdA - c2 * m * G;    // спільний коефіцієнт при v²
  if (a <= 0) return null;
  const b = -c1 * m * G;
  const c = -c0 * m * G;
  return (-b + Math.sqrt(b * b - 4 * a * c)) / (2 * a);
}

/** Загальний випадок: C_rr — довільна функція швидкості; ділимо навпіл. */
function crossoverSpeedNum(
  m: number, cRRof: (v: number) => number, cdA: number, rho = RHO, vHi = 120,
): number | null {
  const gap = (v: number) => 0.5 * rho * cdA * v * v - cRRof(v) * m * G;
  if (gap(vHi) <= 0) return null;
  let lo = 0, hi = vHi;                      // gap(0) < 0, gap(vHi) > 0
  for (let i = 0; i < 60; i++) {
    const mid = (lo + hi) / 2;
    if (gap(mid) > 0) hi = mid; else lo = mid;
  }
  return (lo + hi) / 2;
}

/** Швидкість відносно ДОРОГИ з поправкою на зустрічний вітер і ухил. */
function crossoverGroundSpeed(
  m: number, cRR: number, cdA: number, headwind = 0, grade = 0, rho = RHO,
): number {
  const theta = Math.atan(grade);
  const cEff = cRR * Math.cos(theta) + Math.sin(theta);
  return crossoverSpeed(m, cEff, cdA, rho) - headwind;
}

/** ρ = p/(R·T), R = 287.05 Дж/(кг·К) для сухого повітря. */
function airDensity(tC: number, pPa = 101325): number {
  return pPa / (287.05 * (tC + 273.15));
}

const FLEET: Vehicle[] = [
  { name: "велосипед із гонщиком", mass: 85,    cRR: 0.0040, cdA: 0.30 },
  { name: "електросамокат",        mass: 100,   cRR: 0.0150, cdA: 0.55 },
  { name: "легковик-хетчбек",      mass: 1200,  cRR: 0.0120, cdA: 0.66 },
  { name: "електроседан",          mass: 1900,  cRR: 0.0090, cdA: 0.53 },
  { name: "фура, 40 т",            mass: 40000, cRR: 0.0060, cdA: 6.30 },
];

for (const { name, mass, cRR, cdA } of FLEET) {
  const vStar = crossoverSpeed(mass, cRR, cdA);
  console.log(
    `${name.padEnd(22)} v* = ${(vStar * 3.6).toFixed(1).padStart(5)} км/год` +
    `   на 90 км/год повітря дає ${(100 * aeroShare(90 / 3.6, vStar)).toFixed(1).padStart(4)} %`,
  );
}

const m = 1200, cRR = 0.012, cdA = 0.66;
const rhoCold = airDensity(-10);
const cRRof = (v: number) => 0.0105 + 4e-6 * v * v;   // v у м/с

const show = (label: string, vStar: number | null) =>
  console.log("  " + label.padEnd(28) +
    (vStar === null ? "—" : `${(vStar * 3.6).toFixed(1).padStart(5)} км/год`));

console.log("\nтой самий хетчбек, різні умови:");
show("рівна дорога, безвітря", crossoverSpeed(m, cRR, cdA));
show("зустрічний вітер 5 м/с", crossoverGroundSpeed(m, cRR, cdA, 5));
show("підйом 3 %", crossoverGroundSpeed(m, cRR, cdA, 0, 0.03));
show(`мороз −10 °C (ρ = ${rhoCold.toFixed(3)})`, crossoverSpeed(m, cRR, cdA, rhoCold));
show("C_rr = 0.0105 + 4e−6·v²", crossoverSpeedVar(m, 0.0105, 0, 4e-6, cdA));
show("те саме половинним поділом", crossoverSpeedNum(m, cRRof, cdA));
show("а якби c₂ = 4e−5", crossoverSpeedVar(m, 0.0105, 0, 4e-5, cdA));
