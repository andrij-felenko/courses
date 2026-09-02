#include "bumpless_pid.h"
#include "cascade.h"
#include "hil.h"
#include "plant.h"
#include "portable_irq.h"
#include "ramp.h"

#include <math.h>
#include <stdio.h>

#define DT_FAST 0.001f  /* внутрішній контур кута — 1 кГц */
#define DT_LOOP 0.0025f /* контур висоти — 2.5 мс, як у прикладі зі статті */

static float clampf(float value, float lo, float hi)
{
    if (value < lo) return lo;
    if (value > hi) return hi;
    return value;
}

static pid_config_t altitude_config(void)
{
    pid_config_t cfg;
    cfg.kp = 0.10f;   /* частка газу на метр помилки */
    cfg.ki = 0.06f;
    cfg.kd = 0.15f;   /* демпфування за вертикальною швидкістю */
    cfg.kff = 0.0f;
    cfg.out_min = 0.0f;
    cfg.out_max = 1.0f;
    cfg.i_min = 0.0f;
    cfg.i_max = 0.95f;
    cfg.slew_rate_max = 2.5f; /* м/с — паспортна швидкість набору */
    cfg.d_lpf_tau = 0.05f;
    cfg.max_expected_noise = 0.05f;
    return cfg;
}

/* ------------------------------------------------------------------ */
/* 1. Наївний перезапуск проти безривкового переходу                   */
/* ------------------------------------------------------------------ */

typedef struct {
    float first_output;
    float first_jump;
    float min_altitude;
    float max_altitude;
    float min_load_g;
    float settle_seconds;
} hold_stats_t;

static hold_stats_t run_altitude_hold(bool bumpless, float seconds)
{
    const float hover = 0.52f;

    quad_plant_t plant;
    quad_plant_init(&plant, 1.8f, hover, 25.0f);
    for (int i = 0; i < 400; ++i) { /* усталений висячий політ під ручним газом */
        quad_plant_step(&plant, hover, DT_LOOP);
    }

    const pid_config_t cfg = altitude_config();
    bumpless_pid_t pid;
    bumpless_pid_init(&pid, &cfg);

    const float h0 = plant.altitude_m;
    if (bumpless) {
        bumpless_pid_handover(&pid, h0, h0, hover);
    } else {
        /* Той самий «чистий аркуш»: уставка з місії, інтегратор нуль,
           пам'ять диференціатора порожня. */
        bumpless_pid_start_naive(&pid, h0);
    }

    hold_stats_t st;
    st.first_output = 0.0f;
    st.first_jump = 0.0f;
    st.min_altitude = h0;
    st.max_altitude = h0;
    st.min_load_g = 1.0f;
    st.settle_seconds = 0.0f;

    const int steps = (int)(seconds / DT_LOOP);
    for (int i = 0; i < steps; ++i) {
        const float u = bumpless_pid_update(&pid, plant.altitude_m, DT_LOOP);
        if (i == 0) {
            st.first_output = u;
            st.first_jump = fabsf(u - hover);
        }

        quad_plant_step(&plant, u, DT_LOOP);

        if (plant.altitude_m < st.min_altitude) st.min_altitude = plant.altitude_m;
        if (plant.altitude_m > st.max_altitude) st.max_altitude = plant.altitude_m;

        const float n = quad_plant_load_factor(&plant);
        if (n < st.min_load_g) st.min_load_g = n;

        /* Заспокоєнням вважаємо мить, після якої апарат уже не виходить
           за чверть метра від точки, в якій його застало перемикання. */
        if (fabsf(plant.altitude_m - h0) > 0.25f) {
            st.settle_seconds = (float)(i + 1) * DT_LOOP;
        }
    }
    return st;
}

/* ------------------------------------------------------------------ */
/* 2. Три генератори траєкторії                                        */
/* ------------------------------------------------------------------ */

typedef enum { RAMP_SLEW = 0, RAMP_LPF = 1, RAMP_SCURVE = 2 } ramp_method_t;

typedef struct {
    float peak_climb_mps;
    float peak_load_g;
    float time_to_target_s;
    float overshoot_m;
} ramp_stats_t;

