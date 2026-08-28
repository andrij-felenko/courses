void run_unit_tests() {
    using namespace rf_propagation;
    AtmosphericCalculator calc;

    // Тест 1: Смуга кисню 60 ГГц (перевірка високих втрат O2)
    LinkConfig cfg60{.frequency_ghz = 60.0, .distance_km = 1.0, .humidity_g_m3 = 7.5};
    auto report60 = calc.evaluate(cfg60);
    // Питоме поглинання O2 має бути у межах 14.0 - 17.0 дБ/км
    assert(report60.gamma_o2_db_km >= 14.0 && report60.gamma_o2_db_km <= 17.0);

    // Тест 2: Низька частота 2 ГГц (перевірка малого дощового згасання)
    LinkConfig cfg2{.frequency_ghz = 2.0, .distance_km = 10.0, .rain_rate_mm_h = 50.0};
    auto report2 = calc.evaluate(cfg2);
    // Питоме дощове згасання не повинно перевищувати 0.1 дБ/км
    assert(report2.gamma_rain_db_km < 0.1);

    std::cout << "[PASSED] Усі юніт-тести атмосферного калькулятора успішно виконано!\n";
}
