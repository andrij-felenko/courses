// ЦИКЛ-ДИСПЕТЧЕР: закритий. Не знає жодного виду знижки поіменно.
// Додавання нових видів його НЕ торкається.
long apply_discount(DiscountKind kind, long cart_total, const void *params) {
    if (kind < 0 || kind >= DISC_COUNT)      // вихід за межі таблиці — ловимо
        return 0;                             // невідомий вид: знижки нема
    DiscountFn fn = DISCOUNT_TABLE[kind];    // взяли обробник за індексом
    if (fn == NULL)                           // рядок є, а обробник не заповнено
        return 0;
    return fn(cart_total, params);           // викликали, не знаючи, хто це
}
