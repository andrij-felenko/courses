  let ta = 0;
  let vc = 0;

  for (const line of acc.lines) {                 // петля 1: рахунок і друк
    const a = amountFor(line);
    out += `  ${line.meter}: ${line.kWh} кВт·год — ${(a / 100).toFixed(2)} грн\n`;
    ta += a;
  }
  for (const line of acc.lines) {                 // петля 2: лише бонуси
    vc += creditsFor(acc, line);
  }
// тести: зелено
