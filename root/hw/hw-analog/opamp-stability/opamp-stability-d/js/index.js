// Частота, де розімкнене |A| падає до заданого замкненого підсилення G:
//   на ділянці одного полюса |A|·f = GBW (стала площа),
//   тож перетин лінії 1/β настає на f_cross = GBW / G.
function crossoverHz(gbw, gain) {
  return gbw / gain;              // частота зрізу петлі для цього G
}

const gbw  = 50.0e6;              // 50 МГц з даташита
const fP2  =  6.0e6;              // другий полюс — 6 МГц

for (const gain of [4.0, 1.0]) {
  const fc = crossoverHz(gbw, gain);
  // перетин безпечний, лише якщо він НИЖЧЕ за другий полюс
  // (тоді крива там ще на пологому −20 дБ/дек)
  const safe = fc < fP2;
  const verdict = safe ? "перетин до p2 -> стійко"
                       : "перетин ЗА p2 -> дзвін!";
  console.log(`G=${gain.toFixed(0)}: f_cross=${(fc / 1e6).toFixed(1)} MHz  ->  ${verdict}`);
}