static ramp_stats_t run_ramp(ramp_method_t method, float climb_m, float seconds)
{
    const float hover = 0.52f;

    quad_plant_t plant;
    quad_plant_init(&plant, 1.8f, hover, 25.0f);
    for (int i = 0; i < 400; ++i) {
        quad_plant_step(&plant, hover, DT_LOOP);
    }

    pid_config_t cfg = altitude_config();
    if (method != RAMP_SLEW) {
        /* Уставку формує зовнішній генератор — власний ремпінг контуру
           вимикаємо, інакше два обмежувачі різатимуть той самий сигнал. */
        cfg.slew_rate_max = 0.0f;
    }

    const float h0 = plant.altitude_m;
    const float goal = h0 + climb_m;

    bumpless_pid_t pid;
    bumpless_pid_init(&pid, &cfg);
    bumpless_pid_handover(&pid, h0, (method == RAMP_SLEW) ? goal : h0, hover);

    float shaped = h0;
    scurve_t curve;
    scurve_start(&curve, h0, goal, 2.5f, 1.5f, 2.0f);

    ramp_stats_t st;
    st.peak_climb_mps = 0.0f;
    st.peak_load_g = 1.0f;
    st.time_to_target_s = seconds;
    st.overshoot_m = 0.0f;

    bool reached = false;
    const int steps = (int)(seconds / DT_LOOP);
    for (int i = 0; i < steps; ++i) {
        if (method == RAMP_LPF) {
            shaped = ramp_lpf_step(shaped, goal, DT_LOOP, 1.5f);
            bumpless_pid_set_target(&pid, shaped);
        } else if (method == RAMP_SCURVE) {
            (void)scurve_step(&curve, DT_LOOP);
            bumpless_pid_set_target(&pid, curve.position);
        }

        const float u = bumpless_pid_update(&pid, plant.altitude_m, DT_LOOP);
        quad_plant_step(&plant, u, DT_LOOP);

        const float climb = fabsf(plant.vz_mps);
        if (climb > st.peak_climb_mps) st.peak_climb_mps = climb;

        const float n = quad_plant_load_factor(&plant);
        if (fabsf(n - 1.0f) > fabsf(st.peak_load_g - 1.0f)) st.peak_load_g = n;

        if (!reached && fabsf(plant.altitude_m - goal) < 0.30f) {
            reached = true;
            st.time_to_target_s = (float)(i + 1) * DT_LOOP;
        }
        if (plant.altitude_m - goal > st.overshoot_m) {
            st.overshoot_m = plant.altitude_m - goal;
        }
    }
    return st;
}

/* ------------------------------------------------------------------ */
/* 3. Каскад: наївний, розірваний і атомарний перехід                  */
/* ------------------------------------------------------------------ */

typedef enum { HANDOVER_NAIVE, HANDOVER_TORN, HANDOVER_ATOMIC } handover_kind_t;

typedef struct {
    float first_jump;
    float worst_jump;
    float max_drift_m;
    float max_angle_deg;
} cascade_stats_t;

/* Попередній режим: пілот тримає апарат простим ПД по куту. Інтегратора в
   нього немає, тож позицію він тримає з невеликим статичним зсувом — зате
   саме він напрацював ту команду приводу, яку каскад мусить успадкувати. */
static float manual_hold(const lat_plant_t *p)
{
    const float angle_cmd = clampf(-0.35f * p->position_m - 0.55f * p->velocity_mps,
                                   -0.40f, 0.40f);
    return clampf(6.0f * (angle_cmd - p->angle_rad), -1.0f, 1.0f);
}

static cascade_meas_t measure(const lat_plant_t *p)
{
    cascade_meas_t m;
    m.position_m = p->position_m;
    m.velocity_mps = p->velocity_mps;
    m.angle_rad = p->angle_rad;
    return m;
}

