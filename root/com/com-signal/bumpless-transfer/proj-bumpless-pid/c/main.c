#include <stdio.h>
#include <stdbool.h>
#include <math.h>

// Режими роботи регулятора
typedef enum {
    BUMPLESS_MODE_MANUAL   = 0,
    BUMPLESS_MODE_TRACKING = 1,
    BUMPLESS_MODE_AUTO     = 2
} bumpless_mode_t;

// Конфігураційні параметри регулятора
typedef struct {
    float kp;             // Пропорційний коефіцієнт
    float ki;             // Інтегральний коефіцієнт
    float kd;             // Диференціальний коефіцієнт
    float kt;             // Коефіцієнт контуру узгодження (1 / Tt)
    float b_weight;       // Вага уставки для P-каналу (0.0 ... 1.0)
    float tf_deriv;       // Стала часу фільтра похідної (с)
    float u_min;          // Нижня фізична межа актуатора
    float u_max;          // Верхня фізична межа актуатора
    float ramp_rate_max;  // Максимальна швидкість зміни уставки (од/с)
} bumpless_pid_config_t;

// Стан (пам'ять) регулятора між тактами
typedef struct {
    bumpless_pid_config_t cfg;
    bumpless_mode_t mode;

    float integrator;      // Накопичений стан інтегратора
    float y_prev;          // Попереднє значення виміру для похідної
    float deriv_filt;      // Відфільтрована похідна від виміру
    float r_filt;          // Відфільтрована (профільована) уставка
    float u_last;          // Останній фактично виданий сигнал на актуатор
    bool is_initialized;   // Прапорець первинної ініціалізації
} bumpless_pid_t;

static inline float pid_clamp(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

// Ініціалізація структури регулятора
void bumpless_pid_init(bumpless_pid_t *pid, const bumpless_pid_config_t *cfg, float initial_y) {
    if (!pid || !cfg) return;
    pid->cfg = *cfg;
    pid->mode = BUMPLESS_MODE_MANUAL;
    pid->integrator = 0.0f;
    pid->y_prev = initial_y;
    pid->deriv_filt = 0.0f;
    pid->r_filt = initial_y;
    pid->u_last = 0.0f;
    pid->is_initialized = true;
}

// Перемикання режиму роботи
void bumpless_pid_set_mode(bumpless_pid_t *pid, bumpless_mode_t new_mode) {
    if (!pid) return;
    pid->mode = new_mode;
}

// Безударна зміна пропорційного коефіцієнта (Gain Scheduling)
void bumpless_pid_set_gains(bumpless_pid_t *pid, float new_kp, float new_ki, float new_kd) {
    if (!pid) return;
    
    // Якщо регулятор активний, компенсуємо стрибок пропорційної складової в інтеграторі
    if (pid->mode == BUMPLESS_MODE_AUTO) {
        float current_error = pid->r_filt - pid->y_prev;
        float delta_kp = new_kp - pid->cfg.kp;
        pid->integrator -= delta_kp * current_error;
    }
    
    pid->cfg.kp = new_kp;
    pid->cfg.ki = new_ki;
    pid->cfg.kd = new_kd;
}

// Один дискретний крок обчислення регулятора
float bumpless_pid_step(bumpless_pid_t *pid, float r_target, float y_meas, float u_manual, float dt) {
    if (!pid || !pid->is_initialized || dt <= 0.0f) return 0.0f;

    // 1. Профілювання уставки (Slew-rate limiting)
    float max_step = pid->cfg.ramp_rate_max * dt;
    float delta_r = r_target - pid->r_filt;
    pid->r_filt += pid_clamp(delta_r, -max_step, max_step);

    // 2. Розрахунок помилки
    float e = pid->r_filt - y_meas;

    // 3. Диференціальна складова від виміру (Derivative on Measurement)
    float dy = (y_meas - pid->y_prev) / dt;
    float alpha_d = dt / (dt + pid->cfg.tf_deriv);
    pid->deriv_filt += alpha_d * (-dy - pid->deriv_filt);
    pid->y_prev = y_meas;

    // 4. Обробка ручного режиму або режиму стеження
    if (pid->mode == BUMPLESS_MODE_MANUAL || pid->mode == BUMPLESS_MODE_TRACKING) {
        float u_act = pid_clamp(u_manual, pid->cfg.u_min, pid->cfg.u_max);
        
        // Зворотний перерахунок інтегратора для забезпечення тотожності u_calc == u_act
        float u_p = pid->cfg.kp * (pid->cfg.b_weight * pid->r_filt - y_meas);
        float u_d = pid->cfg.kd * pid->deriv_filt;
        pid->integrator = u_act - u_p - u_d;
        
        pid->u_last = u_act;
        return u_act;
    }

    // 5. Автоматичний режим (2-DoF PID)
    float u_p = pid->cfg.kp * (pid->cfg.b_weight * pid->r_filt - y_meas);
    float u_d = pid->cfg.kd * pid->deriv_filt;
    float u_calc = u_p + pid->integrator + u_d;

    // 6. Обмеження виходу фізичними межами актуатора
    float u_act = pid_clamp(u_calc, pid->cfg.u_min, pid->cfg.u_max);

    // 7. Оновлення інтегратора з компенсацією насичення (Back-calculation Anti-windup)
    float tracking_diff = u_act - u_calc;
    pid->integrator += (pid->cfg.ki * e + pid->cfg.kt * tracking_diff) * dt;

    pid->u_last = u_act;
    return u_act;
}
