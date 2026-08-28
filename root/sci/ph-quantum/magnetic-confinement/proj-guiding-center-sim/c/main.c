#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double R_0;      /* Великий радіус тора (м) */
    double a;        /* Малий радіус камери (м) */
    double B_0;      /* Тороїдальне поле на осі (Тл) */
    double B_pol_0;  /* Полоїдальне поле на краю (Тл) */
    double mass;     /* Маса частинки (кг) */
    double charge;   /* Заряд частинки (Кл) */
} PlasmaConfig;

typedef struct {
    double R;          /* Радіус (м) */
    double Z;          /* Висота (м) */
    double v_parallel; /* Паралельна швидкість (м/с) */
    double v_perp;     /* Перпендикулярна швидкість (м/с) */
} GuidingCenterState;

/* Крок чисельного інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
void gc_step_rk4(GuidingCenterState *s, const PlasmaConfig *cfg, double dt) {
    double q = cfg->charge;
    double m = cfg->mass;
    double R0 = cfg->R_0;
    double B0 = cfg->B_0;
    double Bpol0 = cfg->B_pol_0;

    /* Обчислення похідних в точці (R, Z) */
    auto compute_derivatives = [&](double R, double Z, double *dR, double *dZ) {
        double r = sqrt((R - R0)*(R - R0) + Z*Z);
        if (r < 1e-6) r = 1e-6;

        double B_phi = B0 * R0 / R;
        double B_pol = Bpol0 * (r / cfg->a);
        double B_total = sqrt(B_phi*B_phi + B_pol*B_pol);

        double mu = (m * s->v_perp * s->v_perp) / (2.0 * B_total);
        double v_drift_Z = (m * s->v_parallel * s->v_parallel + mu * B_total) / (q * B0 * R0);

        /* Обертальне перетворення (рух уздовж силової лінії B_pol) */
        double v_rot_R = -s->v_parallel * (B_pol / B_total) * (Z / r);
        double v_rot_Z =  s->v_parallel * (B_pol / B_total) * ((R - R0) / r);

        *dR = v_rot_R;
        *dZ = v_rot_Z + v_drift_Z;
    };

    double dR1, dZ1, dR2, dZ2, dR3, dZ3, dR4, dZ4;
    compute_derivatives(s->R, s->Z, &dR1, &dZ1);
    compute_derivatives(s->R + 0.5*dt*dR1, s->Z + 0.5*dt*dZ1, &dR2, &dZ2);
    compute_derivatives(s->R + 0.5*dt*dR2, s->Z + 0.5*dt*dZ2, &dR3, &dZ3);
    compute_derivatives(s->R + dt*dR3, s->Z + dt*dZ3, &dR4, &dZ4);

    s->R += (dt / 6.0) * (dR1 + 2.0*dR2 + 2.0*dR3 + dR4);
    s->Z += (dt / 6.0) * (dZ1 + 2.0*dZ2 + 2.0*dZ3 + dZ4);
}

int main(void) {
    PlasmaConfig cfg = {
        .R_0 = 1.65,      /* Параметри токамака ASDEX Upgrade */
        .a = 0.5,
        .B_0 = 2.5,
        .B_pol_0 = 0.3,   /* Якщо 0.0 — суто тороїдальне поле без B_θ */
        .mass = 3.34e-27, /* Маса дейтерієвого іона D+ */
        .charge = 1.602e-19
    };

    GuidingCenterState state = {
        .R = 1.85,
        .Z = 0.0,
        .v_parallel = 5.0e5, /* Теплова швидкість T ~ 2 keV */
        .v_perp = 7.0e5
    };

    double dt = 1.0e-8;
    int num_steps = 10000;

    printf("Крок\tR (м)\t\tZ (м)\n");
    for (int i = 0; i <= num_steps; i++) {
        if (i % 1000 == 0) {
            printf("%d\t%.6f\t%.6f\n", i, state.R, state.Z);
        }
        gc_step_rk4(&state, &cfg, dt);
    }

    return 0;
}
