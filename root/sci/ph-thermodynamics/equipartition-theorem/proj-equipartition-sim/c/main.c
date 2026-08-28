#include <stdio.h>
#include <stdlib.h>
#include <math.h>

typedef struct {
    double x, y;
} Vec2C;

typedef struct {
    Vec2C r1, r2;
    Vec2C v1, v2;
    Vec2C f1, f2;
    double m1, m2;
    double r0;
    double k_spring;
} DiatomicMoleculeC;

static inline Vec2C vec_add(Vec2C a, Vec2C b) { return (Vec2C){a.x + b.x, a.y + b.y}; }
static inline Vec2C vec_sub(Vec2C a, Vec2C b) { return (Vec2C){a.x - b.x, a.y - b.y}; }
static inline Vec2C vec_scale(Vec2C a, double s) { return (Vec2C){a.x * s, a.y * s}; }
static inline double vec_dot(Vec2C a, Vec2C b) { return a.x * b.x + a.y * b.y; }
static inline double vec_norm_sq(Vec2C a) { return a.x * a.x + a.y * a.y; }

void compute_forces_c(DiatomicMoleculeC* m, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        Vec2C r_rel = vec_sub(m[i].r2, m[i].r1);
        double dist = sqrt(vec_norm_sq(r_rel));
        double dr = dist - m[i].r0;
        Vec2C dir = vec_scale(r_rel, 1.0 / (dist > 1e-9 ? dist : 1.0));
        Vec2C f_spring = vec_scale(dir, m[i].k_spring * dr);
        m[i].f1 = f_spring;
        m[i].f2 = vec_scale(f_spring, -1.0);
    }
}

void simulation_step_c(DiatomicMoleculeC* m, size_t n, double dt) {
    for (size_t i = 0; i < n; ++i) {
        m[i].v1 = vec_add(m[i].v1, vec_scale(m[i].f1, 0.5 * dt / m[i].m1));
        m[i].v2 = vec_add(m[i].v2, vec_scale(m[i].f2, 0.5 * dt / m[i].m2));
        m[i].r1 = vec_add(m[i].r1, vec_scale(m[i].v1, dt));
        m[i].r2 = vec_add(m[i].r2, vec_scale(m[i].v2, dt));
    }
    compute_forces_c(mol, n);
    for (size_t i = 0; i < n; ++i) {
        m[i].v1 = vec_add(m[i].v1, vec_scale(m[i].f1, 0.5 * dt / m[i].m1));
        m[i].v2 = vec_add(m[i].v2, vec_scale(m[i].f2, 0.5 * dt / m[i].m2));
    }
}

int main(void) {
    const size_t num_mol = 100;
    const double dt = 0.001;
    DiatomicMoleculeC* mol = (DiatomicMoleculeC*)malloc(num_mol * sizeof(DiatomicMoleculeC));

    for (size_t i = 0; i < num_mol; ++i) {
        mol[i].m1 = 1.0; mol[i].m2 = 1.0;
        mol[i].r0 = 1.0; mol[i].k_spring = 100.0;
        mol[i].r1 = (Vec2C){(double)(i % 10) * 4.0, (double)(i / 10) * 4.0};
        mol[i].r2 = (Vec2C){mol[i].r1.x + 1.0, mol[i].r1.y};
        mol[i].v1 = (Vec2C){(double)(i % 5) * 1.5, 0.1};
        mol[i].v2 = (Vec2C){-(double)(i % 5) * 1.5, -0.1};
    }

    compute_forces_c(mol, num_mol);

    printf("Крок\tE_trans\tE_rot\tE_vib\n");
    for (int step = 0; step <= 3000; ++step) {
        simulation_step_c(mol, num_mol, dt);
        if (step % 1000 == 0) {
            double sum_trans = 0, sum_rot = 0, sum_vib = 0;
            for (size_t i = 0; i < num_mol; ++i) {
                double M = mol[i].m1 + mol[i].m2;
                Vec2C v_cm = vec_scale(vec_add(vec_scale(mol[i].v1, mol[i].m1), vec_scale(mol[i].v2, mol[i].m2)), 1.0 / M);
                sum_trans += 0.5 * M * vec_norm_sq(v_cm);

                Vec2C r_rel = vec_sub(mol[i].r2, mol[i].r1);
                double dist = sqrt(vec_norm_sq(r_rel));
                Vec2C n = vec_scale(r_rel, 1.0 / dist);
                Vec2C v_rel = vec_sub(mol[i].v2, mol[i].v1);
                double v_vib = vec_dot(v_rel, n);
                double v_rot = v_rel.x * n.y - v_rel.y * n.x;

                double mu = (mol[i].m1 * mol[i].m2) / M;
                sum_vib += 0.5 * mu * v_vib * v_vib + 0.5 * mol[i].k_spring * (dist - mol[i].r0) * (dist - mol[i].r0);
                sum_rot += 0.5 * mu * v_rot * v_rot;
            }
            printf("%d\t%.4f\t%.4f\t%.4f\n", step, sum_trans / num_mol, sum_rot / num_mol, sum_vib / num_mol);
        }
    }

    free(mol);
    return 0;
}
