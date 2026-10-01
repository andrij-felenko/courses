typedef struct {
    uint16_t threshold_delta;  // Зсув порогу над базовою лінією
    uint32_t blanking_ms;      // Інтервал блокування в мілісекундах
    uint32_t last_trigger_ms;  // Час останнього спрацьовування
} piezo_filter_t;

void piezo_set_threshold(piezo_filter_t *filter, uint16_t delta) {
    if (filter) {
        filter->threshold_delta = delta;
    }
}

void piezo_set_blanking_ms(piezo_filter_t *filter, uint32_t blanking_ms) {
    if (filter) {
        filter->blanking_ms = blanking_ms;
    }
}
