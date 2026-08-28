#include <stdio.h>
#include <stdbool.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ── Векторна геометрія ──────────────────────────────────────────────────────
typedef struct { float x, y, z; } Vector3f;

static inline float clampf(float val, float min_v, float max_v) {
    if (val < min_v) return min_v;
    if (val > max_v) return max_v;
    return val;
}

static inline float wrap_pi(float rad) {
    while (rad > (float)M_PI)  rad -= 2.0f * (float)M_PI;
    while (rad < -(float)M_PI) rad += 2.0f * (float)M_PI;
    return rad;
}

// ── Дискретний ПІД-регулятор із захистом від насичення (Anti-Windup) ────────
typedef struct {
    float kp, ki, kd;
    float integ;
    float integ_max;
    float prev_meas;
    float out_min, out_max;
} PID_Controller;

static void pid_init(PID_Controller *pid, float kp, float ki, float kd,
                     float i_max, float out_min, float out_max) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->integ = 0.0f;
    pid->integ_max = i_max;
    pid->prev_meas = 0.0f;
    pid->out_min = out_min;
    pid->out_max = out_max;
}

static float pid_update(PID_Controller *pid, float target, float meas, float dt) {
    float error = target - meas;

    // Диференційна складова від похідної виміру (запобігає удару при стрибку уставки)
    float deriv = 0.0f;
    if (dt > 1e-6f) {
        deriv = -(meas - pid->prev_meas) / dt;
    }
    pid->prev_meas = meas;

    // Попередній вихід без урахування нового інтеграла
    float p_term = pid->kp * error;
    float d_term = pid->kd * deriv;
    float out_unsat = p_term + pid->ki * pid->integ + d_term;

    // Умовне інтегрування (clamping anti-windup): не накопичуємо, якщо регулятор у насиченні
    bool saturated_high = (out_unsat >= pid->out_max && error > 0.0f);
    bool saturated_low  = (out_unsat <= pid->out_min && error < 0.0f);

    if (!saturated_high && !saturated_low) {
        pid->integ += error * dt;
        pid->integ = clampf(pid->integ, -pid->integ_max, pid->integ_max);
    }

    float out = p_term + pid->ki * pid->integ + d_term;
    return clampf(out, pid->out_min, pid->out_max);
}

// ── Структури стану та конфігурації автопілота ──────────────────────────────
typedef struct {
    // Входи від EKF / IMU
    Vector3f pos_neu;       // [м] Північ, Схід, Вгору
    Vector3f vel_neu;       // [м/с]
    Vector3f euler_rad;     // [рад] Roll, Pitch, Yaw
    Vector3f gyro_rps;      // [рад/с] кутові швидкості тіла P, Q, R
    float v_battery;        // [В] поточна напруга
    float v_nominal;        // [В] номінальна напруга 4S (14.8В) або 6S (22.2В)

    // Уставки від планувальника місії
    Vector3f target_pos_neu;
    float target_yaw_rad;

    // Проміжні змінні каскадів
    Vector3f des_vel_neu;
    Vector3f des_accel_neu;
    Vector3f des_euler_rad;
    Vector3f des_rates_rps;
    float base_throttle;

    // Регулятори
    PID_Controller pid_pos_n, pid_pos_e, pid_pos_z;
    PID_Controller pid_vel_n, pid_vel_e, pid_vel_z;
    PID_Controller pid_rate_p, pid_rate_q, pid_rate_r;

    // Коефіцієнти P для кутів орієнтації
    float kp_roll_angle, kp_pitch_angle, kp_yaw_angle;

    // Фізичні обмеження
    float max_horiz_vel;    // [м/с] напр. 12.0
    float max_tilt_angle;   // [рад] напр. 0.61 (35°)
    float thr_hover;        // [0..1] базова тяга зависання, напр. 0.45
} CascadedAutopilot;

