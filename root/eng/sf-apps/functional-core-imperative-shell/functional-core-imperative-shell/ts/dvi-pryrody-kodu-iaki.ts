async function checkout(cartId: string): Promise<void> {
  const cart = await db.loadCart(cartId);        // дія: читання
  const rate = await config.taxRate();           // дія: читання

  let total = 0;                                  // ↓ рішення переплетене з дією
  for (const it of cart.items) total += it.price * it.qty;
  total *= 1 + rate;
  if (total > 1000) total *= 0.95;               // знижка за великий чек

  await db.saveOrder(cartId, total);             // дія: запис
  await mailer.sendReceipt(cart.email, total);   // дія: запис
}
