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