void autopilot_init(CascadedAutopilot *ap) {
    // Горизонтальна позиція: P-регулятор формує бажану швидкість
    pid_init(&ap->pid_pos_n, 1.0f, 0.0f, 0.0f, 0.0f, -12.0f, 12.0f);
    pid_init(&ap->pid_pos_e, 1.0f, 0.0f, 0.0f, 0.0f, -12.0f, 12.0f);
    pid_init(&ap->pid_pos_z, 1.2f, 0.0f, 0.0f, 0.0f, -3.0f, 4.0f);

    // Швидкості: PID формує прискорення [м/с²]
    pid_init(&ap->pid_vel_n, 2.0f, 0.5f, 0.1f, 5.0f, -6.0f, 6.0f);
    pid_init(&ap->pid_vel_e, 2.0f, 0.5f, 0.1f, 5.0f, -6.0f, 6.0f);
    pid_init(&ap->pid_vel_z, 2.5f, 1.2f, 0.05f, 4.0f, -8.0f, 8.0f);

    // Орієнтація: P-контур на кути
    ap->kp_roll_angle  = 6.5f;
    ap->kp_pitch_angle = 6.5f;
    ap->kp_yaw_angle   = 3.5f;

    // Кутові швидкості: PID формує нормовані моменти [-1.0 .. +1.0]
    pid_init(&ap->pid_rate_p, 0.15f, 0.20f, 0.003f, 0.3f, -1.0f, 1.0f);
    pid_init(&ap->pid_rate_q, 0.15f, 0.20f, 0.003f, 0.3f, -1.0f, 1.0f);
    pid_init(&ap->pid_rate_r, 0.22f, 0.12f, 0.000f, 0.3f, -1.0f, 1.0f);

    ap->max_horiz_vel = 12.0f;
    ap->max_tilt_angle = 35.0f * (float)M_PI / 180.0f;
    ap->thr_hover = 0.45f;
    ap->v_nominal = 16.0f;
    ap->v_battery = 16.0f;
}

// ── Повільний крок: Контури позиції та швидкості (50 Гц) ────────────────────
void autopilot_update_slow_loop(CascadedAutopilot *ap, float dt) {
    const float GRAVITY = 9.80665f;

    // 1. Контур позиції (P): розрахунок цільової швидкості
    float des_vn = pid_update(&ap->pid_pos_n, ap->target_pos_neu.x, ap->pos_neu.x, dt);
    float des_ve = pid_update(&ap->pid_pos_e, ap->target_pos_neu.y, ap->pos_neu.y, dt);
    float des_vz = pid_update(&ap->pid_pos_z, ap->target_pos_neu.z, ap->pos_neu.z, dt);

    // Обмеження вектора горизонтальної швидкості
    float horiz_speed = sqrtf(des_vn * des_vn + des_ve * des_ve);
    if (horiz_speed > ap->max_horiz_vel && horiz_speed > 1e-4f) {
        float scale = ap->max_horiz_vel / horiz_speed;
        des_vn *= scale;
        des_ve *= scale;
    }
    ap->des_vel_neu.x = des_vn;
    ap->des_vel_neu.y = des_ve;
    ap->des_vel_neu.z = des_vz;

    // 2. Контур швидкостей (PID): розрахунок бажаних прискорень
    float a_n = pid_update(&ap->pid_vel_n, ap->des_vel_neu.x, ap->vel_neu.x, dt);
    float a_e = pid_update(&ap->pid_vel_e, ap->des_vel_neu.y, ap->vel_neu.y, dt);
    float a_z = pid_update(&ap->pid_vel_z, ap->des_vel_neu.z, ap->vel_neu.z, dt);
    ap->des_accel_neu = (Vector3f){ a_n, a_e, a_z };

    // 3. Проекція прискорень Землі на курс апарата (Body Frame)
    float psi = ap->euler_rad.z; // поточний курс
    float cos_psi = cosf(psi);
    float sin_psi = sinf(psi);

    float a_fwd   =  a_n * cos_psi + a_e * sin_psi;
    float a_right = -a_n * sin_psi + a_e * cos_psi;

    // 4. Перетворення прискорень на кути нахилу корпуса
    float target_pitch = atan2f(a_fwd, GRAVITY);
    float target_roll  = atan2f(a_right, GRAVITY);

    target_pitch = clampf(target_pitch, -ap->max_tilt_angle, ap->max_tilt_angle);
    target_roll  = clampf(target_roll,  -ap->max_tilt_angle, ap->max_tilt_angle);

    ap->des_euler_rad.x = target_roll;
    ap->des_euler_rad.y = target_pitch;
    ap->des_euler_rad.z = ap->target_yaw_rad;

    // 5. Вертикальний канал тяги з компенсацією нахилу та напруги
    float roll = ap->euler_rad.x;
    float pitch = ap->euler_rad.y;
    float cos_tilt = cosf(roll) * cosf(pitch);
    if (cos_tilt < 0.35f) cos_tilt = 0.35f; // оберігаємо від ділення на 0 при екстремальних кутах

    // Відносна зміна тяги від прискорення a_z
    float thr_accel_offset = (a_z / GRAVITY) * ap->thr_hover;
    float raw_throttle = (ap->thr_hover + thr_accel_offset) / cos_tilt;

    // Компенсація розряду акумулятора
    if (ap->v_battery > 6.0f) {
        raw_throttle *= (ap->v_nominal / ap->v_battery);
    }
    ap->base_throttle = clampf(raw_throttle, 0.08f, 0.95f);
}

