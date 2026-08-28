placeOrder(cart: Cart, card: Card): OrderResult {
  // ✗ рахує знижку — це БІЗНЕС-рішення, а не виклик підсистеми
  if (cart.total > 1000) cart.total *= 0.9;

  // ✗ вирішує, чи давати клієнтові кредит — знову бізнес-правило
  if (this.isVip(cart.email) && cart.total < this.creditLimit(cart.email)) { /* ... */ }

  // ✗ сам рахує податок за таблицею регіонів — предметна логіка
  const tax = cart.total * this.taxRateFor(cart.region);

  // ✗ веде власний стан — лічильник, кеш, історія
  this.ordersToday++;
  this.recentCarts.push(cart);

  // ...і десь тут, поміж усім цим, ще й ті чотири виклики служб
}
