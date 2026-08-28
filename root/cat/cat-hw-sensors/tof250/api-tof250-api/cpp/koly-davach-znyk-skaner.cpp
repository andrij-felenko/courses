#include <Wire.h>

void setup() {
    Wire.begin();
    Serial.begin(115200);      // це швидкість Serial-МОНІТОРА, не давача
    while (!Serial) { }
    Serial.println("Скан I2C-шини...");

    uint8_t found = 0;
    for (uint8_t addr = 1; addr < 127; addr++) {
        Wire.beginTransmission(addr);
        if (Wire.endTransmission() == 0) {   // 0 = хтось підтвердив цю адресу
            Serial.print("  знайдено пристрій за 0x");
            if (addr < 16) Serial.print('0');
            Serial.println(addr, HEX);
            found++;
        }
    }
    if (found == 0)
        Serial.println("  тиша. Перевір живлення, SDA/SCL і підтяжки.");
}

void loop() { }
