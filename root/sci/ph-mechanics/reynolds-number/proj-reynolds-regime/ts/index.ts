// Пороги переходу — саме для КРУГЛОЇ ТРУБИ (характерний розмір = діаметр).
const RE_LAMINAR_MAX = 2300;
const RE_TURBULENT_MIN = 4000;

type Regime = 'ламінарний' | 'перехідний' | 'турбулентний';

interface Result {
  Re: number;
  regime: Regime;
  f: number;        // коефіцієнт тертя Дарсі
  dp: number;       // втрата тиску, Па
  head: number;     // втрата напору, м
  note?: string;    // застереження, якщо є
}

const reynolds = (rho: number, v: number, D: number, mu: number): number =>
  (rho * v * D) / mu;                 // Re = ρ·v·D/μ; D — ДІАМЕТР, не радіус

function classify(Re: number): Regime {
  if (Re < RE_LAMINAR_MAX) return 'ламінарний';
  if (Re < RE_TURBULENT_MIN) return 'перехідний';
  return 'турбулентний';
}

function frictionFactor(Re: number, eps: number, D: number): number {
  if (Re < RE_LAMINAR_MAX) return 64 / Re;          // ламінар: точно, ε байдужа
  // турбулент — явна формула Гааланда:
  // 1/√f = −1.8·log₁₀[ (ε/D / 3.7)^1.11 + 6.9/Re ]
  const invSqrtF = -1.8 * Math.log10((eps / D / 3.7) ** 1.11 + 6.9 / Re);
  return 1 / invSqrtF ** 2;
}

function pipeLoss(
  rho: number, v: number, D: number, mu: number, L: number,
  eps = 1.5e-6, g = 9.81,
): Result {
  const Re = reynolds(rho, v, D, mu);
  const regime = classify(Re);
  const f = frictionFactor(Re, eps, D);
  const dp = f * (L / D) * (rho * v ** 2 / 2);      // Дарсі–Вайсбах
  return {
    Re, regime, f, dp, head: dp / (rho * g),
    note: regime === 'перехідний' ? 'перехідна смуга: f — груба оцінка' : undefined,
  };
}

const r = pipeLoss(1000, 1.0, 0.015, 1e-3, 10.0);
console.log(`Re    = ${r.Re.toFixed(0)}  (${r.regime})`);
console.log(`f     = ${r.f.toFixed(4)}`);
console.log(`Δp    = ${(r.dp / 1000).toFixed(2)} кПа  на 10 м труби`);
console.log(`напір = ${r.head.toFixed(2)} м`);
