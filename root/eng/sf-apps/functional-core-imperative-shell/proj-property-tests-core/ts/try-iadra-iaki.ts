type Item = { price: number; qty: number };          // ціна в копійках
type Order = { preDiscount: number; total: number; discounted: boolean };

function priceOrder(items: Item[], taxRate: number): Order {
  let subtotal = 0;
  for (const it of items) subtotal += it.price * it.qty;
  const preDiscount = subtotal * (1 + taxRate);        // сума з податком, ДО знижки
  const discounted = preDiscount > 1000;               // знижка за великий чек
  const total = discounted ? preDiscount * 0.95 : preDiscount;
  return { preDiscount, total, discounted };
}
