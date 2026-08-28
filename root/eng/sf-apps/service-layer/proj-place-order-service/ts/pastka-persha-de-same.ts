// АНТИПРИКЛАД: ручні commit/rollback, розсипані по методу
async placeOrder(cmd: PlaceOrderCommand): Promise<OrderDto> {
  const conn = await db.connect();
  await conn.query("BEGIN");
  try {
    const cart = await loadCart(conn, cmd.cartId);
    const order = cart.checkout();
    await charge(order.total(), cmd.card);   // а якщо кине ТУТ?
    await save(conn, order);
    await conn.query("COMMIT");              // легко забути на якійсь гілці
  } catch (e) {
    await conn.query("ROLLBACK");            // а якщо кине сам ROLLBACK?
    throw e;
  } finally {
    conn.release();                          // а якщо забути це — витік з'єднань
  }
}
