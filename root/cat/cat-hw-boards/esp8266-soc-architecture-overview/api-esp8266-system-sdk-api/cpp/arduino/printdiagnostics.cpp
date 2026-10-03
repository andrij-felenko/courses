// Приклад системи діагностики у C++ (ESP8266 Arduino Core)
#include <Arduino.h>

void printDiagnostics() {
    Serial.printf("Версія SDK: %s\n", ESP.getSdkVersion());
    Serial.printf("Частота CPU: %u МГц\n", ESP.getCpuFreqMHz());

    // Зчитування текстової причини скидання в Arduino Core
    String resetReason = ESP.getResetReason();
    String resetInfo = ESP.getResetInfo();

    Serial.println("--- ДІАГНОСТИКА СТАНОУ ---");
    Serial.println("Причина скидання: " + resetReason);
    Serial.println("Деталі: " + resetInfo);
}
