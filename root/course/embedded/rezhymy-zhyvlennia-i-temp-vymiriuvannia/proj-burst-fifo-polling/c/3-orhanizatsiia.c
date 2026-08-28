extern SensorFifoDriver g_sensor;
volatile bool g_dma_in_progress = false;

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin) {
    if (GPIO_Pin == SENSOR_INT1_PIN) {
        sensor_on_watermark_isr(&g_sensor);
    }
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi) {
    if (hspi == g_sensor.hspi) {
        sensor_on_dma_complete(&g_sensor);
        g_dma_in_progress = false;
    }
}

void enter_system_low_power_loop(void) {
    sensor_fifo_init(&g_sensor);

    while (1) {
        /* 1. Запуск вичитування якщо прийшов тригер Watermark */
        if (g_sensor.data_ready_flag && !g_dma_in_progress) {
            g_dma_in_progress = true;
            if (!sensor_fetch_fifo_burst(&g_sensor)) {
                g_dma_in_progress = false;
            }
        }

        /* 2. Якщо триває передача DMA, чекаємо у режимі Sleep (ядро зупинено, DMA активний) */
        if (g_dma_in_progress) {
            HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
        } else {
            /* 3. Якщо передачу завершено — переходимо в глибокий Stop Mode */
            /* Пробудження відбудеться лише при наступному імпульсі Watermark на лінії EXTI */
            HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);
        }
    }
}
