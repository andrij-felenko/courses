/* spatial_admittance_controller.h / .c */
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define DOF 6

typedef struct {
    double m_d[DOF];      /* Віртуальна маса/інерція (кг, кг·м²) */
    double b_d[DOF];      /* Віртуальне демпфування (Н·с/м, Н·м·с/рад) */
    double k_d[DOF];      /* Віртуальна жорсткість (Н/м, Н·м/рад) */
    double deadband[DOF]; /* Поріг чутливості за силою (Н, Н·м) */
    double max_vel[DOF];  /* Ліміт швидкості корекції (м/с, рад/с) */
    double max_disp[DOF]; /* Ліміт максимального зміщення (м, рад) */
} AdmittanceParams;

typedef struct {
    double pos_c[DOF];    /* Фактичне зміщення адмітансу Δx */
    double vel_c[DOF];    /* Швидкість зміни зміщення Δv */
    double acc_c[DOF];    /* Прискорення адмітансу Δa */
} AdmittanceState;

void admittance_init(AdmittanceState *state) {
    if (!state) return;
    memset(state, 0, sizeof(AdmittanceState));
}

void admittance_update(const AdmittanceParams *params,
                       AdmittanceState *state,
                       const double f_meas[DOF],
                       const double f_des[DOF],
                       double dt,
                       double x_cmd_out[DOF],
                       const double x_traj[DOF]) {
    if (!params || !state || !f_meas || !f_des || !x_cmd_out || !x_traj || dt <= 0.0) {
        return;
    }

    for (int i = 0; i < DOF; ++i) {
        /* 1. Обчислення похибки сили з компенсацією мертвої зони давача */
        double f_err = f_meas[i] - f_des[i];
        if (fabs(f_err) < params->deadband[i]) {
            f_err = 0.0;
        } else if (f_err > 0.0) {
            f_err -= params->deadband[i];
        } else {
            f_err += params->deadband[i];
        }

        /* 2. Обчислення цільового прискорення за рівнянням адмітансу:
           M_d · acc = F_err - B_d · vel - K_d · pos */
        double mass = (params->m_d[i] > 1e-4) ? params->m_d[i] : 1.0;
        double net_force = f_err - (params->b_d[i] * state->vel_c[i]) - (params->k_d[i] * state->pos_c[i]);
        state->acc_c[i] = net_force / mass;

        /* 3. Чисельне інтегрування швидкості та позиції (напівнеявний метод Ейлера) */
        state->vel_c[i] += state->acc_c[i] * dt;

        /* Сатурація швидкості задля безпеки оператора */
        if (state->vel_c[i] > params->max_vel[i]) {
            state->vel_c[i] = params->max_vel[i];
        } else if (state->vel_c[i] < -params->max_vel[i]) {
            state->vel_c[i] = -params->max_vel[i];
        }

        state->pos_c[i] += state->vel_c[i] * dt;

        /* Обмеження максимального просторового відхилення */
        if (state->pos_c[i] > params->max_disp[i]) {
            state->pos_c[i] = params->max_disp[i];
            state->vel_c[i] = 0.0;
        } else if (state->pos_c[i] < -params->max_disp[i]) {
            state->pos_c[i] = -params->max_disp[i];
            state->vel_c[i] = 0.0;
        }

        /* 4. Формування скоригованої траєкторії для позиційного контуру */
        x_cmd_out[i] = x_traj[i] - state->pos_c[i];
    }
}
