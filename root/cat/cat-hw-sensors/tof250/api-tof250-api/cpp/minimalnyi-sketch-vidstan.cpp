#include <Wire.h>
#define TOF_ADDR 0x52

int tofRead() {
    Wire.beginTransmission(TOF_ADDR);
    Wire.write(0x00);                          // регістр живої відстані
    if (Wire.endTransmission(false) != 0) return -1;
    if (Wire.requestFrom(TOF_ADDR, (uint8_t)2) != 2) return -1;
    uint16_t hi = Wire.read(), lo = Wire.read();
    return (int)((hi << 8) | lo);
}

void setup() {
    Wire.begin();                              // SDA/SCL — типові виводи плати
    Serial.begin(115200);
    while (!Serial) { }
    Serial.println("TOF250 готовий");
}

void loop() {
    int mm = tofRead();
    if (mm >= 0) {
        Serial.print(mm);
        Serial.println(" mm");
    } else {
        Serial.println("немає відповіді (перевір адресу й дроти)");
    }
    delay(100);                                // ~10 замірів на секунду
}
