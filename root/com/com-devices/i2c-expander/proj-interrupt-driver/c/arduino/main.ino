#include <Wire.h>

#define MCP_ADDR 0x20
#define INT_PIN 2

volatile bool intFlag = false;

void IRAM_ATTR onInterrupt() {
    intFlag = true;
}

void setup() {
    Wire.begin();
    pinMode(INT_PIN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(INT_PIN), onInterrupt, FALLING);

    // Налаштування MCP23017: об'єднати INTA/B, Open-Drain
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x0A); // IOCON
    Wire.write(0x44); // MIRROR=1, ODR=1
    Wire.endTransmission();

    // Порт A як вхід із підтяжкою та перериванням
    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x00); // IODIRA
    Wire.write(0xFF); // Всі 8 пінів - входи
    Wire.endTransmission();

    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x0C); // GPPUA
    Wire.write(0xFF); // Підтяжки увімкнено
    Wire.endTransmission();

    Wire.beginTransmission(MCP_ADDR);
    Wire.write(0x04); // GPINTENA
    Wire.write(0xFF); // Дозвіл переривань для всіх пінів
    Wire.endTransmission();
}

void loop() {
    if (intFlag) {
        delay(25); // Апаратний дебаунсинг
        intFlag = false;

        Wire.beginTransmission(MCP_ADDR);
        Wire.write(0x10); // INTCAPA
        Wire.endTransmission();

        Wire.requestFrom(MCP_ADDR, 1);
        if (Wire.available()) {
            uint8_t captured = Wire.read();
            // Обробка захопленого байта кнопок
        }
    }
}
