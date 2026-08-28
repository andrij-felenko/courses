# ⚙️ Налаштування термопрофілю для ручного монтажу

Коли інженер паяє багатошарову друковану плату на нагрівальному столику або монтує мікросхему в корпусі QFN за допомогою термоповітряного фена, інтуїтивне бажання «просто виставити 250 °C і погріти, поки припій не заблищить» майже гарантовано призводить до браку. Спроба гріти плату у відкритому контурі без точного контролю швидкості наростання температури створює катастрофічний тепловий удар. Склотекстоліт вигинається від нерівномірного розширення внутрішніх мідних шарів, залишкова волога всередині компаунду мікросхем миттєво скипає з утворенням мікротріщин (ефект «попкорну»), а флюс повністю вигорає й окиснюється задовго до того, як розплавляться кульки припою під масивним заземленим тепловідводом (Thermal Pad).

Цей проєкт реалізує вбудований контролер термопрофілю для нижнього підігріву (Hot Plate / Preheater) та комбінованих станцій ручного монтажу. Програма виконує цифрове зчитування термопари K-типу з апаратною компенсацією холодного спаю, замкнене ПІД-регулювання потужності нагрівача з фільтрацією диференціального шуму, автоматичне проходження чотирьох фаз температурного профілю стандарту IPC/JEDEC J-STD-020 та захист від теплового розгону при механічному зміщенні або обриві датчика.

## Теплова модель та розрахунок фаз профілю

Багатошарова друкована плата становить собою неоднорідну термодинамічну систему: теплопровідність мідних полігонів (`k ≈ 390 Вт/(м·К)`) у тисячу разів перевищує теплопровідність епоксидного склотекстоліту FR-4 (`k ≈ 0.3 Вт/(м·К)`). Якщо до поверхні холодної плати прикласти високотемпературний струмінь повітря, виникає крутий просторовий температурний градієнт `dT/dx`. Швидкість зміни температури в кожній точці описується рівнянням теплопровідності Фур'є з урахуванням конвективних втрат в оточуюче середовище:

```
dT/dt = (k / (ρ · c)) · ∇²T - (h · A / (m · c)) · (T - T_amb) + (P_heater / (m · c))
```

де `ρ` — густина матеріалу, `c` — питома теплоємність, `h` — коефіцієнт тепловіддачі конвекцією, `A` — площа поверхні, `P_heater` — підведена потужність нагрівання.

Щоб запобігти механічній деструкції та забезпечити правильну хімічну активацію флюсу, процес ручного монтажу розбивається на чотири фази з жорсткими обмеженнями на похідну температури за часом `dT/dt`:

```
Температура T (°C)
  245 ┤                       ╭───────╮            [Фаза 3: Reflow, T_peak = 240..245 °C]
      │                      ╱         ╲
  217 ┤· · · · · · · · · · ·╱· · · · · ·╲· · · ·   [Точка плавлення SAC305 = 217 °C]
      │           ╭────────╯             ╲
  150 ┤          ╱ [Фаза 2: Soak]         ╲
      │         ╱  (150..180 °C, 60..90 с) ╲
      │  ╭─────╯                            ╲      [Фаза 4: Cooldown, < 3 °C/с]
   25 ┤──╯ [Фаза 1: Preheat, 1.0..2.0 °C/с]  ╲────
      └─────────────────────────────────────────── Час t (секунди)
```

