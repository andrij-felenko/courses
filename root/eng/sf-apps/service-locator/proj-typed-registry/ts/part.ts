class Locator {
  private static map = new Map<string, unknown>();
  static register(key: string, value: unknown): void { Locator.map.set(key, value); }
  static get(key: string): unknown { return Locator.map.get(key); }
}

Locator.register("gateway", new StripeGateway());          // на старті програми

const gateway = Locator.get("gateway") as PaymentGateway;  // ① приведення руками, у кожній точці
gateway.charge(order.total());

const g = Locator.get("getway") as PaymentGateway;         // ② одрук: компілюється, g === undefined
g.charge(order.total());                                    //    → TypeError аж у рантаймі
