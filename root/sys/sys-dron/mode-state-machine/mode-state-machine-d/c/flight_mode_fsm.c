// flight_mode_fsm.h / flight_mode_fsm.c
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef enum {
    MODE_MANUAL     = 0,
    MODE_ACRO       = 1,
    MODE_STABILIZE  = 2,
    MODE_ALT_HOLD   = 3,
    MODE_POS_HOLD   = 4,
    MODE_AUTO       = 5,
    MODE_FAILSAFE_LAND = 6
} FlightModeId;

// Бітова маска готовності сенсорів
typedef enum {
    SENSOR_IMU_HEALTHY   = (1 << 0),
    SENSOR_AHRS_VALID    = (1 << 1),
    SENSOR_BARO_HEALTHY  = (1 << 2),
    SENSOR_EKF_VERT_OK   = (1 << 3),
    SENSOR_EKF_HORIZ_OK  = (1 << 4),
    SENSOR_GPS_3D_FIX    = (1 << 5),
    SENSOR_HOME_SET      = (1 << 6)
} SensorFlags;

// Контекст телеметрії та стану борта
typedef struct {
    uint32_t sensor_flags;
    float current_alt_m;
    float current_pos_ned[3];
    float current_yaw_rad;
    float estimated_hover_thrust;
    
    // Сетопоінти контуру керування
    float target_alt_m;
    float target_pos_ned[3];
    float target_yaw_rad;
    float target_thrust;
    float rate_integral_reset;
} FlightContext;

// Опис інтерфейсу стану
typedef struct FlightModeState FlightModeState;

struct FlightModeState {
    FlightModeId id;
    uint32_t required_sensors;
    bool (*enter)(FlightContext *ctx);
    void (*update)(FlightContext *ctx, float dt);
    void (*exit)(FlightContext *ctx);
};

// Реалізація обробників режимів
static bool stabilize_enter(FlightContext *ctx) {
    ctx->rate_integral_reset = 1.0f;
    return true;
}

static void stabilize_update(FlightContext *ctx, float dt) {
    (void)ctx; (void)dt;
    // Обчислення кутів від стіків та подача на контур кутових швидкостей
}

static void stabilize_exit(FlightContext *ctx) {
    (void)ctx;
}

// Вхід у режим ALT_HOLD із синхронізацією сетопоінтів (Bumpless Transfer)
static bool althold_enter(FlightContext *ctx) {
    ctx->target_alt_m = ctx->current_alt_m;               // Синхронізація висоти
    ctx->target_thrust = ctx->estimated_hover_thrust;     // Предзавантаження тяги
    ctx->rate_integral_reset = 1.0f;
    return true;
}

static void althold_update(FlightContext *ctx, float dt) {
    (void)ctx; (void)dt;
    // ПІД-регулятор вертикальної швидкості
}

static void althold_exit(FlightContext *ctx) {
    (void)ctx;
}

// Таблиця станів
static const FlightModeState mode_table[] = {
    { MODE_STABILIZE, SENSOR_IMU_HEALTHY | SENSOR_AHRS_VALID, 
      stabilize_enter, stabilize_update, stabilize_exit },
    { MODE_ALT_HOLD,  SENSOR_IMU_HEALTHY | SENSOR_AHRS_VALID | SENSOR_BARO_HEALTHY | SENSOR_EKF_VERT_OK, 
      althold_enter, althold_update, althold_exit }
};

typedef struct {
    const FlightModeState *current_mode;
    FlightContext *ctx;
} ModeManager;

void mode_manager_init(ModeManager *mgr, FlightContext *ctx) {
    mgr->ctx = ctx;
    mgr->current_mode = &mode_table[0]; // Старт у Stabilize
    mgr->current_mode->enter(mgr->ctx);
}

// Спроба перемикання режиму з перевіркою Guard-умов
bool mode_manager_request_mode(ModeManager *mgr, FlightModeId new_mode_id) {
    const FlightModeState *target = NULL;
    for (size_t i = 0; i < sizeof(mode_table) / sizeof(mode_table[0]); ++i) {
        if (mode_table[i].id == new_mode_id) {
            target = &mode_table[i];
            break;
        }
    }
    
    if (target == NULL) return false;

    // Перевірка Guard-умови наявності сенсорів
    if ((mgr->ctx->sensor_flags & target->required_sensors) != target->required_sensors) {
        return false; // Відхилено: бракує обов'язкових давачів
    }

    // Виконання безударного переходу
    mgr->current_mode->exit(mgr->ctx);
    if (!target->enter(mgr->ctx)) {
        // Якщо ініціалізація нового стану провалилася — повернення у базовий стан
        mgr->current_mode = &mode_table[0];
        mgr->current_mode->enter(mgr->ctx);
        return false;
    }

    mgr->current_mode = target;
    return true;
}
