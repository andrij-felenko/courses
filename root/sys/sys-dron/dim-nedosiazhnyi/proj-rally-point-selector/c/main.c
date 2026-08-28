#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define RALLY_MAX_POINTS 16
#define DEG_TO_RAD (M_PI / 180.0)
#define RAD_TO_DEG (180.0 / M_PI)

/* Опис характеристик окремого запасного майданчика */
typedef struct {
    double latitude_deg;         /* Географічна широта WGS-84 */
    double longitude_deg;        /* Географічна довгота WGS-84 */
    float altitude_amsl_m;       /* Абсолютна висота поверхні майданчика (м) */
    float break_alt_agl_m;       /* Висота безпечного розвороту над точкою (м) */
    float landing_heading_deg;   /* Рекомендований курс посадки (0..360) */
    float clearance_radius_m;    /* Радіус вільної від перешкод зони (м) */
    uint8_t priority;            /* Пріоритет (1..10, 10 - найвищий) */
    bool is_active;              /* Прапорець доступності майданчика */
} RallyPointDefinition;

/* Поточний навігаційний та енергетичний стан БПЛА */
typedef struct {
    double current_lat;
    double current_lon;
    float current_alt_amsl_m;
    float cruise_airspeed_m_s;   /* Задана повітряна швидкість Va */
    float climb_rate_m_s;        /* Вертикальна швидкість підйому Vz */
    float cruise_power_w;        /* Електрична потужність горизонту (Вт) */
    float climb_power_w;         /* Електрична потужність підйому (Вт) */
    float remaining_energy_wh;   /* Доступний залишок енергії в АКБ (Вт·год) */
    float battery_voltage_v;     /* Поточна напруга під навантаженням (В) */
    float battery_internal_res_ohm; /* Внутрішній опір батареї Ri (Ом) */
} VehicleFlightStatus;

/* Оцінка вітрового вектора з фільтра EKF */
typedef struct {
    float wind_speed_m_s;        /* Модуль швидкості вітру Vw (м/с) */
    float wind_from_direction_deg;/* Метеорологічний напрямок звідки дме */
} WindConditions;

/* Результат розрахунку параметрів для конкретного майданчика */
typedef struct {
    int point_index;
    float distance_to_point_m;
    float ground_speed_m_s;
    float flight_time_s;
    float total_energy_wh;
    float final_score;
    bool is_feasible;
} RallyCandidateEvaluation;

/* Внутрішній стан модуля вибору з підтримкою гістерезису */
typedef struct {
    RallyPointDefinition registry[RALLY_MAX_POINTS];
    uint8_t total_points;
    int active_selected_index;
    int pending_candidate_index;
    float pending_candidate_duration_s;
    float hysteresis_delta_j;
    float hold_time_threshold_s;
} RallySelectorModule;

/* Ініціалізація модуля */
void rally_selector_init(RallySelectorModule *module) {
    memset(module, 0, sizeof(RallySelectorModule));
    module->active_selected_index = -1;
    module->pending_candidate_index = -1;
    module->pending_candidate_duration_s = 0.0f;
    module->hysteresis_delta_j = 0.08f;
    module->hold_time_threshold_s = 3.0f;
}

/* Додавання або оновлення майданчика у внутрішньому реєстрі */
bool rally_selector_set_point(RallySelectorModule *module, uint8_t idx,
                              const RallyPointDefinition *point) {
    if (idx >= RALLY_MAX_POINTS || point == NULL) {
        return false;
    }
    module->registry[idx] = *point;
    if (idx >= module->total_points) {
        module->total_points = idx + 1;
    }
    return true;
}

/* Обчислення пласкої відстані та азимуту */
static void compute_distance_azimuth(double lat1, double lon1,
                                     double lat2, double lon2,
                                     float *out_dist_m, float *out_azimuth_deg) {
    double dlat = (lat2 - lat1) * DEG_TO_RAD;
    double dlon = (lon2 - lon1) * DEG_TO_RAD;
    double mean_lat = (lat1 + lat2) * 0.5 * DEG_TO_RAD;

    double x = dlon * cos(mean_lat) * 6371000.0;
    double y = dlat * 6371000.0;

    *out_dist_m = (float)sqrt(x * x + y * y);
    double brg = atan2(x, y) * RAD_TO_DEG;
    if (brg < 0.0) {
        brg += 360.0;
    }
    *out_azimuth_deg = (float)brg;
}