1. **Фаза підігріву (Preheat):** підйом температури від 25 °C до 150 °C зі строго контрольованою швидкістю `1.0..2.0 °C/с`. Перевищення швидкості 2.5 °C/с створює термічний стрес у керамічних конденсаторах типорозмірів 0805–1210: різниця коефіцієнтів розширення титанату барію та срібних торцевих електродів призводить до утворення прихованих мікротріщин.
2. **Фаза витримки (Soak / Activation):** плато 150–180 °C тривалістю 60–90 секунд. У цей проміжок відбувається вирівнювання теплового потенціалу між тонкими сигнальними доріжками та багатошаровими полігонами землі. Водночас м'які розчинники флюсу спокійно випаровуються, а кислотні активатори руйнують оксидні плівки на міді, готуючи чистий метал до змочування.
3. **Фаза оплавлення (Reflow):** короткочасний сплеск вище точки ліквідусу припою. Для безсвинцевого сплаву SAC305 (`T_melt = 217 °C`) пікова температура становить 235–245 °C; для евтектичного олов'яно-свинцевого Sn63Pb37 (`T_melt = 183 °C`) пік становить 210–225 °C. Час перебування над точкою плавлення (*Time Above Liquidus*, TAL) обмежується 30–60 секундами, щоб запобігти надмірному росту інтерметалідів `Cu6Sn5` та `Cu3Sn`, які роблять паяний шов крихким.
4. **Фаза охолодження (Cooldown):** спад температури зі швидкістю не більше 2.0–3.0 °C/с. Надто швидке охолодження призводить до викривлення плати, а занадто повільне формує грубозернисту матрицю припою зі зниженою механічною витривалістю.

## Архітектура прошивки та інтерфейс керування

Контролер побудовано за схемою періодичного опитування сенсорів із фіксованим квантом часу (100 мс для внутрішнього контуру ПІД-регулятора та 1 с для кінцевого автомата етапів). Зчитування термопари здійснюється за інтерфейсом SPI з мікросхеми MAX31855, яка виконує 14-бітне аналого-цифрове перетворення з роздільною здатністю 0.25 °C та повертає діагностичні прапорці обриву термопари (OC), замикання на землю (SCG) або живлення (SCV).

Для керування нагрівальним елементом використовується низькочастотний програмний ШІМ із періодом 1 секунда, синхронізований із нульовою фазою мережі (через оптопару з Zero-Cross детекцією для SSR) або швидкий ШІМ для низьковольтних нагрівальних столиків постійного струму.

