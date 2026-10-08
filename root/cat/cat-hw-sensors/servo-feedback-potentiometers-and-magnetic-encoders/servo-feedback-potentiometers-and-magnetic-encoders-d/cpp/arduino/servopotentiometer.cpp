// Зчитування потенціометра та аналогова фільтрація кута у C++ (Arduino)
#include <Arduino.h>

class ServoPotentiometer {
private:
    uint8_t pin;
    float filteredAngle;
    uint16_t adcMin;
    uint16_t adcMax;
    float maxAngle;
    float alpha;

public:
    ServoPotentiometer(uint8_t adcPin, uint16_t minAdc = 100, uint16_t maxAdc = 3990, float maxDeg = 180.0f)
        : pin(adcPin), filteredAngle(0.0f), adcMin(minAdc), adcMax(maxAdc), maxAngle(maxDeg), alpha(0.15f) {}

    void begin() {
        pinMode(pin, INPUT);
    }

    float readAngle() {
        uint16_t rawAdc = analogRead(pin);

        // Обрізання нелінійних мертвих зон
        if (rawAdc < adcMin) rawAdc = adcMin;
        if (rawAdc > adcMax) rawAdc = adcMax;

        // Лінійне перетворення АЦП у кут
        float norm = static_cast<float>(rawAdc - adcMin) / static_cast<float>(adcMax - adcMin);
        float currentAngle = norm * maxAngle;

        // Фільтрація високочастотних завад струмознімача
        filteredAngle = (alpha * currentAngle) + ((1.0f - alpha) * filteredAngle);
        return filteredAngle;
    }
};
