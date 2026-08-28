int main(void) {
    uart_rx_engine_t rx16;
    uart_rx_init(&rx16, UART_OVERSAMPLING_16X);

    printf("=== ТЕСТ 1: Фільтрація імпульсної завади (Glitch Filter) ===\n");
    /* Лінія в IDLE */
    uart_rx_tick(&rx16, 1);
    /* Короткий спад на 2 такти */
    uart_rx_tick(&rx16, 0); // Такт 0: спад (Start verify почався)
    uart_rx_tick(&rx16, 0); // Такт 1
    /* Лінія відновилася в 1 */
    for (int t = 2; t < 16; ++t) {
        uart_rx_tick(&rx16, 1);
    }
    if (rx16.last_frame.glitch_detected && rx16.state == RX_STATE_IDLE) {
        printf("✓ Успіх: заваду відфільтровано, FSM повернувся в IDLE\n\n");
    }

    printf("=== ТЕСТ 2: Мажоритарне відновлення зашумленого біта ===\n");
    /* Передача байта 0x01 (D0=1, D1..D7=0) із завадою на D0: вибірки 1, 0, 1 */
    uart_rx_init(&rx16, UART_OVERSAMPLING_16X);
    /* Старт-біт (16 нулів) */
    for (int t = 0; t < 16; ++t) uart_rx_tick(&rx16, 0);
    /* D0 (має бути 1, але на такті 8 шум = 0) */
    for (int t = 0; t < 16; ++t) {
        uint8_t pin = (t == 8) ? 0 : 1; // Вибірки: S7=1, S8=0, S9=1
        uart_rx_tick(&rx16, pin);
    }
    /* D1..D7 (чисті нулі) */
    for (int b = 1; b < 8; ++b) {
        for (int t = 0; t < 16; ++t) uart_rx_tick(&rx16, 0);
    }
    /* Стоп-біт (одиниці) */
    for (int t = 0; t < 16; ++t) uart_rx_tick(&rx16, 1);

    if (rx16.has_new_frame) {
        printf("✓ Отримано байт: 0x%02X (очікувалось 0x01)\n", rx16.last_frame.data_byte);
        printf("✓ Прапорець шуму NF: %s (очікувалось TRUE)\n", rx16.last_frame.noise_flag ? "TRUE" : "FALSE");
        printf("✓ Помилка кадру FE: %s\n", rx16.last_frame.framing_error ? "TRUE" : "FALSE");
    }

    return 0;
}
