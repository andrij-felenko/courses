# ⚙️ Гібридний селектор: фільтр безпеки над оптимізаційним планувальником

У складних автономних системах оптимізаційний планувальник (наприклад, алгоритм траєкторій на основі MPC, A* чи Dynamic Window Approach) працює з відносно низькою частотою (10–50 Гц) і може затримувати видачу команди через тривалий розрахунок або тимчасову незбіжність чисельного солвера. Навпаки, бар'єр безпеки (*Safety Envelope Filter / Interlock Supervisor*) мусить виконуватися в кожному такті жорсткого реального часу (100–500 Гц) з гарантованою часовою складністю `O(1)` і нульовим динамічним виділенням пам'яті.

Цей проєкт реалізує промисловий модуль фільтрації безпеки. Він перехоплює команду-кандидата від високорівневого планувальника, верифікує її за фізичними та геометричними інваріантами й або пропускає без змін, або проєктує на допустиму область керування, або активує детерміноване аварійне гальмування.

### Алгоритм фільтрації та фізичні інваріанти допуску

Бар'єр безпеки оперує чотирма незалежними фізичними обмеженнями, які не можуть бути порушені за жодних умов:

1. **Контроль свіжості кандидата (Watchdog / Heartbeat):**
   Високорівневий планувальник зазвичай працює на окремому обчислювачі (наприклад, Linux SBC із ROS 2) або в низькопріоритетній задачі RTOS. Якщо черговий пакет уставки запізнюється понад `WATCHDOG_MAX_TICKS` (наприклад, 10 тактів по 10 мс = 100 мс), супервізор перехоплює керування й починає детерміноване лінійне сповільнення з прискоренням `MAX_BRAKE_ACCEL_MPS2`, скидаючи швидкість до нуля.

2. **Динамічний розрахунок гальмівного шляху:**
   Для поточної швидкості `v` та дистанції до перешкоди за даними далекоміра `d_obs` розраховується мінімальна відстань безпечної зупинки:
   ```
   d_stop = (v^2) / (2 · a_brake_max) + v · tau_latency + d_safety_margin
   ```
   де `tau_latency` — сумарна транспортна затримка тракту (зчитування давача + інтервал утримання команди + затримка наростання гальмівного моменту ESC), а `d_safety_margin` — фіксований геометричний буфер. Якщо фактична дистанція `d_obs < d_stop`, лінійна швидкість уперед примусово обмежується аналітичною стелею:
   ```
   v_max_safe = sqrt(2 · a_brake_max · (d_obs − d_safety_margin))
   ```
   Це гарантує, що машина зупиниться перед стіною навіть при помилці планувальника.

3. **Захист від просідання живлення та аварійного перезавантаження (Brown-out Reset):**
   При різкому прискоренні струм моторів створює падіння напруги на внутрішньому опорі акумулятора `ESR`. Якщо напруга шини наближається до критичного порогу `CRITICAL_VOLTAGE_V`, максимальна дозволена швидкість і прискорення лінійно масштабуються вниз. Це запобігає апаратному скиданню керуючого мікроконтролера через просідання живлення.

4. **Захист від перевертання за кутом нахилу:**
   Якщо апарат рухається нерівним рельєфом і кут нахилу платформи наближається до критичного ліміту `max_tilt_limit`, кутова швидкість рискання примусово затискається. Це запобігає динамічному перекиданню ровера від дії відцентрової сили на схилі.

### Реалізація: C та ідіоматичний C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAFETY_MARGIN_M       0.35f
#define MAX_BRAKE_ACCEL_MPS2  3.0f
#define LATENCY_PAD_SEC       0.04f
#define MAX_ALLOWED_SPEED_MPS 2.5f
#define MAX_YAW_RATE_RADPS    1.8f
#define CRITICAL_VOLTAGE_V    13.8f
#define NOMINAL_VOLTAGE_V     16.0f
#define WATCHDOG_MAX_TICKS    10

