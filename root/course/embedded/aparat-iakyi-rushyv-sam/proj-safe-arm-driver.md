# ⚙️ Безпечний драйвер приводу з динамічним блокуванням та Watchdog

Надійне керування силовими приводами вимагає суворого протоколу переходу між безпечним станом знеструмлення та активним робочим режимом. Якщо прошивка дозволяє прямий запис у регістри ШІМ без попередньої перевірки умов безпеки, будь-який збій покажчика пам'яті, переповнення стека або помилка ініціалізації здатні запустити мотор у непередбачуваний момент.

Розгляньмо практичну інженерну реалізацію драйвера безпечного приводу, побудованого на трьох взаємопов'язаних рубежах оборони: автоматі станів взяття на охорону (англ. *arming state machine*), динамічному генераторі імпульсів безпеки (англ. *safety heartbeat*) та апаратному нагляді за часом виконання через сторожовий таймер (Watchdog).

## Архітектура драйвера та стани безпеки

Драйвер керує двома фізичними виводами мікроконтролера:
1. `PIN_SAFETY_HEARTBEAT` — вивід генерації прямокутного динамічного сигналу частотою 1 кГц, що живить апаратну помпу заряду ключа дозволу сили. Постійний рівень «0» або «1» на цьому виводі призводить до швидкого розряджання фільтруючої ємності помпи та фізичного знеструмлення приводу.
2. `PIN_MOTOR_PWM` — вивід таймера широтно-імпульсної модуляції для регулювання швидкості або крутного моменту мотора.

Система функціонує за п'ятьма строго розділеними станами:
- `STATE_DISARMED` — початковий стан після старту пристрою. Генератор помпи заряду зупинено, коефіцієнт заповнення ШІМ дорівнює нулю, силове живлення мотора фізично відключене апаратним ключем;
- `STATE_ARM_REQUESTED` — оператор або високорівневий планувальник місії надіслав запит на активацію сили, супроводжений спеціальним магічним токеном валідації;
- `STATE_PRE_ARM_CHECK` — фаза самодіагностики: перевірка напруги батареї через вбудований АЦП, стану лінії аварійної зупинки (E-Stop) та відсутності прапорів перегріву або перевантаження за струмом;
- `STATE_ARMED` — робочий режим: дозволено подачу сили, у кожному циклі формується імпульс серцебиття та оновлюється цільове значення ШІМ;
- `STATE_FAULT` — аварійний стан: миттєве апаратне скидання всіх вихідних сигналів у нуль, зупинка серцебиття та блокування роботи до повного перезапуску системи.

Драйвер спроєктовано так, щоб будь-яке порушення послідовності викликів або помилка валідації повертали автомат у безпечний стан `FAULT`.

## Реалізація драйвера на C та C++

Нижче наведено повну реалізацію драйвера двома мовами: на мові C зі строгою перевіркою структур та на мові C++ із використанням концептів компіляції та типізованих станів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define SAFETY_TOKEN_MAGIC  0x5A3C96E1U
#define PWM_MAX_DUTY        1000U
#define MIN_SAFE_VOLTAGE_MV 11000U
#define MAX_SAFE_VOLTAGE_MV 14500U

typedef enum {
    ACTUATOR_DISARMED = 0,
    ACTUATOR_ARM_REQUESTED,
    ACTUATOR_PRE_ARM_CHECK,
    ACTUATOR_ARMED,
    ACTUATOR_FAULT
} ActuatorState;

typedef struct {
    ActuatorState state;
    uint32_t last_heartbeat_ms;
    uint32_t arm_request_time_ms;
    uint16_t current_pwm;
    bool emergency_stop_active;
} SafeActuatorDriver;

// Платформні виклики керування регістрами GPIO та таймера
extern void hw_gpio_write_heartbeat(bool level);
extern void hw_timer_set_pwm_duty(uint16_t duty);
extern uint32_t hw_get_time_ms(void);
extern uint16_t hw_read_supply_voltage_mv(void);
extern bool hw_read_estop_pin(void);
extern void hw_watchdog_reset(void);

void safe_actuator_init(SafeActuatorDriver *drv) {
    // 1. Апаратні виходи встановлюємо в безпечний нуль ДО дозволу виходів
    hw_gpio_write_heartbeat(false);
    hw_timer_set_pwm_duty(0);

    drv->state = ACTUATOR_DISARMED;
    drv->last_heartbeat_ms = 0;
    drv->arm_request_time_ms = 0;
    drv->current_pwm = 0;
    drv->emergency_stop_active = false;
}

bool safe_actuator_request_arm(SafeActuatorDriver *drv, uint32_t token) {
    if (token != SAFETY_TOKEN_MAGIC) {
        drv->state = ACTUATOR_FAULT;
        return false;
    }
    if (drv->state != ACTUATOR_DISARMED) {
        return false;
    }
    drv->state = ACTUATOR_ARM_REQUESTED;
    drv->arm_request_time_ms = hw_get_time_ms();
    return true;
}

