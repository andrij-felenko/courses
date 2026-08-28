// ESP-IDF, ESP32: GPIO як маркер фаз для профілювальника
#define MARK_GPIO   25                 // вільний вивід → цифровий вхід приладу
#define MARK_MASK   (1u << MARK_GPIO)

static inline void mark_high(void) { REG_WRITE(GPIO_OUT_W1TS_REG, MARK_MASK); }
static inline void mark_low (void) { REG_WRITE(GPIO_OUT_W1TC_REG, MARK_MASK); }

void measure_cycle(void) {
    gpio_set_direction(MARK_GPIO, GPIO_MODE_OUTPUT);

    mark_high();                        // ── межа фази: почалася передача
    wifi_send(packet, len);
    mark_low();                         // ── фаза скінчилася

    sensor_read();                      // ця фаза без маркера — поки нецікава
}
