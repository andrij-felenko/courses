#include <stddef.h>
#include "servo_s_curve.h"

uint16_t servo_s_curve_angle_to_pulse(const servo_s_curve_t *servo, q16_t angle_deg_q16) {
    if (servo == NULL) {
        return 0;
    }

    /* 1. Програмне обмеження вхідного кута калібрувальними рамками */
    q16_t angle_clamped = angle_deg_q16;
    if (angle_clamped < servo->min_angle_deg_q16) {
        angle_clamped = servo->min_angle_deg_q16;
    } else if (angle_clamped > servo->max_angle_deg_q16) {
        angle_clamped = servo->max_angle_deg_q16;
    }

    q16_t angle_range = servo->max_angle_deg_q16 - servo->min_angle_deg_q16;
    if (angle_range <= 0) {
        return servo->min_pulse_us;
    }

    /* 2. Лінійне масштабування кута в тривалість імпульсу ШІМ без плаваючої коми */
    int64_t pulse_range = (int64_t)servo->max_pulse_us - servo->min_pulse_us;
    int64_t delta_angle = (int64_t)angle_clamped - servo->min_angle_deg_q16;
    int64_t pulse_calc = (int64_t)servo->min_pulse_us + ((delta_angle * pulse_range) / angle_range);

    /* 3. Жорсткий апаратний clamping за мікросекундами проти ударів об упори */
    if (pulse_calc < (int64_t)servo->min_pulse_us) {
        pulse_calc = servo->min_pulse_us;
    } else if (pulse_calc > (int64_t)servo->max_pulse_us) {
        pulse_calc = servo->max_pulse_us;
    }

    return (uint16_t)pulse_calc;
}

void servo_s_curve_init(servo_s_curve_t *servo, uint16_t dt_ms, q16_t initial_angle_deg_q16) {
    if (servo == NULL) {
        return;
    }

    servo->min_angle_deg_q16 = Q16_FROM_INT(SERVO_DEFAULT_MIN_ANGLE_DEG);
    servo->max_angle_deg_q16 = Q16_FROM_INT(SERVO_DEFAULT_MAX_ANGLE_DEG);
    servo->min_pulse_us      = SERVO_DEFAULT_MIN_PULSE_US;
    servo->max_pulse_us      = SERVO_DEFAULT_MAX_PULSE_US;

    /* Типові безпечні ліміти кінематики для MG90S: 180 град/с, 720 град/с^2 */
    servo->max_vel_deg_s     = Q16_FROM_INT(180);
    servo->max_accel_deg_s2  = Q16_FROM_INT(720);

    servo->dt_ms             = (dt_ms > 0) ? dt_ms : SERVO_DEFAULT_DT_MS;

    /* Обмеження початкового положення */
    q16_t clamped_init = initial_angle_deg_q16;
    if (clamped_init < servo->min_angle_deg_q16) {
        clamped_init = servo->min_angle_deg_q16;
    } else if (clamped_init > servo->max_angle_deg_q16) {
        clamped_init = servo->max_angle_deg_q16;
    }

    servo->current_pos_q16   = clamped_init;
    servo->current_vel_q16   = 0;
    servo->current_acc_q16   = 0;

    servo->start_pos_q16     = clamped_init;
    servo->target_pos_q16    = clamped_init;
    servo->duration_q16      = 0;
    servo->total_steps       = 0;
    servo->current_step      = 0;
    servo->is_moving         = false;

    servo->current_pulse_us  = servo_s_curve_angle_to_pulse(servo, clamped_init);
}

void servo_s_curve_set_limits(servo_s_curve_t *servo,
                              q16_t min_angle_q16,
                              q16_t max_angle_q16,
                              uint16_t min_pulse_us,
                              uint16_t max_pulse_us) {
    if (servo == NULL || min_angle_q16 >= max_angle_q16 || min_pulse_us >= max_pulse_us) {
        return;
    }

    servo->min_angle_deg_q16 = min_angle_q16;
    servo->max_angle_deg_q16 = max_angle_q16;
    servo->min_pulse_us      = min_pulse_us;
    servo->max_pulse_us      = max_pulse_us;

    /* Коригуємо поточну позицію під нові калібрувальні межі */
    if (servo->current_pos_q16 < servo->min_angle_deg_q16) {
        servo->current_pos_q16 = servo->min_angle_deg_q16;
    } else if (servo->current_pos_q16 > servo->max_angle_deg_q16) {
        servo->current_pos_q16 = servo->max_angle_deg_q16;
    }

    servo->current_pulse_us = servo_s_curve_angle_to_pulse(servo, servo->current_pos_q16);
}

