/* profile_controller.h - Керування термопрофілем (C99) */
#ifndef PROFILE_CONTROLLER_H
#define PROFILE_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>

typedef enum {
    STAGE_IDLE = 0,
    STAGE_PREHEAT,
    STAGE_SOAK,
    STAGE_REFLOW,
    STAGE_COOLDOWN,
    STAGE_ERROR_FAULT
} ProfileStage;

typedef enum {
    FAULT_NONE = 0,
    FAULT_SENSOR_DISCONNECTED,
    FAULT_THERMAL_RUNAWAY,
    FAULT_OVERHEAT_LIMIT
} SystemFault;

typedef struct {
    float kp;
    float ki;
    float kd;
    float integral;
    float prev_error;
    float integral_limit;
    float derivative_filter; /* коефіцієнт згладжування шуму */
    float filtered_derivative;
} PidController;

typedef struct {
    float target_temp;
    float ramp_rate;       /* °C за секунду */
    uint32_t hold_time_s;  /* час витримки на етапі */
} StageConfig;

typedef struct {
    ProfileStage stage;
    SystemFault fault;
    float current_temp;
    float target_temp;
    float duty_cycle;      /* 0.0f .. 1.0f */
    uint32_t stage_timer_s;
    uint32_t runaway_counter_s;
    float temp_at_full_power;
    uint8_t current_stage_idx;
    PidController pid;
    StageConfig stages[4];
} ReflowController;

void reflow_init(ReflowController *ctrl, const StageConfig *configs);
void reflow_start(ReflowController *ctrl);
void reflow_abort(ReflowController *ctrl, SystemFault reason);
void reflow_tick_1s(ReflowController *ctrl, float measured_temp, bool sensor_valid);

#endif /* PROFILE_CONTROLLER_H */
