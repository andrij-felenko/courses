// Один адаптер на всіх: «форму» перекладу впорскуємо замиканням.
class PluggableGateway<T> implements PaymentGateway {
  constructor(
    private adaptee: T,
    private doCharge: (a: T, amount: number, currency: string) => Promise<string>,
  ) {}
  charge(amount: number, currency: string): Promise<string> {
    return this.doCharge(this.adaptee, amount, currency);   // уся специфіка — у замиканні
  }
}

const stripeGw = new PluggableGateway(
  new StripeClient(),
  (s, amount, cur) =>
    s.createCharge({ amountInMinor: toMinor(amount, cur), currency: cur.toLowerCase() })
     .then(r => r.id),                                       // переклад — тут, без окремого класу
);
