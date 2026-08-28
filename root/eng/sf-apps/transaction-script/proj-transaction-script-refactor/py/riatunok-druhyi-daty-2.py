def place_order(customer_id: str, product_id: int, qty: int) -> int:
    tx = db.begin()                                     # ── МЕЖА ТРАНЗАКЦІЇ лишилась у сценарії
    try:
        product = tx.execute(
            "SELECT price, stock FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError("немає такого товару")
        customer = tx.execute(
            "SELECT region FROM customers WHERE id = ?", (customer_id,)).fetchone()
        discount = loyalty_discount(tx, customer_id)

        order = Order(OrderInput(                        # об'єкт рахує й перевіряє — БЕЗ бази
            product_id=product_id, qty=qty, unit_price=product.price,
            stock=product.stock, discount=discount, region=customer.region))

        cur = tx.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
            (customer_id, order.total))
        order_id = cur.lastrowid
        for l in order.lines:
            tx.execute(
                "INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
                (order_id, l["product_id"], l["qty"], l["price"]))
        tx.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))

        tx.commit()                                     # ── межа закривається тут-таки
        return order_id
    except Exception:
        tx.rollback(); raise
