// ports.ts — що звіт вимагає від світу, без згадки про базу
export interface OrdersSource {
  ordersOf(userId: number, month: string): Promise<Order[]>;
}

// sqlOrders.ts — один із можливих постачальників замовлень
export class SqlOrders implements OrdersSource {
  constructor(private db: Db) {}

  async ordersOf(userId: number, month: string): Promise<Order[]> {
    const rows = await this.db.query<{ amount: number; kind: string }>(
      "select amount, kind from orders where user_id = ? and month = ? and status = 'paid'",
      [userId, month],
    );
    return rows.map((r) => ({
      amount: r.amount,
      kind: r.kind === "refund" ? "refund" : "sale",
    }));
  }
}

// report.ts — сценарій: узяти замовлення, порахувати, скласти рядок
export async function monthlyInvoice(src: OrdersSource, userId: number, month: string) {
  const orders = await src.ordersOf(userId, month);
  if (orders.length === 0) return { total: 0, line: "Замовлень за місяць немає" };
  const total = totalDue(orders);
  return { total, line: invoiceLine(total) };
}

// main.ts — композиційний корінь: тут і тільки тут вибирають реалізації
async function main() {
  const db = await openDb(process.env.DB_URL!);
  const src = new SqlOrders(db);
  const [userId, month] = [Number(process.argv[2]), process.argv[3]];
  const { total, line } = await monthlyInvoice(src, userId, month);
  console.log(line);
  await logInvoice(db, userId, month, total);
  await db.close();
}
main();
