// Шов: обіцянка мовою клієнта, без натяку на пошту чи чергу
interface Notifier {
  notify(to: string, message: string): void;
}

// Стара реалізація тепер лише виконує обіцянку
class LegacyMailerNotifier implements Notifier {
  private mailer = new LegacyMailer();
  notify(to: string, message: string) {
    this.mailer.sendMail(to, message);
  }
}

class OrderService {
  constructor(private notifier: Notifier) {}   // залежність від шва, не від деталі
  placeOrder(order: Order) {
    // ...бізнес-логіка...
    this.notifier.notify(order.email, "Замовлення прийнято");
  }
}
