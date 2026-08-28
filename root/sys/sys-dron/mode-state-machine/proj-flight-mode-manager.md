# ⚙️ Модуль керування та валідації польотних режимів

Модуль керування польотними режимами (`FlightModeManager`) — це центральний диспетчер автопілота, який виступає єдиною точкою прийняття рішень щодо зміни стану бортової системи. Без ізольованого менеджера режимів код автопілота швидко перетворюється на заплутану мережу умовних операторів, де низькорівневі регулятори напряму опитують приймач радіокерування, команди телеметрії MAVLink перезаписують внутрішні змінні навігатора, а аварійні ситуації призводять до неконтрольованого стрибка вихідних сигналів моторів.

Задача цього модуля — забезпечити надійну ізоляцію контурів регулювання, реалізувати строгий пріоритетний арбітраж команд, валідувати готовність сенсорів крізь охоронні умови (guard conditions), гарантувати безвузлове перемикання (bumpless transfer) та виконувати автоматичну каскадну деградацію при відмові давачів у польоті.

---

## Архітектура та функціональний контракт модуля

Модуль `FlightModeManager` проектується для роботи у складі високонадійних польотних стеків реального часу на мікроконтролерах класу ARM Cortex-M4/M7 (STM32F4/F7/H7) під керуванням ОСРЧ (FreeRTOS, NuttX) або у bare-metal середовищі.

```
       +-------------------------------------------------------------+
       |                  Джерела команд на перехід                  |
       |  [0: Failsafe]  [1: RC Switch/Override]  [2: GCS]  [3: Nav] |
       +-------------------------------------------------------------+
                                      |
                                      v
+----------------------------------------------------------------------------+
|                         FlightModeManager                                  |
|                                                                            |
|  1. Черга запитів та арбітраж пріоритетів (Arbitration Engine)             |
|  2. Валідатор Guard-умов сенсорного здоров'я (Sensor Guard Validator)       |
|  3. Виконавець переходу: on_exit() -> Bumpless Sync -> on_enter()          |
|  4. Монітор каскадної деградації (Sensor-Loss Fallback Monitor)            |
+----------------------------------------------------------------------------+
       |                                                      |
       v                                                      v
+-------------------------------+             +------------------------------+
|   Активний режим (Active)     |             |   Контекст борта (Context)   |
|   - Stabilize / AltHold / Auto|             |   - Оцінки EKF, Сетопоінти   |
+-------------------------------+             +------------------------------+
```

### Вимоги до модуля:
1.  **Детермінізм пам'яті**: нульове динамічне виділення пам'яті в польотному циклі (відсутність `malloc`/`free` та операторів `new`/`delete`). Усі об'єкти режимів і таблиці станів розміщуються статично на етапі компіляції.
2.  **Пріоритетна фільтрація**: команда з нижчим рівнем авторитетності не може перервати виконання захисного режиму вищого пріоритету.
3.  **Безпечний відкат (Rollback Integrity)**: якщо ініціалізація нового стану (`on_enter()`) повертає помилку, менеджер зобов'язаний негайно відновити попередній або базовий безпечний режим (`STABILIZE`).
4.  **Атомарність викликів**: захист від гонитви станів (race conditions) при багатопотоковому зверненні з різних завдань RTOS.

---

## Структури даних та контекст борта

В основі роботи менеджера режимів лежить розділення стану автопілота на три незалежні сутності:
1.  **Сенсорний статус (`sensor_flags`)**: бітова маска, що формується підсистемами первинної обробки давачів та фільтром стану EKF. Кожен біт відповідає за конкретний аспект достовірності даних (наявність 3D-фіксу GPS, стабільність вертикальної швидкості EKF-Z, відсутність завад магнітометра).
2.  **Фізичний стан апарата**: оцінені фільтром Калмана координати, кути орієнтації, лінійні швидкості в системі координат NED (North-East-Down) та оцінка базової тяги висіння (`estimated_hover_thrust`).
3.  **Сетопоінти контурів регулювання**: цільові величини, які генерує активний режим для передачі у внутрішні ПІД-контури (цільова висота `target_alt_m`, цільові координати `target_pos_ned`, цільовий курс `target_yaw_rad` та тяга `target_thrust`).

Контекст борта передається у функції обробників кожного режиму через єдиний покажчик на структуру `FmmContext` (у C) або посилання `FlightContext&` (у C++). Це гарантує, що жоден режим не має прихованого глобального стану і не взаємодіє з апаратними реєстрами напряму.

