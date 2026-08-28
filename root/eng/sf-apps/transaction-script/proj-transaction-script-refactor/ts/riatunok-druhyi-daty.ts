interface OrderInput {
  productId: number; qty: number; unitPrice: number; stock: number;
  discount: number; region: string;
}

class Order {
  readonly total: number;
  readonly discount: number;
  readonly lines: { productId: number; qty: number; price: number }[];

  constructor(i: OrderInput) {
    // інваріанти перевіряються ОДИН раз — у мить народження об'єкта
    if (i.qty < 1) throw new Error("кількість має бути ≥ 1");
    if (i.stock < i.qty) throw new Error("недостатньо на складі");

    const subtotal = i.unitPrice * i.qty;
    let net = subtotal * (1 - i.discount);
    const floor = regionFloor(i.region);
    // інваріант, що ЗЧІПЛЯЄ поля: чиста сума ніколи не нижча за поріг регіону
    this.discount = net < floor ? (subtotal > 0 ? 1 - floor / subtotal : 0) : i.discount;
    net = Math.max(net, floor);
    this.total = net * (1 + regionTax(i.region));
    this.lines = [{ productId: i.productId, qty: i.qty, price: i.unitPrice }];
  }
}
