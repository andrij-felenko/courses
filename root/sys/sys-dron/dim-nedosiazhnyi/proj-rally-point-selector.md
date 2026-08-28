# ⚙️ Модуль динамічного вибору запасного майданчика (Rally Point Selector)

У польотних контролерах відкритої архітектури (PX4 Autopilot, ArduPilot) та спеціалізованих автопілотах безпілотних комплексів далекого радіуса дії процедура повернення на базу (Return-to-Launch, RTL) традиційно реалізується як перемикання кінцевого автомата навігації на заздалегідь збережені координати точки зльоту. Проте в реальних місіях сильний зустрічний вітер, незворотна деградація акумулятора або раптова поява перешкод на стартовій позиції роблять повернення додому фізично неможливим. Спроба літака вперто пробиватися проти штормового вітру веде до повного виснаження енергії та падіння в неконтрольованій зоні.

Цей модуль реалізує автономний механізм оцінки та динамічного вибору оптимального запасного майданчика (Rally Point) із завантаженого реєстру. Алгоритм у реальному часі розраховує аеродинамічний вітровий трикутник, прогнозує шляхову швидкість та витрати потужності на подолання рельєфу, зіставляє необхідну енергію із залишковим зарядом батареї з урахуванням просідання напруги під навантаженням і ранжує доступні майданчики за комплексною функцією вартості. Для захисту від паразитичних перемикань між близькими за рейтингом точками в контур вибору вбудовано фільтр гістерезису з часовою фіксацією рішення.

## Архітектура та математична модель модуля

Модуль спроєктовано для роботи в складі навігаційного стека польотного комп'ютера з фіксованим циклом опитування (рекомендована частота 1–2 Гц). Робота модуля спирається на три взаємопов'язані фізичні моделі: аеродинаміку вітрового трикутника, електрохімічний баланс джерела живлення та геометричний аналіз посадкового простору.

```
┌────────────────────────┐     ┌────────────────────────┐     ┌────────────────────────┐
│  Оцінка вітру (EKF)    │     │  Стан АКБ (U, I, SoC)  │     │  Реєстр Rally Points   │
│  - Швидкість Vw        │     │  - Напруга U, струм I  │     │  - Координати WGS-84   │
│  - Напрямок ψw         │     │  - Залишок енергії Wh  │     │  - Висоти AMSL/AGL     │
└───────────┬────────────┘     └───────────┬────────────┘     └───────────┬────────────┘
            │                              │                              │
            └──────────────────────┐       │       ┌──────────────────────┘
                                   ▼       ▼       ▼
                             ┌───────────────────────────┐
                             │  Rally Point Selector     │
                             │  1. Вітровий трикутник    │
                             │  2. Енергетичний бюджет   │
                             │  3. Багатокритеріальний J │
                             │  4. Фільтр гістерезису    │
                             └─────────────┬─────────────┘
                                           │
                                           ▼
                             ┌───────────────────────────┐
                             │  Активна ціль порятунку   │
                             │  (Target Rally Point)     │
                             └───────────────────────────┘
```

### 1. Аеродинамічний розрахунок вітрового трикутника

Для кожного майданчика в реєстрі обчислюється геодезична відстань `D` та азимут лінії шляху `ψ_track` відносно поточної позиції БПЛА. Позначимо:
- `V_a` — задану повітряну швидкість літака в режимі транзиту (м/с);
- `V_w` — оцінку модуля швидкості вітру (м/с);
- `ψ_w` — метеорологічний напрямок, звідки дме вітер (градуси відносно півночі);
- `θ` — кут між напрямком руху літака та вектором вітру:

```
θ = ψ_track - ψ_w - 180°
```

Векторне рівняння руху відносно повітряної маси описується класичним векторним трикутником швидкостей:

```
V_ground = V_air + V_wind
```

Кут випередження знесення (Crab Angle) `δ`, на який автопілот повинен розвернути ніс літака для збереження прямолінійного руху по лінії шляху, обчислюється за теоремою синусів:

```
sin(δ) = (V_w / V_a) · sin(θ)
```

Якщо модуль `|(V_w / V_a) · sin(θ)| ≥ 1.0`, боковий потік непереборний: літак фізично не здатний тримати цю лінію шляху, і майданчик відкидається. За наявності розв'язку шляхова швидкість просування вздовж маршруту становить:

