// ДО: один метод валідує, рахує ціну, пише в базу й шле лист.
// Чотири причини змінюватись зрощені в одному місці.
class OrderManager {
  placeOrder(cart: Cart, user: User): number {
    if (cart.items.length === 0)                 // 1) перевірка
      throw new Error("порожній кошик");
    for (const it of cart.items)
      if (it.qty <= 0) throw new Error("хибна кількість");

    let total = cart.items.reduce((s, it) => s + it.price * it.qty, 0); // 2) ціна
    if (user.isVip) total *= 0.9;

    const conn = db.connect();                    // 3) запис у базу
    conn.execute("INSERT INTO orders(...) VALUES(...)", user.id, total);

    const smtp = new Smtp("mail.local");          // 4) сповіщення
    smtp.send("shop@x", user.email, `Замовлення на ${total} прийнято`);
    return total;
  }
}
