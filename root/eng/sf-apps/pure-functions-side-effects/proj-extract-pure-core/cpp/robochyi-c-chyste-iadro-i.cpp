// ── ПІСЛЯ, частина 1: ЧИСТЕ ЯДРО ─────────────────────────────────
// const-посилання на вхід + Pricing явним аргументом + повернення значенням.
// Ніяких db/log/cout/глобалей. Той самий вхід → той самий вихід, завжди.
Totals computeTotals(const Order& order, const Pricing& p) {
    double subtotal = 0.0;
    for (const Item& it : order.items)         // const Item& — не зіпсуємо вхід
        subtotal += it.price * it.qty;

    double volumeDisc = 0.0;
    if      (subtotal > 1000.0) volumeDisc = 0.10;
    else if (subtotal >  300.0) volumeDisc = 0.05;

    double tierDisc = 0.0;
    if      (order.customerTier == "gold")   tierDisc = 0.08;
    else if (order.customerTier == "silver") tierDisc = 0.04;

    double afterDisc = subtotal * (1.0 - volumeDisc) * (1.0 - tierDisc);
    double taxed     = afterDisc * (1.0 + p.taxRate);
    double shipping  = (afterDisc >= p.freeShipFrom) ? 0.0 : p.shipCost;

    return Totals{
        subtotal,
        subtotal - afterDisc,   // скільки всього знижено
        taxed - afterDisc,      // сам податок
        shipping,
        taxed + shipping        // підсумок
    };
}
