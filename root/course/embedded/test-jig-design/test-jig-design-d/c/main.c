// Спрощена логіка: подати живлення й розрізнити кидок від короткого.
// jig_current_ma() читає струм крізь силову голку (шунт на боці джига).
bool jig_power_up_and_check(void) {
    jig_set_current_limit_ma(1500);   // стеля: вище кидка, але береже від пожежі
    jig_power_on_dut();               // увімкнути ключ живлення DUT

    uint32_t t0 = jig_millis();
    // Даємо кидку відбути своє: конденсатори мають зарядитись за INRUSH_MS.
    const uint32_t INRUSH_MS   = 50;
    const uint16_t I_SHORT_MA  = 1400; // майже стеля: якщо тут сидимо — коротке
    const uint16_t I_NORMAL_MA = 250;  // стеля робочого струму доброї плати

    // Фаза 1: перечекати кидок, але стежити, чи не сидимо на стелі надто довго.
    while ((jig_millis() - t0) < INRUSH_MS) {
        if (jig_current_ma() >= I_SHORT_MA &&
            (jig_millis() - t0) > 10) {     // на стелі довше 10 мс — це не кидок
            jig_power_off_dut();
            jig_fail("SHORT: current pinned at limit", jig_current_ma());
            return false;
        }
    }

    // Фаза 2: кидок мав минути. Тепер струм має бути робочий.
    uint16_t i_now = jig_current_ma();
    if (i_now > I_NORMAL_MA) {
        jig_power_off_dut();
        jig_fail("overcurrent after inrush", i_now);   // просідання/часткове коротке
        return false;
    }
    return true;   // живлення чисте, плата не гріється — можна шити й міряти
}
