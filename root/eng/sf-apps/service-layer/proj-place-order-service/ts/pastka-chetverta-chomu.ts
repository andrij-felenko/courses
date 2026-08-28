// АНТИПРИКЛАД: сервіс тримає стан поточної операції в полі
class OrderService {
  private currentOrder!: Order;          // ← спільне поле — біда під навантаженням

  async placeOrder(cmd: PlaceOrderCommand): Promise<OrderDto> {
    const cart = await this.orders.loadCart(cmd.cartId);
    this.currentOrder = cart.checkout();  // запит B перезапише це поле…
    await this.payments.charge(this.currentOrder.total(), cmd.card, cmd.idempotencyKey);
    await this.orders.save(this.currentOrder);   // …і запит A збереже ЧУЖЕ замовлення
    return OrderDto.from(this.currentOrder);
  }
}
