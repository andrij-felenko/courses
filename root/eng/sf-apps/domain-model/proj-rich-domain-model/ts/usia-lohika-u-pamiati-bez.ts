describe("оформлення замовлення — уся логіка в пам'яті", () => {
  it("постійний клієнт дістає знижку, а склад меншає", () => {
    const laptop = new Product("SKU-1", Money.of(3_000_000, "UAH"), 5);  // 30 000.00, 5 шт
    const gold = new Customer("C-1", "gold");

    const order = new Order("O-1", "C-1");
    order.addLine(laptop, 2);
    order.place(gold);

    expect(order.status).toBe("placed");
    expect(order.total().equals(Money.of(5_400_000, "UAH"))).toBe(true);  // 60 000 − 10%
    expect(laptop.stock()).toBe(3);                                       // 5 − 2
  });

  it("вартові не пускають неможливий стан", () => {
    const reg = new Customer("C-1", "regular");

    const empty = new Order("O-2", "C-1");
    expect(() => empty.place(reg)).toThrow(DomainError);        // порожнє оформити не можна

    const order = new Order("O-3", "C-1");
    order.addLine(new Product("SKU-1", Money.of(1000, "UAH"), 10), 1);
    expect(() => order.ship()).toThrow(DomainError);           // чернетку не відвантажити
    order.place(reg);
    expect(() => order.place(reg)).toThrow(DomainError);       // оформити двічі — не можна
  });
});
