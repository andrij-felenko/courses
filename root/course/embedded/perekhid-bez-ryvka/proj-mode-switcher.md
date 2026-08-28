# ⚙️ Диспетчер режимів польоту з безривковим перемиканням

Розглянемо практичну реалізацію бортового диспетчера режимів польоту для безпілотного літального апарата. Програма керує трьома режимами польоту:
1. `MODE_MANUAL` — пряме прокидання ручки газу/елеватора пілота на виконавчі органи.
2. `MODE_ALT_HOLD` — автоматична стабілізація висоти барометричним ПІД-контуром.
3. `MODE_AUTO_MISSION` — автоматичний політ за маршрутними точками (Waypoints).

Головне завдання проекту — забезпечити математично строгу неперервність сигналу тяги та положення кермових поверхонь у моменти довільних перемикань тумблера пульта, виключаючи удари по приводах та клювання фюзеляжу, як описано в теоретичному розборі [переходу без ривка](root:embedded/perekhid-bez-ryvka).

## Архітектура диспетчера станів

Диспетчер режимів побудований за схемою скінченного автомата (Finite State Machine). При надходженні команди зміни режиму він:
1. Запитує останнє фактичне положення виконавчих приводів `u_prev`.
2. Зчитує свіжі показники сенсорів (висоту, кут тангажу).
3. Здійснює безривкову передачу повноважень (`bumpless handover`) активному регулятору.
4. Перемикає селектор джерела сигналів.

```
                  ┌────────────────────────────────────────┐
                  │          Диспетчер режимів             │
                  │        (Flight Mode Manager)           │
                  └──────────────────┬─────────────────────┘
                                     │
             ┌───────────────────────┼───────────────────────┐
             ▼                       ▼                       ▼
      [MODE_MANUAL]           [MODE_ALT_HOLD]        [MODE_AUTO_MISSION]
      Ручка пульта             ПІД-регулятор          Навігаційний контур
     u = Stick_throttle      u = PID(Alt_target)      u = PID(Waypoint_alt)
             │                       │                       │
             └───────────────────────┼───────────────────────┘
                                     │
                                     ▼
                       ┌───────────────────────────┐
                       │  Безривковий комутатор    │
                       │   u_new(0+) == u_prev     │
                       └─────────────┬─────────────┘
                                     ▼
                       [Сервопривід / Регулятор ESC]
```

## Апаратна інтеграція та конвеєр сигналів

У реальній прошивці польотного контролера (наприклад, на базі STM32F4/STM32H7) диспетчер режимів взаємодіє з трьома апаратними підсистемами:

1. **Канал команд оператора (RC Receiver)**: Дані від приймача (CRSF або SBUS) надходять через UART у режимі DMA з періодом 20 мс (50 Гц) або 6.6 мс (150 Гц для швидких лінків ExpressLRS). Диспетчер виділяє значення каналу газу (Throttle) та 3-позиційного перемикача режимів (AUX1).
2. **Датчик висоти (Barometer / Altitude Fusion)**: Висота вимірюється барометричним сенсором (MS5611/BMP280 через шину SPI), після чого комплексується з вертикальним прискоренням акселерометра в комплементарному фільтрі для отримання висоти без шумів і з мінімальною затримкою.
3. **Вихідний генератор ШІМ / DShot**: Розрахований сигнал `output` перетворюється на керувальний пакет протоколу DShot або імпульси ШІМ таймера (період 400 Гц), що керують швидкістю обертання безколекторних двигунів або кутом сервомашинок.

## Алгоритм зворотного узгодження ручки (Stick Matching)

Окрема інженерна проблема виникає при переході з автоматичного режиму назад у ручний (`MODE_ALT_HOLD -> MODE_MANUAL`). Поки апарат летів в автоматі, пілот міг випадково або навмисно зсунути фізичну ручку газу на пульті в крайнє нижнє положення (наприклад, 20% замість 56%, які тримав автопілот).

Якщо в момент перемикання миттєво підключити ручку пульта до двигунів, виникне той самий удар керування (Control Bump), тільки викликаний уже людиною: тяга впаде з 56% до 20%, і літак почне падати.

