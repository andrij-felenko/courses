#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define MAX_RALLY_POINTS 16
#define EARTH_RADIUS_M 6371000.0
#define DEG_TO_RAD (3.14159265358979323846 / 180.0)
#define RAD_TO_DEG (180.0 / 3.14159265358979323846)

/* Стани скінченного автомата менеджера Home Point */
typedef enum {
    HOME_STATE_UNINITIALIZED = 0,
    HOME_STATE_ACQUIRING_LOCK,
    HOME_STATE_LOCKED_STATIC,
    HOME_STATE_TRACKING_DYNAMIC,
    HOME_STATE_FALLBACK_RALLY
} HomeState;

/* Геодезичні координати 3D */
typedef struct {
    double lat;      /* Градуси (-90.0 .. +90.0) */
    double lon;      /* Градуси (-180.0 .. +180.0) */
    float  alt_msl;  /* Висота над рівнем моря, метри */
} GeoCoord3D;

/* Вектор 2D швидкості або вітру */
typedef struct {
    float vx;  /* Швидкість на Північ (North), м/с */
    float vy;  /* Швидкість на Схід (East), м/с */
} Vector2D;

/* Стан навігаційного фільтра EKF */
typedef struct {
    GeoCoord3D pos;
    Vector2D   vel;
    float      hacc;            /* Горизонтальна точність (1-sigma), м */
    float      vacc;            /* Вертикальна точність (1-sigma), м */
    float      hdop;            /* Geometric dilution of precision */
    int        satellites;      /* Кількість супутників */
    float      ekf_test_ratio;  /* Нев'язка інновацій EKF (< 1.0 - норма, < 0.2 - відмінно) */
    bool       is_converged;    /* Прапорець збіжності EKF */
} EkfState;

/* Точка безпечного збору (Rally Point) */
typedef struct {
    int        id;
    GeoCoord3D pos;
    float      safe_alt_agl;    /* Безпечна висота заходу над ґрунтом, м */
    float      clear_radius_m;  /* Радіус вільної від перешкод зони, м */
    bool       is_active;       /* Чи доступний майданчик */
} RallyPoint;

/* Конфігурація менеджера */
typedef struct {
    float req_hacc_m;           /* Максимально допустима горизонтальна похибка (напр. 1.8 м) */
    float req_hdop;             /* Максимальний HDOP (напр. 1.2) */
    int   req_sats;             /* Мінімальна кількість супутників (напр. 14) */
    float hold_time_s;          /* Час утримання стабільних умов для фіксації (напр. 5.0 с) */
    float air_speed_cruise_ms;  /* Крейсерська повітряна швидкість дрона, м/с */
    float power_cruise_w;       /* Потужність споживання в крейсерському польоті, Вт */
    float power_climb_w;        /* Потужність при наборі висоти, Вт */
} HomeConfig;

/* Основна структура менеджера */
typedef struct {
    HomeState   state;
    HomeConfig  config;
    GeoCoord3D  home_pos;
    float       home_baro_ground_pa; /* Тиск на рівні землі на старті */
    float       stable_timer_s;      /* Лічильник стабільного вікна */
    
    /* Стан динамічної бази (Moving Home) */
    GeoCoord3D  base_pos_raw;
    Vector2D    base_vel_est;
    double      last_base_update_s;
    float       alpha_pos;           /* Коефіцієнт alpha-beta фільтра */
    float       beta_vel;

    /* Реєстр точок збору */
    RallyPoint  rally_points[MAX_RALLY_POINTS];
    int         rally_count;
} HomeManager;

/* Обчислення ортодромічної відстані за формулою гаверсинусів (Haversine) */
static double calculate_distance_m(GeoCoord3D a, GeoCoord3D b) {
    double dlat = (b.lat - a.lat) * DEG_TO_RAD;
    double dlon = (b.lon - a.lon) * DEG_TO_RAD;
    double lat1 = a.lat * DEG_TO_RAD;
    double lat2 = b.lat * DEG_TO_RAD;

    double sin_dlat2 = sin(dlat / 2.0);
    double sin_dlon2 = sin(dlon / 2.0);
    double h = sin_dlat2 * sin_dlat2 + cos(lat1) * cos(lat2) * sin_dlon2 * sin_dlon2;
    double c = 2.0 * atan2(sqrt(h), sqrt(1.0 - h));
    return EARTH_RADIUS_M * c;
}

