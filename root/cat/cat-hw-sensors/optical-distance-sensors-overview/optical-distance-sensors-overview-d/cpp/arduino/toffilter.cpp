#include <Arduino.h>
#include <Wire.h>

#define TOF_I2C_ADDR 0x29
#define WINDOW_SIZE  5

class ToFFilter {
private:
    uint16_t buffer[WINDOW_SIZE];
    uint8_t idx = 0;
    uint8_t cnt = 0;
    float emaState = 0.0f;
    float alpha = 0.25f;
    bool isInit = false;

public:
    ToFFilter(float smoothingAlpha) : alpha(smoothingAlpha) {}

    uint16_t process(uint16_t rawVal) {
        buffer[idx] = rawVal;
        idx = (idx + 1) % WINDOW_SIZE;
        if (cnt < WINDOW_SIZE) cnt++;

        uint16_t sorted[WINDOW_SIZE];
        for (uint8_t i = 0; i < cnt; i++) {
            sorted[i] = buffer[i];
        }
        for (uint8_t i = 0; i < cnt - 1; i++) {
            for (uint8_t j = i + 1; j < cnt; j++) {
                if (sorted[i] > sorted[j]) {
                    uint16_t tmp = sorted[i];
                    sorted[i] = sorted[j];
                    sorted[j] = tmp;
                }
            }
        }

        uint16_t medianVal = sorted[cnt / 2];

        if (!isInit) {
            emaState = static_cast<float>(medianVal);
            isInit = true;
        } else {
            emaState = alpha * static_cast<float>(medianVal) + (1.0f - alpha) * emaState;
        }

        return static_cast<uint16_t>(emaState + 0.5f);
    }
};

ToFFilter tofFilter(0.25f);

uint16_t readRawDistance() {
    Wire.beginTransmission(TOF_I2C_ADDR);
    Wire.write(0x14);
    if (Wire.endTransmission() != 0) return 0;

    Wire.requestFrom(TOF_I2C_ADDR, (uint8_t)2);
    if (Wire.available() >= 2) {
        uint8_t msb = Wire.read();
        uint8_t lsb = Wire.read();
        return ((uint16_t)msb << 8) | lsb;
    }
    return 0;
}

void setup() {
    Serial.begin(115200);
    Wire.begin();
}

void loop() {
    uint16_t raw = readRawDistance();
    if (raw > 0) {
        uint16_t filtered = tofFilter.process(raw);
        Serial.print("Raw: ");
        Serial.print(raw);
        Serial.print(" mm | Filtered: ");
        Serial.print(filtered);
        Serial.println(" mm");
    }
    delay(50);
}
