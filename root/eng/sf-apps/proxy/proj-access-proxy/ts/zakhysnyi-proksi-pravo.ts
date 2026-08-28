class AccessDenied extends Error {}   // окремий тип, щоб клієнт міг його впіймати

class ProtectedOrderService implements OrderService {
  constructor(
    private real: OrderService,        // кого захищаємо (делегат)
    private user: User,                // від чийого імені йдуть виклики
  ) {}

  private require(permission: string): void {
    if (!this.user.can(permission)) {  // одна точка перевірки для всіх методів
      throw new AccessDenied(`${this.user.name}: немає права ${permission}`);
    }
  }

  getOrder(id: string): Order {
    this.require("orders:read");        // спершу право...
    return this.real.getOrder(id);      // ...тоді делегуємо
  }
  placeOrder(order: Order): string {
    this.require("orders:write");
    return this.real.placeOrder(order);
  }
  cancelOrder(id: string): void {
    this.require("orders:cancel");
    this.real.cancelOrder(id);
  }
}
