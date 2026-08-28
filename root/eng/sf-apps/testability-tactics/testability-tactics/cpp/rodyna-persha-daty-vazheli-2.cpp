// Підроблені джерела: курс і день задаємо ми — вхід під повним контролем.
struct FakeRate  : RateSource { double rate() override { return 40.0; } };
struct SatClock  : Clock      { bool is_weekend() override { return true; } };

void test_weekend_surcharge() {
    Order o{ .amount = 100.0 };
    FakeRate rates;  SatClock sat;
    double got = order_total(o, rates, sat);
    // 100 · 40 = 4000, вихідний → ×1.05 = 4200. Точне, відтворюване число.
    assert(std::abs(got - 4200.0) < 1e-9);
}
