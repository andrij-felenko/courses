#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_RALLY_POINTS 16
#define DEG_TO_RAD (M_PI / 180.0)
#define RAD_TO_DEG (180.0 / M_PI)

typedef struct {
    double lat;              /* Широта (градуси) */
    double lon;              /* Довгота (градуси) */
    float alt_amsl_m;        /* Висота майданчика AMSL (метри) */
    float break_alt_m;       /* Безпечна висота маневру AGL (метри) */
    float landing_hdg_deg;   /* Напрямок заходу на посадку (0..360) */
    float clearance_radius_m;/* Радіус вільної зони (метри) */
    uint8_t priority;        /* Пріоритет (1..10, 10 - найвищий) */
    bool is_active;          /* Доступність майданчика */
} RallyPoint;

typedef struct {
    double lat;
    double lon;
    float alt_amsl_m;
    float airspeed_m_s;      /* Повітряна швидкість літака Va */
    float remaining_energy_wh;/* Залишок енергії в АКБ (Вт·год) */
    float cruise_power_w;    /* Потужність горизонтального польоту (Вт) */
    float climb_power_w;     /* Потужність набору висоти (Вт) */
    float climb_rate_m_s;    /* Швидкість підйому Vz (м/с) */
} VehicleState;

typedef struct {
    float speed_m_s;         /* Швидкість вітру Vw (м/с) */
    float dir_from_deg;      /* Звідки дме вітер (градуси) */
} WindEstimate;

typedef struct {
    int index;               /* Індекс майданчика в реєстрі */
    float ground_speed_m_s;  /* Отримана шляхова швидкість Vg */
    float flight_time_s;     /* Розрахунковий час підльоту */
    float energy_required_wh;/* Необхідна енергія */
    float score;             /* Фінальний штрафний бал (менше = краще) */
    bool is_reachable;       /* Чи вистачає енергії */
} EvaluatedRally;

/* Обчислення пласкої відстані та азимуту (еквідистантна проекція для малих відстаней) */
static void flat_distance_bearing(double lat1, double lon1, double lat2, double lon2,
                                  float *distance_m, float *bearing_deg) {
    double dlat = (lat2 - lat1) * DEG_TO_RAD;
    double dlon = (lon2 - lon1) * DEG_TO_RAD;
    double mean_lat = (lat1 + lat2) * 0.5 * DEG_TO_RAD;
    
    double x = dlon * cos(mean_lat) * 6371000.0;
    double y = dlat * 6371000.0;
    
    *distance_m = (float)sqrt(x * x + y * y);
    double brg = atan2(x, y) * RAD_TO_DEG;
    if (brg < 0.0) brg += 360.0;
    *bearing_deg = (float)brg;
}

/* Оцінка одного майданчика за вітровим трикутником та енергією */
bool evaluate_rally_point(const RallyPoint *rp, int idx,
                          const VehicleState *vs,
                          const WindEstimate *wind,
                          EvaluatedRally *result) {
    if (!rp->is_active) return false;

    float dist_m = 0.0f, track_deg = 0.0f;
    flat_distance_bearing(vs->lat, vs->lon, rp->lat, rp->lon, &dist_m, &track_deg);

    /* Кут між лінією шляху та вектором звідки дме вітер */
    float theta_rad = (track_deg - wind->dir_from_deg - 180.0f) * (float)DEG_TO_RAD;
    
    /* Розрахунок кута випередження за теоремою синусів */
    float sin_crab = (wind->speed_m_s / vs->airspeed_m_s) * sinf(theta_rad);
    if (fabsf(sin_crab) >= 1.0f) {
        return false; /* Боковий вітер перевищує повітряну швидкість */
    }
    
    float crab_rad = asinf(sin_crab);
    float vg = vs->airspeed_m_s * cosf(crab_rad) + wind->speed_m_s * cosf(theta_rad);
    if (vg < 2.0f) {
        return false; /* Немає просування вперед або знесення назад */
    }

    /* Розрахунок набору висоти до break_alt */
    float target_alt = rp->alt_amsl_m + rp->break_alt_m;
    float delta_h = target_alt - vs->alt_amsl_m;
    float t_climb = (delta_h > 0.0f) ? (delta_h / vs->climb_rate_m_s) : 0.0f;
    float dist_climb = t_climb * vg;
    float dist_cruise = (dist_m > dist_climb) ? (dist_m - dist_climb) : 0.0f;
    float t_cruise = dist_cruise / vg;
    float t_total = t_climb + t_cruise;

    /* Витрата енергії у Вт·год (P * t / 3600) + 15% на посадку */
    float e_climb = (vs->climb_power_w * t_climb) / 3600.0f;
    float e_cruise = (vs->cruise_power_w * t_cruise) / 3600.0f;
    float e_approach = (vs->cruise_power_w * 90.0f) / 3600.0f;
    float e_total = e_climb + e_cruise + e_approach;

    /* Перевірка енергетичного порогу з буфером 20% */
    bool reachable = (e_total * 1.20f) <= vs->remaining_energy_wh;

    /* Оцінка посадкового курсу проти вітру */
    float wind_land_diff = (wind->dir_from_deg - rp->landing_hdg_deg) * (float)DEG_TO_RAD;
    float wind_align_cost = 0.5f * (1.0f - cosf(wind_land_diff));

    /* Багатокритеріальний розрахунок вартості J */
    float energy_norm = e_total / vs->remaining_energy_wh;
    float time_norm = t_total / 1800.0f; /* Нормування до 30 хв */
    float priority_norm = (float)rp->priority / 10.0f;

    float score = 0.45f * energy_norm +
                  0.25f * wind_align_cost +
                  0.20f * time_norm -
                  0.10f * priority_norm;

    result->index = idx;
    result->ground_speed_m_s = vg;
    result->flight_time_s = t_total;
    result->energy_required_wh = e_total;
    result->score = score;
    result->is_reachable = reachable;

    return true;
}

/* Ранжування майданчиків за зростанням вартості */
int rank_rally_points(const RallyPoint *points, int count,
                      const VehicleState *vs,
                      const WindEstimate *wind,
                      EvaluatedRally *out_ranked) {
    int valid_count = 0;
    for (int i = 0; i < count && i < MAX_RALLY_POINTS; ++i) {
        EvaluatedRally eval;
        if (evaluate_rally_point(&points[i], i, vs, wind, &eval)) {
            if (eval.is_reachable) {
                out_ranked[valid_count++] = eval;
            }
        }
    }

    /* Сортування вставками */
    for (int i = 1; i < valid_count; ++i) {
        EvaluatedRally key = out_ranked[i];
        int j = i - 1;
        while (j >= 0 && out_ranked[j].score > key.score) {
            out_ranked[j + 1] = out_ranked[j];
            j = j - 1;
        }
        out_ranked[j + 1] = key;
    }

    return valid_count;
}
