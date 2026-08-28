# ⚙️ Архітектура арбітра польотних режимів та безударного перемикання

Головне завдання архітектури польотного стека — гарантувати безпечний перехід між парадигмами керування в реальному часі. Якщо апарат летить на швидкості 15 м/с в автономному місійному режимі (Supervisory / Mission), і пілот раптово перемикає тумблер на пульті в прямий ручний режим (Direct Manual / Acro), пряме підключення нового джерела уставки до виконавчих контурів призведе до миттєвого зриву динаміки або аварії.

У момент зміни парадигми виникають три критичні загрози:
1. **Стрибок уставки (Setpoint Discontinuity):** автопілот тримав кут тангажу −25° для підтримання швидкості проти вітру, тоді як стік пілота на пульті стоїть у нейтралі (нульовий кут або нульова швидкість обертання). Миттєва східчаста зміна цілі змусить регулятор видати максимальний керівний момент, створивши перевантаження на силову установку й ривок конструкції.
2. **Накопичення інтегратора (Integrator Windup):** інтегральна ланка PID-регулятора внутрішнього контуру в попередньому режимі накопичила стале зміщення для компенсації несиметрії тяги моторів або поривів вітру. Якщо в новому режимі цей інтегратор не зафіксувати або не перерахувати під нову помилку, виникне потужний сплеск моменту (*integrator kick*).
3. **Конфлікт систем координат:** наглядовий режим оперує векторами швидкості у світовій системі NED (північ-схід-вниз), допоміжний режим Fly-by-Wire задає кути крену й тангажу відносно горизонту, а прямий ручний режим транслює положення стіка в кутові швидкості навколо власних зв'язаних осей дрона (*body frame*). Перемикання вимагає коректної трансформації базисів без втрати знака.

Нижче наведено робочу реалізацію арбітра режимів польотного контролера мовами C та ідіоматичною C++20. Модуль забезпечує **безударний перехід** (*bumpless transfer*), фільтрацію темпу наростання (*slew-rate limiting*), демпфування інтеграторів та багаторівневий сторожовий таймер аварійної деградації (*failsafe watchdog*).

## Архітектура арбітра: реалізація C та C++

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_RATE_DEG_S       360.0f
#define MAX_ANGLE_DEG        45.0f
#define SLEW_RATE_DEG_S      180.0f  // Максимальна швидкість зміни уставки при переході
#define RC_TIMEOUT_MS        500
#define OFFBOARD_TIMEOUT_MS  1000

typedef enum {
    MODE_DIRECT_MANUAL = 0, // 1. Acro / Rate: уставка кутової швидкості (град/с)
    MODE_ASSISTED_ANGLE,    // 2. Fly-by-Wire: уставка кута нахилу (град)
    MODE_SUPERVISORY_AUTO,  // 3. Наглядове: уставка від бортового комп'ютера
    MODE_FAILSAFE_LAND      // Аварійний спуск при відмові зв'язку
} control_mode_t;

typedef struct {
    float roll_deg;
    float pitch_deg;
    float yaw_deg;
    float rate_roll_deg_s;
    float rate_pitch_deg_s;
    float rate_yaw_deg_s;
} vehicle_state_t;

typedef struct {
    float roll_cmd;   // град/с (у Manual) або град (у Angle/Auto)
    float pitch_cmd;
    float yaw_cmd;
    float throttle;   // 0.0 .. 1.0
} control_setpoint_t;

typedef struct {
    control_mode_t current_mode;
    control_mode_t requested_mode;
    control_setpoint_t active_setpoint;
    control_setpoint_t target_setpoint;
    
    uint32_t last_rc_time_ms;
    uint32_t last_offboard_time_ms;
    bool is_transitioning;
    float transition_progress; // 0.0 .. 1.0
} mode_arbiter_t;

