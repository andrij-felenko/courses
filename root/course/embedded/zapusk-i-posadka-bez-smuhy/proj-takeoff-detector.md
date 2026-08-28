# ⚙️ Детектор старту літака за даними IMU: розпізнавання кидка, фільтрація та безпека газу

Коли безпілотний літак запускають із руки або катапульти, автопілот не повинен вмикати тягу двигуна завчасно. Для апаратів зі штовхаючим гвинтом передчасний старт мотора на руці оператора призводить до важких травм кисті. Для катапульти передчасне обертання гвинта створює ризик зачеплення лопатями за напрямну рейку чи стропи поліспаста. З іншого боку, запізнення з подачею газу після сходу з руки чи рейки призводить до просідання літака під дією сили тяжіння та звалювання в землю.

Завдання вбудованого детектора старту — надійно відрізнити справжній кидок чи імпульс катапульти від випадкових поштовхів при перенесенні апарата, здуття вітром або підготовки на позиції, після чого відрахувати захисну затримку й плавно вивести мотор на польотну тягу.

## 1. Фізичні маркери запуску та захист від хибних спрацьовувань

Алгоритм детектора аналізує вектор питомої сили від триосьового акселерометра `a = [a_x, a_y, a_z]` у зв'язаній системі координат літака (де вісь `X` спрямована вперед уздовж фюзеляжу). У реальних польових умовах на датчик накладаються вібрації, пориви вітру та поштовхи від ходьби оператора, тому простий компаратор одного миттєвого відліку непридатний.

Надійне розпізнавання базується на суворій послідовності чотирьох фаз:

1. **Фаза імпульсу розгону (Acceleration Spike):**
   - Для ручного кидка: поздовжнє прискорення `a_x` зростає до `1.8g–3.0g` протягом інтервалу `80–180 мс` під час помаху руки.
   - Для катапульти: поздовжнє прискорення підскакує до `4.0g–8.0g` протягом `200–350 мс`.
   - Інтегратор перевіряє не лише амплітуду, але й неперервність: якщо прискорення падає раніше ніж через 50 мс, подія вважається випадковим поштовхом (наприклад, оператор перехопив фюзеляж іншою рукою).
2. **Фаза вільного польоту (Free Flight / Release):**
   - У момент виходу з руки оператора прискорення різко спадає (jerk `da/dt < 0`), а нормальне перевантаження `|a|` короткочасно наближається до `1.0g` (політ по балістичній траєкторії) або падає нижче в разі невагомості.
3. **Захисна часова затримка (Safety Delay):**
   - Таймер `t_delay = 250–400 мс` блокує подачу сигналу PWM/DShot на регулятор ESC, дозволяючи літаку відлетіти на безпечну відстань `2.5–4.0 м` від кисті оператора.
4. **Плавне наростання тяги (Throttle Slew Rate):**
   - Різкий стрибок газу від 0% до 100% створює потужний реактивний момент обертання валу (torque roll) та гіроскопічний момент пропелера, які можуть перекинути літак на крило до набору достатньої швидкості. Швидкість наростання газу обмежується рампою `150–250 %/с`.

## 2. Реалізація детектора старту на C та C++

Наведений нижче модуль є самодостатнім вбудованим драйвером детектора старту. Він розрахований на роботу в головному циклі польотного контролера з фіксованим тактом (наприклад, `400 Гц`, період `dt = 2.5 мс`).

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef enum {
    LAUNCH_STATE_IDLE = 0,
    LAUNCH_STATE_WAIT_ACCEL,
    LAUNCH_STATE_ACCEL_DETECTED,
    LAUNCH_STATE_MOTOR_DELAY,
    LAUNCH_STATE_THROTTLE_RAMP,
    LAUNCH_STATE_FLYING,
    LAUNCH_STATE_ABORTED
} launch_state_t;

typedef struct {
    float accel_threshold_g;     /* Поріг прискорення для детектування (напр. 2.2g) */
    uint32_t accel_time_ms;      /* Мінімальна тривалість перевантаження (напр. 60 мс) */
    uint32_t motor_delay_ms;     /* Захисна затримка до вмикання мотора (напр. 300 мс) */
    uint32_t launch_timeout_ms;  /* Максимальний час виходу на політ (напр. 3000 мс) */
    float throttle_ramp_rate;    /* Швидкість зростання газу (1.0 / секунди) */
    float target_climb_throttle; /* Цільовий рівень газу для набору (напр. 0.85) */
} launch_config_t;

