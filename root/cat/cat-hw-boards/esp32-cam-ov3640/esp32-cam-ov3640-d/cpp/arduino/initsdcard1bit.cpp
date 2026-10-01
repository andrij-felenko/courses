#include "SD_MMC.h"
#include "Arduino.h"

bool initSDCard1Bit() {
  // Запуск SD_MMC у 1-бітовому режимі (mode1bit = true)
  // Вивільняє GPIO4 (спалах), GPIO12 та GPIO13
  if (!SD_MMC.begin("/sdcard", true)) {
    Serial.println("Помилка монтування MicroSD картки у 1-бітовому режимі!");
    return false;
  }
  uint8_t cardType = SD_MMC.cardType();
  if (cardType == CARD_NONE) {
    Serial.println("MicroSD карту не підключено.");
    return false;
  }
  Serial.println("MicroSD успішно змонтовано у 1-бітовому режимі.");
  return true;
}
