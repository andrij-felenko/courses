#include "return_budget.h"

#include <math.h>
#include <string.h>

/* Радіус домашньої зони: ближче рахувати повернення немає сенсу */
#define HOME_RADIUS_M 15.0f

/* Мінімальна шляхова швидкість, нижче якої час польоту прямує в нескінченність */
#define V_GROUND_MIN_MS 1.0f

/* Обмеження значення у діапазон */
static inline float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

static bool config_is_valid(const return_config_t* cfg) {
    if (cfg->v_air_min_ms <= 0.0f || cfg->v_air_max_ms < cfg->v_air_min_ms) return false;
    if (cfg->v_best_range_still_ms <= 0.0f) return false;
    if (cfg->c_ind <= 0.0f || cfg->c_par <= 0.0f) return false;
    if (cfg->nominal_energy_wh <= 0.0f || cfg->cell_count == 0) return false;
    if (cfg->cell_v_cutoff <= 0.0f) return false;
    if (cfg->reserve_margin_ratio < 0.0f) return false;
    if (cfg->filter_time_constant_s <= 0.0f) return false;
    if (cfg->t_land_maneuver_sec < 0.0f || cfg->p_hover_watts < 0.0f) return false;
    return true;
}

/* Телеметрія з давачів — джерело NaN: EKF, що розійшовся, дає inf, і далі
   ним отруюється весь розрахунок. Тому пускаємо всередину лише скінченні числа. */
static bool telemetry_is_sane(const return_telemetry_t* t) {
    for (int i = 0; i < 3; ++i) {
        if (!isfinite(t->pos_current_ned[i]) || !isfinite(t->pos_home_ned[i])) return false;
    }
    if (!isfinite(t->wind_ned[0]) || !isfinite(t->wind_ned[1])) return false;
    if (!isfinite(t->voltage_v) || !isfinite(t->r_internal_ohms)) return false;
    if (!isfinite(t->energy_remaining_wh)) return false;
    if (t->voltage_v < 0.0f || t->r_internal_ohms < 0.0f || t->energy_remaining_wh < 0.0f) return false;
    return true;
}

/* Оптимізація швидкості за лінеаризованою полярою Маккреді */
static float compute_optimal_airspeed(const return_config_t* cfg, float headwind_ms) {
    float v_opt = cfg->v_best_range_still_ms;

    if (headwind_ms > 0.0f) {
        /* Проти зустрічного вітру швидкість збільшуємо: коротший час у повітрі
           окупає більшу паразитну потужність (k ≈ 0.4 для типової поляри). */
        v_opt += 0.40f * headwind_ms;
    } else {
        /* При попутному вітрі — навпаки, сповільнюємось до економічного режиму. */
        v_opt += 0.25f * headwind_ms;
    }

    return clampf(v_opt, cfg->v_air_min_ms, cfg->v_air_max_ms);
}

/* Електрична потужність горизонтального крейсерського польоту */
static float compute_cruise_power(const return_config_t* cfg, float v_air_ms) {
    /* P(V) = c_ind / V + c_par * V³ + P_avionics */
    const float p_ind = cfg->c_ind / v_air_ms;
    const float p_par = cfg->c_par * v_air_ms * v_air_ms * v_air_ms;
    return p_ind + p_par + cfg->p_avionics_watts;
}

int32_t return_budget_init(return_budget_handle_t* handle, const return_config_t* config) {
    if (!handle || !config) {
        return RETURN_ERR_INVALID_CONFIG;
    }
    if (!config_is_valid(config)) {
        return RETURN_ERR_INVALID_CONFIG;
    }

    memset(handle, 0, sizeof(*handle));
    handle->config = *config;
    handle->filtered_e_return_wh = 0.0f;
    handle->current_state = RETURN_STATE_OK;
    handle->initialized = true;
    return RETURN_OK;
}

void return_budget_reset(return_budget_handle_t* handle) {
    if (!handle) return;
    handle->filtered_e_return_wh = 0.0f;
    handle->current_state = RETURN_STATE_OK;
}