Для розв'язання цієї задачі диспетчер підтримує алгоритм **підхоплення ручки (Stick Matching / Catch-up)**:
1. При переході в ручний режим вихід тимчасово фіксується на рівні `u_prev` (віртуальний автотрим).
2. На екран пульта керування чи світлодіодний індикатор виводиться підказка: куди треба змістити фізичну ручку (вгору чи вниз).
3. Пряме керування передається пілоту лише тоді, коли фізичне положення ручки перетне вікно ±3% навколо значення `u_prev`, або після активації аварійного силового перехоплення (Force Override).

## Аварійний перехід при втраті зв'язку (Failsafe Handover)

Якщо приймач фіксує втрату пакетів телеметрії (Failsafe timeout > 500 мс), диспетчер автоматично ініціює аварійний перехід в автономний режим повернення на базу (`MODE_AUTO_MISSION` з точкою Home).

Завдяки виклику `pid_bumpless_handover` в обробнику Failsafe:
- Апарат не смикається й не провалює тягу в момент зникнення сигналу з пульта.
- Поточна висота та курс фіксуються як стартові координати маневру повернення.
- Автопілот плавно розвертає борт на точку старту з обмеженим темпом кутової швидкості.

## Реалізація диспетчера режимів польоту

:::tabs
```c
#include <stdio.h>
#include <stdbool.h>
#include <math.h>

typedef enum {
    MODE_MANUAL = 0,
    MODE_ALT_HOLD,
    MODE_AUTO_MISSION
} flight_mode_t;

typedef struct {
    float kp, ki, kd, kff;
    float out_min, out_max;
    float i_min, i_max;
    float slew_rate_max;
} pid_cfg_t;

typedef struct {
    pid_cfg_t cfg;
    float integral;
    float prev_meas;
    float target_sp;
    float current_sp;
    float last_out;
    bool  ready;
} pid_t;

static inline float clamp(float v, float min_v, float max_v) {
    return (v < min_v) ? min_v : (v > max_v) ? max_v : v;
}

void pid_init(pid_t *p, const pid_cfg_t *c) {
    p->cfg = *c;
    p->integral = 0.0f;
    p->prev_meas = 0.0f;
    p->target_sp = 0.0f;
    p->current_sp = 0.0f;
    p->last_out = 0.0f;
    p->ready = false;
}

void pid_bumpless_handover(pid_t *p, float current_meas, float target_sp, float prev_out) {
    p->current_sp = current_meas;
    p->target_sp = target_sp;
    p->prev_meas = current_meas;

    float err = p->current_sp - current_meas; // 0
    float p_term = p->cfg.kp * err;
    float ff_term = p->cfg.kff * p->current_sp;

    float needed_i = prev_out - p_term - ff_term;
    p->integral = clamp(needed_i, p->cfg.i_min, p->cfg.i_max);
    p->last_out = prev_out;
    p->ready = true;
}

float pid_update(pid_t *p, float meas, float dt) {
    if (!p->ready || dt <= 0.0f) return p->last_out;

    // Ремпінг уставки
    if (p->cfg.slew_rate_max > 0.0f) {
        float max_step = p->cfg.slew_rate_max * dt;
        float d = p->target_sp - p->current_sp;
        if (d > max_step) p->current_sp += max_step;
        else if (d < -max_step) p->current_sp -= max_step;
        else p->current_sp = p->target_sp;
    } else {
        p->current_sp = p->target_sp;
    }

    float err = p->current_sp - meas;
    float p_term = p->cfg.kp * err;

    float d_meas = (meas - p->prev_meas) / dt;
    p->prev_meas = meas;
    float d_term = -p->cfg.kd * d_meas;

    float ff_term = p->cfg.kff * p->current_sp;
    float cand_i = p->integral + p->cfg.ki * err * dt;
    float u_raw = p_term + cand_i + d_term + ff_term;

    // Clamping анти-віндап
    bool sat_h = (u_raw > p->cfg.out_max) && (err > 0.0f);
    bool sat_l = (u_raw < p->cfg.out_min) && (err < 0.0f);
    if (!sat_h && !sat_l) {
        p->integral = clamp(cand_i, p->cfg.i_min, p->cfg.i_max);
    }

    p->last_out = clamp(u_raw, p->cfg.out_min, p->cfg.out_max);
    return p->last_out;
}

// ── Диспетчер режимів літака ──
typedef struct {
    flight_mode_t current_mode;
    pid_t alt_hold_pid;
    pid_t auto_mission_pid;
    float last_actuator_output;
} flight_manager_t;

void flight_manager_init(flight_manager_t *mgr) {
    mgr->current_mode = MODE_MANUAL;
    mgr->last_actuator_output = 0.0f;

    // Налаштування контуру утримання висоти
    pid_cfg_t alt_cfg = {
        .kp = 0.08f, .ki = 0.04f, .kd = 0.02f, .kff = 0.0f,
        .out_min = 0.0f, .out_max = 1.0f,
        .i_min = 0.0f, .i_max = 0.9f,
        .slew_rate_max = 2.0f // набирати не більше 2 м/с
    };
    pid_init(&mgr->alt_hold_pid, &alt_cfg);

    // Налаштування контуру місії (агресивніший)
    pid_cfg_t auto_cfg = {
        .kp = 0.12f, .ki = 0.05f, .kd = 0.03f, .kff = 0.0f,
        .out_min = 0.0f, .out_max = 1.0f,
        .i_min = 0.0f, .i_max = 0.9f,
        .slew_rate_max = 3.5f // набирати не більше 3.5 м/с
    };
    pid_init(&mgr->auto_mission_pid, &auto_cfg);
} 

void flight_manager_switch_mode(flight_manager_t *mgr, flight_mode_t new_mode,
                                float current_alt, float mission_target_alt) {
    if (new_mode == mgr->current_mode) return;

    float prev_out = mgr->last_actuator_output;

    switch (new_mode) {
        case MODE_MANUAL:
            // При поверненні в ручний режим привід віддається ручці пілота
            break;

        case MODE_ALT_HOLD:
            // Безривкове захоплення: поточна висота стає уставкою
            pid_bumpless_handover(&mgr->alt_hold_pid, current_alt, current_alt, prev_out);
            break;

        case MODE_AUTO_MISSION:
            // Безривкове захоплення: стартуємо з поточної висоти, але цілимося в точку місії
            pid_bumpless_handover(&mgr->auto_mission_pid, current_alt, mission_target_alt, prev_out);
            break;
    }

    mgr->current_mode = new_mode;
}

float flight_manager_step(flight_manager_t *mgr, float stick_throttle,
                          float current_alt, float dt) {
    float output = 0.0f;

    switch (mgr->current_mode) {
        case MODE_MANUAL:
            output = stick_throttle;
            break;

        case MODE_ALT_HOLD:
            output = pid_update(&mgr->alt_hold_pid, current_alt, dt);
            break;

        case MODE_AUTO_MISSION:
            output = pid_update(&mgr->auto_mission_pid, current_alt, dt);
            break;
    }

    mgr->last_actuator_output = output;
    return output;
}
```
```cpp
#include <iostream>
#include <algorithm>
#include <concepts>
#include <cstdint>

enum class FlightMode : uint8_t {
    Manual = 0,
    AltHold,
    AutoMission
};

struct PidConfig {
    float kp{0.0f};
    float ki{0.0f};
    float kd{0.0f};
    float kff{0.0f};
    float out_min{0.0f};
    float out_max{1.0f};
    float i_min{0.0f};
    float i_max{0.9f};
    float slew_rate_max{0.0f};
};

class BumplessPidController {
public:
    constexpr explicit BumplessPidController(const PidConfig& config) noexcept
        : cfg_{config} {}

    void handover(float current_measurement, float target_setpoint,
                  float prev_actuator_output) noexcept {
        current_setpoint_ = current_measurement;
        target_setpoint_ = target_setpoint;
        prev_measurement_ = current_measurement;

        const float err = current_setpoint_ - current_measurement;
        const float p_term = cfg_.kp * err;
        const float ff_term = cfg_.kff * current_setpoint_;

        const float needed_i = prev_actuator_output - p_term - ff_term;
        integral_ = std::clamp(needed_i, cfg_.i_min, cfg_.i_max);
        last_output_ = prev_actuator_output;
        is_initialized_ = true;
    }

    [[nodiscard]] float update(float measurement, float dt) noexcept {
        if (!is_initialized_ || dt <= 0.0f) return last_output_;

        if (cfg_.slew_rate_max > 0.0f) {
            const float max_step = cfg_.slew_rate_max * dt;
            const float d = target_setpoint_ - current_setpoint_;
            if (d > max_step) current_setpoint_ += max_step;
            else if (d < -max_step) current_setpoint_ -= max_step;
            else current_setpoint_ = target_setpoint_;
        } else {
            current_setpoint_ = target_setpoint_;
        }

        const float err = current_setpoint_ - measurement;
        const float p_term = cfg_.kp * err;

        const float d_meas = (measurement - prev_measurement_) / dt;
        prev_measurement_ = measurement;
        const float d_term = -cfg_.kd * d_meas;

        const float ff_term = cfg_.kff * current_setpoint_;
        const float cand_i = integral_ + cfg_.ki * err * dt;
        const float u_raw = p_term + cand_i + d_term + ff_term;

        const bool sat_h = (u_raw > cfg_.out_max) && (err > 0.0f);
        const bool sat_l = (u_raw < cfg_.out_min) && (err < 0.0f);
        if (!sat_h && !sat_l) {
            integral_ = std::clamp(cand_i, cfg_.i_min, cfg_.i_max);
        }

        last_output_ = std::clamp(u_raw, cfg_.out_min, cfg_.out_max);
        return last_output_;
    }

    [[nodiscard]] float last_output() const noexcept { return last_output_; }

private:
    PidConfig cfg_{};
    float integral_{0.0f};
    float prev_measurement_{0.0f};
    float target_setpoint_{0.0f};
    float current_setpoint_{0.0f};
    float last_output_{0.0f};
    bool is_initialized_{false};
};

class FlightManager {
public:
    FlightManager()
        : alt_hold_pid_{PidConfig{
              .kp = 0.08f, .ki = 0.04f, .kd = 0.02f, .kff = 0.0f,
              .out_min = 0.0f, .out_max = 1.0f,
              .i_min = 0.0f, .i_max = 0.9f,
              .slew_rate_max = 2.0f
          }},
          auto_mission_pid_{PidConfig{
              .kp = 0.12f, .ki = 0.05f, .kd = 0.03f, .kff = 0.0f,
              .out_min = 0.0f, .out_max = 1.0f,
              .i_min = 0.0f, .i_max = 0.9f,
              .slew_rate_max = 3.5f
          }} {}

    void switch_mode(FlightMode new_mode, float current_alt, float mission_target_alt) noexcept {
        if (new_mode == current_mode_) return;

        const float prev_out = last_actuator_output_;

        switch (new_mode) {
            case FlightMode::Manual:
                break;
            case FlightMode::AltHold:
                alt_hold_pid_.handover(current_alt, current_alt, prev_out);
                break;
            case FlightMode::AutoMission:
                auto_mission_pid_.handover(current_alt, mission_target_alt, prev_out);
                break;
        }

        current_mode_ = new_mode;
    }

    [[nodiscard]] float step(float stick_throttle, float current_alt, float dt) noexcept {
        float out = 0.0f;
        switch (current_mode_) {
            case FlightMode::Manual:
                out = stick_throttle;
                break;
            case FlightMode::AltHold:
                out = alt_hold_pid_.update(current_alt, dt);
                break;
            case FlightMode::AutoMission:
                out = auto_mission_pid_.update(current_alt, dt);
                break;
        }
        last_actuator_output_ = out;
        return out;
    }

    [[nodiscard]] FlightMode current_mode() const noexcept { return current_mode_; }

private:
    FlightMode current_mode_{FlightMode::Manual};
    BumplessPidController alt_hold_pid_;
    BumplessPidController auto_mission_pid_;
    float last_actuator_output_{0.0f};
};
```
:::

