/* Налаштування потоку приймання DMA1_Stream0 (SPI1_RX) */
DMA1_Stream0->CR = 0;
while (DMA1_Stream0->CR & DMA_SxCR_EN); /* Очікування зупинки */

DMA1_Stream0->PAR = (uint32_t)&(SPI1->DR);
DMA1_Stream0->M0AR = (uint32_t)g_spi1_rx_dma_buf;
DMA1_Stream0->NDTR = IMU_PACKET_SIZE;
DMA1_Stream0->CR = DMA_SxCR_MINC |            /* Інкремент адреси в пам'яті */
                   DMA_SxCR_TCIE |            /* Переривання по завершенню */
                   (0U << DMA_SxCR_PL_Pos);   /* Пріоритет */

/* Дозвіл запитів DMA від SPI */
SPI1->CR2 |= SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN;
