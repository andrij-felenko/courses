// Запуск чергового приймання: спершу почистити кеш ПІД буфер, тоді пускати DMA.
static void rx_start(void)
{
    // ПЕРЕД стартом: у кеші не має лишитися брудних рядків буфера,
    // інакше витіснення під час приймання затре свіже в SRAM.
    SCB_InvalidateDCache_by_Addr((uint32_t *)rx_buf, RX_LEN);

    // Налаштувати й пустити канал DMA на приймання RX_LEN байтів у rx_buf.
    dma_rx_config((uint32_t)rx_buf, RX_LEN);
    dma_rx_enable();   // з цієї миті DMA пише в SRAM сам
}

// Переривання «DMA завершив приймання повного буфера».
void DMA1_Stream0_IRQHandler(void)
{
    if (dma_rx_complete_flag()) {
        dma_rx_clear_flags();

        // ПІСЛЯ завершення: викинути копії, що ядро могло спекулятивно
        // затягнути під час приймання — тоді читання піде в SRAM за свіжим.
        SCB_InvalidateDCache_by_Addr((uint32_t *)rx_buf, RX_LEN);

        process_packet(rx_buf, RX_LEN);   // тепер це справді прийняте
        rx_start();                       // почати наступний буфер
    }
}
