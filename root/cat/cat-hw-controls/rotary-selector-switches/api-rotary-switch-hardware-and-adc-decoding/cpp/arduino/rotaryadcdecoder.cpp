#include <Arduino.h>

class RotaryADCDecoder {
private:
    static const uint8_t posCount = 12;
    uint16_t nominalADC[posCount];
    uint16_t hysteresis;
    uint8_t currentPosition;
    bool errorState;

public:
    RotaryADCDecoder(const uint16_t* centers, uint16_t hyst = 30)
        : hysteresis(hyst), currentPosition(0), errorState(false) {
        for (uint8_t i = 0; i < posCount; i++) {
            nominalADC[i] = centers[i];
        }
    }

    uint8_t update(uint16_t rawADC) {
        if (rawADC < 20 || rawADC > 1000) { // 10-бітний АЦП Arduino
            errorState = true;
            return currentPosition;
        }
        errorState = false;

        int32_t currentCenter = nominalADC[currentPosition];
        if (abs((int32_t)rawADC - currentCenter) <= (50 + hysteresis)) {
            return currentPosition;
        }

        for (uint8_t i = 0; i < posCount; i++) {
            if (abs((int32_t)rawADC - (int32_t)nominalADC[i]) <= 50) {
                currentPosition = i;
                break;
            }
        }
        return currentPosition;
    }

    bool isFault() const { return errorState; }
};
