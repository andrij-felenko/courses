// billing.ts — доступ до бази, правило, формат, вивід і журнал в одному тілі
import { Db } from "./db";

export async function printMonthlyInvoice(db: Db, userId: number, month: string) {
  const rows = await db.query<{ amount: number; kind: string }>(
    "select amount, kind from orders where user_id = ? and month = ? and status = 'paid'",
    [userId, month],
  );
  if (rows.length === 0) {
    console.log("Замовлень за місяць немає");
    return;
  }
  let net = 0;
  for (const r of rows) {
    if (r.kind === "refund") net -= r.amount;
    else net += r.amount;
  }
  if (net < 0) net = 0;
  if (net > 5000) net = Math.round(net * 0.95 * 100) / 100;  // знижка постійним
  const total = Math.round(net * 1.2 * 100) / 100;           // ПДВ 20 %
  const line = `Разом до сплати: ${total.toFixed(2)} грн`;
  console.log(line);
  await db.exec(
    "insert into invoice_log (user_id, month, total) values (?, ?, ?)",
    [userId, month, total],
  );
}
