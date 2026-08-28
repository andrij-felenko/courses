/* docking_controller.h */
#ifndef DOCKING_CONTROLLER_H
#define DOCKING_CONTROLLER_H

#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    float fx;
    float fy;
    float cx;
    float cy;
    float tag_size_m;
} camera_intrinsics_t;

typedef struct {
    float u[4];
    float v[4];
    uint32_t tag_id;
    uint64_t timestamp_us;
    bool valid;
} fiducial_corners_t;

typedef struct {
    float pos_body[3];      /* X (вперед), Y (праворуч), Z (вниз) в метрах */
    float vel_body[3];      /* лінійні швидкості в м/с */
    float yaw_relative_rad; /* відносний розворот за курсом */
    uint64_t state_time_us;
    bool is_tracking;
} docking_target_state_t;

typedef struct {
    float x[6];             /* [px, py, pz, vx, vy, vz] */
    float P[6][6];          /* матриця коваріацій помилок */
    float q_pos;            /* шум процесу положення */
    float q_vel;            /* шум процесу швидкості */
    float r_pos;            /* шум вимірювання камери */
    uint64_t last_update_us;
    bool initialized;
} docking_kalman_filter_t;

typedef struct {
    float kp_xy;
    float kd_xy;
    float kz_desc;
    float max_horiz_vel;
    float max_desc_vel;
    float min_desc_vel;
    float land_height_threshold;
} guidance_params_t;

typedef struct {
    float vel_cmd_body[3];  /* Vx, Vy, Vz уставки швидкості для FC */
    float yaw_rate_cmd_rad;
    bool initiate_touchdown;
    bool abort_landing;
} guidance_output_t;

typedef enum {
    DOCK_STATE_IDLE = 0,
    DOCK_STATE_ROOF_OPENING,
    DOCK_STATE_WAITING_UAV_APPROACH,
    DOCK_STATE_TOUCHDOWN_CONFIRMED,
    DOCK_STATE_MECHANICAL_CLAMPING,
    DOCK_STATE_CONTACT_PROBE,
    DOCK_STATE_PRECHARGE_SOFTSTART,
    DOCK_STATE_MAIN_CHARGING,
    DOCK_STATE_CHARGE_COMPLETE,
    DOCK_STATE_EMERGENCY_ISOLATION
} dock_station_fsm_state_t;

typedef struct {
    float sense_voltage_drop_mv;
    float probe_current_ma;
    float battery_voltage_mv;
    float charge_current_a;
    float cell_temperatures_c[6];
    uint8_t cell_count;
    bool uav_disarmed;
    bool bms_can_alive;
    bool emergency_stop_pressed;
} dock_hardware_inputs_t;

typedef struct {
    bool roof_open_cmd;
    bool clamp_motors_engage;
    bool probe_generator_enable;
    bool precharge_relay_enable;
    bool main_power_relay_enable;
    bool cooling_fans_enable;
    float target_psu_voltage_v;
    float target_psu_current_limit_a;
} dock_hardware_outputs_t;

typedef struct {
    dock_station_fsm_state_t state;
    uint32_t state_timer_ms;
    float contact_resistance_mohm;
    uint8_t retry_count;
} dock_station_controller_t;

/* Функції ініціалізації та оновлення */
void docking_kalman_init(docking_kalman_filter_t *kf, float q_pos, float q_vel, float r_pos);
void docking_kalman_predict(docking_kalman_filter_t *kf, float dt);
void docking_kalman_update(docking_kalman_filter_t *kf, const float meas_pos[3]);

bool docking_solve_pnp(const camera_intrinsics_t *cam, const fiducial_corners_t *corners, float out_pos_body[3], float *out_yaw_rad);

void docking_guidance_compute(
    const docking_target_state_t *target,
    const guidance_params_t *params,
    float dt,
    guidance_output_t *out);

void dock_station_fsm_init(dock_station_controller_t *ctrl);
void dock_station_fsm_update(
    dock_station_controller_t *ctrl,
    const dock_hardware_inputs_t *inputs,
    dock_hardware_outputs_t *outputs,
    uint32_t dt_ms);

#ifdef __cplusplus
}
#endif

#endif /* DOCKING_CONTROLLER_H */
