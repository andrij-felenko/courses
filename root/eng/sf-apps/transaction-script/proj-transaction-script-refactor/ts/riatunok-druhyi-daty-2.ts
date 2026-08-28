async function placeOrder(customerId: string, productId: number, qty: number): Promise<number> {
  const tx = await db.begin();                          // ── МЕЖА ТРАНЗАКЦІЇ лишилась у сценарії
  try {
    const product = await tx.get("SELECT price, stock FROM products WHERE id = ?", productId);
    if (!product) throw new Error("немає такого товару");
    const customer = await tx.get("SELECT region FROM customers WHERE id = ?", customerId);
    const discount = await loyaltyDiscount(tx, customerId);

    const order = new Order({                            // об'єкт рахує й перевіряє — БЕЗ бази
      productId, qty, unitPrice: product.price, stock: product.stock,
      discount, region: customer.region,
    });

    const { lastID: orderId } = await tx.run(
      "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
      customerId, order.total);
    for (const l of order.lines)
      await tx.run("INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
        orderId, l.productId, l.qty, l.price);
    await tx.run("UPDATE products SET stock = stock - ? WHERE id = ?", qty, productId);

    await tx.commit();                                  // ── межа закривається тут-таки
    return orderId;
  } catch (e) { await tx.rollback(); throw e; }
}
