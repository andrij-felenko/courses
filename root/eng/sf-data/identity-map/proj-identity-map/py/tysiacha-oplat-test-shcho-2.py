def payment_run(map_factory, rounds=1000):
    db = Db()
    db.seed(rounds)
    lost = twins = 0
    for pk in range(1, rounds + 1):
        with Session(db, map_factory) as s:
            order = s.load(Order, pk)          # гілка 1 — служба оплати
            order.status = "paid"
            same = s.load(Order, pk)           # гілка 2 — служба знижок
            same.discount = 15
            if order is not same:
                twins += 1
        # читаємо повз лічильник — це вже перевірка, а не робота застосунку
        row = db.conn.execute(
            "SELECT status, discount FROM orders WHERE id = ?", (pk,)).fetchone()
        if row["status"] != "paid" or row["discount"] != 15:
            lost += 1
    return lost, twins, db.selects
