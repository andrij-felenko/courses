#include "bumpless_pid.h"

#include "ramp.h"

#include <math.h>
#include <stdio.h>

static float clampf(float value, float lo, float hi)
{
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

void bumpless_pid_safe_i_limits(const pid_config_t *cfg,
                                float *i_min_safe, float *i_max_safe)
{
    /* Запас, який лишаємо пропорційній ланці. Якщо передзавантажити інтегратор
       упритул до упора приводу, перша ж помилка нового режиму не матиме куди
       рости — і контур піде в розкручування інтеграла. */
    const float margin = cfg->kp * cfg->max_expected_noise;
    float lo = cfg->i_min;
    float hi = cfg->i_max;

    if (cfg->out_min + margin > lo) lo = cfg->out_min + margin;
    if (cfg->out_max - margin < hi) hi = cfg->out_max - margin;

    if (lo > hi) {
        /* Запас ширший за весь хід приводу: коефіцієнти нереальні. Межі не
           вивертаємо — стягуємо в точку, регулятор лишиться без інтеграла. */
        const float mid = 0.5f * (lo + hi);
        lo = mid;
        hi = mid;
    }

    *i_min_safe = lo;
    *i_max_safe = hi;
}

void bumpless_pid_reset(bumpless_pid_t *pid)
{
    pid->integral = 0.0f;
    pid->prev_measurement = 0.0f;
    pid->deriv_filt = 0.0f;
    pid->target_setpoint = 0.0f;
    pid->current_setpoint = 0.0f;
    pid->last_output = 0.0f;
    pid->is_initialized = false;
    pid->faults = PID_FAULT_NONE;
}

void bumpless_pid_init(bumpless_pid_t *pid, const pid_config_t *cfg)
{
    pid->cfg = *cfg;
    bumpless_pid_reset(pid);
}

void bumpless_pid_start_naive(bumpless_pid_t *pid, float setpoint)
{
    bumpless_pid_reset(pid);
    pid->target_setpoint = setpoint;
    pid->current_setpoint = setpoint;
    pid->is_initialized = true;
}

/* Спільне ядро обох варіантів передачі повноважень. */
static void preload(bumpless_pid_t *pid, float measurement, float hold_setpoint,
                    float target_setpoint, float prev_output)
{
    if (!isfinite(measurement) || !isfinite(prev_output) ||
        !isfinite(hold_setpoint) || !isfinite(target_setpoint)) {
        /* Захоплення не відбулося. Диспетчер режимів мусить побачити прапорець
           і лишитися в попередньому режимі: краще старий контур, ніж контур,
           передзавантажений сміттям. */
        pid->faults |= PID_FAULT_BAD_MEASUREMENT;
        return;
    }

    /* Крок 1. Відстеження уставки: у типовому виклику hold_setpoint і є
       поточним виміром, тож помилка на першому такті дорівнює нулю. */
    pid->current_setpoint = hold_setpoint;
    pid->target_setpoint = target_setpoint;

    /* Крок 2. Пам'ять диференціатора прирівнюємо до факту. */
    pid->prev_measurement = measurement;
    pid->deriv_filt = 0.0f;

    const float error = pid->current_setpoint - measurement;
    const float p_term = pid->cfg.kp * error;
    const float d_term = -pid->cfg.kd * pid->deriv_filt; /* тотожно 0, лишаємо у формулі */
    const float ff_term = pid->cfg.kff * pid->current_setpoint;

    /* Крок 3. I(0+) = u_prev - P - D - FF. */
    const float needed_i = prev_output - p_term - d_term - ff_term;

    float i_lo = 0.0f;
    float i_hi = 0.0f;
    bumpless_pid_safe_i_limits(&pid->cfg, &i_lo, &i_hi);
    pid->integral = clampf(needed_i, i_lo, i_hi);

    if (fabsf(pid->integral - needed_i) > 1e-6f) {
        /* Привід стояв у насиченні: точний перехід неможливий, залишковий
           стрибок дорівнює зрізаній частині. Телеметрія має це знати. */
        pid->faults |= PID_FAULT_PRELOAD_CLAMPED;
    }

    pid->last_output = clampf(p_term + pid->integral + d_term + ff_term,
                              pid->cfg.out_min, pid->cfg.out_max);
    pid->is_initialized = true;
}

void bumpless_pid_handover(bumpless_pid_t *pid, float current_measurement,
                           float target_setpoint, float prev_actuator_output)
{
    preload(pid, current_measurement, current_measurement,
            target_setpoint, prev_actuator_output);
}

void bumpless_pid_handover_hold(bumpless_pid_t *pid, float current_measurement,
                                float hold_setpoint, float target_setpoint,
                                float prev_actuator_output)
{
    preload(pid, current_measurement, hold_setpoint,
            target_setpoint, prev_actuator_output);
}

float bumpless_pid_update(bumpless_pid_t *pid, float measurement, float dt)
{
    if (!pid->is_initialized) {
        pid->faults |= PID_FAULT_NOT_READY;
        return pid->last_output;
    }
    if (!isfinite(measurement)) {
        /* Збій шини давача. Інтегратор не рухаємо взагалі: тримаємо останній
           справний вихід — завмерла поверхня краща за перекладку в NaN. */
        pid->faults |= PID_FAULT_BAD_MEASUREMENT;
        return pid->last_output;
    }
    if (!isfinite(dt) || dt <= 0.0f) {
        pid->faults |= PID_FAULT_BAD_DT;
        return pid->last_output;
    }
    if (dt > PID_DT_MAX) {
        pid->faults |= PID_FAULT_BAD_DT;
        dt = PID_DT_MAX;
    }

    /* 1. Ремпінг уставки. */
    pid->current_setpoint = ramp_slew_step(pid->current_setpoint,
                                           pid->target_setpoint,
                                           pid->cfg.slew_rate_max * dt);

    /* 2. Пропорційна складова. */
    const float error = pid->current_setpoint - measurement;
    const float p_term = pid->cfg.kp * error;

    /* 3. Похідна ВИМІРУ, ще й згладжена: диференціювання помилки давало б
          удар на кожній зміні уставки, а сира похідна — на кожному шумі. */
    const float d_raw = (measurement - pid->prev_measurement) / dt;
    pid->prev_measurement = measurement;
    const float alpha = (pid->cfg.d_lpf_tau > 0.0f)
                            ? dt / (dt + pid->cfg.d_lpf_tau)
                            : 1.0f;
    pid->deriv_filt += alpha * (d_raw - pid->deriv_filt);
    const float d_term = -pid->cfg.kd * pid->deriv_filt;

    /* 4. Пряме прогнозне керування. */
    const float ff_term = pid->cfg.kff * pid->current_setpoint;

    /* 5. Пробне інтегрування — у стан його ще не пишемо. */
    const float i_candidate = clampf(pid->integral + pid->cfg.ki * error * dt,
                                     pid->cfg.i_min, pid->cfg.i_max);
    const float u_raw = p_term + i_candidate + d_term + ff_term;

    /* 6. Анти-віндап затиском: приймаємо новий інтеграл лише тоді, коли він
          не штовхає вже насичений вихід іще далі за упор. */
    const bool pushing_up = (u_raw > pid->cfg.out_max) && (i_candidate > pid->integral);
    const bool pushing_down = (u_raw < pid->cfg.out_min) && (i_candidate < pid->integral);
    if (!pushing_up && !pushing_down) {
        pid->integral = i_candidate;
    }

    /* 7. Фізична межа ходу приводу. */
    const float u_final = clampf(u_raw, pid->cfg.out_min, pid->cfg.out_max);
    if (u_final != u_raw) {
        pid->faults |= PID_FAULT_OUTPUT_SATURATED;
    }

    pid->last_output = u_final;
    return u_final;
}

void pid_fault_names(unsigned faults, char *out, size_t cap)
{
    static const char *const NAMES[5] = {
        "BAD_MEASUREMENT", "BAD_DT", "PRELOAD_CLAMPED", "NOT_READY", "OUTPUT_SATURATED"
    };

    if (cap == 0u) {
        return;
    }
    out[0] = '\0';
    if (faults == PID_FAULT_NONE) {
        snprintf(out, cap, "%s", "-");
        return;
    }

    size_t len = 0;
    for (unsigned i = 0; i < 5u; ++i) {
        if ((faults & (1u << i)) == 0u) {
            continue;
        }
        const int written = snprintf(out + len, cap - len, "%s%s",
                                     (len > 0u) ? "|" : "", NAMES[i]);
        if (written <= 0 || (size_t)written >= cap - len) {
            break; /* рядок телеметрії скінчився — решту прапорців обрізаємо */
        }
        len += (size_t)written;
    }
}
