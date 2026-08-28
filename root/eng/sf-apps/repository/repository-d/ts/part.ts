async function isLoyalCustomer(customerId: string): Promise<boolean> {
  const conn = await pool.getConnection();
  try {
    const rows = await conn.query(
      "SELECT total, created_at FROM orders " +
      "WHERE customer_id = ? AND status = 'paid' " +
      "ORDER BY created_at DESC LIMIT 3",
      [customerId],
    );
    const orders = rows.map(r => new Order(r.total, new Date(r.created_at)));
    // одне-єдине бізнес-правило, поховане під греблею з драйвера:
    return orders.length === 3 && orders.every(o => o.total > 500);
  } finally {
    conn.release();
  }
}