:::tabs
```c
/* profile_controller.h - Керування термопрофілем (C99) */
#ifndef PROFILE_CONTROLLER_H
#define PROFILE_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STAGE_IDLE = 0,
    STAGE_PREHEAT,
    STAGE_SOAK,
    STAGE_REFLOW,
    STAGE_COOLDOWN,
    STAGE_ERROR_FAULT
} ProfileStage;

typedef enum {
    FAULT_NONE = 0,
    FAULT_SENSOR_DISCONNECTED,
    FAULT_THERMAL_RUNAWAY,
    FAULT_OVERHEAT_LIMIT
} SystemFault;

typedef struct {
    float kp;
    float ki;
    float kd;
    float integral;
    float prev_error;
    float integral_limit;
    float derivative_filter; /* коефіцієнт згладжування шуму */
    float filtered_derivative;
} PidController;

typedef struct {
    float target_temp;
    float ramp_rate;       /* °C за секунду */
    uint32_t hold_time_s;  /* час витримки на етапі */
} StageConfig;

typedef struct {
    ProfileStage stage;
    SystemFault fault;
    float current_temp;
    float target_temp;
    float duty_cycle;      /* 0.0f .. 1.0f */
    uint32_t stage_timer_s;
    uint32_t runaway_counter_s;
    float temp_at_full_power;
    uint8_t current_stage_idx;
    PidController pid;
    StageConfig stages[4];
} ReflowController;

void reflow_init(ReflowController *ctrl, const StageConfig *configs);
void reflow_start(ReflowController *ctrl);
void reflow_abort(ReflowController *ctrl, SystemFault reason);
void reflow_tick_1s(ReflowController *ctrl, float measured_temp, bool sensor_valid);

#endif /* PROFILE_CONTROLLER_H */
```
```cpp
// ProfileController.hpp - Керування термопрофілем (C++20)
#pragma once

#include <array>
#include <cstdint>
#include <span>
#include <algorithm>
#include <cmath>
#include <expected>

namespace embedded::thermal {

enum class Stage : uint8_t {
    Idle = 0,
    Preheat,
    Soak,
    Reflow,
    Cooldown,
    ErrorFault
};

enum class Fault : uint8_t {
    None = 0,
    SensorDisconnected,
    ThermalRunaway,
    OverheatLimit
};

struct StageConfig {
    float target_temp_c;
    float ramp_rate_c_per_s;
    uint32_t hold_time_s;
};

class PidController {
public:
    constexpr PidController(float kp, float ki, float kd, float int_limit, float d_filter = 0.7f) noexcept
        : kp_(kp), ki_(ki), kd_(kd), integral_limit_(int_limit), d_filter_(d_filter) {}

    void reset() noexcept {
        integral_ = 0.0f;
        prev_error_ = 0.0f;
        filtered_derivative_ = 0.0f;
    }

    [[nodiscard]] float calculate(float setpoint, float measured, float dt_s) noexcept {
        const float error = setpoint - measured;
        
        // Інтегрування з анти-віндапом (обмеження накопичення)
        integral_ += error * dt_s;
        integral_ = std::clamp(integral_, -integral_limit_, integral_limit_);

        // Диференціювання з фільтром низьких частот першого порядку
        const float raw_derivative = (dt_s > 0.0f) ? ((error - prev_error_) / dt_s) : 0.0f;
        filtered_derivative_ = (d_filter_ * filtered_derivative_) + ((1.0f - d_filter_) * raw_derivative);
        prev_error_ = error;

        const float output = (kp_ * error) + (ki_ * integral_) + (kd_ * filtered_derivative_);
        return std::clamp(output, 0.0f, 1.0f);
    }

private:
    float kp_;
    float ki_;
    float kd_;
    float integral_limit_;
    float d_filter_;
    float integral_{0.0f};
    float prev_error_{0.0f};
    float filtered_derivative_{0.0f};
};

class ReflowController {
public:
    static constexpr size_t kStageCount = 4;
    static constexpr float kMaxSafeTempC = 270.0f;
    static constexpr float kMinRunawayRiseC = 2.0f; // Мінімально очікуваний підйом T за 15 с при 100% потужності

    explicit ReflowController(std::array<StageConfig, kStageCount> config) noexcept
        : stages_(config), pid_(0.035f, 0.0008f, 0.18f, 40.0f, 0.75f) {}

    void start() noexcept {
        if (stage_ == Stage::Idle) {
            stage_ = Stage::Preheat;
            current_stage_idx_ = 0;
            stage_timer_s_ = 0;
            runaway_counter_s_ = 0;
            target_temp_ = 25.0f;
            pid_.reset();
            fault_ = Fault::None;
        }
    }

    void abort(Fault reason) noexcept {
        stage_ = Stage::ErrorFault;
        fault_ = reason;
        duty_cycle_ = 0.0f;
    }

    [[nodiscard]] Stage current_stage() const noexcept { return stage_; }
    [[nodiscard]] Fault current_fault() const noexcept { return fault_; }
    [[nodiscard]] float duty_cycle() const noexcept { return duty_cycle_; }
    [[nodiscard]] float target_temp() const noexcept { return target_temp_; }

    void tick_1s(std::expected<float, Fault> sensor_reading) noexcept {
        if (!sensor_reading.has_value()) {
            abort(sensor_reading.error());
            return;
        }

        const float current_temp = sensor_reading.value();
        if (current_temp > kMaxSafeTempC) {
            abort(Fault::OverheatLimit);
            return;
        }

        if (stage_ == Stage::Idle || stage_ == Stage::ErrorFault) {
            duty_cycle_ = 0.0f;
            return;
        }

        // Перевірка захисту від теплового розгону (Thermal Runaway Watchdog)
        if (duty_cycle_ > 0.95f) {
            if (current_temp - temp_at_full_power_ < kMinRunawayRiseC) {
                runaway_counter_s_++;
                if (runaway_counter_s_ >= 15) {
                    abort(Fault::ThermalRunaway);
                    return;
                }
            } else {
                runaway_counter_s_ = 0;
                temp_at_full_power_ = current_temp;
            }
        } else {
            runaway_counter_s_ = 0;
            temp_at_full_power_ = current_temp;
        }

        process_stage_progression(current_temp);
        duty_cycle_ = pid_.calculate(target_temp_, current_temp, 1.0f);
    }

private:
    void process_stage_progression(float current_temp) noexcept {
        const auto& cfg = stages_[current_stage_idx_];

        // Плавне зміщення уставки за заданим рампом
        if (target_temp_ < cfg.target_temp_c) {
            target_temp_ += cfg.ramp_rate_c_per_s;
            if (target_temp_ > cfg.target_temp_c) target_temp_ = cfg.target_temp_c;
        } else if (target_temp_ > cfg.target_temp_c) {
            target_temp_ -= cfg.ramp_rate_c_per_s;
            if (target_temp_ < cfg.target_temp_c) target_temp_ = cfg.target_temp_c;
        }

        // Перевірка стабілізації та відліку часу витримки
        if (std::abs(current_temp - cfg.target_temp_c) <= 3.0f || target_temp_ == cfg.target_temp_c) {
            stage_timer_s_++;
            if (stage_timer_s_ >= cfg.hold_time_s) {
                advance_stage();
            }
        }
    }

    void advance_stage() noexcept {
        stage_timer_s_ = 0;
        current_stage_idx_++;
        if (current_stage_idx_ >= kStageCount) {
            stage_ = Stage::Idle;
            duty_cycle_ = 0.0f;
            target_temp_ = 25.0f;
        } else {
            stage_ = static_cast<Stage>(current_stage_idx_ + 1);
        }
    }

    std::array<StageConfig, kStageCount> stages_;
    PidController pid_;
    Stage stage_{Stage::Idle};
    Fault fault_{Fault::None};
    size_t current_stage_idx_{0};
    uint32_t stage_timer_s_{0};
    uint32_t runaway_counter_s_{0};
    float target_temp_{25.0f};
    float duty_cycle_{0.0f};
    float temp_at_full_power_{25.0f};
};

} // namespace embedded::thermal
```
:::

