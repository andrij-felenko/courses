#include <cstdint>

enum class StationStatus {
    Ok,
    SensorErrorSE,
    HeaterErrorHE
};

class BakuSafetyEvaluator {
public:
    StationStatus evaluate(std::uint16_t adcVal, float currentTemp, float targetTemp, std::uint32_t heatingTicks) const noexcept {
        if (adcVal < 15 || adcVal > 1005) {
            return StationStatus::SensorErrorSE;
        }
        if (heatingTicks > 600 && (targetTemp - currentTemp > 45.0f)) {
            return StationStatus::HeaterErrorHE;
        }
        return StationStatus::Ok;
    }
};
