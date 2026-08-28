/* ФАТАЛЬНА ПОМИЛКА: виклик блокуючого м'ютекса всередині ISR */
void USART1_IRQHandler(void) {
    /* Якщо м'ютекс зайнятий іншою задачею, обробник переривання 
     * НЕ МОЖЕ заснути — у нього немає власного стека задачі!
     * Результат: миттєвий Assert ядра RTOS або зависання процесора. */
    xSemaphoreTake(g_uart_mutex, portMAX_DELAY); /* КРАХ! */
    
    uint8_t byte = USART1->RDR;
    buffer_push(byte);
    xSemaphoreGive(g_uart_mutex);
}
