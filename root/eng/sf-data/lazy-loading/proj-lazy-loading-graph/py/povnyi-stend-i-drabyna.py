def scenario_naive() -> int:
    db = Db()
    orders = [OrderLazyField(db, r) for r in db.find_all_orders()]
    for o in orders: _ = o.customer["name"]
    return db.queries

def scenario_identity_map() -> int:
    db = Db()
    imap = IdentityMap(db)
    for r in db.find_all_orders(): _ = imap.customer(r["customer_id"])["name"]
    return db.queries

def scenario_batch() -> int:
    db = Db()
    rows = db.find_all_orders()
    customers = db.find_customers([r["customer_id"] for r in rows])
    for r in rows: _ = customers[r["customer_id"]]["name"]
    return db.queries

def scenario_join() -> int:
    db = Db()
    for row in db.find_orders_join_customer(): _ = row["customer"]["name"]
    return db.queries

print("запитів  стратегія")
for run, name in [(scenario_naive,        "ліниво в циклі"),
                  (scenario_identity_map, "+ мапа тотожності"),
                  (scenario_batch,        "пакетний IN-запит"),
                  (scenario_join,         "жадібний JOIN")]:
    print(f"{run():>7}  {name}")