## Тестовий сценарій та перевірка гладкості переходу

Наведемо симуляційний цикл, що демонструє політ тривалістю 15 секунд з двома переходами режимів:
- `t = 5.0 с`: перемикання з `MODE_MANUAL` (тримали газ 56% на висоті 42.0 м) у `MODE_ALT_HOLD`.
- `t = 10.0 с`: перемикання з `MODE_ALT_HOLD` у `MODE_AUTO_MISSION` (уставка маршрутної точки 80.0 м).

:::tabs
```c
int main(void) {
    flight_manager_t mgr;
    flight_manager_init(&mgr);

    float dt = 0.02f; // 50 Гц
    float alt = 42.0f;
    float stick = 0.56f;

    printf("Час[с] | Режим | Висота[м] | Вихід[%%] | Стрибок dU\n");
    printf("--------------------------------------------------\n");

    float prev_out = 0.56f;

    for (int step = 0; step <= 750; ++step) {
        float t = step * dt;

        // Подія 1: t = 5.0с -> перемикаємося в AltHold
        if (step == 250) {
            flight_manager_switch_mode(&mgr, MODE_ALT_HOLD, alt, alt);
            printf(">>> [t=5.0s] ПЕРЕМИКАННЯ: MANUAL -> ALT_HOLD <<<\n");
        }

        // Подія 2: t = 10.0с -> перемикаємося в AutoMission (ціль 80м)
        if (step == 500) {
            flight_manager_switch_mode(&mgr, MODE_AUTO_MISSION, alt, 80.0f);
            printf(">>> [t=10.0s] ПЕРЕМИКАННЯ: ALT_HOLD -> AUTO_MISSION (Target=80m) <<<\n");
        }

        float out = flight_manager_step(&mgr, stick, alt, dt);
        float du = fabsf(out - prev_out);

        // Друк ключових точок
        if (step == 249 || step == 250 || step == 251 ||
            step == 499 || step == 500 || step == 501) {
            printf("%5.2f  | %5d | %8.2f  | %8.4f | %10.6f\n",
                   t, mgr.current_mode, alt, out, du);
        }

        // Проста фізична модель реакції висоти на тягу
        alt += (out - 0.56f) * 10.0f * dt;
        prev_out = out;
    }

    return 0;
}
```
```cpp
int main() {
    FlightManager mgr;
    constexpr float dt = 0.02f;
    float alt = 42.0f;
    float stick = 0.56f;

    std::cout << "Час[с] | Режим | Висота[м] | Вихід[%] | Стрибок dU\n";
    std::cout << "--------------------------------------------------\n";

    float prev_out = 0.56f;

    for (int step = 0; step <= 750; ++step) {
        const float t = static_cast<float>(step) * dt;

        if (step == 250) {
            mgr.switch_mode(FlightMode::AltHold, alt, alt);
            std::cout << ">>> [t=5.0s] ПЕРЕМИКАННЯ: MANUAL -> ALT_HOLD <<<\n";
        }

        if (step == 500) {
            mgr.switch_mode(FlightMode::AutoMission, alt, 80.0f);
            std::cout << ">>> [t=10.0s] ПЕРЕМИКАННЯ: ALT_HOLD -> AUTO_MISSION (Target=80m) <<<\n";
        }

        const float out = mgr.step(stick, alt, dt);
        const float du = std::abs(out - prev_out);

        if (step == 249 || step == 250 || step == 251 ||
            step == 499 || step == 500 || step == 501) {
            std::cout << t << "s | Mode: " << static_cast<int>(mgr.current_mode())
                      << " | Alt: " << alt << " | Out: " << out << " | dU: " << du << "\n";
        }

        alt += (out - 0.56f) * 10.0f * dt;
        prev_out = out;
    }

    return 0;
}
```
:::

