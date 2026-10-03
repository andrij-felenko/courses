#include <Arduino.h>

const uint8_t LED_PIN = 2;

void setup() {
    // Ініціалізація виводу через стандартний API
    pinMode(LED_PIN, OUTPUT);
    Serial.begin(115200);
}

void loop() {
    // Швидке перемикання виводу через прямий доступ до MMIO регістрів
    GPOS = (1 << LED_PIN); // Атомарне встановлення HIGH (GPIO_OUT_W1TS)
    delayMicroseconds(100);
    
    GPOC = (1 << LED_PIN); // Атомарне скидання LOW (GPIO_OUT_W1TC)
    delayMicroseconds(100);

    // Зчитування значення 10-бітного АЦП (0..1023)
    uint16_t adc_val = analogRead(A0);
    
    // Уникнення блокування WDT під час тривалих обчислень
    optimistic_yield(1000);
}
