// НЕ РОБІТЬ ТАК — усе нереентерабельне в обробнику
static const char *TAG = "uart";

static void IRAM_ATTR uart_isr(void *arg) {
    char buf[32];
    size_t n = read_line(buf);           // умовно: читаємо рядок
    char *tok = strtok(buf, ",");        // статичний стан! — зітре позицію задачі
    int *vals = malloc(n * sizeof(int)); // замок купи! — з ISR у FreeRTOS заборонено
    ESP_LOGI(TAG, "got %s", tok);        // буфер виводу + malloc! — подвійний удар
    // ... три способи тихо зламати систему в одному обробнику
}
