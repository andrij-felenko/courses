#include "hil.h"

#include "bumpless_pid.h"
#include "plant.h"

#include <math.h>

#define HIL_DT 0.0025f

/* Бібліотека режимів для тесту нульового стрибка: різні коефіцієнти, різний
   прогнозний внесок, однакові межі приводу — щоб трим переходив із рук у руки. */
static const pid_config_t MODE_LIBRARY[4] = {
    { .kp = 0.60f, .ki = 0.90f, .kd = 0.05f, .kff = 0.00f,
      .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
      .slew_rate_max = 30.0f, .d_lpf_tau = 0.02f, .max_expected_noise = 0.02f },
    { .kp = 0.18f, .ki = 0.25f, .kd = 0.30f, .kff = 0.15f,
      .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
      .slew_rate_max = 5.0f, .d_lpf_tau = 0.05f, .max_expected_noise = 0.03f },
    { .kp = 1.20f, .ki = 0.05f, .kd = 0.00f, .kff = 0.00f,
      .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
      .slew_rate_max = 0.0f, .d_lpf_tau = 0.00f, .max_expected_noise = 0.01f },
    { .kp = 0.35f, .ki = 1.40f, .kd = 0.12f, .kff = 0.40f,
      .out_min = -1.0f, .out_max = 1.0f, .i_min = -0.95f, .i_max = 0.95f,
      .slew_rate_max = 2.5f, .d_lpf_tau = 0.03f, .max_expected_noise = 0.05f },
};

static pid_config_t altitude_hold_config(void)
{
    pid_config_t cfg;
    cfg.kp = 0.10f;
    cfg.ki = 0.06f;
    cfg.kd = 0.15f;
    cfg.kff = 0.0f;
    cfg.out_min = 0.0f;
    cfg.out_max = 1.0f;
    cfg.i_min = 0.0f;
    cfg.i_max = 0.95f;
    cfg.slew_rate_max = 2.5f;
    cfg.d_lpf_tau = 0.05f;
    cfg.max_expected_noise = 0.05f;
    return cfg;
}

/* 1. Тест нульового стрибка: 50 перемикань між усіма режимами по колу.
      Вимір навмисно тримаємо сталим — тест судить алгоритм, а не фізику:
      якби апарат між тактами рухався, P і D дали б цілком законний внесок. */
static void run_glitch_test(hil_report_t *rep)
{
    const float measurement = 0.30f; /* збурений стаціонар: вітер вимагає триму */
    float u_prev = 0.30f;

    rep->switch_count = 50u;
    rep->glitch_limit = 1e-4f;
    rep->glitch_worst = 0.0f;

    for (unsigned i = 0; i < rep->switch_count; ++i) {
        const pid_config_t *cfg = &MODE_LIBRARY[i % 4u];

        bumpless_pid_t pid;
        bumpless_pid_init(&pid, cfg);
        bumpless_pid_handover(&pid, measurement, measurement, u_prev);

        const float u = bumpless_pid_update(&pid, measurement, HIL_DT);
        const float glitch = fabsf(u - u_prev);
        if (glitch > rep->glitch_worst) {
            rep->glitch_worst = glitch;
        }

        /* Наступний режим приймає повноваження вже з рук цього. */
        u_prev = u;
    }

    rep->glitch_pass = (rep->glitch_worst < rep->glitch_limit);
}

/* 2. Тест насиченого передзавантаження: привід стоїть на упорі 100 %,
      апарат розігнаний угору, вмикається утримання висоти. */
