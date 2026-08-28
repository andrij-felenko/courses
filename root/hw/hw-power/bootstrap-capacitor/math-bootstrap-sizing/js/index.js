// Усі величини — у базових одиницях СІ: кулони, ампери, фаради, секунди, вольти.
// p — об'єкт параметрів із полями:
//   Qg        заряд затвора верхнього ключа, Кл (з даташита MOSFET)
//   Qls       заряд зсуву рівня за такт, Кл (з даташита драйвера)
//   Qrr       зворотний заряд відновлення діода, Кл (0 для Шотткі)
//   Iqbs      струм спокою верхнього боку, А (макс із даташита)
//   IcbsLeak  витік плаваючої шини драйвера + конденсатора, А
//   IgLeak    витік затвора + зсуву рівня в статиці, А
//   f         частота ШІМ, Гц
//   dutyMax   максимальна робоча шпаруватість, 0..1
//   dVAllow   дозволене просідання VB-VS, В
//   Rcharge   сумарний послідовний опір доливу, Ом
//   dcbiasDerate  частка ємності, що лишається під напругою (напр. 0.5)
//   margin    додатковий запас (пуск, розкид), напр. 3.0

// Нижня межа: скільки ємності треба, щоб не просісти за найдовший відкритий такт.
function cbsMin(p) {
  const tOn   = p.dutyMax / p.f;                    // найдовший відкритий час
  const qOnce = p.Qg + p.Qls + p.Qrr;              // разові порції
  const iFlow = p.Iqbs + p.IcbsLeak + p.IgLeak;
  const qFlow = iFlow * tOn;                        // цівки × час
  const qTotal = qOnce + qFlow;
  return { cbs: qTotal / p.dVAllow, qTotal };       // Cbs >= Qвитрат / ΔV
}

// Верхня межа: більше цієї ємності не встигне долитися за паузу tOff (5·τ).
function cbsMax(p) {
  const tOff = (1.0 - p.dutyMax) / p.f;             // закрита частина періоду
  const tauAllow = tOff / 5.0;                      // 5 сталих часу на долив
  return tauAllow / p.Rcharge;                      // Cbs_max = t_off / (5·R)
}

// Номінал, який реально ставимо: підлогу ділимо на DC-bias і множимо на запас.
function cbsPick(p) {
  const { cbs: lo } = cbsMin(p);
  return lo / p.dcbiasDerate * p.margin;            // компенсуємо DC-bias і запас
}

function main() {
  const p = {
    Qg: 50e-9, Qls: 5e-9, Qrr: 2e-9,
    Iqbs: 230e-6, IcbsLeak: 50e-6, IgLeak: 0.3e-6,
    f: 20e3, dutyMax: 0.90, dVAllow: 0.5,
    Rcharge: 10.0, dcbiasDerate: 0.5, margin: 3.0,
  };

  const { cbs: lo, qTotal } = cbsMin(p);
  const hi = cbsMax(p);
  const pick = cbsPick(p);

  console.log(`Qвитрат   = ${(qTotal * 1e9).toFixed(1)} нКл`);
  console.log(`Cbs(min)  = ${(lo * 1e9).toFixed(0)} нФ   (нижня межа з балансу заряду)`);
  console.log(`Cbs(max)  = ${(hi * 1e9).toFixed(0)} нФ   (верхня межа з перезаряду)`);
  console.log(`ставимо   ~ ${(pick * 1e6).toFixed(2)} мкФ  (з DC-bias і запасом)`);

  if (pick > hi) {
    console.log("УВАГА: потрібна ємність не долиється за паузу!");
    console.log("  → знизь R доливу, зменш стелю шпаруватості або візьми зарядову помпу.");
  }
}

main();
