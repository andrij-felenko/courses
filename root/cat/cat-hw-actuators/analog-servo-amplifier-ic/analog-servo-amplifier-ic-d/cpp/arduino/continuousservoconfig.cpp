#include <Arduino.h>

struct ContinuousServoConfig {
    uint32_t neutralUs{1500};
    uint32_t deadbandUs{10};
    uint32_t maxDevUs{400};
};

struct ContinuousServoState {
    int8_t speedPct{0};
    bool isInDeadband{true};
};

class ContinuousServoMapper {
private:
    ContinuousServoConfig config;

public:
    explicit ContinuousServoMapper(const ContinuousServoConfig& cfg) : config(cfg) {}

    ContinuousServoState mapPulseToDrive(uint32_t pulseUs) const {
        ContinuousServoState state;
        int32_t diff = static_cast<int32_t>(pulseUs) - static_cast<int32_t>(config.neutralUs);

        if (diff > static_cast<int32_t>(config.deadbandUs)) {
            state.isInDeadband = false;
            int32_t activeDev = diff - static_cast<int32_t>(config.deadbandUs);
            int32_t maxActive = static_cast<int32_t>(config.maxDevUs) - static_cast<int32_t>(config.deadbandUs);
            int32_t speed = (activeDev * 100) / maxActive;
            state.speedPct = (speed > 100) ? 100 : static_cast<int8_t>(speed);
        } else if (diff < -static_cast<int32_t>(config.deadbandUs)) {
            state.isInDeadband = false;
            int32_t activeDev = (-diff) - static_cast<int32_t>(config.deadbandUs);
            int32_t maxActive = static_cast<int32_t>(config.maxDevUs) - static_cast<int32_t>(config.deadbandUs);
            int32_t speed = (activeDev * 100) / maxActive;
            state.speedPct = (speed > 100) ? -100 : static_cast<int8_t>(-speed);
        }

        return state;
    }
};
