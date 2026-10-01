#include <Arduino.h>

class PiezoProcessor {
private:
    float vRef;
    float adcMax;
    float sensitivity;
    float zeroOffset;
    float alphaHPF;
    float prevX;
    float prevY;
    float thresholdG;

public:
    PiezoProcessor(float vref = 3.3f, int adcBits = 12, float sens = 0.1f)
        : vRef(vref), sensitivity(sens), alphaHPF(0.95f), prevX(0.0f), prevY(0.0f), thresholdG(1.5f) {
        adcMax = (1 << adcBits) - 1;
        zeroOffset = adcMax / 2.0f;
    }

    bool processSample(int rawAdc, float &accelG) {
        // 1. Компенсація зміщення та обчислення напруги
        float deltaAdc = rawAdc - zeroOffset;
        float vSignal = (deltaAdc * vRef) / adcMax;

        // 2. Масштабування у прискорення (g)
        float accelRaw = vSignal / sensitivity;

        // 3. Цифрова IIR ФВЧ фільтрація
        float accelFiltered = alphaHPF * (prevY + accelRaw - prevX);
        prevX = accelRaw;
        prevY = accelFiltered;

        accelG = accelFiltered;

        // 4. Порівняння з порогом події
        return abs(accelFiltered) >= thresholdG;
    }
};
