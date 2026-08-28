class Order {
  #items: Item[] = [];

  addItem(it: Item): void {
    if (this.#closed) throw new Error("замовлення закрите");   // правило всередині
    this.#items.push(it);
  }
  get itemCount(): number { return this.#items.length; }        // назовні — факт, не нутрощі
}
order.addItem(newItem);   // перевірка вже застосована, обійти нема як
