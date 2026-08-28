// ВСЕ в обробнику — логіку не дістати тестом окремо:
volatile uint8_t rx_state;
void UART_ISR_bad(void) {
    uint8_t b = UART_DATA;        // читаємо залізний регістр
    if (b == 0x7E) rx_state = 1;  // ...а тут уже чиста логіка, замурована в ISR
    else if (rx_state == 1) { /* ... */ }
}

// ВІДОКРЕМЛЕНО: логіка — звичайна функція, обробник лише годує її байтом
uint8_t frame_step(uint8_t state, uint8_t b) {
    if (b == 0x7E) return 1;      // початок кадру
    if (state == 1) return 2;     // перший байт тіла
    return state;
}
void UART_ISR(void) {             // тонка обгортка: лише міст до заліза
    rx_state = frame_step(rx_state, UART_DATA);
}

// тепер логіку ганяємо на хості як завгодно ретельно:
void test_frame_sync(void) {
    TEST_ASSERT_EQUAL_UINT8(1, frame_step(0,    0x7E)); // маркер → синхронізувалися
    TEST_ASSERT_EQUAL_UINT8(2, frame_step(1,    0x10)); // далі — перший байт тіла
    TEST_ASSERT_EQUAL_UINT8(0, frame_step(0,    0x10)); // байт без маркера → стоїмо
}
