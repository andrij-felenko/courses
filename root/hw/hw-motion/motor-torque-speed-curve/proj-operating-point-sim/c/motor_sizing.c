/* motor_sizing.h / motor_sizing.c — Розрахунок електромеханічного приводу */
#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double u_nom;       /* Номінальна напруга живлення, В */
    double r_arm;       /* Активний опір обмотки якоря, Ом */
    double k_t;         /* Стала крутного моменту, Н·м/А */
    double k_e;         /* Стала протиЕРС, В·с/рад (у системі SI k_e = k_t) */
    double i_0;         /* Струм холостого ходу, А */
    double m_cont;      /* Номінальний неперервний момент S1, Н·м */
    double m_peak;      /* Граничний піковий момент, Н·м */
    double omega_max;   /* Максимальна механічна швидкість, рад/с */
    double j_rotor;     /* Момент інерції ротора, кг·м² */
} MotorParams;

typedef struct {
    double m_static;    /* Постійний момент опору (тертя, вантаж), Н·м */
    double b_viscous;   /* Коефіцієнт в'язкого тертя, Н·м·с/рад */
    double c_aero;      /* Коефіцієнт аеродинамічного навантаження, Н·м·с²/рад² */
} LoadCharacteristics;

typedef struct {
    double omega_op;    /* Усталена кутова швидкість, рад/с */
    double rpm_op;      /* Швидкість обертання, об/хв */
    double torque_op;   /* Робочий крутний момент, Н·м */
    double current_op;  /* Струм якоря в робочій точці, А */
    double p_mech;      /* Корисна механічна потужність, Вт */
    double p_loss;      /* Джоулеві теплові втрати в обмотці (I²R), Вт */
    double efficiency;  /* Електромеханічний ККД (P_mech / P_elec) */
    bool is_s1_safe;    /* Чи лежить режим у межах безпечної зони S1 */
} OperatingPoint;

typedef struct {
    double target_omega_load;   /* Необхідна кутова швидкість навантаження, рад/с */
    double target_torque_load;  /* Необхідний тривалий момент навантаження, Н·м */
    double j_load;              /* Момент інерції навантаження, кг·м² */
    double accel_time;          /* Бажаний час розгону до target_omega, с */
    double gear_efficiency;     /* ККД редуктора (0.75 - 0.95) */
} MechanismRequirements;

typedef struct {
    double i_optimal_inertia;   /* Оптимальне передавальне число за інерцією */
    double i_min_continuous;    /* Мінімальне передавальне число за моментом S1 */
    double i_selected;          /* Рекомендоване передавальне число */
    double motor_req_torque;    /* Необхідний тривалий момент від мотора, Н·м */
    double motor_accel_torque;  /* Піковий момент мотора під час розгону, Н·м */
    bool is_feasible;           /* Чи задовольняє мотор вимогам механізму */
} GearboxSelectionResult;

/* Знаходження робочої точки чисельним методом Ньютона-Рафсона */
OperatingPoint motor_solve_operating_point(const MotorParams *m,
                                          const LoadCharacteristics *load,
                                          double u_applied)
{
    OperatingPoint pt = {0};
    double omega_0 = u_applied / m->k_e;

    /* Початкове наближення для швидкості */
    double omega = omega_0 * 0.7;

    for (int iter = 0; iter < 100; ++iter) {
        /* Момент мотора: M_m = (k_t / R) * (U - k_e * omega) */
        double m_motor = m->k_t * (u_applied - m->k_e * omega) / m->r_arm;
        /* Момент навантаження: M_l = M_s + B * omega + C * omega² */
        double m_load = load->m_static + load->b_viscous * omega + load->c_aero * omega * omega;

        double f = m_motor - m_load;
        if (fabs(f) < 1e-7) {
            break;
        }

        /* Похідна dF/d_omega = -k_t * k_e / R - B - 2 * C * omega */
        double df = -(m->k_t * m->k_e) / m->r_arm - load->b_viscous - 2.0 * load->c_aero * omega;
        omega = omega - f / df;

        if (omega < 0.0) {
            omega = 0.0;
            break;
        }
        if (omega > omega_0) {
            omega = omega_0;
        }
    }

    pt.omega_op = omega;
    pt.rpm_op = omega * (60.0 / (2.0 * M_PI));
    pt.torque_op = m->k_t * (u_applied - m->k_e * omega) / m->r_arm;
    if (pt.torque_op < 0.0) pt.torque_op = 0.0;

    pt.current_op = m->i_0 + pt.torque_op / m->k_t;
    pt.p_mech = pt.torque_op * pt.omega_op;
    pt.p_loss = pt.current_op * pt.current_op * m->r_arm;

    double p_elec = u_applied * pt.current_op;
    pt.efficiency = (p_elec > 1e-6) ? (pt.p_mech / p_elec) : 0.0;
    pt.is_s1_safe = (pt.torque_op <= m->m_cont) && (pt.omega_op <= m->omega_max);

    return pt;
}

/* Підбір редуктора та перевірка динаміки розгону */
GearboxSelectionResult motor_select_gearbox(const MotorParams *m,
                                            const MechanismRequirements *req)
{
    GearboxSelectionResult res = {0};

    /* 1. Оптимальне передавальне число за узгодженням інерції: i = sqrt(J_load / J_rotor) */
    res.i_optimal_inertia = sqrt(req->j_load / m->j_rotor);

    /* 2. Мінімальне передавальне число за тривалим моментом S1: i >= M_req / (M_cont * eta) */
    res.i_min_continuous = req->target_torque_load / (m->m_cont * req->gear_efficiency);

    /* Обираємо більше значення, щоб гарантувати тривалу роботу в зоні S1 */
    res.i_selected = (res.i_optimal_inertia > res.i_min_continuous)
                     ? res.i_optimal_inertia
                     : res.i_min_continuous;

    /* Перевірка швидкості мотора при обраному i */
    double omega_motor_req = req->target_omega_load * res.i_selected;
    if (omega_motor_req > m->omega_max) {
        /* Зменшуємо i до гранично допустимого за швидкістю */
        res.i_selected = m->omega_max / req->target_omega_load;
    }

    res.motor_req_torque = req->target_torque_load / (res.i_selected * req->gear_efficiency);

    /* 3. Розрахунок прискорення та пікового моменту під час розгону */
    double alpha_load = req->target_omega_load / req->accel_time;
    double alpha_motor = alpha_load * res.i_selected;
    double j_reflected = req->j_load / (res.i_selected * res.i_selected);

    /* M_accel = (J_rotor + J_reflected / eta) * alpha_motor + M_req */
    double j_total_motor_side = m->j_rotor + j_reflected / req->gear_efficiency;
    res.motor_accel_torque = j_total_motor_side * alpha_motor + res.motor_req_torque;

    res.is_feasible = (res.motor_req_torque <= m->m_cont) &&
                      (res.motor_accel_torque <= m->m_peak) &&
                      (omega_motor_req <= m->omega_max);

    return res;
}

/* Обчислення середньоквадратичного моменту M_RMS для перевірки теплового режиму */
double motor_compute_rms_torque(const double *torques, const double *durations, size_t count)
{
    if (!torques || !durations || count == 0) return 0.0;
    double sum_sq = 0.0;
    double total_time = 0.0;
    for (size_t i = 0; i < count; ++i) {
        sum_sq += torques[i] * torques[i] * durations[i];
        total_time += durations[i];
    }
    return (total_time > 0.0) ? sqrt(sum_sq / total_time) : 0.0;
}
