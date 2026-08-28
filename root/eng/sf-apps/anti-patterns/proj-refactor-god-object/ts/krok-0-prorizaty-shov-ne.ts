class OrderManager {
  placeOrder(cart: Cart, user: User): number {
    if (cart.items.length === 0) throw new Error("порожній кошик");
    for (const it of cart.items)
      if (it.qty <= 0) throw new Error("хибна кількість");

    let total = cart.items.reduce((s, it) => s + it.price * it.qty, 0);
    if (user.isVip) total *= 0.9;

    const conn = this.openDb();                   // ← було db.connect()
    conn.execute("INSERT INTO orders(user_id, total) VALUES(?, ?)", user.id, total);

    const smtp = this.openSmtp();                 // ← було new Smtp("mail.local")
    smtp.send("shop@x", user.email, `Замовлення на ${total} прийнято`);
    return total;
  }

  // два шви — і більше нічого нового
  protected openDb(): Conn { return db.connect(); }
  protected openSmtp(): Smtp { return new Smtp("mail.local"); }
}
