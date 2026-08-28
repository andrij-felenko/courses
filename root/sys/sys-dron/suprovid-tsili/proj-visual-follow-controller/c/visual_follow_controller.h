/* ========================================================================== */
/* visual_follow_controller.h - C99 Implementation                            */
/* ========================================================================== */
#ifndef VISUAL_FOLLOW_CONTROLLER_H
#define VISUAL_FOLLOW_CONTROLLER_H

#include <math.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

#define M_PI_F (3.14159265358979323846f)
#define DEG_TO_RAD_F (0.017453292519943295f)
#define RAD_TO_DEG_F (57.29577951308232f)

/* Калібрувальні параметри камери */
typedef struct {
    float fx;
    float fy;
    float cx;
    float cy;
} vfc_camera_intrinsics_t;

/* Обмежувальна рамка цілі */
typedef struct {
    float u;
    float v;
    float width;
    float height;
    float confidence;
    uint32_t target_id;
    uint64_t timestamp_us;
} vfc_target_bbox_t;

/* 6D Вектор стану цілі (NED) */
typedef struct {
    float pos_n;
    float pos_e;
    float pos_d;
    float vel_n;
    float vel_e;
    float vel_d;
} vfc_target_state_t;

/* Стан безпілотника */
typedef struct {
    float pos_n;
    float pos_e;
    float pos_d;
    float vel_n;
    float vel_e;
    float vel_d;
    float roll_rad;
    float pitch_rad;
    float yaw_rad;
    float gyro_yaw_rad_s;
    float gyro_pitch_rad_s;
} vfc_drone_state_t;

/* Конфігурація ПД-регулятора підвісу */
typedef struct {
    float kp;
    float kd;
    float tau_d;
    float max_rate_rad_s;
    float min_pitch_rad;
    float max_pitch_rad;
} vfc_gimbal_pid_config_t;

/* Конфігурація траєкторії Follow-Me / Orbit */
typedef struct {
    float follow_distance_m;
    float follow_altitude_m;
    float relative_angle_rad;
    float orbit_radius_m;
    float orbit_speed_m_s;
    float kp_pos;
    float kp_pos_z;
    float max_vel_horiz_m_s;
    float max_vel_vert_m_s;
} vfc_trajectory_config_t;

/* Вихідні уставки для автопілота */
typedef struct {
    float gimbal_yaw_rate_rad_s;
    float gimbal_pitch_rate_rad_s;
    float cmd_vel_n;
    float cmd_vel_e;
    float cmd_vel_d;
    float cmd_acc_n;
    float cmd_acc_e;
    float cmd_acc_d;
    float cmd_yaw_rad;
    float cmd_yaw_rate_rad_s;
    bool  target_valid;
    bool  occluded;
} vfc_control_outputs_t;

/* Внутрішній контекст контролера */
typedef struct {
    vfc_camera_intrinsics_t cam;
    vfc_gimbal_pid_config_t gimbal_cfg;
    vfc_trajectory_config_t traj_cfg;
    
    /* Стан фільтра Калмана */
    float x[6];
    float P[6][6];
    float q_acc;
    float r_pos;
    
    /* Стан ПД регулятора підвісу */
    float prev_err_yaw;
    float prev_err_pitch;
    float prev_d_err_yaw;
    float prev_d_err_pitch;
    
    /* Стан траєкторії */
    float orbit_angle_rad;
    uint32_t lost_frames_count;
    bool is_initialized;
} vfc_controller_context_t;

/* Прототипи функцій API */
void vfc_init(vfc_controller_context_t *ctx,
              const vfc_camera_intrinsics_t *cam,
              const vfc_gimbal_pid_config_t *gimbal_cfg,
              const vfc_trajectory_config_t *traj_cfg);

void vfc_reset(vfc_controller_context_t *ctx);

void vfc_predict_kalman(vfc_controller_context_t *ctx, float dt);

bool vfc_update_kalman(vfc_controller_context_t *ctx,
                       const vfc_drone_state_t *drone,
                       const vfc_target_bbox_t *bbox,
                       float terrain_alt_m);

void vfc_step_ibvs_and_trajectory(vfc_controller_context_t *ctx,
                                  const vfc_drone_state_t *drone,
                                  const vfc_target_bbox_t *bbox,
                                  bool orbit_mode,
                                  float dt,
                                  vfc_control_outputs_t *out);

#ifdef __cplusplus
}
#endif

#endif /* VISUAL_FOLLOW_CONTROLLER_H */

/* ========================================================================== */
/* visual_follow_controller.c - C99 Implementation                            */
/* ========================================================================== */
#include <math.h>
#include <stdbool.h>
#include <string.h>

