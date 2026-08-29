#include "vehicle.h"

#include <math.h>

void airframe_init(Airframe *a, float inertia, float damping, float torque_gain) {
    a->angle = 0.0f;
    a->rate = 0.0f;
    a->inertia = inertia > 1e-6f ? inertia : 1e-6f;
    a->damping = damping;
    a->torque_gain = torque_gain;
}

void airframe_step(Airframe *a, float control, float disturbance, float dt) {
    float torque = control * a->torque_gain + disturbance - a->damping * a->rate;
    float accel = torque / a->inertia;

    /* Напівнеявний (Ейлер–Кромер) крок: на 500 Гц він тримає фазу точніше за
       прямий Ейлер, а фаза тут — головна вимірювана величина. */
    a->rate += accel * dt;
    a->angle += a->rate * dt;
}

void autopilot_init(Autopilot *ap, ControlMode mode, float dt) {
    ap->mode = mode;
    ap->kp_angle = 8.0f;
    ap->kp_rate = 0.6f;
    ap->ki_rate = 1.5f;
    ap->max_rate = 3.5f;    /* ~200 град/с на повному ході стіка */
    ap->max_angle = 0.52f;  /* ~30 град */
    ap->torque_limit = 1.5f;
    ap->slew_limit = 25.0f; /* практично без обмеження */
    ap->suppression = false;
    ap->i_state = 0.0f;
    ap->setpoint = 0.0f;
    ap->sens = 1.0f;
    ap->steps = 0;
    ap->saturated = 0;
    pio_init(&ap->stick_mon, dt);
}

void autopilot_enable_suppression(Autopilot *ap, bool on) {
    ap->suppression = on;
    /* Разом із демпфуванням вмикається й жорсткий обмежувач крутизни. */
    ap->slew_limit = on ? 5.0f : 25.0f;
}

float autopilot_update(Autopilot *ap, float stick, const Airframe *a, float dt) {
    float target_sens, shaped, max_step, d, rate_cmd, angle_cmd, err, unsat, out;
    bool saturated, unwinding;

    ap->steps++;

    /* 1. Динамічне демпфування стіка. Якщо сама команда коливається в смузі
          0.5–2.5 Гц, чутливість пульта тимчасово падає: це знімає підсилення
          контуру саме там, де людина підняла його з переляку. */
    pio_update(&ap->stick_mon, stick);
    target_sens = 1.0f;
    if (ap->suppression && pio_active(&ap->stick_mon, 0.10f)) {
        target_sens = 0.45f;
    }
    ap->sens += (target_sens - ap->sens) * (dt / 0.20f);
    shaped = stick * ap->sens;

    /* 2. Обмеження крутизни уставки: панічний перекид стіка з краю в край не
          має вимагати від машини швидкості, якої вона фізично не має. */
    max_step = ap->slew_limit * dt;
    d = shaped - ap->setpoint;
    if (d > max_step) {
        d = max_step;
    } else if (d < -max_step) {
        d = -max_step;
    }
    ap->setpoint += d;

    /* 3. Зовнішній контур: у Rate стік задає кутову швидкість, у Angle — кут,
          і тоді швидкий контур замикається вже на борту. */
    if (ap->mode == MODE_RATE) {
        rate_cmd = ap->setpoint * ap->max_rate;
    } else {
        angle_cmd = ap->setpoint * ap->max_angle;
        rate_cmd = ap->kp_angle * (angle_cmd - a->angle);
        if (rate_cmd > ap->max_rate) {
            rate_cmd = ap->max_rate;
        } else if (rate_cmd < -ap->max_rate) {
            rate_cmd = -ap->max_rate;
        }
    }

    /* 4. Внутрішній ПІ-контур швидкості на локальному гіроскопі. */
    err = rate_cmd - a->rate;
    unsat = ap->kp_rate * err + ap->i_state;
    out = unsat;
    if (out > ap->torque_limit) {
        out = ap->torque_limit;
    } else if (out < -ap->torque_limit) {
        out = -ap->torque_limit;
    }

    saturated = fabsf(unsat - out) > 1e-6f;
    if (saturated) {
        ap->saturated++;
    }
    /* Анти-віндап: поки вихід уперся в межу, інтегратор має право рухатися
       лише в бік виходу з насичення. Інакше маємо класичний windup. */
    unwinding = saturated && ((err > 0.0f) != (out > 0.0f));
    if (!saturated || unwinding) {
        ap->i_state += ap->ki_rate * err * dt;
        if (ap->i_state > ap->torque_limit) {
            ap->i_state = ap->torque_limit;
        } else if (ap->i_state < -ap->torque_limit) {
            ap->i_state = -ap->torque_limit;
        }
    }
    return out;
}

ObjectDynamics autopilot_object(const Autopilot *ap, const Airframe *a) {
    ObjectDynamics obj;
    float loop = ap->kp_rate * a->torque_gain;          /* жорсткість контуру швидкості */
    float inner_tc = a->inertia / (loop + a->damping);  /* стала часу цього контуру */

    if (ap->mode == MODE_RATE) {
        /* Стік задає швидкість, кут набігає інтегруванням: Y_c = G/s. */
        obj.gain = ap->max_rate * loop / (loop + a->damping);
        obj.lag_tc = inner_tc;
        obj.integrating = true;
    } else {
        /* Стік задає кут: Y_c = G/(T*s + 1). */
        obj.gain = ap->max_angle;
        obj.lag_tc = 1.0f / ap->kp_angle + inner_tc;
        obj.integrating = false;
    }
    return obj;
}

float autopilot_saturation(const Autopilot *ap) {
    return ap->steps > 0 ? (float)ap->saturated / (float)ap->steps : 0.0f;
}

float autopilot_sensitivity(const Autopilot *ap) { return ap->sens; }
