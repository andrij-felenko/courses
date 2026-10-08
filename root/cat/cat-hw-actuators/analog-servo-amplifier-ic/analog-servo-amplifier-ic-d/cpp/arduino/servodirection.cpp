#include <Arduino.h>

enum class ServoDirection {
    Stop,
    Clockwise,
    CounterClockwise
};

class ServoDeadbandEvaluator {
private:
    uint32_t deadbandUs;

public:
    explicit ServoDeadbandEvaluator(uint32_t deadbandUs = 5)
        : deadbandUs(deadbandUs) {}

    ServoDirection evaluate(uint32_t pulseInUs, uint32_t pulseFbUs) const {
        int32_t diff = static_cast<int32_t>(pulseInUs) - static_cast<int32_t>(pulseFbUs);

        if (diff > static_cast<int32_t>(deadbandUs)) {
            return ServoDirection::Clockwise;
        } else if (diff < -static_cast<int32_t>(deadbandUs)) {
            return ServoDirection::CounterClockwise;
        }
        return ServoDirection::Stop;
    }
};
