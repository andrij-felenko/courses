function creditsFor(account: Account, line: Line): number {
  let credits = 0;
  if (account.active) {
    if (line.tariff !== "business") {
      credits += Math.max(line.kWh - 200, 0);
      if (line.tariff === "night") credits += Math.floor(line.kWh / 500);
    }
  }
  return credits;
}

// у statement:  vc += creditsFor(acc, line);
// тести: зелено
