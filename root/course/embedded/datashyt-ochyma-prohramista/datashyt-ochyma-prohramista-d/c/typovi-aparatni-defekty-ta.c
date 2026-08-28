/* Програмне розблокування шини I2C (Bus Recovery) мовою C */
void i2c_bus_recovery(void) {
    gpio_set_mode_output_od(PIN_SCL);
    gpio_set_mode_input_pullup(PIN_SDA);

    /* Генеруємо 9 тактових імпульсів на лінії SCL */
    for (int i = 0; i < 9; i++) {
        if (gpio_read(PIN_SDA) == 1) {
            break; /* Чип відпустив SDA, шина розблокована */
        }
        gpio_write(PIN_SCL, 0);
        delay_us(5);
        gpio_write(PIN_SCL, 1);
        delay_us(5);
    }

    /* Формуємо сигнал STOP: перехід SDA з 0 в 1 при SCL = 1 */
    gpio_set_mode_output_od(PIN_SDA);
    gpio_write(PIN_SDA, 0);
    delay_us(5);
    gpio_write(PIN_SCL, 1);
    delay_us(5);
    gpio_write(PIN_SDA, 1);
    delay_us(5);
}
