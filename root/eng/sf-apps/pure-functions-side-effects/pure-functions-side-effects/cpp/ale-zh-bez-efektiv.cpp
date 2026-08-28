// НЕЧИСТА оболонка: тонка, лише приносить дані й виносить ефект
void handleCheckout(OrderId id) {
    Order order    = db.load(id);              // ефект: читання ззовні
    double taxRate = config.taxRate();         // ефект: читання ззовні

    double total = totalPrice(order.items, taxRate);  // ← ЧИСТЕ ядро: усе рішення тут

    db.saveTotal(id, total);                   // ефект: запис назовні
    log.info("total for {} = {}", id, total);  // ефект: вивід
}