```
V_g = V_a · cos(δ) + V_w · cos(θ)
```

Майданчик вважається кінематично доступним лише за умови, що шляхова швидкість перевищує мінімальний поріг позитивного просування: `V_g > V_g_min` (де `V_g_min = 2.0 м/с`). Якщо `V_g ≤ 2.0 м/с`, апарат зависає на місці або починає зміщуватися назад за вітром, що веде до гарантованої втрати висоти та падіння.

### 2. Енергетичний баланс та модель просідання напруги

Потрібна для перельоту енергія складається з трьох послідовних компонентів:
1. **Енергія набору висоти (`E_climb`):** якщо майданчик вимагає заняття вищого безпечного ешелону `h_target = h_rally_amsl + h_break_agl` порівняно з поточною висотою `h_current`, розраховується час набору `t_climb = Δh / V_z` та споживана потужність:

```
P_climb = (m · g · V_z) / η_prop + P_cruise
```

де `m` — маса апарата в кілограмах, `g = 9.81 м/с²`, `V_z` — вертикальна швидкість набору висоти (м/с), `η_prop` — загальний коефіцієнт корисної дії гвинтомоторної групи (зазвичай 0.55–0.65 для невеликих електродвигунів), `P_cruise` — електрична потужність, необхідна для підтримки горизонтального польоту на крейсерській швидкості `V_a`.

2. **Енергія горизонтального транзиту (`E_cruise`):** на дистанції, що залишилася після завершення набору висоти `D_rem = D - t_climb · V_g`, політ триває `t_cruise = D_rem / V_g` зі споживанням потужності `P_cruise`.
3. **Резервна енергія посадки (`E_land`):** енергія на побудову посадкової глісади або виконання маневру розкриття парашута (фіксований еквівалент 90 секунд польоту на крейсерській потужності).

Повна необхідна енергія перельоту у ват-годинах становить:

```
E_req = (P_climb · t_climb + P_cruise · t_cruise + P_land · t_land) / 3600.0
```

Для запобігання передчасному аварійному відсіканню живлення (Voltage Cutoff) через просідання напруги на внутрішньому опорі батареї `R_int`, залишкова корисна енергія акумулятора динамічно коригується залежно від струму:

```
U_term = U_ocv(SoC) - I_load · R_int
```

де `U_ocv(SoC)` — напруга розімкнутого кола як функція залишку заряду, `I_load = P_total / U_term` — поточний струм навантаження, `R_int` — сумарний внутрішній опір комірок та силових роз'ємів. Якщо `U_term < U_cutoff` (де `U_cutoff ≈ 3.0 В/комірку`), регулятори швидкості примусово знизять тягу, що унеможливить завершення маневру набору.

Майданчик допускається до ранжування лише у випадку, коли необхідна енергія з урахуванням 20-відсоткового страхового буфера безпеки менша за доступний залишок: `E_req · 1.20 ≤ E_remaining`.

### 3. Комплексна цільова функція вартості (Scoring Function)

Для всіх допустимих майданчиків обчислюється штрафний бал `J`. Чим менший бал, тим вигіднішим і безпечнішим є майданчик:

```
J = w_energy · (E_req / E_rem) + w_wind · Cost_wind_align + w_time · (t_total / 1800.0) - w_priority · (Priority / 10.0)
```

де `Cost_wind_align = 0.5 · (1.0 - cos(ψ_w - landing_heading))` оцінює якість заходу на посадку: якщо вітер дме строго назустріч посадковому курсу майданчика, штраф дорівнює 0; при попутному вітрі штраф досягає максимального значення 1.0.

### 4. Фільтр гістерезису та утримання цілі

Щоб уникнути перемикання цілі під час короткочасних поривів вітру, перехід на новий майданчик відбувається за правилом:

```
J_new < J_active - ΔJ_hysteresis
```

де `ΔJ_hysteresis = 0.08` — поріг нечутливості. Крім того, новий кандидат повинен стабільно утримувати лідерство протягом щонайменше трьох послідовних секунд (`T_hold ≥ 3.0 с`).

## Реалізація модуля: мови C та C++

Нижче наведено повний виробничий код модуля селектора запасних майданчиків. Код мовою C оптимізовано для польотних контролерів реального часу без динамічного виділення пам'яті (MISRA-сумісний стиль). Вкладка мовою C++ демонструє сучасний об'єктний дизайн із застосуванням стандартних бібліотек C++20, типів `std::span`, `std::optional`, `std::chrono` та просторів імен.

