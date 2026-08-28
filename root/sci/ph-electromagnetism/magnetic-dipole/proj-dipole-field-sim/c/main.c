#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MU0_OVER_4PI 1.0e-7
#define PLUMMER_EPS 1.0e-5
#define MAX_DIPOLES 100

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    Vec3 pos; // Положення r (м)
    Vec3 m;   // Магнітний момент m (А·м²)
} Dipole;

// Векторні операції
static inline Vec3 vec_add(Vec3 a, Vec3 b) {
    return (Vec3){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline Vec3 vec_sub(Vec3 a, Vec3 b) {
    return (Vec3){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline Vec3 vec_scale(Vec3 v, double s) {
    return (Vec3){v.x * s, v.y * s, v.z * s};
}

static inline double vec_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec_cross(Vec3 a, Vec3 b) {
    return (Vec3){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline double vec_norm(Vec3 v) {
    return sqrt(vec_dot(v, v));
}

static inline Vec3 vec_normalize(Vec3 v) {
    double len = vec_norm(v);
    if (len < 1.0e-12) return (Vec3){0.0, 0.0, 0.0};
    return vec_scale(v, 1.0 / len);
}

// Розрахунок суммарного поля B у точці p від системи N диполів
Vec3 compute_magnetic_field(Vec3 p, const Dipole *dipoles, int n_dipoles) {
    Vec3 B_sum = {0.0, 0.0, 0.0};
    for (int i = 0; i < n_dipoles; ++i) {
        Vec3 R = vec_sub(p, dipoles[i].pos);
        double r2 = vec_dot(R, R) + PLUMMER_EPS * PLUMMER_EPS;
        double r = sqrt(r2);
        double r5 = r2 * r2 * r;
        
        Vec3 R_hat = vec_scale(R, 1.0 / r);
        double m_dot_rhat = vec_dot(dipoles[i].m, R_hat);
        
        // B = (μ₀/4πr³) * [3(m·r̂)r̂ - m]
        Vec3 B_dip = vec_scale(
            vec_sub(vec_scale(R_hat, 3.0 * m_dot_rhat), dipoles[i].m),
            MU0_OVER_4PI / (r * r * r)
        );
        B_sum = vec_add(B_sum, B_dip);
    }
    return B_sum;
}

// Розрахунок сили F та моменту tau, що діють на target_idx-й диполь
void compute_force_and_torque(int target_idx, const Dipole *dipoles, int n_dipoles,
                             Vec3 *out_force, Vec3 *out_torque) {
    Vec3 F_sum = {0.0, 0.0, 0.0};
    Vec3 B_ext = {0.0, 0.0, 0.0};
    Dipole target = dipoles[target_idx];

    for (int j = 0; j < n_dipoles; ++j) {
        if (j == target_idx) continue;
        
        Vec3 R = vec_sub(target.pos, dipoles[j].pos);
        double r2 = vec_dot(R, R) + PLUMMER_EPS * PLUMMER_EPS;
        double r = sqrt(r2);
        double r4 = r2 * r2;
        Vec3 R_hat = vec_scale(R, 1.0 / r);

        double m1_r = vec_dot(dipoles[j].m, R_hat);
        double m2_r = vec_dot(target.m, R_hat);
        double m1_m2 = vec_dot(dipoles[j].m, target.m);

        // F = (3μ₀/4πr⁴) * [ (m₁·r̂)m₂ + (m₂·r̂)m₁ + (m₁·m₂ - 5(m₁·r̂)(m₂·r̂))r̂ ]
        Vec3 term1 = vec_scale(target.m, m1_r);
        Vec3 term2 = vec_scale(dipoles[j].m, m2_r);
        Vec3 term3 = vec_scale(R_hat, m1_m2 - 5.0 * m1_r * m2_r);
        Vec3 F_ij = vec_scale(
            vec_add(vec_add(term1, term2), term3),
            3.0 * MU0_OVER_4PI / r4
        );
        F_sum = vec_add(F_sum, F_ij);

        // Поле B_ext від j-го диполя у точці target.pos
        Vec3 B_j = vec_scale(
            vec_sub(vec_scale(R_hat, 3.0 * m1_r), dipoles[j].m),
            MU0_OVER_4PI / (r * r * r)
        );
        B_ext = vec_add(B_ext, B_j);
    }

    *out_force = F_sum;
    *out_torque = vec_cross(target.m, B_ext);
}

// Крок трасування силової лінії методом RK4
Vec3 trace_step_rk4(Vec3 curr, double step_size, const Dipole *dipoles, int n_dipoles) {
    Vec3 k1 = vec_normalize(compute_magnetic_field(curr, dipoles, n_dipoles));
    
    Vec3 p2 = vec_add(curr, vec_scale(k1, 0.5 * step_size));
    Vec3 k2 = vec_normalize(compute_magnetic_field(p2, dipoles, n_dipoles));

    Vec3 p3 = vec_add(curr, vec_scale(k2, 0.5 * step_size));
    Vec3 k3 = vec_normalize(compute_magnetic_field(p3, dipoles, n_dipoles));

    Vec3 p4 = vec_add(curr, vec_scale(k3, step_size));
    Vec3 k4 = vec_normalize(compute_magnetic_field(p4, dipoles, n_dipoles));

    Vec3 dr = vec_scale(
        vec_add(vec_add(k1, vec_scale(k2, 2.0)), vec_add(vec_scale(k3, 2.0), k4)),
        step_size / 6.0
    );
    return vec_add(curr, dr);
}

int main(void) {
    Dipole dipoles[2] = {
        {.pos = {-0.05, 0.0, 0.0}, .m = {0.0, 0.0, 1.0}}, // Диполь 1 у (-5см, 0, 0)
        {.pos = { 0.05, 0.0, 0.0}, .m = {0.0, 0.0, 1.0}}  // Диполь 2 у (+5см, 0, 0)
    };

    printf("=== СИМУЛЯЦІЯ ВЗАЄМОДІЇ ДВОХ МАГНІТНИХ ДИПОЛІВ (C) ===\n");
    
    Vec3 F0, tau0, F1, tau1;
    compute_force_and_torque(0, dipoles, 2, &F0, &tau0);
    compute_force_and_torque(1, dipoles, 2, &F1, &tau1);

    printf("Диполь 0: Сила F = (%e, %e, %e) Н\n", F0.x, F0.y, F0.z);
    printf("Диполь 0: Момент τ = (%e, %e, %e) Н·м\n", tau0.x, tau0.y, tau0.z);
    printf("Диполь 1: Сила F = (%e, %e, %e) Н\n", F1.x, F1.y, F1.z);
    printf("Диполь 1: Момент τ = (%e, %e, %e) Н·м\n", tau1.x, tau1.y, tau1.z);

    // Трасування силової лінії від точки (0.06, 0.0, 0.01)
    Vec3 start_p = {0.06, 0.0, 0.01};
    printf("\nТрасування силової лінії (RK4, 5 кроків):\n");
    Vec3 curr = start_p;
    for (int step = 0; step < 5; ++step) {
        Vec3 B = compute_magnetic_field(curr, dipoles, 2);
        printf("Крок %d: r = (%f, %f, %f) м, |B| = %e Тл\n", step, curr.x, curr.y, curr.z, vec_norm(B));
        curr = trace_step_rk4(curr, 0.01, dipoles, 2);
    }

    return 0;
}
