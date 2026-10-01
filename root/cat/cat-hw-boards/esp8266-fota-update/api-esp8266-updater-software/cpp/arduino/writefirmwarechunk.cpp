#include <ESP8266WiFi.h>
#include <Updater.h>

bool writeFirmwareChunk(uint8_t* data, size_t len, size_t totalSize, bool isFirst, bool isLast) {
  if (isFirst) {
    // Ініціалізація сесії оновлення для Flash-пам'яті
    if (!Update.begin(totalSize, U_FLASH)) {
      Update.printError(Serial);
      return false;
    }
  }

  // Потоковий запис порції байтів у неактивний сектор
  if (Update.write(data, len) != len) {
    Update.printError(Serial);
    return false;
  }

  if (isLast) {
    // Фіналізація та верифікація записаного образу
    if (Update.end(true)) {
      Serial.println("Оновлення успішно завершено! Перезавантаження...");
      ESP.restart();
    } else {
      Update.printError(Serial);
      return false;
    }
  }
  return true;
}
