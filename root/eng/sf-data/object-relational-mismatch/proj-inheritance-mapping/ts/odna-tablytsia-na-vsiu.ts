type Row = {
  id: number; kind: 'card' | 'bank'; amount_cents: number; currency: string;
  created_at: string; card_last4: string | null; auth_code: string | null;
  iban: string | null; reference: string | null;
};

function fromRow(r: Row): Payment {
  const amount = new Money(r.amount_cents, r.currency);
  const at = new Date(r.created_at);
  switch (r.kind) {
    case 'card': return new CardPayment(r.id, amount, at, r.card_last4!, r.auth_code!);
    case 'bank': return new BankTransfer(r.id, amount, at, r.iban!, r.reference!);
  }
}
