// одна ділова операція — одна процедура, згори вниз, як рецепт
async function placeOrder(customerId: string, productId: number, qty: number): Promise<number> {
  const tx = await db.begin();                        // відкрили транзакцію: усе або нічого
  try {
    const product = await tx.get(
      "SELECT price, stock FROM products WHERE id = ?", productId);
    if (!product) throw new Error("немає такого товару");
    if (product.stock < qty) throw new Error("недостатньо на складі");

    const discount = await loyaltyDiscount(tx, customerId);   // спільна підпроцедура
    const total = product.price * qty * (1 - discount);

    const { lastID: orderId } = await tx.run(
      "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
      customerId, total);
    await tx.run(
      "INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
      orderId, productId, qty, product.price);
    await tx.run(
      "UPDATE products SET stock = stock - ? WHERE id = ?", qty, productId);

    await tx.commit();                                // усі чотири зміни доїхали разом
    return orderId;
  } catch (e) {
    await tx.rollback();                              // будь-яка невдача — відкат усього
    throw e;
  }
}
