class Money { constructor(readonly cents: number, readonly ccy: string) {} }

abstract class Payment {
  constructor(readonly id: number, readonly amount: Money, readonly createdAt: Date) {}
  abstract settle(): void;
}
class CardPayment extends Payment {
  constructor(id: number, amount: Money, createdAt: Date,
              readonly cardLast4: string, readonly authCode: string) {
    super(id, amount, createdAt);
  }
  settle() { /* провести через платіжний шлюз */ }
}
class BankTransfer extends Payment {
  constructor(id: number, amount: Money, createdAt: Date,
              readonly iban: string, readonly reference: string) {
    super(id, amount, createdAt);
  }
  settle() { /* звірити з банківською випискою */ }
}
