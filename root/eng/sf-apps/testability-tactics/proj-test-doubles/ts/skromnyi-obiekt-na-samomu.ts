// Уся логіка — у чистій частині, яку тестуємо густо й дешево.
class ConfirmationComposer {
  compose(email: string, total: Money): { to: string; subject: string; body: string } {
    const hrn = (total / 100).toFixed(2);
    return { to: email, subject: "Замовлення прийнято",
             body: `Дякуємо! До сплати: ${hrn} грн.` };
  }
}

// Скромна оболонка: жодного рішення — лише делегування + один зовнішній виклик.
class SmtpNotifier implements Notifier {
  constructor(
    private readonly composer: ConfirmationComposer,
    private readonly smtp: SmtpClient,   // чуже, за ВЛАСНИМ портом
  ) {}
  sendConfirmation(email: string, total: Money): void {
    this.smtp.send(this.composer.compose(email, total));
  }
}
