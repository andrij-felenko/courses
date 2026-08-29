#include "uav/return_budget.hpp"

#include <algorithm>
#include <cmath>

namespace uav::nav {
namespace {

// Радіус домашньої зони: ближче рахувати повернення немає сенсу
constexpr float kHomeRadiusM = 15.0f;
// Мінімальна шляхова швидкість, нижче якої час польоту прямує в нескінченність
constexpr float kMinGroundSpeedMs = 1.0f;

[[nodiscard]] constexpr float clamp(float value, float low, float high) noexcept {
    return std::max(low, std::min(value, high));
}

[[nodiscard]] bool isFinite(Vec3 v) noexcept {
    return std::isfinite(v.north) && std::isfinite(v.east) && std::isfinite(v.down);
}

[[nodiscard]] bool isSane(const Telemetry& t) noexcept {
    if (!isFinite(t.position) || !isFinite(t.home)) return false;
    if (!std::isfinite(t.wind.north) || !std::isfinite(t.wind.east)) return false;
    if (!std::isfinite(t.voltage_v) || !std::isfinite(t.r_internal_ohms)) return false;
    if (!std::isfinite(t.energy_remaining_wh)) return false;
    return t.voltage_v >= 0.0f && t.r_internal_ohms >= 0.0f && t.energy_remaining_wh >= 0.0f;
}

[[nodiscard]] bool isSane(const Config& c) noexcept {
    if (c.v_air_min_ms <= 0.0f || c.v_air_max_ms < c.v_air_min_ms) return false;
    if (c.v_best_range_still_ms <= 0.0f) return false;
    if (c.c_ind <= 0.0f || c.c_par <= 0.0f) return false;
    if (c.nominal_energy_wh <= 0.0f || c.cell_count == 0 || c.cell_v_cutoff <= 0.0f) return false;
    if (c.reserve_margin_ratio < 0.0f || c.filter_time_constant_s <= 0.0f) return false;
    return c.t_land_maneuver_sec >= 0.0f && c.p_hover_watts >= 0.0f;
}

struct WindProjection {
    float headwind_ms{0.0f};   // додатне — вітер у лоб
    float crosswind_ms{0.0f};  // завжди невід'ємне
};

// Скалярний добуток дає зустрічну складову (зі знаком «мінус», бо wind — це
// куди дме повітря), псевдоскалярний — бокову.
[[nodiscard]] WindProjection projectWind(Vec2 wind, Vec2 course) noexcept {
    return WindProjection{
        .headwind_ms = -(wind.north * course.north + wind.east * course.east),
        .crosswind_ms = std::abs(wind.north * course.east - wind.east * course.north)};
}

} // namespace

std::expected<Estimator, Error> Estimator::create(const Config& config) noexcept {
    if (!isSane(config)) {
        return std::unexpected{Error::InvalidConfig};
    }
    return Estimator{config};
}

void Estimator::reset() noexcept {
    filtered_return_wh_ = 0.0f;
    state_ = State::Ok;
}

float Estimator::optimalAirspeed(float headwind_ms) const noexcept {
    float v_opt = config_.v_best_range_still_ms;

    if (headwind_ms > 0.0f) {
        // Проти зустрічного вітру швидкість збільшуємо: коротший час у повітрі
        // окупає більшу паразитну потужність (k ≈ 0.4 для типової поляри).
        v_opt += 0.40f * headwind_ms;
    } else {
        // При попутному — сповільнюємось до економічного режиму.
        v_opt += 0.25f * headwind_ms;
    }

    return clamp(v_opt, config_.v_air_min_ms, config_.v_air_max_ms);
}

float Estimator::cruisePower(float v_air_ms) const noexcept {
    return config_.c_ind / v_air_ms
         + config_.c_par * v_air_ms * v_air_ms * v_air_ms
         + config_.p_avionics_watts;
}

std::expected<Budget, Error> Estimator::update(const Telemetry& telemetry, float dt_sec) noexcept {
    if (!isSane(telemetry) || !std::isfinite(dt_sec) || dt_sec <= 0.0f) {
        // Стан не міняємо: зіпсований кадр — не привід міняти режим польоту.
        return std::unexpected{Error::InvalidTelemetry};
    }

    Budget budget{};

    // 1. Геометрія до точки Home
    const float d_north = telemetry.home.north - telemetry.position.north;
    const float d_east = telemetry.home.east - telemetry.position.east;
    const float distance_m = std::hypot(d_north, d_east);
    budget.distance_to_home_m = distance_m;

    if (distance_m < kHomeRadiusM) {
        // Уже вдома: фільтр скидаємо, щоб наступний виліт починався з чистої оцінки.
        filtered_return_wh_ = 0.0f;
        state_ = State::Ok;
        budget.state = State::Ok;
        budget.e_usable_compensated_wh = telemetry.energy_remaining_wh;
        budget.energy_margin_ratio = 1.0f;
        return budget;
    }

    const Vec2 course{.north = d_north / distance_m, .east = d_east / distance_m};

    // 2. Проєкція вітру на шлях повернення
    const auto wind = projectWind(telemetry.wind, course);

    // 3. Оптимальна повітряна швидкість
    const float v_air = optimalAirspeed(wind.headwind_ms);
    budget.v_air_optimal_ms = v_air;

    // 4. Ліміт бокового зносу: боком нас зносить швидше, ніж ми летимо
    if (wind.crosswind_ms >= v_air) {
        state_ = State::EmergencyLand;
        return std::unexpected{Error::CrosswindLimit};
    }

    // clamp обов'язковий: шум давача швидкості легко робить відношення 1.00004f,
    // і std::asin віддає NaN на весь навігаційний контур.
    const float wca_rad = std::asin(clamp(wind.crosswind_ms / v_air, -1.0f, 1.0f));
    budget.wca_rad = wca_rad;

    const float v_ground = v_air * std::cos(wca_rad) - wind.headwind_ms;
    budget.v_ground_ret_ms = v_ground;

    if (v_ground <= kMinGroundSpeedMs) {
        state_ = State::EmergencyLand;
        return std::unexpected{Error::HeadwindTooHigh};
    }

    const float time_cruise_s = distance_m / v_ground;
    budget.time_to_home_sec = time_cruise_s;

    // 5. Складові енергії
    const float p_cruise = cruisePower(v_air);
    budget.e_cruise_wh = p_cruise * time_cruise_s / 3600.0f;

    const float altitude_agl_m = -telemetry.position.down;
    const float alt_deficit_m = config_.rtl_safe_altitude_m - altitude_agl_m;
    if (alt_deficit_m > 0.0f && config_.v_climb_ms > 0.0f) {
        const float time_climb_s = alt_deficit_m / config_.v_climb_ms;
        budget.e_climb_wh = config_.p_climb_watts * time_climb_s / 3600.0f;
    }

    budget.e_land_wh = config_.p_hover_watts * config_.t_land_maneuver_sec / 3600.0f;

    // Без трубки Піто швидкість оцінює EKF за GNSS і тангажем — похибка більша,
    // тож піднімаємо гарантований запас на 10%.
    const float reserve_ratio =
        telemetry.airspeed_synthetic ? config_.reserve_margin_ratio * 1.10f
                                     : config_.reserve_margin_ratio;

    const float subtotal_wh = budget.e_cruise_wh + budget.e_climb_wh + budget.e_land_wh;
    budget.e_reserve_wh = subtotal_wh * reserve_ratio;
    const float raw_return_wh = subtotal_wh + budget.e_reserve_wh;

    // 6. Фільтр 1-го порядку проти брязкоту тригера на поривах
    if (filtered_return_wh_ <= 0.001f) {
        filtered_return_wh_ = raw_return_wh;
    } else {
        const float alpha = clamp(dt_sec / (config_.filter_time_constant_s + dt_sec), 0.01f, 0.5f);
        filtered_return_wh_ = (1.0f - alpha) * filtered_return_wh_ + alpha * raw_return_wh;
    }
    budget.e_return_total_wh = filtered_return_wh_;

    // 7. Просідання напруги й корисний залишок ємності
    const float voltage_nom_v = telemetry.voltage_v > 0.1f
                                    ? telemetry.voltage_v
                                    : static_cast<float>(config_.cell_count) * 3.7f;
    const float current_a = p_cruise / voltage_nom_v;
    const float projected_v = telemetry.voltage_v - current_a * telemetry.r_internal_ohms;
    budget.projected_sag_voltage_v = projected_v;

    const float cutoff_v = static_cast<float>(config_.cell_count) * config_.cell_v_cutoff;
    float usable_wh = telemetry.energy_remaining_wh;

    // Хвіст ємності під струмом повернення недосяжний: напруга впаде у відсічку
    // раніше, ніж кулонометр дорахує залишок. Відсікаємо його наперед.
    if (projected_v < cutoff_v + 0.6f) {
        const float penalty = clamp((cutoff_v + 0.6f - projected_v) / 1.5f, 0.0f, 0.5f);
        usable_wh *= (1.0f - penalty);
    }
    budget.e_usable_compensated_wh = usable_wh;
    budget.energy_margin_ratio =
        usable_wh > 0.0f ? (usable_wh - budget.e_return_total_wh) / usable_wh : -1.0f;

    // Кінцевий автомат рішень
    if (projected_v <= cutoff_v) {
        state_ = State::EmergencyLand;
        budget.rtl_mandatory = true;
    } else if (usable_wh <= budget.e_return_total_wh) {
        state_ = State::RtlMandatory;
        budget.rtl_mandatory = true;
    } else if (budget.energy_margin_ratio < 0.10f) {
        state_ = State::Caution;
    } else {
        state_ = State::Ok;
    }

    budget.state = state_;
    return budget;
}

} // namespace uav::nav
