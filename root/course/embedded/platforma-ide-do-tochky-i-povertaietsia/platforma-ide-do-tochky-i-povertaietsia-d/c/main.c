#include <math.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_WAYPOINTS        16
#define NAV_PI               3.14159265358979323846f
#define NAV_TWO_PI           6.28318530717958647692f

typedef enum {
    NAV_STATE_IDLE = 0,
    NAV_STATE_ROTATE_TO_WP,
    NAV_STATE_TRACK_WP,
    NAV_STATE_ACTION_AT_WP,
    NAV_STATE_RETURN_TO_BASE,
    NAV_STATE_PARKED_HOME,
    NAV_STATE_FAULT_STALL
} nav_state_t;

typedef struct {
    float x;        // X координата, м
    float y;        // Y координата, м
    float theta;    // Курс (азимут), рад [-PI, PI]
} pose2d_t;

typedef struct {
    float x;
    float y;
    float dwell_time_sec; // Час зупинки в точці, с
} waypoint_t;

typedef struct {
    float track_width_m;     // База L, м
    float wheel_radius_m;    // Радіус колеса r, м
    float ticks_per_rev;     // Імпульсів на повний оберт колеса
    float max_linear_vel;    // Максимальна лінійна швидкість v, м/с
    float max_angular_vel;   // Максимальна кутова швидкість ω, рад/с
    float lookahead_dist;    // Відстань попереднього перегляду L_d, м
    float acceptance_rad;    // Радіус досягнення точки, м
    float gyro_weight;       // Коефіцієнт злиття з гіроскопом (0.95 - 0.98)
} nav_config_t;

typedef struct {
    pose2d_t     pose;
    nav_state_t  state;
    nav_config_t cfg;

    waypoint_t   mission[MAX_WAYPOINTS];
    uint8_t      mission_count;
    uint8_t      current_wp_idx;

    float        action_timer_sec;
    float        gyro_bias_z;
    bool         is_calibrated;

    float        cmd_linear_vel;  // Результуюча v_cmd, м/с
    float        cmd_angular_vel; // Результуюча ω_cmd, рад/с
    float        wheel_vel_l;     // Лінійні швидкості коліс, м/с
    float        wheel_vel_r;
} nav_controller_t;

// Нормалізація кута в інтервал [-PI, PI]
static inline float nav_wrap_to_pi(float angle) {
    while (angle > NAV_PI)  angle -= NAV_TWO_PI;
    while (angle < -NAV_PI) angle += NAV_TWO_PI;
    return angle;
}

// Ініціалізація модуля
void nav_init(nav_controller_t *nav, const nav_config_t *cfg) {
    memset(nav, 0, sizeof(nav_controller_t));
    nav->cfg = *cfg;
    nav->state = NAV_STATE_IDLE;
}

// Завантаження маршруту
bool nav_add_waypoint(nav_controller_t *nav, float x, float y, float dwell_sec) {
    if (nav->mission_count >= MAX_WAYPOINTS) return false;
    nav->mission[nav->mission_count].x = x;
    nav->mission[nav->mission_count].y = y;
    nav->mission[nav->mission_count].dwell_time_sec = dwell_sec;
    nav->mission_count++;
    return true;
}

// Інтегрування одометрії та корекція за гіроскопом
void nav_update_odometry_imu(nav_controller_t *nav,
                             int32_t delta_ticks_l,
                             int32_t delta_ticks_r,
                             float gyro_z_rad_s,
                             float dt_sec) {
    // 1. Перевід тиків у переміщення ободів
    float c_tick = (NAV_TWO_PI * nav->cfg.wheel_radius_m) / nav->cfg.ticks_per_rev;
    float ds_l = (float)delta_ticks_l * c_tick;
    float ds_r = (float)delta_ticks_r * c_tick;

    float ds = (ds_r + ds_l) * 0.5f;
    float dtheta_odo = (ds_r - ds_l) / nav->cfg.track_width_m;

    // 2. Інтегрування гіроскопа
    float gyro_rate_clean = gyro_z_rad_s - nav->gyro_bias_z;
    float dtheta_gyro = gyro_rate_clean * dt_sec;

    // 3. Комплементарне злиття приросту кута
    float dtheta_fused = (nav->cfg.gyro_weight * dtheta_gyro) +
                         ((1.0f - nav->cfg.gyro_weight) * dtheta_odo);

    // 4. Оновлення координат за схемою середньої точки
    float theta_mid = nav->pose.theta + (dtheta_fused * 0.5f);
    nav->pose.x += ds * cosf(theta_mid);
    nav->pose.y += ds * sinf(theta_mid);
    nav->pose.theta = nav_wrap_to_pi(nav->pose.theta + dtheta_fused);
}

// Розрахунок Pure Pursuit наведення на цільові координати (gx, gy)
static void nav_compute_pure_pursuit(nav_controller_t *nav, float gx, float gy,
                                     float *out_v, float *out_w) {
    float dx = gx - nav->pose.x;
    float dy = gy - nav->pose.y;
    float dist = sqrtf(dx * dx + dy * dy);

    if (dist < 0.001f) {
        *out_v = 0.0f;
        *out_w = 0.0f;
        return;
    }

    float target_azimuth = atan2f(dy, dx);
    float heading_error = nav_wrap_to_pi(target_azimuth - nav->pose.theta);

    // Зниження лінійної швидкості при наближенні та при великому куті
    float d_slow = nav->cfg.lookahead_dist * 2.0f;
    float dist_scale = (dist < d_slow) ? (dist / d_slow) : 1.0f;
    if (dist_scale < 0.15f) dist_scale = 0.15f;

    float angle_factor = cosf(heading_error);
    if (angle_factor < 0.0f) angle_factor = 0.0f;

    float v_cmd = nav->cfg.max_linear_vel * dist_scale * angle_factor;

    // Кутова швидкість за кривиною дуги Pure Pursuit
    float curvature = (2.0f * sinf(heading_error)) / nav->cfg.lookahead_dist;
    float w_cmd = v_cmd * curvature;

    // Обмеження максимальної кутової швидкості
    if (w_cmd > nav->cfg.max_angular_vel)  w_cmd = nav->cfg.max_angular_vel;
    if (w_cmd < -nav->cfg.max_angular_vel) w_cmd = -nav->cfg.max_angular_vel;

    *out_v = v_cmd;
    *out_w = w_cmd;
}

