#include <Arduino.h>

class PiezoSensorDriver {
private:
    uint8_t pin;
    float alphaBaseline;
    float scaleGPerLsb;
    float thresholdG;
    float baseline;

public:
    PiezoSensorDriver(uint8_t adcPin, float scaleG, float threshG, float alpha = 0.005f)
        : pin(adcPin), alphaBaseline(alpha), scaleGPerLsb(scaleG), thresholdG(threshG), baseline(2048.0f) {}

    void begin() {
        pinMode(pin, INPUT);
        baseline = (float)analogRead(pin);
    }

    // Прочитати АЦП, оновити нуль та оцінити енергію поштовху
    float readAcceleration(bool &isImpact) {
        uint16_t rawAdc = analogRead(pin);

        // Оновлення спокійного зміщення постійної складової (DC offset)
        baseline = (alphaBaseline * (float)rawAdc) + ((1.0f - alphaBaseline) * baseline);

        // Обчислення амплітуди відхилення від нуля
        float diff = abs((float)rawAdc - baseline);
        float accelG = diff * scaleGPerLsb;

        isImpact = (accelG >= thresholdG);
        return accelG;
    }
};
