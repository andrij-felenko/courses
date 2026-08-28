#include <math.h>
#include <stdbool.h>

#define GRAVITY 9.80665f
#define MAX_TILT_RAD 0.6108f // 35 градусів

typedef struct { float x, y, z; } Vec3;

typedef struct {
    float kp, ki, kd;
    float integ, i_max;
    float prev_meas;
    float out_min, out_max;
} PID;

static inline float clampf(float v, float min_v, float max_v) {
    return (v < min_v) ? min_v : ((v > max_v) ? max_v : v);
}

static inline float wrap_pi(float a) {
    while (a > (float)M_PI)  a -= 2.0f * (float)M_PI;
    while (a < -(float)M_PI) a += 2.0f * (float)M_PI;
    return a;
}

static float pid_calc(PID *p, float target, float meas, float dt) {
    float err = target - meas;
    float deriv = (dt > 1e-5f) ? -(meas - p->prev_meas) / dt : 0.0f;
    p->prev_meas = meas;

    float p_out = p->kp * err;
    float d_out = p->kd * deriv;
    float unsat = p_out + p->ki * p->integ + d_out;

    // Анти-віндап із зупинкою інтегрування в насиченні (clamping)
    if (!((unsat >= p->out_max && err > 0.0f) || (unsat <= p->out_min && err < 0.0f))) {
        p->integ = clampf(p->integ + err * dt, -p->i_max, p->i_max);
    }
    return clampf(p_out + p->ki * p->integ + d_out, p->out_min, p->out_max);
}

// Повільний крок: Позиція (P) -> Швидкість (PID) -> Бажані кути (50 Гц)
void position_controller_step(const Vec3 *pos_tgt, const Vec3 *pos_meas,
                              const Vec3 *vel_meas, const Vec3 *euler_meas,
                              float thr_hover, float v_bat, float v_nom, float dt,
                              PID *p_pos_n, PID *p_pos_e, PID *p_pos_z,
                              PID *p_vel_n, PID *p_vel_e, PID *p_vel_z,
                              Vec3 *out_euler_tgt, float *out_throttle) {
    // 1. Позиція -> Цільова швидкість
    float vn_des = pid_calc(p_pos_n, pos_tgt->x, pos_meas->x, dt);
    float ve_des = pid_calc(p_pos_e, pos_tgt->y, pos_meas->y, dt);
    float vz_des = pid_calc(p_pos_z, pos_tgt->z, pos_meas->z, dt);

    // 2. Швидкість -> Прискорення
    float an_des = pid_calc(p_vel_n, vn_des, vel_meas->x, dt);
    float ae_des = pid_calc(p_vel_e, ve_des, vel_meas->y, dt);
    float az_des = pid_calc(p_vel_z, vz_des, vel_meas->z, dt);

    // 3. Проекція прискорень на курс корпусу
    float psi = euler_meas->z;
    float a_fwd =  an_des * cosf(psi) + ae_des * sinf(psi);
    float a_rgt = -an_des * sinf(psi) + ae_des * cosf(psi);

    // 4. Прискорення -> Кути нахилу
    out_euler_tgt->x = clampf(atan2f(a_rgt, GRAVITY), -MAX_TILT_RAD, MAX_TILT_RAD); // Roll
    out_euler_tgt->y = clampf(atan2f(a_fwd, GRAVITY), -MAX_TILT_RAD, MAX_TILT_RAD); // Pitch
    out_euler_tgt->z = pos_tgt->z; // Yaw задається окремо або тримається

    // 5. Вертикальний канал: тяга + компенсація нахилу та батареї
    float cos_tilt = cosf(euler_meas->x) * cosf(euler_meas->y);
    if (cos_tilt < 0.35f) cos_tilt = 0.35f;

    float raw_thr = (thr_hover + (az_des / GRAVITY) * thr_hover) / cos_tilt;
    if (v_bat > 5.0f) raw_thr *= (v_nom / v_bat);
    *out_throttle = clampf(raw_thr, 0.05f, 0.95f);
}

// Швидкий крок: Кути (P) -> Кутові швидкості (PID) -> Моменти моторів (500 Гц)
void attitude_controller_step(const Vec3 *euler_tgt, const Vec3 *euler_meas,
                              const Vec3 *gyro_meas, float dt,
                              float kp_roll, float kp_pitch, float kp_yaw,
                              PID *p_rate_p, PID *p_rate_q, PID *p_rate_r,
                              Vec3 *out_torques) {
    // 1. Похибка кутів (із захистом від 360° на Yaw)
    float e_roll  = euler_tgt->x - euler_meas->x;
    float e_pitch = euler_tgt->y - euler_meas->y;
    float e_yaw   = wrap_pi(euler_tgt->z - euler_meas->z);

    // 2. Бажані кутові швидкості тіла
    float p_des = clampf(kp_roll  * e_roll,  -4.0f, 4.0f);
    float q_des = clampf(kp_pitch * e_pitch, -4.0f, 4.0f);
    float r_des = clampf(kp_yaw   * e_yaw,   -2.5f, 2.5f);

    // 3. ПІД-регулятори гіроскопа формують керуючі моменти
    out_torques->x = pid_calc(p_rate_p, p_des, gyro_meas->x, dt);
    out_torques->y = pid_calc(p_rate_q, q_des, gyro_meas->y, dt);
    out_torques->z = pid_calc(p_rate_r, r_des, gyro_meas->z, dt);
}
