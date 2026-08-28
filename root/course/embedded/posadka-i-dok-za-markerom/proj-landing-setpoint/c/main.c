#include <math.h>
#include <stdbool.h>
#include <stdint.h>

#define MARKER_TIMEOUT_SEC     0.4f
#define MAX_HORIZONTAL_VEL     1.5f   /* м/с */
#define MAX_VERTICAL_VEL       0.8f   /* м/с */
#define MIN_VERTICAL_VEL       0.15f  /* м/с */
#define CONE_SLOPE             0.45f  /* тангенс кута напівконуса посадки (≈24°) */
#define MIN_CONE_RADIUS        0.06f  /* мінімальний радіус біля землі, м */

typedef struct {
    float x;
    float y;
    float z;
} Vector3f;

typedef struct {
    float kp_xy;
    float ki_xy;
    float kd_xy;
    float kp_z;
    float i_limit_xy;
    float cam_to_body_r[3][3]; /* матриця повороту камери відносно корпусу */
    Vector3f cam_to_body_t;    /* зміщення камери відносно центру мас, м */
} PrecisionLandingConfig;

typedef struct {
    Vector3f integral_err;
    Vector3f prev_body_err;
    float last_detection_time;
    uint32_t active_marker_id;
    bool is_tracking;
} PrecisionLandingState;

typedef struct {
    Vector3f vel_setpoint_body; /* уставка швидкості в Body NED (м/с) */
    float yaw_rate_setpoint;    /* уставка швидкості гарчання (рад/с) */
    bool descent_allowed;       /* дозвіл на вертикальне зниження */
    bool touchdown_ready;       /* готовність до відсікання двигунів */
} LandingSetpointOutput;

/* Ініціалізація стану контролера */
void landing_control_init(PrecisionLandingState *state)
{
    state->integral_err.x = 0.0f;
    state->integral_err.y = 0.0f;
    state->integral_err.z = 0.0f;
    state->prev_body_err.x = 0.0f;
    state->prev_body_err.y = 0.0f;
    state->prev_body_err.z = 0.0f;
    state->last_detection_time = 0.0f;
    state->active_marker_id = 0;
    state->is_tracking = false;
}

