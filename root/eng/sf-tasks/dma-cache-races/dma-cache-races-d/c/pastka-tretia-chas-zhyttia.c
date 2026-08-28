/* НЕПРАВИЛЬНО */
void bad_dma_example(void) {
    uint8_t buf[1024];           /* на стеку, невирівняний */
    fill_data(buf, sizeof(buf));
    dma_start_send(buf, sizeof(buf));
    /* функція повертається → кадр стеку перезаписано, DMA ще зайнятий */
}

/* ПРАВИЛЬНО */
static uint8_t buf[1024] __attribute__((aligned(32)));  /* статичний, вирівняний */
static SemaphoreHandle_t sem_tx;

void good_dma_example(void) {
    fill_data(buf, sizeof(buf));
    esp_cache_msync(buf, sizeof(buf),
                    ESP_CACHE_MSYNC_FLAG_DIR_C2M);  /* write-back перед стартом */
    __DSB();                                        /* записи в пам'ять — до старту DMA */
    dma_start_send(buf, sizeof(buf));
    xSemaphoreTake(sem_tx, portMAX_DELAY);          /* чекаємо переривання завершення */
    /* лише тепер buf вільний для наступного використання */
}

/* Переривання завершення */
void IRAM_ATTR tx_done_isr(void *arg) {
    BaseType_t woken = pdFALSE;
    xSemaphoreGiveFromISR(sem_tx, &woken);
    portYIELD_FROM_ISR(woken);
}
