#include <stdint.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    // Коефіцієнти підсилення
    float kp;
    float ki;
    float kd;
    float kff;

    // Стан інтегратора та фільтрів
    float integrator;
    float prev_gyro;
    float prev_setpoint;
    float dterm_filtered;

    // Параметри фільтрації та обмеження
    float dterm_lpf_alpha;  // Коефіцієнт згладжування PT1
    float out_min;          // Мінімальний вихід моменту (-1.0f)
    float out_max;          // Максимальний вихід моменту (+1.0f)
    float i_limit;          // Поріг насичення інтегратора
} RatePidController;

static inline float constrain_f(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

// Ініціалізація структури регулятора
void rate_pid_init(RatePidController *pid, float kp, float ki, float kd, float kff,
                   float cutoff_hz, float loop_rate_hz) {
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->kff = kff;

    pid->integrator = 0.0f;
    pid->prev_gyro = 0.0f;
    pid->prev_setpoint = 0.0f;
    pid->dterm_filtered = 0.0f;

    pid->out_min = -1.0f;
    pid->out_max = 1.0f;
    pid->i_limit = 0.35f; // Інтегратор не може займати більше 35% тяги

    // Розрахунок коефіцієнта PT1 фільтра: alpha = dt / (RC + dt)
    float dt = 1.0f / loop_rate_hz;
    float rc = 1.0f / (2.0f * 3.14159265f * cutoff_hz);
    pid->dterm_lpf_alpha = dt / (rc + dt);
}

// Основний крок обчислення моменту (викликається в циклі 1-8 кГц)
float rate_pid_update(RatePidController *pid, float setpoint_dps, float gyro_dps,
                      float dt, bool enable_i) {
    // 1. Помилка кутової швидкості
    float error = setpoint_dps - gyro_dps;

    // 2. Пропорційна складова
    float p_out = pid->kp * error;

    // 3. Диференційна складова (Derivative on Measurement)
    // Диференціюємо зміну виміру гіроскопа, а не помилку
    float gyro_delta = (gyro_dps - pid->prev_gyro) / dt;
    pid->prev_gyro = gyro_dps;

    float raw_dterm = -pid->kd * gyro_delta;

    // Проходження крізь PT1 низькочастотний фільтр D-терма
    pid->dterm_filtered += pid->dterm_lpf_alpha * (raw_dterm - pid->dterm_filtered);

    // 4. Прямий зв'язок (Feedforward) за швидкістю зміни стіка
    float sp_delta = (setpoint_dps - pid->prev_setpoint) / dt;
    pid->prev_setpoint = setpoint_dps;
    float ff_out = pid->kff * sp_delta;

    // 5. Інтегральна складова із захистом від насичення (Anti-Windup)
    if (enable_i) {
        pid->integrator += pid->ki * error * dt;
        pid->integrator = constrain_f(pid->integrator, -pid->i_limit, pid->i_limit);
    } else {
        // Плавне обнулення інтегратора на землі
        pid->integrator *= 0.95f;
    }

    // 6. Сумування компонентів і загальне насичення
    float total_out = p_out + pid->integrator + pid->dterm_filtered + ff_out;
    return constrain_f(total_out, pid->out_min, pid->out_max);
}
