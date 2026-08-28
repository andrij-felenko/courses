# ⚙️ Реалізація менеджера домашньої точки та точок збору на C та C++

Ця практична вставка містить алгоритмічну реалізацію бортового менеджера домашньої точки (`Home Position Manager`) та диспетчера точок безпечного збору (`Rally Point Selector`) мовами C та C++. Вона потрібна для того, щоб перетворити теоретичні вимоги до валідації навігаційних даних, екстраполяції затримки рухомої бази та розрахунку енергетичної вартості повернення проти вітру на надійний модуль керування польотом, готовий до інтеграції в польотний стек реального часу.

Без спеціалізованого менеджера логіка RTL в автопілотах зводиться до сліпого захоплення перших доступних координат або вибору найближчої географічної точки без урахування залишкової ємності акумулятора, зустрічного вітру чи теплового розгону барометра. Наведений нижче модуль реалізує повний життєвий цикл керування точкою повернення: сувору фільтрацію розширеного фільтра Калмана (EKF) перед фіксацією, екстраполяцію координат рухомої бази через альфа-бета фільтр та багатокритеріальний вибір між домашнім майданчиком і мережею Rally Points.

## Архітектурні вимоги та детермінізм реального часу

Розробка навігаційного модуля для критичних бортових систем вимагає дотримання суворих правил детермінізму:

1. **Відсутність динамічного виділення пам'яті в циклі виконання:** функції `malloc`, `free`, а також неконтрольоване розширення контейнерів (як-от динамічна релокація пам'яті) суворо заборонені в контурі керування. Усі масиви точок збору та буфери телеметрії мають фіксовані максимальні розміри на етапі компіляції (`MAX_RALLY_POINTS = 16`).
2. **Чисельна стійкість тригонометричних обчислень:** при розрахунку ортодромічної відстані між координатами застосовується формула гаверсинусів (англ. *Haversine formula*), яка запобігає втраті значущих розрядів при малих різницях координат, типових для польотів на дистанції до кількох десятків кілометрів.
3. **Захист від застарілих та хибних повідомлень:** модуль перевіряє часові мітки телеметрії бази та відкидає пакети, затримка яких перевищує допустимий ліміт (`t_latency > 5.0 с`), переходячи в режим аварійної ізоляції.

## Стани скінченного автомата та логіка переходів

Модуль спроєктовано навколо скінченного автомата станів (англ. *Finite State Machine*, FSM):

- **`UNINITIALIZED` (Неініціалізовано):** стан після подачі живлення на борт. Навігаційні дані відсутні або розкид псевдодальностей перевищує допустимі норми. Блокування Arming. Модуль постійно опитує стан EKF.
- **`ACQUIRING_LOCK` (Накопичення та схід):** супутники захоплено, але коваріації EKF ще не зійшлися. Модуль веде ковзне часове вікно (наприклад, 5–10 секунд), перевіряючи виконання сукупності строгих критеріїв: горизонтальна точність `HACC < 1.8 м`, показник просторової геометрії `HDOP < 1.2`, кількість видимих супутників `Sats ≥ 14` та інноваційна нев'язка EKF `test_ratio < 0.25`. Будь-який короткочасний сплеск шуму скидає лічильник стабільності в нуль.
- **`LOCKED_STATIC` (Статична фіксація):** критерії стабільності виконано протягом усього вікна; координати `(lat, lon, alt_msl)` та опорний атмосферний тиск на рівні ґрунту `P_ground` зафіксовано як основну домашню точку. Автопілот отримує дозвіл на озброєння (Arming Ready).
- **`TRACKING_DYNAMIC` (Супровід рухомої бази):** спеціальний режим для виконання місій із катерів, морських суден або мобільних командних пунктів. Модуль приймає пакети MAVLink `HOME_POSITION` або `GPS_RAW_INT`, компенсує затримку передачі `Δt_latency` за вектором швидкості судна та перевіряє радіус розходження.
- **`FALLBACK_RALLY` (Аварійний вибір точки збору):** у разі нестачі енергії на повернення додому проти сильного вітру або блокування базової точки модуль розраховує енергетичну вартість досягнення кожного доступного майданчика з реєстру `RallyPoint` з урахуванням тривимірного вектора руху та залишку заряду батареї.

