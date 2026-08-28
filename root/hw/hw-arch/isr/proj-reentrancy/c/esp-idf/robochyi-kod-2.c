static volatile char line[64];   // спільний сирий буфер (тому volatile)
static SemaphoreHandle_t ready;  // сигнал «рядок готовий» замість прапорця
static portMUX_TYPE mux = portMUX_INITIALIZER_UNLOCKED;

static void IRAM_ATTR uart_isr(void *arg) {  // верхня половина — нічого «розумного»
    static uint8_t i = 0;
    BaseType_t woken = pdFALSE;
    char c = (char)read_byte();      // лише читання регістра — реентерабельно
    if (c == '\n') {
        line[i] = 0;
        i = 0;
        xSemaphoreGiveFromISR(ready, &woken);   // *FromISR — єдина дозволена форма
    } else if (i < sizeof(line) - 1) {
        line[i++] = c;               // складаємо байти по одному
    }
    if (woken) portYIELD_FROM_ISR(); // жодних strtok / malloc / ESP_LOGI
}

static void parse_task(void *arg) {  // нижня половина — тут можна ВСЕ
    char tmp[64];
    for (;;) {
        xSemaphoreTake(ready, portMAX_DELAY);
        portENTER_CRITICAL(&mux);
        strncpy(tmp, (const char *)line, sizeof(tmp)); // атомарний знімок буфера
        portEXIT_CRITICAL(&mux);
        char *save, *tok = strtok_r(tmp, ",", &save);  // розбір — в одному місці!
        ESP_LOGI(TAG, "%s", tok);                      // лог — у задачі, де безпечно
    }
}