/* Обчислення азимута (bearing) від точки A до точки B у радіанах */
static double calculate_bearing_rad(GeoCoord3D a, GeoCoord3D b) {
    double lat1 = a.lat * DEG_TO_RAD;
    double lat2 = b.lat * DEG_TO_RAD;
    double dlon = (b.lon - a.lon) * DEG_TO_RAD;

    double y = sin(dlon) * cos(lat2);
    double x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon);
    double bearing = atan2(y, x);
    if (bearing < 0.0) {
        bearing += 2.0 * 3.14159265358979323846;
    }
    return bearing;
}

/* Ініціалізація менеджера */
void home_manager_init(HomeManager *mgr, HomeConfig cfg) {
    if (!mgr) return;
    mgr->state = HOME_STATE_UNINITIALIZED;
    mgr->config = cfg;
    mgr->stable_timer_s = 0.0f;
    mgr->rally_count = 0;
    mgr->alpha_pos = 0.85f;
    mgr->beta_vel = 0.05f;
    mgr->last_base_update_s = 0.0;
    mgr->home_baro_ground_pa = 101325.0f;
}

/* Додавання точки збору (Rally Point) */
bool home_manager_add_rally_point(HomeManager *mgr, RallyPoint pt) {
    if (!mgr || mgr->rally_count >= MAX_RALLY_POINTS) return false;
    mgr->rally_points[mgr->rally_count++] = pt;
    return true;
}

/* Оновлення стану менеджера на основі телеметрії EKF */
void home_manager_update_ekf(HomeManager *mgr, const EkfState *ekf, float dt_s, float raw_baro_pa) {
    if (!mgr || !ekf || dt_s <= 0.0f) return;

    switch (mgr->state) {
        case HOME_STATE_UNINITIALIZED:
            if (ekf->satellites >= mgr->config.req_sats &&
                ekf->hdop <= mgr->config.req_hdop &&
                ekf->hacc <= mgr->config.req_hacc_m &&
                ekf->ekf_test_ratio < 0.25f &&
                ekf->is_converged) {
                mgr->state = HOME_STATE_ACQUIRING_LOCK;
                mgr->stable_timer_s = dt_s;
            }
            break;

        case HOME_STATE_ACQUIRING_LOCK:
            if (ekf->satellites >= mgr->config.req_sats &&
                ekf->hdop <= mgr->config.req_hdop &&
                ekf->hacc <= mgr->config.req_hacc_m &&
                ekf->ekf_test_ratio < 0.25f) {
                mgr->stable_timer_s += dt_s;
                if (mgr->stable_timer_s >= mgr->config.hold_time_s) {
                    /* Умови стабільні протягом заданого вікна -> Фіксація точки */
                    mgr->home_pos = ekf->pos;
                    mgr->home_baro_ground_pa = raw_baro_pa;
                    mgr->state = HOME_STATE_LOCKED_STATIC;
                }
            } else {
                /* Деградація якості до завершення вікна -> скидання таймера */
                mgr->stable_timer_s = 0.0f;
                mgr->state = HOME_STATE_UNINITIALIZED;
            }
            break;

        case HOME_STATE_LOCKED_STATIC:
        case HOME_STATE_TRACKING_DYNAMIC:
        case HOME_STATE_FALLBACK_RALLY:
            /* У польоті статична позиція не перезаписується автоматично */
            break;
    }
}

