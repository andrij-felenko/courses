#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define EPSILON_0 8.854187817e-12 // Електрична стала (Ф/м)

typedef struct {
    int nx, ny, nz;
    double h;           // Крок сітки (м)
    double *v;          // Скалярний потенціал V (Вольт)
    double *rho;        // Об'ємна густина заряду (Кл/м³)
    double *ex;         // Компонента поля Ex (В/м)
    double *ey;         // Компонента поля Ey (В/м)
    double *ez;         // Компонента поля Ez (В/м)
    bool *fixed;        // Граничні умови Діріхле (true = фіксований потенціал)
} Grid3D;

// Отримання лінійного індексу в плоскому масиві 3D
static inline int idx(const Grid3D *g, int i, int j, int k) {
    return i * (g->ny * g->nz) + j * g->nz + k;
}

// Створення та ініціалізація сітки
Grid3D* grid_create(int nx, int ny, int nz, double h) {
    Grid3D *g = (Grid3D*)malloc(sizeof(Grid3D));
    if (!g) return NULL;

    g->nx = nx;
    g->ny = ny;
    g->nz = nz;
    g->h = h;

    size_t num_cells = (size_t)nx * ny * nz;
    g->v = (double*)calloc(num_cells, sizeof(double));
    g->rho = (double*)calloc(num_cells, sizeof(double));
    g->ex = (double*)calloc(num_cells, sizeof(double));
    g->ey = (double*)calloc(num_cells, sizeof(double));
    g->ez = (double*)calloc(num_cells, sizeof(double));
    g->fixed = (bool*)calloc(num_cells, sizeof(bool));

    if (!g->v || !g->rho || !g->ex || !g->ey || !g->ez || !g->fixed) {
        free(g->v); free(g->rho); free(g->ex); free(g->ey); free(g->ez); free(g->fixed);
        free(g);
        return NULL;
    }
    return g;
}

// Звільнення пам'яті
void grid_free(Grid3D *g) {
    if (!g) return;
    free(g->v);
    free(g->rho);
    free(g->ex);
    free(g->ey);
    free(g->ez);
    free(g->fixed);
    free(g);
}

// Задання точкового або об'ємного заряду
void grid_add_charge(Grid3D *g, int i, int j, int k, double q_coulombs) {
    if (i >= 0 && i < g->nx && j >= 0 && j < g->ny && k >= 0 && k < g->nz) {
        double cell_volume = g->h * g->h * g->h;
        g->rho[idx(g, i, j, k)] += q_coulombs / cell_volume;
    }
}

// Ітераційний розв'язувач Пуассона методом SOR
int grid_solve_poisson(Grid3D *g, double tol, int max_iter, double omega) {
    double h2 = g->h * g->h;
    double inv_eps = 1.0 / EPSILON_0;

    for (int iter = 0; iter < max_iter; iter++) {
        double max_diff = 0.0;

        for (int i = 1; i < g->nx - 1; i++) {
            for (int j = 1; j < g->ny - 1; j++) {
                for (int k = 1; k < g->nz - 1; k++) {
                    int curr = idx(g, i, j, k);
                    if (g->fixed[curr]) continue;

                    double v_old = g->v[curr];
                    double sum_neighbors = g->v[idx(g, i+1, j, k)] + g->v[idx(g, i-1, j, k)] +
                                           g->v[idx(g, i, j+1, k)] + g->v[idx(g, i, j-1, k)] +
                                           g->v[idx(g, i, j, k+1)] + g->v[idx(g, i, j, k-1)];

                    double v_gs = (sum_neighbors + h2 * g->rho[curr] * inv_eps) / 6.0;
                    double v_new = (1.0 - omega) * v_old + omega * v_gs;

                    g->v[curr] = v_new;
                    double diff = fabs(v_new - v_old);
                    if (diff > max_diff) max_diff = diff;
                }
            }
        }

        if (max_diff < tol) {
            return iter + 1; // Успішна збіжність
        }
    }
    return max_iter;
}

// Обчислення векторного поля E = -grad(V)
void grid_compute_electric_field(Grid3D *g) {
    double inv_2h = 1.0 / (2.0 * g->h);

    for (int i = 1; i < g->nx - 1; i++) {
        for (int j = 1; j < g->ny - 1; j++) {
            for (int k = 1; k < g->nz - 1; k++) {
                int id = idx(g, i, j, k);
                g->ex[id] = -(g->v[idx(g, i+1, j, k)] - g->v[idx(g, i-1, j, k)]) * inv_2h;
                g->ey[id] = -(g->v[idx(g, i, j+1, k)] - g->v[idx(g, i, j-1, k)]) * inv_2h;
                g->ez[id] = -(g->v[idx(g, i, j, k+1)] - g->v[idx(g, i, j, k-1)]) * inv_2h;
            }
        }
    }
}

