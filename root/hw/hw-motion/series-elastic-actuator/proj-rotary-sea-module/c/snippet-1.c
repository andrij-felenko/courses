/* Конфігурація та запуск апаратного зчитування енкодерів через DMA */
#define ENCODER_FRAME_WORDS  2
static uint16_t dma_tx_cmd[ENCODER_FRAME_WORDS] = {0xFFFF, 0xFFFF};
static uint16_t dma_rx_raw[ENCODER_FRAME_WORDS] = {0, 0};

void Sea_Init_Encoder_DMA(void) {
    /* Налаштування потоків DMA1 Channel 1 (SPI1_RX) та Channel 2 (SPI1_TX) */
    hdma_spi1_rx.Instance = DMA1_Channel1;
    hdma_spi1_rx.Init.Request = DMA_REQUEST_SPI1_RX;
    hdma_spi1_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_spi1_rx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_rx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    hdma_spi1_rx.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    hdma_spi1_rx.Init.Mode = DMA_CIRCULAR;
    hdma_spi1_rx.Init.Priority = DMA_PRIORITY_VERY_HIGH;
    HAL_DMA_Init(&hdma_spi1_rx);
    __HAL_LINKDMA(&hspi1, hdmarx, hdma_spi1_rx);

    hdma_spi1_tx.Instance = DMA1_Channel2;
    hdma_spi1_tx.Init.Request = DMA_REQUEST_SPI1_TX;
    hdma_spi1_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_spi1_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_spi1_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_spi1_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    hdma_spi1_tx.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    hdma_spi1_tx.Init.Mode = DMA_CIRCULAR;
    hdma_spi1_tx.Init.Priority = DMA_PRIORITY_HIGH;
    HAL_DMA_Init(&hdma_spi1_tx);
    __HAL_LINKDMA(&hspi1, hdmatx, hdma_spi1_tx);

    /* Запуск безперервного двостороннього циклічного обміну */
    HAL_SPI_TransmitReceive_DMA(&hspi1, (uint8_t *)dma_tx_cmd, (uint8_t *)dma_rx_raw, ENCODER_FRAME_WORDS);
}

/* Обробник завершення DMA-транзакції: розпакування кутів без блокування CPU */
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi->Instance == SPI1) {
        uint16_t raw_motor = dma_rx_raw[0] & 0x3FFF;
        uint16_t raw_joint = dma_rx_raw[1] & 0x3FFF;
        
        sea_handle.theta_motor_raw = raw_motor;
        sea_handle.theta_joint_raw = raw_joint;
        sea_handle.data_ready_flag = 1;
    }
}
