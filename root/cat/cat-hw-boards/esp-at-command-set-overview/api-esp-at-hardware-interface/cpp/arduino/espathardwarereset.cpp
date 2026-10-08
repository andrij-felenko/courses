#include <Arduino.h>

const int ESP_AT_RST_PIN = 4;
const int ESP_AT_EN_PIN  = 5;

void espAtHardwareReset() {
    pinMode(ESP_AT_EN_PIN, OUTPUT);
    pinMode(ESP_AT_RST_PIN, OUTPUT);

    // Активація модуля через EN
    digitalWrite(ESP_AT_EN_PIN, HIGH);
    delay(20);

    // Формування примусового імпульсу скидання на лінії RST
    digitalWrite(ESP_AT_RST_PIN, LOW);
    delay(50); // Тривалість імпульсу t_RST = 50 мс
    digitalWrite(ESP_AT_RST_PIN, HIGH);

    // Затримка t_ready перед передачею першої AT-команди
    delay(500);
}
