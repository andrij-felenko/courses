function amountFor(line: Line): number {
  let result = 0;
  if (line.tariff === "day") {
    result = line.kWh * 250;
    if (line.kWh > 100) result += (line.kWh - 100) * 30;
  } else if (line.tariff === "night") {
    result = line.kWh * 120;
  } else if (line.tariff === "business") {
    result = line.kWh * 300;
    if (line.kWh > 500) result += (line.kWh - 500) * 40;
  } else {
    throw new Error(`невідомий тариф: ${line.tariff}`);
  }
  return result;
}
// у statement: for (const line of acc.lines) { … amountFor(line) … }
// тести: зелено
