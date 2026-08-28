void thermostat_hw_init(void) {
    gpio_config_t out = {
        .pin_bit_mask = 1ULL << PIN_SSR,
        .mode = GPIO_MODE_OUTPUT,
    };
    gpio_config(&out);
    gpio_set_level(PIN_SSR, 0);

    gpio_config_t in = {
        .pin_bit_mask = 1ULL << PIN_ZC,
        .mode = GPIO_MODE_INPUT,
        .intr_type = GPIO_INTR_POSEDGE,   // фронт від оптрона = нуль мережі
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&in);

    gpio_install_isr_service(0);
    gpio_isr_handler_add(PIN_ZC, (gpio_isr_t)zc_isr, NULL);
}

// Задати бажану потужність (0..1000). Викликає регулятор температури.
void thermostat_set_power(int32_t permille) {
    if (permille < 0)    permille = 0;
    if (permille > 1000) permille = 1000;
    g_power_permille = permille;   // 32-бітний запис атомарний на ESP32
}
