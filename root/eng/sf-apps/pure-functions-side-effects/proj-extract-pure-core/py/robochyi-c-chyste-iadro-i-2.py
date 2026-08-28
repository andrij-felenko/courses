# ── ПІСЛЯ, частина 2: ТОНКА ІМПЕРАТИВНА ОБОЛОНКА ─────────────────
# Приносить дані → кличе чисте ядро → виносить ефекти. Рішень тут нема.
def handle_order(order_id: int, db: Database, log: Logger, p: Pricing) -> float:
    order = db.load_order(order_id)               # ефект: читання ззовні

    t = compute_totals(order, p)                  # ← усе рішення тут, у чистому

    db.save_total(order_id, t.total)              # ефект: запис назовні
    log.info(f"order {order_id} total={t.total}") # ефект: вивід
    return t.total
