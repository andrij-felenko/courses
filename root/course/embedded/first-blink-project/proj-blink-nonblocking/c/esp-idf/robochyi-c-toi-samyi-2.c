#define LED_PIN     GPIO_NUM_2
#define LED_INT     200              // блимати кожні 200 мс
#define SENSOR_INT  1000             // читати давач кожну 1000 мс

void app_main(void) {
    gpio_config_t cfg = { .pin_bit_mask = 1ULL << LED_PIN, .mode = GPIO_MODE_OUTPUT };
    gpio_config(&cfg);

    uint32_t lastBlink = 0, lastSensor = 0;
    bool ledOn = false;

    while (1) {
        uint32_t now = (uint32_t)(esp_timer_get_time() / 1000);

        // справа 1: блимання світлодіодом
        if (now - lastBlink >= LED_INT) {
            lastBlink = now;
            ledOn = !ledOn;
            gpio_set_level(LED_PIN, ledOn ? 1 : 0);
        }

        // справа 2: опитування давача — СВОЯ мітка, СВІЙ інтервал
        if (now - lastSensor >= SENSOR_INT) {
            lastSensor = now;
            float t = read_temperature();
            send_temperature(t);
        }

        // обидві гілки бачать один і той самий `now`;
        // жодна не блокує іншу; оберт триває мікросекунди
        vTaskDelay(1);
    }
}
