# 📋 Інтерфейс модуля розрахунку енергетичного бюджету повернення

Цей довідник визначає публічний контракт модуля `return_budget` — вбудованої бібліотеки для автопілотів (PX4, ArduPilot або власного польотного контролера) та бортових комп'ютерів *(companion computer)*. Модуль виконує періодичний розрахунок енергії для повернення на базу, визначає оптимальну повітряну швидкість проти вітру, враховує динамічне просідання напруги батареї та формує подію примусового RTL.

## 1. Архітектурні принципи та вимоги до середовища

Модуль розроблено з дотриманням суворих вимог до вбудованого програмного забезпечення реального часу критичних систем:

* **Детермінізм часу виконання**: усі обчислення виконуються за фіксовану кількість тактів процесора без ітеративних циклів із невідомим часом збіжності чи рекурсії. На процесорі ARM Cortex-M7 із частотою 480 МГц час виконання функції оновлення становить менше 4 мікросекунд.
* **Відсутність динамічної пам'яті**: заборонено виклики `malloc`, `free`, `new` та роботу з купами пам'яті. Усі контексти та структури виділяються статично або на стеку викликаючого потоку.
* **Сумісність із MISRA C:2012**: код відповідає правилам безпечного програмування, використовує явне приведення типів, перевірку меж та захист від ділення на нуль і взяття квадратного кореня з від'ємних чисел.
* **Повторна входжуваність (Reentrancy)**: бібліотека не містить глобального змінного стану. Кілька екземплярів монітора можуть одночасно обробляти телеметрію різних силових установок або альтернативних точок посадки.

## 2. Заголовні файли та версіонування

Модуль надає чистий C99-інтерфейс для польотних контролерів і сувору типізовану обгортку C++17/C++20 для високорівневих систем бортового інтелекту.

:::tabs
@tab C (return_budget.h)
```c
#ifndef RETURN_BUDGET_H
#define RETURN_BUDGET_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define RETURN_BUDGET_API_VERSION_MAJOR 1
#define RETURN_BUDGET_API_VERSION_MINOR 0

#ifdef __cplusplus
}
#endif

#endif /* RETURN_BUDGET_H */
```
@tab C++ (ReturnBudget.hpp)
```cpp
#pragma once

#include <cstdint>
#include <optional>
#include <string_view>

namespace uav::nav {

constexpr std::string_view kReturnBudgetVersion = "1.0.0";

} // namespace uav::nav
```
:::

## 3. Типи даних, стани та коди повернення

### 3.1. Кінцевий автомат станів повернення

Кінцевий автомат FSM інкапсулює логіку прийняття навігаційних рішень. Переходи між станами відбуваються на основі зіставлення корисної енергії батареї з необхідним бюджетом повернення:

* `RETURN_STATE_OK` (0): корисний запас батареї істотно перевищує необхідну енергію повернення разом із гарантованим резервом (`Margin > 15%`). Автопілот виконує місію в штатному режимі.
* `RETURN_STATE_CAUTION` (1): розрахункова маржа запасу опустилася нижче 10%. Бортовий навігатор генерує попередження оператору, забороняючи прокладання точок місії далі від бази.
* `RETURN_STATE_RTL_MANDATORY` (2): пройдено динамічну точку неповернення (`E_batt_usable <= E_return`). Потрібне негайне примусове переривання місії та активація повернення додому.
* `RETURN_STATE_EMERGENCY_LAND` (3): повернення на базу фізично неможливе (швидкість зустрічного вітру перевищує льотні спроможності борту, боковий вітер не дозволяє втримати курс або напруга просіла до апаратного порогу відсікання). Потрібна негайна посадка на запасний майданчик або в поле.

### 3.2. Коди статусів та помилок

Кожна функція модуля повертає 32-бітний цілочисельний статус. Від'ємні значення відповідають помилкам, нуль — успішному завершенню.

