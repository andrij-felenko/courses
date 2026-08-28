# ⚙️ Бібліотека порогових предикатів з гістерезисом

Програмний компаратор із гістерезисом — це базовий будівельний блок систем керування реального часу. Його ключова архітектурна вимога — **строге розділення незмінного конфігураційного контракту та мутабельного стану пам'яті**.

У цьому проєктному модулі наведено повнофункціональну бібліотеку порогових предикатів для мікроконтролерних систем. Реалізація підтримує як роботу з сирими цілочисельними квантами [АЦП](root:hw-analog/adc) без залучення блоку плаваючої коми (FPU), так і розрахунки у фізичних одиницях (`float` / `double`).

## Архітектурний дизайн: розділення конфігурації та стану

У багатьох аматорських проєктах вбудованих систем припускаються грубої помилки проектування: зберігання внутрішнього стану компаратора всередині локальних статичних змінних (наприклад, `static bool s_state`). Такий підхід робить функцію нереентерабельною: її неможливо використати для двох незалежних каналів вимірювання (наприклад, для паралельного контролю двох нагрівальних зон одного верстата), а також створює прихований стан гонитви при виклику з різних потоків операційної системи або обробників апаратних переривань.

Професійна бібліотечна архітектура базується на строгому розділенні даних на дві незалежні структури:

1. **Конфігурація (`HysteresisConfig`)**: незмінні параметри меж перемикання (`low_threshold`, `high_threshold`). Ця структура може безпечно розміщуватися у флеш-пам'яті мікроконтролера (ROM / Flash) як константа або оновлюватися в RAM при зміні уставок оператором.
   - Обов'язковий інваріант конфігурації: `high_threshold > low_threshold`.
   - Розмір у пам'яті: для цілочисельної версії `sizeof(hysteresis_cfg_i32_t)` складає рівно 8 байтів (два поля по 32 біти).
2. **Мутабельний стан (`HysteresisState`)**: мінімальний набір змінних в оперативній пам'яті (RAM), що зберігає поточне бінарне рішення `current_state` та статус ініціалізації першого проходу `initialized`.
   - Розмір у пам'яті: `sizeof(hysteresis_state_i32_t)` становить лише 2 байти (два логічні прапорці `bool`).
3. **Чиста функція кроку (`Update / Step`)**: детерміновано обчислює новий стан на основі конфігурації, попереднього стану та свіжого виміряного відліку сенсора, не маючи жодних глобальних побічних ефектів (англ. *side effects*).

## Цілочисельна арифметика проти рухомої коми

На недорогих мікроконтролерах без апаратного співпроцесора обчислень із плаваючою комою (зокрема ядрах ARM Cortex-M0, Cortex-M0+, Cortex-M3 або базі RISC-V RV32I) будь-які математичні операції та порівняння над числами типу `float` виконуються через програмну емуляцію компілятора (бібліотечні виклики `__aeabi_fcmplt` / `__aeabi_fcmpgt`). Одне таке плаваюче порівняння може витрачати від 40 до 120 процесорних тактів і збільшувати розмір бінарного образу прошивки за рахунок затягування бібліотеки емуляції `libgcc`.

Цілочисельний предикат на основі `int32_t` або `int16_t` оперує безпосередньо сирими кодами [АЦП](root:hw-analog/adc). Асемблерний лістинг такого кроку складається всього з 3–5 базових машинних інструкцій (`LDR`, `CMP`, `IT`, `STR`), що виконуються за 3–4 такти процесора. Це гарантує жорстку часову детермінованість при виклику всередині швидких таймерних переривань частотою 10–50 кГц.

## Безпека в багатопотоковому середовищі (Thread-Safety та ISR)

Якщо стан компаратора оновлюється з переривання АЦП (ISR), а зчитується з фонової задачі RTOS, необхідно враховувати атомарність операцій:

- На 32-розрядних архітектурах читання та запис окремого байта прапорця `bool` або 32-розрядного числа `int32_t` є природно атомарними інструкціями на рівні шини пам'яті.
- Проте якщо виконується динамічна переконфігурація обох порогів (`low` та `high`) з потоку користувацького інтерфейсу, потік може бути перерваний обробником ISR якраз посередині оновлення двох полів. У цей мікросекундний момент інваріант `high > low` може бути тимчасово порушений.
- Тому при динамічній зміні меж у багатопотоковому середовищі функція переконфігурації повинна захищатися критичною секцією (відключенням переривань або м'ютексом).

## Реалізація бібліотеки на C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* ========================================================================= */
/* 1. Цілочисельний компаратор (для сирих кодів АЦП / фіксованої крапки)      */
/* ========================================================================= */

typedef struct {
    int32_t low_threshold;   /* Поріг вимкнення: перехід 1 -> 0 */
    int32_t high_threshold;  /* Поріг увімкнення: перехід 0 -> 1 */
} hysteresis_cfg_i32_t;

typedef struct {
    bool current_state;      /* Поточний логічний вихід (true = 1, false = 0) */
    bool initialized;        /* Чи було виконано ініціалізацію стартового стану */
} hysteresis_state_i32_t;

/**
 * @brief Ініціалізація меж за номінальною уставкою та симетричною мертвою зоною
 */
static inline bool hysteresis_cfg_init_symmetric_i32(hysteresis_cfg_i32_t *cfg,
                                                     int32_t setpoint,
                                                     int32_t deadband) {
    if (!cfg || deadband <= 0) {
        return false;
    }
    int32_t half = deadband / 2;
    cfg->low_threshold = setpoint - half;
    cfg->high_threshold = setpoint + (deadband - half);
    return true;
}

/**
 * @brief Крок оновлення стану цілочисельного компаратора
 */
static inline bool hysteresis_update_i32(const hysteresis_cfg_i32_t *cfg,
                                        hysteresis_state_i32_t *state,
                                        int32_t raw_sample) {
    if (!state->initialized) {
        /* Стратегія холодного старту: активний рівень 1 лише якщо значення строго
         * досягло або перевищило верхню межу. В усіх інших випадках — безпечний 0 */
        state->current_state = (raw_sample >= cfg->high_threshold);
        state->initialized = true;
        return state->current_state;
    }

    if (state->current_state) {
        /* Стан 1 (активний): перехід у 0 лише при спаді нижче low_threshold */
        if (raw_sample <= cfg->low_threshold) {
            state->current_state = false;
        }
    } else {
        /* Стан 0 (неактивний): перехід в 1 лише при підйомі вище high_threshold */
        if (raw_sample >= cfg->high_threshold) {
            state->current_state = true;
        }
    }

    return state->current_state;
}

/* ========================================================================= */
/* 2. Компаратор чисел із рухомою комою (float)                               */
/* ========================================================================= */

typedef struct {
    float low_threshold;
    float high_threshold;
} hysteresis_cfg_f32_t;

typedef struct {
    bool current_state;
    bool initialized;
} hysteresis_state_f32_t;

static inline bool hysteresis_cfg_init_symmetric_f32(hysteresis_cfg_f32_t *cfg,
                                                     float setpoint,
                                                     float deadband) {
    if (!cfg || deadband <= 0.0f) {
        return false;
    }
    float half = deadband * 0.5f;
    cfg->low_threshold = setpoint - half;
    cfg->high_threshold = setpoint + half;
    return true;
}

static inline bool hysteresis_update_f32(const hysteresis_cfg_f32_t *cfg,
                                        hysteresis_state_f32_t *state,
                                        float sample) {
    if (!state->initialized) {
        state->current_state = (sample >= cfg->high_threshold);
        state->initialized = true;
        return state->current_state;
    }

    if (state->current_state) {
        if (sample <= cfg->low_threshold) {
            state->current_state = false;
        }
    } else {
        if (sample >= cfg->high_threshold) {
            state->current_state = true;
        }
    }

    return state->current_state;
}
```
```cpp
#include <concepts>
#include <cstdint>
#include <type_traits>

namespace embedded::control {

/**
 * @brief Політика визначення стану при холодному старті всередині мертвої зони
 */
enum class StartupPolicy {
    ActiveOnlyAboveHigh,    // 1 лише при значенні >= high_threshold (безпечний дефолт)
    PassiveBelowLow,        // 0 лише при значенні <= low_threshold (агресивний старт)
    StrictlyInactive        // Завжди 0 на старті, доки не відбудеться перше перетинання
};

/**
 * @brief Узагальнений шаблонний клас порогового компаратора з гістерезисом
 */
template <typename T>
requires std::is_arithmetic_v<T>
class HysteresisComparator {
public:
    constexpr HysteresisComparator(T low_threshold, T high_threshold, 
                                   StartupPolicy policy = StartupPolicy::ActiveOnlyAboveHigh) noexcept
        : low_(low_threshold), high_(high_threshold), policy_(policy) {}

    /**
     * @brief Фабричний метод побудови симетричного компаратора: уставка ± (зона / 2)
     */
    static constexpr HysteresisComparator FromSetpoint(T setpoint, T deadband,
                                                       StartupPolicy policy = StartupPolicy::ActiveOnlyAboveHigh) noexcept {
        T half = deadband / static_cast<T>(2);
        return HysteresisComparator(setpoint - half, setpoint + (deadband - half), policy);
    }

    /**
     * @brief Обчислення нового стану за черговим відліком сигналу
     */
    [[nodiscard]] constexpr bool Update(T sample) noexcept {
        if (!initialized_) {
            switch (policy_) {
                case StartupPolicy::ActiveOnlyAboveHigh:
                    state_ = (sample >= high_);
                    break;
                case StartupPolicy::PassiveBelowLow:
                    state_ = (sample > low_);
                    break;
                case StartupPolicy::StrictlyInactive:
                    state_ = false;
                    break;
            }
            initialized_ = true;
            return state_;
        }

        if (state_) {
            if (sample <= low_) {
                state_ = false;
            }
        } else {
            if (sample >= high_) {
                state_ = true;
            }
        }

        return state_;
    }

    [[nodiscard]] constexpr bool State() const noexcept { return state_; }
    [[nodiscard]] constexpr bool IsInitialized() const noexcept { return initialized_; }
    
    constexpr void Reset() noexcept {
        state_ = false;
        initialized_ = false;
    }

    /**
     * @brief Безпечна зміна порогів на льоту без скидання поточного стану
     */
    constexpr void Reconfigure(T low_threshold, T high_threshold) noexcept {
        low_ = low_threshold;
        high_ = high_threshold;
    }

private:
    T low_{};
    T high_{};
    StartupPolicy policy_{StartupPolicy::ActiveOnlyAboveHigh};
    bool state_{false};
    bool initialized_{false};
};

} // namespace embedded::control
```
:::

## Інтеграція в таблиці переходів скінченних автоматів (FSM)

Розглянемо практичний приклад побудови контролера охолодження процесорного блоку. Скінченний автомат має три дискретні стани:

1. `COOLER_STATE_IDLE`: вентилятор вимкнено, температура в нормі;
2. `COOLER_STATE_COOLING`: вентилятор увімкнено, триває продувка радіатора;
3. `COOLER_STATE_ALARM`: аварійний перегрів (понад 85°C), навантаження примусово скидається.

Предикат гістерезису бере на себе всю низькорівневу фільтрацію теплового шуму, надаючи автомату вищого рівня чистий булевий сигнал запиту на охолодження (`fan_demand`), вільний від деренчання на межах.

:::tabs
```c
#include <stdio.h>

typedef enum {
    COOLER_STATE_IDLE,
    COOLER_STATE_COOLING,
    COOLER_STATE_ALARM
} cooler_state_t;

typedef struct {
    cooler_state_t state;
    hysteresis_cfg_f32_t fan_hysteresis;
    hysteresis_state_f32_t fan_state;
    float alarm_threshold_c;
} cooler_controller_t;

void cooler_controller_init(cooler_controller_t *ctrl) {
    ctrl->state = COOLER_STATE_IDLE;
    /* Вимкнення кулера при 45°C, увімкнення при 60°C (мертва зона 15°C) */
    ctrl->fan_hysteresis.low_threshold = 45.0f;
    ctrl->fan_hysteresis.high_threshold = 60.0f;
    ctrl->fan_state.current_state = false;
    ctrl->fan_state.initialized = false;
    ctrl->alarm_threshold_c = 85.0f;
}

void cooler_controller_step(cooler_controller_t *ctrl, float temp_c) {
    /* Крок 1: обчислення порогового предикату */
    bool fan_demand = hysteresis_update_f32(&ctrl->fan_hysteresis, &ctrl->fan_state, temp_c);

    /* Крок 2: диспетчеризація станів FSM */
    switch (ctrl->state) {
        case COOLER_STATE_IDLE:
            if (temp_c >= ctrl->alarm_threshold_c) {
                ctrl->state = COOLER_STATE_ALARM;
            } else if (fan_demand) {
                ctrl->state = COOLER_STATE_COOLING;
            }
            break;

        case COOLER_STATE_COOLING:
            if (temp_c >= ctrl->alarm_threshold_c) {
                ctrl->state = COOLER_STATE_ALARM;
            } else if (!fan_demand) {
                ctrl->state = COOLER_STATE_IDLE;
            }
            break;

        case COOLER_STATE_ALARM:
            /* Повернення з аварійного стану лише після повного охолодження */
            if (temp_c < ctrl->fan_hysteresis.low_threshold) {
                ctrl->state = COOLER_STATE_IDLE;
            }
            break;
    }
}
```
```cpp
#include <iostream>

namespace embedded::fsm {

enum class CoolerState {
    Idle,
    Cooling,
    Alarm
};

class CoolerSystem {
public:
    CoolerSystem()
        : fan_comparator_(45.0f, 60.0f), alarm_limit_(85.0f), state_(CoolerState::Idle) {}

    void Step(float current_temperature_c) noexcept {
        const bool fan_active = fan_comparator_.Update(current_temperature_c);

        switch (state_) {
            case CoolerState::Idle:
                if (current_temperature_c >= alarm_limit_) {
                    state_ = CoolerState::Alarm;
                } else if (fan_active) {
                    state_ = CoolerState::Cooling;
                }
                break;

            case CoolerState::Cooling:
                if (current_temperature_c >= alarm_limit_) {
                    state_ = CoolerState::Alarm;
                } else if (!fan_active) {
                    state_ = CoolerState::Idle;
                }
                break;

            case CoolerState::Alarm:
                if (current_temperature_c < 45.0f) {
                    state_ = CoolerState::Idle;
                }
                break;
        }
    }

    [[nodiscard]] CoolerState GetState() const noexcept { return state_; }
    [[nodiscard]] bool IsFanRunning() const noexcept { return fan_comparator_.State(); }

private:
    control::HysteresisComparator<float> fan_comparator_;
    float alarm_limit_{85.0f};
    CoolerState state_{CoolerState::Idle};
};

} // namespace embedded::fsm
```
:::

## Тестування та верифікація граничних умов

Щоб гарантувати повну відсутність регресій та брязкоту в серійному виробництві, модуль гістерезису покривають набором детермінованих модульних тестів (Unit Tests). Тестовий сценарій моделює типову зашумлену траєкторію фізичного процесу через критичні межі:

1. **Тест спокою в мертвій зоні (Deadband Invariance)**:  
   При подачі послідовності `50°C → 55°C → 52°C → 58°C` вихід зобов'язаний стабільно залишатися рівним `0`.
2. **Тест спрацьовування верхнього порога (Upper Transition)**:  
   Подача `60.0°C` або `60.1°C` перемикає вихід у стан `1`.
3. **Тест стійкості до шуму в активному стані (Active State Noise Immunity)**:  
   Коли після нагріву до 65°C температура спадає до `52°C` і починає зазнавати випадкових коливань `52°C → 48°C → 54°C → 46°C`, вихід зобов'язаний стабільно утримувати `1`, оскільки жоден відлік не опустився нижче `45.0°C`.
4. **Тест повернення через нижній поріг (Lower Transition)**:  
   Лише після того, як виміряний сигнал опуститься до `44.9°C` (строго нижче `45.0°C`), компаратор повертається у вимкнений стан `0`.
5. **Тест точності на межах (Exact Boundary Inclusivity)**:  
   Перевірка поведінки при точній рівності `sample == high_threshold` та `sample == low_threshold`, що гарантує відсутність невизначених станів у логіці операторів `>=` та `<=`.

Такий вичерпний тестовий контур повністю унеможливлює появу непередбачуваних перемикань силових ключів у реальному польовому обладнанні.
