#include <cstdint>
#include <optional>
#include <algorithm>

namespace navigation {

struct RangeMeasurement {
    uint16_t anchor_id{0};
    float    distance_m{0.0f};
    float    variance_m2{0.0025f}; // Базова дисперсія (5 см)^2
};

class UwbMeasurementFilter {
public:
    static constexpr float MinValidDistanceM = 0.1f;
    static constexpr float MaxValidDistanceM = 80.0f;
    static constexpr float NlosRejectThresholdDb = 10.0f;
    static constexpr float NlosWarnThresholdDb   = 6.0f;

    [[nodiscard]] static std::optional<RangeMeasurement> process(
        uint16_t anchor_id, float raw_dist_m, float fpp_dbm, float rxp_dbm) noexcept {

        if (raw_dist_m < MinValidDistanceM || raw_dist_m > MaxValidDistanceM) {
            return std::nullopt;
        }

        const float nlos_diff = rxp_dbm - fpp_dbm;

        if (nlos_diff > NlosRejectThresholdDb) {
            // Hard NLOS: повністю відкидаємо хибний замір
            return std::nullopt;
        }

        float variance = 0.0025f; // (5 см)^2 для прямої видимості LOS
        if (nlos_diff > NlosWarnThresholdDb) {
            // Soft NLOS: збільшуємо невизначеність для фільтра Калмана
            variance = 0.0400f;   // (20 см)^2
        }

        return RangeMeasurement{
            .anchor_id   = anchor_id,
            .distance_m  = raw_dist_m,
            .variance_m2 = variance
        };
    }
};

} // namespace navigation
