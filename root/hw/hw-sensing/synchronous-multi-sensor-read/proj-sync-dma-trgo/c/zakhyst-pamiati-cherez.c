/* Налаштування регіону MPU для некешованого буфера DMA */
void mpu_setup_dma_buffers(void) {
    /* Вимикаємо MPU перед конфігурацією */
    MPU->CTRL = 0;

    /* Вибираємо регіон 0 для буферів сенсорної шини */
    MPU->RNR = 0;
    MPU->RBAR = (uint32_t)g_spi1_rx_dma_buf & MPU_RBAR_ADDR_Msk;
    MPU->RASR = (0 << MPU_RASR_XN_Pos)   |  /* Дозвіл виконання (не має значення) */
                (3 << MPU_RASR_AP_Pos)   |  /* Повний доступ (Read/Write) */
                (0 << MPU_RASR_TEX_Pos)  |  /* TEX=001, C=0, B=0: Normal Non-Cacheable */
                (1 << MPU_RASR_C_Pos)    |
                (0 << MPU_RASR_B_Pos)    |
                (0 << MPU_RASR_S_Pos)    |  /* Not Shareable */
                (5 << MPU_RASR_SIZE_Pos) |  /* Розмір регіону 64 байти (2^(5+1)) */
                (1 << MPU_RASR_ENABLE_Pos);

    /* Вмикаємо MPU з дозволом фонового простору */
    MPU->CTRL = MPU_CTRL_ENABLE_Msk | MPU_CTRL_PRIVDEFENA_Msk;
    __DSB();
    __ISB();
}