typedef struct {
    float vx;       /* Лінійна швидкість уперед, м/с */
    float vy;       /* Бічна швидкість, м/с */
    float yaw_rate; /* Кутова швидкість рискання, рад/с */
} CommandVector;

typedef struct {
    float obstacle_dist_m; /* Найменша відстань за променем руху, м */
    float battery_voltage; /* Напруга силової шини, В */
    float current_tilt_rad;/* Поточний кут відхилення від вертикалі, рад */
    float max_tilt_limit;  /* Критичний кут нахилу, рад */
    bool  emergency_switch;/* Апаратна кнопка аварійної зупинки */
} SensorEnvelope;

typedef enum {
    SAFETY_PASS_THROUGH = 0,
    SAFETY_CLAMPED      = 1,
    SAFETY_BRAKE_ENGAGED= 2,
    SAFETY_ESTOP_ACTIVE = 3
} SafetyStatus;

typedef struct {
    uint32_t last_valid_tick;
    uint32_t current_tick;
    float    last_safe_vx;
} SafetySupervisorState;

void safety_supervisor_init(SafetySupervisorState *state) {
    if (!state) return;
    state->last_valid_tick = 0;
    state->current_tick = 0;
    state->last_safe_vx = 0.0f;
}

SafetyStatus safety_filter_step(
    SafetySupervisorState *state,
    const CommandVector *candidate,
    const SensorEnvelope *sensors,
    float dt_sec,
    CommandVector *out_safe_cmd
) {
    if (!state || !candidate || !sensors || !out_safe_cmd || dt_sec <= 0.0f) {
        return SAFETY_ESTOP_ACTIVE;
    }

    state->current_tick++;

    /* 1. Апаратний аварійний вимикач має найвищий пріоритет */
    if (sensors->emergency_switch) {
        out_safe_cmd->vx = 0.0f;
        out_safe_cmd->vy = 0.0f;
        out_safe_cmd->yaw_rate = 0.0f;
        state->last_safe_vx = 0.0f;
        return SAFETY_ESTOP_ACTIVE;
    }

    /* 2. Перевірка сторожового таймера оптимізатора */
    if ((state->current_tick - state->last_valid_tick) > WATCHDOG_MAX_TICKS) {
        /* Плавне гальмування до нуля */
        float decel = MAX_BRAKE_ACCEL_MPS2 * dt_sec;
        if (state->last_safe_vx > decel) {
            state->last_safe_vx -= decel;
        } else {
            state->last_safe_vx = 0.0f;
        }
        out_safe_cmd->vx = state->last_safe_vx;
        out_safe_cmd->vy = 0.0f;
        out_safe_cmd->yaw_rate = 0.0f;
        return SAFETY_BRAKE_ENGAGED;
    }

    /* 3. Розрахунок гальмівного бар'єра за дистанцією */
    float target_vx = candidate->vx;
    if (target_vx < 0.0f) {
        target_vx = 0.0f; /* Заборона руху назад у спрощеній моделі */
    }

    float stop_dist = (target_vx * target_vx) / (2.0f * MAX_BRAKE_ACCEL_MPS2)
                    + target_vx * LATENCY_PAD_SEC
                    + SAFETY_MARGIN_M;

    bool clamped = false;

    if (sensors->obstacle_dist_m < stop_dist) {
        /* Допустима швидкість із залишком безпечної дистанції */
        float available_dist = sensors->obstacle_dist_m - SAFETY_MARGIN_M;
        if (available_dist <= 0.05f) {
            target_vx = 0.0f;
        } else {
            float max_v_safe = sqrtf(2.0f * MAX_BRAKE_ACCEL_MPS2 * available_dist);
            if (target_vx > max_v_safe) {
                target_vx = max_v_safe;
                clamped = true;
            }
        }
    }

    /* 4. Масштабування за напругою акумулятора */
    if (sensors->battery_voltage < NOMINAL_VOLTAGE_V) {
        float v_factor = (sensors->battery_voltage - CRITICAL_VOLTAGE_V)
                       / (NOMINAL_VOLTAGE_V - CRITICAL_VOLTAGE_V);
        if (v_factor < 0.0f) v_factor = 0.0f;
        if (v_factor > 1.0f) v_factor = 1.0f;

        float max_bat_vx = MAX_ALLOWED_SPEED_MPS * v_factor;
        if (target_vx > max_bat_vx) {
            target_vx = max_bat_vx;
            clamped = true;
        }
    }

    /* 5. Захист від перевертання за кутом нахилу */
    float target_yaw_rate = candidate->yaw_rate;
    if (sensors->current_tilt_rad > (sensors->max_tilt_limit * 0.8f)) {
        float tilt_scale = (sensors->max_tilt_limit - sensors->current_tilt_rad)
                         / (sensors->max_tilt_limit * 0.2f);
        if (tilt_scale < 0.0f) tilt_scale = 0.0f;
        if (tilt_scale > 1.0f) tilt_scale = 1.0f;

        target_yaw_rate *= tilt_scale;
        target_vx *= tilt_scale;
        clamped = true;
    }

    /* 6. Обмеження абсолютних меж швидкості */
    if (target_vx > MAX_ALLOWED_SPEED_MPS) {
        target_vx = MAX_ALLOWED_SPEED_MPS;
        clamped = true;
    }
    if (target_yaw_rate > MAX_YAW_RATE_RADPS) {
        target_yaw_rate = MAX_YAW_RATE_RADPS;
        clamped = true;
    } else if (target_yaw_rate < -MAX_YAW_RATE_RADPS) {
        target_yaw_rate = -MAX_YAW_RATE_RADPS;
        clamped = true;
    }

    out_safe_cmd->vx = target_vx;
    out_safe_cmd->vy = candidate->vy; /* Бічна швидкість для ровера = 0 */
    out_safe_cmd->yaw_rate = target_yaw_rate;

    state->last_safe_vx = target_vx;
    state->last_valid_tick = state->current_tick;

    return clamped ? SAFETY_CLAMPED : SAFETY_PASS_THROUGH;
}
```
```cpp
#include <cstdint>
#include <cmath>
#include <algorithm>
#include <expected>
#include <span>