// Чисельна перевірка закону Гаусса: інтегрування потоку ∮ E · dA
double grid_verify_gauss_law(const Grid3D *g, int i1, int i2, int j1, int j2, int k1, int k2, double *out_q_enclosed) {
    double flux = 0.0;
    double area_elem = g->h * g->h;
    double q_sum = 0.0;

    // Підсумовування вільних зарядів усередині кубоїда
    for (int i = i1; i <= i2; i++) {
        for (int j = j1; j <= j2; j++) {
            for (int k = k1; k <= k2; k++) {
                q_sum += g->rho[idx(g, i, j, k)] * (g->h * g->h * g->h);
            }
        }
    }
    *out_q_enclosed = q_sum;

    // Грані X (ліва та права)
    for (int j = j1; j <= j2; j++) {
        for (int k = k1; k <= k2; k++) {
            flux += -g->ex[idx(g, i1, j, k)] * area_elem; // Ліва грань (нормаль -X)
            flux +=  g->ex[idx(g, i2, j, k)] * area_elem; // Права грань (нормаль +X)
        }
    }

    // Грані Y (нижня та верхня)
    for (int i = i1; i <= i2; i++) {
        for (int k = k1; k <= k2; k++) {
            flux += -g->ey[idx(g, i, j1, k)] * area_elem; // Нижня грань (нормаль -Y)
            flux +=  g->ey[idx(g, i, j2, k)] * area_elem; // Верхня грань (нормаль +Y)
        }
    }

    // Грані Z (ближня та далека)
    for (int i = i1; i <= i2; i++) {
        for (int j = j1; j <= j2; j++) {
            flux += -g->ez[idx(g, i, j, k1)] * area_elem; // Ближня грань (нормаль -Z)
            flux +=  g->ez[idx(g, i, j, k2)] * area_elem; // Далека грань (нормаль +Z)
        }
    }

    return flux;
}

int main(void) {
    int n = 41;         // Розмір сітки 41x41x41
    double h = 0.05;    // Крок сітки 5 см (розмір області 2x2x2 м)
    Grid3D *g = grid_create(n, n, n, h);
    if (!g) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    // Поміщаємо заряд +1 нКл в центр сітки
    int center = n / 2;
    double charge_q = 1.0e-9; // 1 нКл
    grid_add_charge(g, center, center, center, charge_q);

    // Встановлюємо нульові граничні умови на межах області (V = 0)
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            g->fixed[idx(g, i, j, 0)] = true; g->v[idx(g, i, j, 0)] = 0.0;
            g->fixed[idx(g, i, j, n-1)] = true; g->v[idx(g, i, j, n-1)] = 0.0;
            g->fixed[idx(g, i, 0, j)] = true; g->v[idx(g, i, 0, j)] = 0.0;
            g->fixed[idx(g, i, n-1, j)] = true; g->v[idx(g, i, n-1, j)] = 0.0;
            g->fixed[idx(g, 0, i, j)] = true; g->v[idx(g, 0, i, j)] = 0.0;
            g->fixed[idx(g, n-1, i, j)] = true; g->v[idx(g, n-1, i, j)] = 0.0;
        }
    }

    printf("Розв'язання рівняння Пуассона (SOR)... ");
    int iters = grid_solve_poisson(g, 1.0e-5, 2000, 1.6);
    printf("Збіжність за %d ітерацій.\n", iters);

    grid_compute_electric_field(g);

    // Перевірка закону Гаусса на кубічній поверхні навколо центру (розмір 10x10x10 комірок)
    double q_enc = 0.0;
    int margin = 5;
    double flux = grid_verify_gauss_law(g, center - margin, center + margin,
                                           center - margin, center + margin,
                                           center - margin, center + margin, &q_enc);

    double expected_flux = q_enc / EPSILON_0;
    double rel_error = fabs(flux - expected_flux) / expected_flux * 100.0;

    printf("\n=== РЕЗУЛЬТАТИ ЧИСЕЛЬНОЇ ПЕРЕВІРКИ ЗАКОНУ ГАУССА ===\n");
    printf("Внутрішній заряд Q_enclosed : %.4e Кл\n", q_enc);
    printf("Обчислений потік ∮ E · dA   : %.4e В·м\n", flux);
    printf("Теоретичний потік Q / eps0  : %.4e В·м\n", expected_flux);
    printf("Відносна похибка сітки     : %.2f%%\n", rel_error);

    grid_free(g);
    return 0;
}
