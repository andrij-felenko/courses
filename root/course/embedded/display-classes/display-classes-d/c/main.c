// Модель: яскравість екрана ≈ (струм LED) × (оптичне пропускання панелі).
// Приглушення підсвіткою — це просто менший середній струм LED.
float screen_nits(float led_mA, float mA_full, float nits_full) {
    return nits_full * (led_mA / mA_full);      // лінійно за струмом (спрощено)
}

const float MA_FULL = 60.0f, NITS_FULL = 300.0f;

float i_full = 60.0f;                            // повна яскравість: 60 мА
float n_full = screen_nits(i_full, MA_FULL, NITS_FULL);   // = 300 кд/м²

float i_half = 30.0f;                            // приглушили струм удвічі
float n_half = screen_nits(i_half, MA_FULL, NITS_FULL);   // = 150 кд/м²

// у бюджеті струму це прямий виграш: −30 мА постійно, поки екран увімкнено
float saved_mA = i_full - i_half;               // = 30 мА заощаджено
