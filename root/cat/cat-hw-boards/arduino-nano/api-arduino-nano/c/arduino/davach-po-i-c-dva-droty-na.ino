#include <Wire.h>

const uint8_t ADDR    = 0x76;   // адреса давача (з даташита)
const uint8_t REG_ID  = 0xD0;   // регістр «хто ти»
const uint8_t REG_OUT = 0xF7;   // старший байт виміру

// прочитати n байтів від регістра reg у buf; true — успіх
bool i2c_read(uint8_t reg, uint8_t *buf, uint8_t n) {
    Wire.beginTransmission(ADDR);
    Wire.write(reg);                          // назвати регістр
    if (Wire.endTransmission(false) != 0)     // повторний старт, без stop
        return false;                         // ніхто не підтвердив адресу
    if (Wire.requestFrom(ADDR, n) != n)       // попросити n байтів
        return false;                         // прийшло менше — збій
    for (uint8_t i = 0; i < n; i++) buf[i] = Wire.read();
    return true;
}

void setup() {
    Serial.begin(9600);
    Wire.begin();                             // A4 = SDA, A5 = SCL

    uint8_t id = 0;
    if (i2c_read(REG_ID, &id, 1))
        Serial.println(id, HEX);              // побачили ID — давач на шині
    else
        Serial.println(F("немає відповіді"));
}

void loop() {
    uint8_t raw[2];
    if (i2c_read(REG_OUT, raw, 2)) {
        int value = (raw[0] << 8) | raw[1];   // старший байт першим
        Serial.println(value);
    }
    delay(500);
}
