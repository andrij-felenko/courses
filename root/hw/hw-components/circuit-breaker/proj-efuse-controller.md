# ⚙️ Програмне керування та алгоритм роботи інтелектуального електронного запобіжника

На відміну від нерегульованих механічних автоматів захисту, твердотілий електронний запобіжник (e-Fuse / Smart High-Side Switch) поєднує силовий MOSFET-ключ із цифровим або змішаним контролером керування. Це дозволяє динамічно змінювати струмові пороги під час роботи приладу, реалізовувати програмований плавний пуск (Soft-Start) для безіскрового заряду ємностей навантаження, вести точний облік виділеної енергії `I²t` і керувати стратегією повторних увімкнень (Auto-Retry проти Latch-Off) без фізичної заміни компонентів або перекомутації щита.

### Архітектура програмного автомата станів

Контролер e-Fuse працює як детермінований скінченний автомат станів (*Finite State Machine* — FSM) із п'ятьма режимами:

1. **`STATE_OFF` (Вимкнено):** Силовий затвор MOSFET розряджений на землю (`V_GS = 0`), вихід повністю відключений від шини живлення. Контролер очікує зовнішньої команди увімкнення `ENABLE` та безперервно перевіряє безпеку вхідної напруги за вікном компараторів недонапруги (UVLO — *Undervoltage Lockout*) та перенапруги (OVLO — *Overvoltage Lockout*). Якщо вхідна напруга виходить за допустимі межі (наприклад, падає нижче 4.5 В або перевищує 32 В для 24-вольтової шини), запуск блокується.
2. **`STATE_SOFT_START` (Плавний пуск):** Затвор відкривається з контрольованою швидкістю через внутрішній ЦАП або ШІМ-інтегратор (`dV_gate/dt = const`), плавно піднімаючи напругу на виході. Струм заряду вихідних конденсаторів обмежується на безпечному рівні:
   ```
   I_inrush = C_load · (dV_out / dt)
   ```
   Якщо на платі встановлено банк фільтруючих конденсаторів `C_load = 2200 мкФ`, а допустимий пусковий струм становить 2.2 А, контролер задає швидкість наростання напруги:
   ```
   dV_out / dt = I_inrush / C_load = 2.2 А / (2200 · 10⁻⁶ Ф) = 1000 В/с = 1 В/мс
   ```
   Для виходу на номінальні 24 В знадобиться рівно 24 мс. Якщо вихідна напруга не досягає 90% від вхідної за час максимального таймауту `T_startup_max` (наприклад, 50 мс), фіксується пускова аварія через надлишковий витік або коротке замикання навантаження.
3. **`STATE_ON` (Штатний робочий режим):** Силовий ключ повністю відкритий у зоні омічної провідності (`R_DS(on) = 2 ... 10 мОм`). Контролер виконує високошвидкісне опитування струму через SenseFET або шунт Кельвіна. Струм одночасно аналізується двома контурами:
   - Миттєвий апаратний компаратор КЗ: при перевищенні порогу жорсткого КЗ (`I > I_short_circuit`) затвор MOSFET розряджається на землю за субмікросекундний час (< 500 нс);
   - Програмний інтегратор `I²t`: при помірному перевантаженні (`I_nom < I < I_short_circuit`) обчислюється накопичене теплове навантаження `∑ (I² - I_nom²) · Δt`.
4. **`STATE_CURRENT_LIMIT` (Активне обмеження струму):** При помірному стрибку навантаження контролер переводить MOSFET у лінійний режим (зону насичення), динамічно утримуючи струм на фіксованій стелі `I_limit` протягом короткого інтервалу бланкування `t_blanking`.
5. **`STATE_FAULT` (Аварійне блокування / Охолодження):** Затвор заблоковано. Якщо активовано режим `AUTO_RETRY`, контролер запускає таймер охолодження кристала (500–2000 мс) перед новою спробою старту; у режимі `LATCH_OFF` вимикач лишається знеструмленим до явного скидання сигналу живлення або команди хост-процесора.

