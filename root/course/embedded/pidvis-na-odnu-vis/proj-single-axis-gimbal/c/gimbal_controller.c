#include "gimbal_controller.h"

#include <math.h>

#define GIMBAL_PI 3.14159265f

void gimbal_init(SingleAxisGimbal *g, const GimbalConfig *cfg)
{
    g->filter.angle_deg = 0.0f;
    g->filter.alpha     = cfg->alpha;

    g->pid.kp = cfg->kp;
    g->pid.ki = cfg->ki;
    g->pid.kd = cfg->kd;

    g->pid.out_min      = -GIMBAL_MAX_ANGLE_DEG;
    g->pid.out_max      =  GIMBAL_MAX_ANGLE_DEG;
    g->pid.deadband_deg = cfg->deadband_deg;

    g->pid.integrator  = 0.0f;
    g->pid.d_lpf_state = 0.0f;

    /* ФНЧ 1-го порядку для похідної: beta = dt / (dt + RC), RC = 1/(2*pi*fc).
     * На 25 Гц і такті 5 мс beta ≈ 0.44 — сплеск від вібрації гасне за
     * кілька тактів, а фаза контуру майже не зсувається. */
    if (cfg->d_cutoff_hz > 0.0f) {
        const float rc = 1.0f / (2.0f * GIMBAL_PI * cfg->d_cutoff_hz);
        g->pid.d_lpf_alpha = GIMBAL_DT_SEC / (GIMBAL_DT_SEC + rc);
    } else {
        g->pid.d_lpf_alpha = 1.0f;   /* Без фільтрації */
    }

    g->gyro_bias_dps = 0.0f;
    g->is_calibrated = false;
}

void gimbal_reset_control(SingleAxisGimbal *g)
{
    g->pid.integrator  = 0.0f;
    g->pid.d_lpf_state = 0.0f;
}

/* ---------------------------------------------------------------- калібрування */

void gyro_cal_reset(GyroCal *cal)
{
    cal->n    = 0;
    cal->mean = 0.0f;
    cal->m2   = 0.0f;
}

void gyro_cal_push(GyroCal *cal, float gyro_dps)
{
    /* Онлайновий алгоритм Велфорда: стійкий до втрати точності float
     * і не тримає жодної вибірки в пам'яті. */
    cal->n += 1;
    const float delta = gyro_dps - cal->mean;
    cal->mean += delta / (float)cal->n;
    cal->m2   += delta * (gyro_dps - cal->mean);
}

bool gyro_cal_finish(const GyroCal *cal, uint16_t need_samples, float *bias_out)
{
    if (cal->n < need_samples || cal->n < 2) {
        return false;
    }

    const float variance = cal->m2 / (float)(cal->n - 1);
    if (!(variance <= GIMBAL_MAX_BIAS_VAR)) {
        /* Порівняння «через не більше» ловить і NaN: якщо в вибірку
         * потрапило сміття з побитої шини, калібрування бракується. */
        return false;
    }

    *bias_out = cal->mean;
    return true;
}

void gimbal_set_bias(SingleAxisGimbal *g, float bias_dps)
{
    g->gyro_bias_dps = bias_dps;
    g->is_calibrated = true;
}

void gimbal_seed_angle(SingleAxisGimbal *g, float ay, float az)
{
    g->filter.angle_deg = atan2f(ay, az) * (180.0f / GIMBAL_PI);
}

/* ------------------------------------------------------- комплементарний фільтр */

float comp_filter_update(CompFilter *f, float raw_gyro_dps, float gyro_bias_dps,
                         float ay, float az, float dt)
{
    /* 1. Кутова швидкість без постійного зсуву. */
    const float rate_dps = raw_gyro_dps - gyro_bias_dps;

    /* 2. Передбачення інтегруванням гіроскопа — швидко, але спливає. */
    const float pred_angle = f->angle_deg + rate_dps * dt;

    /* 3. Кут за вектором тяжіння — повільно, але без дрейфу. */
    const float acc_angle_deg = atan2f(ay, az) * (180.0f / GIMBAL_PI);

    /* 4. Злиття: гіроскоп задає форму, акселерометр тягне до істини. */
    f->angle_deg = f->alpha * pred_angle + (1.0f - f->alpha) * acc_angle_deg;

    return f->angle_deg;
}