| Код повернення | Число | Фізична причина та реакція системи |
|---|---|---|
| `RETURN_OK` | `0` | Обчислення виконано успішно, вихідні дані валідні |
| `RETURN_ERR_HEADWIND_TOO_HIGH` | `-1` | Зустрічний вітер перевищує максимальну повітряну швидкість апарата (`V_w >= V_max`), шляхова швидкість падає до нуля або стає від'ємною |
| `RETURN_ERR_CROSSWIND_LIMIT` | `-2` | Боковий вітер перевищує повітряну швидкість (`V_w * sin(θ) > V_a`), апарат не здатний скомпенсувати знос і втримати пряму лінію |
| `RETURN_ERR_INVALID_CONFIG` | `-3` | Некоректні конфігураційні константи (нульова ємність, `V_min <= 0`, `V_max <= V_min`) |
| `RETURN_ERR_INVALID_TELEMETRY` | `-4` | Неприпустимі значення вхідних давачів (NaN, нульова напруга, відсутній фікс) |
| `RETURN_ERR_BATTERY_CRITICAL` | `-5` | Прогнозована термінальна напруга під навантаженням падає нижче `V_cutoff` |

## 4. Конфігураційні структури

### 4.1. Параметри літального апарата

Структура конфігурації заповнюється одноразово під час ініціалізації бортового стека з енергонезалежної пам'яті (Flash/EEPROM). Вона містить аеродинамічні характеристики планера, параметри силової установки та налаштування батарейного модуля.

Поля конфігурації мають суворі валідаційні обмеження:
* `c_ind`, `c_par` повинні бути строго додатними дійсними числами;
* `v_air_min_ms` має перевищувати швидкість звалювання планера щонайменше на 20%;
* `v_air_max_ms` задає конструктивну межу міцності та тяги двигуна;
* `cell_v_cutoff` для літій-іонних акумуляторів типово обирається в діапазоні 2.85–3.00 В на комірку для запобігання незворотній деградації хімічної структури катода.

:::tabs
@tab C
```c
typedef struct {
    float c_ind;                  /* Коефіцієнт індуктивного опору (Вт·с/м) */
    float c_par;                  /* Коефіцієнт паразитного опору (Вт·с³/м³) */
    float v_air_min_ms;           /* Мінімальна повітряна швидкість (зрив + запас), м/с */
    float v_air_max_ms;           /* Максимальна повітряна швидкість силової установки, м/с */
    float v_best_range_still_ms;  /* Швидкість найкращої дальності у штиль, м/с */
    float v_climb_ms;             /* Швидкість набору висоти, м/с */
    float p_climb_watts;          /* Потужність у наборі висоти, Вт */
    float v_descend_ms;           /* Швидкість зниження, м/с */
    float p_descend_watts;        /* Потужність на зниженні, Вт */
    float p_hover_watts;          /* Потужність зависання перед посадкою, Вт */
    float p_avionics_watts;       /* Базове споживання бортової електроніки, Вт */
    float t_land_maneuver_sec;    /* Гарантований час на зависання й автопосадку, с */
    float rtl_safe_altitude_m;    /* Безпечна мінімальна висота повернення, м */
    uint8_t cell_count;           /* Кількість послідовних комірок (наприклад, 6 для 6S) */
    float cell_v_cutoff;          /* Критична напруга відсікання на 1 комірку, В */
    float nominal_energy_wh;      /* Паспортна енергоємність збірки, Вт·год */
    float reserve_margin_ratio;   /* Коефіцієнт запасу на пориви вітру (0.15 … 0.25) */
    float filter_time_constant_s; /* Стала часу низькочастотного фільтра, с */
} return_config_t;
```
@tab C++
```cpp
struct ReturnConfig {
    float c_ind{0.0f};                  // Коефіцієнт індуктивного опору (Вт·с/м)
    float c_par{0.0f};                  // Коефіцієнт паразитного опору (Вт·с³/м³)
    float v_air_min_ms{10.0f};          // Мінімальна повітряна швидкість, м/с
    float v_air_max_ms{25.0f};          // Максимальна повітряна швидкість, м/с
    float v_best_range_still_ms{14.0f}; // Швидкість найкращої дальності у штиль, м/с
    float v_climb_ms{3.0f};             // Швидкість набору висоти, м/с
    float p_climb_watts{350.0f};        // Потужність у наборі висоти, Вт
    float v_descend_ms{2.5f};           // Швидкість зниження, м/с
    float p_descend_watts{120.0f};      // Потужність на зниженні, Вт
    float p_hover_watts{450.0f};        // Потужність зависання перед посадкою, Вт
    float p_avionics_watts{25.0f};      // Базове споживання бортової електроніки, Вт
    float t_land_maneuver_sec{45.0f};   // Гарантований час на посадку, с
    float rtl_safe_altitude_m{60.0f};   // Безпечна мінімальна висота повернення, м
    uint8_t cell_count{6};              // Кількість послідовних комірок (6S)
    float cell_v_cutoff{3.0f};          // Критична напруга відсікання на 1 комірку, В
    float nominal_energy_wh{180.0f};    // Паспортна енергоємність збірки, Вт·год
    float reserve_margin_ratio{0.20f};  // Коефіцієнт запасу на пориви вітру (20%)
    float filter_time_constant_s{2.0f}; // Стала часу низькочастотного фільтра, с
};
```
:::

