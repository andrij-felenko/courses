def insert(p: Payment, tx) -> None:
    kind = "card" if isinstance(p, CardPayment) else "bank"
    tx.execute(
        "INSERT INTO payments(id, kind, amount_cents, currency, created_at)"
        " VALUES (%s, %s, %s, %s, %s)",
        (p.id, kind, p.amount.cents, p.amount.ccy, p.created_at))
    if isinstance(p, CardPayment):
        tx.execute(
            "INSERT INTO card_payments(id, card_last4, auth_code) VALUES (%s, %s, %s)",
            (p.id, p.card_last4, p.auth_code))
    elif isinstance(p, BankTransfer):
        tx.execute(
            "INSERT INTO bank_transfers(id, iban, reference) VALUES (%s, %s, %s)",
            (p.id, p.iban, p.reference))
