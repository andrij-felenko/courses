def batch_run(map_factory, rows=200_000):
    db = Db()
    db.seed(rows)
    peak = 0
    with Session(db, map_factory) as s:
        for pk in range(1, rows + 1):
            order = s.load(Order, pk)
            if pk % 1000 == 0:
                order.status = "paid"        # кожен тисячний — брудний
            peak = max(peak, len(s.identity_map))
        pinned = len(s._uow._dirty)           # скільки об'єктів тримає одиниця роботи
    return peak, pinned, db.writes
