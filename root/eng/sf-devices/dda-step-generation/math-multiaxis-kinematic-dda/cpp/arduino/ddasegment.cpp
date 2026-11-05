#include <Arduino.h>

const uint8_t NUM_AXES = 3;
const uint8_t PIN_STEP_X = 2;
const uint8_t PIN_STEP_Y = 3;
const uint8_t PIN_STEP_Z = 4;

struct DdaSegment {
    int32_t delta[NUM_AXES];
    int32_t accumulator[NUM_AXES];
    uint8_t leadAxis;
    uint32_t totalSteps;
    uint32_t currentStep;
};

volatile DdaSegment currentSeg;
volatile bool isExecuting = false;

void inline stepAllAxesDirect(uint8_t stepMask) {
    PORTD |= stepMask;
    PORTD &= ~stepMask;
}

void onHardwareTimerTick() {
    if (!isExecuting) return;

    if (currentSeg.currentStep < currentSeg.totalSteps) {
        uint8_t mask = 0;
        for (uint8_t i = 0; i < NUM_AXES; i++) {
            if (i == currentSeg.leadAxis) {
                mask |= (1 << (PIN_STEP_X + i));
            } else {
                currentSeg.accumulator[i] += currentSeg.delta[i];
                if (currentSeg.accumulator[i] >= (int32_t)currentSeg.totalSteps) {
                    mask |= (1 << (PIN_STEP_X + i));
                    currentSeg.accumulator[i] -= currentSeg.totalSteps;
                }
            }
        }
        stepAllAxesDirect(mask);
        currentSeg.currentStep++;
    } else {
        isExecuting = false;
    }
}
