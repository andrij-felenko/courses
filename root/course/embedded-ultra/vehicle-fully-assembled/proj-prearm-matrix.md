# ⚙️ Реалізація матриці передпольотних перевірок та контуру безпеки

Модуль оцінки стану безпеки (Pre-Arm Safety Matrix) реалізує багаторівневу перевірку апаратних і програмних підсистем перед дозволом на запуск двигунів. Без такої матриці будь-який прихований збій — тимчасове просідання напруги, розсинхронізація фільтра Калмана, незавершене калібрування компаса чи ненавмисний рух стіка газу — передає керування силовим ключам і призводить до аварії на старті.

### Архітектура автомата безпеки та бітова маска готовності

У багатопотоковому середовищі операційної системи реального часу (RTOS) стан безпеки оцінюється в окремому низькопріоритетному потоці опитування стану з частотою 10–20 Гц. Це унеможливлює блокування високочастотних контурів розрахунку орієнтації та PID-стабілізації (частота 400–8000 Гц), але гарантує постійну готовність свіжого статусу передпольотної діагностики.

Система передпольотної безпеки будується як детермінований скінченний автомат із чотирма основними станами:

1. `DISARMED` (заблоковано): вихідні ШІМ-таймери або цифрові кадри DShot повністю вимкнені (коефіцієнт заповнення 0%). Будь-яка команда від польотного регулятора PID ігнорується драйвером приводів.
2. `ARMING_REQUEST` (запит на активацію): перехідний стан, коли оператор надіслав команду зведення (перемикачем на пульті чи командою `MAV_CMD_COMPONENT_ARM_DISARM`). Модуль безпеки проводить атомарну оцінку всієї матриці умов.
3. `ARMED` (озброєно): перевірки успішно пройдені. Таймери активуються, мотори переходять у режим мінімальних холостих обертів (Idle Spin), контури стабілізації отримують дозвіл керувати тягою.
4. `FAILSAFE_LOCKOUT` (аварійне блокування): критична відмова в польоті або на землі (втрата RC, пробій батареї, перегрів), що викликає примусове знеструмлення або перехід в аварійну посадку.

Стан кожної підсистеми кодується окремим бітовим прапорцем у 32-бітному полі `prearm_status_mask`:

- `BIT(0) — PREARM_MASK_IMU_CALIBRATED`: акселерометр пройшов 6-позиційне калібрування, гіроскоп не має дрейфу нуля.
- `BIT(1) — PREARM_MASK_MAG_HEALTHY`: компас відкалібрований, магнітна інновація EKF не перевищує поріг.
- `BIT(2) — PREARM_MASK_BARO_VALID`: барометр стабільний, шум висоти в межах допустимого.
- `BIT(3) — PREARM_MASK_BATTERY_OK`: напруга вища за поріг розрядженого акумулятора з урахуванням фільтра гістерезису.
- `BIT(4) — PREARM_MASK_RC_STICK_SAFE`: стік газу перебуває в крайній нижній позиції (< 5% діапазону).
- `BIT(5) — PREARM_MASK_EKF_CONVERGED`: фільтр Калмана збігся, дисперсії оцінки швидкості й орієнтації менші за критичну межу.
- `BIT(6) — PREARM_MASK_SAFETY_SWITCH`: фізична апаратна кнопка на фюзеляжі переведена людиною в робоче положення.

Дозвіл на армінг обчислюється як суворе побітове порівняння поточної маски з маскою обов'язкових вимог `REQUIRED_MASK`.

### Часовий гістерезис помилок та захист від брязкоту

Миттєвий вимір сенсора може зазнавати випадкових викидів або короткочасного шуму на шині I2C/SPI через електромагнітні наводки або стрибки струму. Щоб уникнути хибного дозволу на армінг під час перехідних процесів або передчасного блокування через одиничний збійний пакет, модуль оцінює не лише миттєвий стан, але й тривалість безперервної стабільності сигналу:

```
T_stable ≥ T_threshold  (наприклад, 2000 мс безперервно)
```

