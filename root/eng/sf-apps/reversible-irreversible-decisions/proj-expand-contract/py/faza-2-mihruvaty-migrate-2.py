# Подвійне читання зі звірянням. Поки trust_new=False — стара авторитетна,
# нова читається лише для звіряння (тінь). Коли доказів досить — прапорець
# перемикають, і авторитетною стає нова.
def read_amount_minor(conn, order_id: int, trust_new: bool) -> int:
    row = conn.execute(
        "SELECT total, amount_minor FROM orders WHERE id = %s", (order_id,)
    ).one()
    old_as_new = int((row.total * 100).to_integral_value())  # стара, зведена до копійок

    if row.amount_minor is None:
        return old_as_new                    # ще не заповнено — падаємо на стару

    if row.amount_minor != old_as_new:       # РОЗБІЖНІСТЬ — інваріант порушено!
        metrics.increment("amount_minor.drift")
        log.error("drift order=%s old=%s new=%s",
                  order_id, old_as_new, row.amount_minor)
        return old_as_new                    # у сумніві — авторитетна стара

    return row.amount_minor if trust_new else old_as_new
