// Обчислення калібрування та перетворення вибірок мовою C++
#include <cmath>
#include <cstdint>

class Ina219Math {
public:
    struct CalibData {
        float currentLsb;
        float powerLsb;
        uint16_t calValue;
    };

    static CalibData computeCalibration(float rShunt, float maxCurrent) {
        float minLsb = maxCurrent / 32768.0f;
        float currentLsb = std::ceil(minLsb * 10000.0f) / 10000.0f;
        float powerLsb = 20.0f * currentLsb;
        uint16_t calValue = static_cast<uint16_t>(std::trunc(0.04096f / (currentLsb * rShunt)));

        return {currentLsb, powerLsb, calValue};
    }

    static float busRawToVolts(uint16_t busReg) {
        return static_cast<float>(busReg >> 3) * 0.004f;
    }

    static float currentRawToAmps(int16_t currentReg, float currentLsb) {
        return static_cast<float>(currentReg) * currentLsb;
    }
};
