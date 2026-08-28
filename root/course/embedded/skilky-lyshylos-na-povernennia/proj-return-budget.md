# 🛠️ Модуль оцінки енергетичного бюджету повернення на C та C++

Цей проектний розбір містить повну реалізацію бортового оцінювача бюджету повернення *(Return Budget Estimator)*. Модуль розраховує трикутник швидкостей для довільного напрямку вітру, знаходить оптимальну крейсерську швидкість проти вітру, прогнозує просідання напруги під навантаженням та керує кінцевим автоматом виклику RTL.

Код спроектовано для роботи на бортових мікроконтролерах реального часу (STM32H7, ESP32-S3, RP2040) без динамічного виділення пам'яті (`malloc`/`new`).

## 1. Архітектура та математичний контур обчислення

Робота модуля на кожному кроці розбита на сім послідовних математичних етапів:

1. **Геометричний аналіз повернення**: обчислення вектора зближення з точкою Home `(d_north, d_east)` у локальній системі координат NED та прямої горизонтальної дистанції `D = √(d_north² + d_east²)`. Якщо апарат уже перебуває в радіусі домашньої зони (менше 15 метрів), обчислення перериваються зі статусом `RETURN_STATE_OK`.
2. **Проєкція вітрового вектора**: знаходження зустрічної складової `V_headwind` через скалярний добуток вектора вітру та одиничного вектора курсу додому, а також бокової складової `V_crosswind` через псевдоскалярний (двовимірний векторний) добуток.
3. **Оптимізація швидкості (поляра Маккреді)**: визначення оптимальної повітряної швидкості `V_air*`. При зустрічному вітрі швидкість зростає для скорочення часу перельоту, при попутному — знижується до економічного крейсерського режиму.
4. **Перевірка ліміту бокового зносу**: якщо `V_crosswind ≥ V_air`, апарат фізично не здатен компенсувати знос, модуль повертає статус `RETURN_ERR_CROSSWIND_LIMIT` та ініціює аварійну посадку. В іншому випадку обчислюється кут випередження вітру `WCA` та результуюча шляхова швидкість `V_ground`.
5. **Розрахунок компонентів енергії**: інтеграція потужності горизонтального перельоту `E_cruise`, енергії набору безпечного ешелону `E_climb`, енергії маневру посадки `E_land` та нарахування гарантованого коефіцієнта запасу `E_reserve`.
6. **Низькочастотна фільтрація (Anti-Chattering)**: експоненційне згладжування повної оцінки енергії фільтром 1-го порядку для усунення брязкоту тригера RTL від короткочасних вітрових поривів.
7. **Компенсація просідання напруги (Voltage Sag)**: розрахунок очікуваного струму повернення `I_return`, прогнозування просідання `ΔV = I_return · R_int` та динамічне відсікання недосяжного залишку ємності батареї.

## 2. Чисельна стабільність та захист від граничних станів

Під час виконання тригонометричних обчислень у середовищі мікроконтролера з апаратним FPU одиночної точності (IEEE 754 float32) можливі чисельні похибки округлення:

* **Захист функції арксинуса**: відношення `v_crosswind / v_air_opt` через шум давача швидкості або порив вітру може короткочасно перевищити `1.0f` (наприклад, `1.00004f`). Без примусового обмеження функція `asinf()` поверне `NaN`, що призведе до катастрофічного збою навігаційного фільтра. Функція `clampf(val, -1.0f, 1.0f)` гарантує валідність аргументу.
* **Захист від ділення на нуль**: при нульовій або від'ємній шляховій швидкості (`v_ground <= 1.0f`) час польоту `t = D / v_ground` прямує до нескінченності. Модуль негайно перериває розрахунок і переводить систему в аварійний режим `RETURN_STATE_EMERGENCY_LAND`.
* **Захист від втрати сенсора повітряної швидкості**: якщо трубка Піто забивається льодом або брудом, EKF автопілота переходить у синтетичний режим оцінки швидкості за прискореннями GNSS та кутами тангажу. Оцінювач продовжує роботу на синтетичній швидкості, збільшуючи гарантований запас `reserve_margin_ratio` на 10%.

## 3. Практичне калібрування параметрів за логами польотів