void safe_actuator_disarm(SafeActuatorDriver *drv) {
    // Миттєво зупиняємо генератор помпи та скидаємо ШІМ
    hw_gpio_write_heartbeat(false);
    hw_timer_set_pwm_duty(0);
    drv->current_pwm = 0;
    if (drv->state != ACTUATOR_FAULT) {
        drv->state = ACTUATOR_DISARMED;
    }
}

void safe_actuator_process_cycle(SafeActuatorDriver *drv, uint16_t target_pwm) {
    uint32_t now = hw_get_time_ms();
    drv->emergency_stop_active = hw_read_estop_pin();

    if (drv->emergency_stop_active) {
        safe_actuator_disarm(drv);
        drv->state = ACTUATOR_FAULT;
        return;
    }

    switch (drv->state) {
        case ACTUATOR_DISARMED:
            hw_gpio_write_heartbeat(false);
            hw_timer_set_pwm_duty(0);
            break;

        case ACTUATOR_ARM_REQUESTED:
            drv->state = ACTUATOR_PRE_ARM_CHECK;
            break;

        case ACTUATOR_PRE_ARM_CHECK: {
            uint16_t v_mv = hw_read_supply_voltage_mv();
            if (v_mv >= MIN_SAFE_VOLTAGE_MV && v_mv <= MAX_SAFE_VOLTAGE_MV) {
                drv->state = ACTUATOR_ARMED;
                drv->last_heartbeat_ms = now;
            } else {
                safe_actuator_disarm(drv);
                drv->state = ACTUATOR_FAULT;
            }
            break;
        }

        case ACTUATOR_ARMED: {
            // Генерація динамічного меандру серцебиття з періодом 1 мс (1 кГц)
            static bool hb_phase = false;
            hb_phase = !hb_phase;
            hw_gpio_write_heartbeat(hb_phase);
            drv->last_heartbeat_ms = now;

            if (target_pwm > PWM_MAX_DUTY) {
                target_pwm = PWM_MAX_DUTY;
            }
            drv->current_pwm = target_pwm;
            hw_timer_set_pwm_duty(drv->current_pwm);
            break;
        }

        case ACTUATOR_FAULT:
        default:
            safe_actuator_disarm(drv);
            break;
    }

    // Регулярне годування сторожового таймера
    hw_watchdog_reset();
}
```
```cpp
#include <cstdint>
#include <optional>
#include <concepts>

namespace safety {

enum class ActuatorState : uint8_t {
    Disarmed = 0,
    ArmRequested,
    PreArmCheck,
    Armed,
    Fault
};

struct SafetyConfig {
    static constexpr uint32_t TokenMagic = 0x5A3C96E1U;
    static constexpr uint16_t PwmMaxDuty = 1000U;
    static constexpr uint16_t MinSafeVoltageMv = 11000U;
    static constexpr uint16_t MaxSafeVoltageMv = 14500U;
};

// Концепт апаратної платформи для компіляційної перевірки периферії
template <typename Platform>
concept HardwareInterface = requires(Platform p, bool b, uint16_t duty) {
    { p.writeHeartbeat(b) } -> std::same_as<void>;
    { p.setPwmDuty(duty) } -> std::same_as<void>;
    { p.getTimeMs() } -> std::same_as<uint32_t>;
    { p.readVoltageMv() } -> std::same_as<uint16_t>;
    { p.readEstopActive() } -> std::same_as<bool>;
    { p.feedWatchdog() } -> std::same_as<void>;
};

template <HardwareInterface Platform>
class SafeActuator {
public:
    explicit SafeActuator(Platform& hw) noexcept
        : hw_(hw), state_(ActuatorState::Disarmed), currentPwm_(0), hbPhase_(false) {
        // Гарантований безпечний стан апаратних ліній при інстанціації
        hw_.writeHeartbeat(false);
        hw_.setPwmDuty(0);
    }

    [[nodiscard]] bool requestArm(uint32_t token) noexcept {
        if (token != SafetyConfig::TokenMagic) {
            state_ = ActuatorState::Fault;
            disarm();
            return false;
        }
        if (state_ != ActuatorState::Disarmed) {
            return false;
        }
        state_ = ActuatorState::ArmRequested;
        return true;
    }

    void disarm() noexcept {
        hw_.writeHeartbeat(false);
        hw_.setPwmDuty(0);
        currentPwm_ = 0;
        if (state_ != ActuatorState::Fault) {
            state_ = ActuatorState::Disarmed;
        }
    }

