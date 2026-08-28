// money.ts — лише подання грошей рядком
export function formatMoney(v: number): string {
  const rounded = Math.round(v * 100) / 100;
  return `${rounded.toFixed(2)} грн`;
}

// invoice.ts — що саме пишемо користувачеві
export function invoiceLine(total: number): string {
  return `Разом до сплати: ${formatMoney(total)}`;
}
