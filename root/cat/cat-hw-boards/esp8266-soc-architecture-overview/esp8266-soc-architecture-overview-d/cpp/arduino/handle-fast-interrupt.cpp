#include <Arduino.h>

// Використання макросу IRAM_ATTR для розміщення функції в IRAM
void IRAM_ATTR handle_fast_interrupt() {
    // Швидка обробка переривання без промахів кешу MMU
    digitalWrite(LED_BUILTIN, !digitalRead(LED_BUILTIN));
}

void checkMemoryBudget() {
    uint32_t free_heap = ESP.getFreeHeap();
    uint32_t max_block = ESP.getMaxFreeBlockSize();
    uint8_t frag_percent = ESP.getHeapFragmentation();

    Serial.printf("Телеметрія RAM -> Вільна купа: %u б | Макс. блок: %u б | Фрагментація: %u%%\n",
                  free_heap, max_block, frag_percent);

    if (max_block < 16384) {
        Serial.println("УВАГА: Неможливо виділити суцільний буфер 16 КБ під TLS сокет!");
    }
}