Якщо хоча б один параметр виходить за межі норми навіть на один такт опитування (наприклад, стік газу здригнувся до 6% чи напруга на частку секунди просіла нижче 3.70 В через запуск передавача), таймер стабільності миттєво скидається в нуль. Для повторного отримання дозволу всі параметри повинні знову безперервно витримуватися в межах норми протягом повного інтервалу гістерезису `T_threshold`.

Окремо контролюється поведінка після відмови: якщо запит на зведення відхилено, система не просто блокує зміну стану, але й транслює текстове повідомлення `STATUSTEXT` протоколу MAVLink із рівнем критичності `MAV_SEVERITY_CRITICAL` та точною причиною відмови (наприклад, `PreArm: Compass inconsistent by 45 deg` або `PreArm: Battery below 3.70V/cell`), що дозволяє оператору на наземній станції GCS миттєво локалізувати проблему.

### Крайові випадки та апаратні пастки

Під час практичної інтеграції модуля оцінки безпеки виникають чотири характерні крайові ситуації:

1. **Просідання напруги під час спрацювання реле або підсвічування.** Підключення додаткових споживачів створює імпульсне просідання шини живлення. Якщо поріг батареї перевіряється без фільтрації низьких частот, апаратний детектор забороняє армінг. Фільтр ковзного середнього (EMA) на вимірах напруги усуває короткочасні імпульси тривалістю менше 100 мс.
2. **Зрушення апарата під час підтвердження команди.** Якщо оператор натискає тумблер зведення на пульті в той момент, коли апарат несуть у руках на точку старту, гіроскоп фіксує кутову швидкість `||ω|| > 0.05 рад/с`. Модуль безпеки блокує армінг, запобігаючи запуску гвинтів у руках людини.
3. **Аномалія локального магнітного поля на стартовому майданчику.** Розміщення дрона на залізобетонній плиті або поряд з металевими конструкціями викликає відхилення вектора магнітного поля від глобальної моделі WMM. Матриця перевірок виявляє розбіжність магнітної інновації EKF і блокує старт, запобігаючи неконтрольованому закручуванню по осі Yaw під час відриву.
4. **Несправність апаратного перемикача Safety Switch.** Окислення контактів або обрив сигнального проводу кнопки безпеки залишає біт `PREARM_BIT_SAFETY_SW` у нулі, надійно утримуючи силові ШІМ-лінії заблокованими на рівні мікроконтролера вводу-виводу.

### Програмна реалізація мовами C та C++

Нижче наведено робочий модуль оцінювача стану безпеки, який реалізує бітову маску, фільтрацію з гістерезисом та керування силовими ключами.

:::tabs
@tab C
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define PREARM_BIT_IMU_OK       (1U << 0)
#define PREARM_BIT_MAG_OK       (1U << 1)
#define PREARM_BIT_BARO_OK      (1U << 2)
#define PREARM_BIT_BATTERY_OK   (1U << 3)
#define PREARM_BIT_RC_SAFE      (1U << 4)
#define PREARM_BIT_EKF_OK       (1U << 5)
#define PREARM_BIT_SAFETY_SW    (1U << 6)

#define PREARM_ALL_REQUIRED     (PREARM_BIT_IMU_OK | \
                                 PREARM_BIT_MAG_OK | \
                                 PREARM_BIT_BARO_OK | \
                                 PREARM_BIT_BATTERY_OK | \
                                 PREARM_BIT_RC_SAFE | \
                                 PREARM_BIT_EKF_OK | \
                                 PREARM_BIT_SAFETY_SW)

typedef enum {
    VEHICLE_DISARMED = 0,
    VEHICLE_ARMED,
    VEHICLE_FAILSAFE
} vehicle_arm_state_t;

typedef struct {
    float cell_voltage;
    float throttle_stick;
    float ekf_pos_variance;
    float gyro_drift_rad_s;
    bool  imu_calibrated;
    bool  mag_calibrated;
    bool  baro_healthy;
    bool  safety_switch_pressed;
} sensor_snapshot_t;

typedef struct {
    vehicle_arm_state_t state;
    uint32_t current_mask;
    uint32_t stable_counter_ms;
    const char *last_failure_reason;
} prearm_evaluator_t;

