#include <Arduino.h>

class MAX31865Reader {
private:
    const float _rRef;
    static constexpr float ADC_SCALE = 32768.0f;

public:
    explicit MAX31865Reader(float rRef = 400.0f) : _rRef(rRef) {}

    float calculateResistance(uint16_t rawAdcCode15Bit) const {
        return (static_cast<float>(rawAdcCode15Bit) * _rRef) / ADC_SCALE;
    }
};

MAX31865Reader sensor(400.0f);

void setup() {
    Serial.begin(115200);
    uint16_t adcCode = 8192; // Приклад коду для ~100 Ом (0 °C)
    float resistance = sensor.calculateResistance(adcCode);
    
    Serial.print(F("Опір RTD: "));
    Serial.print(resistance, 4);
    Serial.println(F(" Ом"));
}

void loop() {
    // Періодичне зчитування
}