## Повна реалізація мовами C та C++

:::tabs
```c
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
```
```cpp
#include <iostream>
#include <vector>
#include <optional>
#include <cmath>
#include <numbers>
#include <algorithm>
#include <array>

namespace drone::navigation {

inline constexpr double EarthRadiusM = 6371000.0;
inline constexpr double DegToRad = std::numbers::pi / 180.0;
inline constexpr double RadToDeg = 180.0 / std::numbers::pi;

enum class HomeState {
    Uninitialized,
    AcquiringLock,
    LockedStatic,
    TrackingDynamic,
    FallbackRally
};

struct GeoCoord3D {
    double lat{0.0};      // Градуси
    double lon{0.0};      // Градуси
    float  alt_msl{0.0f}; // Метри над рівнем моря
};

struct Vector2D {
    float vx{0.0f}; // North, м/с
    float vy{0.0f}; // East, м/с
};

struct EkfState {
    GeoCoord3D pos;
    Vector2D   vel;
    float      hacc{99.0f};
    float      vacc{99.0f};
    float      hdop{99.0f};
    int        satellites{0};
    float      ekf_test_ratio{1.0f};
    bool       is_converged{false};
};

struct RallyPoint {
    int        id{0};
    GeoCoord3D pos;
    float      safe_alt_agl{30.0f};
    float      clear_radius_m{25.0f};
    bool       is_active{true};
};

struct HomeConfig {
    float req_hacc_m{1.8f};
    float req_hdop{1.2f};
    int   req_sats{14};
    float hold_time_s{5.0f};
    float air_speed_cruise_ms{15.0f};
    float power_cruise_w{180.0f};
    float power_climb_w{280.0f};
};

class HomeManager {
public:
    explicit HomeManager(HomeConfig config)
        : m_config(config) {}

    void add_rally_point(const RallyPoint& point) {
        m_rally_points.push_back(point);
    }

    void update_ekf(const EkfState& ekf, float dt_s, float raw_baro_pa) {
        if (dt_s <= 0.0f) return;

        switch (m_state) {
            case HomeState::Uninitialized:
                if (is_ekf_quality_sufficient(ekf)) {
                    m_state = HomeState::AcquiringLock;
                    m_stable_timer_s = dt_s;
                }
                break;

            case HomeState::AcquiringLock:
                if (is_ekf_quality_sufficient(ekf)) {
                    m_stable_timer_s += dt_s;
                    if (m_stable_timer_s >= m_config.hold_time_s) {
                        m_home_pos = ekf.pos;
                        m_home_baro_ground_pa = raw_baro_pa;
                        m_state = HomeState::LockedStatic;
                    }
                } else {
                    m_stable_timer_s = 0.0f;
                    m_state = HomeState::Uninitialized;
                }
                break;

            case HomeState::LockedStatic:
            case HomeState::TrackingDynamic:
            case HomeState::FallbackRally:
                break;
        }
    }

    void update_moving_base(GeoCoord3D base_raw, Vector2D base_vel, double timestamp_s, double current_time_s) {
        const double latency_s = current_time_s - timestamp_s;
        if (latency_s < 0.0 || latency_s > 5.0) {
            return;
        }

        const double dt_n_m = base_vel.vx * latency_s;
        const double dt_e_m = base_vel.vy * latency_s;

        const double lat_rad = base_raw.lat * DegToRad;
        const double dlat_deg = (dt_n_m / EarthRadiusM) * RadToDeg;
        const double dlon_deg = (dt_e_m / (EarthRadiusM * std::cos(lat_rad))) * RadToDeg;

        GeoCoord3D extrapolated_pos{
            base_raw.lat + dlat_deg,
            base_raw.lon + dlon_deg,
            base_raw.alt_msl
        };

        if (m_state == HomeState::LockedStatic || m_state == HomeState::TrackingDynamic) {
            m_home_pos = extrapolated_pos;
            m_base_vel_est = base_vel;
            m_last_base_update_s = current_time_s;
            m_state = HomeState::TrackingDynamic;
        }
    }

    struct ReturnPlan {
        GeoCoord3D destination;
        std::optional<int> rally_id;
        float required_energy_joules{0.0f};
        bool is_safe_return{false};
    };

    [[nodiscard]] ReturnPlan evaluate_return_destination(GeoCoord3D current_pos, Vector2D wind, float battery_energy_joules) const {
        ReturnPlan plan;
        float best_cost = 1e9f;
        GeoCoord3D best_destination = m_home_pos;
        std::optional<int> chosen_rally_id = std::nullopt;

        if (m_state == HomeState::LockedStatic || m_state == HomeState::TrackingDynamic) {
            best_cost = compute_travel_cost(current_pos, m_home_pos, wind);
        }

        for (const auto& rally : m_rally_points) {
            if (!rally.is_active) continue;
            float cost = compute_travel_cost(current_pos, rally.pos, wind);
            if (cost < best_cost) {
                best_cost = cost;
                best_destination = rally.pos;
                chosen_rally_id = rally.id;
            }
        }

        plan.destination = best_destination;
        plan.rally_id = chosen_rally_id;
        plan.required_energy_joules = best_cost;
        plan.is_safe_return = (best_cost * 1.30f <= battery_energy_joules);

        return plan;
    }

    [[nodiscard]] HomeState state() const noexcept { return m_state; }
    [[nodiscard]] GeoCoord3D home_position() const noexcept { return m_home_pos; }
    [[nodiscard]] float home_baro_pa() const noexcept { return m_home_baro_ground_pa; }

private:
    [[nodiscard]] bool is_ekf_quality_sufficient(const EkfState& ekf) const noexcept {
        return ekf.satellites >= m_config.req_sats &&
               ekf.hdop <= m_config.req_hdop &&
               ekf.hacc <= m_config.req_hacc_m &&
               ekf.ekf_test_ratio < 0.25f &&
               ekf.is_converged;
    }

    [[nodiscard]] static double compute_distance_m(GeoCoord3D a, GeoCoord3D b) noexcept {
        const double dlat = (b.lat - a.lat) * DegToRad;
        const double dlon = (b.lon - a.lon) * DegToRad;
        const double lat1 = a.lat * DegToRad;
        const double lat2 = b.lat * DegToRad;

        const double sin_dlat = std::sin(dlat / 2.0);
        const double sin_dlon = std::sin(dlon / 2.0);
        const double h = sin_dlat * sin_dlat + std::cos(lat1) * std::cos(lat2) * sin_dlon * sin_dlon;
        return EarthRadiusM * (2.0 * std::atan2(std::sqrt(h), std::sqrt(1.0 - h)));
    }

    [[nodiscard]] static double compute_bearing_rad(GeoCoord3D a, GeoCoord3D b) noexcept {
        const double lat1 = a.lat * DegToRad;
        const double lat2 = b.lat * DegToRad;
        const double dlon = (b.lon - a.lon) * DegToRad;

        const double y = std::sin(dlon) * std::cos(lat2);
        const double x = std::cos(lat1) * std::sin(lat2) - std::sin(lat1) * std::cos(lat2) * std::cos(dlon);
        double bearing = std::atan2(y, x);
        if (bearing < 0.0) {
            bearing += 2.0 * std::numbers::pi;
        }
        return bearing;
    }

    [[nodiscard]] float compute_travel_cost(GeoCoord3D current_pos, GeoCoord3D target_pos, Vector2D wind) const noexcept {
        const double dist_m = compute_distance_m(current_pos, target_pos);
        if (dist_m < 1.0) return 0.0f;

        const double bearing_rad = compute_bearing_rad(current_pos, target_pos);
        const float track_dx = static_cast<float>(std::sin(bearing_rad));
        const float track_dy = static_cast<float>(std::cos(bearing_rad));

        const float wind_along_track = wind.vy * track_dx + wind.vx * track_dy;
        const float ground_speed = m_config.air_speed_cruise_ms + wind_along_track;

        if (ground_speed < 2.0f) {
            return 1e9f; // Вітер перевищує можливості апарата
        }

        const float flight_time_s = static_cast<float>(dist_m / ground_speed);
        float energy_joules = flight_time_s * m_config.power_cruise_w;

        const float alt_diff = target_pos.alt_msl - current_pos.alt_msl;
        if (alt_diff > 0.0f) {
            const float climb_time_s = alt_diff / 2.5f;
            energy_joules += climb_time_s * m_config.power_climb_w;
        }

        return energy_joules;
    }

    HomeState              m_state{HomeState::Uninitialized};
    HomeConfig             m_config;
    GeoCoord3D             m_home_pos{};
    float                  m_home_baro_ground_pa{101325.0f};
    float                  m_stable_timer_s{0.0f};
    Vector2D               m_base_vel_est{};
    double                 m_last_base_update_s{0.0};
    std::vector<RallyPoint> m_rally_points{};
};

} // namespace drone::navigation
```
:::

