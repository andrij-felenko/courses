// domain/dispatch.ts — ЯДРО. Знає лише порт Notifier, жодного постачальника.
export class OrderDispatch {
  constructor(private notifier: Notifier) {}    // впровадження залежності

  async onCourierAssigned(order: Order, customer: Recipient): Promise<void> {
    const outcome = await this.notifier.notify(customer, {
      kind: "courier_near",
      orderId: order.id,
      minutesAway: order.etaMinutes,
    });
    // рішення домену — БЕЗ знання про 429 чи 421
    if (outcome.status === "retryable") this.scheduleRetry(order);
  }
}

// main.ts — КОМПОЗИЦІЙНИЙ КОРІНЬ: єдиний рядок вибору постачальника.
const notifier: Notifier =
  process.env.MAIL === "smtp"
    ? new SmtpNotifier(makeTransport(), "no-reply@food.app")
    : new SendGridNotifier(process.env.SENDGRID_KEY!, "no-reply@food.app");

const dispatch = new OrderDispatch(notifier);  // ядро дістає порт, не знаючи, який адаптер
