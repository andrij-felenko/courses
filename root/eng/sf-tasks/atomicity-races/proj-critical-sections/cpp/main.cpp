// 1) ISR ↔ main, одне ядро: вимкнути переривання на пару інструкцій
volatile uint32_t pulses = 0;
void IRAM_ATTR onPulse() { pulses++; }            // обробник лише рахує

uint32_t takeSnapshot() {
    noInterrupts();                               // вхід у критичну секцію
    uint32_t n = pulses; pulses = 0;              // неподільна пара RMW
    interrupts();                                 // вихід — ОБОВ'ЯЗКОВО
    return n;                                     // далі друкуємо вже поза секцією
}

// 2) Два ядра: спінлок portMUX — замикає І вимикає переривання
portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;
void bumpShared(uint32_t *counter) {
    portENTER_CRITICAL(&mux);                     // в обробнику — portENTER_CRITICAL_ISR
    (*counter)++;                                 // не пускає й друге ядро
    portEXIT_CRITICAL(&mux);
}

// 3) Задача ↔ задача: м'ютекс FreeRTOS (може блокуватись; НЕ з ISR)
SemaphoreHandle_t m = xSemaphoreCreateMutex();
void updateConfig(Config *cfg, int v) {
    xSemaphoreTake(m, portMAX_DELAY);             // чекає, доки звільнять
    cfg->a = v; cfg->b = v * 2;                   // узгоджене оновлення кількох полів
    xSemaphoreGive(m);
}
