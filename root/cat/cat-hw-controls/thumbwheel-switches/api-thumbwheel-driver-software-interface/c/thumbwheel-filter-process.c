#define DEBOUNCE_THRESHOLD 3

// Програмний дебаунсинг зчитування
void thumbwheel_filter_process(thumbwheel_driver_t *drv, uint16_t raw_frame) {
    for (uint8_t i = 0; i < drv->config.decades_count; i++) {
        // Виділення 4-бітної тетради поточного розряду
        uint8_t current_nibble = (raw_frame >> (i * 4)) & 0x0F;
        
        if (current_nibble == drv->prev_nibbles[i]) {
            if (drv->debounce_cnt[i] < DEBOUNCE_THRESHOLD) {
                drv->debounce_cnt[i]++;
                if (drv->debounce_cnt[i] == DEBOUNCE_THRESHOLD) {
                    drv->nibbles[i] = current_nibble; // Фіксація стабільного значення
                }
            }
        } else {
            drv->prev_nibbles[i] = current_nibble;
            drv->debounce_cnt[i] = 0; // Скидання лічильника при зміні стану
        }
    }
}
