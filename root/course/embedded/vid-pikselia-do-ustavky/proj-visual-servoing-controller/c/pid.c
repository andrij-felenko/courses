#include "pid.h"

#include <math.h>

static float clampf(float v, float lo, float hi)
{
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

void pid_init(ServoingPid *pid, float kp, float ki, float kd,
              float max_output, float max_integral, float deadband)
{
    pid->kp = kp;
    pid->ki = ki;
    pid->kd = kd;
    pid->max_output = max_output;
    pid->max_integral = max_integral;
    pid->deadband = deadband;
    pid_reset(pid);
}

void pid_reset(ServoingPid *pid)
{
    pid->integral = 0.0f;
    pid->prev_meas = 0.0f;
    pid->primed = false;
}

float pid_update(ServoingPid *pid, float setpoint, float measurement, float dt)
{
    if (!(dt > 0.0f) || !isfinite(measurement)) {
        return 0.0f;
    }

    float error = setpoint - measurement;

    /* Зона нечутливості: тремтіння нейромережі на кілька пікселів не має
     * рухати приводи взагалі. */
    if (fabsf(error) < pid->deadband) {
        error = 0.0f;
    } else {
        error -= (error > 0.0f) ? pid->deadband : -pid->deadband;
    }

    const float p_term = pid->kp * error;

    const float integral_prev = pid->integral;
    pid->integral = clampf(pid->integral + error * dt,
                           -pid->max_integral, pid->max_integral);
    const float i_term = pid->ki * pid->integral;

    float d_term = 0.0f;
    if (pid->primed) {
        d_term = -pid->kd * (measurement - pid->prev_meas) / dt;
    } else {
        pid->primed = true;   /* перший крок похідної не має */
    }
    pid->prev_meas = measurement;

    float output = p_term + i_term + d_term;

    if (fabsf(output) > pid->max_output) {
        /* Умовне інтегрування: привід уже в упорі, накопичувати далі означає
         * заплатити довгим виходом із насичення на зворотному русі. */
        if ((output > 0.0f && error > 0.0f) || (output < 0.0f && error < 0.0f)) {
            pid->integral = integral_prev;
        }
        output = clampf(output, -pid->max_output, pid->max_output);
    }

    return output;
}