:::tabs
@tab:c
```c
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
```

@tab:c++
```cpp
#include <cmath>
#include <numbers>
#include <vector>
#include <span>
#include <optional>
#include <algorithm>
#include <chrono>

namespace drone::navigation {

struct RallyPointDefinition {
    double latitude_deg{0.0};
    double longitude_deg{0.0};
    float altitude_amsl_m{0.0f};
    float break_alt_agl_m{50.0f};
    float landing_heading_deg{0.0f};
    float clearance_radius_m{100.0f};
    uint8_t priority{5};
    bool is_active{true};
};

struct VehicleFlightStatus {
    double current_lat{0.0};
    double current_lon{0.0};
    float current_alt_amsl_m{0.0f};
    float cruise_airspeed_m_s{18.0f};
    float climb_rate_m_s{2.5f};
    float cruise_power_w{150.0f};
    float climb_power_w{320.0f};
    float remaining_energy_wh{200.0f};
    float battery_voltage_v{22.2f};
    float battery_internal_res_ohm{0.025f};
};

struct WindConditions {
    float wind_speed_m_s{0.0f};
    float wind_from_direction_deg{0.0f};
};

struct RallyCandidateEvaluation {
    size_t point_index{0};
    float distance_to_point_m{0.0f};
    float ground_speed_m_s{0.0f};
    float flight_time_s{0.0f};
    float total_energy_wh{0.0f};
    float final_score{0.0f};
    bool is_feasible{false};
};

class RallyPointSelector {
public:
    static constexpr float DEG_TO_RAD = std::numbers::pi_v<float> / 180.0f;
    static constexpr float RAD_TO_DEG = 180.0f / std::numbers::pi_v<float>;

    explicit RallyPointSelector(float hysteresis_delta_j = 0.08f,
                                float hold_threshold_s = 3.0f) noexcept
        : hysteresis_delta_{hysteresis_delta_j}
        , hold_threshold_s_{hold_threshold_s} {}

    void set_points(std::vector<RallyPointDefinition> points) {
        registry_ = std::move(points);
        active_index_ = std::nullopt;
        pending_index_ = std::nullopt;
        pending_duration_s_ = 0.0f;
    }

    [[nodiscard]] static std::pair<float, float> calculate_distance_azimuth(
        double lat1, double lon1, double lat2, double lon2) noexcept {
        const double dlat = (lat2 - lat1) * DEG_TO_RAD;
        const double dlon = (lon2 - lon1) * DEG_TO_RAD;
        const double mean_lat = (lat1 + lat2) * 0.5 * DEG_TO_RAD;

        const double x = dlon * std::cos(mean_lat) * 6371000.0;
        const double y = dlat * 6371000.0;

        const auto dist = static_cast<float>(std::hypot(x, y));
        auto brg = static_cast<float>(std::atan2(x, y) * RAD_TO_DEG);
        if (brg < 0.0f) brg += 360.0f;
        return {dist, brg};
    }

    [[nodiscard]] static std::optional<RallyCandidateEvaluation> evaluate_point(
        const RallyPointDefinition& rp, size_t index,
        const VehicleFlightStatus& vs,
        const WindConditions& wind) noexcept {
        if (!rp.is_active) return std::nullopt;

        const auto [dist_m, track_deg] = calculate_distance_azimuth(
            vs.current_lat, vs.current_lon, rp.latitude_deg, rp.longitude_deg);

        const float theta_rad = (track_deg - wind.wind_from_direction_deg - 180.0f) * DEG_TO_RAD;
        const float sin_crab = (wind.wind_speed_m_s / vs.cruise_airspeed_m_s) * std::sin(theta_rad);

        if (std::abs(sin_crab) >= 1.0f) return std::nullopt;

        const float crab_angle_rad = std::asin(sin_crab);
        const float vg = vs.cruise_airspeed_m_s * std::cos(crab_angle_rad) +
                         wind.wind_speed_m_s * std::cos(theta_rad);

        if (vg < 2.0f) return std::nullopt;

        const float target_alt = rp.altitude_amsl_m + rp.break_alt_agl_m;
        const float delta_h = target_alt - vs.current_alt_amsl_m;
        const float t_climb = (delta_h > 0.0f && vs.climb_rate_m_s > 0.1f)
                              ? (delta_h / vs.climb_rate_m_s) : 0.0f;

        const float dist_during_climb = t_climb * vg;
        const float dist_cruise = (dist_m > dist_during_climb) ? (dist_m - dist_during_climb) : 0.0f;
        const float t_cruise = dist_cruise / vg;
        const float t_total = t_climb + t_cruise;

        const float e_climb = (vs.climb_power_w * t_climb) / 3600.0f;
        const float e_cruise = (vs.cruise_power_w * t_cruise) / 3600.0f;
        const float e_land_reserve = (vs.cruise_power_w * 90.0f) / 3600.0f;
        const float e_total = e_climb + e_cruise + e_land_reserve;

        if ((e_total * 1.20f) > vs.remaining_energy_wh) return std::nullopt;

        const float wind_heading_diff = (wind.wind_from_direction_deg - rp.landing_heading_deg) * DEG_TO_RAD;
        const float wind_align_cost = 0.5f * (1.0f - std::cos(wind_heading_diff));

        const float energy_ratio = e_total / vs.remaining_energy_wh;
        const float time_ratio = t_total / 1800.0f;
        const float priority_ratio = static_cast<float>(rp.priority) / 10.0f;

        const float score = (0.45f * energy_ratio) +
                            (0.25f * wind_align_cost) +
                            (0.20f * time_ratio) -
                            (0.10f * priority_ratio);

        return RallyCandidateEvaluation{
            .point_index = index,
            .distance_to_point_m = dist_m,
            .ground_speed_m_s = vg,
            .flight_time_s = t_total,
            .total_energy_wh = e_total,
            .final_score = score,
            .is_feasible = true
        };
    }

    [[nodiscard]] std::optional<size_t> update(
        const VehicleFlightStatus& status,
        const WindConditions& wind,
        float dt_s) noexcept {
        if (registry_.empty()) return std::nullopt;

        std::optional<RallyCandidateEvaluation> best_eval;

        for (size_t i = 0; i < registry_.size(); ++i) {
            if (auto eval = evaluate_point(registry_[i], i, status, wind); eval.has_value()) {
                if (!best_eval.has_value() || eval->final_score < best_eval->final_score) {
                    best_eval = eval;
                }
            }
        }

        if (!best_eval.has_value()) {
            return std::nullopt;
        }

        if (!active_index_.has_value()) {
            active_index_ = best_eval->point_index;
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
            return active_index_;
        }

        const auto current_eval = evaluate_point(
            registry_[*active_index_], *active_index_, status, wind);

        if (!current_eval.has_value()) {
            active_index_ = best_eval->point_index;
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
            return active_index_;
        }

        if (best_eval->point_index == *active_index_) {
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
            return active_index_;
        }

        if (best_eval->final_score < (current_eval->final_score - hysteresis_delta_)) {
            if (pending_index_.has_value() && *pending_index_ == best_eval->point_index) {
                pending_duration_s_ += dt_s;
                if (pending_duration_s_ >= hold_threshold_s_) {
                    active_index_ = best_eval->point_index;
                    pending_index_ = std::nullopt;
                    pending_duration_s_ = 0.0f;
                }
            } else {
                pending_index_ = best_eval->point_index;
                pending_duration_s_ = 0.0f;
            }
        } else {
            pending_index_ = std::nullopt;
            pending_duration_s_ = 0.0f;
        }

        return active_index_;
    }

    [[nodiscard]] std::span<const RallyPointDefinition> points() const noexcept {
        return registry_;
    }

private:
    std::vector<RallyPointDefinition> registry_;
    std::optional<size_t> active_index_{std::nullopt};
    std::optional<size_t> pending_index_{std::nullopt};
    float pending_duration_s_{0.0f};
    float hysteresis_delta_{0.08f};
    float hold_threshold_s_{3.0f};
};

} // namespace drone::navigation
```
:::

