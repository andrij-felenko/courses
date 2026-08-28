from decimal import Decimal

# Подвійний запис: обидві форми в одному операторі, узгоджено.
# total тут — Decimal (точні гривні); копійки — цілим, без float.
def create_order(conn, customer_id: int, total: Decimal) -> None:
    amount_minor = int((total * 100).to_integral_value())   # рівно round(total·100)
    conn.execute(
        "INSERT INTO orders (customer_id, total, amount_minor) "
        "VALUES (%s, %s, %s)",
        (customer_id, total, amount_minor),
    )
