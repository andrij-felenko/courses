// amp[0] — основна (1-ша гармоніка), amp[1..] — 2-га, 3-тя, ...
function thdFromHarmonics(amp) {
  const fund = amp[0];                     // основна гармоніка, U₁
  if (fund <= 0) return 0;                 // немає сигналу — THD не визначений

  let sumSq = 0;                           // сума квадратів вищих гармонік
  for (let k = 1; k < amp.length; ++k)     // від 2-ї (індекс 1) і вище
    sumSq += amp[k] * amp[k];              // U₂² + U₃² + ...

  return Math.sqrt(sumSq) / fund;          // √(ΣUₙ²) / U₁  — частка
}

function demo() {
  // основна 1.000 В; гармоніки 2..7 (типовий спадний «хвіст»)
  const amp = [1.000, 0.0120, 0.0050, 0.0020,
               0.0011, 0.0006, 0.0003];

  const thd    = thdFromHarmonics(amp);    // √(1.2e-4+2.5e-5+...) /1.0
  const thdPct = thd * 100;                // у відсотках
  const thdDb  = 20 * Math.log10(thd);     // у децибелах

  // thd    ≈ 0.0132  (корінь із суми ≈ 0.0132 В при основній 1.000 В)
  // thdPct ≈ 1.32 %
  // thdDb  ≈ −37.6 dB
  return { thd, thdPct, thdDb };
}
