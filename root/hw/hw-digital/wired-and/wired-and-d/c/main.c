// Оцінка фронту одиниці для шини wired-AND і перевірка, чи встигає біт.
// Формули прямо з RC: t_rise ≈ k·Rp·Cbus, де k покриває підйом до порогу.
float rc_rise_ns(float Rp_ohm, float Cbus_pF, float k) {
    float tau_ns = Rp_ohm * (Cbus_pF * 1e-12f) * 1e9f;  // τ у наносекундах
    return k * tau_ns;                                   // час до порогу «1»
}

int bit_fits(float bit_period_ns, float rise_ns) {
    // лишаємо запас: фронт має вкластися приблизно в третину біта
    return rise_ns < bit_period_ns * 0.33f;
}

// приклад: Rp = 4.7 кОм, Cbus = 100 пФ, k ≈ 2.2 (підйом до ~0.7·VDD)
// rc_rise_ns(4700, 100, 2.2f) ≈ 1034 нс → на 1 МГц (1000 нс/біт) не влазить.
