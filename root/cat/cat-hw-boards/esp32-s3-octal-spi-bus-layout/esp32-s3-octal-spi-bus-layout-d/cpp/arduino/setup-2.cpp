#include <Arduino.h>
#include "esp_efuse.h"
#include "esp_efuse_table.h"

void setup() {
    Serial.begin(115200);
    while (!Serial) { delay(10); }

    Serial.println("[VDD_SPI] Опитування системних регістрів живлення Octal SPI...");

    uint32_t force_val = 0;
    uint32_t tieh_val = 0;

    esp_efuse_read_field_blob(ESP_EFUSE_VDD_SPI_FORCE, &force_val, 1);
    esp_efuse_read_field_blob(ESP_EFUSE_VDD_SPI_TIEH, &tieh_val, 1);

    if (force_val == 1) {
        Serial.printf("[VDD_SPI] Живлення пам'яті заблоковано в eFuse. Напруга: %s\n", 
                      (tieh_val == 1) ? "1.8 В (Octal OPI)" : "3.3 В (Standard SPI)");
    } else {
        Serial.println("[VDD_SPI] УВАГА: Напруга залежить від фізичної підтяжки GPIO45 на платі!");
    }
}

void loop() {
    vTaskDelay(pdMS_TO_TICKS(2000));
}
