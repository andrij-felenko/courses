// Типова помилка: покажчик на не-volatile регістр або прапорець
uint32_t *uart_status = (uint32_t *)0x40013800; // Адреса USART1->SR
#define USART_SR_TXE (1 << 7)

void uart_send_byte(uint8_t byte) {
    // Очікуємо звільнення буфера передавача
    while (!(*uart_status & USART_SR_TXE)) {
        // Порожній цикл очікування
    }
    *(uint32_t *)0x40013804 = byte; // USART1->DR
}
