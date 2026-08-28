// Конфіги — у const (лягають у ПЗП). Один конфіг = один тип давача.
static const fd_config_t CFG_BARO = {
    .min = 300.0f, .max = 1100.0f,   // гПа: фізичні межі на Землі
    .max_step = 5.0f,                // за крок (20 мс) тиск не стрибне більше
    .timeout_ms = 100u,              // барометр шле ~50 Гц → 20 мс; 100 мс = тривога
    .eps = 0.03f,                    // власний шум барометра ~0.02 гПа
    .stuck_limit = 50u,              // 50 відліків (~1 с) без руху — завмер
    .trip_count = 3u,                // 3 погані поспіль → не вірю
    .heal_count = 25u,               // 25 добрих поспіль → знову вірю
};

static fd_channel_t baro;            // стан цього конкретного барометра

void sensors_init(void) {
    fd_init(&baro, &CFG_BARO);
}

// Викликається на кожен новий відлік барометра.
void on_baro_sample(float hpa, uint32_t now_ms) {
    fd_update(&baro, hpa, now_ms);
    if (fd_is_valid(&baro)) {
        altitude_from_pressure(hpa);          // канал живий — користуємось
    } else {
        // Канал відкинуто. Старший код вирішує запасний хід:
        log_fault("baro", fd_reason(&baro));  // у лог — ЧОМУ впав
        altitude_hold_last();                 // коротко тримаємо останнє добре
    }
}