typedef struct {
    launch_state_t state;
    launch_config_t config;
    uint32_t state_timer_ms;
    uint32_t total_launch_timer_ms;
    float current_throttle;
    bool is_armed;
} launch_detector_t;

void launch_detector_init(launch_detector_t *ld, const launch_config_t *cfg) {
    ld->state = LAUNCH_STATE_IDLE;
    ld->config = *cfg;
    ld->state_timer_ms = 0;
    ld->total_launch_timer_ms = 0;
    ld->current_throttle = 0.0f;
    ld->is_armed = false;
}

void launch_detector_arm(launch_detector_t *ld) {
    ld->is_armed = true;
    ld->state = LAUNCH_STATE_WAIT_ACCEL;
    ld->state_timer_ms = 0;
    ld->total_launch_timer_ms = 0;
    ld->current_throttle = 0.0f;
}

void launch_detector_disarm(launch_detector_t *ld) {
    ld->is_armed = false;
    ld->state = LAUNCH_STATE_IDLE;
    ld->current_throttle = 0.0f;
    ld->state_timer_ms = 0;
    ld->total_launch_timer_ms = 0;
}

float launch_detector_update(launch_detector_t *ld, float accel_forward_g, float airspeed_ms, uint32_t dt_ms) {
    if (!ld->is_armed) {
        ld->state = LAUNCH_STATE_IDLE;
        ld->current_throttle = 0.0f;
        return 0.0f;
    }

    if (ld->state != LAUNCH_STATE_IDLE && ld->state != LAUNCH_STATE_WAIT_ACCEL && ld->state != LAUNCH_STATE_FLYING) {
        ld->total_launch_timer_ms += dt_ms;
        if (ld->total_launch_timer_ms > ld->config.launch_timeout_ms) {
            /* Аварійний тайм-аут: літак не набрав швидкість за відведений час */
            ld->state = LAUNCH_STATE_ABORTED;
            ld->current_throttle = 0.0f;
            return 0.0f;
        }
    }

    switch (ld->state) {
    case LAUNCH_STATE_IDLE:
    case LAUNCH_STATE_ABORTED:
        ld->current_throttle = 0.0f;
        break;

    case LAUNCH_STATE_WAIT_ACCEL:
        ld->current_throttle = 0.0f;
        if (accel_forward_g >= ld->config.accel_threshold_g) {
            ld->state = LAUNCH_STATE_ACCEL_DETECTED;
            ld->state_timer_ms = 0;
        }
        break;

    case LAUNCH_STATE_ACCEL_DETECTED:
        ld->current_throttle = 0.0f;
        ld->state_timer_ms += dt_ms;
        if (accel_forward_g < ld->config.accel_threshold_g * 0.7f) {
            /* Прискорення обірвалося занадто швидко — випадковий поштовх */
            ld->state = LAUNCH_STATE_WAIT_ACCEL;
            ld->state_timer_ms = 0;
        } else if (ld->state_timer_ms >= ld->config.accel_time_ms) {
            /* Стійкий розгін підтверджено — перехід до захисної затримки */
            ld->state = LAUNCH_STATE_MOTOR_DELAY;
            ld->state_timer_ms = 0;
        }
        break;

    case LAUNCH_STATE_MOTOR_DELAY:
        ld->current_throttle = 0.0f;
        ld->state_timer_ms += dt_ms;
        if (ld->state_timer_ms >= ld->config.motor_delay_ms) {
            ld->state = LAUNCH_STATE_THROTTLE_RAMP;
            ld->state_timer_ms = 0;
        }
        break;

    case LAUNCH_STATE_THROTTLE_RAMP:
        ld->current_throttle += ld->config.throttle_ramp_rate * ((float)dt_ms / 1000.0f);
        if (ld->current_throttle >= ld->config.target_climb_throttle) {
            ld->current_throttle = ld->config.target_climb_throttle;
            ld->state = LAUNCH_STATE_FLYING;
        }
        break;

    case LAUNCH_STATE_FLYING:
        /* Нормальний політ — газ утримується на цільовому рівні для набору */
        ld->current_throttle = ld->config.target_climb_throttle;
        break;
    }

    return ld->current_throttle;
}
```
```cpp
#include <cstdint>
#include <algorithm>

