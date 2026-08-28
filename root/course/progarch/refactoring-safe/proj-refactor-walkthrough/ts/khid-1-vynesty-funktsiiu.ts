function amountFor(l: Line): number {
  let a = 0;
  if (l.tariff === "day") {
    a = l.kWh * 250;
    if (l.kWh > 100) a += (l.kWh - 100) * 30;
  } else if (l.tariff === "night") {
    a = l.kWh * 120;
  } else if (l.tariff === "business") {
    a = l.kWh * 300;
    if (l.kWh > 500) a += (l.kWh - 500) * 40;
  } else {
    throw new Error(`невідомий тариф: ${l.tariff}`);
  }
  return a;
}

// у statement блок тарифу зник, лишився виклик:
    const a = amountFor(l);
// тести: зелено
