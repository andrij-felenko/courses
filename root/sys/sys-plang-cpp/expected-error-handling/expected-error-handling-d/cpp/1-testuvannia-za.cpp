TEST_CASE("Перевірка безпечного квадратного кореня", "[math]") {
    SECTION("Успішне обчислення") {
        auto res = safe_sqrt(16.0);
        REQUIRE(res.has_value());
        REQUIRE(*res == Catch::Approx(4.0));
    }
    
    SECTION("Обробка від'ємного числа") {
        auto res = safe_sqrt(-4.0);
        REQUIRE_FALSE(res.has_value());
        REQUIRE(res.error() == "Спроба обчислити квадратний корінь з від'ємного числа");
    }
}
