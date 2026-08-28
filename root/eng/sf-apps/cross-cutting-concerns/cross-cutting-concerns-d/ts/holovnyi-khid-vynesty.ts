// Концерн вписаний у справу: логування переплетене з роботою
class OrderService {
  placeOrder(order: Order): Receipt {
    log.info("placeOrder: in");            // концерн
    try {
      const r = this.doPlace(order);       // справа
      log.info("placeOrder: ok");          // концерн
      return r;
    } catch (e) {
      log.error("placeOrder: err", e);     // концерн
      throw e;
    }
  }
}