static inline float vfc_clamp(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

void vfc_init(vfc_controller_context_t *ctx,
              const vfc_camera_intrinsics_t *cam,
              const vfc_gimbal_pid_config_t *gimbal_cfg,
              const vfc_trajectory_config_t *traj_cfg) {
    if (!ctx || !cam || !gimbal_cfg || !traj_cfg) return;
    
    memset(ctx, 0, sizeof(vfc_controller_context_t));
    ctx->cam = *cam;
    ctx->gimbal_cfg = *gimbal_cfg;
    ctx->traj_cfg = *traj_cfg;
    ctx->q_acc = 3.0f;
    ctx->r_pos = 0.25f;
    
    vfc_reset(ctx);
}

void vfc_reset(vfc_controller_context_t *ctx) {
    if (!ctx) return;
    
    memset(ctx->x, 0, sizeof(ctx->x));
    memset(ctx->P, 0, sizeof(ctx->P));
    
    for (int i = 0; i < 3; ++i) {
        ctx->P[i][i] = 100.0f;       /* Початкова невизначеність позиції: 10 м */
        ctx->P[i+3][i+3] = 25.0f;    /* Початкова невизначеність швидкості: 5 м/с */
    }
    
    ctx->prev_err_yaw = 0.0f;
    ctx->prev_err_pitch = 0.0f;
    ctx->prev_d_err_yaw = 0.0f;
    ctx->prev_d_err_pitch = 0.0f;
    ctx->orbit_angle_rad = 0.0f;
    ctx->lost_frames_count = 0;
    ctx->is_initialized = false;
}

void vfc_predict_kalman(vfc_controller_context_t *ctx, float dt) {
    if (!ctx || dt <= 0.0001f) return;
    
    /* 1. Передбачення вектору стану: X = F * X */
    ctx->x[0] += ctx->x[3] * dt;
    ctx->x[1] += ctx->x[4] * dt;
    ctx->x[2] += ctx->x[5] * dt;
    
    /* 2. Передбачення коваріації: P = F * P * F^T + Q */
    float dt2 = dt * dt;
    float dt3_3 = (dt2 * dt) / 3.0f;
    float dt2_2 = dt2 / 2.0f;
    float q = ctx->q_acc;
    
    for (int i = 0; i < 3; ++i) {
        int v_idx = i + 3;
        
        ctx->P[i][i] += dt * (ctx->P[v_idx][i] + ctx->P[i][v_idx]) + dt2 * ctx->P[v_idx][v_idx] + dt3_3 * q;
        ctx->P[i][v_idx] += dt * ctx->P[v_idx][v_idx] + dt2_2 * q;
        ctx->P[v_idx][i] += dt * ctx->P[v_idx][v_idx] + dt2_2 * q;
        ctx->P[v_idx][v_idx] += dt * q;
    }
}

bool vfc_update_kalman(vfc_controller_context_t *ctx,
                       const vfc_drone_state_t *drone,
                       const vfc_target_bbox_t *bbox,
                       float terrain_alt_m) {
    if (!ctx || !drone || !bbox) return false;
    
    if (bbox->confidence < 0.5f) {
        ctx->lost_frames_count++;
        return false;
    }
    
    /* Перетворення пікселів у промінь у системі координат камери */
    float delta_u = bbox->u - ctx->cam.cx;
    float delta_v = bbox->v - ctx->cam.cy;
    float los_c_x = delta_u / ctx->cam.fx;
    float los_c_y = delta_v / ctx->cam.fy;
    float los_c_z = 1.0f;
    
    float norm = sqrtf(los_c_x * los_c_x + los_c_y * los_c_y + los_c_z * los_c_z);
    los_c_x /= norm;
    los_c_y /= norm;
    los_c_z /= norm;
    
    /* Орієнтація камери в системі NED */
    float cy = cosf(drone->yaw_rad);
    float sy = sinf(drone->yaw_rad);
    float cp = cosf(drone->pitch_rad);
    float sp = sinf(drone->pitch_rad);
    float cr = cosf(drone->roll_rad);
    float sr = sinf(drone->roll_rad);
    
    /* Матриця обертання R_c_to_ned (Body FRD = NED при нульових кутах) */
    float r13 = cy * sp * cr + sy * sr;
    float r23 = sy * sp * cr - cy * sr;
    float r33 = cp * cr;
    
    float los_ned_d = r33 * los_c_z + (-sp) * los_c_x + (cp * sr) * los_c_y;
    if (fabsf(los_ned_d) < 0.05f) {
        return false; /* Промінь паралельний горизонту */
    }
    
    /* Розрахунок дистанції до перетину з рельєфом */
    float height_agl = terrain_alt_m - drone->pos_d;
    if (height_agl <= 1.0f) height_agl = 1.0f;
    
    float slant_range = height_agl / los_ned_d;
    if (slant_range <= 0.0f || slant_range > 1500.0f) {
        return false;
    }
    
    float z_meas[3];
    z_meas[0] = drone->pos_n + (cy * cp) * (slant_range * los_c_z);
    z_meas[1] = drone->pos_e + (sy * cp) * (slant_range * los_c_z);
    z_meas[2] = drone->pos_d + los_ned_d * slant_range;
    
    if (!ctx->is_initialized) {
        ctx->x[0] = z_meas[0];
        ctx->x[1] = z_meas[1];
        ctx->x[2] = z_meas[2];
        ctx->x[3] = 0.0f;
        ctx->x[4] = 0.0f;
        ctx->x[5] = 0.0f;
        ctx->is_initialized = true;
        ctx->lost_frames_count = 0;
        return true;
    }
    
    /* Нев'язка та стробування Махаланобіса */
    float y_res[3];
    float S[3];
    float d_mahalanobis_sq = 0.0f;
    
    for (int i = 0; i < 3; ++i) {
        y_res[i] = z_meas[i] - ctx->x[i];
        S[i] = ctx->P[i][i] + ctx->r_pos;
        d_mahalanobis_sq += (y_res[i] * y_res[i]) / S[i];
    }
    
    if (d_mahalanobis_sq > 11.34f) {
        ctx->lost_frames_count++;
        return false; /* Аномальна детекція */
    }
    
    /* Оновлення Калмана */
    for (int i = 0; i < 3; ++i) {
        int v_idx = i + 3;
        float K_pos = ctx->P[i][i] / S[i];
        float K_vel = ctx->P[v_idx][i] / S[i];
        
        ctx->x[i] += K_pos * y_res[i];
        ctx->x[v_idx] += K_vel * y_res[i];
        
        ctx->P[i][i] = (1.0f - K_pos) * ctx->P[i][i];
        ctx->P[v_idx][i] = (1.0f - K_pos) * ctx->P[v_idx][i];
        ctx->P[i][v_idx] = ctx->P[v_idx][i];
        ctx->P[v_idx][v_idx] -= K_vel * ctx->P[i][v_idx];
    }
    
    ctx->lost_frames_count = 0;
    return true;
}

void vfc_step_ibvs_and_trajectory(vfc_controller_context_t *ctx,
                                  const vfc_drone_state_t *drone,
                                  const vfc_target_bbox_t *bbox,
                                  bool orbit_mode,
                                  float dt,
                                  vfc_control_outputs_t *out) {
    if (!ctx || !drone || !out) return;
    if (dt <= 0.0001f) dt = 0.02f;
    
    memset(out, 0, sizeof(vfc_control_outputs_t));
    
    /* 1. Крок фільтра Калмана */
    vfc_predict_kalman(ctx, dt);
    bool updated = false;
    if (bbox && bbox->confidence >= 0.5f) {
        updated = vfc_update_kalman(ctx, drone, bbox, 0.0f);
    }
    
    out->target_valid = ctx->is_initialized && (ctx->lost_frames_count < 150);
    out->occluded = (ctx->lost_frames_count > 3);
    
    /* 2. Контур IBVS підвісу камери */
    if (bbox && bbox->confidence >= 0.5f) {
        float delta_u = bbox->u - ctx->cam.cx;
        float delta_v = bbox->v - ctx->cam.cy;
        
        float err_yaw = atan2f(delta_u, ctx->cam.fx);
        float err_pitch = atan2f(delta_v, ctx->cam.fy);
        
        float d_err_yaw_raw = (err_yaw - ctx->prev_err_yaw) / dt;
        float d_err_pitch_raw = (err_pitch - ctx->prev_err_pitch) / dt;
        
        float alpha = dt / (dt + ctx->gimbal_cfg.tau_d);
        float d_err_yaw = alpha * d_err_yaw_raw + (1.0f - alpha) * ctx->prev_d_err_yaw;
        float d_err_pitch = alpha * d_err_pitch_raw + (1.0f - alpha) * ctx->prev_d_err_pitch;
        
        ctx->prev_err_yaw = err_yaw;
        ctx->prev_err_pitch = err_pitch;
        ctx->prev_d_err_yaw = d_err_yaw;
        ctx->prev_d_err_pitch = d_err_pitch;
        
        float cmd_yaw_rate = (ctx->gimbal_cfg.kp * err_yaw + ctx->gimbal_cfg.kd * d_err_yaw) - drone->gyro_yaw_rad_s;
        float cmd_pitch_rate = (ctx->gimbal_cfg.kp * err_pitch + ctx->gimbal_cfg.kd * d_err_pitch) - drone->gyro_pitch_rad_s;
        
        out->gimbal_yaw_rate_rad_s = vfc_clamp(cmd_yaw_rate, -ctx->gimbal_cfg.max_rate_rad_s, ctx->gimbal_cfg.max_rate_rad_s);
        out->gimbal_pitch_rate_rad_s = vfc_clamp(cmd_pitch_rate, -ctx->gimbal_cfg.max_rate_rad_s, ctx->gimbal_cfg.max_rate_rad_s);
    }
    
    /* 3. Траєкторний контур дрона */
    if (out->target_valid) {
        float pos_sp_n = 0.0f;
        float pos_sp_e = 0.0f;
        float pos_sp_d = ctx->x[2] - ctx->traj_cfg.follow_altitude_m;
        
        float vel_ff_n = ctx->x[3];
        float vel_ff_e = ctx->x[4];
        float vel_ff_d = ctx->x[5];
        
        if (!orbit_mode) {
            /* Режим Follow-Me */
            float tgt_heading = atan2f(ctx->x[4], ctx->x[3]);
            float drone_azimuth = tgt_heading + ctx->traj_cfg.relative_angle_rad;
            
            pos_sp_n = ctx->x[0] - ctx->traj_cfg.follow_distance_m * cosf(drone_azimuth);
            pos_sp_e = ctx->x[1] - ctx->traj_cfg.follow_distance_m * sinf(drone_azimuth);
        } else {
            /* Режим Dynamic Orbit */
            float omega_orbit = ctx->traj_cfg.orbit_speed_m_s / ctx->traj_cfg.orbit_radius_m;
            ctx->orbit_angle_rad += omega_orbit * dt;
            if (ctx->orbit_angle_rad > 2.0f * M_PI_F) ctx->orbit_angle_rad -= 2.0f * M_PI_F;
            
            pos_sp_n = ctx->x[0] + ctx->traj_cfg.orbit_radius_m * cosf(ctx->orbit_angle_rad);
            pos_sp_e = ctx->x[1] + ctx->traj_cfg.orbit_radius_m * sinf(ctx->orbit_angle_rad);
            
            vel_ff_n += -ctx->traj_cfg.orbit_speed_m_s * sinf(ctx->orbit_angle_rad);
            vel_ff_e +=  ctx->traj_cfg.orbit_speed_m_s * cosf(ctx->orbit_angle_rad);
            
            float a_centripetal = (ctx->traj_cfg.orbit_speed_m_s * ctx->traj_cfg.orbit_speed_m_s) / ctx->traj_cfg.orbit_radius_m;
            out->cmd_acc_n = -a_centripetal * cosf(ctx->orbit_angle_rad);
            out->cmd_acc_e = -a_centripetal * sinf(ctx->orbit_angle_rad);
        }
        
        /* Розрахунок уставки швидкості */
        float err_pos_n = pos_sp_n - drone->pos_n;
        float err_pos_e = pos_sp_e - drone->pos_e;
        float err_pos_d = pos_sp_d - drone->pos_d;
        
        out->cmd_vel_n = vfc_clamp(vel_ff_n + ctx->traj_cfg.kp_pos * err_pos_n, -ctx->traj_cfg.max_vel_horiz_m_s, ctx->traj_cfg.max_vel_horiz_m_s);
        out->cmd_vel_e = vfc_clamp(vel_ff_e + ctx->traj_cfg.kp_pos * err_pos_e, -ctx->traj_cfg.max_vel_horiz_m_s, ctx->traj_cfg.max_vel_horiz_m_s);
        out->cmd_vel_d = vfc_clamp(vel_ff_d + ctx->traj_cfg.kp_pos_z * err_pos_d, -ctx->traj_cfg.max_vel_vert_m_s, ctx->traj_cfg.max_vel_vert_m_s);
        
        /* Розрахунок уставки курсу на ціль */
        out->cmd_yaw_rad = atan2f(ctx->x[1] - drone->pos_e, ctx->x[0] - drone->pos_n);
        if (orbit_mode) {
            out->cmd_yaw_rate_rad_s = ctx->traj_cfg.orbit_speed_m_s / ctx->traj_cfg.orbit_radius_m;
        }
    }
}
