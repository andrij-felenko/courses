type Money = number; // копійки

interface PriceCatalog { priceOf(sku: string): Money; }
interface OrderRepository {
  save(order: Order): void;
  find(id: string): Order | undefined;
}
interface Notifier { sendConfirmation(email: string, total: Money): void; }
interface AuditLog { record(event: string, id: string): void; }

interface Line  { sku: string; qty: number; }
interface Order { id: string; email: string; total: Money; status: "placed"; }
interface PlaceOrderCmd { orderId: string; email: string; items: Line[]; }

interface Deps {
  catalog: PriceCatalog; repo: OrderRepository;
  notifier: Notifier;    audit: AuditLog;
}

function placeOrder(cmd: PlaceOrderCmd, deps: Deps): Order {
  const total = cmd.items.reduce(
    (sum, line) => sum + deps.catalog.priceOf(line.sku) * line.qty, 0);
  const order: Order = { id: cmd.orderId, email: cmd.email, total, status: "placed" };
  deps.repo.save(order);
  deps.notifier.sendConfirmation(order.email, total);
  deps.audit.record("order_placed", order.id);
  return order;
}
