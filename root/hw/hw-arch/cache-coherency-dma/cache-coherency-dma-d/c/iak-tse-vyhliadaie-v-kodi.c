// 32 — розмір лінії кеша Cortex-M7; буфер вирівняно на межу лінії
static uint8_t rx_buf[256] __attribute__((aligned(32)));

void receive_frame(void) {
    start_dma_receive(rx_buf, sizeof(rx_buf));   // DMA пише в ОЗП
    while (!dma_done()) { /* чекаємо або спимо */ }

    // DMA поклав свіже в ОЗП; кеш може тримати старе — викидаємо його
    SCB_InvalidateDCache_by_Addr((uint32_t *)rx_buf, sizeof(rx_buf));

    process(rx_buf);   // тепер читання піде в ОЗП і візьме нові байти
}
