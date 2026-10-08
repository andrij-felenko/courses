#include <algorithm>
#include <stdint.h>

class SmoothServoController {
private:
    uint16_t minPulseUs;
    uint16_t maxPulseUs;
    uint16_t maxStepUs;    // Максимальна зміна мкс за один крок
    float currentPulseUs;
    uint16_t targetPulseUs;

public:
    SmoothServoController(uint16_t minP, uint16_t maxP, uint16_t maxStep)
        : minPulseUs(minP), maxPulseUs(maxP), maxStepUs(maxStep),
          currentPulseUs((minP + maxP) / 2), targetPulseUs((minP + maxP) / 2) {}

    // Встановлення нової цільової уставки з обмеженням
    void setTarget(uint16_t targetUs) {
        if (targetUs < minPulseUs) targetUs = minPulseUs;
        if (targetUs > maxPulseUs) targetUs = maxPulseUs;
        targetPulseUs = targetUs;
    }

    // Періодична функція оновлення (викликається у таймерному циклі)
    uint16_t update() {
        float error = (float)targetPulseUs - currentPulseUs;
        
        if (std::abs(error) <= maxStepUs) {
            currentPulseUs = (float)targetPulseUs;
        } else {
            if (error > 0) {
                currentPulseUs += maxStepUs;
            } else {
                currentPulseUs -= maxStepUs;
            }
        }
        return (uint16_t)currentPulseUs;
    }
};
