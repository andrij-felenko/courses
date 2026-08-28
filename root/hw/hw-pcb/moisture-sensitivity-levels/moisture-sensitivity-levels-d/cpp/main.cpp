#include <iostream>
#include <string_view>
#include <chrono>
#include <optional>
#include <array>
#include <cmath>

namespace msl {

using namespace std::chrono_literals;

enum class Level {
    Msl1, Msl2, Msl2a, Msl3, Msl4, Msl5, Msl5a, Msl6
};

struct Spec {
    Level level;
    std::string_view name;
    std::chrono::hours floor_life;
    double max_temp_c;
    double max_rh_percent;
};

constexpr std::array<Spec, 8> Specs = {{
    { Level::Msl1,  "MSL 1",  std::chrono::hours::max(), 30.0, 85.0 },
    { Level::Msl2,  "MSL 2",  8760h,                     30.0, 60.0 },
    { Level::Msl2a, "MSL 2a", 672h,                      30.0, 60.0 },
    { Level::Msl3,  "MSL 3",  168h,                      30.0, 60.0 },
    { Level::Msl4,  "MSL 4",  72h,                       30.0, 60.0 },
    { Level::Msl5,  "MSL 5",  48h,                       30.0, 60.0 },
    { Level::Msl5a, "MSL 5a", 24h,                       30.0, 60.0 },
    { Level::Msl6,  "MSL 6",  6h,                        30.0, 60.0 }
}};

[[nodiscard]] constexpr double calculate_desiccant_units(
    double bag_length_in, double bag_width_in,
    double wvtr_g_per_100sqin_day, double shelf_life_months) noexcept {
    const double total_area_sqin = 2.0 * bag_length_in * bag_width_in;
    constexpr double d_cap = 0.16; // Вологоємність при 10% RH
    return (0.011 * total_area_sqin * wvtr_g_per_100sqin_day * shelf_life_months) / d_cap;
}

[[nodiscard]] double calculate_derating_factor(double ambient_temp_c, double ambient_rh_percent) noexcept {
    const double p_sat = 0.61078 * std::exp((17.27 * ambient_temp_c) / (ambient_temp_c + 237.3));
    const double p_actual = (ambient_rh_percent / 100.0) * p_sat;
    const double p_sat_nominal = 0.61078 * std::exp((17.27 * 30.0) / (30.0 + 237.3));
    const double p_nominal = 0.60 * p_sat_nominal;
    return p_actual / p_nominal;
}

struct EvaluationResult {
    bool requires_baking{false};
    bool fully_recovered{false};
    std::chrono::hours remaining_floor_life{0h};
    std::chrono::hours required_dry_cabinet_time{0h};
    std::string_view action_message;
};

[[nodiscard]] EvaluationResult evaluate_exposure(
    Level level,
    std::chrono::hours exposed,
    std::chrono::hours in_dry_cabinet,
    double dry_cabinet_rh,
    double ambient_temp_c = 30.0,
    double ambient_rh_percent = 60.0) noexcept {
    
    const auto& spec = Specs[static_cast<size_t>(level)];
    
    if (spec.floor_life == std::chrono::hours::max()) {
        return {
            .requires_baking = false,
            .fully_recovered = true,
            .remaining_floor_life = std::chrono::hours::max(),
            .required_dry_cabinet_time = 0h,
            .action_message = "MSL 1: Необмежений строк цехового життя."
        };
    }

    const double derating = calculate_derating_factor(ambient_temp_c, ambient_rh_percent);
    const auto effective_exposed_h = static_cast<int64_t>(std::ceil(exposed.count() * derating));
    const auto effective_exposed = std::chrono::hours(effective_exposed_h);

    if (effective_exposed > spec.floor_life) {
        return {
            .requires_baking = true,
            .fully_recovered = false,
            .remaining_floor_life = 0h,
            .required_dry_cabinet_time = 0h,
            .action_message = "КРИТИЧНО: Floor Life вичерпано! Потрібне сушіння при 125 °C або 40 °C."
        };
    }

    const auto max_short_exp = (level <= Level::Msl3) ? 12h : 8h;

    if (dry_cabinet_rh <= 5.0) {
        const auto needed_dry = exposed * 5;
        if (exposed <= max_short_exp && in_dry_cabinet >= needed_dry) {
            return {
                .requires_baking = false,
                .fully_recovered = true,
                .remaining_floor_life = spec.floor_life,
                .required_dry_cabinet_time = needed_dry,
                .action_message = "Успіх: Floor Life повністю відновлено за правилом 5x."
            };
        }
        return {
            .requires_baking = false,
            .fully_recovered = false,
            .remaining_floor_life = spec.floor_life - effective_exposed,
            .required_dry_cabinet_time = needed_dry,
            .action_message = "У процесі сухого відновлення (RH < 5%)."
        };
    }

    if (dry_cabinet_rh <= 10.0) {
        return {
            .requires_baking = false,
            .fully_recovered = false,
            .remaining_floor_life = spec.floor_life - effective_exposed,
            .required_dry_cabinet_time = 0h,
            .action_message = "Суха шафа RH < 10%: лічильник на паузі, але не відновлюється."
        };
    }

    const auto total_spent = effective_exposed + in_dry_cabinet;
    if (total_spent >= spec.floor_life) {
        return {
            .requires_baking = true,
            .fully_recovered = false,
            .remaining_floor_life = 0h,
            .required_dry_cabinet_time = 0h,
            .action_message = "УВАГА: Вологе сховище, строк вичерпано!"
        };
    }

    return {
        .requires_baking = false,
        .fully_recovered = false,
        .remaining_floor_life = spec.floor_life - total_spent,
        .required_dry_cabinet_time = 0h,
        .action_message = "Увага: Вологість сховища > 10%, Floor Life продовжує втрачатися."
    };
}

} // namespace msl