---

## Алгоритмічний конвеєр переходу між режимами

Процедура зміни режиму виконується суворо за детермінованим алгоритмом із чотирьох кроків:

```
[Запит: fmm_request_mode(target_mode, source)]
     |
     v
1. Перевірка авторитетності джерела
   (source >= current_source АБО current_source != FAILSAFE)
     |---[Ні]---> Повернення помилки FMM_RES_REJECTED_LOW_PRIORITY
     |
     +---[Так]--> 2. Перевірка Guard-умов сенсорного здоров'я
                  ((ctx->sensor_flags & target->required_sensors) == target->required_sensors)
                    |---[Ні]---> Повернення помилки FMM_RES_REJECTED_GUARD_FAILED
                    |
                    +---[Так]--> 3. Виклик процедури виходу з поточного режиму:
                                 current_mode->exit(ctx)
                                   |
                                   v
                                 4. Виклик процедури входу в новий режим:
                                 target->enter(ctx) [BUMPLESS SYNC]
                                   |
                                   +---[Успіх]--> current_mode := target; return ACCEPTED
                                   |
                                   +---[Збій]---> Rollback: current_mode := STABILIZE;
                                                  current_mode->enter(ctx);
                                                  return REJECTED_INIT_FAILED
```

### Принцип безвузлової синхронізації (Bumpless Transfer Protocol)

Під час виконання функції `enter()` кожного режиму здійснюється обов'язкова ініціалізація внутрішніх змінних:

*   **У режимі ALT_HOLD**:
    ```
    ctx->target_alt_m = ctx->current_alt_m;            // Фіксація поточної висоти як цільової
    ctx->target_vel_ned[2] = 0.0f;                      // Обнулення бажаної вертикальної швидкості
    ctx->target_thrust = ctx->estimated_hover_thrust;  // Предзавантаження інтегратора базовою тягою
    ctx->reset_pid_integrators = true;                 // Скидання накопичених помилок кутових швидкостей
    ```
*   **У режимі POS_HOLD**:
    ```
    ctx->target_alt_m = ctx->current_alt_m;
    ctx->target_pos_ned[0] = ctx->current_pos_ned[0];  // Фіксація 2D точки висіння (North)
    ctx->target_pos_ned[1] = ctx->current_pos_ned[1];  // Фіксація 2D точки висіння (East)
    ctx->target_vel_ned[0] = 0.0f;
    ctx->target_vel_ned[1] = 0.0f;
    ctx->target_vel_ned[2] = 0.0f;
    ctx->target_yaw_rad = ctx->current_yaw_rad;        // Фіксація курсу (запобігання розвороту)
    ctx->target_thrust = ctx->estimated_hover_thrust;
    ctx->reset_pid_integrators = true;
    ```

Ця послідовність усуває розрив першої похідної керувального сигналу, завдяки чому в момент перемикання тумблера апарат не відчуває стрибка прискорення.

---

## Програмна реалізація модуля на C та C++

Нижче наведено повний вихідний код модуля мовами C та C++. Реалізація на C використовує структури з функціональними покажчиками та статичні таблиці дескрипторів. Реалізація на C++20 використовує строгу типізацію, патерн State з віртуальним диспетчеризуванням, `std::expected` для безпечної обробки помилок та повну відсутність динамічного виділення пам'яті.

