function totalAmount(account: Account): number {
  let total = 0;
  for (const line of account.lines) total += amountFor(line);
  return total;
}
function totalCredits(account: Account): number {
  let credits = 0;
  for (const line of account.lines) credits += creditsFor(account, line);
  return credits;
}
// тести: зелено
