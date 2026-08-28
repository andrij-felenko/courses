#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define PI_F 3.14159265358979323846f

typedef struct {
    float state;
    float alpha;
} PT1Filter;

static inline void pt1_init(PT1Filter *f, float cutoff_hz, float dt) {
    float rc = 1.0f / (2.0f * PI_F * cutoff_hz);
    f->alpha = dt / (rc + dt);
    f->state = 0.0f;
}

static inline float pt1_update(PT1Filter *f, float input) {
    f->state += f->alpha * (input - f->state);
    return f->state;
}

typedef struct {
    float kp;
    float ki;
    float kd;
    float k_ff;
    float i_term;
    float i_max;
    float out_max;
    float prev_meas;
    PT1Filter d_filter;
} RatePID;

static inline void rate_pid_init(RatePID *pid, float kp, float ki, float kd, float k_ff,
                                 float i_max, float out_max, float d_cutoff_hz, float dt) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->k_ff = k_ff;
    pid->i_term = 0.0f;
    pid->i_max = i_max;
    pid->out_max = out_max;
    pid->prev_meas = 0.0f;
    pt1_init(&pid->d_filter, d_cutoff_hz, dt);
}

static inline float rate_pid_update(RatePID *pid, float target_rate, float meas_rate, float dt) {
    float error = target_rate - meas_rate;

    // Пропорційна ланка
    float p_out = pid->kp * error;

    // Прямий зв'язок (Feedforward) для прискорення реакції на зміну завдання
    float ff_out = pid->k_ff * target_rate;

    // Диференційна ланка: D-on-Measurement з фільтрацією PT1
    float raw_d = -(meas_rate - pid->prev_meas) / dt;
    pid->prev_meas = meas_rate;
    float filtered_d = pt1_update(&pid->d_filter, raw_d);
    float d_out = pid->kd * filtered_d;

    // Сума ланок без інтеграла
    float u_no_i = p_out + d_out + ff_out;

    // Інтегральна ланка з умовним інтегруванням (Conditional Integration Anti-Windup)
    float new_i = pid->i_term + (pid->ki * error * dt);
    if (new_i > pid->i_max) new_i = pid->i_max;
    if (new_i < -pid->i_max) new_i = -pid->i_max;

    float potential_out = u_no_i + new_i;
    bool saturated = (potential_out > pid->out_max && error > 0.0f) ||
                     (potential_out < -pid->out_max && error < 0.0f);

    if (!saturated) {
        pid->i_term = new_i;
    }

    // Підсумкове обмеження вихідного зусилля
    float output = u_no_i + pid->i_term;
    if (output > pid->out_max) output = pid->out_max;
    if (output < -pid->out_max) output = -pid->out_max;

    return output;
}

typedef struct {
    float kp;
    float max_rate;
} AnglePID;

static inline float angle_pid_update(const AnglePID *pid, float target_angle, float meas_angle) {
    float error = target_angle - meas_angle;
    float target_rate = pid->kp * error;
    if (target_rate > pid->max_rate) target_rate = pid->max_rate;
    if (target_rate < -pid->max_rate) target_rate = -pid->max_rate;
    return target_rate;
}

int main(void) {
    const float dt_sim = 0.001f;     // Базовий крок симуляції (1000 Гц)
    const float sim_time = 2.0f;     // Тривалість 2.0 секунди
    const int total_steps = (int)(sim_time / dt_sim);

    // Фізичні константи обертального важеля
    float angle_rad = 0.0f;
    float rate_rad_s = 0.0f;
    const float inertia = 0.005f;    // кг·м²
    const float arm_length = 0.15f;  // м
    const float motor_tau = 0.03f;   // Стала часу мотора (30 мс)
    float motor_thrust_diff = 0.0f;

    // Ініціалізація регуляторів
    RatePID rate_pid;
    rate_pid_init(&rate_pid, 0.18f, 0.25f, 0.004f, 0.02f, 0.3f, 1.0f, 60.0f, dt_sim);

    AnglePID angle_pid = { .kp = 6.5f, .max_rate = 4.0f };

    const float target_angle = 0.35f; // Уставка кута: 0.35 рад (~20 градусів)
    float target_rate = 0.0f;

    for (int step = 0; step < total_steps; ++step) {
        float t = (float)step * dt_sim;

        // Зовнішній контур Angle loop викликається кожні 4 кроки (250 Гц)
        if (step % 4 == 0) {
            target_rate = angle_pid_update(&angle_pid, target_angle, angle_rad);
        }

        // Внутрішній контур Rate loop викликається щокроку (1000 Гц)
        float control_cmd = rate_pid_update(&rate_pid, target_rate, rate_rad_s, dt_sim);

        // Динаміка зміни тяги моторів через перехідний процес першого порядку
        float target_thrust_diff = control_cmd * 2.0f;
        motor_thrust_diff += (dt_sim / motor_tau) * (target_thrust_diff - motor_thrust_diff);

        // Ступінчасте збурення вітром на інтервалі 1.0–1.3 с
        float wind_torque = 0.0f;
        if (t >= 1.0f && t <= 1.3f) {
            wind_torque = 0.08f; // Зовнішній момент 0.08 Н·м
        }

        // Сумарний момент і розрахунок кутового прискорення
        float total_torque = (motor_thrust_diff * arm_length) + wind_torque;
        float angular_accel = total_torque / inertia;

        // Чисельне інтегрування динаміки руху (метод Ейлера)
        rate_rad_s += angular_accel * dt_sim;
        angle_rad += rate_rad_s * dt_sim;
    }

    return 0;
}
