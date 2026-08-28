#include <Wire.h>
#define TOF_ADDR 0x52          // 7-бітна адреса модуля (байт 0xA4 → 0x52)

int readDistanceMM() {
    Wire.beginTransmission(TOF_ADDR);
    Wire.write(0x00);                    // хочу читати з регістра 0x00 (відстань)
    if (Wire.endTransmission(false) != 0) // повторний старт, не відпускаючи шину
        return -1;                        // модуль не відповів

    Wire.requestFrom(TOF_ADDR, 2);        // очікую два байти
    if (Wire.available() < 2) return -1;

    uint16_t hi = Wire.read();            // старший байт
    uint16_t lo = Wire.read();            // молодший байт
    return (int)((hi << 8) | lo);         // мм
}

void setup() {
    Wire.begin();
    Serial.begin(115200);
}
void loop() {
    int mm = readDistanceMM();
    if (mm >= 0) { Serial.print(mm); Serial.println(" mm"); }
    delay(100);                           // ~10 разів на секунду
}
