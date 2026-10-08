#include <cstdint>
#include <array>
#include <cmath>
#include <algorithm>

template <std::size_t LutSize = 17>
class RvdtSignalProcessor {
public:
    struct CalibrationData {
        float nullOffsetRad{0.0f};
        float sensitivityPerRad{1.0f};
        std::array<float, LutSize> lutAnglesDeg{};
        std::array<float, LutSize> lutCorrectionsDeg{};
    };

    explicit RvdtSignalProcessor(CalibrationData cal) : cal_(std::move(cal)) {}

    float calculateAngleDeg(std::uint16_t rawVs1, std::uint16_t rawVs2) const {
        const float v1 = static_cast<float>(rawVs1);
        const float v2 = static_cast<float>(rawVs2);
        const float sum = v1 + v2;

        if (sum < 1.0f) {
            return 0.0f; // Виявлення відсутності сигналу несучої
        }

        const float ratio = (v1 - v2) / sum;
        const float rawAngleRad = ratio / cal_.sensitivityPerRad;
        const float angleRad = rawAngleRad - cal_.nullOffsetRad;
        const float angleDeg = angleRad * (180.0f / 3.14159265f);

        return applyLutCorrection(angleDeg);
    }

private:
    CalibrationData cal_;

    float applyLutCorrection(float angleDeg) const {
        if (angleDeg <= cal_.lutAnglesDeg.front()) {
            return angleDeg + cal_.lutCorrectionsDeg.front();
        }
        if (angleDeg >= cal_.lutAnglesDeg.back()) {
            return angleDeg + cal_.lutCorrectionsDeg.back();
        }

        auto it = std::lower_bound(cal_.lutAnglesDeg.begin(), cal_.lutAnglesDeg.end(), angleDeg);
        std::size_t idx = std::distance(cal_.lutAnglesDeg.begin(), it);
        if (idx > 0) {
            idx--;
        }

        const float span = cal_.lutAnglesDeg[idx + 1] - cal_.lutAnglesDeg[idx];
        const float t = (span > 0.0001f) ? (angleDeg - cal_.lutAnglesDeg[idx]) / span : 0.0f;
        const float corr = cal_.lutCorrectionsDeg[idx] + t * (cal_.lutCorrectionsDeg[idx + 1] - cal_.lutCorrectionsDeg[idx]);

        return angleDeg + corr;
    }
};
