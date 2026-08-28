/* Конфігурація апаратного подвійного буфера DMA (Ping-Pong) */
void dma_double_buffer_init(uint8_t *buf0, uint8_t *buf1, uint16_t size) {
    DMA1_Stream0->CR &= ~DMA_SxCR_EN;
    while (DMA1_Stream0->CR & DMA_SxCR_EN);

    DMA1_Stream0->PAR = (uint32_t)&(SPI1->DR);
    DMA1_Stream0->M0AR = (uint32_t)buf0;
    DMA1_Stream0->M1AR = (uint32_t)buf1;
    DMA1_Stream0->NDTR = size;

    /* Вмикаємо режим DBM та дозволяємо переривання перемикання буферів */
    DMA1_Stream0->CR |= DMA_SxCR_DBM | DMA_SxCR_MINC | DMA_SxCR_TCIE;
    DMA1_Stream0->CR |= DMA_SxCR_EN;
}
