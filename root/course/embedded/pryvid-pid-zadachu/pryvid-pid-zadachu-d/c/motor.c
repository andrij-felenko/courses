#include "motor.h"

#include <math.h>
#include <stddef.h>

#define TWO_PI 6.283185307179586

double rpm_to_rad_s(double rpm)
{
    return rpm * TWO_PI / 60.0;
}

double rad_s_to_rpm(double rad_s)
{
    return rad_s * 60.0 / TWO_PI;
}

const char *motor_family_name(MotorFamily family)
{
    switch (family) {
    case MOTOR_BDC:     return "колекторний";
    case MOTOR_STEPPER: return "кроковий";
    case MOTOR_BLDC:    return "безколекторний";
    case MOTOR_SERVO:   return "сервопривід";
    }
    return "невідомий";
}

double motor_torque_constant(const MotorSpecs *m)
{
    if (m->rated_current_a <= 0.0) {
        return 0.0;
    }
    return m->rated_torque_nm / m->rated_current_a;
}

double motor_stall_current(const MotorSpecs *m)
{
    /* У крокового пускового кидка немає взагалі: чоппер тримає струм на уставці. */
    if (m->family == MOTOR_STEPPER) {
        return m->rated_current_a;
    }
    if (m->phase_resistance_ohm <= 0.0) {
        return 0.0;
    }
    return m->supply_v / m->phase_resistance_ohm;   /* при w = 0 протиЕРС немає: I = V / R_a */
}

double motor_available_torque(const MotorSpecs *m, double omega_rad_s)
{
    double rpm = rad_s_to_rpm(fabs(omega_rad_s));

    if (m->no_load_speed_rpm <= 0.0 || rpm > m->no_load_speed_rpm) {
        return 0.0;
    }

    switch (m->family) {
    case MOTOR_BDC: {
        /* T(w) = T_stall * (1 - w / w_0): протиЕРС лінійно з'їдає напругу живлення */
        double stall_torque = motor_torque_constant(m) * motor_stall_current(m);
        return stall_torque * (1.0 - rpm / m->no_load_speed_rpm);
    }
    case MOTOR_STEPPER: {
        /* Індуктивність не дає струму наростати за час кроку: спад першого
           порядку від частоти імпульсів зі зламом на corner_speed_rpm. */
        double x;
        if (m->corner_speed_rpm <= 0.0) {
            return m->rated_torque_nm;
        }
        x = rpm / m->corner_speed_rpm;
        return m->rated_torque_nm / sqrt(1.0 + x * x);
    }
    case MOTOR_BLDC:
        /* До базової швидкості — сталий момент, вище — стала потужність. */
        if (m->corner_speed_rpm <= 0.0 || rpm <= m->corner_speed_rpm) {
            return m->rated_torque_nm;
        }
        return m->rated_torque_nm * (m->corner_speed_rpm / rpm);
    case MOTOR_SERVO:
        /* Редуктор тримає паспортний момент аж до межі обертів. */
        return m->rated_torque_nm;
    }
    return 0.0;
}

double motor_current_for_torque(const MotorSpecs *m, double torque_nm)
{
    double kt;

    /* Кроковий бере повний струм фази незалежно від навантаження — саме звідси
       його нагрів тоді, коли він не робить жодної корисної роботи. */
    if (m->family == MOTOR_STEPPER) {
        return m->rated_current_a;
    }
    kt = motor_torque_constant(m);
    if (kt <= 0.0) {
        return 0.0;
    }
    return fabs(torque_nm) / kt;
}

/* Скільки обмоток одночасно під струмом. */
static double phase_factor(MotorFamily family)
{
    switch (family) {
    case MOTOR_STEPPER: return 2.0;  /* обидві фази статора */
    case MOTOR_BLDC:    return 1.5;  /* 3 * (I_peak / sqrt(2))^2 для синусоїдного FOC */
    default:            return 1.0;  /* один контур якоря */
    }
}

double motor_copper_loss_w(const MotorSpecs *m, double torque_nm, bool standstill)
{
    double i;

    if (m->family == MOTOR_STEPPER) {
        i = m->rated_current_a * (standstill ? m->hold_current_frac : 1.0);
    } else {
        i = motor_current_for_torque(m, torque_nm);
    }
    return phase_factor(m->family) * i * i * m->phase_resistance_ohm;   /* P = k * I^2 * R */
}

double motor_winding_temp_c(const MotorSpecs *m, double average_loss_w, double ambient_c)
{
    return ambient_c + average_loss_w * m->thermal_r_c_per_w;
}

double gearbox_reflect_torque(const Gearbox *g, double load_torque_nm)
{
    return load_torque_nm / (g->ratio * g->efficiency);   /* передача ділить момент на N * eta */
}

double gearbox_reflect_inertia(const Gearbox *g, double load_inertia_kgm2)
{
    return load_inertia_kgm2 / (g->ratio * g->ratio);     /* а інерцію — на квадрат N */
}

double gearbox_heat_loss_w(const Gearbox *g, double output_power_w)
{
    if (g->efficiency <= 0.0) {
        return 0.0;
    }
    return fabs(output_power_w) * (1.0 - g->efficiency) / g->efficiency;
}

const char *motor_specs_problem(const MotorSpecs *m)
{
    if (m == NULL || m->name == NULL) {
        return "паспорт мотора не заданий";
    }
    if (m->rated_torque_nm <= 0.0) {
        return "номінальний момент має бути додатним";
    }
    if (m->rated_current_a <= 0.0) {
        return "номінальний струм має бути додатним";
    }
    if (m->no_load_speed_rpm <= 0.0) {
        return "межа обертів має бути додатною";
    }
    if (m->phase_resistance_ohm <= 0.0) {
        return "опір обмотки має бути додатним";
    }
    if (m->thermal_r_c_per_w <= 0.0) {
        return "тепловий опір має бути додатним";
    }
    if (m->rotor_inertia_kgm2 < 0.0) {
        return "момент інерції ротора від'ємний";
    }
    if (m->hold_current_frac < 0.0 || m->hold_current_frac > 1.0) {
        return "частка струму утримання поза межами 0..1";
    }
    if (m->step_resolution_deg < 0.0) {
        return "дискрет положення від'ємний";
    }
    if ((m->family == MOTOR_STEPPER || m->family == MOTOR_BLDC) &&
        (m->corner_speed_rpm <= 0.0 || m->corner_speed_rpm > m->no_load_speed_rpm)) {
        return "злам кривої моменту поза робочим діапазоном";
    }
    if (m->family == MOTOR_BDC) {
        /* k_e = k_t, тож холостий хід не має права розходитися з V / k_t.
           Розходження означає, що числа в паспорті взяті з різних моторів. */
        double kt, w0_rpm;
        if (m->supply_v <= 0.0) {
            return "напруга живлення має бути додатною";
        }
        kt = motor_torque_constant(m);
        w0_rpm = rad_s_to_rpm(m->supply_v / kt);
        if (m->no_load_speed_rpm > 1.5 * w0_rpm || m->no_load_speed_rpm * 1.5 < w0_rpm) {
            return "паспорт суперечливий: холостий хід не сходиться з V / k_t";
        }
    }
    return NULL;
}

const char *gearbox_problem(const Gearbox *g)
{
    if (g == NULL) {
        return "редуктор не заданий";
    }
    if (g->ratio <= 0.0) {
        return "передавальне відношення має бути додатним";
    }
    if (g->efficiency <= 0.0 || g->efficiency > 1.0) {
        return "ККД передачі поза межами 0..1";
    }
    if (g->backlash_deg < 0.0) {
        return "люфт від'ємний";
    }
    return NULL;
}
