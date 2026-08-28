typedef struct {
    uint8_t  tec;
    uint8_t  rec;
    bool     is_bus_off;
    bool     is_passive;
    uint32_t recovery_timer_ms;
    uint32_t backoff_delay_ms;
} health_can_monitor_state_t;

uint16_t health_can_evaluate_health(health_can_monitor_state_t *can_state, uint32_t dt_ms) {
    if (!can_state) return 0;

    if (can_state->is_bus_off) {
        can_state->recovery_timer_ms += dt_ms;
        if (can_state->recovery_timer_ms >= can_state->backoff_delay_ms) {
            // Спроба програмного скидання Bus-off
            can_state->recovery_timer_ms = 0;
            if (can_state->backoff_delay_ms < 5000) {
                can_state->backoff_delay_ms *= 2; // Збільшення паузи
            }
        }
        return 0; // Повна відмова шини
    }

    // Скидання затримки при нормальній роботі
    can_state->backoff_delay_ms = 100;
    can_state->recovery_timer_ms = 0;

    uint8_t max_err = (can_state->tec > can_state->rec) ? can_state->tec : can_state->rec;

    if (max_err < 32) {
        return 1000;
    }
    if (max_err >= 128) {
        return 200; // Error Passive
    }

    // Інтерполяція між 32 помилками (1000) та 128 помилками (200)
    return (uint16_t)(1000 - ((uint32_t)(max_err - 32) * 800) / (128 - 32));
}