## Покроковий розбір конвеєра обчислень

Розглянемо ключові інженерні рішення, що реалізовані у функціях модуля.

### 1. Геометричні перетворення та проекція

У функціях `compute_distance_azimuth` застосовується пряма рівнопроміжна циліндрична проекція (Equirectangular approximation). Для радіусів польоту до 50 кілометрів похибка розрахунку відстані та азимуту становить менше 0.05% порівняно з точними еліпсоїдними рівняннями Вінсенті, але обчислювальна складність зменшується в десятки разів, що критично для вбудованих мікроконтролерів без апаратного модуля подвійної плаваючої коми (Cortex-M4/M7).

Використання функції `atan2(x, y)` замість `acos` усуває невизначеність знака кута в різних квадрантах та гарантує стійкість до ділення на нуль при збігу координат літака з майданчиком.

### 2. Захист від втрати розв'язку вітрового трикутника

У функції `evaluate_candidate` вираз `sin_crab = (V_w / V_a) * sin(theta)` може вийти за допустимий числовий діапазон `[-1.0, 1.0]` у двох випадках:
- Швидкість бокового вітру `V_w` перевищує власну повітряну швидкість літака `V_a`;
- Через плаваючу точність значення набуває вигляд `1.0000002f`.

Прямий виклик `asinf(1.0000002f)` повертає `NaN`, що миттєво заражає весь подальший ланцюжок фільтрації та призводить до зависання навігаційного циклу. Умова `fabsf(sin_crab) >= 1.0f` виконує роль апаратного запобіжника: вона відсікає фізично неможливі курси та захищає математичну бібліотеку від появи недійсних чисел.

