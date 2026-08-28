function statement(invoice: Invoice): string {
  let result = 0;
  for (const line of invoice.lines) {
    let amount = line.qty * line.unitPrice;
    if (line.qty > 100) {
      amount -= (line.qty - 100) * line.unitPrice * 0.05;
    }
    result += amount;
  }
  return `Разом: ${result} грн`;
}