/* Повна перевірка досяжності та розрахунок вартості кандидата */
static bool evaluate_candidate(const RallyPointDefinition *rp, int idx,
                               const VehicleFlightStatus *vs,
                               const WindConditions *wind,
                               RallyCandidateEvaluation *eval) {
    if (!rp->is_active) {
        return false;
    }

    float dist_m = 0.0f, track_deg = 0.0f;
    compute_distance_azimuth(vs->current_lat, vs->current_lon,
                             rp->latitude_deg, rp->longitude_deg,
                             &dist_m, &track_deg);

    /* Аеродинамічний вітровий трикутник */
    float theta_rad = (track_deg - wind->wind_from_direction_deg - 180.0f) * (float)DEG_TO_RAD;
    float sin_crab = (wind->wind_speed_m_s / vs->cruise_airspeed_m_s) * sinf(theta_rad);

    if (fabsf(sin_crab) >= 1.0f) {
        return false; /* Неможливо скомпенсувати боковий вітер */
    }

    float crab_angle_rad = asinf(sin_crab);
    float vg = vs->cruise_airspeed_m_s * cosf(crab_angle_rad) +
               wind->wind_speed_m_s * cosf(theta_rad);

    if (vg < 2.0f) {
        return false; /* Недостатнє поступальне просування */
    }

    /* Висотний профіль */
    float target_alt = rp->altitude_amsl_m + rp->break_alt_agl_m;
    float delta_h = target_alt - vs->current_alt_amsl_m;
    float t_climb = (delta_h > 0.0f && vs->climb_rate_m_s > 0.1f)
                    ? (delta_h / vs->climb_rate_m_s) : 0.0f;

    float dist_during_climb = t_climb * vg;
    float dist_cruise = (dist_m > dist_during_climb) ? (dist_m - dist_during_climb) : 0.0f;
    float t_cruise = dist_cruise / vg;
    float t_total = t_climb + t_cruise;

    /* Енергетичні витрати (Вт·год) */
    float e_climb = (vs->climb_power_w * t_climb) / 3600.0f;
    float e_cruise = (vs->cruise_power_w * t_cruise) / 3600.0f;
    float e_land_reserve = (vs->cruise_power_w * 90.0f) / 3600.0f;
    float e_total = e_climb + e_cruise + e_land_reserve;

    /* Перевірка енергетичного порогу з 20% коефіцієнтом безпеки */
    if ((e_total * 1.20f) > vs->remaining_energy_wh) {
        return false;
    }

    /* Оцінка якості заходу на посадку проти вітру */
    float wind_heading_diff = (wind->wind_from_direction_deg - rp->landing_heading_deg) * (float)DEG_TO_RAD;
    float wind_align_cost = 0.5f * (1.0f - cosf(wind_heading_diff));

    /* Багатокритеріальний розрахунок вартості J */
    float energy_ratio = e_total / vs->remaining_energy_wh;
    float time_ratio = t_total / 1800.0f;
    float priority_ratio = (float)rp->priority / 10.0f;

    float score = (0.45f * energy_ratio) +
                  (0.25f * wind_align_cost) +
                  (0.20f * time_ratio) -
                  (0.10f * priority_ratio);

    eval->point_index = idx;
    eval->distance_to_point_m = dist_m;
    eval->ground_speed_m_s = vg;
    eval->flight_time_s = t_total;
    eval->total_energy_wh = e_total;
    eval->final_score = score;
    eval->is_feasible = true;

    return true;
}

/* Періодичний крок виконання селектора (викликається з dt) */
int rally_selector_update(RallySelectorModule *module,
                          const VehicleFlightStatus *status,
                          const WindConditions *wind,
                          float dt_s) {
    if (module->total_points == 0) {
        return -1;
    }

    RallyCandidateEvaluation best_eval;
    bool found_any = false;
    best_eval.final_score = 1e6f;

    /* Пошук найкращого доступного кандидата у поточному циклі */
    for (uint8_t i = 0; i < module->total_points; ++i) {
        RallyCandidateEvaluation eval;
        if (evaluate_candidate(&module->registry[i], i, status, wind, &eval)) {
            if (eval.final_score < best_eval.final_score) {
                best_eval = eval;
                found_any = true;
            }
        }
    }

    if (!found_any) {
        /* Жоден майданчик недосяжний */
        return -1;
    }

    /* Якщо активної цілі ще немає — обираємо першого лідера негайно */
    if (module->active_selected_index < 0) {
        module->active_selected_index = best_eval.point_index;
        module->pending_candidate_index = -1;
        module->pending_candidate_duration_s = 0.0f;
        return module->active_selected_index;
    }

    /* Перевірка стану поточної активної цілі */
    RallyCandidateEvaluation current_eval;
    bool current_is_valid = evaluate_candidate(
        &module->registry[module->active_selected_index],
        module->active_selected_index, status, wind, &current_eval);

    /* Якщо поточна ціль втратила валідність (вичерпано енергію) — негайно перемикаємо */
    if (!current_is_valid) {
        module->active_selected_index = best_eval.point_index;
        module->pending_candidate_index = -1;
        module->pending_candidate_duration_s = 0.0f;
        return module->active_selected_index;
    }

    /* Якщо найкращий кандидат — це поточна ціль, скидаємо таймер претендента */
    if (best_eval.point_index == module->active_selected_index) {
        module->pending_candidate_index = -1;
        module->pending_candidate_duration_s = 0.0f;
        return module->active_selected_index;
    }

    /* Перевірка порогу гістерезису */
    if (best_eval.final_score < (current_eval.final_score - module->hysteresis_delta_j)) {
        if (best_eval.point_index == module->pending_candidate_index) {
            module->pending_candidate_duration_s += dt_s;
            if (module->pending_candidate_duration_s >= module->hold_time_threshold_s) {
                /* Перемикання на нову ціль після успішного утримання */
                module->active_selected_index = best_eval.point_index;
                module->pending_candidate_index = -1;
                module->pending_candidate_duration_s = 0.0f;
            }
        } else {
            module->pending_candidate_index = best_eval.point_index;
            module->pending_candidate_duration_s = 0.0f;
        }
    } else {
        module->pending_candidate_index = -1;
        module->pending_candidate_duration_s = 0.0f;
    }

    return module->active_selected_index;
}