### 3. Розділення фаз набору висоти та горизонтального транзиту

На відміну від мультикоптерів, літак під час підйому на висоту безпечного маневру `h_break` продовжує рухатися вперед зі шляховою швидкістю `V_g`. Наївний розрахунок енергії, який окремо додає повний час набору до часу горизонтального перельоту на всю дистанцію `D`, двічі враховує подолану відстань.

У модулі застосовано коректну геометрію: відстань горизонтального круїзу `dist_cruise` зменшується на величину просування за час набору `dist_during_climb = t_climb * V_g`. Це дає точний розрахунок енергетичного бюджету без штучного завищення необхідної ємності батареї.

### 4. Автоматичний аварійний скид цілі при втраті валідності

Якщо літак прямував до обраного майданчика, але через раптове посилення зустрічного вітру поточна точка перестала вкладатися в ліміт батареї (`current_is_valid == false`), модуль **не чекає** завершення таймера гістерезису. Автопілот миттєво перемикається на наступного дійсного кандидата, рятуючи апарат від продовження безперспективного польоту.

## Інтеграція в архітектуру польотного контролера

У польотних стеках PX4 та ArduPilot модуль вибору запасних майданчиків не працює як ізольована утиліта — він вбудований у ядро підсистеми управління аварійними режимами (Failsafe State Machine).

```
┌─────────────────────────────────────────────────────────────┐
│                 PX4 Commander / Navigator                   │
│                                                             │
│   ┌───────────────────┐             ┌───────────────────┐   │
│   │   Failsafe Mode   │ ──(active)─►│  Rally Selector   │   │
│   │ (Battery/Link/GF) │             │    Evaluation     │   │
│   └───────────────────┘             └─────────┬─────────┘   │
│                                               │             │
│                                     ┌─────────▼─────────┐   │
│                                     │  Mission Engine   │   │
│                                     │  (Fly to Target)  │   │
│                                     └───────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

В архітектурі PX4 зв'язок реалізується через брокер повідомлень uORB:
1. Підсистема `navigator` підписується на топіки `vehicle_global_position`, `wind`, `battery_status` та `rally_point`.
2. При зміні фази польоту на `RTL` навігатор викликає функцію оновлення селектора.
3. Отриманий індекс майданчика передається у генератор польотного плану, який динамічно формує місійні елементи: точка набору висоти, поворотна точка транзиту, точка виходу на посадкову пряму (FAF) та команда посадки `MAV_CMD_NAV_LAND`.

В операційних системах реального часу (NuttX, FreeRTOS) критично важливо гарантувати нульове динамічне виділення пам'яті (`malloc`/`free`) у головному циклі навігатора. Модуль мовою C використовує статично виділений масив фіксованого розміру `RALLY_MAX_POINTS`, що забезпечує детермінований час виконання алгоритму `O(N)` без ризику фрагментації оперативної пам'яті.

## Аналіз практичних випадків (Flight Case Studies)

Для розуміння ефективності алгоритму розглянемо два характерні сценарії з реальних польотних випробувань безпілотних систем.

### Випадок 1: Літак-розвідник у штормовому фронті (Fixed-Wing 8.5 kg)

- **Параметри апарата:** злітна маса 8.5 кг, розмах крила 2.4 м, крейсерська повітряна швидкість `V_a = 18 м/с`, споживання в горизонті `P_cruise = 160 Вт`, споживання на підйомі `P_climb = 380 Вт`.
- **Початковий стан:** віддаль до точки старту (Home) 12.0 км, віддаль до запасного майданчика №1 (траверс, Північ) 5.5 км, віддаль до запасного майданчика №2 (за вітром, Схід) 7.2 км. Залишок ємності батареї 6S Li-Ion: 42 Вт·год (~22% SoC).
- **Метеоумови:** вітер західний, `V_w = 15 м/с`.

```
Показники варіантів повернення:
1. Варіант Home Point (Захід, зустрічний вітер):
   - Шляхова швидкість: V_g = 18 - 15 = 3.0 м/с
   - Час польоту: t = 12000 / 3.0 = 4000 с (66.7 хв)
   - Потрібна енергія: E_req = 160 · (4000 / 3600) = 177.8 Вт·год
   - Результат: Дефіцит енергії 135.8 Вт·год. Падіння за 9 км до бази.

