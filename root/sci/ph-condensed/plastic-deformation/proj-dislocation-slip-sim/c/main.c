/* Simulation of Schmid factor and dislocation strain hardening in C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define NUM_SLIP_SYSTEMS 12

typedef struct {
    double n[3]; /* Нормаль до площини ковзання */
    double s[3]; /* Напрямок ковзання */
} SlipSystem;

typedef struct {
    double G_GPa;      /* Модуль зсуву (ГПа) */
    double b_nm;       /* Вектор Бюргерса (нм) */
    double tau_0_MPa;  /* Паєрлсівське напруження (МПа) */
    double alpha;      /* Коефіцієнт зміцнення Тейлора */
    double k1;         /* Коефіцієнт накопичення дислокацій (м^-1) */
    double k2;         /* Коефіцієнт анігіляції дислокацій */
    double rho_0;      /* Початкова щільність дислокацій (м^-2) */
} MaterialParams;

/* 12 систем ковзання ГЦК кристала {111}<110> */
static const SlipSystem FCC_SLIP_SYSTEMS[NUM_SLIP_SYSTEMS] = {
    /* Площина (1, 1, 1) */
    {{ 1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
    {{ 1.0,  1.0,  1.0}, { 1.0,  0.0, -1.0}},
    {{ 1.0,  1.0,  1.0}, { 1.0, -1.0,  0.0}},
    /* Площина (-1, 1, 1) */
    {{-1.0,  1.0,  1.0}, { 0.0,  1.0, -1.0}},
    {{-1.0,  1.0,  1.0}, { 1.0,  0.0,  1.0}},
    {{-1.0,  1.0,  1.0}, { 1.0,  1.0,  0.0}},
    /* Площина (1, -1, 1) */
    {{ 1.0, -1.0,  1.0}, { 0.0,  1.0,  1.0}},
    {{ 1.0, -1.0,  1.0}, { 1.0,  0.0, -1.0}},
    {{ 1.0, -1.0,  1.0}, { 1.0,  1.0,  0.0}},
    /* Площина (1, 1, -1) */
    {{ 1.0,  1.0, -1.0}, { 0.0,  1.0,  1.0}},
    {{ 1.0,  1.0, -1.0}, { 1.0,  0.0,  1.0}},
    {{ 1.0,  1.0, -1.0}, { 1.0, -1.0,  0.0}}
};

static double dot_product(const double v1[3], const double v2[3]) {
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2];
}

static double vector_norm(const double v[3]) {
    return sqrt(dot_product(v, v));
}

/* Обчислення максимального фактора Шміда */
double calculate_max_schmid_factor(const double tensile_axis[3], int *best_system_idx) {
    double norm_axis = vector_norm(tensile_axis);
    if (norm_axis < 1e-9) return 0.0;

    double n_dir[3] = {
        tensile_axis[0] / norm_axis,
        tensile_axis[1] / norm_axis,
        tensile_axis[2] / norm_axis
    };

    double max_m = 0.0;
    int best_idx = 0;

    for (int i = 0; i < NUM_SLIP_SYSTEMS; ++i) {
        double n_norm = vector_norm(FCC_SLIP_SYSTEMS[i].n);
        double s_norm = vector_norm(FCC_SLIP_SYSTEMS[i].s);

        double cos_phi = fabs(dot_product(n_dir, FCC_SLIP_SYSTEMS[i].n)) / n_norm;
        double cos_lambda = fabs(dot_product(n_dir, FCC_SLIP_SYSTEMS[i].s)) / s_norm;

        double m = cos_phi * cos_lambda;
        if (m > max_m) {
            max_m = m;
            best_idx = i;
        }
    }

    if (best_system_idx) *best_system_idx = best_idx;
    return max_m;
}

/* Симуляція кривої розтягу σ(ε_p) */
void simulate_strain_hardening(const MaterialParams *mat, double max_strain, int steps) {
    double tensile_axis[3] = {1.0, 2.0, 3.0}; /* Орієнтація напрямку розтягу */
    int active_system = 0;
    double m_max = calculate_max_schmid_factor(tensile_axis, &active_system);

    printf("Орієнтація вісі розтягу: [1, 2, 3]\n");
    printf("Максимальний фактор Шміда m_max = %.4f (Система #%d)\n", m_max, active_system + 1);
    printf("--------------------------------------------------\n");
    printf("Деформація ε_p | Щільність ρ (м^-2) | Напруження σ (МПа)\n");
    printf("--------------------------------------------------\n");

    double rho = mat->rho_0;
    double d_eps = max_strain / steps;
    double G_Pa = mat->G_GPa * 1e9;
    double b_m = mat->b_nm * 1e-9;

    for (int step = 0; step <= steps; ++step) {
        double eps_p = step * d_eps;

        /* Формула Тейлора для зсувного напруження τ */
        double tau = (mat->tau_0_MPa * 1e6) + mat->alpha * G_Pa * b_m * sqrt(rho);
        double sigma_MPa = (tau / 1e6) / m_max;

        if (step % (steps / 5) == 0) {
            printf("%14.3f | %17.3e | %19.2f\n", eps_p, rho, sigma_MPa);
        }

        /* Крок інтегрування методом Ейлера: dρ/dε_p = k1*sqrt(ρ) - k2*ρ */
        double drho_deps = mat->k1 * sqrt(rho) - mat->k2 * rho;
        rho += drho_deps * d_eps;
    }
}

int main(void) {
    MaterialParams copper = {
        .G_GPa = 48.0,
        .b_nm = 0.256,
        .tau_0_MPa = 1.5,
        .alpha = 0.3,
        .k1 = 4.5e8,
        .k2 = 12.0,
        .rho_0 = 1.0e11
    };

    simulate_strain_hardening(&copper, 0.20, 100);
    return 0;
}
