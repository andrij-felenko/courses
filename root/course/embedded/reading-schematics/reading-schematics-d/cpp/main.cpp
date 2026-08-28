#include <Wire.h>

const uint8_t SENSOR_ADDR = 0x40;   // адреса давача на шині I2C
const uint8_t LOAD_PIN    = 5;      // GPIO на затвор Q1 через Rg

void setup() {
    Wire.begin();                   // піднімаємо I2C (SDA/SCL із підтяжками зі схеми)
    pinMode(LOAD_PIN, OUTPUT);
    digitalWrite(LOAD_PIN, LOW);    // навантаження вимкнене на старті
}

uint16_t readSensor() {
    Wire.beginTransmission(SENSOR_ADDR);
    Wire.write(0x00);               // вказали регістр, який хочемо
    Wire.endTransmission(false);    // повторний старт, без відпускання шини
    Wire.requestFrom(SENSOR_ADDR, (uint8_t)2);
    uint16_t hi = Wire.read();
    uint16_t lo = Wire.read();
    return (hi << 8) | lo;          // склали 16-бітове значення
}

void loop() {
    uint16_t v = readSensor();
    // залежно від давача вмикаємо силовий вихід через Q1
    digitalWrite(LOAD_PIN, (v > 3000) ? HIGH : LOW);
    delay(100);
}