static cascade_config_t position_hold_config(void)
{
    cascade_config_t cfg;

    /* Контур позиції (20 Гц). Інтегратора не має навмисно: сталий трим
       тримає нижній поверх, дублювати його зверху немає потреби. */
    cfg.pos.kp = 0.50f; cfg.pos.ki = 0.0f; cfg.pos.kd = 0.0f; cfg.pos.kff = 0.0f;
    cfg.pos.out_min = -3.0f; cfg.pos.out_max = 3.0f;
    cfg.pos.i_min = -1.0f; cfg.pos.i_max = 1.0f;
    cfg.pos.slew_rate_max = 1.0f; cfg.pos.d_lpf_tau = 0.0f; cfg.pos.max_expected_noise = 0.05f;

    /* Контур швидкості (50 Гц): його вихід — уставка кута в радіанах. */
    cfg.vel.kp = 0.12f; cfg.vel.ki = 0.05f; cfg.vel.kd = 0.0f; cfg.vel.kff = 0.0f;
    cfg.vel.out_min = -0.35f; cfg.vel.out_max = 0.35f;
    cfg.vel.i_min = -0.35f; cfg.vel.i_max = 0.35f;
    cfg.vel.slew_rate_max = 0.0f; cfg.vel.d_lpf_tau = 0.0f; cfg.vel.max_expected_noise = 0.05f;

    /* Контур кута (1 кГц): його вихід — нормалізована команда на мотори. */
    cfg.ang.kp = 6.00f; cfg.ang.ki = 2.00f; cfg.ang.kd = 0.0f; cfg.ang.kff = 0.0f;
    cfg.ang.out_min = -1.0f; cfg.ang.out_max = 1.0f;
    cfg.ang.i_min = -1.0f; cfg.ang.i_max = 1.0f;
    cfg.ang.slew_rate_max = 0.0f; cfg.ang.d_lpf_tau = 0.0f; cfg.ang.max_expected_noise = 0.01f;

    cfg.vel_from_pos_gain = 1.0f;
    cfg.ang_from_vel_gain = 1.0f;
    cfg.pos_div = 50u;  /* 1 кГц / 50 = 20 Гц */
    cfg.vel_div = 20u;  /* 1 кГц / 20 = 50 Гц */
    return cfg;
}

static cascade_stats_t run_cascade(handover_kind_t kind, float seconds)
{
    lat_plant_t plant;
    lat_plant_init(&plant, 3.5f, 0.15f, 1.5f, 0.05f);

    float u_manual = 0.0f;
    for (int i = 0; i < (int)(12.0f / DT_FAST); ++i) {
        u_manual = manual_hold(&plant);
        lat_plant_step(&plant, u_manual, DT_FAST);
    }

    const cascade_config_t cfg = position_hold_config();
    cascade_t casc;
    cascade_init(&casc, &cfg);

    cascade_meas_t m = measure(&plant);
    const float target_position = 0.0f;
    const unsigned tear_ticks = 20u; /* 20 мс між половинами розірваної транзакції */

    switch (kind) {
    case HANDOVER_NAIVE:
        cascade_start_naive(&casc, target_position);
        break;
    case HANDOVER_TORN:
        /* Перемикання почалося в задачі 20 Гц і не встигло дійти до верхніх
           поверхів: швидкий контур уже працює, зовнішні ще ні. */
        cascade_load_inner(&casc, &m, u_manual);
        break;
    case HANDOVER_ATOMIC:
    default:
        cascade_handover(&casc, &m, target_position, u_manual);
        break;
    }

    cascade_stats_t st;
    st.first_jump = 0.0f;
    st.worst_jump = 0.0f;
    st.max_drift_m = fabsf(plant.position_m);
    st.max_angle_deg = fabsf(plant.angle_rad) * 180.0f / 3.14159265f;

    const int steps = (int)(seconds / DT_FAST);
    for (int i = 0; i < steps; ++i) {
        if (kind == HANDOVER_TORN && (unsigned)i == tear_ticks) {
            m = measure(&plant);
            cascade_load_outer(&casc, &m, target_position);
        }

        if (irq_locked()) {
            /* Транзакція перемикання ще триває — швидкий контур чесно
               відкладає свій такт, а не рахує на напівзавантаженому стані. */
            irq_note_deferred_tick();
            continue;
        }

        m = measure(&plant);
        const float u = cascade_update(&casc, &m, DT_FAST);

        const float jump = fabsf(u - u_manual);
        if (i == 0) st.first_jump = jump;
        if ((unsigned)i <= tear_ticks && jump > st.worst_jump) st.worst_jump = jump;

        lat_plant_step(&plant, u, DT_FAST);

        if (fabsf(plant.position_m) > st.max_drift_m) st.max_drift_m = fabsf(plant.position_m);
        const float angle_deg = fabsf(plant.angle_rad) * 180.0f / 3.14159265f;
        if (angle_deg > st.max_angle_deg) st.max_angle_deg = angle_deg;
    }
    return st;
}