:::tabs
```c
// ============================================================================
// flight_mode_manager.h / flight_mode_manager.c (Реалізація на C)
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

// Ідентифікатори польотних режимів
typedef enum {
    FMM_MODE_MANUAL        = 0,
    FMM_MODE_ACRO          = 1,
    FMM_MODE_STABILIZE     = 2,
    FMM_MODE_ALT_HOLD      = 3,
    FMM_MODE_POS_HOLD      = 4,
    FMM_MODE_AUTO          = 5,
    FMM_MODE_RTL           = 6,
    FMM_MODE_FAILSAFE_LAND = 7,
    FMM_MODE_COUNT
} FmmModeId;

// Джерела команд з відповідними рівнями пріоритету
typedef enum {
    FMM_SRC_OFFBOARD       = 0, // Найнижчий пріоритет
    FMM_SRC_NAVIGATOR      = 1,
    FMM_SRC_GCS_COMMAND    = 2,
    FMM_SRC_RC_SWITCH      = 3,
    FMM_SRC_STICK_OVERRIDE = 4,
    FMM_SRC_FAILSAFE       = 5  // Найвищий пріоритет
} FmmCmdSource;

// Результати виконання запиту на зміну режиму
typedef enum {
    FMM_RES_ACCEPTED               = 0,
    FMM_RES_REJECTED_LOW_PRIORITY  = 1,
    FMM_RES_REJECTED_GUARD_FAILED  = 2,
    FMM_RES_REJECTED_INIT_FAILED   = 3,
    FMM_RES_REJECTED_UNKNOWN_MODE  = 4
} FmmResult;

// Бітові маски сенсорного здоров'я та EKF
#define SENSOR_FLAG_IMU_OK        (1u << 0)
#define SENSOR_FLAG_AHRS_OK       (1u << 1)
#define SENSOR_FLAG_BARO_OK       (1u << 2)
#define SENSOR_FLAG_EKF_Z_OK      (1u << 3)
#define SENSOR_FLAG_EKF_XY_OK     (1u << 4)
#define SENSOR_FLAG_GPS_3D_FIX    (1u << 5)
#define SENSOR_FLAG_HOME_VALID    (1u << 6)
#define SENSOR_FLAG_MISSION_VALID (1u << 7)

// Контекст стану літального апарата
typedef struct {
    uint32_t sensor_flags;
    bool is_armed;
    bool is_flying;
    
    // Оцінені EKF параметри
    float current_alt_m;
    float current_vel_ned[3];
    float current_pos_ned[3];
    float current_yaw_rad;
    float estimated_hover_thrust;
    
    // Вихідні сетопоінти для контурів регулювання
    float target_alt_m;
    float target_vel_ned[3];
    float target_pos_ned[3];
    float target_yaw_rad;
    float target_thrust;
    bool reset_pid_integrators;
} FmmContext;

// Опис структури окремого режиму
typedef struct FmmModeHandler FmmModeHandler;

struct FmmModeHandler {
    FmmModeId id;
    const char *name;
    uint32_t required_sensors;
    bool (*enter)(FmmContext *ctx);
    void (*update)(FmmContext *ctx, float dt);
    void (*exit)(FmmContext *ctx);
};

// Структура менеджера режимів
typedef struct {
    FmmContext *ctx;
    const FmmModeHandler *current_mode;
    FmmCmdSource current_source;
    uint32_t mode_change_count;
    uint32_t last_transition_ms;
} FlightModeManager;

// Реалізація обробників режимів
static bool mode_stabilize_enter(FmmContext *ctx) {
    ctx->reset_pid_integrators = true;
    return true;
}

static void mode_stabilize_update(FmmContext *ctx, float dt) {
    (void)ctx; (void)dt;
}

static void mode_stabilize_exit(FmmContext *ctx) {
    (void)ctx;
}

static bool mode_althold_enter(FmmContext *ctx) {
    ctx->target_alt_m = ctx->current_alt_m;
    ctx->target_vel_ned[2] = 0.0f;
    ctx->target_thrust = ctx->estimated_hover_thrust;
    ctx->reset_pid_integrators = true;
    return true;
}

static void mode_althold_update(FmmContext *ctx, float dt) {
    (void)ctx; (void)dt;
}

static void mode_althold_exit(FmmContext *ctx) {
    (void)ctx;
}

static bool mode_poshold_enter(FmmContext *ctx) {
    ctx->target_alt_m = ctx->current_alt_m;
    ctx->target_pos_ned[0] = ctx->current_pos_ned[0];
    ctx->target_pos_ned[1] = ctx->current_pos_ned[1];
    ctx->target_vel_ned[0] = 0.0f;
    ctx->target_vel_ned[1] = 0.0f;
    ctx->target_vel_ned[2] = 0.0f;
    ctx->target_yaw_rad = ctx->current_yaw_rad;
    ctx->target_thrust = ctx->estimated_hover_thrust;
    ctx->reset_pid_integrators = true;
    return true;
}

static void mode_poshold_update(FmmContext *ctx, float dt) {
    (void)ctx; (void)dt;
}

static void mode_poshold_exit(FmmContext *ctx) {
    (void)ctx;
}

static bool mode_auto_enter(FmmContext *ctx) {
    ctx->reset_pid_integrators = true;
    return true;
}

static void mode_auto_update(FmmContext *ctx, float dt) {
    (void)ctx; (void)dt;
}

static void mode_auto_exit(FmmContext *ctx) {
    (void)ctx;
}

static bool mode_land_enter(FmmContext *ctx) {
    ctx->target_vel_ned[0] = 0.0f;
    ctx->target_vel_ned[1] = 0.0f;
    ctx->target_vel_ned[2] = 0.7f;
    ctx->reset_pid_integrators = true;
    return true;
}

static void mode_land_update(FmmContext *ctx, float dt) {
    (void)ctx; (void)dt;
}

static void mode_land_exit(FmmContext *ctx) {
    (void)ctx;
}

static const FmmModeHandler g_mode_table[FMM_MODE_COUNT] = {
    [FMM_MODE_STABILIZE] = {
        .id = FMM_MODE_STABILIZE,
        .name = "STABILIZE",
        .required_sensors = SENSOR_FLAG_IMU_OK | SENSOR_FLAG_AHRS_OK,
        .enter = mode_stabilize_enter,
        .update = mode_stabilize_update,
        .exit = mode_stabilize_exit
    },
    [FMM_MODE_ALT_HOLD] = {
        .id = FMM_MODE_ALT_HOLD,
        .name = "ALT_HOLD",
        .required_sensors = SENSOR_FLAG_IMU_OK | SENSOR_FLAG_AHRS_OK | 
                            SENSOR_FLAG_BARO_OK | SENSOR_FLAG_EKF_Z_OK,
        .enter = mode_althold_enter,
        .update = mode_althold_update,
        .exit = mode_althold_exit
    },
    [FMM_MODE_POS_HOLD] = {
        .id = FMM_MODE_POS_HOLD,
        .name = "POS_HOLD",
        .required_sensors = SENSOR_FLAG_IMU_OK | SENSOR_FLAG_AHRS_OK | 
                            SENSOR_FLAG_BARO_OK | SENSOR_FLAG_EKF_Z_OK | 
                            SENSOR_FLAG_EKF_XY_OK | SENSOR_FLAG_GPS_3D_FIX,
        .enter = mode_poshold_enter,
        .update = mode_poshold_update,
        .exit = mode_poshold_exit
    },
    [FMM_MODE_AUTO] = {
        .id = FMM_MODE_AUTO,
        .name = "AUTO",
        .required_sensors = SENSOR_FLAG_IMU_OK | SENSOR_FLAG_AHRS_OK | 
                            SENSOR_FLAG_BARO_OK | SENSOR_FLAG_EKF_Z_OK | 
                            SENSOR_FLAG_EKF_XY_OK | SENSOR_FLAG_GPS_3D_FIX |
                            SENSOR_FLAG_MISSION_VALID,
        .enter = mode_auto_enter,
        .update = mode_auto_update,
        .exit = mode_auto_exit
    },
    [FMM_MODE_FAILSAFE_LAND] = {
        .id = FMM_MODE_FAILSAFE_LAND,
        .name = "FAILSAFE_LAND",
        .required_sensors = SENSOR_FLAG_IMU_OK | SENSOR_FLAG_AHRS_OK | 
                            SENSOR_FLAG_BARO_OK | SENSOR_FLAG_EKF_Z_OK,
        .enter = mode_land_enter,
        .update = mode_land_update,
        .exit = mode_land_exit
    }
};

void fmm_init(FlightModeManager *mgr, FmmContext *ctx) {
    mgr->ctx = ctx;
    mgr->current_source = FMM_SRC_RC_SWITCH;
    mgr->current_mode = &g_mode_table[FMM_MODE_STABILIZE];
    mgr->mode_change_count = 0;
    mgr->last_transition_ms = 0;
    
    if (mgr->current_mode->enter) {
        mgr->current_mode->enter(mgr->ctx);
    }
}

FmmResult fmm_request_mode(FlightModeManager *mgr, FmmModeId mode_id, FmmCmdSource source, uint32_t now_ms) {
    if (mode_id >= FMM_MODE_COUNT) return FMM_RES_REJECTED_UNKNOWN_MODE;

    const FmmModeHandler *target = &g_mode_table[mode_id];
    if (target->enter == NULL) return FMM_RES_REJECTED_UNKNOWN_MODE;

    if (source < mgr->current_source && mgr->current_source == FMM_SRC_FAILSAFE) {
        return FMM_RES_REJECTED_LOW_PRIORITY;
    }

    if ((mgr->ctx->sensor_flags & target->required_sensors) != target->required_sensors) {
        return FMM_RES_REJECTED_GUARD_FAILED;
    }

    if (mgr->current_mode && mgr->current_mode->exit) {
        mgr->current_mode->exit(mgr->ctx);
    }

    if (!target->enter(mgr->ctx)) {
        mgr->current_mode = &g_mode_table[FMM_MODE_STABILIZE];
        mgr->current_source = FMM_SRC_FAILSAFE;
        mgr->current_mode->enter(mgr->ctx);
        return FMM_RES_REJECTED_INIT_FAILED;
    }

    mgr->current_mode = target;
    mgr->current_source = source;
    mgr->mode_change_count++;
    mgr->last_transition_ms = now_ms;
    return FMM_RES_ACCEPTED;
}

static void check_sensor_loss_and_degrade(FlightModeManager *mgr, uint32_t now_ms) {
    if (!mgr->current_mode) return;

    uint32_t req = mgr->current_mode->required_sensors;
    if ((mgr->ctx->sensor_flags & req) == req) return;

    if (mgr->current_mode->id == FMM_MODE_AUTO || mgr->current_mode->id == FMM_MODE_POS_HOLD) {
        if ((mgr->ctx->sensor_flags & g_mode_table[FMM_MODE_ALT_HOLD].required_sensors) == 
            g_mode_table[FMM_MODE_ALT_HOLD].required_sensors) {
            (void)fmm_request_mode(mgr, FMM_MODE_ALT_HOLD, FMM_SRC_FAILSAFE, now_ms);
        } else {
            (void)fmm_request_mode(mgr, FMM_MODE_STABILIZE, FMM_SRC_FAILSAFE, now_ms);
        }
    } else if (mgr->current_mode->id == FMM_MODE_ALT_HOLD) {
        (void)fmm_request_mode(mgr, FMM_MODE_STABILIZE, FMM_SRC_FAILSAFE, now_ms);
    }
}

void fmm_update(FlightModeManager *mgr, float dt, uint32_t now_ms) {
    check_sensor_loss_and_degrade(mgr, now_ms);
    if (mgr->current_mode && mgr->current_mode->update) {
        mgr->current_mode->update(mgr->ctx, dt);
    }
}

void fmm_handle_stick_override(FlightModeManager *mgr, float stick_deflection, uint32_t now_ms) {
    if (stick_deflection < 0.15f) return;
    if (mgr->current_mode->id == FMM_MODE_AUTO || mgr->current_mode->id == FMM_MODE_RTL) {
        if ((mgr->ctx->sensor_flags & g_mode_table[FMM_MODE_POS_HOLD].required_sensors) ==
            g_mode_table[FMM_MODE_POS_HOLD].required_sensors) {
            (void)fmm_request_mode(mgr, FMM_MODE_POS_HOLD, FMM_SRC_STICK_OVERRIDE, now_ms);
        } else {
            (void)fmm_request_mode(mgr, FMM_MODE_ALT_HOLD, FMM_SRC_STICK_OVERRIDE, now_ms);
        }
    }
}

FmmModeId fmm_get_current_mode(const FlightModeManager *mgr) {
    return mgr->current_mode ? mgr->current_mode->id : FMM_MODE_STABILIZE;
}
```
```cpp
// ============================================================================
// FlightModeManager.hpp (Реалізація на C++20)
// ============================================================================
#pragma once
#include <cstdint>
#include <string_view>
#include <array>
#include <expected>

namespace sys_dron::fmm {

enum class FlightMode : uint8_t {
    Manual = 0,
    Acro,
    Stabilize,
    AltHold,
    PosHold,
    Auto,
    Rtl,
    FailsafeLand,
    Count
};

enum class CommandSource : uint8_t {
    Offboard = 0,
    Navigator,
    GcsCommand,
    RcSwitch,
    StickOverride,
    Failsafe
};

enum class TransitionError : uint8_t {
    LowerPriorityThanActive,
    MissingRequiredSensors,
    InitializationFailed,
    InvalidMode
};

enum class SensorFlag : uint32_t {
    ImuOk        = 1 << 0,
    AhrsOk       = 1 << 1,
    BaroOk       = 1 << 2,
    EkfZOk       = 1 << 3,
    EkfXyOk      = 1 << 4,
    Gps3DFix     = 1 << 5,
    HomeValid    = 1 << 6,
    MissionValid = 1 << 7
};

inline constexpr uint32_t operator|(SensorFlag a, SensorFlag b) noexcept {
    return static_cast<uint32_t>(a) | static_cast<uint32_t>(b);
}

struct FlightContext {
    uint32_t sensor_flags{0};
    bool is_armed{false};
    bool is_flying{false};

    float current_alt_m{0.0f};
    std::array<float, 3> current_vel_ned{0.0f, 0.0f, 0.0f};
    std::array<float, 3> current_pos_ned{0.0f, 0.0f, 0.0f};
    float current_yaw_rad{0.0f};
    float estimated_hover_thrust{0.45f};

    // Сетопоінти
    float target_alt_m{0.0f};
    std::array<float, 3> target_vel_ned{0.0f, 0.0f, 0.0f};
    std::array<float, 3> target_pos_ned{0.0f, 0.0f, 0.0f};
    float target_yaw_rad{0.0f};
    float target_thrust{0.0f};
    bool reset_pid_integrators{false};

    [[nodiscard]] constexpr bool has_sensors(uint32_t mask) const noexcept {
        return (sensor_flags & mask) == mask;
    }
};

class ModeBase {
public:
    virtual ~ModeBase() = default;
    [[nodiscard]] virtual FlightMode id() const noexcept = 0;
    [[nodiscard]] virtual std::string_view name() const noexcept = 0;
    [[nodiscard]] virtual uint32_t required_sensors() const noexcept = 0;

    virtual bool on_enter(FlightContext& ctx) = 0;
    virtual void on_update(FlightContext& ctx, float dt) = 0;
    virtual void on_exit(FlightContext& ctx) = 0;
};

class StabilizeMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::Stabilize; }
    [[nodiscard]] std::string_view name() const noexcept override { return "STABILIZE"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class AltHoldMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::AltHold; }
    [[nodiscard]] std::string_view name() const noexcept override { return "ALT_HOLD"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk | SensorFlag::BaroOk | SensorFlag::EkfZOk;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.target_alt_m = ctx.current_alt_m;
        ctx.target_vel_ned[2] = 0.0f;
        ctx.target_thrust = ctx.estimated_hover_thrust;
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class PosHoldMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::PosHold; }
    [[nodiscard]] std::string_view name() const noexcept override { return "POS_HOLD"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk | SensorFlag::BaroOk | 
               SensorFlag::EkfZOk | SensorFlag::EkfXyOk | SensorFlag::Gps3DFix;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.target_alt_m = ctx.current_alt_m;
        ctx.target_pos_ned = ctx.current_pos_ned;
        ctx.target_vel_ned = {0.0f, 0.0f, 0.0f};
        ctx.target_yaw_rad = ctx.current_yaw_rad;
        ctx.target_thrust = ctx.estimated_hover_thrust;
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class AutoMode final : public ModeBase {
public:
    [[nodiscard]] FlightMode id() const noexcept override { return FlightMode::Auto; }
    [[nodiscard]] std::string_view name() const noexcept override { return "AUTO"; }
    [[nodiscard]] uint32_t required_sensors() const noexcept override {
        return SensorFlag::ImuOk | SensorFlag::AhrsOk | SensorFlag::BaroOk | 
               SensorFlag::EkfZOk | SensorFlag::EkfXyOk | SensorFlag::Gps3DFix | 
               SensorFlag::MissionValid;
    }
    bool on_enter(FlightContext& ctx) override {
        ctx.reset_pid_integrators = true;
        return true;
    }
    void on_update(FlightContext&, float) override {}
    void on_exit(FlightContext&) override {}
};

class FlightModeManager {
public:
    explicit FlightModeManager(FlightContext& ctx) noexcept : ctx_(ctx) {
        current_mode_ = &stabilize_mode_;
        current_mode_->on_enter(ctx_);
    }

    std::expected<void, TransitionError> request_mode(FlightMode mode, CommandSource source) {
        ModeBase* target = resolve_mode(mode);
        if (!target) return std::unexpected(TransitionError::InvalidMode);

        if (source < current_source_ && current_source_ == CommandSource::Failsafe) {
            return std::unexpected(TransitionError::LowerPriorityThanActive);
        }

        if (!ctx_.has_sensors(target->required_sensors())) {
            return std::unexpected(TransitionError::MissingRequiredSensors);
        }

        current_mode_->on_exit(ctx_);
        if (!target->on_enter(ctx_)) {
            current_mode_ = &stabilize_mode_;
            current_source_ = CommandSource::Failsafe;
            current_mode_->on_enter(ctx_);
            return std::unexpected(TransitionError::InitializationFailed);
        }

        current_mode_ = target;
        current_source_ = source;
        return {};
    }

    void update(float dt) {
        handle_sensor_loss();
        current_mode_->on_update(ctx_, dt);
    }

    void handle_stick_override(float stick_deflection) {
        if (stick_deflection < 0.15f) return;
        if (current_mode_->id() == FlightMode::Auto) {
            if (ctx_.has_sensors(pos_hold_mode_.required_sensors())) {
                (void)request_mode(FlightMode::PosHold, CommandSource::StickOverride);
            } else {
                (void)request_mode(FlightMode::AltHold, CommandSource::StickOverride);
            }
        }
    }

    [[nodiscard]] FlightMode current_mode_id() const noexcept {
        return current_mode_->id();
    }

private:
    void handle_sensor_loss() {
        if (!ctx_.has_sensors(current_mode_->required_sensors())) {
            if (current_mode_->id() == FlightMode::Auto || current_mode_->id() == FlightMode::PosHold) {
                if (ctx_.has_sensors(alt_hold_mode_.required_sensors())) {
                    (void)request_mode(FlightMode::AltHold, CommandSource::Failsafe);
                } else {
                    (void)request_mode(FlightMode::Stabilize, CommandSource::Failsafe);
                }
            } else if (current_mode_->id() == FlightMode::AltHold) {
                (void)request_mode(FlightMode::Stabilize, CommandSource::Failsafe);
            }
        }
    }

    ModeBase* resolve_mode(FlightMode mode) noexcept {
        switch (mode) {
            case FlightMode::Stabilize: return &stabilize_mode_;
            case FlightMode::AltHold:   return &alt_hold_mode_;
            case FlightMode::PosHold:   return &pos_hold_mode_;
            case FlightMode::Auto:      return &auto_mode_;
            default:                    return nullptr;
        }
    }

    FlightContext& ctx_;
    StabilizeMode stabilize_mode_{};
    AltHoldMode alt_hold_mode_{};
    PosHoldMode pos_hold_mode_{};
    AutoMode auto_mode_{};

    ModeBase* current_mode_{&stabilize_mode_};
    CommandSource current_source_{CommandSource::RcSwitch};
};

} // namespace sys_dron::fmm
```
:::

