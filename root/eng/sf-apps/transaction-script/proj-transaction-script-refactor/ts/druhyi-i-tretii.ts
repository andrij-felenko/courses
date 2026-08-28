async function changeQty(orderId: number, newQty: number): Promise<void> {
  const tx = await db.begin();
  try {
    const line = await tx.get(
      "SELECT product_id, price FROM order_lines WHERE order_id = ?", orderId);
    const order = await tx.get(
      "SELECT customer_id FROM orders WHERE id = ?", orderId);

    const discount = await loyaltyDiscount(tx, order.customer_id);
    const total = line.price * newQty * (1 - discount);     // ← та сама формула, друга копія

    await tx.run("UPDATE order_lines SET qty = ? WHERE order_id = ?", newQty, orderId);
    await tx.run("UPDATE orders SET total = ? WHERE id = ?", total, orderId);
    await tx.commit();
  } catch (e) { await tx.rollback(); throw e; }
}
