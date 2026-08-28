/* Допоміжна функція драйвера UART (низький рівень) */
void uart_send_byte(uint8_t byte) {
    __disable_irq();
    /* Запис байта в апаратний буфер FIFO */
    UART1->DR = byte;
    __enable_irq(); // ПОМИЛКА: безумовне увімкнення переривань!
}

/* Високорівнева функція відправки цілого пакету */
void telemetry_send_packet(const uint8_t *payload, size_t len) {
    __disable_irq(); // Зовнішня критична секція: хочемо передати весь пакет неподільно
    
    update_packet_checksum(payload, len);
    uart_send_byte(payload[0]); // Вкладений виклик!
    
    /* 
     * ТУТ ПЕРЕРИВАННЯ ВЖЕ УВІМКНЕНІ функцією uart_send_byte()!
     * Решта цієї функції виконується БЕЗ захисту, хоча розробник упевнений,
     * що перебуває всередині критичної секції.
     */
    for (size_t i = 1; i < len; i++) {
        UART1->DR = payload[i];
    }
    
    __enable_irq();
}
