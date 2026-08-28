#include <Wire.h>
const uint8_t DAC = 0x60;         // MCP4725, A0 на землі

void dacSet(uint16_t v) {         // v: 0..4095 (12 біт)
    v &= 0x0FFF;                  // лишаємо тільки 12 значущих біт
    Wire.beginTransmission(DAC);
    Wire.write(v >> 8);           // верхні 4 біти (старший нібл = 0 → швидкий запис)
    Wire.write(v & 0xFF);        // молодші 8 біт
    Wire.endTransmission();
}

void setup() {
    Wire.begin();                 // SDA=21, SCL=22 на класичному ESP32
    dacSet(2048);                 // ≈ половина шкали ≈ 1.65 В
}
void loop() {}