/* ------------------------------------------------------------------ */
/* 4. Команда проти телеметрії вала                                    */
/* ------------------------------------------------------------------ */

typedef struct {
    float shaft_at_switch_deg;
    float first_command_deg;
    float extra_travel_deg;
} servo_stats_t;

static servo_stats_t run_servo_handover(bool use_telemetry)
{
    servo_t servo;
    servo_init(&servo, 400.0f, 0.3f, 0.0f); /* 0.15 с на 60 градусів */

    const float pilot_command = 25.0f;
    for (int i = 0; i < 8; ++i) { /* 20 мс різкого маневру: вал відстає */
        (void)servo_step(&servo, pilot_command, DT_LOOP);
    }

    const float shaft = servo.position_deg;

    pid_config_t cfg;
    cfg.kp = 0.80f; cfg.ki = 1.20f; cfg.kd = 0.0f; cfg.kff = 0.0f;
    cfg.out_min = -30.0f; cfg.out_max = 30.0f;
    cfg.i_min = -30.0f; cfg.i_max = 30.0f;
    cfg.slew_rate_max = 0.0f; cfg.d_lpf_tau = 0.0f; cfg.max_expected_noise = 0.2f;

    bumpless_pid_t pid;
    bumpless_pid_init(&pid, &cfg);

    /* Ось і вся різниця: чим саме ми вважаємо u_prev. */
    const float u_prev = use_telemetry ? shaft : pilot_command;
    bumpless_pid_handover(&pid, shaft, shaft, u_prev);

    servo_stats_t st;
    st.shaft_at_switch_deg = shaft;
    st.first_command_deg = 0.0f;
    st.extra_travel_deg = 0.0f;

    const int steps = (int)(1.0f / DT_LOOP);
    for (int i = 0; i < steps; ++i) {
        const float u = bumpless_pid_update(&pid, servo.position_deg, DT_LOOP);
        if (i == 0) st.first_command_deg = u;

        (void)servo_step(&servo, u, DT_LOOP);

        const float travel = fabsf(servo.position_deg - shaft);
        if (travel > st.extra_travel_deg) st.extra_travel_deg = travel;
    }
    return st;
}

/* ------------------------------------------------------------------ */

static void print_hold_report(void)
{
    const hold_stats_t naive = run_altitude_hold(false, 15.0f);
    const hold_stats_t smooth = run_altitude_hold(true, 15.0f);

    printf("1. Утримання висоти: перемикання на 25 м, газ висіння 0.52\n");
    printf("   %-28s %12s %12s\n", "показник", "наївно", "безривково");
    printf("   %-28s %12.4f %12.4f\n", "вихід на 1-му такті", naive.first_output, smooth.first_output);
    printf("   %-28s %12.4f %12.4f\n", "стрибок |du|", naive.first_jump, smooth.first_jump);
    printf("   %-28s %12.2f %12.2f\n", "просідання, м", 25.0f - naive.min_altitude, 25.0f - smooth.min_altitude);
    printf("   %-28s %12.2f %12.2f\n", "переліт, м", naive.max_altitude - 25.0f, smooth.max_altitude - 25.0f);
    printf("   %-28s %12.2f %12.2f\n", "мінімальна перевантага, g", naive.min_load_g, smooth.min_load_g);
    printf("   %-28s %12.2f %12.2f\n", "заспокоєння, с", naive.settle_seconds, smooth.settle_seconds);
    printf("\n");
}

static void print_ramp_report(void)
{
    static const char *const NAMES[3] = { "обмежувач темпу", "фільтр 1-го порядку", "S-профіль" };
    printf("2. Підведення до нової цілі: набір +15 м після захоплення\n");
    printf("   %-22s %10s %10s %10s %10s\n", "генератор", "пік м/с", "пік g", "час, с", "переліт");
    for (int method = 0; method < 3; ++method) {
        const ramp_stats_t st = run_ramp((ramp_method_t)method, 15.0f, 25.0f);
        printf("   %-22s %10.2f %10.3f %10.2f %10.2f\n",
               NAMES[method], st.peak_climb_mps, st.peak_load_g,
               st.time_to_target_s, st.overshoot_m);
    }
    printf("\n");
}