void mode_arbiter_init(mode_arbiter_t *arbiter) {
    arbiter->current_mode = MODE_ASSISTED_ANGLE;
    arbiter->requested_mode = MODE_ASSISTED_ANGLE;
    arbiter->active_setpoint = (control_setpoint_t){0.0f, 0.0f, 0.0f, 0.0f};
    arbiter->target_setpoint = (control_setpoint_t){0.0f, 0.0f, 0.0f, 0.0f};
    arbiter->last_rc_time_ms = 0;
    arbiter->last_offboard_time_ms = 0;
    arbiter->is_transitioning = false;
    arbiter->transition_progress = 1.0f;
}

static float clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

static float apply_slew_rate(float current, float target, float max_delta) {
    float error = target - current;
    if (fabsf(error) <= max_delta) {
        return target;
    }
    return current + (error > 0.0f ? max_delta : -max_delta);
}

bool mode_arbiter_request_mode(mode_arbiter_t *arbiter, 
                               control_mode_t new_mode, 
                               const vehicle_state_t *state) {
    if (arbiter->current_mode == new_mode) {
        return true;
    }

    // БЕЗУДАРНИЙ ПЕРЕХІД: фіксація поточного стану як стартової точки нової уставки
    if (new_mode == MODE_DIRECT_MANUAL) {
        arbiter->active_setpoint.roll_cmd = state->rate_roll_deg_s;
        arbiter->active_setpoint.pitch_cmd = state->rate_pitch_deg_s;
        arbiter->active_setpoint.yaw_cmd = state->rate_yaw_deg_s;
    } else if (new_mode == MODE_ASSISTED_ANGLE || new_mode == MODE_SUPERVISORY_AUTO) {
        arbiter->active_setpoint.roll_cmd = clampf(state->roll_deg, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
        arbiter->active_setpoint.pitch_cmd = clampf(state->pitch_deg, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
        arbiter->active_setpoint.yaw_cmd = state->yaw_deg;
    }

    arbiter->current_mode = new_mode;
    arbiter->is_transitioning = true;
    arbiter->transition_progress = 0.0f;
    return true;
}

void mode_arbiter_update(mode_arbiter_t *arbiter,
                         const vehicle_state_t *state,
                         const control_setpoint_t *rc_sp,
                         const control_setpoint_t *offboard_sp,
                         uint32_t now_ms,
                         float dt_sec) {
    // 1. Моніторинг здоров'я лінків (Failsafe Watchdog)
    bool rc_valid = (now_ms - arbiter->last_rc_time_ms) <= RC_TIMEOUT_MS;
    bool offboard_valid = (now_ms - arbiter->last_offboard_time_ms) <= OFFBOARD_TIMEOUT_MS;

    // Сходинкова деградація при втраті зв'язку
    if (arbiter->current_mode == MODE_SUPERVISORY_AUTO && !offboard_valid) {
        if (rc_valid) {
            mode_arbiter_request_mode(arbiter, MODE_ASSISTED_ANGLE, state);
        } else {
            mode_arbiter_request_mode(arbiter, MODE_FAILSAFE_LAND, state);
        }
    } else if ((arbiter->current_mode == MODE_ASSISTED_ANGLE || 
                arbiter->current_mode == MODE_DIRECT_MANUAL) && !rc_valid) {
        mode_arbiter_request_mode(arbiter, MODE_FAILSAFE_LAND, state);
    }

    // 2. Селекція цільової уставки
    switch (arbiter->current_mode) {
        case MODE_DIRECT_MANUAL:
            arbiter->target_setpoint.roll_cmd = rc_sp->roll_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.pitch_cmd = rc_sp->pitch_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.yaw_cmd = rc_sp->yaw_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.throttle = rc_sp->throttle;
            break;

        case MODE_ASSISTED_ANGLE:
            arbiter->target_setpoint.roll_cmd = rc_sp->roll_cmd * MAX_ANGLE_DEG;
            arbiter->target_setpoint.pitch_cmd = rc_sp->pitch_cmd * MAX_ANGLE_DEG;
            arbiter->target_setpoint.yaw_cmd = rc_sp->yaw_cmd * MAX_RATE_DEG_S;
            arbiter->target_setpoint.throttle = rc_sp->throttle;
            break;

        case MODE_SUPERVISORY_AUTO:
            arbiter->target_setpoint.roll_cmd = clampf(offboard_sp->roll_cmd, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
            arbiter->target_setpoint.pitch_cmd = clampf(offboard_sp->pitch_cmd, -MAX_ANGLE_DEG, MAX_ANGLE_DEG);
            arbiter->target_setpoint.yaw_cmd = offboard_sp->yaw_cmd;
            arbiter->target_setpoint.throttle = offboard_sp->throttle;
            break;

        case MODE_FAILSAFE_LAND:
            arbiter->target_setpoint.roll_cmd = 0.0f;
            arbiter->target_setpoint.pitch_cmd = 0.0f;
            arbiter->target_setpoint.yaw_cmd = state->yaw_deg;
            arbiter->target_setpoint.throttle = 0.40f;
            break;
    }

    // 3. Фільтрація темпу наростання (Slew Rate)
    float max_delta = SLEW_RATE_DEG_S * dt_sec;
    arbiter->active_setpoint.roll_cmd = apply_slew_rate(arbiter->active_setpoint.roll_cmd, 
                                                         arbiter->target_setpoint.roll_cmd, 
                                                         max_delta);
    arbiter->active_setpoint.pitch_cmd = apply_slew_rate(arbiter->active_setpoint.pitch_cmd, 
                                                          arbiter->target_setpoint.pitch_cmd, 
                                                          max_delta);
    arbiter->active_setpoint.yaw_cmd = apply_slew_rate(arbiter->active_setpoint.yaw_cmd, 
                                                        arbiter->target_setpoint.yaw_cmd, 
                                                        max_delta);
    arbiter->active_setpoint.throttle = arbiter->target_setpoint.throttle;
}
```
```cpp
#include <chrono>
#include <algorithm>
#include <cmath>
#include <optional>

namespace FlightStack {

using namespace std::chrono_literals;

enum class ControlMode : uint8_t {
    DirectManual = 0, // 1. Acro / Rate
    AssistedAngle,    // 2. Fly-by-Wire / Stabilize
    SupervisoryAuto,  // 3. Waypoint / Offboard
    FailsafeLand      // Аварійна деградація
};

struct VehicleState {
    float roll_deg{0.0f};
    float pitch_deg{0.0f};
    float yaw_deg{0.0f};
    float rate_roll_deg_s{0.0f};
    float rate_pitch_deg_s{0.0f};
    float rate_yaw_deg_s{0.0f};
};

struct ControlSetpoint {
    float roll{0.0f};
    float pitch{0.0f};
    float yaw{0.0f};
    float throttle{0.0f};
};

class ModeArbiter {
public:
    static constexpr float kMaxRateDegS    = 360.0f;
    static constexpr float kMaxAngleDeg   = 45.0f;
    static constexpr float kSlewRateDegS  = 180.0f;
    static constexpr auto kRcTimeout      = 500ms;
    static constexpr auto kOffboardTimeout = 1000ms;

    explicit ModeArbiter() = default;

    bool requestMode(ControlMode new_mode, const VehicleState& state) noexcept {
        if (current_mode_ == new_mode) {
            return true;
        }

        // Безударний перехід: занулення розриву уставки
        if (new_mode == ControlMode::DirectManual) {
            active_setpoint_.roll  = state.rate_roll_deg_s;
            active_setpoint_.pitch = state.rate_pitch_deg_s;
            active_setpoint_.yaw   = state.rate_yaw_deg_s;
        } else if (new_mode == ControlMode::AssistedAngle || 
                   new_mode == ControlMode::SupervisoryAuto) {
            active_setpoint_.roll  = std::clamp(state.roll_deg, -kMaxAngleDeg, kMaxAngleDeg);
            active_setpoint_.pitch = std::clamp(state.pitch_deg, -kMaxAngleDeg, kMaxAngleDeg);
            active_setpoint_.yaw   = state.yaw_deg;
        }

        current_mode_ = new_mode;
        return true;
    }

    void notifyRcPacket(std::chrono::milliseconds now) noexcept {
        last_rc_time_ = now;
    }

    void notifyOffboardPacket(std::chrono::milliseconds now) noexcept {
        last_offboard_time_ = now;
    }

    void update(const VehicleState& state,
                const ControlSetpoint& rc_sp,
                const ControlSetpoint& offboard_sp,
                std::chrono::milliseconds now,
                float dt_sec) noexcept {
        // 1. Перевірка тайм-аутів зв'язку
        const bool rc_valid = (now - last_rc_time_) <= kRcTimeout;
        const bool offboard_valid = (now - last_offboard_time_) <= kOffboardTimeout;

        // 2. Логіка деградації режимів
        if (current_mode_ == ControlMode::SupervisoryAuto && !offboard_valid) {
            if (rc_valid) {
                requestMode(ControlMode::AssistedAngle, state);
            } else {
                requestMode(ControlMode::FailsafeLand, state);
            }
        } else if ((current_mode_ == ControlMode::AssistedAngle || 
                    current_mode_ == ControlMode::DirectManual) && !rc_valid) {
            requestMode(ControlMode::FailsafeLand, state);
        }

        // 3. Формування цільової уставки
        ControlSetpoint target{};
        switch (current_mode_) {
            case ControlMode::DirectManual:
                target.roll     = rc_sp.roll * kMaxRateDegS;
                target.pitch    = rc_sp.pitch * kMaxRateDegS;
                target.yaw      = rc_sp.yaw * kMaxRateDegS;
                target.throttle = rc_sp.throttle;
                break;

            case ControlMode::AssistedAngle:
                target.roll     = rc_sp.roll * kMaxAngleDeg;
                target.pitch    = rc_sp.pitch * kMaxAngleDeg;
                target.yaw      = rc_sp.yaw * kMaxRateDegS;
                target.throttle = rc_sp.throttle;
                break;

            case ControlMode::SupervisoryAuto:
                target.roll     = std::clamp(offboard_sp.roll, -kMaxAngleDeg, kMaxAngleDeg);
                target.pitch    = std::clamp(offboard_sp.pitch, -kMaxAngleDeg, kMaxAngleDeg);
                target.yaw      = offboard_sp.yaw;
                target.throttle = offboard_sp.throttle;
                break;

            case ControlMode::FailsafeLand:
                target.roll     = 0.0f;
                target.pitch    = 0.0f;
                target.yaw      = state.yaw_deg;
                target.throttle = 0.40f; // Контрольована швидкість спуску
                break;
        }

        // 4. Плавний фільтр наростання уставки (Slew-rate limiting)
        const float max_delta = kSlewRateDegS * dt_sec;
        active_setpoint_.roll     = applySlewRate(active_setpoint_.roll, target.roll, max_delta);
        active_setpoint_.pitch    = applySlewRate(active_setpoint_.pitch, target.pitch, max_delta);
        active_setpoint_.yaw      = applySlewRate(active_setpoint_.yaw, target.yaw, max_delta);
        active_setpoint_.throttle = target.throttle;
    }

    [[nodiscard]] ControlMode currentMode() const noexcept { return current_mode_; }
    [[nodiscard]] const ControlSetpoint& activeSetpoint() const noexcept { return active_setpoint_; }

private:
    static float applySlewRate(float current, float target, float max_delta) noexcept {
        const float error = target - current;
        if (std::abs(error) <= max_delta) {
            return target;
        }
        return current + (error > 0.0f ? max_delta : -max_delta);
    }

    ControlMode current_mode_{ControlMode::AssistedAngle};
    ControlSetpoint active_setpoint_{};
    std::chrono::milliseconds last_rc_time_{0};
    std::chrono::milliseconds last_offboard_time_{0};
};

} // namespace FlightStack
```
:::

## Аналіз механізму безударного переходу

Розберімо покрокову послідовність дій під час переходу з режиму наглядового керування `MODE_SUPERVISORY_AUTO` у допоміжний ручний режим `MODE_ASSISTED_ANGLE`:

1. **Захоплення поточного фізичного кута:** У момент спрацювання тумблера функція `mode_arbiter_request_mode()` зчитує поточні оцінені кути нахилу дрона з розширеного фільтра Калмана EKF (`state->roll_deg`, `state->pitch_deg`) і негайно записує їх у поле `active_setpoint`. Якщо дрон у цей момент мав нахил 20° праворуч для подолання бокового вітру, активна уставка починає свій рух саме з 20°, а не з нуля.
2. **Фільтрація швидкості зміни уставки (Slew Rate):** Протягом наступних тактів головного циклу (частота 100–250 Гц) функція `apply_slew_rate()` щотакту змінює активну уставку в бік поточної команди пілота не швидше ніж на `SLEW_RATE_DEG_S · dt` градусів за такт. Якщо максимальна швидкість становить 180°/с, то кутова невідповідність у 20° плавно зводиться до нуля за 110 мс. Для пілота перехід відчувається як пружне й передбачуване взяття керування під контроль, без жодного ривка чи провалу по висоті.
3. **Демпфування та очищення інтеграторів PID:** При виклику `request_mode` арбітр надсилає подію в контури стабілізації, де виконується скидання або синхронізація інтегральних накопичувачів. Для кутового контуру інтегратор обнуляється, а для швидкісного контуру `I_term` попередньо ініціалізується величиною поточного статичного моменту моторів (*feedforward balance*), щоб завадити раптовому перекосу при відключенні автоматичного горизонту.

## Обробка нечутливої зони стіків (Stick Deadband)

У практичній реалізації польотних стеків (ArduPilot / PX4) важливу роль відіграє захист від випадкового переривання автономної місії через джитер потенціометрів пульта. Для цього навколо нейтрального положення стіка вводиться нечутлива зона (*deadband*), яка зазвичай становить 5–8% від повного ходу (наприклад, у діапазоні ШІМ від 1460 до 1540 мкс при нейтралі 1500 мкс).

Коли дрон перебуває в режимі наглядового керування `MODE_SUPERVISORY_AUTO`, будь-які мікрорухи стіків у межах мертвої зони повністю ігноруються. Однак щойно оператор свідомо відхиляє стік за межі мертвої зони (понад 1550 мкс або менше 1450 мкс), спрацьовує механізм пріоритетного перехоплення (*Pilot Stick Override*): арбітр фіксує активну дію людини й миттєво ініціює безударний перехід у режим `MODE_ASSISTED_ANGLE`, призупиняючи виконання місії та повертаючи контроль пілотові.

## Крайові випадки та ієрархія аварійної деградації

Арбітр реалізує сувору ієрархію пріоритетів безпеки при виникненні аномалій у каналах зв'язку:

- **Джитер та поодинока втрата пакетів від бортового комп'ютера:** Якщо повідомлення протоколу MAVLink (`SET_POSITION_TARGET_LOCAL_NED`) по шині UART/Ethernet запізнюється на 50–100 мс через навантаження процесора комп'ютера компаньйона, арбітр не перемикає режим панічно, оскільки поріг тайм-ауту встановлено на 1000 мс. Протягом цього вікна дрон продовжує рух за раніше розрахованою екстрапольованою траєкторією.
- **Повне зависання або відмова бортового комп'ютера:** Після 1000 мс відсутності оновлень арбітр автоматично деградує в режим `MODE_ASSISTED_ANGLE`, якщо надходить валідний сигнал з пульта оператора. Дрон автоматично вирівнюється в горизонт і зависає на поточній висоті, сповіщаючи оператора повідомленням MAVLink `STATUSTEXT ("Failsafe: Offboard lost, switched to Angle")`.
- **Одночасна втрата пульта та бортового лінка:** Якщо обидва джерела команд мовчать, арбітр переходить у безумовний режим `MODE_FAILSAFE_LAND`, спрямовуючи уставки кутів у нуль і встановлюючи тягу на рівень контрольованого спуску (40%), що запобігає неконтрольованому відльоту (*flyaway*).
- **Повернення зв'язку після збою:** Якщо після аварійної деградації зв'язок із пультом або бортовим комп'ютером відновлюється, арбітр **не повертається автоматично** у високорівневий режим. Повернення в автономний режим вимагає явного підтвердження від оператора (скидання та повторне вмикання тумблера режимів на пульті або надсилання команди з GCS), що виключає неочікувані маневри напівживого апарата.