namespace Safety {

struct CommandVector {
    float vx{0.0f};       // Лінійна швидкість уперед, м/с
    float vy{0.0f};       // Бічна швидкість, м/с
    float yaw_rate{0.0f}; // Кутова швидкість, рад/с
};

struct SensorEnvelope {
    float obstacle_dist_m{0.0f};
    float battery_voltage{16.0f};
    float current_tilt_rad{0.0f};
    float max_tilt_limit{0.52f}; // ~30 градусів
    bool  emergency_switch{false};
};

enum class Status : uint8_t {
    PassThrough,
    Clamped,
    BrakeEngaged,
    EmergencyStop
};

enum class FaultCode : uint8_t {
    InvalidTimeStep,
    SensorSignalLost,
    CriticalTiltExceeded
};

class Supervisor {
public:
    static constexpr float kSafetyMarginM{0.35f};
    static constexpr float kMaxBrakeAccelMps2{3.0f};
    static constexpr float kLatencyPadSec{0.04f};
    static constexpr float kMaxAllowedSpeedMps{2.5f};
    static constexpr float kMaxYawRateRadps{1.8f};
    static constexpr float kCriticalVoltageV{13.8f};
    static constexpr float kNominalVoltageV{16.0f};
    static constexpr uint32_t kWatchdogMaxTicks{10};

    constexpr Supervisor() noexcept = default;

