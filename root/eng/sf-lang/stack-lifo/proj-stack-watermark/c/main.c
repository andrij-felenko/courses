// Періодична перевірка запасу стека задачі (викликати ЗРІДКА, не в гарячому циклі).
void check_stack_health(TaskHandle_t task) {
    // повертає запас у СЛОВАХ (4 байти на ESP32); HighWaterMark2 — у байтах
    UBaseType_t words_left = uxTaskGetStackHighWaterMark(task);
    size_t bytes_left = (size_t)words_left * sizeof(StackType_t);

    if (bytes_left < 256) {             // поріг із поправкою, не «нуль у нуль»
        ESP_LOGW("stack", "задачі лишилось лише %u Б стека!", (unsigned)bytes_left);
        // тут: підняти розмір стека задачі, або спростити найглибший виклик
    }
}