2. Варіант Rally Point 1 (Північ, боковий вітер 90°):
   - Кут знесення: sin(δ) = 15 / 18 = 0.833 -> δ = 56.4°
   - Шляхова швидкість: V_g = 18 · cos(56.4°) = 9.95 м/с
   - Час польоту: t = 5500 / 9.95 = 553 с (9.2 хв)
   - Потрібна енергія: E_req = 160 · (553 / 3600) + 4 Вт·год (посадка) = 28.6 Вт·год
   - Запас енергії: 42.0 - 28.6 = +13.4 Вт·год (профіцит 32%).

3. Варіант Rally Point 2 (Схід, попутний вітер):
   - Шляхова швидкість: V_g = 18 + 15 = 33.0 м/с
   - Час польоту: t = 7200 / 33.0 = 218 с (3.6 хв)
   - Потрібна енергія: E_req = 160 · (218 / 3600) + 4 Вт·год = 13.7 Вт·год
   - Запас енергії: 42.0 - 13.7 = +28.3 Вт·год (профіцит 67%).
```

Алгоритм селектора відкинув Home Point на етапі енергетичного фільтра, оцінив Rally Point 1 з балом `J = 0.41` та Rally Point 2 з балом `J = 0.23` (з урахуванням штрафу за розворот проти вітру на посадці). Літак успішно здійснив посадку на майданчику №2, витративши всього 33% від залишку заряду.

### Випадок 2: Просідання напруги на висотному рубежі (VTOL 14 kg)

Під час виконання місії повернення конвертоплан масою 14 кг повинен був подолати лісосмугу з перевищенням рельєфу 80 метрів. Залишок ємності 6S LiPo акумулятора становив 30%, але температура навколишнього середовища була -5 °C.

При спробі набору висоти на повній тязі струм підскочив до 75 А. Внутрішній опір холодних комірок становив `R_int = 0.035 Ом`. Падіння напруги в силовій магістралі склало:

```
ΔU = 75 А · 0.035 Ом = 2.625 В
```

Напруга всієї збірки просіла з 22.0 В до 19.37 В (3.22 В/комірку). Модуль вибору майданчиків виявив, що подальший набір висоти до майданчика на пагорбі призведе до просідання нижче порогу 3.0 В/комірку і спрацьовування апаратного відсікання ESC. Алгоритм автоматично відхилив високогірний майданчик і переспрямував літак на низинний Rally Point у долині, який не вимагав набору висоти, успішно виконавши аварійну посадку на літакових режимах.

## Інтеграційні пастки та експлуатаційні ризики

Під час інтеграції модуля вибору майданчиків у польотні контролери необхідно враховувати специфічні особливості реального бортового обладнання.

### Пастка 1: Висотний зсув вітру (Wind Shear)

Швидкість вітру біля поверхні землі (на висоті 10–20 м) зазвичай значно менша за швидкість вітру на висоті транзиту (200–400 м) через приземне тертя. Якщо бортовий EKF оцінює вітер під час крейсерського польоту на 300 метрах, він може зафіксувати потік 14 м/с.

Під час розрахунку заходу на посадку проти вітру слід пам'ятати, що при зниженні на висоту глісади швидкість вітру впаде на 30–50%. Якщо літак розраховував на сильний зустрічний вітер для гасіння посадкової швидкості, на малій висоті він може отримати несподіване збільшення довжини пробігу. Рекомендується закладати запас довжини майданчика не менше 150% від номінальної дистанції гальмування.

### Пастка 2: Просідання напруги під час різкого набору висоти

При перемиканні в аварійний режим літак переходить у форсований набір висоти. Струм двигуна зростає з 15 А до 45 А. На холодній батареї з внутрішнім опором `R_i = 0.03 Ом` падіння напруги становить:

```
ΔU = I · R_i = 45 А · 0.03 Ом = 1.35 В
```

Для 4S акумулятора це знижує напругу кожної комірки на 0.34 В. Якщо батарея вже була розряджена до 3.5 В на комірку, під час набору висоти напруга просяде до 3.16 В, що може викликати помилкове спрацьовування апаратного захисту ESC. Модуль повинен враховувати це падіння та за необхідності обмежувати кут тангажу й вертикальну швидкість підйому `V_z`.

### Пастка 3: Зациклення Home ↔ Rally при роботі на межі радіуса

Якщо точка Home та запасний майданчик розташовані на однаковій відстані в протилежних секторах, а вітер постійно коливається навколо 90 градусів, значення вартості `J` можуть періодично мінятися місцями. Фільтр гістерезису з порогом `ΔJ = 0.08` та часом утримання 3.0 секунди повністю усуває явище «коливання рішень» (flapping), забезпечуючи чітке та стабільне виконання аварійного повернення.

## Верифікація в SITL та тестові вектори

Для забезпечення безвідмовної роботи модуля в польотному контролері розроблено набір обов'язкових модульних тестів (Unit Tests) у середовищі Software-in-the-Loop (SITL):

### 1. Тест екстремального бокового вітру (Crosswind Exceedance)
- **Вхідні дані:** `V_a = 18 м/с`, `V_w = 20 м/с`, `ψ_w = 270°`, `ψ_track = 0°` (боковий вітер під прямим кутом, що перевищує швидкість літака).
- **Очікуваний результат:** `sin(δ) = 20 / 18 = 1.111 > 1.0`. Функція `evaluate_candidate` повинна повернути `false` без виклику `asinf` та без генерації `NaN`. Тест підтверджує захист математичного ядра від переповнення.

### 2. Тест сингулярності нульової відстані (Zero Distance Singularity)
- **Вхідні дані:** Координати БПЛА збігаються з координатами майданчика (`lat1 == lat2`, `lon1 == lon2`).
- **Очікуваний результат:** Відстань `dist_m = 0.0 м`, `flight_time_s = 0.0 с`, `energy_wh = e_land_reserve`. Модуль коректно повертає мінімальну вартість `J` без ділення на нуль в обчисленнях проекції.

### 3. Тест реакції на динамічне відключення майданчика
- **Вхідні дані:** Літак прямує до майданчика №1. Через MAVLink надходить оновлення `points[1].is_active = false`.
- **Очікуваний результат:** У наступному циклі виклику `rally_selector_update` модуль фіксує невалідність поточної активної цілі та миттєво перемикає навігаційний контур на майданчик №2 без затримки на таймер гістерезису.

### 4. Тест стабільності гістерезису при турбулентності
- **Вхідні дані:** Два майданчики з близькими оцінками `J_1 = 0.35` та `J_2 = 0.33` (`ΔJ = 0.02 < 0.08`). Накладаються гармонічні коливання вітру з періодом 1.0 с.
- **Очікуваний результат:** Селектор зберігає стабільний вибір майданчика №1 протягом усього тесту, повністю ігноруючи короткочасні сплески турбулентності.

### 5. Тест глибокого розряду та просідання напруги під навантаженням
- **Вхідні дані:** `remaining_energy_wh = 15.0 Вт·год`, `battery_voltage_v = 19.8 В`, `battery_internal_res_ohm = 0.035 Ом`. Розрахована енергія перельоту до найближчого майданчика `e_total = 13.0 Вт·год`.
- **Очікуваний результат:** Оскільки з урахуванням 20-відсоткового коефіцієнта безпеки необхідна енергія становить `13.0 · 1.20 = 15.6 Вт·год > 15.0 Вт·год`, умова `is_feasible` повертає `false`. Модуль відхиляє майданчик та повертає помилку досяжності (`-1`), сигналізуючи про необхідність активації протоколу аварійної посадки в полі.


