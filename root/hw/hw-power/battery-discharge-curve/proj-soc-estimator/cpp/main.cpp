// soc_estimator.hpp / .cpp — C++20 версія класу оцінки стану батареї
#include <iostream>
#include <vector>
#include <array>
#include <algorithm>
#include <cmath>
#include <optional>

namespace bms {

struct OcvPoint {
    float soc_percent;
    float ocv_volts;
};

class BatteryEstimator {
public:
    BatteryEstimator(float capacity_ah, float r_internal_ohm, float v_cutoff)
        : capacity_ah_(capacity_ah),
          r_internal_(r_internal_ohm),
          v_cutoff_(v_cutoff),
          current_soc_(1.0f),
          accumulated_mah_(0.0f) {}

    // Кусково-лінійна інтерполяція за кривою OCV
    [[nodiscard]] static float ocv_to_soc(float ocv_volts) noexcept {
        constexpr std::array<OcvPoint, 11> lookup = {{
            {  0.0f, 3.00f}, { 10.0f, 3.45f}, { 20.0f, 3.68f},
            { 30.0f, 3.74f}, { 40.0f, 3.77f}, { 50.0f, 3.83f},
            { 60.0f, 3.83f}, { 70.0f, 3.92f}, { 80.0f, 4.02f},
            { 90.0f, 4.11f}, {100.0f, 4.20f}
        }};

        if (ocv_volts <= lookup.front().ocv_volts) return 0.0f;
        if (ocv_volts >= lookup.back().ocv_volts) return 100.0f;

        auto it = std::upper_bound(lookup.begin(), lookup.end(), ocv_volts,
            [](float val, const OcvPoint& pt) { return val < pt.ocv_volts; });

        const auto& p2 = *it;
        const auto& p1 = *(it - 1);

        float ratio = (ocv_volts - p1.ocv_volts) / (p2.ocv_volts - p1.ocv_volts);
        return p1.soc_percent + ratio * (p2.soc_percent - p1.soc_percent);
    }

    // Оновлення стану алгоритму за такт вимірювання
    [[nodiscard]] bool update(float v_cell, float current_amps, float dt_sec) noexcept {
        if (v_cell <= v_cutoff_) {
            current_soc_ = 0.0f;
            return false; // Досягнуто граничну відсічку
        }

        float delta_ah = (current_amps * dt_sec) / 3600.0f;
        accumulated_mah_ += delta_ah * 1000.0f;

        float soc_coulomb = std::clamp(current_soc_ - (delta_ah / capacity_ah_), 0.0f, 1.0f);

        // Корекція за OCV при малому струмі розряду
        if (std::abs(current_amps) < 0.05f) {
            float ocv_est = v_cell + current_amps * r_internal_;
            float soc_ocv = ocv_to_soc(ocv_est) / 100.0f;
            current_soc_ = 0.95f * soc_coulomb + 0.05f * soc_ocv;
        } else {
            current_soc_ = soc_coulomb;
        }

        return true;
    }

    [[nodiscard]] float get_soc_percent() const noexcept { return current_soc_ * 100.0f; }
    [[nodiscard]] float get_consumed_mah() const noexcept { return accumulated_mah_; }

private:
    float capacity_ah_;
    float r_internal_;
    float v_cutoff_;
    float current_soc_;
    float accumulated_mah_;
};

} // namespace bms
