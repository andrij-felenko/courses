// billing.test.ts — єдиний спосіб перевірити правило, поки все сплетено
test("рахунок за місяць", async () => {
  const db = await openTestDb();                 // контейнер із Postgres
  await db.exec("delete from orders where user_id = 7");
  await db.exec("delete from invoice_log where user_id = 7");
  await db.exec("insert into orders values (7, '2026-06', 5000, 'sale', 'paid')");
  await db.exec("insert into orders values (7, '2026-06', 900, 'sale', 'paid')");
  const out = await captureStdout(() => printMonthlyInvoice(db, 7, "2026-06"));
  expect(out.trim()).toBe("Разом до сплати: 6726.00 грн");
  const log = await db.query("select total from invoice_log where user_id = 7");
  expect(log[0].total).toBeCloseTo(6726.0);
  await db.close();
});
