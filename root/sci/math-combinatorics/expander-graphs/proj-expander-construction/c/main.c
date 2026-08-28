#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

typedef struct {
    int x;
    int y;
} Vertex;

static inline int mod_m(int a, int m) {
    int r = a % m;
    return r < 0 ? r + m : r;
}

// Повертає 8 сусідів вершини (x, y) у графі Маргуліса — Габбера — Галіля
void get_mgg_neighbors(Vertex v, int m, Vertex neighbors[8]) {
    int x = v.x;
    int y = v.y;

    neighbors[0] = (Vertex){x, mod_m(y + x, m)};
    neighbors[1] = (Vertex){x, mod_m(y - x, m)};
    neighbors[2] = (Vertex){x, mod_m(y + x + 1, m)};
    neighbors[3] = (Vertex){x, mod_m(y - x - 1, m)};
    neighbors[4] = (Vertex){mod_m(x + y, m), y};
    neighbors[5] = (Vertex){mod_m(x - y, m), y};
    neighbors[6] = (Vertex){mod_m(x + y + 1, m), y};
    neighbors[7] = (Vertex){mod_m(x - y - 1, m), y};
}

// Випадкове блукання довжиною steps від початкової вершини
void expander_random_walk(Vertex start, int m, int steps, Vertex *path) {
    Vertex current = start;
    path[0] = current;
    Vertex neighbors[8];

    for (int k = 1; k <= steps; ++k) {
        get_mgg_neighbors(current, m, neighbors);
        int next_idx = rand() % 8;
        current = neighbors[next_idx];
        path[k] = current;
    }
}

// Монотонний нормалізатор вектора
static void normalize_vector(double *v, int size) {
    double norm = 0.0;
    for (int i = 0; i < size; ++i) {
        norm += v[i] * v[i];
    }
    norm = sqrt(norm);
    if (norm > 1e-12) {
        for (int i = 0; i < size; ++i) {
            v[i] /= norm;
        }
    }
}

// Ортогоналізація відносно постійного першого власного вектора v1 = (1/√N, ..., 1/√N)
static void project_perpendicular_to_v1(double *v, int size) {
    double sum = 0.0;
    for (int i = 0; i < size; ++i) {
        sum += v[i];
    }
    double avg = sum / size;
    for (int i = 0; i < size; ++i) {
        v[i] -= avg;
    }
}

// Обчислення другого власного значення λ2 методом степенів (Power Iteration)
double compute_mgg_lambda2(int m, int max_iterations, double tol) {
    int N = m * m;
    double *v = (double *)malloc(N * sizeof(double));
    double *next_v = (double *)malloc(N * sizeof(double));

    if (!v || !next_v) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        free(v);
        free(next_v);
        return -1.0;
    }

    // Ініціалізація випадковим вектором
    for (int i = 0; i < N; ++i) {
        v[i] = ((double)rand() / RAND_MAX) - 0.5;
    }

    project_perpendicular_to_v1(v, N);
    normalize_vector(v, N);

    double lambda2 = 0.0;
    Vertex neighbors[8];

    for (int iter = 0; iter < max_iterations; ++iter) {
        // Множення на матрицю суміжності: next_v = A * v
        for (int i = 0; i < N; ++i) {
            next_v[i] = 0.0;
        }

        for (int idx = 0; idx < N; ++idx) {
            Vertex cur = {idx / m, idx % m};
            get_mgg_neighbors(cur, m, neighbors);
            for (int k = 0; k < 8; ++k) {
                int n_idx = neighbors[k].x * m + neighbors[k].y;
                next_v[n_idx] += v[idx];
            }
        }

        // Ортогоналізація відносно v1 для видалення компоненти першого власного вектора (λ1 = 8)
        project_perpendicular_to_v1(next_v, N);

        // Оцінка значення Рейлі: λ2 = v^T * next_v
        double rayleigh = 0.0;
        for (int i = 0; i < N; ++i) {
            rayleigh += v[i] * next_v[i];
        }

        normalize_vector(next_v, N);

        double diff = fabs(rayleigh - lambda2);
        lambda2 = rayleigh;

        for (int i = 0; i < N; ++i) {
            v[i] = next_v[i];
        }

        if (diff < tol) {
            break;
        }
    }

    free(v);
    free(next_v);
    return lambda2;
}

int main(void) {
    int m = 12; // Сітка 12x12 (N = 144)
    printf("--- Тестування графа Маргуліса — Габбера — Галіля (m = %d, N = %d) ---\n", m, m * m);

    Vertex start = {0, 0};
    Vertex neighbors[8];
    get_mgg_neighbors(start, m, neighbors);

    printf("Сусіди вершини (0, 0):\n");
    for (int i = 0; i < 8; ++i) {
        printf("  Сусід %d: (%d, %d)\n", i + 1, neighbors[i].x, neighbors[i].y);
    }

    double lambda2 = compute_mgg_lambda2(m, 500, 1e-6);
    double gap = 8.0 - lambda2;

    printf("\nСпектральний аналіз:\n");
    printf("  d (степінь) = 8\n");
    printf("  λ₂ (друге власне значення) = %.6f\n", lambda2);
    printf("  Спектральна щілина γ = d - λ₂ = %.6f\n", gap);

    return 0;
}
