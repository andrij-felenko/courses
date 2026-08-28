#include <stdio.h>
#include <math.h>
#include <stdbool.h>

/* Фізичні константи в системі SI */
static const double C_LIGHT = 2.99792458e8;     /* швидкість світла, м/с */
static const double EPS0    = 8.8541878128e-12; /* електрична стала, Ф/м */
static const double Q_ELEM  = -1.602176634e-19; /* заряд електрона, Кл */
static const double M_ELEM  = 9.1093837015e-31; /* маса електрона, кг */
static const double PI_VAL  = 3.141592653589793;

/* Вектор стану частинки: координати та швидкості */
typedef struct {
    double x, y, z;
    double vx, vy, vz;
} ParticleState;

/* Похідні стану: швидкості та прискорення */
typedef struct {
    double dx, dy, dz;
    double dvx, dvy, dvz;
} StateDeriv;

/* Обчислення похідних стану за рівнянням Ландау-Ліфшиця */
static StateDeriv compute_derivatives(const ParticleState *s, double B0) {
    StateDeriv d;
    d.dx = s->vx;
    d.dy = s->vy;
    d.dz = s->vz;

    /* 1. Сила Лоренца: F_lor = q * (v x B), B = (0, 0, B0) */
    double F_lor_x = Q_ELEM * (s->vy * B0);
    double F_lor_y = Q_ELEM * (-s->vx * B0);
    double F_lor_z = 0.0;

    /* 2. Радіаційне гальмування Ландау-Ліфшиця: F_rad = -gamma_damp * v_perp */
    /* gamma_damp = q^4 * B0^2 / (6 * pi * eps0 * m^2 * c^3) */
    double gamma_damp = (pow(Q_ELEM, 4) * B0 * B0) /
                        (6.0 * PI_VAL * EPS0 * M_ELEM * M_ELEM * pow(C_LIGHT, 3));

    double F_rad_x = -gamma_damp * s->vx;
    double F_rad_y = -gamma_damp * s->vy;
    double F_rad_z = 0.0;

    /* Повне прискорення a = (F_lor + F_rad) / m */
    d.dvx = (F_lor_x + F_rad_x) / M_ELEM;
    d.dvy = (F_lor_y + F_rad_y) / M_ELEM;
    d.dvz = (F_lor_z + F_rad_z) / M_ELEM;

    return d;
}

/* Миттєва потужність випромінювання Лармора P = q^2 * a^2 / (6 * pi * eps0 * c^3) */
static double compute_larmor_power(double ax, double ay, double az) {
    double a_sq = ax * ax + ay * ay + az * az;
    return (Q_ELEM * Q_ELEM * a_sq) / (6.0 * PI_VAL * EPS0 * pow(C_LIGHT, 3));
}

