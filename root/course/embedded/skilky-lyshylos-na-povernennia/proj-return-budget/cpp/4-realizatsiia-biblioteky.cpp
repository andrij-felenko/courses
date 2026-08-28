#include "ReturnBudget.hpp"
#include <algorithm>
#include <cmath>

namespace uav::nav {

namespace {

constexpr float kPi = 3.14159265358979323846f;

[[nodiscard]] constexpr float clamp(float val, float min_val, float max_val) noexcept {
    return std::max(min_val, std::min(val, max_val));
}

} // namespace

ReturnBudgetEstimator::ReturnBudgetEstimator(const return_config_t& config)
    : config_(config) {}

float ReturnBudgetEstimator::computeOptimalAirspeed(float headwind_component_ms) const noexcept {
    float v_opt = config_.v_best_range_still_ms;

    if (headwind_component_ms > 0.0f) {
        v_opt += 0.40f * headwind_component_ms;
    } else {
        v_opt += 0.25f * headwind_component_ms;
    }

    return clamp(v_opt, config_.v_air_min_ms, config_.v_air_max_ms);
}

float ReturnBudgetEstimator::computeGroundSpeed(
    float airspeed_ms, 
    float wind_speed_ms, 
    float wind_angle_rad
) const noexcept {
    const float crosswind = wind_speed_ms * std::sin(wind_angle_rad);
    if (std::abs(crosswind) >= airspeed_ms) {
        return 0.0f;
    }
    const float sin_wca = crosswind / airspeed_ms;
    const float cos_wca = std::sqrt(1.0f - sin_wca * sin_wca);
    const float headwind = wind_speed_ms * std::cos(wind_angle_rad);
    return (airspeed_ms * cos_wca) - headwind;
}

float ReturnBudgetEstimator::estimateVoltageSag(
    float current_draw_a, 
    float r_internal_ohms
) const noexcept {
    return current_draw_a * r_internal_ohms;
}

void ReturnBudgetEstimator::reset() noexcept {
    filtered_return_energy_wh_ = 0.0f;
    current_state_ = 0;
}

std::optional<return_budget_result_t> ReturnBudgetEstimator::update(
    const return_telemetry_t& telem, 
    float dt_seconds
) {
    if (config_.v_air_min_ms <= 0.0f || config_.v_air_max_ms <= config_.v_air_min_ms) {
        return std::nullopt;
    }

    return_budget_result_t result{};

    // 1. Геометрія до точки Home
    const float d_north = telem.pos_home_ned[0] - telem.pos_current_ned[0];
    const float d_east  = telem.pos_home_ned[1] - telem.pos_current_ned[1];
    const float dist_horizontal_m = std::hypot(d_north, d_east);
    result.distance_to_home_m = dist_horizontal_m;

    if (dist_horizontal_m < 15.0f) {
        result.state = 0; // RETURN_STATE_OK
        result.rtl_mandatory = false;
        return result;
    }

    const float u_north = d_north / dist_horizontal_m;
    const float u_east  = d_east / dist_horizontal_m;

    // 2. Вектор вітру
    const float v_headwind = -(telem.wind_ned[0] * u_north + telem.wind_ned[1] * u_east);
    const float v_crosswind = std::abs(telem.wind_ned[0] * u_east - telem.wind_ned[1] * u_north);

    // 3. Оптимізація повітряної швидкості
    const float v_air_opt = computeOptimalAirspeed(v_headwind);
    result.v_air_optimal_ms = v_air_opt;

    if (v_crosswind >= v_air_opt) {
        result.state = 3; // EMERGENCY_LAND
        result.rtl_mandatory = true;
        return result;
    }

    const float sin_wca = v_crosswind / v_air_opt;
    const float wca_rad = std::asin(clamp(sin_wca, -1.0f, 1.0f));
    result.wca_rad = wca_rad;

    const float v_ground = v_air_opt * std::cos(wca_rad) - v_headwind;
    result.v_ground_ret_ms = v_ground;

    if (v_ground <= 1.0f) {
        result.state = 3; // EMERGENCY_LAND
        result.rtl_mandatory = true;
        return result;
    }

    const float time_cruise_s = dist_horizontal_m / v_ground;
    result.time_to_home_sec = time_cruise_s;

    // 4. Енергетичні розрахунки
    const float p_cruise = (config_.c_ind / v_air_opt) + 
                           (config_.c_par * v_air_opt * v_air_opt * v_air_opt) + 
                           config_.p_avionics_watts;
    const float e_cruise_wh = (p_cruise * time_cruise_s) / 3600.0f;
    result.e_cruise_wh = e_cruise_wh;

    // Набір висоти
    const float current_alt = -telem.pos_current_ned[2];
    const float alt_deficit = config_.rtl_safe_altitude_m - current_alt;
    float e_climb_wh = 0.0f;
    if (alt_deficit > 0.0f && config_.v_climb_ms > 0.0f) {
        const float time_climb_s = alt_deficit / config_.v_climb_ms;
        e_climb_wh = (config_.p_climb_watts * time_climb_s) / 3600.0f;
    }
    result.e_climb_wh = e_climb_wh;

    // Посадковий маневр
    const float e_land_wh = (config_.p_hover_watts * config_.t_land_maneuver_sec) / 3600.0f;
    result.e_land_wh = e_land_wh;

    const float e_subtotal = e_cruise_wh + e_climb_wh + e_land_wh;
    const float e_reserve_wh = e_subtotal * config_.reserve_margin_ratio;
    result.e_reserve_wh = e_reserve_wh;

    const float raw_return_total = e_subtotal + e_reserve_wh;

    // 5. Низькочастотний фільтр
    if (filtered_return_energy_wh_ <= 0.001f) {
        filtered_return_energy_wh_ = raw_return_total;
    } else {
        const float alpha = clamp(dt_seconds / (config_.filter_time_constant_s + dt_seconds), 0.01f, 0.5f);
        filtered_return_energy_wh_ = (1.0f - alpha) * filtered_return_energy_wh_ + alpha * raw_return_total;
    }
    result.e_return_total_wh = filtered_return_energy_wh_;

    // 6. Voltage Sag
    const float voltage_nom = telem.voltage_v > 0.1f ? telem.voltage_v : (config_.cell_count * 3.7f);
    const float i_return_est = p_cruise / voltage_nom;
    const float delta_v_sag = estimateVoltageSag(i_return_est, telem.r_internal_ohms);
    const float projected_v = telem.voltage_v - delta_v_sag;
    result.projected_sag_voltage_v = projected_v;

    const float total_v_cutoff = config_.cell_count * config_.cell_v_cutoff;
    float usable_wh = telem.energy_remaining_wh;

    if (projected_v < total_v_cutoff + 0.6f) {
        const float penalty = clamp((total_v_cutoff + 0.6f - projected_v) / 1.5f, 0.0f, 0.5f);
        usable_wh *= (1.0f - penalty);
    }
    result.e_usable_compensated_wh = usable_wh;

    const float margin_wh = usable_wh - result.e_return_total_wh;
    result.energy_margin_ratio = usable_wh > 0.0f ? (margin_wh / usable_wh) : -1.0f;

    // 7. FSM
    if (projected_v <= total_v_cutoff) {
        current_state_ = 3; // EMERGENCY_LAND
        result.rtl_mandatory = true;
    } else if (usable_wh <= result.e_return_total_wh) {
        current_state_ = 2; // RTL_MANDATORY
        result.rtl_mandatory = true;
    } else if (result.energy_margin_ratio < 0.10f) {
        current_state_ = 1; // CAUTION
        result.rtl_mandatory = false;
    } else {
        current_state_ = 0; // OK
        result.rtl_mandatory = false;
    }

    result.state = current_state_;
    return result;
}

} // namespace uav::nav
