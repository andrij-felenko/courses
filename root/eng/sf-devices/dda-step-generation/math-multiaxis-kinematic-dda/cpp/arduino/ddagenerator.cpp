#include <Arduino.h>

class DdaGenerator {
public:
    static const uint8_t NUM_AXES = 3;

    struct Axis {
        int32_t delta;
        int32_t accumulator;
        int8_t direction;
    };

    Axis axes[NUM_AXES];
    uint8_t leadAxis;
    uint32_t totalSteps;
    uint32_t currentStep;

    void init(int32_t dx, int32_t dy, int32_t dz) {
        int32_t deltas[NUM_AXES] = {dx, dy, dz};
        int32_t maxDelta = 0;
        leadAxis = 0;

        for (uint8_t i = 0; i < NUM_AXES; i++) {
            if (deltas[i] < 0) {
                axes[i].direction = -1;
                axes[i].delta = -deltas[i];
            } else {
                axes[i].direction = 1;
                axes[i].delta = deltas[i];
            }

            if (axes[i].delta > maxDelta) {
                maxDelta = axes[i].delta;
                leadAxis = i;
            }
        }

        totalSteps = maxDelta;
        currentStep = 0;

        for (uint8_t i = 0; i < NUM_AXES; i++) {
            axes[i].accumulator = maxDelta / 2;
        }
    }

    bool stepTick(bool stepOut[NUM_AXES]) {
        if (currentStep >= totalSteps) {
            return false;
        }

        for (uint8_t i = 0; i < NUM_AXES; i++) {
            stepOut[i] = false;
            if (i == leadAxis) {
                stepOut[i] = true;
            } else {
                axes[i].accumulator += axes[i].delta;
                if (axes[i].accumulator >= (int32_t)totalSteps) {
                    stepOut[i] = true;
                    axes[i].accumulator -= totalSteps;
                }
            }
        }

        currentStep++;
        return true;
    }
};
