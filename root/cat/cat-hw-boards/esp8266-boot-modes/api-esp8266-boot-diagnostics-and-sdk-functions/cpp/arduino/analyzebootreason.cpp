#include <Arduino.h>

void analyzeBootReason() {
    rst_info *info = ESP.getResetInfoPtr();
    
    Serial.printf("Код причини завантаження: %d\n", info->reason);
    
    if (info->reason == REASON_WDT_RST || info->reason == REASON_SOFT_WDT_RST) {
        Serial.println("Перезавантаження викликано сторожовим таймером WDT");
    } else if (info->reason == REASON_EXCEPTION_RST) {
        Serial.printf("Аварійне переривання ядра! Cause: %d, EPC1: 0x%08x, VADDR: 0x%08x\n",
                      info->exccause, info->epc1, info->excvaddr);
    } else if (info->reason == REASON_DEEP_SLEEP_RESET) {
        Serial.println("Пробудження з режиму глибокого сну");
    } else {
        Serial.println("Звичайний запуск або апаратне скидання");
    }
}
