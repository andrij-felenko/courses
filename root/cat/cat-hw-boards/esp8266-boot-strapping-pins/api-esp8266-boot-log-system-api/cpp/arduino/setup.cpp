#include <ESP8266WiFi.h>

void setup() {
  Serial.begin(115200);
  delay(100);

  // Отримання текстового опису та структури скидання у середовищі Arduino
  String reset_reason = ESP.getResetReason();
  rst_info *raw_info = ESP.getResetInfoPtr();

  Serial.println();
  Serial.print("Причина старту: ");
  Serial.println(reset_reason);

  if (raw_info->reason == REASON_EXCEPTION_RST) {
    Serial.printf("Адреса винятку EPC1: 0x%08X\n", raw_info->epc1);
    // Логіка переходу у безпечний режим при циклічних падіннях
  }
}

void loop() {
  // Основний цикл програми
}