void prearm_init(prearm_evaluator_t *eval) {
    memset(eval, 0, sizeof(*eval));
    eval->state = VEHICLE_DISARMED;
    eval->last_failure_reason = "System initialized in DISARMED state";
}

void prearm_update(prearm_evaluator_t *eval, const sensor_snapshot_t *s, uint32_t dt_ms) {
    uint32_t mask = 0;

    if (s->imu_calibrated && s->gyro_drift_rad_s < 0.05f) {
        mask |= PREARM_BIT_IMU_OK;
    }
    if (s->mag_calibrated) {
        mask |= PREARM_BIT_MAG_OK;
    }
    if (s->baro_healthy) {
        mask |= PREARM_BIT_BARO_OK;
    }
    if (s->cell_voltage >= 3.70f) {
        mask |= PREARM_BIT_BATTERY_OK;
    }
    if (s->throttle_stick <= 0.05f) {
        mask |= PREARM_BIT_RC_SAFE;
    }
    if (s->ekf_pos_variance < 0.80f) {
        mask |= PREARM_BIT_EKF_OK;
    }
    if (s->safety_switch_pressed) {
        mask |= PREARM_BIT_SAFETY_SW;
    }

    eval->current_mask = mask;

    if ((mask & PREARM_ALL_REQUIRED) == PREARM_ALL_REQUIRED) {
        eval->stable_counter_ms += dt_ms;
    } else {
        eval->stable_counter_ms = 0;
    }
}

bool prearm_request_arm(prearm_evaluator_t *eval) {
    if (eval->state == VEHICLE_ARMED) {
        return true;
    }
    if (eval->state == VEHICLE_FAILSAFE) {
        eval->last_failure_reason = "Cannot arm: Failsafe lockout active";
        return false;
    }

    if ((eval->current_mask & PREARM_ALL_REQUIRED) != PREARM_ALL_REQUIRED) {
        if (!(eval->current_mask & PREARM_BIT_IMU_OK)) {
            eval->last_failure_reason = "IMU uncalibrated or high gyro drift";
        } else if (!(eval->current_mask & PREARM_BIT_MAG_OK)) {
            eval->last_failure_reason = "Compass uncalibrated or inconsistent";
        } else if (!(eval->current_mask & PREARM_BIT_BATTERY_OK)) {
            eval->last_failure_reason = "Battery cell voltage below 3.70V";
        } else if (!(eval->current_mask & PREARM_BIT_RC_SAFE)) {
            eval->last_failure_reason = "Throttle stick not at minimum";
        } else if (!(eval->current_mask & PREARM_BIT_EKF_OK)) {
            eval->last_failure_reason = "EKF position variance too high";
        } else if (!(eval->current_mask & PREARM_BIT_SAFETY_SW)) {
            eval->last_failure_reason = "Hardware safety switch not pressed";
        } else {
            eval->last_failure_reason = "General sensor failure";
        }
        return false;
    }

    if (eval->stable_counter_ms < 1500) {
        eval->last_failure_reason = "Sensors not stable long enough (< 1.5s)";
        return false;
    }

    eval->state = VEHICLE_ARMED;
    eval->last_failure_reason = "Armed successfully";
    return true;
}

void prearm_force_disarm(prearm_evaluator_t *eval, const char *reason) {
    eval->state = VEHICLE_DISARMED;
    eval->last_failure_reason = reason;
}
```
@tab C++
```cpp
#include <cstdint>
#include <string_view>
#include <expected>
#include <chrono>

