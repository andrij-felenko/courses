conn = connect("shop.db")

with transaction(conn):                  # межу відкриває сценарій
    orders = OrderMapper(conn)
    stock = StockMapper(conn)            # той самий conn — та сама транзакція

    order = orders.find_by_id(7)
    if order is None:
        raise LookupError("нема замовлення 7")

    order.cancel()                       # домен вирішує, чи можна
    orders.update(order)
    stock.release(order.lines)
