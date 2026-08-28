// Допоміжне: контекст із зафіксованими годинником і базою.
static InvoiceCtx fixedCtx(double disc, bool seasonal,
                           std::tm date, double vatRate) {
    InvoiceCtx c;
    c.discountRate = disc;
    c.forceSeasonal = seasonal;
    c.clock = [date]{ return date; };            // час ЗАФІКСОВАНО
    c.vat   = [vatRate](const std::string&){ return vatRate; };  // база ЗАФІКСОВАНА
    return c;
}
static std::tm dateOf(int y, int mon1based, int day) {
    std::tm t{}; t.tm_year = y - 1900; t.tm_mon = mon1based - 1; t.tm_mday = day;
    return t;
}

void CharacterizeInvoice_plainDay() {
    // net=100, qty=3, DE, БЕЗ знижок, звичайний день (15 березня), ПДВ 19%.
    InvoiceCtx ctx = fixedCtx(0.0, false, dateOf(2025, 3, 15), 0.19);
    double got = computeInvoiceTotal(100.0, "DE", 3, ctx);
    EXPECT_NEAR(got, -1.0, 1e-9);       // -1 — НАВМИСНА дурниця, хай упаде
}