```
                  +─────────────+
                  |  STATE_OFF  | <───────────────────────────+
                  +─────────────+                             │
                         │                                    │
                  [Команда EN=1]                              │
                         ▼                                    │
               +──────────────────+                           │
               | STATE_SOFT_START | ──[Таймаут пуску]──+      │
               +──────────────────+                    │      │
                         │                             │      │
                 [V_out >= 0.9·V_in]                   │      │
                         ▼                             │      │
                  +─────────────+                      │      │
        +───────► |  STATE_ON   | ──[Струм КЗ]──+      │      │
        │         +─────────────+               │      │      │
        │                │                      │      │      │
        │          [Перевантаж.]                │      │      │
        │                ▼                      │      │      │
        │     +─────────────────────+           │      │      │
[Норма] │     | STATE_CURRENT_LIMIT | ──[I²t]───┤      │      │
        │     +─────────────────────+           │      │      │
        │                │                      │      │      │
        └────────────────┘                      ▼      ▼      │
                                         +─────────────+      │
                                         | STATE_FAULT | ─────+
                                         +─────────────+ [Auto-retry таймер
                                                          або скидання команди]
```

### Фізика захисту від виходу за межі області безпечної роботи (SOA)

Найкритичніший режим для силового MOSFET в e-Fuse — робота в лінійному контурі обмеження струму (Current Limit).

У повністю відкритому стані падіння напруги на транзисторі мізерне (`V_DS = I_D · R_DS(on) ≈ 5 А · 0.005 Ом = 25 мВ`), і потужність розсіювання становить лише `P = 0.125 Вт`. Але коли на виході виникає коротке замикання, а контролер обмежує струм на рівні 5 А при напрузі живлення 24 В, уся напруга джерела падає безпосередньо на кристалі транзистора:

```
P_MOSFET = V_DS · I_limit = 24 В × 5 А = 120 Вт!
```

Виділення потужності 120 Вт на крихітному кремнієвому кристалі площею 4 мм² викликає стрибок температури переходу `T_j` зі швидкістю понад 500 °C за мілісекунду. Це призводить до виникнення локальних гарячих точок (*hot spots*), термомеханічного розтріскування кремнію та вторинного пробою кристала.

Щоб запобігти тепловій загибелі ключа, алгоритм e-Fuse відстежує область безпечної роботи (SOA — *Safe Operating Area*): чим вища виміряна напруга `V_DS = V_in - V_out`, тим коротшим є допустимий час роботи в режимі струмообмеження до аварійного відсікання.

### Програмна реалізація контролера e-Fuse

Нижче наведено робочий код драйвера інтелектуального e-Fuse з вимірюванням напруг, апаратним відсіканням КЗ, програмним інтегратором `I²t`, розрахунком теплового стресу SOA та логікою охолодження.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

/* Стани скінченного автомата e-Fuse */
typedef enum {
    EFUSE_STATE_OFF = 0,
    EFUSE_STATE_SOFT_START,
    EFUSE_STATE_ON,
    EFUSE_STATE_CURRENT_LIMIT,
    EFUSE_STATE_FAULT
} efuse_state_t;

/* Причина виникнення аварії */
typedef enum {
    FAULT_NONE = 0,
    FAULT_SHORT_CIRCUIT,
    FAULT_THERMAL_I2T,
    FAULT_SOA_VIOLATION,
    FAULT_STARTUP_TIMEOUT,
    FAULT_UNDERVOLTAGE
} efuse_fault_t;

/* Конфігурація параметрів захисту */
typedef struct {
    float v_in_min_v;           /* Поріг UVLO (В) */
    float i_nominal_a;          /* Номінальний струм (А) */
    float i_short_circuit_a;    /* Поріг миттєвого відсікання КЗ (А) */
    float i2t_threshold_a2s;    /* Максимальний тепловий інтеграл (А²·с) */
    float max_linear_power_w;   /* Максимальна потужність у лінійному режимі (Вт) */
    float soft_start_step_v;    /* Крок наростання напруги затвора (В/тік) */
    uint32_t startup_timeout_ms;/* Максимальний час запуску (мс) */
    uint32_t cool_down_time_ms; /* Час паузи перед автоперезапуском (мс) */
    bool auto_retry_enabled;    /* Дозвіл автоматичного повторного старту */
} efuse_config_t;

