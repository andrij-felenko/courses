mode_t fsm_step(mode_t current, const health_t *h, float dt) {
    // ── 1. НАЙТЯЖЧЕ: втрата орієнтації б'є у внутрішній контур ──────────
    //     без достовірного крену/тангажа немає ЧИМ керувати — жоден
    //     зовнішній режим не має сенсу. Це аварія з будь-якого режиму.
    if (!debounce_imu(h->imu_ok, dt)) {
        return MODE_LAND;          // сідати наосліп краще, ніж перекинутись
    }

    // ── 2. БАТАРЕЯ: вибору не лишає, сходинка залежить від глибини ──────
    batt_level_t b = batt_classify(h->batt_volt);   // OK / LOW / CRITICAL (з гістерезисом)
    if (b == BATT_CRITICAL) {
        return MODE_LAND;          // не долетимо додому — сідай негайно тут
    }
    if (b == BATT_LOW) {
        return worse_of(current, MODE_RTL);   // час додому, але ще не аварія
    }

    // ── 3. ЗВ'ЯЗОК: пропав пульт — за планом вертаємось додому ──────────
    if (!debounce_link(h->rc_link, dt)) {
        return worse_of(current, MODE_RTL);
    }

    // ── 4. НАЙЛЕГШЕ: втрата GNSS чіпає лише зовнішній контур ────────────
    //     апарат не падає — лише не знає, ДЕ він. Знімаємо навігацію.
    if (!h->gnss_ok) {
        return worse_of(current, MODE_LOITER);
    }

    // ── 5. усе здорове: тримаємо поточний режим (можливе повернення) ────
    return current;
}
