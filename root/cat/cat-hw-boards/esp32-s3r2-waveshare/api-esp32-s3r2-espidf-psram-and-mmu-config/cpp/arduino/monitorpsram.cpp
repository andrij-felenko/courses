#include <Arduino.h>
#include "esp_heap_caps.h"

// Моніторинг кучі PSRAM у середовищі Arduino IDE
void monitorPSRAM() {
  size_t freePSRAM = heap_caps_get_free_size(MALLOC_CAP_SPIRAM);
  size_t minFreePSRAM = heap_caps_get_minimum_free_size(MALLOC_CAP_SPIRAM);
  size_t maxBlock = heap_caps_get_largest_free_block(MALLOC_CAP_SPIRAM);

  Serial.printf("[PSRAM] Вільна: %u байтів | Мін. залишок: %u байтів | Макс. блок: %u байтів\n",
                (unsigned int)freePSRAM,
                (unsigned int)minFreePSRAM,
                (unsigned int)maxBlock);

  if (minFreePSRAM < 65536) {
    Serial.println("[ПОПЕРЕДЖЕННЯ] Наближення до межі пам'яті PSRAM!");
  }
}