## 5. Вхідна телеметрія та вихідні результати

### 5.1. Структура зрізу польотної телеметрії

Вхідна структура формується навігаційним контуром на кожному такті оцінки з виходів фільтра Калмана (EKF) та системи керування живленням (BMS). Вектор вітру подається у географічній системі координат NED (North-East-Down), де позитивні значення означають напрямок вітру на північ та схід відповідно.

Внутрішній опір `r_internal_ohms` оцінюється бортовим фільтром заряду за відгуком напруги на стрибки струму. Якщо оцінка опору недоступна (наприклад, на простій авіоніці без точного вимірювання струму), передається табличне значення, скориговане на температуру батареї.

:::tabs
@tab C
```c
typedef struct {
    float pos_current_ned[3];     /* Поточна позиція [Північ, Схід, Вниз], метри */
    float pos_home_ned[3];        /* Позиція точки повернення Home [Північ, Схід, Вниз], метри */
    float wind_ned[2];            /* Вектор горизонтального вітру [North, East], м/с */
    float voltage_v;              /* Поточна напруга батареї під навантаженням, В */
    float current_a;              /* Поточний струм розряду, А */
    float energy_remaining_wh;    /* Оцінка залишкової енергії, Вт·год */
    float soc_ratio;              /* Ступінь заряду (0.0 … 1.0) */
    float r_internal_ohms;        /* Внутрішній опір збірки, Ом */
    float battery_temp_c;         /* Температура акумуляторного блоку, °C */
} return_telemetry_t;
```
@tab C++
```cpp
struct ReturnTelemetry {
    std::array<float, 3> pos_current_ned{0.0f, 0.0f, 0.0f}; // Позиція [North, East, Down], м
    std::array<float, 3> pos_home_ned{0.0f, 0.0f, 0.0f};    // Точка Home [North, East, Down], м
    std::array<float, 2> wind_ned{0.0f, 0.0f};            // Вітер [North, East], м/с
    float voltage_v{0.0f};                                // Напруга батареї під навантаженням, В
    float current_a{0.0f};                                // Струм розряду, А
    float energy_remaining_wh{0.0f};                      // Залишкова енергія, Вт·год
    float soc_ratio{1.0f};                                // Ступінь заряду (0.0 … 1.0)
    float r_internal_ohms{0.05f};                         // Внутрішній опір, Ом
    float battery_temp_c{20.0f};                          // Температура блоку, °C
};
```
:::

### 5.2. Вихідна структура розрахунку енергетичного бюджету

