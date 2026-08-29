#include "budget/thermal_model.hpp"

#include <algorithm>

namespace budget {

Budget ThermalModel::sample(double ambient_c, double power_w) noexcept
{
    ambient_c_  = ambient_c;
    power_w_    = power_w;
    junction_c_ = junction(ambient_c, power_w, limits_.rth_ja_c_per_w);
    peak_c_     = std::max(peak_c_, junction_c_);

    if (junction_c_ >= limits_.tj_max_c) {
        ++trips_;
        throttled_ = true;
        return Budget::ThermalTrip | Budget::ThermalWarning;
    }

    if (junction_c_ >= warn_threshold_c()) {
        throttled_ = true;
        return Budget::ThermalWarning;
    }

    // Тривогу знімаємо лише з гістерезисом: без нього вузол смикався б між
    // повним і зниженим навантаженням на кожному відліку.
    if (throttled_ && junction_c_ < warn_threshold_c() - limits_.hysteresis_c) {
        throttled_ = false;
    }

    return throttled_ ? Budget::ThermalWarning : Budget::None;
}

} // namespace budget
