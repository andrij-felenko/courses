#pragma once

#include "types.hpp"

namespace fc {

// Навігаційний контур утримання лінії шляху з двома захистами на час
// перехоплення: заморожуванням інтегратора й підтягуванням уставки.
class NavLoop {
public:
    struct Setpoint {
        float leg_x{}, leg_y{};    // початок поточного відрізка
        float wp_x{}, wp_y{};      // поворотний пункт маршруту
        float alt_target{};        // м
        float airspeed_target{};   // м/с
    };

    struct Gains {
        float kp_xte{0.9f};   // зовнішній контур: бічне відхилення → курс
        float ki_xte{0.6f};
        float kd_xte{0.4f};
        float i_max{30.0f};   // межа накопичення, градуси зносу
        Seconds decay_tau{0.4f};
        float k_track{1.5f};  // внутрішній контур: похибка курсу → крен
        float kp_alt{0.6f};
        float kp_spd{0.03f};
        float throttle_trim{0.62f};
    };

    explicit NavLoop(Setpoint sp, Gains gains = {}) noexcept : sp_(sp), k_(gains) {}

    // frozen приходить зі Status::freeze_nav.
    ControlCommand step(const VehicleState& st, bool frozen, Seconds dt) noexcept;

    [[nodiscard]] float crosstrack(const VehicleState& st) const noexcept;
    [[nodiscard]] float bearing_deg() const noexcept;
    [[nodiscard]] float integral() const noexcept { return integral_; }

    // Вимикається лише для того, щоб показати наслідки його відсутності.
    void set_anti_windup(bool on) noexcept { anti_windup_ = on; }

private:
    static constexpr float kTrackLimitDeg = 30.0f;
    static constexpr float kRollLimitDeg = 25.0f;
    static constexpr float kPitchUpDeg = 10.0f;
    static constexpr float kPitchDownDeg = -8.0f;

    Setpoint sp_;
    Gains k_;
    float integral_{0.0f};
    float prev_xte_{0.0f};
    bool have_prev_{false};
    bool anti_windup_{true};
};

} // namespace fc