## Інженерні пастки та правила калібрування

Під час налаштування та роботи з саморобними або лабораторними термостоликами виникають типові критичні проблеми:

1. **Термічний шум та диференціальний сплеск:** термопара K-типу генерує напругу порядку `41 мкВ/°C`. Імпульсні перешкоди від комутації нагрівача (наприклад, симістора чи польового транзистора) наводять на дроти термопари паразитні шуми амплітудою в кілька мілівольтів. Нефільтрована похідна `de/dt` у класичному ПІД-регуляторі реагує на ці стрибки миттєвими хаотичними змінами вихідної потужності. Застосування цифрового фільтра низьких частот для `D`-складової з коефіцієнтом `0.7..0.8` повністю ліквідує цей шум без втрати швидкості реакції системи.
2. **Інтегральне насичення (Windup) на фазі розгону:** масивна алюмінієва плита столика має велику теплову інерцію (теплоємність `C = m · c`). Під час фази підігріву реальна температура завжди відстає від лінійно зростаючої уставки на 10–15 °C. Якщо не обмежити накопичення інтегральної складової константою `integral_limit`, на момент досягнення полиці витримки (150 °C) інтегратор буде повністю насичений. У результаті столик вилетить за уставку на 25–40 °C вгору (*overshoot*), що спалить флюс до початку паяння.
3. **Зсув холодного спаю біля гарячих вузлів:** мікросхема MAX31855 вимірює напругу термопари відносно температури власного кремнієвого кристала. Якщо вимірювальна плата розташована під столиком чи обдувається вихідним повітрям нагрівача, температура чіпа може піднятися до 60–80 °C, що створює похибку вимірювання в 15–20 °C. Плату перетворювача необхідно виносити за межі теплового контуру та з'єднувати з термопарою екранованим компенсаційним кабелем.
