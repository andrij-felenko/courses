/* Процедура відновлення заблокованої шини I2C */
void i2c_bus_recover_gpio(uint8_t scl_pin, uint8_t sda_pin) {
    /* 1. Налаштування пінів як Open-Drain GPIO */
    gpio_set_mode(scl_pin, GPIO_MODE_OUTPUT_OD);
    gpio_set_mode(sda_pin, GPIO_MODE_INPUT);

    /* 2. Генерація 9 тактів SCL для виштовхування байта зі slave */
    for (int i = 0; i < 9; i++) {
        if (gpio_get_level(sda_pin) == 1) {
            break; /* Slave відпустив лінію SDA */
        }
        gpio_set_level(scl_pin, 0);
        delay_us(5);
        gpio_set_level(scl_pin, 1);
        delay_us(5);
    }

    /* 3. Генерація умови STOP вручну */
    gpio_set_mode(sda_pin, GPIO_MODE_OUTPUT_OD);
    gpio_set_level(sda_pin, 0);
    delay_us(5);
    gpio_set_level(scl_pin, 1);
    delay_us(5);
    gpio_set_level(sda_pin, 1);
    delay_us(5);
}
