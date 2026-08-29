#include "altitude_fusion.hpp"

#include <cmath>

namespace fc {

void AltitudeFusion::update(std::optional<float> baro_alt, float acc_up, float dt) noexcept
{
    if (!(dt > 0.0f)) return;

    if (!primed_) {
        // Перший придатний відлік барометра задає початок відліку.
        if (baro_alt && std::isfinite(*baro_alt)) {
            alt_ = *baro_alt;
            climb_ = 0.0f;
            primed_ = true;
        }
        return;
    }

    const float acc = std::isfinite(acc_up) ? acc_up : 0.0f;

    // Прогноз за акселерометром
    alt_ += climb_ * dt + 0.5f * acc * dt * dt;
    climb_ += acc * dt;

    // Корекція за барометром
    if (!baro_alt || !std::isfinite(*baro_alt)) return;
    if (std::fabs(*baro_alt - alt_) > spike_limit_) {
        // Стрибок на десятки метрів за такт — це не політ, а поштовх тиску.
        ++rejected_;
        return;
    }
    const float err = *baro_alt - alt_;
    alt_ += k_alt_ * err * dt;
    climb_ += k_climb_ * err * dt;
}

}  // namespace fc