Вихідна структура надає автопілоту повний розклад компонентів бюджету, розраховану оптимальну швидкість повернення та директивний прапорець виклику RTL.

Особливу увагу слід звертати на поле `projected_sag_voltage_v`: якщо воно наближається до порогу відсікання, автопілот має зменшити темп набору висоти для запобігання перевантаженню силової шини живлення.

:::tabs
@tab C
```c
typedef struct {
    float v_air_optimal_ms;       /* Оптимальна повітряна швидкість повернення V_a*, м/с */
    float v_ground_ret_ms;        /* Очікувана шляхова швидкість зближення з базою V_g, м/с */
    float wca_rad;                /* Кут випередження вітру WCA, радіани */
    float distance_to_home_m;     /* Пряма дистанція до домашньої точки, м */
    float time_to_home_sec;       /* Розрахунковий час повернення, с */
    float e_cruise_wh;            /* Енергія горизонтального перельоту проти вітру, Вт·год */
    float e_climb_wh;             /* Енергія набору безпечної висоти RTL, Вт·год */
    float e_land_wh;              /* Енергія процедури посадки, Вт·год */
    float e_reserve_wh;           /* Енергетичний запас на маневри й пориви, Вт·год */
    float e_return_total_wh;      /* Повна необхідна енергія на повернення, Вт·год */
    float e_usable_compensated_wh;/* Фактично доступна корисна енергія (Voltage Sag), Вт·год */
    float projected_sag_voltage_v;/* Прогнозована напруга на клемах при тязі повернення, В */
    float energy_margin_ratio;    /* Відносний залишок: (E_usable - E_return) / E_usable */
    uint8_t state;                /* Стан return_state_t */
    bool rtl_mandatory;           /* true — точка неповернення пройдена, потрібен RTL */
} return_budget_result_t;
```
@tab C++
```cpp
struct ReturnBudgetResult {
    float v_air_optimal_ms{0.0f};        // Оптимальна повітряна швидкість V_a*, м/с
    float v_ground_ret_ms{0.0f};         // Шляхова швидкість зближення V_g, м/с
    float wca_rad{0.0f};                 // Кут випередження вітру WCA, рад
    float distance_to_home_m{0.0f};      // Дистанція до точки Home, м
    float time_to_home_sec{0.0f};        // Розрахунковий час повернення, с
    float e_cruise_wh{0.0f};             // Енергія горизонтального перельоту, Вт·год
    float e_climb_wh{0.0f};              // Енергія набору висоти RTL, Вт·год
    float e_land_wh{0.0f};               // Енергія посадки, Вт·год
    float e_reserve_wh{0.0f};            // Запас на пориви, Вт·год
    float e_return_total_wh{0.0f};       // Повна необхідна енергія, Вт·год
    float e_usable_compensated_wh{0.0f}; // Корисна енергія з урахуванням Sag, Вт·год
    float projected_sag_voltage_v{0.0f}; // Прогнозована напруга під тягою, В
    float energy_margin_ratio{0.0f};     // Відносний залишок запасу
    uint8_t state{0};                    // Стан монітора
    bool rtl_mandatory{false};           // true — обов'язковий RTL
};
```
:::

## 6. Протоколи функцій та життєвий цикл

### 6.1. Ініціалізація та валідація параметрів

Функція `return_budget_init` перевіряє коректність конфігурації перед початком місії. Якщо хоча б один параметр виходить за фізичні межі (наприклад, `v_air_min_ms <= 0` або `reserve_margin_ratio < 0`), модуль повертає `RETURN_ERR_INVALID_CONFIG` і блокує зліт апарата.

:::tabs
@tab C
```c
int32_t return_budget_init(
    return_budget_handle_t* handle,
    const return_config_t* config
);
```
@tab C++
```cpp
// Конструктор класу ReturnBudgetEstimator виконує валідацію конфігурації
explicit ReturnBudgetEstimator(const ReturnConfig& config);
```
:::