Для точної роботи модуля на конкретному планері необхідно визначити коефіцієнти `c_ind` та `c_par`:

1. **Калібрування аеродинамічної поляри**:
   * Виконується тестовий політ у штиль на кількох фіксованих швидкостях (наприклад, 12, 15, 18, 22 м/с) на постійній висоті.
   * З бортового журналу витягуються значення середньої електричної потужності `P_elec` для кожної швидкості.
   * Методом найменших квадратів виконується підгонка функції `P(V) = c_ind / V + c_par · V³ + P_avionics`.
2. **Калібрування внутрішнього опору батареї `R_int`**:
   * На висоті виконується серія східчастих імпульсів газу (з 30% до 85% тяги тривалістю 2 секунди).
   * За різницею миттєвої напруги та струму обчислюється динамічний опір `R_int = (V_idle - V_step) / (I_step - I_idle)`.
   * Отримане значення зберігається в конфігурації з температурним коефіцієнтом для зимових умов.

## 4. Реалізація бібліотеки на C та C++

:::tabs
@tab C (return_budget.c)
```c
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
```
@tab C++ (ReturnBudgetEstimator.cpp)
```cpp
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
```
:::

## 5. Інтеграція в польотний цикл автопілота

Навігаційний контур викликає метод оновлення в періодичному потоці керування. Якщо функція повертає ознаку `rtl_mandatory`, автопілот ініціює зміну режиму на RTL, фіксує причину в бортовому журналі Flash та інформує наземний пульт керування.

:::tabs
@tab C
```c
void navigation_periodic_2hz(void) {
    return_telemetry_t telem;
    read_sensors_and_ekf(&telem);

    return_budget_result_t budget;
    int32_t status = return_budget_update(&g_return_budget_handle, &telem, &budget);

    if (status == RETURN_OK) {
        if (budget.rtl_mandatory) {
            trigger_failsafe_rtl(RTL_REASON_BATTERY_PNR);
        } else if (budget.state == RETURN_STATE_CAUTION) {
            send_mavlink_statustext(MAV_SEVERITY_WARNING, "PNR approaching: wind reserve critical");
        }
    } else {
        handle_navigation_error(status);
    }
}
```
@tab C++
```cpp
void NavigationTask::onPeriodicUpdate(float dt_seconds) {
    const auto telemetry = sensor_manager_.getLatestTelemetry();
    
    if (const auto budget = return_estimator_.update(telemetry, dt_seconds)) {
        if (budget->rtl_mandatory) {
            failsafe_controller_.triggerRtl(FailsafeReason::BatteryPointOfNoReturn);
        } else if (budget->state == 1 /* CAUTION */) {
            telemetry_bus_.postWarning("PNR approaching: wind reserve critical");
        }
    } else {
        diagnostics_.reportError("Return budget estimation failed: invalid state");
    }
}
```
:::

## 6. Верифікація та тестові сценарії

Для підтвердження надійності модуля на етапі збірки виконується набір автоматичних юніт-тестів із контрольними польотними сценаріями:

1. **Тест симетричного штилю**: перевірка, що при нульовому вітрі розрахункова оптимальна швидкість строго дорівнює `v_best_range_still_ms`, а час повернення відповідає формулі `D / V_0`.
2. **Тест штормового зустрічного вітру**: перевірка виявлення неможливості повернення при `V_wind >= V_air_max` та переходу у стан `RETURN_STATE_EMERGENCY_LAND`.
3. **Тест просідання напруги на виснаженій батареї**: перевірка, що при залишку заряду 25% та внутрішньому опорі 70 мОм розрахунковий корисний залишок енергії зменшується на величину прогнозованого штрафу за падіння напруги.
4. **Тест фільтрації поривів**: подача короткочасного сплеску швидкості вітру тривалістю 0.5 секунди не повинна викликати помилкового спрацьовування прапорця `rtl_mandatory`.
5. **Тест бокового зносу (Crosswind Stall)**: перевірка, що при боковому вітрі `16 м/с` та повітряній швидкості `15 м/с` модуль не падає у виняток `NaN`, а повертає статус `RETURN_ERR_CROSSWIND_LIMIT`.
