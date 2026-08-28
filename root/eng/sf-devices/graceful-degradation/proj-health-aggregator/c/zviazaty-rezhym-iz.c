void apply_device_mode(void) {
    static dev_mode_t s_prev = DEV_HEALTHY;
    dev_mode_t mode = health_aggregate();

    if (mode != s_prev) {
        // Перехід режиму — завжди в лог і телеметрію (деградація видима)
        const char *names[] = { "HEALTHY", "DEGRADED", "SAFE" };
        ESP_LOGW(TAG, "device mode: %s -> %s", names[s_prev], names[mode]);
        mqtt_publish("status/device", names[mode]);
        s_prev = mode;
    }

    switch (mode) {
        case DEV_HEALTHY:
            gpio_set_level(GPIO_FAULT_LED, 0);
            break;
        case DEV_DEGRADED:
            gpio_set_level(GPIO_FAULT_LED, 1);   // постійне світло — увага
            actuators_limit_power(70);           // обережніше, але працюємо
            break;
        case DEV_SAFE:
            actuators_all_off();                 // знеструмити виконавчі органи
            enter_safe_state();                  // зупинка — далі лише людина
            break;
    }
}
