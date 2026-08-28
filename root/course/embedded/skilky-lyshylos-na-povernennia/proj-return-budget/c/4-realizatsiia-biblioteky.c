#include "return_budget.h"
#include <math.h>
#include <string.h>

#ifndef M_PI_F
#define M_PI_F 3.14159265358979323846f
#endif

/* Обмеження значення у діапазон */
static inline float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

/* Ініціалізація модуля */
int32_t return_budget_init(return_budget_handle_t* handle, const return_config_t* config) {
    if (!handle || !config) {
        return RETURN_ERR_INVALID_CONFIG;
    }
    if (config->v_air_min_ms <= 0.0f || config->v_air_max_ms <= config->v_air_min_ms ||
        config->nominal_energy_wh <= 0.0f || config->cell_count == 0) {
        return RETURN_ERR_INVALID_CONFIG;
    }

    memset(handle, 0, sizeof(return_budget_handle_t));
    handle->config = *config;
    handle->initialized = true;
    handle->filtered_e_return_wh = 0.0f;
    handle->current_state = RETURN_STATE_OK;
    return RETURN_OK;
}

/* Оптимізація швидкості проти вітру за лінеаризованою полярою Маккреді */
static float compute_optimal_airspeed(const return_config_t* cfg, float headwind_ms) {
    /* Базова швидкість найкращої дальності у штиль */
    float v_opt = cfg->v_best_range_still_ms;

    if (headwind_ms > 0.0f) {
        /* Проти зустрічного вітру швидкість збільшується (k ≈ 0.4) */
        v_opt += 0.40f * headwind_ms;
    } else {
        /* При попутному вітрі швидкість зменшується для економії, але не нижче мінімуму */
        v_opt += 0.25f * headwind_ms;
    }

    return clampf(v_opt, cfg->v_air_min_ms, cfg->v_air_max_ms);
}

/* Оцінка електричної потужності горизонтального крейсерського польоту */
static float compute_cruise_power(const return_config_t* cfg, float v_air_ms) {
    /* P(V) = c_ind / V + c_par * V³ + P_avionics */
    float p_ind = cfg->c_ind / v_air_ms;
    float p_par = cfg->c_par * v_air_ms * v_air_ms * v_air_ms;
    return p_ind + p_par + cfg->p_avionics_watts;
}

