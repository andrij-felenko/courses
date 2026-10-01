typedef struct {
    uint32_t timestamp_ms;     // Час події в мілісекундах
    uint16_t peak_amplitude;   // Максимальна амплітуда удару
    uint8_t intensity_percent; // Відносна інтенсивність (0-100%)
} knock_event_t;

typedef void (*knock_callback_t)(const knock_event_t *event);

uint16_t piezo_read_raw(const piezo_driver_t *driver) {
    return 0; // Повернення поточного аналогового виміру
}

bool piezo_poll_event(piezo_driver_t *driver, knock_event_t *event) {
    return false; // Перевірка події в черзі
}
