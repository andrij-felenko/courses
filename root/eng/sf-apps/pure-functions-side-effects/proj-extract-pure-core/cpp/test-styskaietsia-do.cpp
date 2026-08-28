// ── Тест ЧИСТОГО ядра: увесь тест — вхід і очікуваний вихід ──────
void test_totals() {
    Pricing p;   // дефолтна політика: tax 0.20, freeShip 500, ship 49

    // gold, кошик 1200 → обсяг >1000 дає 10%, gold дає 8%
    // 1200 · 0.90 · 0.92 = 993.6 ; податок ×1.20 = 1192.32
    // 993.6 ≥ 500 → доставка безкоштовна, тож total = 1192.32
    Order gold{1, "gold", {{600.0, 2}}};
    Totals g = computeTotals(gold, p);
    assert(std::abs(g.total - 1192.32) < 1e-6);

    // regular, кошик 200 → жодної знижки, доставка платна
    // 200 ×1.20 = 240 + 49
    Order small{2, "regular", {{200.0, 1}}};
    assert(std::abs(computeTotals(small, p).total - 289.0) < 1e-6);

    // порожній кошик → усе нулі, доставка платна
    Order empty{3, "regular", {}};
    assert(std::abs(computeTotals(empty, p).total - 49.0) < 1e-6);
}
