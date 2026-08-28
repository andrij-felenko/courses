void i2c_bus_recovery_clear(void) {
    /* 1. Переведення пінів у GPIO Open-Drain */
    gpio_set_mode_open_drain(PIN_SCL);
    gpio_set_mode_open_drain(PIN_SDA);
    gpio_write(PIN_SCL, 1);
    gpio_write(PIN_SDA, 1);

    /* 2. Якщо SDA утримується веденим пристроєм у нулі */
    if (gpio_read(PIN_SDA) == 0) {
        for (uint8_t i = 0; i < 9; i++) {
            gpio_write(PIN_SCL, 0);
            delay_us(5);
            gpio_write(PIN_SCL, 1);
            delay_us(5);
            /* Якщо ведений відпустив лінію — виходимо достроково */
            if (gpio_read(PIN_SDA) == 1) {
                break;
            }
        }
        /* 3. Генерація умови STOP */
        gpio_write(PIN_SDA, 0);
        delay_us(5);
        gpio_write(PIN_SCL, 1);
        delay_us(5);
        gpio_write(PIN_SDA, 1);
        delay_us(5);
    }

    /* 4. Повернення до апаратної периферії */
    i2c_peripheral_reinit();
}
