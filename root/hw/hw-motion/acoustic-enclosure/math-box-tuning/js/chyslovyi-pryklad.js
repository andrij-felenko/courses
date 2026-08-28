// Параметри Тіле–Смолла — просто з даташита: { fs, vas, qts }

// Об'єм закритого ящика під бажану Q_tc.
// Виводиться з V_box = V_as / (α² − 1), де α = Q_tc/Q_ts.
function sealedVolumeLitres(d, qtcTarget) {
  const alpha = qtcTarget / d.qts;   // у скільки разів піднімаємо Q
  const denom = alpha * alpha - 1.0; // α² − 1
  if (denom <= 0.0) return -1.0;     // Q_tc ≤ Q_ts недосяжна в ЗАКРИТОМУ ящику
  return d.vas / denom;
}

// Частота −3 дБ (для Батерворта Q_tc=0.707 вона дорівнює f_c).
function closedBoxFc(d, vboxLitres) {
  return d.fs * Math.sqrt(1.0 + d.vas / vboxLitres);
}

const woofer = { fs: 40.0, vas: 20.0, qts: 0.35 };

const qtc = 0.707;
const vbox = sealedVolumeLitres(woofer, qtc);
const fc = closedBoxFc(woofer, vbox);

console.log(`Ціль Q_tc = ${qtc.toFixed(3)}`);
console.log(`Об'єм коробки V_box = ${vbox.toFixed(1)} л`);
console.log(`Частота в ящику f_c = ${fc.toFixed(1)} Гц`);