/* Структура контексту драйвера */
typedef struct {
    efuse_state_t state;
    efuse_fault_t last_fault;
    efuse_config_t config;
    
    float v_gate_target_v;      /* Цільова напруга затвора */
    float v_gate_current_v;     /* Поточна напруга затвора */
    float accumulated_i2t;      /* Накопичений тепловий інтеграл (А²·с) */
    float linear_mode_energy_j; /* Енергія розсіювання в лінійному режимі (Дж) */
    
    uint32_t state_timer_ms;    /* Внутрішній таймер стану */
    uint32_t retry_count;       /* Лічильник спроб перезапуску */
} efuse_controller_t;

/* Апаратні виклики (HAL) */
extern void hal_set_gate_voltage(float voltage_v);
extern void hal_fast_gate_shutdown(void);
extern float hal_read_vin_voltage(void);
extern float hal_read_vout_voltage(void);
extern float hal_read_load_current(void);

/* Ініціалізація контролера */
void efuse_init(efuse_controller_t *dev, const efuse_config_t *cfg) {
    dev->state = EFUSE_STATE_OFF;
    dev->last_fault = FAULT_NONE;
    dev->config = *cfg;
    dev->v_gate_target_v = 10.0f; /* 10 В для повного відкриття N-MOSFET */
    dev->v_gate_current_v = 0.0f;
    dev->accumulated_i2t = 0.0f;
    dev->linear_mode_energy_j = 0.0f;
    dev->state_timer_ms = 0;
    dev->retry_count = 0;
    
    hal_fast_gate_shutdown();
}

