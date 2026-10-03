#include <Arduino.h>

void setup() {
    Serial.begin(115200);

    // 1. Динамічне перепризначення шини HardwareSerial (UART1) на довільні піни через GPIO Matrix
    // RX = GPIO5, TX = GPIO4
    Serial1.begin(115200, SERIAL_8N1, 5, 4);

    // 2. Зчитування аналогового сигналу з ADC1 (GPIO1 / A0)
    // Виклики безпечні навіть під час активного Wi-Fi з'єднання
    analogReadResolution(12);
    int val = analogRead(A0);
    Serial.printf("Значення ADC1: %d\n", val);
}

void loop() {
    delay(1000);
}
