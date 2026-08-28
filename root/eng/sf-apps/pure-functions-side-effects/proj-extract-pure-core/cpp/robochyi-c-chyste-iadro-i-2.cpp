// ── ПІСЛЯ, частина 2: ТОНКА ІМПЕРАТИВНА ОБОЛОНКА ─────────────────
// Приносить дані → кличе чисте ядро → виносить ефекти. Рішень тут нема.
double handleOrder(int orderId, Database& db, Logger& log, const Pricing& p) {
    Order order = db.loadOrder(orderId);          // ефект: читання ззовні

    Totals t = computeTotals(order, p);           // ← усе рішення тут, у чистому

    db.saveTotal(orderId, t.total);               // ефект: запис назовні
    log.info("order " + std::to_string(orderId) +
             " total=" + std::to_string(t.total));// ефект: вивід
    return t.total;
}