/* Один крок інтегрування методом Рунге-Кутти 4-го порядку */
static ParticleState rk4_step(const ParticleState *s, double dt, double B0) {
    StateDeriv k1 = compute_derivatives(s, B0);

    ParticleState s2;
    s2.x  = s->x  + 0.5 * dt * k1.dx;
    s2.y  = s->y  + 0.5 * dt * k1.dy;
    s2.z  = s->z  + 0.5 * dt * k1.dz;
    s2.vx = s->vx + 0.5 * dt * k1.dvx;
    s2.vy = s->vy + 0.5 * dt * k1.dvy;
    s2.vz = s->vz + 0.5 * dt * k1.dvz;
    StateDeriv k2 = compute_derivatives(&s2, B0);

    ParticleState s3;
    s3.x  = s->x  + 0.5 * dt * k2.dx;
    s3.y  = s->y  + 0.5 * dt * k2.dy;
    s3.z  = s->z  + 0.5 * dt * k2.dz;
    s3.vx = s->vx + 0.5 * dt * k2.dvx;
    s3.vy = s->vy + 0.5 * dt * k2.dvy;
    s3.vz = s->vz + 0.5 * dt * k2.dvz;
    StateDeriv k3 = compute_derivatives(&s3, B0);

    ParticleState s4;
    s4.x  = s->x  + dt * k3.dx;
    s4.y  = s->y  + dt * k3.dy;
    s4.z  = s->z  + dt * k3.dz;
    s4.vx = s->vx + dt * k3.dvx;
    s4.vy = s->vy + dt * k3.dvy;
    s4.vz = s->vz + dt * k3.dvz;
    StateDeriv k4 = compute_derivatives(&s4, B0);

    ParticleState next;
    next.x  = s->x  + (dt / 6.0) * (k1.dx  + 2.0 * k2.dx  + 2.0 * k3.dx  + k4.dx);
    next.y  = s->y  + (dt / 6.0) * (k1.dy  + 2.0 * k2.dy  + 2.0 * k3.dy  + k4.dy);
    next.z  = s->z  + (dt / 6.0) * (k1.dz  + 2.0 * k2.dz  + 2.0 * k3.dz  + k4.dz);
    next.vx = s->vx + (dt / 6.0) * (k1.dvx + 2.0 * k2.dvx + 2.0 * k3.dvx + k4.dvx);
    next.vy = s->vy + (dt / 6.0) * (k1.dvy + 2.0 * k2.dvy + 2.0 * k3.dvy + k4.dvy);
    next.vz = s->vz + (dt / 6.0) * (k1.dvz + 2.0 * k2.dvz + 2.0 * k3.dvz + k4.dvz);

    return next;
}

int main(void) {
    const double B_FIELD = 5.0;            /* Магнітне поле, Тл */
    const double V_INIT  = 0.2 * C_LIGHT;  /* Початкова швидкість, м/с */
    const double DT      = 1.0e-13;        /* Крок інтегрування, с */
    const int    N_STEPS = 10000;          /* Кількість кроків */

    ParticleState state = {0.0, 0.0, 0.0, V_INIT, 0.0, 0.0};
    double total_radiated_energy = 0.0;
    double e_kin_initial = 0.5 * M_ELEM * V_INIT * V_INIT;

    printf("Крок | Час (пс) | R_орбіти (мкм) | V/c | Потужність (нВт) | E_рад (еВ)\n");
    printf("----------------------------------------------------------------------\n");

    for (int step = 0; step <= N_STEPS; ++step) {
        double t_ps = (step * DT) * 1.0e12;
        double v_sq = state.vx * state.vx + state.vy * state.vy + state.vz * state.vz;
        double v_mag = sqrt(v_sq);
        double r_cyclotron = (M_ELEM * v_mag) / (fabs(Q_ELEM) * B_FIELD) * 1.0e6;

        StateDeriv d = compute_derivatives(&state, B_FIELD);
        double p_inst = compute_larmor_power(d.dvx, d.dvy, d.dvz);

        if (step % 2000 == 0) {
            double e_rad_ev = total_radiated_energy / 1.602176634e-19;
            printf("%4d | %8.2f | %14.4f | %5.3f | %16.4e | %10.4f\n",
                   step, t_ps, r_cyclotron, v_mag / C_LIGHT, p_inst * 1.0e9, e_rad_ev);
        }

        /* Накопичення випроміненої енергії методом трапецій */
        total_radiated_energy += p_inst * DT;
        state = rk4_step(&state, DT, B_FIELD);
    }

    double e_kin_final = 0.5 * M_ELEM * (state.vx * state.vx + state.vy * state.vy);
    double delta_ekin = e_kin_initial - e_kin_final;

    printf("\nБаланс енергії:\n");
    printf("  Втрата кінетичної енергії: %.6e Дж (%.4f еВ)\n",
           delta_ekin, delta_ekin / 1.602176634e-19);
    printf("  Інтеграл випромінювання:   %.6e Дж (%.4f еВ)\n",
           total_radiated_energy, total_radiated_energy / 1.602176634e-19);

    return 0;
}
