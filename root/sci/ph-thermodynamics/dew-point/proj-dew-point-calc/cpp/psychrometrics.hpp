// psychrometrics.hpp — Ідіоматичний C++17 клас психометрії
#pragma once

#include <cmath>
#include <optional>
#include <system_error>
#include <string_view>

namespace physics::thermal {

struct PsychroResult {
    double air_temp_c;
    double rel_humidity_pct;
    double dew_point_c;
    double frost_point_c;
    double sat_vapor_press_kpa;
    double vapor_press_kpa;
};

class Psychrometrics {
public:
    static constexpr double kMagnusA = 0.61078;
    static constexpr double kMagnusB = 17.27;
    static constexpr double kMagnusC = 237.3;

    static constexpr double kIceB = 21.875;
    static constexpr double kIceC = 265.5;

    [[nodiscard]] static std::optional<PsychroResult> compute(double temp_c, double rh_pct) noexcept {
        if (temp_c < -50.0 || temp_c > 80.0 || rh_pct < 0.0 || rh_pct > 100.0) {
            return std::nullopt;
        }

        PsychroResult res{};
        res.air_temp_c = temp_c;
        res.rel_humidity_pct = rh_pct;

        res.sat_vapor_press_kpa = kMagnusA * std::exp((kMagnusB * temp_c) / (kMagnusC + temp_c));
        res.vapor_press_kpa = (rh_pct / 100.0) * res.sat_vapor_press_kpa;

        if (rh_pct < 0.001) {
            res.dew_point_c = -50.0;
            res.frost_point_c = -50.0;
        } else {
            const double alpha = ((kMagnusB * temp_c) / (kMagnusC + temp_c)) + std::log(rh_pct / 100.0);
            res.dew_point_c = (kMagnusC * alpha) / (kMagnusB - alpha);

            const double alpha_ice = ((kIceB * temp_c) / (kIceC + temp_c)) + std::log(rh_pct / 100.0);
            res.frost_point_c = (kIceC * alpha_ice) / (kIceB - alpha_ice);
        }

        return res;
    }
};

class AntiCondensationController {
public:
    explicit AntiCondensationController(double margin_on_c = 2.0, double margin_off_c = 4.0)
        : margin_on_{margin_on_c}, margin_off_{margin_off_c}, heater_state_{false} {}

    bool update(double surface_temp_c, double dew_point_c) noexcept {
        const double delta_t = surface_temp_c - dew_point_c;
        if (delta_t <= margin_on_) {
            heater_state_ = true;
        } else if (delta_t >= margin_off_) {
            heater_state_ = false;
        }
        return heater_state_;
    }

    [[nodiscard]] bool is_heater_active() const noexcept { return heater_state_; }

private:
    double margin_on_;
    double margin_off_;
    bool heater_state_;
};

} // namespace physics::thermal
