const C_SOUND = 343.0; // швидкість звуку при 20 °C, м/с

// Довжина круглого порту (метри) під настройку fb.
// vLitres — об'єм коробки; dM — діаметр порту в метрах.
function portLengthM(fb, vLitres, dM) {
  const V = vLitres * 1e-3;        // літри → м³
  const r = dM * 0.5;
  const A = Math.PI * r * r;       // площа перерізу, м²
  const w = 2.0 * Math.PI * fb;    // кутова частота

  const lEff = (C_SOUND * C_SOUND * A) / (w * w * V); // ефективна довжина
  const lEnd = 2.0 * 0.85 * r;     // поправка: ~0.85·d, обидва кінці
  const lPhys = lEff - lEnd;       // стільки різати трубу
  return lPhys;
}

const fb = 35.0, V = 30.0, d = 0.05;
const L = portLengthM(fb, V, d);
console.log(`Фізична довжина порту = ${(L * 100.0).toFixed(1)} см`);