// ── Швидкий крок: Контури орієнтації та кутових швидкостей (500 Гц) ─────────
void autopilot_update_fast_loop(CascadedAutopilot *ap, float dt,
                               float *out_roll_t, float *out_pitch_t,
                               float *out_yaw_t,  float *out_throttle) {
    // 1. Контур орієнтації (P-регулятор кутів)
    float err_roll  = ap->des_euler_rad.x - ap->euler_rad.x;
    float err_pitch = ap->des_euler_rad.y - ap->euler_rad.y;
    float err_yaw   = wrap_pi(ap->des_euler_rad.z - ap->euler_rad.z); // захист від розкручування

    ap->des_rates_rps.x = clampf(ap->kp_roll_angle  * err_roll,  -4.0f, 4.0f);
    ap->des_rates_rps.y = clampf(ap->kp_pitch_angle * err_pitch, -4.0f, 4.0f);
    ap->des_rates_rps.z = clampf(ap->kp_yaw_angle   * err_yaw,   -2.5f, 2.5f);

    // 2. Контур кутових швидкостей (PID-регулятор гіроскопа)
    *out_roll_t  = pid_update(&ap->pid_rate_p, ap->des_rates_rps.x, ap->gyro_rps.x, dt);
    *out_pitch_t = pid_update(&ap->pid_rate_q, ap->des_rates_rps.y, ap->gyro_rps.y, dt);
    *out_yaw_t   = pid_update(&ap->pid_rate_r, ap->des_rates_rps.z, ap->gyro_rps.z, dt);
    *out_throttle = ap->base_throttle;
}

// Приклад виклику та симуляції кроку керування
int main(void) {
    CascadedAutopilot ap;
    autopilot_init(&ap);

    // Встановлюємо ціль: 10 м на північ, 5 м на схід, висота 25 м, курс 90° (схід)
    ap.target_pos_neu = (Vector3f){ 10.0f, 5.0f, 25.0f };
    ap.target_yaw_rad = 90.0f * (float)M_PI / 180.0f;

    // Поточний стан: висимо на (0, 0, 20), курс 0°
    ap.pos_neu   = (Vector3f){ 0.0f, 0.0f, 20.0f };
    ap.vel_neu   = (Vector3f){ 0.0f, 0.0f, 0.0f };
    ap.euler_rad = (Vector3f){ 0.0f, 0.0f, 0.0f };
    ap.gyro_rps  = (Vector3f){ 0.0f, 0.0f, 0.0f };

    // Такт повільного контуру
    autopilot_update_slow_loop(&ap, 0.02f);

    // Такт швидкого контуру
    float tau_roll, tau_pitch, tau_yaw, throttle;
    autopilot_update_fast_loop(&ap, 0.002f, &tau_roll, &tau_pitch, &tau_yaw, &throttle);

    printf("Результати розрахунку каскаду:\n");
    printf("Бажана швидкість: Vn=%.2f, Ve=%.2f, Vz=%.2f м/с\n",
           ap.des_vel_neu.x, ap.des_vel_neu.y, ap.des_vel_neu.z);
    printf("Цільовий тангаж: %.2f deg, крен: %.2f deg\n",
           ap.des_euler_rad.y * 180.0f / (float)M_PI,
           ap.des_euler_rad.x * 180.0f / (float)M_PI);
    printf("Команди моторів: Roll=%.3f, Pitch=%.3f, Yaw=%.3f, Throttle=%.3f\n",
           tau_roll, tau_pitch, tau_yaw, throttle);

    return 0;
}
