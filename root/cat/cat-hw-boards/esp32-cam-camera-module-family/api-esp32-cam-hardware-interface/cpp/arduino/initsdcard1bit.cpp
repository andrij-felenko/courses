#include "esp_camera.h"
#include "SD_MMC.h"

// Ініціалізація SD-картки у 1-бітовому режимі в середовищі Arduino
bool initSDCard1Bit() {
    // Передаємо true в якості третього аргументу (mode1bit = true)
    if (!SD_MMC.begin("/sdcard", true)) {
        Serial.println("Помилка монтування SD-картки у 1-бітовому режимі!");
        return false;
    }
    uint8_t cardType = SD_MMC.cardType();
    if (cardType == CARD_NONE) {
        Serial.println("Картку пам'яті не підключено");
        return false;
    }
    return true;
}
