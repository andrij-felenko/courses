#pragma once

#include <expected>
#include <optional>
#include <utility>
#include <variant>

#include "mission.hpp"

namespace mission {

// Літак: P = A*v^3 + B/v.
struct FixedWing {
    float wing_area_m2{0.45f};
    float cd0{0.045f};
    float span_m{1.70f};
    float oswald_e{0.80f};
};

// Мультикоптер: P = P_hover + k*v^3.
struct Multirotor {
    float disk_area_m2{0.30f};
    float body_drag_k{0.05f};
};

using Aerodynamics = std::variant<FixedWing, Multirotor>;

[[nodiscard]] float air_density(float alt_msl_m) noexcept;

class Aircraft {
public:
    struct Spec {
        Aerodynamics aerodynamics{FixedWing{}};
        float mass_kg{4.5f};
        float eta_prop{0.58f};        // ККД гвинтомоторної групи з регуляторами
        float avionics_w{18.0f};      // не залежить від швидкості
        float airspeed_min_mps{12.0f};
        float airspeed_max_mps{24.0f};
        float max_climb_mps{3.5f};
    };

    explicit Aircraft(Spec spec) : spec_(spec) {}

    [[nodiscard]] const Spec& spec() const noexcept { return spec_; }

    [[nodiscard]] float level_power_w(float airspeed_mps, float rho) const noexcept;
    [[nodiscard]] float climb_power_w(float climb_rate_mps) const noexcept;
    [[nodiscard]] float loiter_power_w(float rho) const noexcept;

    // Швидкості мінімальної потужності й максимальної дальності визначені
    // лише для літака — у коптера цих понять немає.
    [[nodiscard]] std::optional<float> best_endurance_speed(float rho) const noexcept;
    [[nodiscard]] std::optional<float> best_range_speed(float rho) const noexcept;

private:
    [[nodiscard]] std::pair<float, float> polar_coefficients(const FixedWing& wing,
                                                             float rho) const noexcept;
    Spec spec_;
};

class Battery {
public:
    struct Spec {
        float nominal_v{22.2f};
        float capacity_ah{5.2f};
        float peukert_k{1.08f};       // 1.05...1.10 LiPo, 1.15...1.25 Li-Ion
        float ref_current_a{2.0f};
        float internal_r_ohm{0.05f};
        float pack_temp_c{8.0f};
        float health{0.92f};
        float reserve_margin{0.25f};
    };

    explicit Battery(Spec spec) : spec_(spec) {}

    [[nodiscard]] const Spec& spec() const noexcept { return spec_; }
    [[nodiscard]] float nominal_wh() const noexcept { return spec_.nominal_v * spec_.capacity_ah; }
    [[nodiscard]] float temperature_factor() const noexcept;

    // Струм під навантаженням з урахуванням просадки на R_int.
    [[nodiscard]] std::expected<float, Failure> current_a(float load_w) const noexcept;

    // Скільки пакет справді віддасть за такого середнього струму
    // (Пейкерт + температура + знос), без чіпання резерву.
    [[nodiscard]] float delivered_wh(float avg_current_a) const noexcept;

    // Те саме мінус недоторканний резерв — це і є бюджет місії.
    [[nodiscard]] float usable_wh(float avg_current_a) const noexcept;

private:
    Spec spec_;
};

}  // namespace mission