### 6.2. Періодичний розрахунок у польотному циклі

Функція `return_budget_update` викликається в періодичному потоці навігації з рекомендованою частотою від 1 до 5 Гц. Вона виконує векторні розрахунки вітру, формує оцінку за методом Маккреді, згладжує результат низькочастотним фільтром і встановлює прапорець `rtl_mandatory`.

При частоті оновлення нижче 1 Гц підвищується ризик запізнення реакції на різкий вітровий порив, тоді як частоти вище 10 Гц є надлишковими через інерційність аеродинамічних та теплових процесів батареї.

:::tabs
@tab C
```c
int32_t return_budget_update(
    return_budget_handle_t* handle,
    const return_telemetry_t* telemetry,
    return_budget_result_t* result
);
```
@tab C++
```cpp
[[nodiscard]] std::optional<ReturnBudgetResult> update(
    const ReturnTelemetry& telemetry, 
    float dt_seconds
);
```
:::

### 6.3. Скидання фільтрів при перемиканні точок Home

Якщо оператор під час польоту призначає нову точку повернення (наприклад, рухомий майданчик на автомобілі або судні), викликається `return_budget_reset_filter`. Це запобігає затримці реакції фільтра на стрибок дистанції.

:::tabs
@tab C
```c
void return_budget_reset_filter(
    return_budget_handle_t* handle
);
```
@tab C++
```cpp
void reset() noexcept;
```
:::

## 7. Об'єктна C++ обгортка

Для сучасних C++ архітектур (MAVSDK-плагіни, ROS 2 вузли) інтерфейс надається класом `ReturnBudgetEstimator`:

:::tabs
@tab C
```c
/* Процедурне використання у стилі чистого C */
return_budget_handle_t g_budget_handle;
return_config_t g_budget_cfg = { ... };

void flight_init(void) {
    int32_t rc = return_budget_init(&g_budget_handle, &g_budget_cfg);
    if (rc != RETURN_OK) {
        panic_halt("Budget init failed");
    }
}
```
@tab C++
```cpp
namespace uav::nav {

class ReturnBudgetEstimator {
public:
    explicit ReturnBudgetEstimator(const ReturnConfig& config);

    ReturnBudgetEstimator(const ReturnBudgetEstimator&) = delete;
    ReturnBudgetEstimator& operator=(const ReturnBudgetEstimator&) = delete;
    ReturnBudgetEstimator(ReturnBudgetEstimator&&) noexcept = default;
    ReturnBudgetEstimator& operator=(ReturnBudgetEstimator&&) noexcept = default;

    [[nodiscard]] std::optional<ReturnBudgetResult> update(
        const ReturnTelemetry& telemetry, 
        float dt_seconds
    );

    [[nodiscard]] float computeOptimalAirspeed(float headwind_component_ms) const noexcept;
    [[nodiscard]] float computeGroundSpeed(float airspeed_ms, float wind_speed_ms, float wind_angle_rad) const noexcept;
    [[nodiscard]] float estimateVoltageSag(float current_draw_a, float r_internal_ohms) const noexcept;

    void reset() noexcept;
};

} // namespace uav::nav
```
:::

## 8. Протокол інтеграції з MAVLink та телеметрією GCS

Модуль безпосередньо транслює свої стани у стандартні поля протоколу MAVLink:
1. Залишок корисної енергії `e_usable_compensated_wh` та повний бюджет `e_return_total_wh` упаковуються в розширене повідомлення `BATTERY_STATUS_V2`.
2. Прапорець `rtl_mandatory` мапиться на біт `MAV_SYS_STATUS_SENSOR_BATTERY` системного статусу та викликає відправлення статусного тексту `STATUSTEXT` із пріоритетом `MAV_SEVERITY_WARNING`.
3. Оптимальна повітряна швидкість `v_air_optimal_ms` передається у контур контролера швидкості `TECS` *(Total Energy Control System)* як цільове значення під час виконання маневру повернення.
