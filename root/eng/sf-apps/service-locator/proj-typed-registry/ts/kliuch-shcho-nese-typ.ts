// Токен — звичайне значення, але параметризоване типом служби, яку він позначає.
class Token<T> {
  // Поле-фантом: у типі є, у рантаймі — нема (declare не породжує жодного коду).
  // Без згадки T компілятор вважав би Token<A> і Token<B> взаємозамінними; поле це лікує.
  declare readonly _service: T;
  constructor(readonly description: string) {}
}

class ServiceRegistry {
  private map = new Map<Token<unknown>, unknown>();

  // register вимагає, щоб value був саме тим T, що обіцяє токен.
  register<T>(token: Token<T>, value: T): void {
    this.map.set(token, value);
  }

  // resolve повертає T, не any. Єдине приведення заховане ТУТ і виправдане register.
  resolve<T>(token: Token<T>): T {
    if (!this.map.has(token)) {
      throw new Error(`Служба не зареєстрована: ${token.description}`);
    }
    return this.map.get(token) as T;
  }
}

// Токени — константи в одному місці. Ключ — це вони, а не рядок.
const GATEWAY = new Token<PaymentGateway>("payment-gateway");
const CLOCK   = new Token<Clock>("clock");

registry.register(GATEWAY, new StripeGateway());   // ok: StripeGateway is PaymentGateway
// registry.register(GATEWAY, new SystemClock());  // ✗ компілятор: Clock не є PaymentGateway

const gateway = registry.resolve(GATEWAY);         // тип: PaymentGateway, без приведення
// registry.resolve(GATEWY);                        // ✗ компілятор: Cannot find name 'GATEWY'