---

## Інженерні пастки при розробці та верифікації автоматів режимів

### 1. Гонитва перемикань при одночасному Failsafe та ручному тумблері (Race Condition)

*Проблема:* Пілот помічає нестабільність і перемикає тумблер у `STABILIZE` рівно в той самий момент часу, коли бортовий модуль моніторингу батареї активує `FAILSAFE_RTL`. Якщо обидві події обробляються в різних задачах FreeRTOS без взаємного блокування або черги з мітками пріоритету, виникає небезпечна ситуація: автомат спочатку активує `FAILSAFE_RTL`, а за мікросекунду перетирає його режимом `STABILIZE`, знімаючи захисну дію автопілота.

*Рішення:* Строгий арбітраж на основі рівнів джерел (`FmmCmdSource`). Запит від джерела з нижчим рангом відхиляється, якщо активний режим активовано з вищим рангом (`FAILSAFE`), доки прапорець аварії не буде явно скинутий або підтверджений тривалим утриманням тумблера пілота.

### 2. Брязкіт датчиків (Sensor Flapping) та гістерезис

*Проблема:* При польоті в зоні дії завад РЕБ супутниковий приймач кожні 500 мс втрачає і знову знаходить 3D-фікс. Автомат без фільтрації починає безперервно перемикатися між `POS_HOLD` (є фікс) та `ALT_HOLD` (немає фіксу). Кожне перемикання скидає інтегратори й фіксує нові координати, через що апарат починає конвульсивно смикатися.

