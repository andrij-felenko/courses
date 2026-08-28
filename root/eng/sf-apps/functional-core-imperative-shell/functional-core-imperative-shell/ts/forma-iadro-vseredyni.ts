// ── ЯДРО: чисте, нічого не читає й не пише, лише рахує ──
type Order = { total: number; discounted: boolean };

function priceOrder(items: Item[], taxRate: number): Order {
  let total = 0;
  for (const it of items) total += it.price * it.qty;
  total *= 1 + taxRate;
  const discounted = total > 1000;
  if (discounted) total *= 0.95;
  return { total, discounted };
}

// ── ОБОЛОНКА: тонка, лише возить дані; жодного рішення ──
async function checkout(cartId: string): Promise<void> {
  const cart = await db.loadCart(cartId);          // принести
  const rate = await config.taxRate();             // принести

  const order = priceOrder(cart.items, rate);      // ← усе рішення тут, у ядрі

  await db.saveOrder(cartId, order.total);         // винести
  await mailer.sendReceipt(cart.email, order.total); // винести
}