/* Головний цикл розрахунку бюджету повернення */
int32_t return_budget_update(
    return_budget_handle_t* handle,
    const return_telemetry_t* telem,
    return_budget_result_t* out_result
) {
    if (!handle || !handle->initialized || !telem || !out_result) {
        return RETURN_ERR_INVALID_CONFIG;
    }

    const return_config_t* cfg = &handle->config;
    memset(out_result, 0, sizeof(return_budget_result_t));

    /* 1. Геометрія: вектор від поточної позиції до точки Home */
    float d_north = telem->pos_home_ned[0] - telem->pos_current_ned[0];
    float d_east  = telem->pos_home_ned[1] - telem->pos_current_ned[1];
    float d_down  = telem->pos_home_ned[2] - telem->pos_current_ned[2];
    
    float dist_horizontal_m = sqrtf(d_north * d_north + d_east * d_east);
    out_result->distance_to_home_m = dist_horizontal_m;

    /* Якщо вже в точці старту (< 15 метрів) */
    if (dist_horizontal_m < 15.0f) {
        out_result->state = RETURN_STATE_OK;
        out_result->rtl_mandatory = false;
        return RETURN_OK;
    }

    /* Одиничний вектор бажаного шляху додому */
    float u_north = d_north / dist_horizontal_m;
    float u_east  = d_east / dist_horizontal_m;

    /* 2. Проєкція вітрового вектора на шлях повернення */
    /* Скалярний добуток: вітер, направлений назустріч курсу повернення */
    float v_headwind = -(telem->wind_ned[0] * u_north + telem->wind_ned[1] * u_east);
    /* Векторний добуток (бокова складова зносу) */
    float v_crosswind = fabsf(telem->wind_ned[0] * u_east - telem->wind_ned[1] * u_north);

    /* 3. Вибір оптимальної повітряної швидкості */
    float v_air_opt = compute_optimal_airspeed(cfg, v_headwind);
    out_result->v_air_optimal_ms = v_air_opt;

    /* Перевірка ліміту бокового зносу */
    if (v_crosswind >= v_air_opt) {
        out_result->state = RETURN_STATE_EMERGENCY_LAND;
        out_result->rtl_mandatory = true;
        return RETURN_ERR_CROSSWIND_LIMIT;
    }

    /* Кут випередження вітру (WCA) */
    float sin_wca = v_crosswind / v_air_opt;
    float wca_rad = asinf(clampf(sin_wca, -1.0f, 1.0f));
    out_result->wca_rad = wca_rad;

    /* Шляхова швидкість зближення з базою */
    float v_ground = v_air_opt * cosf(wca_rad) - v_headwind;
    out_result->v_ground_ret_ms = v_ground;

    /* Якщо зустрічний вітер зупиняє або здуває борт */
    if (v_ground <= 1.0f) {
        out_result->state = RETURN_STATE_EMERGENCY_LAND;
        out_result->rtl_mandatory = true;
        return RETURN_ERR_HEADWIND_TOO_HIGH;
    }

    /* Час польоту до бази */
    float time_cruise_s = dist_horizontal_m / v_ground;
    out_result->time_to_home_sec = time_cruise_s;

    /* 4. Енергетичні складові польоту */
    float p_cruise = compute_cruise_power(cfg, v_air_opt);
    float e_cruise_wh = (p_cruise * time_cruise_s) / 3600.0f;
    out_result->e_cruise_wh = e_cruise_wh;

    /* Набір безпечної висоти (якщо поточна висота нижча за безпечну) */
    float current_alt_agl = -telem->pos_current_ned[2];
    float alt_deficit = cfg->rtl_safe_altitude_m - current_alt_agl;
    float e_climb_wh = 0.0f;
    if (alt_deficit > 0.0f && cfg->v_climb_ms > 0.0f) {
        float time_climb_s = alt_deficit / cfg->v_climb_ms;
        e_climb_wh = (cfg->p_climb_watts * time_climb_s) / 3600.0f;
    }
    out_result->e_climb_wh = e_climb_wh;

    /* Енергія на маневр посадки (зависання / глісада) */
    float e_land_wh = (cfg->p_hover_watts * cfg->t_land_maneuver_sec) / 3600.0f;
    out_result->e_land_wh = e_land_wh;

    /* Гарантований незнижуваний резерв */
    float e_subtotal = e_cruise_wh + e_climb_wh + e_land_wh;
    float e_reserve_wh = e_subtotal * cfg->reserve_margin_ratio;
    out_result->e_reserve_wh = e_reserve_wh;

    float raw_e_return_total = e_subtotal + e_reserve_wh;

    /* 5. Низькочастотна фільтрація розрахунку для уникнення брязкоту */
    if (handle->filtered_e_return_wh <= 0.001f) {
        handle->filtered_e_return_wh = raw_e_return_total;
    } else {
        float alpha = 0.15f; /* Коефіцієнт згладжування при частоті оновлення 2-5 Гц */
        handle->filtered_e_return_wh = (1.0f - alpha) * handle->filtered_e_return_wh + alpha * raw_e_return_total;
    }
    out_result->e_return_total_wh = handle->filtered_e_return_wh;

    /* 6. Розрахунок просідання напруги та корисної ємності батареї */
    float voltage_nom = telem->voltage_v > 0.1f ? telem->voltage_v : (cfg->cell_count * 3.7f);
    float i_return_est = p_cruise / voltage_nom;
    float delta_v_sag = i_return_est * telem->r_internal_ohms;
    float projected_terminal_v = telem->voltage_v - delta_v_sag;
    out_result->projected_sag_voltage_v = projected_terminal_v;

    /* Якщо напруга під навантаженням опускається нижче V_cutoff */
    float total_v_cutoff = cfg->cell_count * cfg->cell_v_cutoff;
    float usable_energy_wh = telem->energy_remaining_wh;

    /* Зменшення ефективної ємності через просідання */
    if (projected_terminal_v < total_v_cutoff + 0.6f) {
        float penalty_ratio = clampf((total_v_cutoff + 0.6f - projected_terminal_v) / 1.5f, 0.0f, 0.5f);
        usable_energy_wh *= (1.0f - penalty_ratio);
    }
    out_result->e_usable_compensated_wh = usable_energy_wh;

    /* Розрахунок маржі запасу */
    float margin_wh = usable_energy_wh - out_result->e_return_total_wh;
    out_result->energy_margin_ratio = usable_energy_wh > 0.0f ? (margin_wh / usable_energy_wh) : -1.0f;

    /* 7. Кінцевий автомат (FSM) прийняття рішень */
    if (projected_terminal_v <= total_v_cutoff) {
        handle->current_state = RETURN_STATE_EMERGENCY_LAND;
        out_result->rtl_mandatory = true;
    } else if (usable_energy_wh <= out_result->e_return_total_wh) {
        handle->current_state = RETURN_STATE_RTL_MANDATORY;
        out_result->rtl_mandatory = true;
    } else if (out_result->energy_margin_ratio < 0.10f) {
        handle->current_state = RETURN_STATE_CAUTION;
        out_result->rtl_mandatory = false;
    } else {
        handle->current_state = RETURN_STATE_OK;
        out_result->rtl_mandatory = false;
    }

    out_result->state = handle->current_state;
    return RETURN_OK;
}