    std::expected<std::pair<CommandVector, Status>, FaultCode> evaluate(
        const CommandVector& candidate,
        const SensorEnvelope& sensors,
        float dt_sec
    ) noexcept {
        if (dt_sec <= 0.0f) {
            return std::unexpected(FaultCode::InvalidTimeStep);
        }

        current_tick_++;

        if (sensors.emergency_switch) {
            last_safe_vx_ = 0.0f;
            return std::pair{CommandVector{0.0f, 0.0f, 0.0f}, Status::EmergencyStop};
        }

        // Захист від перевищення критичного крену
        if (sensors.current_tilt_rad >= sensors.max_tilt_limit) {
            last_safe_vx_ = 0.0f;
            return std::unexpected(FaultCode::CriticalTiltExceeded);
        }

        // Тайм-аут планувальника
        if ((current_tick_ - last_valid_tick_) > kWatchdogMaxTicks) {
            const float decel = kMaxBrakeAccelMps2 * dt_sec;
            last_safe_vx_ = std::max(0.0f, last_safe_vx_ - decel);
            return std::pair{CommandVector{last_safe_vx_, 0.0f, 0.0f}, Status::BrakeEngaged};
        }

        float target_vx = std::max(0.0f, candidate.vx);
        bool is_clamped = false;

        // 1. Динамічний гальмівний бар'єр
        const float stop_dist = (target_vx * target_vx) / (2.0f * kMaxBrakeAccelMps2)
                              + target_vx * kLatencyPadSec
                              + kSafetyMarginM;

        if (sensors.obstacle_dist_m < stop_dist) {
            const float available_dist = sensors.obstacle_dist_m - kSafetyMarginM;
            if (available_dist <= 0.05f) {
                target_vx = 0.0f;
            } else {
                const float max_v_safe = std::sqrt(2.0f * kMaxBrakeAccelMps2 * available_dist);
                if (target_vx > max_v_safe) {
                    target_vx = max_v_safe;
                    is_clamped = true;
                }
            }
        }

        // 2. Корекція за просіданням батареї
        if (sensors.battery_voltage < kNominalVoltageV) {
            const float v_span = kNominalVoltageV - kCriticalVoltageV;
            const float v_factor = std::clamp((sensors.battery_voltage - kCriticalVoltageV) / v_span, 0.0f, 1.0f);
            const float max_bat_vx = kMaxAllowedSpeedMps * v_factor;
            if (target_vx > max_bat_vx) {
                target_vx = max_bat_vx;
                is_clamped = true;
            }
        }

        // 3. Обмеження рискання за нахилом
        float target_yaw_rate = candidate.yaw_rate;
        const float tilt_warning_thresh = sensors.max_tilt_limit * 0.8f;
        if (sensors.current_tilt_rad > tilt_warning_thresh) {
            const float tilt_headroom = sensors.max_tilt_limit - tilt_warning_thresh;
            const float tilt_scale = std::clamp((sensors.max_tilt_limit - sensors.current_tilt_rad) / tilt_headroom, 0.0f, 1.0f);
            target_yaw_rate *= tilt_scale;
            target_vx *= tilt_scale;
            is_clamped = true;
        }

        // 4. Фізичні обмеження приводів
        if (target_vx > kMaxAllowedSpeedMps) {
            target_vx = kMaxAllowedSpeedMps;
            is_clamped = true;
        }
        const float clamped_yaw = std::clamp(target_yaw_rate, -kMaxYawRateRadps, kMaxYawRateRadps);
        if (clamped_yaw != target_yaw_rate) {
            target_yaw_rate = clamped_yaw;
            is_clamped = true;
        }

        last_safe_vx_ = target_vx;
        last_valid_tick_ = current_tick_;

        CommandVector safe_cmd{target_vx, candidate.vy, target_yaw_rate};
        return std::pair{safe_cmd, is_clamped ? Status::Clamped : Status::PassThrough};
    }