    void update(uint16_t targetPwm) noexcept {
        if (hw_.readEstopActive()) {
            state_ = ActuatorState::Fault;
            disarm();
            return;
        }

        switch (state_) {
            case ActuatorState::Disarmed:
                hw_.writeHeartbeat(false);
                hw_.setPwmDuty(0);
                break;

            case ActuatorState::ArmRequested:
                state_ = ActuatorState::PreArmCheck;
                break;

            case ActuatorState::PreArmCheck: {
                const uint16_t v = hw_.readVoltageMv();
                if (v >= SafetyConfig::MinSafeVoltageMv && v <= SafetyConfig::MaxSafeVoltageMv) {
                    state_ = ActuatorState::Armed;
                } else {
                    state_ = ActuatorState::Fault;
                    disarm();
                }
                break;
            }

            case ActuatorState::Armed: {
                hbPhase_ = !hbPhase_;
                hw_.writeHeartbeat(hbPhase_);

                currentPwm_ = (targetPwm > SafetyConfig::PwmMaxDuty)
                                  ? SafetyConfig::PwmMaxDuty
                                  : targetPwm;
                hw_.setPwmDuty(currentPwm_);
                break;
            }

            case ActuatorState::Fault:
            default:
                disarm();
                break;
        }

        hw_.feedWatchdog();
    }

    [[nodiscard]] ActuatorState getState() const noexcept { return state_; }
    [[nodiscard]] bool isArmed() const noexcept { return state_ == ActuatorState::Armed; }

private:
    Platform& hw_;
    ActuatorState state_;
    uint16_t currentPwm_;
    bool hbPhase_;
};

} // namespace safety
```
:::

## Інженерний аналіз пасток та валідація надійності

Під час інтеграції безпечного драйвера в реальний проект вбудованої системи розробники часто стикаються з трьома критичними помилками архітектури:

### 1. Годування сторожового таймера всередині переривання
Найпоширеніша ілюзія надійності — скидання лічильника Watchdog усередині обробника переривання апаратного таймера (ISR). Оскільки апаратний таймер тактується незалежно від головного процесора, переривання продовжуватиме справно викликатися навіть тоді, коли головний потік прошивки завис у взаємному блокуванні (англ. *deadlock*) або пошкодив таблицю диспетчера задач.

У безпечній архітектурі сторожовий таймер оновлюється **виключно в кінці повного циклу валідації безпеки**. Якщо головний цикл зависає, сторож не отримує підтвердження і через 50–100 мс примусово скидає мікроконтролер, повертаючи затвори ключів під захист апаратних підтяжок.

### 2. Використання статичного сигналу дозволу замість динамічного меандру
Якщо замість генерації частоти 1 кГц розробник використовує звичайний постійний рівень `HIGH` для вмикання силового реле, захист втрачає стійкість до апаратних відмов. При електричному пробої вихідного P-FET транзистора мікроконтролера на лінію виводиться постійна напруга `3.3 В`.

Динамічна помпа заряду з розділовим конденсатором `100 нФ` виключає цей ризик: постійний струм не проходить крізь конденсатор, і ключ живлення розмикається автоматично за лічені мілісекунди після зупинки коливань.

### 3. Програмне пригнічення деренчання аварійної кнопки (E-Stop Debounce)
Лінія кнопки аварійної зупинки повинна оброблятися з пріоритетом на апаратне відключення. Спроба додати занадто довгий програмний фільтр деренчання (наприклад, 100 мс) затримує зняття сигналу безпеки при реальній небезпеці. 

У надійних системах лінію E-Stop заводять одночасно на вхід мікроконтролера для програмного переходу в `STATE_FAULT` та на апаратний розрив живлення драйвера затворів, забезпечуючи нульовий час реакції на аварійне натискання.

## Методика тестування надійності драйвера на стенді

Перевірка безпечного драйвера не обмежується звичайними позитивними юніт-тестами. Для сертифікації силового вузла застосовують методику навмисного внесення апаратних і програмних несправностей (англ. *fault injection testing*):

1. **Тест апаратного обриву лінії серцебиття:** Під час активного обертання мотора лінія `PIN_SAFETY_HEARTBEAT` фізично розмикається. За допомогою цифрового осцилографа фіксують час зникнення напруги на силовому затворі. При правильному розрахунку компонентів помпи заряду час вимкнення сили не повинен перевищувати 3–5 мілісекунд.
2. **Тест зависання процесора:** У прикладний код вставляється штучний нескінченний цикл `while(1)`. Перевіряється, що генерація імпульсів серцебиття негайно припиняється, помпа знеструмлює ключ живлення ще до того, як спрацює апаратний Watchdog, а після скидання сторожа привід залишається у безпечному стані `DISARMED`.
3. **Тест короткого замикання виводу на живлення:** Вивід серцебиття замикається перемичкою на шину `+3.3 В`. Розділовий конденсатор повинен повністю заблокувати постійний струм, запобігаючи вмиканню силового ключа.
