#include <math.h>

// Азимут у градусах 0…360, з поправкою на магнітне схилення
float compass_heading(int16_t x, int16_t y, float declination_deg) {
    float h = atan2f((float)y, (float)x);              // радіани, −π…+π
    h += declination_deg * (float)M_PI / 180.0f;       // схилення → істинна північ
    if (h < 0)          h += 2.0f * (float)M_PI;
    if (h >= 2*M_PI)    h -= 2.0f * (float)M_PI;
    return h * 180.0f / (float)M_PI;                   // 0…360°
}

void setup() {
    Serial.begin(115200);
    compass_begin();
    if (chip == CHIP_NONE) Serial.println("Компас не знайдено на I2C!");
    else Serial.println(chip == CHIP_HMC ? "Знайдено HMC5883L" : "Знайдено QMC5883L");
}

void loop() {
    int16_t x, y, z;
    if (compass_read(&x, &y, &z)) {
        float az = compass_heading(x, y, /*схилення для твого міста*/ 8.0f);
        Serial.print("Азимут: "); Serial.print(az, 1); Serial.println("°");
    }
    delay(100);
}
