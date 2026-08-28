#include <stdbool.h>
#include <math.h>

typedef struct {
    float kp;
    float ki;
    float kd;
    float kff;
    float out_min;
    float out_max;
    float i_min;
    float i_max;
    float slew_rate_max; // максимальна швидкість зміни уставки [од/с], 0 = без ремпінгу
} pid_config_t;

typedef struct {
    pid_config_t cfg;
    float integral;
    float prev_measurement;
    float target_setpoint;   // кінцева цільова уставка
    float current_setpoint;  // згладжена уставка після ремпінгу
    float last_output;
    bool  is_initialized;
} bumpless_pid_t;

static inline float clampf(float val, float min_val, float max_val) {
    if (val < min_val) return min_val;
    if (val > max_val) return max_val;
    return val;
}

void bumpless_pid_init(bumpless_pid_t *pid, const pid_config_t *cfg) {
    pid->cfg = *cfg;
    pid->integral = 0.0f;
    pid->prev_measurement = 0.0f;
    pid->target_setpoint = 0.0f;
    pid->current_setpoint = 0.0f;
    pid->last_output = 0.0f;
    pid->is_initialized = false;
}

// Функція безривкового переходу: викликається ОДИН РАЗ у момент активації режиму
void bumpless_pid_handover(bumpless_pid_t *pid, float current_measurement,
                          float target_setpoint, float prev_actuator_output) {
    // 1. Прив'язуємо поточну уставку до факту, кінцеву ціль виставляємо для ремпінгу
    pid->current_setpoint = current_measurement;
    pid->target_setpoint = target_setpoint;

    // 2. Знешкоджуємо диференційний стрибок
    pid->prev_measurement = current_measurement;

    // 3. Рахуємо пропорційний та прогнозне внески в момент передачі
    float error = pid->current_setpoint - current_measurement; // = 0.0
    float p_term = pid->cfg.kp * error;
    float ff_term = pid->cfg.kff * pid->current_setpoint;

    // 4. Передзавантажуємо інтегратор, щоб замкнути рівність u_new == prev_output
    float needed_i = prev_actuator_output - p_term - ff_term;
    pid->integral = clampf(needed_i, pid->cfg.i_min, pid->cfg.i_max);

    pid->last_output = prev_actuator_output;
    pid->is_initialized = true;
}

// Періодичний крок регулятора: викликається з кроком dt
float bumpless_pid_update(bumpless_pid_t *pid, float measurement, float dt) {
    if (!pid->is_initialized || dt <= 0.0f) {
        return pid->last_output;
    }

    // 1. Ремпінг уставки (Slew Rate Limiting)
    if (pid->cfg.slew_rate_max > 0.0f) {
        float max_step = pid->cfg.slew_rate_max * dt;
        float delta = pid->target_setpoint - pid->current_setpoint;
        if (delta > max_step) {
            pid->current_setpoint += max_step;
        } else if (delta < -max_step) {
            pid->current_setpoint -= max_step;
        } else {
            pid->current_setpoint = pid->target_setpoint;
        }
    } else {
        pid->current_setpoint = pid->target_setpoint;
    }

    // 2. Пропорційна складова
    float error = pid->current_setpoint - measurement;
    float p_term = pid->cfg.kp * error;

    // 3. Диференційна складова за виміром (без похідного удару)
    float d_meas = (measurement - pid->prev_measurement) / dt;
    pid->prev_measurement = measurement;
    float d_term = -pid->cfg.kd * d_meas;

    // 4. Пряме прогнозне керування
    float ff_term = pid->cfg.kff * pid->current_setpoint;

    // 5. Пробне оновлення інтегратора
    float candidate_i = pid->integral + pid->cfg.ki * error * dt;

    // 6. Необмежений вихід
    float u_raw = p_term + candidate_i + d_term + ff_term;

    // 7. Анти-віндап затиск (Clamping)
    bool sat_high = (u_raw > pid->cfg.out_max) && (error > 0.0f);
    bool sat_low  = (u_raw < pid->cfg.out_min) && (error < 0.0f);
    if (!sat_high && !sat_low) {
        pid->integral = clampf(candidate_i, pid->cfg.i_min, pid->cfg.i_max);
    }

    // 8. Фізичне обмеження виходу
    float u_out = clampf(u_raw, pid->cfg.out_min, pid->cfg.out_max);
    pid->last_output = u_out;
    return u_out;
}