/* Оновлення координати рухомої бази (Moving Home) з екстраполяцією затримки */
void home_manager_update_moving_base(HomeManager *mgr, GeoCoord3D base_raw, Vector2D base_vel, double timestamp_s, double current_time_s) {
    if (!mgr) return;

    double latency_s = current_time_s - timestamp_s;
    if (latency_s < 0.0 || latency_s > 5.0) {
        /* Застарілий або некоректний пакет телеметрії бази */
        return;
    }

    /* Екстраполяція зміщення бази за час затримки радіоканалу */
    double dt_n_m = base_vel.vx * latency_s;
    double dt_e_m = base_vel.vy * latency_s;

    double lat_rad = base_raw.lat * DEG_TO_RAD;
    double dlat_deg = (dt_n_m / EARTH_RADIUS_M) * RAD_TO_DEG;
    double dlon_deg = (dt_e_m / (EARTH_RADIUS_M * cos(lat_rad))) * RAD_TO_DEG;

    GeoCoord3D extrapolated_pos;
    extrapolated_pos.lat = base_raw.lat + dlat_deg;
    extrapolated_pos.lon = base_raw.lon + dlon_deg;
    extrapolated_pos.alt_msl = base_raw.alt_msl;

    if (mgr->state == HOME_STATE_LOCKED_STATIC || mgr->state == HOME_STATE_TRACKING_DYNAMIC) {
        mgr->home_pos = extrapolated_pos;
        mgr->base_pos_raw = base_raw;
        mgr->base_vel_est = base_vel;
        mgr->last_base_update_s = current_time_s;
        mgr->state = HOME_STATE_TRACKING_DYNAMIC;
    }
}

/* Розрахунок енергетичної вартості перельоту до цільової точки з урахуванням вітру */
static float evaluate_travel_cost(const HomeManager *mgr, GeoCoord3D current_pos, GeoCoord3D target_pos, Vector2D wind) {
    double dist_m = calculate_distance_m(current_pos, target_pos);
    if (dist_m < 1.0) return 0.0f;

    double bearing_rad = calculate_bearing_rad(current_pos, target_pos);
    float track_dx = (float)sin(bearing_rad);
    float track_dy = (float)cos(bearing_rad);

    /* Проекція вітру на лінію шляху (попутний вітер > 0, зустрічний < 0) */
    float wind_along_track = wind.vy * track_dx + wind.vx * track_dy;
    float ground_speed = mgr->config.air_speed_cruise_ms + wind_along_track;

    /* Якщо зустрічний вітер переважає повітряну швидкість, рух неможливий */
    if (ground_speed < 2.0f) {
        return 1e9f; /* Недосяжна точка */
    }

    float flight_time_s = (float)(dist_m / ground_speed);
    float energy_joules = flight_time_s * mgr->config.power_cruise_w;

    /* Додаткова вартість набору висоти, якщо майданчик вищий за поточну позицію */
    float alt_diff = target_pos.alt_msl - current_pos.alt_msl;
    if (alt_diff > 0.0f) {
        float climb_time = alt_diff / 2.5f; /* 2.5 м/с вертикальна швидкість */
        energy_joules += climb_time * mgr->config.power_climb_w;
    }

    return energy_joules;
}

/* Багатокритеріальний вибір найкращої точки повернення (Home vs Rally Points) */
bool home_manager_select_best_destination(const HomeManager *mgr, GeoCoord3D current_pos, Vector2D wind, float battery_energy_joules, GeoCoord3D *out_target, int *out_rally_id) {
    if (!mgr || !out_target) return false;

    float best_cost = 1e9f;
    GeoCoord3D best_target = mgr->home_pos;
    int selected_rally_id = -1; /* -1 означає Home Point */

    /* 1. Оцінка вартості польоту до основної домашньої точки */
    if (mgr->state == HOME_STATE_LOCKED_STATIC || mgr->state == HOME_STATE_TRACKING_DYNAMIC) {
        best_cost = evaluate_travel_cost(mgr, current_pos, mgr->home_pos, wind);
    }

    /* 2. Оцінка вартості для кожного доступного Rally Point */
    for (int i = 0; i < mgr->rally_count; ++i) {
        if (!mgr->rally_points[i].is_active) continue;

        float rally_cost = evaluate_travel_cost(mgr, current_pos, mgr->rally_points[i].pos, wind);
        if (rally_cost < best_cost) {
            best_cost = rally_cost;
            best_target = mgr->rally_points[i].pos;
            selected_rally_id = mgr->rally_points[i].id;
        }
    }

    /* 3. Перевірка достатності заряду з коефіцієнтом безпеки 1.30 (30% запасу) */
    if (best_cost * 1.30f > battery_energy_joules) {
        /* Енергії недостатньо навіть для оптимальної точки */
        *out_target = best_target;
        if (out_rally_id) *out_rally_id = selected_rally_id;
        return false; /* Failsafe: потрібна екстрена посадка на маршруті */
    }

    *out_target = best_target;
    if (out_rally_id) *out_rally_id = selected_rally_id;
    return true;
}
