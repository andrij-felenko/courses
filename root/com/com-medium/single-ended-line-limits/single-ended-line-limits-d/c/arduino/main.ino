/* В середовищі Arduino для сумісних ядер (наприклад, RP2040 або STM32)
 * доступне керування slew rate через прямий доступ до регістрів або API */

void setup() {
    pinMode(13, OUTPUT); // SPI SCK
    
    #if defined(ARDUINO_ARCH_RP2040)
    // Обмеження швидкості наростання на RP2040 (Raspberry Pi Pico)
    // Slew rate: 0 = повільний (Slow), 1 = швидкий (Fast)
    gpio_set_slew_rate(13, GPIO_SLEW_RATE_SLOW);
    gpio_set_drive_strength(13, GPIO_DRIVE_STRENGTH_4MA);
    #endif
}

void loop() {
    // Основний цикл обміну
}