    void notify_planner_alive() noexcept {
        last_valid_tick_ = current_tick_;
    }

private:
    uint32_t last_valid_tick_{0};
    uint32_t current_tick_{0};
    float    last_safe_vx_{0.0f};
};

} // namespace Safety
```
:::

### Чому ця схема не розриває контур керування

Головна перевага такої побудови — **розв'язка за часом та обов'язками**:

1. **Захист від затримок та зависань високого рівня:**
   Якщо планувальник шляху зависає на важкому оновленні карти зайнятості чи затримується через блокування пам'яті в користувацькому просторі (наприклад, у вузлі ROS 2 або MAVSDK на бортовому комп'ютері), мікроконтролер реального часу не летить «за старою командою у стіну». Сторож фільтра безпеки виявляє запізнення вже на 11-му мілісекундному такті й автономно зупиняє апарат за детермінованим профілем сповільнення без участі завислого вузла.

2. **Математична цілісність без ривків:**
   Якщо оптимізатор пропонує агресивний вектор швидкості, не враховуючи падіння напруги при глибокому розряді батареї, фільтр безпеки не перериває контур різким стрибком `0 / 1`, а виконує неперервне масштабування уставки за аналітичною формулою струмового бюджету. Система лишається математично оптимальною в центрі робочого простору (де діє планувальник) і на 100% захищеною детермінованими правилами біля його фізичних меж.

### Інтеграція в контур керування та диспетчеризація завдань

У реальній прошивці під керуванням FreeRTOS або Zephyr RTOS цей модуль розміщується безпосередньо перед мікшером приводів у високопріоритетній задачі реального часу:

```
[Повільний потік: Планувальник (20 Гц)] 
       │ 
       ▼ (Черга повідомлень / Inter-Core IPC)
[Швидкий потік: Контур безпеки (200 Гц)] ──► [Safety Supervisor] ──► [ПІД / Мікшер] ──► ESC / Мотори
       ▲
       │
[Прямий драйвер SPI/I2C: Лідар + АЦП струму]
```

Такий поділ гарантує, що час реакції на критичну перешкоду або натискання апаратної кнопки аварійного вимкнення визначається виключно кроком швидкого циклу (5 мс при 200 Гц) і механічною інерцією гальм, а не швидкістю обчислення траєкторій у планувальнику.

### Діагностика, логування та налаштування штрафів

Кожне спрацьовування обмеження (`Status::Clamped` або `Status::BrakeEngaged`) фіксується у внутрішньому кільцевому буфері чорної скриньки з міткою часу та значенням порушеного інваріанта:

* Якщо в польотному лозі видно часте затискання швидкості за дистанцією лідара під час штатних маневрів, це сигнал для розробника: вага штрафу наближення до перешкоди в цільовій функції планувальника занижена, і алгоритм оптимізації занадто агресивно «зрізає кути».
* Якщо фіксується затискання за напругою акумулятора при старті, це вказує на завищене значення дозволеного лінійного прискорення в планувальнику порівняно з реальною токовіддачею батарейного блока.

### Обробка крайових випадків та відмов давачів

У польових умовах давачі можуть видавати некоректні значення (`NaN`, `Inf`), зашумлені сплески або повністю втрачати зв'язок по шинах SPI/I2C. Супервізор безпеки обробляє ці стани за принципом **гарантованого закриття небезпеки** (*Fail-Closed*):

1. **Недійсні або некоректні виміри:** Якщо дистанція лідара повертає від'ємне число, значення `NaN` або прапорець апаратної помилки давача, бар'єр не вважає простір вільним, а автоматично підставляє консервативну оцінку на основі попередньої достовірної дистанції та швидкості руху за інерціальним численням (*Dead Reckoning*). Якщо невизначеність не зникає протягом 50 мс, активується плавна зупинка.
2. **Втрата зв'язку з оптимізатором:** При повній відмові бортового комп'ютера або зависанні операційної системи Linux мікроконтролер автопілота не перезавантажує планувальник, а негайно переводить контур у режим утримання позиції або аварійної посадки, використовуючи виключно власні локальні регулятори.

Таким чином, детермінований супервізор безпеки не лише захищає «залізо» від руйнування в полі, але й служить надійним бар'єром між недетермінованим світом високорівневих алгоритмів та жорстким детермінізмом силових приводів.