void servo_s_curve_set_motion_profile(servo_s_curve_t *servo,
                                      q16_t max_vel_deg_s,
                                      q16_t max_accel_deg_s2) {
    if (servo == NULL) {
        return;
    }
    if (max_vel_deg_s > 0) {
        servo->max_vel_deg_s = max_vel_deg_s;
    }
    if (max_accel_deg_s2 > 0) {
        servo->max_accel_deg_s2 = max_accel_deg_s2;
    }
}

bool servo_s_curve_set_target_duration(servo_s_curve_t *servo,
                                       q16_t target_angle_deg_q16,
                                       uint32_t duration_ms) {
    if (servo == NULL) {
        return false;
    }

    /* Захисний clamping цільового положення */
    q16_t target_clamped = target_angle_deg_q16;
    if (target_clamped < servo->min_angle_deg_q16) {
        target_clamped = servo->min_angle_deg_q16;
    } else if (target_clamped > servo->max_angle_deg_q16) {
        target_clamped = servo->max_angle_deg_q16;
    }

    q16_t delta_pos = target_clamped - servo->current_pos_q16;
    if (delta_pos == 0) {
        servo->start_pos_q16   = target_clamped;
        servo->target_pos_q16  = target_clamped;
        servo->current_vel_q16 = 0;
        servo->current_acc_q16 = 0;
        servo->is_moving       = false;
        return false;
    }

    /* Кількість дискретних кроків N = T / dt */
    uint32_t steps = duration_ms / servo->dt_ms;
    if (steps == 0) {
        steps = 1;
    }

    servo->start_pos_q16   = servo->current_pos_q16;
    servo->target_pos_q16  = target_clamped;
    servo->total_steps     = steps;
    servo->current_step    = 0;
    servo->duration_q16    = (q16_t)(((int64_t)steps * servo->dt_ms * Q16_ONE) / 1000);
    if (servo->duration_q16 == 0) {
        servo->duration_q16 = 1;
    }
    servo->is_moving       = true;

    return true;
}

bool servo_s_curve_set_target(servo_s_curve_t *servo, q16_t target_angle_deg_q16) {
    if (servo == NULL) {
        return false;
    }

    q16_t target_clamped = target_angle_deg_q16;
    if (target_clamped < servo->min_angle_deg_q16) {
        target_clamped = servo->min_angle_deg_q16;
    } else if (target_clamped > servo->max_angle_deg_q16) {
        target_clamped = servo->max_angle_deg_q16;
    }

    q16_t delta_pos = target_clamped - servo->current_pos_q16;
    q16_t abs_delta = q16_abs(delta_pos);
    if (abs_delta == 0) {
        servo->is_moving = false;
        return false;
    }

    /*
     * Для квінтичної S-траєкторії s(tau) = 10*tau^3 - 15*tau^4 + 6*tau^5:
     * 1. Пікова швидкість у точці tau=0.5:
     *      v_peak = 15/8 * (|delta| / T) <= v_max
     *      T_vel >= (15 * |delta|) / (8 * v_max)
     * 2. Пікове прискорення в точці tau = (3 - sqrt(3))/6:
     *      a_peak = 10/sqrt(3) * (|delta| / T^2) ~ 5.774 * (|delta| / T^2) <= a_max
     *      T_acc >= sqrt( (5.774 * |delta|) / a_max )
     * Тривалість обирається як T = max(T_vel, T_acc).
     */
    q16_t t_vel_q16 = (q16_t)(((int64_t)abs_delta * 15 * Q16_ONE) /
                              ((int64_t)8 * servo->max_vel_deg_s));

    /* Наближення коефіцієнта 5.774 цілим дробом 2887 / 500 */
    q16_t radicand = (q16_t)(((int64_t)abs_delta * 2887 * Q16_ONE) /
                             ((int64_t)500 * servo->max_accel_deg_s2));
    q16_t t_acc_q16 = q16_sqrt(radicand);

    q16_t t_chosen_q16 = (t_vel_q16 > t_acc_q16) ? t_vel_q16 : t_acc_q16;

    /* Розрахунок тривалості у мілісекундах */
    uint32_t duration_ms = (uint32_t)(((int64_t)t_chosen_q16 * 1000) >> Q16_SHIFT);
    if (duration_ms < servo->dt_ms) {
        duration_ms = servo->dt_ms;
    }

    return servo_s_curve_set_target_duration(servo, target_clamped, duration_ms);
}