/* Обмеження скалярного значення в діапазоні [min_v, max_v] */
static inline float clampf(float val, float min_v, float max_v)
{
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

/* Перетворення вектора з системи камери в систему корпусу: v_b = R_cb * v_c + t_cb */
static Vector3f transform_camera_to_body(const Vector3f *v_cam,
                                         const PrecisionLandingConfig *cfg)
{
    Vector3f v_body;
    v_body.x = cfg->cam_to_body_r[0][0] * v_cam->x +
               cfg->cam_to_body_r[0][1] * v_cam->y +
               cfg->cam_to_body_r[0][2] * v_cam->z + cfg->cam_to_body_t.x;

    v_body.y = cfg->cam_to_body_r[1][0] * v_cam->x +
               cfg->cam_to_body_r[1][1] * v_cam->y +
               cfg->cam_to_body_r[1][2] * v_cam->z + cfg->cam_to_body_t.y;

    v_body.z = cfg->cam_to_body_r[2][0] * v_cam->x +
               cfg->cam_to_body_r[2][1] * v_cam->y +
               cfg->cam_to_body_r[2][2] * v_cam->z + cfg->cam_to_body_t.z;
    return v_body;
}

/* Головна функція такту керування посадкою */
bool landing_control_update(const PrecisionLandingConfig *cfg,
                            PrecisionLandingState *state,
                            const Vector3f *pos_cam,
                            float marker_yaw_cam,
                            uint32_t marker_id,
                            const Vector3f *marker_offset_body,
                            const Vector3f *cur_body_vel,
                            float latency_sec,
                            float current_time,
                            float dt,
                            LandingSetpointOutput *out)
{
    if (dt <= 0.0f || dt > 0.2f) {
        return false;
    }

    bool fresh_detection = (pos_cam != NULL);

    if (fresh_detection) {
        state->last_detection_time = current_time;
        state->active_marker_id = marker_id;
        state->is_tracking = true;
    } else if (current_time - state->last_detection_time > MARKER_TIMEOUT_SEC) {
        state->is_tracking = false;
        out->vel_setpoint_body.x = 0.0f;
        out->vel_setpoint_body.y = 0.0f;
        out->vel_setpoint_body.z = 0.0f;
        out->yaw_rate_setpoint = 0.0f;
        out->descent_allowed = false;
        out->touchdown_ready = false;
        return false;
    }

    Vector3f target_body;
    if (fresh_detection) {
        /* 1. Переведення в систему корпусу */
        Vector3f raw_body = transform_camera_to_body(pos_cam, cfg);

        /* 2. Врахування зміщення вкладеного маркера відносно головного центру дока */
        if (marker_offset_body != NULL) {
            raw_body.x -= marker_offset_body->x;
            raw_body.y -= marker_offset_body->y;
        }

        /* 3. Компенсація затримки передачі кадру через одометрію тіла */
        target_body.x = raw_body.x - cur_body_vel->x * latency_sec;
        target_body.y = raw_body.y - cur_body_vel->y * latency_sec;
        target_body.z = raw_body.z - cur_body_vel->z * latency_sec;
        state->prev_body_err = target_body;
    } else {
        /* Екстраполяція позиції за відсутності свіжого кадру */
        target_body.x = state->prev_body_err.x - cur_body_vel->x * dt;
        target_body.y = state->prev_body_err.y - cur_body_vel->y * dt;
        target_body.z = state->prev_body_err.z - cur_body_vel->z * dt;
        state->prev_body_err = target_body;
    }

    /* Помилка позиціонування: вектор від дрона до маркера (уперед/праворуч/униз) */
    float err_x = target_body.x;
    float err_y = target_body.y;
    float altitude = target_body.z; /* відстань по вертикалі до маркера (м) */

    float horiz_dist = sqrtf(err_x * err_x + err_y * err_y);
    float cone_radius = altitude * CONE_SLOPE + MIN_CONE_RADIUS;

    /* Перевірка перебування всередині конуса безпеки */
    bool inside_cone = (horiz_dist <= cone_radius);
    out->descent_allowed = inside_cone;

    /* Інтегрування горизонтальної помилки для парирування вітру */
    state->integral_err.x += err_x * dt;
    state->integral_err.y += err_y * dt;
    state->integral_err.x = clampf(state->integral_err.x, -cfg->i_limit_xy, cfg->i_limit_xy);
    state->integral_err.y = clampf(state->integral_err.y, -cfg->i_limit_xy, cfg->i_limit_xy);

    /* Розрахунок горизонтальних уставок швидкості */
    float cmd_vx = cfg->kp_xy * err_x + cfg->ki_xy * state->integral_err.x;
    float cmd_vy = cfg->kp_xy * err_y + cfg->ki_xy * state->integral_err.y;

    out->vel_setpoint_body.x = clampf(cmd_vx, -MAX_HORIZONTAL_VEL, MAX_HORIZONTAL_VEL);
    out->vel_setpoint_body.y = clampf(cmd_vy, -MAX_HORIZONTAL_VEL, MAX_HORIZONTAL_VEL);

    /* Розрахунок вертикальної швидкості */
    if (inside_cone && altitude > 0.05f) {
        float vz_cmd = cfg->kp_z * altitude;
        out->vel_setpoint_body.z = clampf(vz_cmd, MIN_VERTICAL_VEL, MAX_VERTICAL_VEL);
    } else {
        /* Зупинка зниження для центрування */
        out->vel_setpoint_body.z = 0.0f;
    }

    /* Розрахунок кута розвороту за маркером */
    if (fresh_detection) {
        out->yaw_rate_setpoint = clampf(0.8f * marker_yaw_cam, -0.5f, 0.5f);
    } else {
        out->yaw_rate_setpoint = 0.0f;
    }

    /* Критерій фінального торкання (Touchdown) */
    out->touchdown_ready = (altitude < 0.12f) && (horiz_dist < 0.04f);

    return true;
}