/* ------------------------------------------------------------------------ ПІД */

float pid_update(GimbalPID *pid, float setpoint_deg, float current_angle_deg,
                 float measured_rate_dps, float dt)
{
    float error = setpoint_deg - current_angle_deg;

    /* Мертва зона похибки. Люфт редуктора й зона нечутливості потенціометра
     * серво роблять дрібну похибку невідпрацьовуваною: контур смикає вал
     * туди-сюди й гріє привід. Нижче порогу вважаємо, що ми в нулі. */
    if (error > -pid->deadband_deg && error < pid->deadband_deg) {
        error = 0.0f;
    }

    const float p_term = pid->kp * error;

    /* Похідна за ВИМІРОМ, а не за похибкою: стрибок уставки не б'є по
     * приводу, а джерело швидкості — гіроскоп, а не різниця кутів. */
    const float d_raw = -measured_rate_dps;
    pid->d_lpf_state += pid->d_lpf_alpha * (d_raw - pid->d_lpf_state);
    const float d_term = pid->kd * pid->d_lpf_state;

    /* Пробний вихід зі СТАРИМ інтегралом — за ним судимо про насичення. */
    const float u_tentative = p_term + pid->integrator + d_term;

    const bool is_saturated =
        (u_tentative > pid->out_max) || (u_tentative < pid->out_min);
    /* Похибка тягне туди ж, куди вже впертий вихід? Тоді інтегрувати нікуди. */
    const bool pushes_further = (u_tentative * error > 0.0f);

    if (!is_saturated || !pushes_further) {
        pid->integrator += pid->ki * error * dt;
    }

    /* Другий рубіж: сам інтеграл не має права вирости більший за весь хід. */
    if (pid->integrator > pid->out_max) pid->integrator = pid->out_max;
    if (pid->integrator < pid->out_min) pid->integrator = pid->out_min;

    float u_out = p_term + pid->integrator + d_term;
    if (u_out > pid->out_max) u_out = pid->out_max;
    if (u_out < pid->out_min) u_out = pid->out_min;

    return u_out;
}

/* --------------------------------------------------------------- вихід на серво */

uint16_t servo_output_map(float correction_deg)
{
    /* [-45°, +45°] → [1000, 2000] мкс, нуль у 1500 мкс. */
    const float us_per_deg =
        (GIMBAL_SERVO_MAX_US - GIMBAL_SERVO_MIN_US) / (2.0f * GIMBAL_MAX_ANGLE_DEG);

    float pulse_us = GIMBAL_SERVO_MID_US + correction_deg * us_per_deg;

    if (pulse_us < GIMBAL_SERVO_MIN_US) pulse_us = GIMBAL_SERVO_MIN_US;
    if (pulse_us > GIMBAL_SERVO_MAX_US) pulse_us = GIMBAL_SERVO_MAX_US;

    return (uint16_t)(pulse_us + 0.5f);
}

/* ----------------------------------------------------------------- такт контуру */

void gimbal_step(SingleAxisGimbal *g, float raw_gyro_dps, float ay, float az,
                 GimbalOutput *out)
{
    const float angle = comp_filter_update(&g->filter, raw_gyro_dps,
                                           g->gyro_bias_dps, ay, az,
                                           GIMBAL_DT_SEC);
    const float rate = raw_gyro_dps - g->gyro_bias_dps;

    /* Уставка стабілізатора горизонту незмінна — нуль. */
    const float correction = pid_update(&g->pid, 0.0f, angle, rate, GIMBAL_DT_SEC);

    out->angle_deg      = angle;
    out->rate_dps       = rate;
    out->correction_deg = correction;
    out->integrator     = g->pid.integrator;
    out->pulse_us       = servo_output_map(correction);
}
