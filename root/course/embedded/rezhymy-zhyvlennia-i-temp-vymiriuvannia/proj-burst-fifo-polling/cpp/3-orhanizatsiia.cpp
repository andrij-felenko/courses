extern FifoSensorDriver<32> g_sensor;
volatile bool g_dma_active = false;

extern "C" void HAL_GPIO_EXTI_Callback(uint16_t pin) {
    if (pin == SENSOR_INT1_PIN) {
        g_sensor.onInterrupt();
    }
}

extern "C" void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef* hspi) {
    g_sensor.onDmaComplete();
    g_dma_active = false;
}

void runEventLoop() {
    auto init_res = g_sensor.init();
    if (!init_res.has_value()) {
        /* Обробка апаратної помилки ініціалізації */
        return;
    }

    while (true) {
        if (!g_dma_active) {
            auto burst_res = g_sensor.startBurstReadDma();
            if (burst_res.has_value()) {
                g_dma_active = true;
            }
        }

        if (g_dma_active) {
            /* DMA вичитує шину: ядро спить у Sleep Mode (RAM + периферія активні) */
            HAL_PWR_EnterSLEEPMode(PWR_MAINREGULATOR_ON, PWR_SLEEPENTRY_WFI);
        } else {
            /* Буфер оброблено: глибокий Stop 2 Mode до наступного переривання Watermark */
            HAL_PWREx_EnterSTOP2Mode(PWR_STOPENTRY_WFI);
        }
    }
}
