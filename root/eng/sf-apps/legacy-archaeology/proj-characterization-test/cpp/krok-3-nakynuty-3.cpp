void CharacterizeInvoice_blackFriday() {
    // той самий вхід, але вмикаємо сезонну знижку 10%
    InvoiceCtx ctx = fixedCtx(0.0, true, dateOf(2025, 3, 15), 0.19);
    double got = computeInvoiceTotal(100.0, "DE", 3, ctx);
    EXPECT_NEAR(got, 321.30, 1e-9);     // 300 * 0.90 * 1.19 = 321.30
}

void CharacterizeInvoice_seasonalByDate() {
    // знижку НЕ форсуємо, але дата = 29 листопада -> код увімкне її сам
    InvoiceCtx ctx = fixedCtx(0.0, false, dateOf(2025, 11, 29), 0.19);
    double got = computeInvoiceTotal(100.0, "DE", 3, ctx);
    EXPECT_NEAR(got, 321.30, 1e-9);     // та сама гілка, але через КАЛЕНДАР
}

void CharacterizeInvoice_truncationBites() {
    // підбираємо вхід, де усічення копійок РЕАЛЬНО зрізає частку.
    // net=10, qty=1, знижка 3% -> 9.70; ПДВ 19% -> 11.543; усічення -> 11.54
    InvoiceCtx ctx = fixedCtx(0.03, false, dateOf(2025, 3, 15), 0.19);
    double got = computeInvoiceTotal(10.0, "XX", 1, ctx);
    EXPECT_NEAR(got, 11.54, 1e-9);      // не 11.54(3): усічення донизу спіймано
}
