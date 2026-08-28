#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define VACUUM_EPSILON0 8.8541878128e-12
#define CUTOFF_EPSILON  1e-9
#define RK4_STEPS       500
#define RK4_STEP_SIZE   1e-10

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

typedef struct {
    Vector3 pos;
    Vector3 p;
} Dipole;

static Vector3 vec3_add(Vector3 a, Vector3 b) {
    Vector3 r = {a.x + b.x, a.y + b.y, a.z + b.z};
    return r;
}

static Vector3 vec3_sub(Vector3 a, Vector3 b) {
    Vector3 r = {a.x - b.x, a.y - b.y, a.z - b.z};
    return r;
}

static Vector3 vec3_scale(Vector3 a, double s) {
    Vector3 r = {a.x * s, a.y * s, a.z * s};
    return r;
}

static double vec3_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static Vector3 vec3_cross(Vector3 a, Vector3 b) {
    Vector3 r = {
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
    return r;
}

static double vec3_norm(Vector3 a) {
    return sqrt(vec3_dot(a, a));
}

static Vector3 vec3_normalize(Vector3 a) {
    double len = vec3_norm(a);
    if (len < 1e-18) {
        Vector3 zero = {0.0, 0.0, 0.0};
        return zero;
    }
    return vec3_scale(a, 1.0 / len);
}

double dipole_potential(const Dipole* d, Vector3 point) {
    Vector3 R = vec3_sub(point, d->pos);
    double r_sq = vec3_dot(R, R) + CUTOFF_EPSILON * CUTOFF_EPSILON;
    double r_len = sqrt(r_sq);
    double k_e = 1.0 / (4.0 * M_PI * VACUUM_EPSILON0);
    double dot_pR = vec3_dot(d->p, R);
    return k_e * dot_pR / (r_len * r_len * r_len);
}

Vector3 dipole_electric_field(const Dipole* d, Vector3 point) {
    Vector3 R = vec3_sub(point, d->pos);
    double r_sq = vec3_dot(R, R) + CUTOFF_EPSILON * CUTOFF_EPSILON;
    double r_len = sqrt(r_sq);
    double r_pow3 = r_len * r_len * r_len;
    double r_pow5 = r_pow3 * r_sq;
    double k_e = 1.0 / (4.0 * M_PI * VACUUM_EPSILON0);

    double dot_pR = vec3_dot(d->p, R);
    Vector3 term1 = vec3_scale(R, 3.0 * dot_pR / r_pow5);
    Vector3 term2 = vec3_scale(d->p, 1.0 / r_pow3);
    Vector3 diff = vec3_sub(term1, term2);

    return vec3_scale(diff, k_e);
}

Vector3 dipole_torque(const Dipole* d, Vector3 external_e) {
    return vec3_cross(d->p, external_e);
}

double dipole_potential_energy(const Dipole* d, Vector3 external_e) {
    return -vec3_dot(d->p, external_e);
}

int trace_field_line_rk4(const Dipole* d, Vector3 start_pt, Vector3* out_path, int max_points) {
    if (!d || !out_path || max_points <= 0) return 0;

    out_path[0] = start_pt;
    int count = 1;
    double h = RK4_STEP_SIZE;

    for (int i = 1; i < max_points; ++i) {
        Vector3 curr = out_path[i - 1];

        Vector3 E1 = dipole_electric_field(d, curr);
        Vector3 k1 = vec3_scale(vec3_normalize(E1), h);

        Vector3 p2 = vec3_add(curr, vec3_scale(k1, 0.5));
        Vector3 E2 = dipole_electric_field(d, p2);
        Vector3 k2 = vec3_scale(vec3_normalize(E2), h);

        Vector3 p3 = vec3_add(curr, vec3_scale(k2, 0.5));
        Vector3 E3 = dipole_electric_field(d, p3);
        Vector3 k3 = vec3_scale(vec3_normalize(E3), h);

        Vector3 p4 = vec3_add(curr, k3);
        Vector3 E4 = dipole_electric_field(d, p4);
        Vector3 k4 = vec3_scale(vec3_normalize(E4), h);

        Vector3 step = vec3_scale(
            vec3_add(vec3_add(k1, vec3_scale(k2, 2.0)), vec3_add(vec3_scale(k3, 2.0), k4)),
            1.0 / 6.0
        );

        Vector3 next_pt = vec3_add(curr, step);
        out_path[i] = next_pt;
        count++;

        if (vec3_norm(vec3_sub(next_pt, d->pos)) > 1e-7) {
            break; // Вихід за область аналізу
        }
    }
    return count;
}

int main(void) {
    Dipole d = {
        .pos = {0.0, 0.0, 0.0},
        .p = {0.0, 0.0, 1e-29} // 1 e·Å ≈ 1.6e-29 C·m
    };

    Vector3 eval_pt = {0.0, 0.0, 1e-9}; // 1 нм по осі z
    double phi = dipole_potential(&d, eval_pt);
    Vector3 E = dipole_electric_field(&d, eval_pt);

    printf("=== Симуляція диполя (C API) ===\n");
    printf("Потенціал phi(1nm) = %.6e V\n", phi);
    printf("Поле E(1nm) = (%.6e, %.6e, %.6e) V/m\n", E.x, E.y, E.z);

    Vector3 ext_E = {1e5, 0.0, 0.0};
    Vector3 torque = dipole_torque(&d, ext_E);
    double energy = dipole_potential_energy(&d, ext_E);

    printf("Обертальний момент torque = (%.6e, %.6e, %.6e) N·m\n", torque.x, torque.y, torque.z);
    printf("Потенціальна енергія U = %.6e J\n", energy);

    Vector3 line_pts[100];
    int n_pts = trace_field_line_rk4(&d, eval_pt, line_pts, 100);
    printf("Прораховано %d точок силової лінії RK4.\n", n_pts);

    return 0;
}
