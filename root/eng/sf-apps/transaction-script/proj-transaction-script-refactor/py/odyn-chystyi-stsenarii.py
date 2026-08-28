def place_order(customer_id: str, product_id: int, qty: int) -> int:
    tx = db.begin()                                     # ── МЕЖА ТРАНЗАКЦІЇ: тут вона відкрита
    try:
        product = tx.execute(
            "SELECT price, stock FROM products WHERE id = ?", (product_id,)).fetchone()
        if product is None:
            raise ValueError("немає такого товару")
        if product.stock < qty:
            raise ValueError("недостатньо на складі")

        discount = loyalty_discount(tx, customer_id)    # спільна підпроцедура
        total = product.price * qty * (1 - discount)    # ← ПРАВИЛО ціни живе тут

        cur = tx.execute(
            "INSERT INTO orders (customer_id, total, status) VALUES (?, ?, 'new')",
            (customer_id, total))
        order_id = cur.lastrowid
        tx.execute(
            "INSERT INTO order_lines (order_id, product_id, qty, price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, qty, product.price))
        tx.execute(
            "UPDATE products SET stock = stock - ? WHERE id = ?", (qty, product_id))

        tx.commit()                                     # ── усі чотири зміни доїхали разом
        return order_id
    except Exception:
        tx.rollback()                                   # будь-яка невдача — відкат усього
        raise
