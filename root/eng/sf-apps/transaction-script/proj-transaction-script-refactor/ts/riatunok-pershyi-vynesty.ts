type Priced = { total: number; discount: number };

// чиста функція: жодної бази, лише правило ціни в одному місці
function priceOrder(unitPrice: number, qty: number, discount: number, region: string): Priced {
  const subtotal = unitPrice * qty;
  let net = subtotal * (1 - discount);
  const floor = regionFloor(region);
  if (net < floor) {                        // поріг тепер існує РІВНО ТУТ
    net = floor;
    discount = subtotal > 0 ? 1 - floor / subtotal : 0;   // підрізана знижка
  }
  const total = net * (1 + regionTax(region));
  return { total, discount };
}

// усі три сценарії тепер кличуть одне:
const { total } = priceOrder(product.price, qty, await loyaltyDiscount(tx, customerId), region);