/* Періодичний крок обробки (викликається кожні delta_ms, наприклад 1 мс) */
void efuse_process_tick(efuse_controller_t *dev, bool enable_cmd, uint32_t delta_ms) {
    float v_in = hal_read_vin_voltage();
    float v_out = hal_read_vout_voltage();
    float i_load = hal_read_load_current();
    float dt_sec = (float)delta_ms / 1000.0f;
    float v_ds = (v_in > v_out) ? (v_in - v_out) : 0.0f;

    /* Перевірка мінімальної напруги живлення (UVLO) */
    if (v_in < dev->config.v_in_min_v && dev->state != EFUSE_STATE_OFF) {
        hal_fast_gate_shutdown();
        dev->state = EFUSE_STATE_FAULT;
        dev->last_fault = FAULT_UNDERVOLTAGE;
        dev->state_timer_ms = 0;
        return;
    }

    switch (dev->state) {
    case EFUSE_STATE_OFF:
        if (enable_cmd && v_in >= dev->config.v_in_min_v) {
            dev->state = EFUSE_STATE_SOFT_START;
            dev->v_gate_current_v = 0.0f;
            dev->state_timer_ms = 0;
            dev->accumulated_i2t = 0.0f;
            dev->linear_mode_energy_j = 0.0f;
        }
        break;

    case EFUSE_STATE_SOFT_START:
        dev->state_timer_ms += delta_ms;

        /* Миттєве відсікання, якщо струм перевищив поріг КЗ */
        if (i_load >= dev->config.i_short_circuit_a) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SHORT_CIRCUIT;
            dev->state_timer_ms = 0;
            return;
        }

        /* Контроль теплового розсіювання на MOSFET під час заряду ємності */
        float power_now = v_ds * i_load;
        dev->linear_mode_energy_j += power_now * dt_sec;
        if (power_now > dev->config.max_linear_power_w && dev->linear_mode_energy_j > 2.0f) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SOA_VIOLATION;
            dev->state_timer_ms = 0;
            return;
        }

        /* Плавне наростання напруги на затворі */
        dev->v_gate_current_v += dev->config.soft_start_step_v;
        if (dev->v_gate_current_v > dev->v_gate_target_v) {
            dev->v_gate_current_v = dev->v_gate_target_v;
        }
        hal_set_gate_voltage(dev->v_gate_current_v);

        /* Перевірка успішного виходу на режим */
        if (v_out >= (v_in * 0.90f)) {
            dev->state = EFUSE_STATE_ON;
            dev->v_gate_current_v = dev->v_gate_target_v;
            hal_set_gate_voltage(dev->v_gate_current_v);
            dev->state_timer_ms = 0;
            dev->linear_mode_energy_j = 0.0f;
        } else if (dev->state_timer_ms > dev->config.startup_timeout_ms) {
            /* Таймаут пуску — занадто велика ємність або витік на виході */
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_STARTUP_TIMEOUT;
            dev->state_timer_ms = 0;
        }
        break;

    case EFUSE_STATE_ON:
        /* 1. Апаратне відсікання короткого замикання (< 500 нс) */
        if (i_load >= dev->config.i_short_circuit_a) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SHORT_CIRCUIT;
            dev->state_timer_ms = 0;
            return;
        }

        /* 2. Інтегрування теплового навантаження I²t */
        if (i_load > dev->config.i_nominal_a) {
            float excess_current = i_load - dev->config.i_nominal_a;
            dev->accumulated_i2t += (excess_current * excess_current) * dt_sec;

            if (dev->accumulated_i2t >= dev->config.i2t_threshold_a2s) {
                hal_fast_gate_shutdown();
                dev->state = EFUSE_STATE_FAULT;
                dev->last_fault = FAULT_THERMAL_I2T;
                dev->state_timer_ms = 0;
                return;
            }
        } else {
            /* Експоненційне охолодження при роботі нижче номіналу */
            dev->accumulated_i2t -= dev->accumulated_i2t * 0.1f * dt_sec;
            if (dev->accumulated_i2t < 0.0f) {
                dev->accumulated_i2t = 0.0f;
            }
        }

        if (!enable_cmd) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_OFF;
        }
        break;

    case EFUSE_STATE_CURRENT_LIMIT:
        /* Режим активного обмеження струму */
        dev->state_timer_ms += delta_ms;
        if (v_ds * i_load > dev->config.max_linear_power_w) {
            hal_fast_gate_shutdown();
            dev->state = EFUSE_STATE_FAULT;
            dev->last_fault = FAULT_SOA_VIOLATION;
            dev->state_timer_ms = 0;
        }
        break;

    case EFUSE_STATE_FAULT:
        dev->state_timer_ms += delta_ms;

        /* Логіка автоперезапуску після охолодження */
        if (dev->config.auto_retry_enabled && enable_cmd) {
            if (dev->state_timer_ms >= dev->config.cool_down_time_ms) {
                dev->retry_count++;
                dev->state = EFUSE_STATE_SOFT_START;
                dev->v_gate_current_v = 0.0f;
                dev->state_timer_ms = 0;
                dev->accumulated_i2t = 0.0f;
                dev->linear_mode_energy_j = 0.0f;
            }
        } else if (!enable_cmd) {
            /* Скидання аварії ручною командою вимкнення */
            dev->state = EFUSE_STATE_OFF;
            dev->last_fault = FAULT_NONE;
            dev->retry_count = 0;
        }
        break;
    }
}
```
```cpp
#include <cstdint>
#include <chrono>
#include <algorithm>

namespace embedded::power {

enum class FuseState : uint8_t {
    Off = 0,
    SoftStart,
    Operational,
    CurrentLimit,
    Fault
};

enum class FaultReason : uint8_t {
    None = 0,
    ShortCircuit,
    ThermalI2t,
    SoaViolation,
    StartupTimeout,
    Undervoltage
};

struct FuseConfig {
    float vin_min_v{4.5f};
    float nominal_current_a{5.0f};
    float short_circuit_current_a{25.0f};
    float i2t_energy_limit_a2s{12.5f};
    float max_linear_power_w{30.0f};
    float soft_start_step_v{0.2f};
    uint32_t startup_timeout_ms{50};
    uint32_t cooldown_time_ms{1000};
    bool auto_retry{true};
};

class SmartEFuseController {
public:
    explicit SmartEFuseController(const FuseConfig& config) noexcept
        : config_(config), state_(FuseState::Off), last_fault_(FaultReason::None) {}