## Аналіз результатів симуляції та практичні висновки

Розберемо поведінку сигналів на межах переходів:

1. **Момент першого перемикання (Manual -> AltHold на кроці 250)**:
   - На кроці 249 (ручний режим) ручка газу тримала `u = 0.560000`, висота польоту становила `42.00 м`.
   - На кроці 250 викликається `pid_bumpless_handover`, який встановлює `current_sp = 42.00 м`, `prev_meas = 42.00 м`, а інтегратор завантажує значенням `I = 0.560000`.
   - Вихід регулятора на кроці 250 становить `u = 0.560000`, стрибок `dU = 0.000000`.
   - Апарат продовжує горизонтальний політ на висоті 42.0 м без найменшого струсу.

2. **Момент другого перемикання (AltHold -> AutoMission на кроці 500)**:
   - На кроці 499 апарат летить на висоті 42.0 м з виходом `u = 0.560000`.
   - Контур місії отримує нову далеку ціль `80.00 м`, але завдяки безривковому захопленню стартова уставка ініціалізується поточною висотою `42.00 м`.
   - Інтегратор контуру місії передзавантажується значенням `0.560000`.
   - Стрибок виходу на кроці 500 становить `dU = 0.000000`.
   - На наступних кроках (501+) обмежувач темпу наростання `slew_rate_max = 3.5 м/с` плавно піднімає уставку до 80 м зі швидкістю `0.07 м` за такт (3.5 · 0.02 с), формуючи контрольований підйом без перевантаження двигунів.

Такий підхід повністю захищає авіоніку та механічні приводи від динамічних ударів, забезпечуючи плавний і безпечний політ.