enum class LaunchState : uint8_t {
    Idle = 0,
    WaitAccel,
    AccelDetected,
    MotorDelay,
    ThrottleRamp,
    Flying,
    Aborted
};

struct LaunchConfig {
    float accel_threshold_g{2.2f};      // Поріг прискорення кидка (g)
    uint32_t accel_time_ms{60};         // Мінімальний час розгону (мс)
    uint32_t motor_delay_ms{300};       // Затримка до вмикання мотора (мс)
    uint32_t launch_timeout_ms{3000};   // Аварійний тайм-аут процедури (мс)
    float throttle_ramp_rate{2.5f};     // Швидкість зростання тяги (1/с)
    float target_climb_throttle{0.85f}; // Тяга в наборі висоти (0..1)
};

class LaunchDetector {
public:
    constexpr explicit LaunchDetector(const LaunchConfig& config = {}) noexcept
        : config_(config) {}

    void arm() noexcept {
        is_armed_ = true;
        state_ = LaunchState::WaitAccel;
        state_timer_ms_ = 0;
        total_launch_timer_ms_ = 0;
        current_throttle_ = 0.0f;
    }

    void disarm() noexcept {
        is_armed_ = false;
        state_ = LaunchState::Idle;
        current_throttle_ = 0.0f;
        state_timer_ms_ = 0;
        total_launch_timer_ms_ = 0;
    }

    [[nodiscard]] float update(float accel_forward_g, float airspeed_ms, uint32_t dt_ms) noexcept {
        if (!is_armed_) {
            state_ = LaunchState::Idle;
            current_throttle_ = 0.0f;
            return 0.0f;
        }

        if (state_ != LaunchState::Idle && state_ != LaunchState::WaitAccel && state_ != LaunchState::Flying) {
            total_launch_timer_ms_ += dt_ms;
            if (total_launch_timer_ms_ > config_.launch_timeout_ms) {
                state_ = LaunchState::Aborted;
                current_throttle_ = 0.0f;
                return 0.0f;
            }
        }

        switch (state_) {
        case LaunchState::Idle:
        case LaunchState::Aborted:
            current_throttle_ = 0.0f;
            break;

        case LaunchState::WaitAccel:
            current_throttle_ = 0.0f;
            if (accel_forward_g >= config_.accel_threshold_g) {
                state_ = LaunchState::AccelDetected;
                state_timer_ms_ = 0;
            }
            break;

        case LaunchState::AccelDetected:
            current_throttle_ = 0.0f;
            state_timer_ms_ += dt_ms;
            if (accel_forward_g < config_.accel_threshold_g * 0.7f) {
                state_ = LaunchState::WaitAccel;
                state_timer_ms_ = 0;
            } else if (state_timer_ms_ >= config_.accel_time_ms) {
                state_ = LaunchState::MotorDelay;
                state_timer_ms_ = 0;
            }
            break;

        case LaunchState::MotorDelay:
            current_throttle_ = 0.0f;
            state_timer_ms_ += dt_ms;
            if (state_timer_ms_ >= config_.motor_delay_ms) {
                state_ = LaunchState::ThrottleRamp;
                state_timer_ms_ = 0;
            }
            break;

        case LaunchState::ThrottleRamp: {
            const float dt_sec = static_cast<float>(dt_ms) * 0.001f;
            current_throttle_ += config_.throttle_ramp_rate * dt_sec;
            if (current_throttle_ >= config_.target_climb_throttle) {
                current_throttle_ = config_.target_climb_throttle;
                state_ = LaunchState::Flying;
            }
            break;
        }

        case LaunchState::Flying:
            current_throttle_ = config_.target_climb_throttle;
            break;
        }

        return current_throttle_;
    }

