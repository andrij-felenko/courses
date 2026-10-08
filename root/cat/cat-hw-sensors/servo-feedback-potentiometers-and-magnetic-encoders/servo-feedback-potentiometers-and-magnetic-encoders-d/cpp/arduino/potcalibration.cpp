// Калібрування та масштабування давачів кута положення в C++ (Arduino)
#include <Arduino.h>

struct PotCalibration {
    uint16_t adcMin;
    uint16_t adcMax;
    float angleMin;
    float angleMax;
    uint16_t zeroOffset;
};

class ServoFeedbackCalibrator {
public:
    static float getPotAngle(uint16_t rawAdc, const PotCalibration& cal) {
        uint16_t clampedAdc = constrain(rawAdc, cal.adcMin, cal.adcMax);
        int32_t correctedAdc = (int32_t)clampedAdc - cal.zeroOffset;
        if (correctedAdc < (int32_t)cal.adcMin) {
            correctedAdc = cal.adcMin;
        }

        float kScale = (cal.angleMax - cal.angleMin) / static_cast<float>(cal.adcMax - cal.adcMin);
        return cal.angleMin + (static_cast<float>(correctedAdc) - static_cast<float>(cal.adcMin)) * kScale;
    }

    static float getMagneticAngle(uint16_t raw14bit, uint16_t zeroOffset14bit) {
        int32_t diff = static_cast<int32_t>(raw14bit) - static_cast<int32_t>(zeroOffset14bit);
        if (diff < 0) {
            diff += 16384;
        }
        uint16_t corrected = static_cast<uint16_t>(diff & 0x3FFF);
        return (static_cast<float>(corrected) * 360.0f) / 16384.0f;
    }
};