static void print_cascade_report(void)
{
    static const char *const NAMES[3] = { "наївний", "розірваний", "атомарний" };

    irq_reset_counters();
    printf("3. Каскад позиція-швидкість-кут: захоплення позиції під боковим вітром\n");
    printf("   %-14s %12s %12s %12s %12s\n", "перехід", "|du| такт 1", "|du| пік", "знос, м", "крен, град");
    for (int kind = 0; kind < 3; ++kind) {
        const cascade_stats_t st = run_cascade((handover_kind_t)kind, 12.0f);
        printf("   %-14s %12.4f %12.4f %12.2f %12.2f\n",
               NAMES[kind], st.first_jump, st.worst_jump, st.max_drift_m, st.max_angle_deg);
    }
    printf("   критичних секцій: %u, відкладених швидких тактів: %u\n\n",
           irq_lock_events(), irq_deferred_ticks());
}

static void print_servo_report(void)
{
    const servo_stats_t commanded = run_servo_handover(false);
    const servo_stats_t telemetry = run_servo_handover(true);

    printf("4. Передзавантаження командою проти телеметрії вала\n");
    printf("   вал у мить перемикання: %.2f град (команда пульта 25.00 град)\n",
           commanded.shaft_at_switch_deg);
    printf("   %-24s %14s %14s\n", "джерело u_prev", "1-ша команда", "зайвий хід");
    printf("   %-24s %14.2f %14.2f\n", "u_commanded", commanded.first_command_deg, commanded.extra_travel_deg);
    printf("   %-24s %14.2f %14.2f\n", "телеметрія вала", telemetry.first_command_deg, telemetry.extra_travel_deg);
    printf("\n");
}

static int print_hil_report(void)
{
    hil_report_t rep;
    hil_run(&rep);

    printf("6. Чеклист HIL-стенда\n");
    printf("   [%s] нульовий стрибок: %u перемикань, найгірший |du| = %.3e (межа %.0e)\n",
           rep.glitch_pass ? "+" : "x", rep.switch_count, (double)rep.glitch_worst,
           (double)rep.glitch_limit);
    printf("   [%s] насичене передзавантаження: залишок %.4f, вихід за 10 тактів %.4f, "
           "інтеграл зійшов на %.4f\n",
           rep.saturated_pass ? "+" : "x", rep.saturated_residual,
           rep.saturated_first_delta, rep.saturated_integral_drop);
    printf("   [%s] темп наростання: крок уставки %.5f (дозволено %.5f), "
           "перевантага %.2f..%.2f g, тактів на упорі %u\n",
           rep.ramp_pass ? "+" : "x", rep.ramp_peak_setpoint_step,
           rep.ramp_allowed_setpoint_step, rep.ramp_min_load_g,
           rep.ramp_peak_load_g, rep.ramp_max_saturated_run);

    if (!hil_all_passed(&rep)) {
        printf("\n   ЧЕКЛИСТ НЕ ПРОЙДЕНО — у повітря не піднімаємо.\n");
        return 1;
    }
    printf("\n   Чеклист пройдено.\n");
    return 0;
}

/* Окремо показуємо, що робить регулятор із зіпсутим відліком давача. */
static void print_sensor_fault_report(void)
{
    const pid_config_t cfg = altitude_config();
    bumpless_pid_t pid;
    bumpless_pid_init(&pid, &cfg);
    bumpless_pid_handover(&pid, 25.0f, 25.0f, 0.52f);

    const float good = bumpless_pid_update(&pid, 25.0f, DT_LOOP);
    const float broken = bumpless_pid_update(&pid, NAN, DT_LOOP);
    const float stalled = bumpless_pid_update(&pid, 25.0f, 0.0f);

    char faults[96];
    pid_fault_names(bumpless_pid_faults(&pid), faults, sizeof faults);

    printf("5. Аномалії шини давача\n");
    printf("   справний відлік: %.4f, NaN: %.4f, dt = 0: %.4f\n", good, broken, stalled);
    printf("   прапорці телеметрії: %s\n\n", faults);
}

int main(void)
{
    printf("Перехід без ривка: стан регулятора при зміні режиму\n\n");

    print_hold_report();
    print_ramp_report();
    print_cascade_report();
    print_servo_report();
    print_sensor_fault_report();
    return print_hil_report();
}
