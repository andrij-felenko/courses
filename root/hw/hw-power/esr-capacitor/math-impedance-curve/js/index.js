// Параметри реального конденсатора → точки галочки |Z(f)|.
// f0 — дно (резонанс), |Z|min = ESR, плюс DF і Q на заданій частоті.

// модуль повного опору в одній точці частоти: |Z| = sqrt(ESR^2 + (wL - 1/wC)^2)
function zMag(f, C, L, esr) {
  const w = 2.0 * Math.PI * f;
  const X = w * L - 1.0 / (w * C);   // чиста реактивність: індуктивна − ємнісна
  return Math.sqrt(esr * esr + X * X);
}

const C = 100e-9;        // 100 нФ
const L = 2e-9;          // 2 нГ паразитної індуктивності
const esr = 0.03;        // 0.03 Ом
const fWork = 100e3;     // робоча частота 100 кГц

const f0 = 1.0 / (2.0 * Math.PI * Math.sqrt(L * C));   // дно галочки
const Xc = 1.0 / (2.0 * Math.PI * fWork * C);          // ємнісний опір на 100 кГц
const DF = esr / Xc;                                    // коефіцієнт втрат
const Q = Xc / esr;                                     // добротність = 1/DF

console.log(`f0      = ${(f0 / 1e6).toFixed(2)} MHz`);
console.log(`|Z|@f0  = ${zMag(f0, C, L, esr).toFixed(3)} Ohm  (= ESR)`);
console.log(`|Z|@100kHz = ${zMag(fWork, C, L, esr).toFixed(2)} Ohm`);
console.log(`DF      = ${DF.toFixed(5)}`);
console.log(`Q       = ${Q.toFixed(0)}`);
