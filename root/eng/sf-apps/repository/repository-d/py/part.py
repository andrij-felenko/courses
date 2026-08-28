def is_loyal_customer(customer_id: str) -> bool:
    conn = pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT total, created_at FROM orders "
            "WHERE customer_id = %s AND status = 'paid' "
            "ORDER BY created_at DESC LIMIT 3",
            (customer_id,),
        )
        orders = [Order(total, created_at) for total, created_at in cur.fetchall()]
        # одне-єдине бізнес-правило, поховане під греблею з драйвера:
        return len(orders) == 3 and all(o.total > 500 for o in orders)
    finally:
        pool.putconn(conn)