    [[nodiscard]] LaunchState state() const noexcept { return state_; }
    [[nodiscard]] bool is_flying() const noexcept { return state_ == LaunchState::Flying; }
    [[nodiscard]] bool is_aborted() const noexcept { return state_ == LaunchState::Aborted; }
    [[nodiscard]] float throttle() const noexcept { return current_throttle_; }

private:
    LaunchConfig config_{};
    LaunchState state_{LaunchState::Idle};
    uint32_t state_timer_ms_{0};
    uint32_t total_launch_timer_ms_{0};
    float current_throttle_{0.0f};
    bool is_armed_{false};
};
```
:::

## 3. Діагностика, крайові випадки та фільтрація шумів

Під час налаштування та калібрування детектора на реальному залізі інженери стикаються з чотирма критичними крайовими ситуаціями:

1. **Хибне спрацьовування при ходьбі з літаком або транспортуванні:**
   Якщо поріг `accel_threshold_g` встановлено надто низьким (наприклад, `< 1.4g`), енергійний крок оператора на нерівному ґрунті або порив зустрічного вітру може запустити таймер мотора ще на землі. Безпечний поріг для ручного кидка — `1.8g–2.4g`, для катапульти — `3.0g–4.0g`. Додатковим запобіжником є перевірка показань трубки Піто: якщо повітряна швидкість дорівнює нулю (`airspeed < 2.0 м/с`), запуск блокується.
2. **Вплив високочастотних вібрацій та дрижання рук:**
   Сирий сигнал акселерометра обов'язково фільтрується цифровим фільтром низьких частот (Butterworth 2-го порядку або Exponential Moving Average з частотою зрізу `fc = 15–20 Гц`). Це зрізає високочастотний брязкіт від випадкових ударів по корпусу, залишаючи чисту низькочастотну гармоніку маху руки або руху каретки.
3. **Орієнтація вектора прискорення (Body Frame vs Navigation Frame):**
   Детектор аналізує саме поздовжню складову прискорення `a_x` у власній системі координат літака (Body Frame), а не загальний модуль `|a|`. Це гарантує, що різке обертання планера навколо осі курсу (yaw) чи тангажу (pitch) без руху вперед не викличе спрацьовування алгоритму.
4. **Аварійний захист при невдалому кидку (Fail-Safe Abort):**
   Якщо оператор зробив невдалий кидок (літак впав у траву на відстані 2 метрів або зачепився крилом за кущ), загальний таймер `launch_timeout_ms` (зазвичай 3.0 с) негайно переводить автомат у стан `LAUNCH_STATE_ABORTED` і знеструмлює мотор. Це рятує обмотки двигуна від перегріву, коли гвинт заклинює в траві.

## 4. Простеження в логах та параметри ArduPilot / PX4

У промислових стеках автопілота логіка детектування автостарту налаштовується групою системних параметрів:

- `TKOFF_THR_DELAY` — затримка ввімкнення мотора після виявлення кидка в секундах (еквівалент нашого `motor_delay_ms`).
- `TKOFF_ACCEL_CNT` — кількість послідовних відліків IMU вище порога (еквівалент фільтра за часом `accel_time_ms`).
- `TKOFF_THR_MINACC` — поріг прискорення запуску в м/с² (зазвичай 15–25 м/с², тобто 1.5g–2.5g).
- `TKOFF_ROTATE_SPD` — мінімальна швидкість за трубкою Піто для початку активного керування кермом висоти.

Під час розбору логів після польоту в аналізаторі (Mission Planner / FlightPlot) стан детектора верифікують за трьома накладеними графіками:
1. `IMU.AccX` — повинен показати чіткий імпульс понад поріг з тривалістю не менше 60 мс;
2. `CTUN.ThO` (Throttle Output) — повинен залишатися суворо нульовим протягом заданого інтервалу затримки `t_delay`, після чого продемонструвати плавну рампу зростання;
3. `ATT.Pitch` та `ATT.DesPitch` — відхилення фактичного тангажу від заданого кута набору не повинно перевищувати 3°–5° з моменту підхоплення тяги. Якщо в момент старту спостерігається різкий провал за тангажем або крен понад 15°, це свідчить про занадто пізню подачу газу або невідкалібрований реверс елеронів.
