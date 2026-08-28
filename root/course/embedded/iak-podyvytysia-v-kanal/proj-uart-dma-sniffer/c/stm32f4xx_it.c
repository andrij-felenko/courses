/* Обробник переривання DMA Idle Line у stm32f4xx_it.c */
extern UART_HandleTypeDef huart2;
extern trace_queue_t g_trace_queue;
extern uint8_t g_rx_dma_buf[256];

void USART2_IRQHandler(void) {
    if (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_IDLE) != RESET) {
        __HAL_UART_CLEAR_IDLEFLAG(&huart2);

        /* Визначаємо, скільки байтів записав контролер DMA */
        uint16_t remaining = __HAL_DMA_GET_COUNTER(huart2.hdmarx);
        uint16_t received_bytes = sizeof(g_rx_dma_buf) - remaining;

        if (received_bytes > 0) {
            /* Отримуємо мікросекунди без плаваючої коми */
            uint32_t now_us = DWT->CYCCNT / (SystemCoreClock / 1000000);
            trace_queue_push(&g_trace_queue, TRACE_DIR_RX, now_us, g_rx_dma_buf, received_bytes);
        }

        /* Перезапуск DMA на наступний прийом */
        HAL_UART_AbortReceive(&huart2);
        HAL_UART_Receive_DMA(&huart2, g_rx_dma_buf, sizeof(g_rx_dma_buf));
    }
    HAL_UART_IRQHandler(&huart2);
}