const char* return_budget_state_name(return_state_t state) {
    switch (state) {
        case RETURN_STATE_OK:             return "OK";
        case RETURN_STATE_CAUTION:        return "CAUTION";
        case RETURN_STATE_RTL_MANDATORY:  return "RTL_MANDATORY";
        case RETURN_STATE_EMERGENCY_LAND: return "EMERGENCY_LAND";
        default:                          return "UNKNOWN";
    }
}

int32_t return_budget_update(return_budget_handle_t* handle,
                             const return_telemetry_t* telem,
                             float dt_sec,
                             return_budget_result_t* out_result) {
    if (!handle || !handle->initialized || !telem || !out_result) {
        return RETURN_ERR_INVALID_CONFIG;
    }

    memset(out_result, 0, sizeof(*out_result));
    out_result->state = handle->current_state;

    if (!telemetry_is_sane(telem) || !isfinite(dt_sec) || dt_sec <= 0.0f) {
        /* Стан не міняємо: зіпсований кадр телеметрії не привід міняти режим польоту,
           рішення про це ухвалює навігаційна задача за кількістю поспіль зіпсованих кадрів. */
        return RETURN_ERR_INVALID_TELEMETRY;
    }

    const return_config_t* cfg = &handle->config;

    /* 1. Геометрія: вектор від поточної позиції до точки Home */
    const float d_north = telem->pos_home_ned[0] - telem->pos_current_ned[0];
    const float d_east  = telem->pos_home_ned[1] - telem->pos_current_ned[1];

    const float dist_horizontal_m = sqrtf(d_north * d_north + d_east * d_east);
    out_result->distance_to_home_m = dist_horizontal_m;

    if (dist_horizontal_m < HOME_RADIUS_M) {
        /* Уже вдома: бюджет повернення нульовий, фільтр скидаємо, щоб наступний
           виліт починався з чистої оцінки, а не з хвоста попереднього. */
        handle->filtered_e_return_wh = 0.0f;
        handle->current_state = RETURN_STATE_OK;
        out_result->state = RETURN_STATE_OK;
        out_result->rtl_mandatory = false;
        out_result->e_usable_compensated_wh = telem->energy_remaining_wh;
        out_result->energy_margin_ratio = 1.0f;
        return RETURN_OK;
    }

    /* Одиничний вектор бажаного шляху додому */
    const float u_north = d_north / dist_horizontal_m;
    const float u_east  = d_east / dist_horizontal_m;

    /* 2. Проєкція вітру на шлях повернення.
       Скалярний добуток дає зустрічну складову (зі знаком «мінус», бо wind_ned —
       це куди дме повітря), псевдоскалярний — бокову. */
    const float v_headwind  = -(telem->wind_ned[0] * u_north + telem->wind_ned[1] * u_east);
    const float v_crosswind = fabsf(telem->wind_ned[0] * u_east - telem->wind_ned[1] * u_north);

    /* 3. Оптимальна повітряна швидкість */
    const float v_air_opt = compute_optimal_airspeed(cfg, v_headwind);
    out_result->v_air_optimal_ms = v_air_opt;

    /* 4. Ліміт бокового зносу: боком нас зносить швидше, ніж ми летимо */
    if (v_crosswind >= v_air_opt) {
        handle->current_state = RETURN_STATE_EMERGENCY_LAND;
        out_result->state = RETURN_STATE_EMERGENCY_LAND;
        out_result->rtl_mandatory = true;
        return RETURN_ERR_CROSSWIND_LIMIT;
    }

    /* Кут випередження вітру. clampf обов'язковий: шум давача швидкості легко
       робить відношення 1.00004f, і asinf() віддає NaN на весь навігаційний контур. */
    const float sin_wca = clampf(v_crosswind / v_air_opt, -1.0f, 1.0f);
    const float wca_rad = asinf(sin_wca);
    out_result->wca_rad = wca_rad;

    /* Шляхова швидкість зближення з базою */
    const float v_ground = v_air_opt * cosf(wca_rad) - v_headwind;
    out_result->v_ground_ret_ms = v_ground;

    if (v_ground <= V_GROUND_MIN_MS) {
        /* Зустрічний вітер зупинив або здуває борт: D / v_ground → ∞ */
        handle->current_state = RETURN_STATE_EMERGENCY_LAND;
        out_result->state = RETURN_STATE_EMERGENCY_LAND;
        out_result->rtl_mandatory = true;
        return RETURN_ERR_HEADWIND_TOO_HIGH;
    }

    const float time_cruise_s = dist_horizontal_m / v_ground;
    out_result->time_to_home_sec = time_cruise_s;

    /* 5. Складові енергії */
    const float p_cruise = compute_cruise_power(cfg, v_air_opt);
    const float e_cruise_wh = (p_cruise * time_cruise_s) / 3600.0f;
    out_result->e_cruise_wh = e_cruise_wh;

    /* Набір безпечного ешелону — лише якщо летимо нижче за нього */
    const float current_alt_agl = -telem->pos_current_ned[2];
    const float alt_deficit = cfg->rtl_safe_altitude_m - current_alt_agl;
    float e_climb_wh = 0.0f;
    if (alt_deficit > 0.0f && cfg->v_climb_ms > 0.0f) {
        const float time_climb_s = alt_deficit / cfg->v_climb_ms;
        e_climb_wh = (cfg->p_climb_watts * time_climb_s) / 3600.0f;
    }
    out_result->e_climb_wh = e_climb_wh;

    /* Посадковий маневр: зависання й глісада */
    const float e_land_wh = (cfg->p_hover_watts * cfg->t_land_maneuver_sec) / 3600.0f;
    out_result->e_land_wh = e_land_wh;

    /* Гарантований резерв. Без трубки Піто швидкість оцінює EKF за GNSS і тангажем —
       похибка більша, тож піднімаємо запас на 10%. */
    float reserve_ratio = cfg->reserve_margin_ratio;
    if (telem->airspeed_synthetic) {
        reserve_ratio *= 1.10f;
    }

    const float e_subtotal = e_cruise_wh + e_climb_wh + e_land_wh;
    const float e_reserve_wh = e_subtotal * reserve_ratio;
    out_result->e_reserve_wh = e_reserve_wh;

    const float raw_e_return_total = e_subtotal + e_reserve_wh;

    /* 6. Фільтр 1-го порядку проти брязкоту тригера на поривах.
       alpha рахуємо від dt, щоб плавання періоду виклику не міняло смугу фільтра. */
    if (handle->filtered_e_return_wh <= 0.001f) {
        handle->filtered_e_return_wh = raw_e_return_total;
    } else {
        const float alpha = clampf(dt_sec / (cfg->filter_time_constant_s + dt_sec), 0.01f, 0.5f);
        handle->filtered_e_return_wh =
            (1.0f - alpha) * handle->filtered_e_return_wh + alpha * raw_e_return_total;
    }
    out_result->e_return_total_wh = handle->filtered_e_return_wh;

    /* 7. Просідання напруги й корисний залишок ємності */
    const float voltage_nom = (telem->voltage_v > 0.1f) ? telem->voltage_v
                                                        : (cfg->cell_count * 3.7f);
    const float i_return_est = p_cruise / voltage_nom;
    const float delta_v_sag = i_return_est * telem->r_internal_ohms;
    const float projected_terminal_v = telem->voltage_v - delta_v_sag;
    out_result->projected_sag_voltage_v = projected_terminal_v;

    const float total_v_cutoff = cfg->cell_count * cfg->cell_v_cutoff;
    float usable_energy_wh = telem->energy_remaining_wh;

    /* Хвіст ємності під струмом повернення недосяжний: напруга впаде в відсічку
       раніше, ніж кулонометр дорахує залишок. Відсікаємо його наперед. */
    if (projected_terminal_v < total_v_cutoff + 0.6f) {
        const float penalty_ratio =
            clampf((total_v_cutoff + 0.6f - projected_terminal_v) / 1.5f, 0.0f, 0.5f);
        usable_energy_wh *= (1.0f - penalty_ratio);
    }
    out_result->e_usable_compensated_wh = usable_energy_wh;

    const float margin_wh = usable_energy_wh - out_result->e_return_total_wh;
    out_result->energy_margin_ratio =
        (usable_energy_wh > 0.0f) ? (margin_wh / usable_energy_wh) : -1.0f;

    /* Кінцевий автомат рішень */
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
