// Порти — усе, з чим сервіс говорить, є абстракцією (DIP).
// Реалізації (Postgres, Stripe, SMTP) живуть деінде й підставляються ззовні.
interface OrderRepository {
  loadCart(cartId: CartId): Promise<Cart>;
  save(order: Order): Promise<void>;
}
interface PaymentGateway {
  // key — ключ ідемпотентності: шлюз сам не спише двічі за тим самим ключем
  charge(amount: Money, card: CardToken, key: string): Promise<PaymentId>;
}
interface Mailer {
  sendConfirmation(order: Order): Promise<void>;
}
// Журнал уже виконаних операцій — серце захисту від подвійного кліку
interface IdempotencyStore {
  find(key: string): Promise<OrderDto | null>;   // уже робили цей ключ?
  remember(key: string, result: OrderDto): Promise<void>;
}
interface TransactionManager {
  run<T>(work: () => Promise<T>): Promise<T>;     // BEGIN … COMMIT / ROLLBACK
}

// Вхідний намір і вихідна виписка — плаский DTO на межі, не голий домен
interface PlaceOrderCommand {
  readonly cartId: CartId;
  readonly card: CardToken;
  readonly idempotencyKey: string;   // згенерований КЛІЄНТОМ, не сервером
}