static void run_saturated_test(hil_report_t *rep)
{
    quad_plant_t plant;
    quad_plant_init(&plant, 1.8f, 0.52f, 60.0f);
    for (int i = 0; i < 400; ++i) { /* 1 с повного газу — вертикальний розгін */
        quad_plant_step(&plant, 1.0f, HIL_DT);
    }

    const pid_config_t cfg = altitude_hold_config();
    bumpless_pid_t pid;
    bumpless_pid_init(&pid, &cfg);
    bumpless_pid_handover(&pid, plant.altitude_m, plant.altitude_m, 1.0f);

    float i_lo = 0.0f;
    float i_hi = 0.0f;
    bumpless_pid_safe_i_limits(&cfg, &i_lo, &i_hi);

    const float preloaded = bumpless_pid_integral(&pid);
    const float u_start = bumpless_pid_last_output(&pid);
    rep->saturated_residual = fabsf(1.0f - u_start);

    float min_integral = preloaded;
    float u_after_10 = u_start;

    const int steps = (int)(3.0f / HIL_DT);
    for (int i = 0; i < steps; ++i) {
        const float u = bumpless_pid_update(&pid, plant.altitude_m, HIL_DT);
        if (i == 9) {
            u_after_10 = u;
        }
        if (bumpless_pid_integral(&pid) < min_integral) {
            min_integral = bumpless_pid_integral(&pid);
        }
        quad_plant_step(&plant, u, HIL_DT);
    }

    rep->saturated_first_delta = u_after_10 - u_start;
    rep->saturated_integral_drop = preloaded - min_integral;

    /* Залишковий стрибок не може бути меншим за резерв, який ми свідомо
       лишили пропорційній ланці, — але й більшим ставати не має права. */
    const float irreducible = cfg.out_max - i_hi;
    rep->saturated_pass =
        (rep->saturated_residual <= irreducible + 1e-4f) &&
        ((bumpless_pid_faults(&pid) & PID_FAULT_PRELOAD_CLAMPED) != 0u) &&
        (rep->saturated_first_delta < 0.0f) &&
        (rep->saturated_integral_drop > 0.01f);
}

/* 3. Тест темпу наростання: після захоплення місія просить +200 м. */
static void run_ramping_test(hil_report_t *rep)
{
    const float hover = 0.52f;
    quad_plant_t plant;
    quad_plant_init(&plant, 1.8f, hover, 25.0f);
    for (int i = 0; i < 400; ++i) {
        quad_plant_step(&plant, hover, HIL_DT);
    }

    const pid_config_t cfg = altitude_hold_config();
    bumpless_pid_t pid;
    bumpless_pid_init(&pid, &cfg);
    bumpless_pid_handover(&pid, plant.altitude_m, plant.altitude_m + 200.0f, hover);

    rep->ramp_allowed_setpoint_step = cfg.slew_rate_max * HIL_DT;
    rep->ramp_peak_setpoint_step = 0.0f;
    rep->ramp_peak_load_g = 1.0f;
    rep->ramp_min_load_g = 1.0f;
    rep->ramp_max_saturated_run = 0u;

    float prev_sp = bumpless_pid_setpoint(&pid);
    unsigned saturated_run = 0u;

    const int steps = (int)(100.0f / HIL_DT);
    for (int i = 0; i < steps; ++i) {
        const float u = bumpless_pid_update(&pid, plant.altitude_m, HIL_DT);

        const float sp = bumpless_pid_setpoint(&pid);
        const float sp_step = fabsf(sp - prev_sp);
        prev_sp = sp;
        if (sp_step > rep->ramp_peak_setpoint_step) {
            rep->ramp_peak_setpoint_step = sp_step;
        }

        if (u >= cfg.out_max - 1e-6f) {
            ++saturated_run;
            if (saturated_run > rep->ramp_max_saturated_run) {
                rep->ramp_max_saturated_run = saturated_run;
            }
        } else {
            saturated_run = 0u;
        }

        quad_plant_step(&plant, u, HIL_DT);

        const float n = quad_plant_load_factor(&plant);
        if (n > rep->ramp_peak_load_g) rep->ramp_peak_load_g = n;
        if (n < rep->ramp_min_load_g) rep->ramp_min_load_g = n;
    }

    /* Пік струму моторів прямо не міряємо — його заступником є найдовша
       серія тактів на упорі газу: саме там мотор тягне пусковий струм. */
    rep->ramp_pass =
        (rep->ramp_peak_setpoint_step <= rep->ramp_allowed_setpoint_step * 1.001f) &&
        (rep->ramp_peak_load_g <= 2.5f) &&
        (rep->ramp_min_load_g >= -0.5f) &&
        (rep->ramp_max_saturated_run < (unsigned)(0.5f / HIL_DT));
}

void hil_run(hil_report_t *rep)
{
    run_glitch_test(rep);
    run_saturated_test(rep);
    run_ramping_test(rep);
}

bool hil_all_passed(const hil_report_t *rep)
{
    return rep->glitch_pass && rep->saturated_pass && rep->ramp_pass;
}
