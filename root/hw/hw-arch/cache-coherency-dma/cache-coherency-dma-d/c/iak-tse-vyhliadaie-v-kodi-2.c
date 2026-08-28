static uint8_t tx_buf[256] __attribute__((aligned(32)));

void send_frame(const uint8_t *data, size_t n) {
    memcpy(tx_buf, data, n);   // пишемо через кеш — свіже поки в кеші

    // зіштовхуємо кеш у ОЗП, щоб DMA прочитав саме нове
    SCB_CleanDCache_by_Addr((uint32_t *)tx_buf, sizeof(tx_buf));

    start_dma_transmit(tx_buf, n);   // DMA читає з ОЗП — і бачить свіже
}
