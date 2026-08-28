async function insert(p: Payment, tx: Tx): Promise<void> {
  const kind = p instanceof CardPayment ? 'card' : 'bank';
  await tx.query(
    `INSERT INTO payments(id, kind, amount_cents, currency, created_at)
     VALUES ($1, $2, $3, $4, $5)`,
    [p.id, kind, p.amount.cents, p.amount.ccy, p.createdAt]);
  if (p instanceof CardPayment)
    await tx.query(
      `INSERT INTO card_payments(id, card_last4, auth_code) VALUES ($1, $2, $3)`,
      [p.id, p.cardLast4, p.authCode]);
  else if (p instanceof BankTransfer)
    await tx.query(
      `INSERT INTO bank_transfers(id, iban, reference) VALUES ($1, $2, $3)`,
      [p.id, p.iban, p.reference]);
}
