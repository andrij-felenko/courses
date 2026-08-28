// ПОГАНО: прапорець просочився всередину бізнес-сервісу та повторюється в багатьох методах
class OrderProcessor {
  processOrder(order: Order, user: User) {
    if (this.flags.isEnabled("new-payment-v2", user)) {
      this.stripeV2.charge(order.amount);
    } else {
      this.legacyBank.process(order.amount);
    }
  }

  refundOrder(order: Order, user: User) {
    if (this.flags.isEnabled("new-payment-v2", user)) {
      this.stripeV2.refund(order.amount);
    } else {
      this.legacyBank.refund(order.amount);
    }
  }
}
