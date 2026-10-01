#include <Arduino.h>

class PiezoPeakDetector {
private:
    float state;
    float alpha;
    uint16_t zeroOffset;

public:
    PiezoPeakDetector(float decayAlpha, uint16_t offset = 512)
        : state(0.0f), alpha(decayAlpha), zeroOffset(offset) {}

    float update(uint16_t rawAdc) {
        float inputVal = abs((float)rawAdc - (float)zeroOffset);
        float decayedVal = state * alpha;

        if (inputVal > decayedVal) {
            state = inputVal;
        } else {
            state = decayedVal;
        }

        return state;
    }

    void reset() {
        state = 0.0f;
    }
};
