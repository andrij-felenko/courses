# АНТИПРИКЛАД: ручні commit/rollback, розсипані по методу
def place_order(self, cmd):
    conn = db.connect()
    conn.execute("BEGIN")
    try:
        cart = load_cart(conn, cmd.cart_id)
        order = cart.checkout()
        charge(order.total(), cmd.card)      # а якщо кине ТУТ?
        save(conn, order)
        conn.execute("COMMIT")               # легко забути на якійсь гілці
    except Exception:
        conn.execute("ROLLBACK")             # а якщо кине сам ROLLBACK?
        raise
    finally:
        conn.close()                         # забудеш це — витік з'єднань