// Крок навігаційного автомата станів
void nav_step_fsm(nav_controller_t *nav, float dt_sec) {
    float target_x = 0.0f;
    float target_y = 0.0f;

    switch (nav->state) {
        case NAV_STATE_IDLE:
            nav->cmd_linear_vel = 0.0f;
            nav->cmd_angular_vel = 0.0f;
            break;

        case NAV_STATE_ROTATE_TO_WP: {
            target_x = nav->mission[nav->current_wp_idx].x;
            target_y = nav->mission[nav->current_wp_idx].y;

            float target_azimuth = atan2f(target_y - nav->pose.y, target_x - nav->pose.x);
            float heading_err = nav_wrap_to_pi(target_azimuth - nav->pose.theta);

            if (fabsf(heading_err) < 0.15f) { // ~8.5 градусів
                nav->state = NAV_STATE_TRACK_WP;
            } else {
                nav->cmd_linear_vel = 0.0f;
                float rot_speed = 1.8f * heading_err;
                if (rot_speed > nav->cfg.max_angular_vel)  rot_speed = nav->cfg.max_angular_vel;
                if (rot_speed < -nav->cfg.max_angular_vel) rot_speed = -nav->cfg.max_angular_vel;
                nav->cmd_angular_vel = rot_speed;
            }
            break;
        }

        case NAV_STATE_TRACK_WP: {
            target_x = nav->mission[nav->current_wp_idx].x;
            target_y = nav->mission[nav->current_wp_idx].y;

            float dx = target_x - nav->pose.x;
            float dy = target_y - nav->pose.y;
            float dist = sqrtf(dx * dx + dy * dy);

            if (dist <= nav->cfg.acceptance_rad) {
                nav->cmd_linear_vel = 0.0f;
                nav->cmd_angular_vel = 0.0f;
                nav->action_timer_sec = nav->mission[nav->current_wp_idx].dwell_time_sec;
                nav->state = NAV_STATE_ACTION_AT_WP;
            } else {
                nav_compute_pure_pursuit(nav, target_x, target_y,
                                         &nav->cmd_linear_vel, &nav->cmd_angular_vel);
            }
            break;
        }

        case NAV_STATE_ACTION_AT_WP:
            nav->cmd_linear_vel = 0.0f;
            nav->cmd_angular_vel = 0.0f;
            nav->action_timer_sec -= dt_sec;

            if (nav->action_timer_sec <= 0.0f) {
                nav->current_wp_idx++;
                if (nav->current_wp_idx >= nav->mission_count) {
                    nav->state = NAV_STATE_RETURN_TO_BASE;
                } else {
                    nav->state = NAV_STATE_ROTATE_TO_WP;
                }
            }
            break;

        case NAV_STATE_RETURN_TO_BASE: {
            target_x = 0.0f;
            target_y = 0.0f;

            float dx = target_x - nav->pose.x;
            float dy = target_y - nav->pose.y;
            float dist = sqrtf(dx * dx + dy * dy);

            if (dist <= nav->cfg.acceptance_rad) {
                nav->state = NAV_STATE_PARKED_HOME;
            } else {
                nav_compute_pure_pursuit(nav, target_x, target_y,
                                         &nav->cmd_linear_vel, &nav->cmd_angular_vel);
            }
            break;
        }

        case NAV_STATE_PARKED_HOME: {
            // Кінцевий доворот на кут 0.0 (вихідна орієнтація)
            float home_heading_err = nav_wrap_to_pi(0.0f - nav->pose.theta);
            if (fabsf(home_heading_err) < 0.05f) {
                nav->cmd_linear_vel = 0.0f;
                nav->cmd_angular_vel = 0.0f;
                nav->state = NAV_STATE_IDLE; // Місія повністю завершена
            } else {
                nav->cmd_linear_vel = 0.0f;
                float rot_speed = 1.5f * home_heading_err;
                if (rot_speed > nav->cfg.max_angular_vel)  rot_speed = nav->cfg.max_angular_vel;
                if (rot_speed < -nav->cfg.max_angular_vel) rot_speed = -nav->cfg.max_angular_vel;
                nav->cmd_angular_vel = rot_speed;
            }
            break;
        }

        default:
            nav->cmd_linear_vel = 0.0f;
            nav->cmd_angular_vel = 0.0f;
            break;
    }

    // Інверсна кінематика та захист від насичення
    float v_l = nav->cmd_linear_vel - (nav->cmd_angular_vel * nav->cfg.track_width_m * 0.5f);
    float v_r = nav->cmd_linear_vel + (nav->cmd_angular_vel * nav->cfg.track_width_m * 0.5f);

    float max_req = fmaxf(fabsf(v_l), fabsf(v_r));
    if (max_req > nav->cfg.max_linear_vel && max_req > 1e-4f) {
        float scale = nav->cfg.max_linear_vel / max_req;
        v_l *= scale;
        v_r *= scale;
    }

    nav->wheel_vel_l = v_l;
    nav->wheel_vel_r = v_r;
}