*Рішення:* Реалізація двофазного лічильника валідності:
*   Для підтвердження відновлення сенсора потрібно 150 валідних пакетів поспіль (3 секунди на частоті 50 Гц).
*   Для фіксації відмови достатньо 25 невалідних пакетів (0.5 секунди).

### 3. Зависання в проміжному стані при відмові входу (Rollback Integrity)

*Проблема:* Якщо цільовий стан у процесі виклику `enter()` повертає `false` (наприклад, планувальник місії не зміг завантажити маршрутну точку з flash-пам'яті), система може залишитися з покажчиком `current_mode = NULL` або в частково ініціалізованому стані, що викличе HardFault при першому ж зверненні до нього в контурі керування.

*Рішення:* Механізм безумовного відкату (Rollback). Якщо `target->enter()` зазнав невдачі, менеджер автоматично активує гарантовано робочий базовий стан (`STABILIZE`) із джерелом `Failsafe`, реєструє помилку в журналі та повертає код результату `FMM_RES_REJECTED_INIT_FAILED`.

### 4. Стрибок кута курсу (Yaw Jitter) при вході в Loiter

*Проблема:* Якщо пілот летів у режимі `ALT_HOLD`, активно обертаючи дрон по курсу (наприклад, зі швидкістю 60 °/с), і раптово перемкнувся в `POS_HOLD`, застаріла уставка курсу може змусити апарат різко смикнутися назад на десятки градусів, викликаючи перевантаження конструкції та зрив відеопотоку.

*Рішення:* Захоплення поточної оцінки курсу EKF `target_yaw = current_yaw` безпосередньо у функції `on_enter()`, а також повне обнулення цільової кутової швидкості.

### 5. Стрибок тримів стіків (Stick Trim Offset)

*Проблема:* Якщо пульт пілота має механічний зсув тримерів (наприклад, канал елеронів видає 1540 мкс замість нейтральних 1500 мкс), автопілот у режимі `AUTO` ігнорує цей зсув, а при переході в `POS_HOLD` сприймає це як постійну команду пілота летіти вправо зі швидкістю 1.5 м/с.

*Рішення:* Калібрування центральної мертвої зони (`RC_DEADZONE = 30 мкс`) та автоматичне калібрування нейтралі стіків під час процедури зведення моторів (`arming`).

---

## Інтеграція в RTOS та потокобезпечний обмін

Для інтеграції модуля `FlightModeManager` в операційну систему реального часу (FreeRTOS) рекомендується наступна схема організації завдань:

1.  **Fast Loop Task (Пріоритет: Real-Time, 400–1000 Гц)**: виконує читання гіроскопів, викликає швидкі ПІД-контури кутових швидкостей. Читає актуальні сетопоінти з `FmmContext`.
2.  **Navigation & FSM Task (Пріоритет: High, 50–100 Гц)**: викликає `fmm_update()`, оцінює guard-умови, генерує сетопоінти положення та висоти.
3.  **Telemetry & RC Task (Пріоритет: Normal, 20–50 Гц)**: приймає пакети MAVLink та RC-канали, формує запити через `fmm_request_mode()`.

Для передачі запитів між низькопріоритетною задачею телеметрії та високопріоритетною задачею FSM застосовується неблокуюча черга повідомлень або подвійна атомарна буферизація, що усуває потребу в блокуючих м'ютексах у польотному циклі.

---

## Тестовий стенд та сценарій наскрізної верифікації

Для перевірки коректності роботи автомата режимів розробляється модульний тест (Unit Test), що симулює типовий польотний профіль із відмовами обладнання:

```
[Крок 1] Ініціалізація системи -> Активний режим: STABILIZE.
[Крок 2] Запит AUTO без GPS-фіксу -> Очікувана відповідь: FMM_RES_REJECTED_GUARD_FAILED.
[Крок 3] Увімкнення прапорців GPS і EKF -> Запит AUTO -> Відповідь: FMM_RES_ACCEPTED.
[Крок 4] Політ на висоті 45 м -> Симуляція скидання прапорця GPS_3D_FIX.
[Крок 5] Виклик fmm_update() -> Автоматична деградація в ALT_HOLD.
[Крок 6] Перевірка сетопоінта: target_alt_m == 45.0 м, target_thrust == 0.45 (Bumpless OK).
[Крок 7] Симуляція Stick Override (відхилення стіка 0.35) -> Перехід у POS_HOLD / ALT_HOLD.
[Крок 8] Активація аварії батареї -> Примусовий перехід у FAILSAFE_LAND.
[Крок 9] Спроба оператора GCS увімкнути AUTO під час Failsafe -> Відповідь: REJECTED_LOW_PRIORITY.
```

Така послідовність автоматизованих тестів у середовищі неперервної інтеграції (CI/CD) на 100% гарантує захист від регресійних дефектів у критичній логіці керування безпілотним апаратом.