    void ProcessTick(bool enable_request, float v_in, float v_out, float i_load, std::chrono::milliseconds dt) noexcept {
        const float dt_sec = std::chrono::duration<float>(dt).count();
        const float v_ds = (v_in > v_out) ? (v_in - v_out) : 0.0f;

        // Захист від зниження напруги живлення (UVLO)
        if (v_in < config_.vin_min_v && state_ != FuseState::Off) {
            TripFault(FaultReason::Undervoltage);
            return;
        }

        switch (state_) {
        case FuseState::Off:
            if (enable_request && v_in >= config_.vin_min_v) {
                state_ = FuseState::SoftStart;
                v_gate_current_v_ = 0.0f;
                state_elapsed_time_ = std::chrono::milliseconds{0};
                accumulated_i2t_ = 0.0f;
                linear_mode_energy_j_ = 0.0f;
            }
            break;

        case FuseState::SoftStart: {
            state_elapsed_time_ += dt;

            // Субмікросекундний захист від КЗ під час пуску
            if (i_load >= config_.short_circuit_current_a) {
                TripFault(FaultReason::ShortCircuit);
                return;
            }

            // Контроль теплового стресу кристала в лінійному режимі (SOA)
            const float power_now = v_ds * i_load;
            linear_mode_energy_j_ += power_now * dt_sec;
            if (power_now > config_.max_linear_power_w && linear_mode_energy_j_ > 2.0f) {
                TripFault(FaultReason::SoaViolation);
                return;
            }

            // Плавний підйом напруги затвора
            v_gate_current_v_ = std::min(v_gate_current_v_ + config_.soft_start_step_v, target_gate_v_);
            ApplyGateVoltage(v_gate_current_v_);

            if (v_out >= (v_in * 0.90f)) {
                state_ = FuseState::Operational;
                v_gate_current_v_ = target_gate_v_;
                ApplyGateVoltage(v_gate_current_v_);
                state_elapsed_time_ = std::chrono::milliseconds{0};
                linear_mode_energy_j_ = 0.0f;
            } else if (state_elapsed_time_.count() > config_.startup_timeout_ms) {
                TripFault(FaultReason::StartupTimeout);
            }
            break;
        }

        case FuseState::Operational:
            // 1. Надшвидке відсікання КЗ
            if (i_load >= config_.short_circuit_current_a) {
                TripFault(FaultReason::ShortCircuit);
                return;
            }

            // 2. Тепловий інтеграл надструму I²t
            if (i_load > config_.nominal_current_a) {
                const float excess = i_load - config_.nominal_current_a;
                accumulated_i2t_ += (excess * excess) * dt_sec;

                if (accumulated_i2t_ >= config_.i2t_energy_limit_a2s) {
                    TripFault(FaultReason::ThermalI2t);
                    return;
                }
            } else {
                // Охолодження при нормальному струмі
                accumulated_i2t_ = std::max(0.0f, accumulated_i2t_ - accumulated_i2t_ * 0.1f * dt_sec);
            }

            if (!enable_request) {
                FastShutdown();
                state_ = FuseState::Off;
            }
            break;

        case FuseState::CurrentLimit:
            state_elapsed_time_ += dt;
            if (v_ds * i_load > config_.max_linear_power_w) {
                TripFault(FaultReason::SoaViolation);
            }
            break;

        case FuseState::Fault:
            state_elapsed_time_ += dt;

            if (config_.auto_retry && enable_request) {
                if (state_elapsed_time_.count() >= config_.cooldown_time_ms) {
                    retry_counter_++;
                    state_ = FuseState::SoftStart;
                    v_gate_current_v_ = 0.0f;
                    state_elapsed_time_ = std::chrono::milliseconds{0};
                    accumulated_i2t_ = 0.0f;
                    linear_mode_energy_j_ = 0.0f;
                }
            } else if (!enable_request) {
                state_ = FuseState::Off;
                last_fault_ = FaultReason::None;
                retry_counter_ = 0;
            }
            break;
        }
    }

