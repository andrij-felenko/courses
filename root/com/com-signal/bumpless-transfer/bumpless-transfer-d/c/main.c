#include <stdbool.h>

typedef enum {
    PID_MODE_MANUAL,
    PID_MODE_TRACKING,
    PID_MODE_AUTO
} pid_mode_t;

typedef struct {
    // Коефіцієнти підсилення
    float kp;
    float ki;
    float kd;
    float kt;          // Коефіцієнт стеження інтегратора (1 / Tt)
    float b_weight;    // Вага уставки для P-складової (0.0 ... 1.0)
    float tf_d;        // Стала часу ФНЧ похідної

    // Обмеження актуатора
    float u_min;
    float u_max;
    float ramp_rate;   // Максимальна швидкість зміни уставки (од/с)

    // Внутрішній стан (пам'ять регулятора)
    float integrator;
    float y_prev;
    float deriv_filtered;
    float r_filtered;
    pid_mode_t mode;
} bumpless_pid_t;

static inline float clampf(float val, float min, float max) {
    if (val < min) return min;
    if (val > max) return max;
    return val;
}

// Зміна Kp "на льоту" з інтегральною компенсацією стрибка
void pid_set_kp_bumpless(bumpless_pid_t *pid, float new_kp, float error) {
    if (pid->mode == PID_MODE_AUTO) {
        // Компенсуємо стан інтегратора, щоб зберегти суму Kp*e + I неперервною
        pid->integrator -= (new_kp - pid->kp) * error;
    }
    pid->kp = new_kp;
}

// Один дискретний такт регулятора
float pid_step(bumpless_pid_t *pid, float r_raw, float y, float u_manual, float dt) {
    // 1. Профілювання уставки (Setpoint Ramping)
    float max_delta_r = pid->ramp_rate * dt;
    float delta_r = r_raw - pid->r_filtered;
    pid->r_filtered += clampf(delta_r, -max_delta_r, max_delta_r);

    // 2. Розрахунок помилки
    float e = pid->r_filtered - y;

    // 3. Диференційна складова від виміру (Derivative on PV) з фільтром
    float dy = (y - pid->y_prev) / dt;
    float alpha_d = dt / (dt + pid->tf_d);
    pid->deriv_filtered += alpha_d * (-dy - pid->deriv_filtered);
    pid->y_prev = y;

    // 4. Обробка режимів ручного керування та стеження
    if (pid->mode == PID_MODE_MANUAL || pid->mode == PID_MODE_TRACKING) {
        float u_act = clampf(u_manual, pid->u_min, pid->u_max);

        // Алгебраїчне узгодження інтегратора для миттєвого безударного переходу
        // u_calc = Kp*(b*r - y) + I + Kd*deriv_filtered == u_act
        float u_p_term = pid->kp * (pid->b_weight * pid->r_filtered - y);
        float u_d_term = pid->kd * pid->deriv_filtered;
        pid->integrator = u_act - u_p_term - u_d_term;

        return u_act;
    }

    // 5. Автоматичний режим (PID_MODE_AUTO)
    float u_p = pid->kp * (pid->b_weight * pid->r_filtered - y);
    float u_d = pid->kd * pid->deriv_filtered;
    float u_calc = u_p + pid->integrator + u_d;

    // Обмеження виходу фізичними межами актуатора
    float u_act = clampf(u_calc, pid->u_min, pid->u_max);

    // 6. Оновлення інтегратора з контуром Back-Calculation Anti-Windup / Tracking
    float tracking_error = u_act - u_calc;
    pid->integrator += (pid->ki * e + pid->kt * tracking_error) * dt;

    return u_act;
}
