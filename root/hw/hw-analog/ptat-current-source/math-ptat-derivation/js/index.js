// Тепловий потенціал U_T = k*T/q при абсолютній температурі T (К), у вольтах.
function thermalVoltage(T_kelvin) {
  const k = 1.380649e-23;   // стала Больцмана, Дж/К
  const q = 1.602177e-19;   // елементарний заряд, Кл
  return k * T_kelvin / q;
}

// Різниця падінь база-емітер двох переходів із відношенням площ N.
// ΔU_BE = U_T*ln(N) — чистий PTAT, лінійний крізь нуль.
function deltaVbe(T_kelvin, N) {
  return thermalVoltage(T_kelvin) * Math.log(N);   // ∝ T
}

// Нахил d(ΔU_BE)/dT = (k/q)*ln(N) — стала, та сама при будь-якій T.
function deltaVbeSlope(N) {
  const kOverQ = 8.617333e-5;   // В/К
  return kOverQ * Math.log(N);                     // ≈ 0.1792 мВ/К для N=8
}

// deltaVbe(233.15, 8.0) -> ~41.8 мВ   (−40 °C)
// deltaVbe(398.15, 8.0) -> ~71.3 мВ   (+125 °C)
// Перевірка лінійності: (71.3 − 41.8) / (398.15 − 233.15) = 0.1792 мВ/К — той самий нахил.
