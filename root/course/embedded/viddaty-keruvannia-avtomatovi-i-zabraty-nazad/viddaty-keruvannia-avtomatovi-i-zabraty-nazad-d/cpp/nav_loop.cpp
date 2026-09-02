#include "nav_loop.hpp"

#include <algorithm>
#include <cmath>

namespace fc {

float NavLoop::bearing_deg() const noexcept {
    return std::atan2(sp_.wp_y - sp_.leg_y, sp_.wp_x - sp_.leg_x) * kRad2Deg;
}

float NavLoop::crosstrack(const VehicleState& st) const noexcept {
    float dx = sp_.wp_x - sp_.leg_x;
    float dy = sp_.wp_y - sp_.leg_y;
    const float len = std::hypot(dx, dy);
    if (len < 1e-3f) return 0.0f; // вироджений відрізок — відхилятися нема від чого
    dx /= len;
    dy /= len;
    // Векторний добуток: додатне значення — апарат ліворуч від лінії.
    return dx * (st.y - sp_.leg_y) - dy * (st.x - sp_.leg_x);
}

ControlCommand NavLoop::step(const VehicleState& st, bool frozen, Seconds dt_raw) noexcept {
    const float dt = std::clamp(dt_raw.count(), 0.0002f, 0.1f);
    const bool freeze = frozen && anti_windup_;

    float xte = crosstrack(st);
    float d_xte = have_prev_ ? (xte - prev_xte_) / dt : 0.0f;
    prev_xte_ = xte;
    have_prev_ = true;

    if (freeze) {
        // Керує пілот. Інтегрування зупинено, накопичене згасає за τ, а лінія
        // шляху перекладається так, щоб проходити через поточну точку: коли
        // автомат отримає керування назад, його похибка дорівнюватиме нулю.
        integral_ *= std::exp(-dt / k_.decay_tau.count());
        sp_.leg_x = st.x;
        sp_.leg_y = st.y;
        sp_.alt_target = st.alt;
        xte = 0.0f;
        d_xte = 0.0f;
        prev_xte_ = 0.0f;
    } else {
        integral_ = std::clamp(integral_ + k_.ki_xte * xte * dt, -k_.i_max, k_.i_max);
    }

    // Інтеграл тут має фізичний сенс кута зносу: на бічному вітрі він сходиться
    // до кута крабування, потрібного, щоб триматися лінії.
    const float corr = std::clamp(k_.kp_xte * xte + integral_ + k_.kd_xte * d_xte,
                                  -kTrackLimitDeg, kTrackLimitDeg);
    const float heading_demand = bearing_deg() - corr;

    ControlCommand u;
    u.roll = std::clamp(k_.k_track * wrap180(st.heading_deg - heading_demand),
                        -kRollLimitDeg, kRollLimitDeg);
    u.pitch = std::clamp(k_.kp_alt * (sp_.alt_target - st.alt), kPitchDownDeg, kPitchUpDeg);
    u.yaw = 0.0f; // розворот координований креном, окремої команди рискання нема
    u.throttle = std::clamp(k_.throttle_trim + k_.kp_spd * (sp_.airspeed_target - st.airspeed),
                            0.0f, 1.0f);
    return u;
}

} // namespace fc