namespace vehicle::safety {

enum class CheckFlag : uint32_t {
    ImuOk       = 1U << 0,
    MagOk       = 1U << 1,
    BaroOk      = 1U << 2,
    BatteryOk   = 1U << 3,
    RcSafe      = 1U << 4,
    EkfOk       = 1U << 5,
    SafetySw    = 1U << 6
};

[[nodiscard]] constexpr uint32_t operator|(CheckFlag a, CheckFlag b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

[[nodiscard]] constexpr uint32_t operator|(uint32_t a, CheckFlag b) noexcept {
    return a | static_cast<uint32_t>(b);
}

constexpr uint32_t RequiredMask = CheckFlag::ImuOk |
                                  CheckFlag::MagOk |
                                  CheckFlag::BaroOk |
                                  CheckFlag::BatteryOk |
                                  CheckFlag::RcSafe |
                                  CheckFlag::EkfOk |
                                  CheckFlag::SafetySw;

enum class ArmState {
    Disarmed,
    Armed,
    FailsafeLockout
};

enum class ArmingError {
    AlreadyArmed,
    FailsafeActive,
    ImuUncalibrated,
    MagInconsistent,
    BaroFault,
    BatteryLow,
    ThrottleNotZero,
    EkfDiverged,
    SafetySwitchOpen,
    HysteresisNotMet
};

struct SensorSnapshot {
    float cellVoltage{0.0f};
    float throttleStick{0.0f};
    float ekfPosVariance{0.0f};
    float gyroDriftRadS{0.0f};
    bool  imuCalibrated{false};
    bool  magCalibrated{false};
    bool  baroHealthy{false};
    bool  safetySwitchPressed{false};
};

class PreArmEvaluator {
public:
    constexpr PreArmEvaluator() noexcept = default;

    void update(const SensorSnapshot& snap, std::chrono::milliseconds dt) noexcept {
        uint32_t mask = 0;

        if (snap.imuCalibrated && snap.gyroDriftRadS < 0.05f) {
            mask |= CheckFlag::ImuOk;
        }
        if (snap.magCalibrated) {
            mask |= CheckFlag::MagOk;
        }
        if (snap.baroHealthy) {
            mask |= CheckFlag::BaroOk;
        }
        if (snap.cellVoltage >= 3.70f) {
            mask |= CheckFlag::BatteryOk;
        }
        if (snap.throttleStick <= 0.05f) {
            mask |= CheckFlag::RcSafe;
        }
        if (snap.ekfPosVariance < 0.80f) {
            mask |= CheckFlag::EkfOk;
        }
        if (snap.safetySwitchPressed) {
            mask |= CheckFlag::SafetySw;
        }

        currentMask_ = mask;

        if ((currentMask_ & RequiredMask) == RequiredMask) {
            stableDuration_ += dt;
        } else {
            stableDuration_ = std::chrono::milliseconds{0};
        }
    }

    [[nodiscard]] std::expected<void, ArmingError> requestArm() noexcept {
        if (state_ == ArmState::Armed) {
            return {};
        }
        if (state_ == ArmState::FailsafeLockout) {
            return std::unexpected(ArmingError::FailsafeActive);
        }

        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::ImuOk))) {
            return std::unexpected(ArmingError::ImuUncalibrated);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::MagOk))) {
            return std::unexpected(ArmingError::MagInconsistent);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::BaroOk))) {
            return std::unexpected(ArmingError::BaroFault);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::BatteryOk))) {
            return std::unexpected(ArmingError::BatteryLow);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::RcSafe))) {
            return std::unexpected(ArmingError::ThrottleNotZero);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::EkfOk))) {
            return std::unexpected(ArmingError::EkfDiverged);
        }
        if (!(currentMask_ & static_cast<uint32_t>(CheckFlag::SafetySw))) {
            return std::unexpected(ArmingError::SafetySwitchOpen);
        }

        if (stableDuration_ < std::chrono::milliseconds{1500}) {
            return std::unexpected(ArmingError::HysteresisNotMet);
        }

        state_ = ArmState::Armed;
        return {};
    }

    void disarm() noexcept {
        state_ = ArmState::Disarmed;
    }

    void triggerFailsafe() noexcept {
        state_ = ArmState::FailsafeLockout;
    }

    [[nodiscard]] ArmState state() const noexcept { return state_; }
    [[nodiscard]] uint32_t bitmask() const noexcept { return currentMask_; }

private:
    ArmState state_{ArmState::Disarmed};
    uint32_t currentMask_{0};
    std::chrono::milliseconds stableDuration_{0};
};

} // namespace vehicle::safety
```
:::
