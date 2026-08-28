// Катастрофічна помилка: неініціалізована структура стану
typedef struct {
    uint32_t timeout_ms;
    bool enable_crc;
    uint8_t retry_count;
} SensorConfig;

void init_sensor(void) {
    SensorConfig cfg; // УВАГА: поля містять випадкове сміття!
    cfg.timeout_ms = 100;
    // Забули ініціалізувати enable_crc та retry_count!

    // В Debug: enable_crc випадково дорівнює false (0x00)
    // В Release: enable_crc дорівнює 0xA5 (true), retry_count = 240
    // Сенсор намагається валідувати CRC, якого немає, і блокує шину
    configure_hardware(&cfg);
}
