SemaphoreHandle_t spiMtx, sdMtx;   // два спільні ресурси, кожен під своїм м'ютексом

// ✗ НЕБЕЗПЕЧНО: задачі беруть замки в РІЗНОМУ порядку → можливий дедлок
void taskA(void *p) {              // A: spi, потім sd
    for (;;) {
        xSemaphoreTake(spiMtx, portMAX_DELAY);
        xSemaphoreTake(sdMtx,  portMAX_DELAY);   // ← чекає на sd, тримаючи spi
        drawAndLog();
        xSemaphoreGive(sdMtx);
        xSemaphoreGive(spiMtx);
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
void taskB(void *p) {              // B: sd, потім spi  ← ПРОТИЛЕЖНИЙ порядок!
    for (;;) {
        xSemaphoreTake(sdMtx,  portMAX_DELAY);
        xSemaphoreTake(spiMtx, portMAX_DELAY);   // ← кільце замикається тут
        logAndDraw();
        xSemaphoreGive(spiMtx);
        xSemaphoreGive(sdMtx);
        vTaskDelay(pdMS_TO_TICKS(20));
    }
}