## Інженерні граблі та аналіз крайових випадків

1. **Ігнорування затримки телеметрії Moving Base:** якщо судно рухається зі швидкістю 15 вузлів (~7.7 м/с), а затримка радіоканалу становить 2 секунди, сирі координати GCS запізнюються на 15.4 метра. Без екстраполяції за вектором швидкості дрон при спробі посадки здійснить удар об воду за кормою судна.
2. **Перезаписування Home Point у повітрі без підтвердження оператора:** якщо польотний контролер скидає точку зльоту в момент відновлення сигналу GNSS після глибокого глушіння, дрон фіксує домашню точку прямо посеред ворожої території або над лісом на маршовій висоті.
3. **Вибір найближчого Rally Point за чистою геодезичною відстанню:** за наявності сильного вітру (12–15 м/с) найближчий проти вітру майданчик (відстань 3 км) вимагає значно більше енергії та часу, ніж розташований за 6 км майданчик за вітром. Критерій вибору зобов'язаний спиратися на розрахунок шляхової швидкості `v_ground = v_air + v_wind_along`.
4. **Сліпе скидання висоти без комплексування з далекоміром:** якщо барометр зазнав синоптичного або теплового дрейфу, зниження до відносної висоти `0.0 м` за барометром призводить до вимкнення двигунів у повітрі або удару об ґрунт на швидкості 2 м/с. На висотах нижче 15 м обов'язково активується оптичний або лазерний далекомір AGL.

## Інтеграція в цикл опитування бортової шини (uORB / AP_HAL)

У реальному польотному стеку (наприклад, у середовищі PX4 на базі шини публікацій-підписок uORB або в ArduPilot на базі планувальника завдань `AP_Scheduler`) модуль викликається у високопріоритетному навігаційному потоці:

- **Підписка на топіки:** екземпляр класу підписується на топіки `vehicle_local_position` (отримання інновацій та дисперсій EKF), `vehicle_gps_position` (кількість супутників, значення DOP) та `sensor_combined` (покази барометра та температури плати).
- **Обробка переповнення часових міток:** внутрішній лічильник часу використовує монотонний системний таймер мікросекунд (`hrt_absolute_time()` у PX4). Обчислення різниці `dt` захищене від переповнення 32-розрядних лічильників та стрибків назад при синхронізації часу GNSS.
- **Публікація оновленої точки:** при переході автопілота в стан `LOCKED_STATIC` або при супроводі в стані `TRACKING_DYNAMIC` менеджер публікує структуру `home_position` у системну шину, сповіщаючи навігаційний планувальник Navigator та модуль безпеки Commander про готовність до безаварійного виконання процедури RTL.

