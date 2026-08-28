const TWO_PI = 2.0 * Math.PI;

// t = { Rf, Cin, Cf, f_gbw }
//   Rf    — резистор перетворення, Ом
//   Cin   — повна вхідна ємність (діод + ОП + монтаж), Ф
//   Cf    — конденсатор компенсації, Ф
//   f_gbw — добуток підсилення на смугу ОП, Гц

// Частоти зламів коефіцієнта зворотного зв'язку
function fzOf(t) {                             // нуль 1/β від вхідної ємності
  return 1.0 / (TWO_PI * t.Rf * (t.Cin + t.Cf));
}
function fpOf(t) {                             // полюс 1/β від Cf = смуга −3 дБ
  return 1.0 / (TWO_PI * t.Rf * t.Cf);
}

// |A|·β = 1: ОП з одним домінантним полюсом має |A(f)| ≈ f_gbw / f.
// 1/β(f) на полиці прямує до (Cin+Cf)/Cf; точну криву беремо з полюса й нуля.
function crossoverHz(t) {
  const fz = fzOf(t), fp = fpOf(t);
  // |A(f)| = f_gbw/f;  |1/β(f)| = sqrt(1+(f/fz)^2) / sqrt(1+(f/fp)^2)
  // шукаємо f, де f_gbw/f = |1/β|, простим діленням навпіл по логарифму
  let lo = fp * 0.05, hi = t.f_gbw;           // перетин гарантовано в цьому вікні
  for (let i = 0; i < 60; ++i) {
    const f = Math.sqrt(lo * hi);             // середина в лог-масштабі
    const A = t.f_gbw / f;
    const ib = Math.sqrt(1.0 + (f/fz)**2) / Math.sqrt(1.0 + (f/fp)**2);
    if (A > ib) lo = f; else hi = f;          // |A| ще вище за 1/β → перетин правіше
  }
  return Math.sqrt(lo * hi);
}

// Запас фази (градуси) при поточному Cf
function phaseMarginDeg(t) {
  const fz = fzOf(t), fp = fpOf(t), fc = crossoverHz(t);
  const deg = 180.0 / Math.PI;
  // фаза петлі: −90° (полюс ОП) − atan(fc/fz) (нуль 1/β) + atan(fc/fp) (полюс 1/β)
  const phase = -90.0 - Math.atan(fc/fz)*deg + Math.atan(fc/fp)*deg;
  return 180.0 + phase;                       // запас до −180°
}

// Cf-орієнтир максимально плоского відгуку (полюс у геом. середині fz та f_gbw)
function cfButterworth(Rf, Cin, f_gbw) {
  return Math.sqrt(Cin / (TWO_PI * Rf * f_gbw));
}

// Приклад: Rf = 1 МОм, Cin = 60 пФ, f_gbw = 10 МГц
function checkExample() {
  const t = { Rf: 1.0e6, Cin: 60.0e-12, Cf: 0.0, f_gbw: 10.0e6 };
  t.Cf = cfButterworth(t.Rf, t.Cin, t.f_gbw);  // ≈ 0.98 пФ
  const pm = phaseMarginDeg(t);                // ≈ 45° — мінімально безпечно
  const bw = fpOf(t);                          // смуга −3 дБ ≈ 162 кГц
  if (pm < 45.0) {
    // запас замалий: побільшити Cf (нижчий полюс, тихіше) або взяти швидший ОП
  }
  void pm; void bw;
}
