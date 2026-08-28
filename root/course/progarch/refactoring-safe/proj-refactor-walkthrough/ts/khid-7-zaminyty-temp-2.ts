function statement(acc: Account): string {
  let out = `Рахунок — ${acc.customer}\n`;
  for (const line of acc.lines) {
    out += `  ${line.meter}: ${line.kWh} кВт·год — ${(amountFor(line) / 100).toFixed(2)} грн\n`;
  }
  out += `Разом: ${(totalAmount(acc) / 100).toFixed(2)} грн\n`;
  out += `Бонусні кіловати: ${totalCredits(acc)}\n`;
  return out;
}
// тести: зелено
