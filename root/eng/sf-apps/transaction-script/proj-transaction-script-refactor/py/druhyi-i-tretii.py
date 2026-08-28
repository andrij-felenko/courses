def change_qty(order_id: int, new_qty: int) -> None:
    tx = db.begin()
    try:
        line = tx.execute(
            "SELECT product_id, price FROM order_lines WHERE order_id = ?", (order_id,)).fetchone()
        order = tx.execute(
            "SELECT customer_id FROM orders WHERE id = ?", (order_id,)).fetchone()

        discount = loyalty_discount(tx, order.customer_id)
        total = line.price * new_qty * (1 - discount)         # ← та сама формула, друга копія

        tx.execute("UPDATE order_lines SET qty = ? WHERE order_id = ?", (new_qty, order_id))
        tx.execute("UPDATE orders SET total = ? WHERE id = ?", (total, order_id))
        tx.commit()
    except Exception:
        tx.rollback(); raise
