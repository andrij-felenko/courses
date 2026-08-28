// Знекровлена модель: замовлення нічого не вміє, лише тримає поля навстіж
class Order {
  status: string = "new";       // "new" | "paid" | "shipped" | "cancelled"
  items: Item[] = [];
  discount: number = 0;         // відсоток знижки, 0..100 — хтозна, ніхто не стереже
  total: number = 0;
}

// Уся думка — ЗЗОВНІ, у сервісі; кожен викликач тримає свій уламок правил
class OrderService {
  applyDiscount(o: Order, percent: number): void {
    o.discount = percent;        // жодної перевірки: приймуться й 500, і −20
    o.total = o.items.reduce((s, i) => s + i.price, 0) * (1 - o.discount / 100);
  }

  ship(o: Order): void {
    // тут ЗАБУЛИ перевірити, що замовлення взагалі оплачене
    o.status = "shipped";
  }
}