bool servo_s_curve_update(servo_s_curve_t *servo) {
    if (servo == NULL || !servo->is_moving) {
        return false;
    }

    servo->current_step++;

    /* Досягнення кінцевої точки профілю */
    if (servo->current_step >= servo->total_steps) {
        servo->current_pos_q16   = servo->target_pos_q16;
        servo->current_vel_q16   = 0;
        servo->current_acc_q16   = 0;
        servo->is_moving         = false;
        servo->current_pulse_us  = servo_s_curve_angle_to_pulse(servo, servo->target_pos_q16);
        return false;
    }

    /*
     * Нормований час tau = current_step / total_steps у форматі Q16.16 (діапазон 0..65536).
     */
    q16_t tau_q16 = (q16_t)(((int64_t)servo->current_step << Q16_SHIFT) / servo->total_steps);

    /*
     * Обчислення полінома квінтичного згладжування s(tau) = tau^3 * (10 + tau * (6*tau - 15)):
     * Забезпечує граничні умови s(0)=0, s(1)=1, s'(0)=s'(1)=0, s''(0)=s''(1)=0.
     */
    q16_t term1 = 6 * tau_q16 - (15 << Q16_SHIFT);
    q16_t term2 = (q16_t)(((int64_t)tau_q16 * term1) >> Q16_SHIFT);
    q16_t term3 = (10 << Q16_SHIFT) + term2;

    q16_t tau2  = (q16_t)(((int64_t)tau_q16 * tau_q16) >> Q16_SHIFT);
    q16_t tau3  = (q16_t)(((int64_t)tau2 * tau_q16) >> Q16_SHIFT);
    q16_t s_q16 = (q16_t)(((int64_t)tau3 * term3) >> Q16_SHIFT);

    /* Розрахунок поточної координати кута */
    q16_t delta_pos = servo->target_pos_q16 - servo->start_pos_q16;
    servo->current_pos_q16 = servo->start_pos_q16 + (q16_t)(((int64_t)delta_pos * s_q16) >> Q16_SHIFT);

    /*
     * Перша похідна швидкості: s'(tau) = 30 * tau^2 * (1 - tau)^2
     * Фізична швидкість: v(t) = (delta_p / T) * s'(tau)
     */
    q16_t one_minus_tau = Q16_ONE - tau_q16;
    q16_t tau_x_inv     = (q16_t)(((int64_t)tau_q16 * one_minus_tau) >> Q16_SHIFT);
    q16_t tau_x_inv_sq  = (q16_t)(((int64_t)tau_x_inv * tau_x_inv) >> Q16_SHIFT);
    q16_t s_prime_q16   = 30 * tau_x_inv_sq;

    servo->current_vel_q16 = (q16_t)(((int64_t)delta_pos * s_prime_q16) / servo->duration_q16);

    /*
     * Друга похідна: s''(tau) = 60 * tau * (1 - tau) * (1 - 2*tau)
     * Фізичне прискорення: a(t) = (delta_p / T^2) * s''(tau)
     */
    q16_t one_minus_2tau = Q16_ONE - 2 * tau_q16;
    q16_t s_ddot_q16     = 60 * (q16_t)(((int64_t)tau_x_inv * one_minus_2tau) >> Q16_SHIFT);
    int64_t dur_sq       = ((int64_t)servo->duration_q16 * servo->duration_q16) >> Q16_SHIFT;
    if (dur_sq > 0) {
        servo->current_acc_q16 = (q16_t)((((int64_t)delta_pos * s_ddot_q16)) / dur_sq);
    } else {
        servo->current_acc_q16 = 0;
    }

    /* Оновлення вихідної тривалості імпульсу з гарантованим clamping */
    servo->current_pulse_us = servo_s_curve_angle_to_pulse(servo, servo->current_pos_q16);

    return true;
}

uint16_t servo_s_curve_get_pulse_us(const servo_s_curve_t *servo) {
    return (servo != NULL) ? servo->current_pulse_us : 0;
}

q16_t servo_s_curve_get_angle_q16(const servo_s_curve_t *servo) {
    return (servo != NULL) ? servo->current_pos_q16 : 0;
}

q16_t servo_s_curve_get_velocity_q16(const servo_s_curve_t *servo) {
    return (servo != NULL) ? servo->current_vel_q16 : 0;
}

q16_t servo_s_curve_get_accel_q16(const servo_s_curve_t *servo) {
    return (servo != NULL) ? servo->current_acc_q16 : 0;
}

bool servo_s_curve_is_moving(const servo_s_curve_t *servo) {
    return (servo != NULL) ? servo->is_moving : false;
}
