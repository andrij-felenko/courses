/* skyrmion_sim.c — Чисельне моделювання магнітного скирміона мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define M_PI_VAL 3.14159265358979323846

typedef struct {
    double x;
    double y;
    double z;
} Vector3;

static inline Vector3 vec_normalize(Vector3 v) {
    double len = sqrt(v.x * v.x + v.y * v.y + v.z * v.z);
    if (len > 1e-12) {
        v.x /= len;
        v.y /= len;
        v.z /= len;
    }
    return v;
}

static inline double vec_dot(Vector3 a, Vector3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vector3 vec_cross(Vector3 a, Vector3 b) {
    Vector3 res;
    res.x = a.y * b.z - a.z * b.y;
    res.y = a.z * b.x - a.x * b.z;
    res.z = a.x * b.y - a.y * b.x;
    return res;
}

/* Обчислення дискретного телесного кута трійки спінів (Ойлер — Аскер) */
static double solid_angle(Vector3 m1, Vector3 m2, Vector3 m3) {
    double triple_prod = vec_dot(m1, vec_cross(m2, m3));
    double denom = 1.0 + vec_dot(m1, m2) + vec_dot(m2, m3) + vec_dot(m3, m1);
    return 2.0 * atan2(triple_prod, denom);
}

typedef struct {
    int size;
    double grid_step;
    Vector3 *spins;
} SkyrmionGridC;

SkyrmionGridC* skyrmion_grid_create(int size, double step) {
    SkyrmionGridC *g = (SkyrmionGridC*)malloc(sizeof(SkyrmionGridC));
    if (!g) return NULL;
    g->size = size;
    g->grid_step = step;
    g->spins = (Vector3*)malloc(size * size * sizeof(Vector3));
    return g;
}

void skyrmion_grid_free(SkyrmionGridC *g) {
    if (g) {
        free(g->spins);
        free(g);
    }
}

static inline int grid_idx(int size, int r, int c) {
    return r * size + c;
}

/* Ініціалізація Неєлівського скирміона у центрі сітки */
void skyrmion_grid_init_neel(SkyrmionGridC *g, double radius) {
    int N = g->size;
    double center = (N - 1) / 2.0;

    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            double dx = (c - center) * g->grid_step;
            double dy = (r - center) * g->grid_step;
            double dist = sqrt(dx * dx + dy * dy);
            
            double theta = M_PI_VAL;
            if (dist < radius) {
                theta = M_PI_VAL * (1.0 - dist / radius);
            } else {
                theta = 0.0;
            }

            double phi = atan2(dy, dx); // Неєлівський скирміон (гамма = 0)

            Vector3 s;
            s.x = sin(theta) * cos(phi);
            s.y = sin(theta) * sin(phi);
            s.z = cos(theta);
            
            g->spins[grid_idx(N, r, c)] = vec_normalize(s);
        }
    }
}

/* Обчислення повного топологічного заряду Q */
double skyrmion_grid_calc_topological_charge(const SkyrmionGridC *g) {
    int N = g->size;
    double total_q = 0.0;

    for (int r = 0; r < N - 1; r++) {
        for (int c = 0; c < N - 1; c++) {
            Vector3 m00 = g->spins[grid_idx(N, r, c)];
            Vector3 m10 = g->spins[grid_idx(N, r, c + 1)];
            Vector3 m01 = g->spins[grid_idx(N, r + 1, c)];
            Vector3 m11 = g->spins[grid_idx(N, r + 1, c + 1)];

            // Перший трикутник (m00, m10, m01)
            double omega1 = solid_angle(m00, m10, m01);
            // Другий трикутник (m11, m01, m10)
            double omega2 = solid_angle(m11, m01, m10);

            total_q += (omega1 + omega2);
        }
    }

    return total_q / (4.0 * M_PI_VAL);
}

int main(void) {
    int N = 64;
    double step = 1.0e-9; // 1 nm
    double sk_radius = 12.0e-9; // 12 nm

    SkyrmionGridC *grid = skyrmion_grid_create(N, step);
    if (!grid) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    skyrmion_grid_init_neel(grid, sk_radius);
    double Q = skyrmion_grid_calc_topological_charge(grid);

    printf("Розмір ґратки: %d x %d\n", N, N);
    printf("Обчислений топологічний заряд Q = %.6f\n", Q);

    skyrmion_grid_free(grid);
    return 0;
}
