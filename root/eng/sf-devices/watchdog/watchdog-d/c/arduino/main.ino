#include "esp_task_wdt.h"

#define WDT_TIMEOUT_S 5          // таймаут сторожа, секунди

void setup() {
  esp_task_wdt_init(WDT_TIMEOUT_S, true);  // увімкнути: 5 с, true → reset
  esp_task_wdt_add(NULL);                  // стерегти ЦЮ задачу (loopTask)
}

void loop() {
  doWork();                 // якщо завис ТУТ — до годівлі не дійде
  esp_task_wdt_reset();     // дійшли здоровими → скидаємо лічильник
}
