#include <Arduino.h>
#include "esp_efuse.h"

void setup() {
    Serial.begin(115200);
    pinMode(0, INPUT_PULLUP);
    int bootPinState = digitalRead(0);

    bool vddSpiForced = esp_efuse_read_field_bit(ESP_EFUSE_VDD_SPI_FORCE);

    Serial.print(F("Логічний рівень виводу BOOT (GPIO0): "));
    Serial.println(bootPinState);
    Serial.print(F("Фіксація напруги VDD_SPI у конфігурації eFuse: "));
    Serial.println(vddSpiForced ? F("Активовано") : F("Вимкнено"));
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(1000));
}
