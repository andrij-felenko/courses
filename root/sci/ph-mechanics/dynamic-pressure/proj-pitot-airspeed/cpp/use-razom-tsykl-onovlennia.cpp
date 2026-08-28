typedef struct {
    float offset;     // нуль-зсув (Па), знятий на землі
    Ema   lp;         // ФНЧ на знаковому перепаді тиску
    float q_min;      // поріг зони нечутливості (Па)
    bool  valid;      // чи можна вірити поточному числу
    float eas, tas;   // останні швидкості (м/с)
} Airspeed;

void airspeed_update(Airspeed *s, float dp_raw,
                     float p_static, float T_kelvin, float dt) {
    // 1. зняти нуль-зсув (він повзе з температурою — періодично перезаміряти на землі)
    float dp = dp_raw - s->offset;

    // 2. ФНЧ на ЗНАКОВОМУ перепаді — ДО відсікання, щоб симетричний шум усереднився в нуль
    float alpha = dt / (0.05f + dt);            // τ ≈ 50 мс
    dp = ema_update(&s->lp, dp, alpha);

    // 3. зона нечутливості: нижче порогу q крихітний і тоне в шумі
    if (dp < s->q_min) { s->valid = false; s->eas = s->tas = 0.0f; return; }
    s->valid = true;

    // 4. густина з реального статичного тиску й температури
    float rho = air_density(p_static, T_kelvin);

    // 5. приладова (ρ₀) і справжня (реальна ρ) швидкості
    s->eas = sqrtf(2.0f * dp / RHO_SSL);
    s->tas = sqrtf(2.0f * dp / rho);

    // 6. на великих дозвукових — стислива поправка (інакше TAS завищена)
    if (s->tas > 80.0f)
        s->tas = tas_compressible(dp, p_static, T_kelvin);
}
