/* Контекст RTOS: Завдання нижньої половини (Bottom-Half) */
static TaskHandle_t xUartTaskHandle = NULL;

void vUartProcessingTask(void *pvParameters) {
    uint8_t rx_byte;
    
    for (;;) {
        /* Чекаємо на сповіщення від ISR у стані глибокого сну (Blocked).
           Нульове споживання CPU під час очікування. */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        /* Вичитуємо всі накопичені байти з Lock-Free буфера */
        while (ring_buffer_pop_main(&uart_ring_buf, &rx_byte)) {
            process_protocol_byte(rx_byte); /* Важкий парсинг пакетів */
        }
    }
}

/* Контекст апаратного переривання: Верхня половина (Top-Half) */
void USART1_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;

    if (USART1->SR & USART_SR_RXNE) {
        uint8_t data = (uint8_t)(USART1->DR);
        
        /* 1. Зберігаємо байт у lock-free буфер */
        ring_buffer_push_isr(&uart_ring_buf, data);

        /* 2. Сповіщаємо завдання нижньої половини */
        vTaskNotifyGiveFromISR(xUartTaskHandle, &xHigherPriorityTaskWoken);

        /* 3. Якщо розблокований таск має вищий пріоритет,
              викликаємо негайне перемикання контексту прямо на виході з ISR */
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }
}
