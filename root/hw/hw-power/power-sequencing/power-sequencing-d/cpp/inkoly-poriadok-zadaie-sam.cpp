// Вивід EN кожного перетворювача керує його шиною: 1 — увімкнено.
#define EN_SENSORS  GPIO_PIN(B, 0)   // шина давачів, 1.8 В
#define EN_RADIO    GPIO_PIN(B, 1)   // шина радіо, 3.3 В

void power_up_sequence(void) {
    gpio_low(EN_SENSORS);
    gpio_low(EN_RADIO);              // старт: усе вимкнено

    gpio_high(EN_SENSORS);           // 1) перша шина
    delay_ms(5);                     //    пауза на усталення й inrush

    gpio_high(EN_RADIO);             // 2) друга шина — лише тепер
    delay_ms(5);

    radio_enable_interface();        // 3) дозвіл на обмін — останнім
}
