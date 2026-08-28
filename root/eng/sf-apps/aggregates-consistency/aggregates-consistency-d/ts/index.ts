class Order {
  // Внутрішні частини — приватні. Ззовні до них не дотягтися.
  #lines: OrderLine[] = [];
  #discount = 0;

  addLine(product: ProductId, qty: number, price: Money): void {
    if (qty <= 0) throw new Error("кількість має бути додатною");
    this.#lines.push(new OrderLine(product, qty, price));
    // правило перевіряти не треба: додавання рядка лише збільшує суму
  }

  applyDiscount(amount: Money): void {
    if (amount.isNegative()) throw new Error("знижка не буває від'ємною");
    if (amount.greaterThan(this.subtotal()))         // ← спільне правило
      throw new Error("знижка не може перевищити суму рядків");
    this.#discount = amount;
  }

  removeLine(product: ProductId): void {
    this.#lines = this.#lines.filter(l => !l.product.equals(product));
    // прибрали рядок → сума впала → знижка могла стати завеликою:
    if (this.#discount > this.subtotal())
      this.#discount = this.subtotal();               // тримаємо правило
  }

  subtotal(): Money { return this.#lines.reduce((s, l) => s.add(l.total()), Money.ZERO); }
  total(): Money    { return this.subtotal().subtract(this.#discount); }
}
