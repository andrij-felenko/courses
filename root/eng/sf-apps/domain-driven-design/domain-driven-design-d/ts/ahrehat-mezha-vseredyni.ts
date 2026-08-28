// Корінь агрегату — єдині двері; позиції змінюють ЛИШЕ через замовлення
class Order {                      // корінь
  private lines: OrderLine[] = []; // внутрішні частини — закриті

  addLine(product: ProductId, qty: number, price: Money): void {
    if (this.isPlaced) throw new DomainError("не можна міняти оформлене замовлення");
    this.lines.push(new OrderLine(product, qty, price));
    // інваріант «сума = сумі позицій» тримається тут і тільки тут
  }

  total(): Money {
    return this.lines.reduce((s, l) => s.plus(l.subtotal()), Money.zero());
  }
}
