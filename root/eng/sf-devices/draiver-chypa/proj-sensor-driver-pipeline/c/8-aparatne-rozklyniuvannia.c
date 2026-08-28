void bsp_i2c_bus_recover(void) {
    /* 1. Перемикання пінів I2C (SCL, SDA) у режим програмного GPIO Open-Drain */
    gpio_set_mode(PIN_SCL, GPIO_OUTPUT_OD);
    gpio_set_mode(PIN_SDA, GPIO_OUTPUT_OD);
    gpio_set_high(PIN_SDA);

    /* 2. Генерація 9 імпульсів тактування SCL з перевіркою звільнення SDA */
    for (uint8_t i = 0; i < 9; ++i) {
        gpio_set_low(PIN_SCL);
        delay_us(5);
        gpio_set_high(PIN_SCL);
        delay_us(5);

        /* Якщо чип відпустив SDA, він знову бачить шину */
        if (gpio_read(PIN_SDA) == 1) {
            break;
        }
    }

    /* 3. Генерація апаратного сигналу STOP: SDA переходить з Low в High при High SCL */
    gpio_set_low(PIN_SDA);
    delay_us(5);
    gpio_set_high(PIN_SCL);
    delay_us(5);
    gpio_set_high(PIN_SDA);
    delay_us(5);

    /* 4. Повернення пінів периферійному контролеру I2C */
    gpio_set_alternate_function(PIN_SCL, AF_I2C);
    gpio_set_alternate_function(PIN_SDA, AF_I2C);
}
