#include <Wire.h>
constexpr uint8_t ADS_ADDR = 0x48;   // ADDR -> GND

// Config: OS=1(старт single-shot), MUX=100(A0 vs GND), PGA=001(±4.096 В),
// MODE=1(single-shot), DR=100(128 SPS), COMP off (0x0003)
constexpr uint16_t CFG = 0xC383;

uint16_t adsRead16(uint8_t reg) {
    Wire.beginTransmission(ADS_ADDR);
    Wire.write(reg);
    Wire.endTransmission();
    Wire.requestFrom(ADS_ADDR, (uint8_t)2);
    return (Wire.read() << 8) | Wire.read();   // MSB перший
}

void adsStart() {
    Wire.beginTransmission(ADS_ADDR);
    Wire.write(0x01);                 // вказати Config-регістр
    Wire.write(CFG >> 8);
    Wire.write(CFG & 0xFF);
    Wire.endTransmission();
}

// Після старту: дочекатись готовності (мін. 1/DR = ~8 мс), тоді читати
int16_t raw = (int16_t)adsRead16(0x00);   // reg 0x00 — Conversion, знаковий!
float fsr   = 4.096f;                      // має збігатись із PGA у CFG (±4.096 В)
float volts = raw * fsr / 32768.0f;        // ±FS = ±32768 кодів