    [[nodiscard]] FuseState GetState() const noexcept { return state_; }
    [[nodiscard]] FaultReason GetLastFault() const noexcept { return last_fault_; }
    [[nodiscard]] float GetThermalStressPercent() const noexcept {
        return (accumulated_i2t_ / config_.i2t_energy_limit_a2s) * 100.0f;
    }

private:
    void TripFault(FaultReason reason) noexcept {
        FastShutdown();
        state_ = FuseState::Fault;
        last_fault_ = reason;
        state_elapsed_time_ = std::chrono::milliseconds{0};
    }

    static void ApplyGateVoltage(float v_gate) noexcept;
    static void FastShutdown() noexcept;

    FuseConfig config_;
    FuseState state_{FuseState::Off};
    FaultReason last_fault_{FaultReason::None};

    float v_gate_current_v_{0.0f};
    static constexpr float target_gate_v_{10.0f};
    float accumulated_i2t_{0.0f};
    float linear_mode_energy_j_{0.0f};

    std::chrono::milliseconds state_elapsed_time_{0};
    uint32_t retry_counter_{0};
};

} // namespace embedded::power
```
:::

### Типові апаратні підводні камені та трасування друкованої плати

1. **Індуктивний перепад на вході (`L_trace · di/dt`):** Коли силовий MOSFET відсікає струм 30 А за час комутації 200 нс, паразитна індуктивність проводів лінії живлення `L_in ≈ 100 нГн` породжує стрибок перенапруги:
   ```
   V_spike = L_in · (di / dt) = 100 · 10⁻⁹ · [ 30 / (200 · 10⁻⁹) ] = 15 В
   ```
   Якщо вхідна напруга становила 24 В, амплітуда перенапруги на стоці сягає 39 В, що миттєво пробиває стік-витік польового транзистора. Вхід e-Fuse обов'язково захищають швидкодіючим супресором (TVS-діодом) та вхідним керамічним демпфуючим конденсатором із низьким послідовним опором (ESR), встановленим безпосередньо біля виводів живлення мікросхеми.

2. **Зворотний струм через внутрішній body-діод:** Вбудований паразитно-технологічний діод MOSFET зміщений у прямому напрямку від витоку до стоку. Якщо навантаження містить акумуляторну батарею або велику ємність, а вхідна напруга знеструмлюється, струм безперешкодно потече назад через діод. Для повної ізоляції застосовують топологію з двох зустрічно увімкнених транзисторів (*Back-to-Back MOSFETs* із загальним витоком).

3. **Трасування вимірювальних ліній Кельвіна (Kelvin Sense Routing):** Якщо для вимірювання струму використовується зовнішній низькоомний шунт (наприклад, 2 мОм), вимірювальні провідники `SENSE+` та `SENSE-` трасують строго диференційною парою однакової довжини безпосередньо від внутрішніх контактних майданчиків резистора. Неприпустимо поєднувати вимірювальну доріжку із силовим полігоном, оскільки паразитний опір мідної фольги товщиною 35 мкм (близько 0.5 мОм/квадрат) та магнітні наводки від `di/dt` внесуть похибку понад 30–50% у розрахунок аварійного струму.

4. **Телеметрія та діагностика через інтерфейс PMBus/I²C:** Сучасні контролери e-Fuse передають у системну шину дані телеметрії в реальному часі: миттєву вхідну та вихідну напругу, струм навантаження, температуру кристала, накопичений відсоток теплового інтеграла `I²t` та прапорці попередження (*Early Warning ALERT* при досягненні 80% від струмової уставки). Це дозволяє системному програмному забезпеченню знижувати споживання другорядних вузлів або вимикати вентилятори охолодження до того, як відбудеться аварійне відключення живлення.
