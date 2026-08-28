#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HUNGARIAN_INF (INT64_MAX / 4)

typedef enum {
    HUNGARIAN_MINIMIZE = 0,
    HUNGARIAN_MAXIMIZE = 1
} HungarianObjective;

typedef struct {
    int64_t total_cost;
    int32_t* assignment; /* assignment[i] містить індекс стовпця для рядка i (0..m-1) */
    int32_t rows;
    int32_t cols;
} HungarianSolution;

void hungarian_solution_free(HungarianSolution* sol) {
    if (sol && sol->assignment) {
        free(sol->assignment);
        sol->assignment = NULL;
    }
}

HungarianSolution hungarian_solve_dense(
    const int64_t* cost_matrix,
    int32_t n,
    int32_t m,
    HungarianObjective objective
) {
    HungarianSolution sol;
    sol.rows = n;
    sol.cols = m;
    sol.total_cost = 0;
    sol.assignment = (int32_t*)malloc((size_t)n * sizeof(int32_t));
    if (!sol.assignment) return sol;
    for (int32_t i = 0; i < n; ++i) sol.assignment[i] = -1;

    int64_t* work_matrix = (int64_t*)malloc((size_t)n * (size_t)m * sizeof(int64_t));
    if (!work_matrix) {
        free(sol.assignment);
        sol.assignment = NULL;
        return sol;
    }

    if (objective == HUNGARIAN_MAXIMIZE) {
        int64_t max_val = cost_matrix[0];
        for (int32_t i = 1; i < n * m; ++i) {
            if (cost_matrix[i] > max_val) max_val = cost_matrix[i];
        }
        for (int32_t i = 0; i < n * m; ++i) {
            work_matrix[i] = max_val - cost_matrix[i];
        }
    } else {
        memcpy(work_matrix, cost_matrix, (size_t)n * (size_t)m * sizeof(int64_t));
    }

    int64_t* u = (int64_t*)calloc((size_t)(n + 1), sizeof(int64_t));
    int64_t* v = (int64_t*)calloc((size_t)(m + 1), sizeof(int64_t));
    int32_t* p = (int32_t*)calloc((size_t)(m + 1), sizeof(int32_t));
    int32_t* way = (int32_t*)calloc((size_t)(m + 1), sizeof(int32_t));
    int64_t* minv = (int64_t*)malloc((size_t)(m + 1) * sizeof(int64_t));
    bool* used = (bool*)malloc((size_t)(m + 1) * sizeof(bool));

    for (int32_t i = 1; i <= n; ++i) {
        p[0] = i;
        int32_t j0 = 0;
        for (int32_t j = 0; j <= m; ++j) {
            minv[j] = HUNGARIAN_INF;
            used[j] = false;
        }

        do {
            used[j0] = true;
            int32_t i0 = p[j0];
            int64_t delta = HUNGARIAN_INF;
            int32_t j1 = 0;

            for (int32_t j = 1; j <= m; ++j) {
                if (!used[j]) {
                    int64_t cur = work_matrix[(i0 - 1) * m + (j - 1)] - u[i0] - v[j];
                    if (cur < minv[j]) {
                        minv[j] = cur;
                        way[j] = j0;
                    }
                    if (minv[j] < delta) {
                        delta = minv[j];
                        j1 = j;
                    }
                }
            }

            for (int32_t j = 0; j <= m; ++j) {
                if (used[j]) {
                    u[p[j]] += delta;
                    v[j] -= delta;
                } else {
                    minv[j] -= delta;
                }
            }
            j0 = j1;
        } while (p[j0] != 0);

        do {
            int32_t j1 = way[j0];
            p[j0] = p[j1];
            j0 = j1;
        } while (j0 != 0);
    }

    for (int32_t j = 1; j <= m; ++j) {
        if (p[j] > 0 && p[j] <= n) {
            sol.assignment[p[j] - 1] = j - 1;
        }
    }

    int64_t total = 0;
    for (int32_t i = 0; i < n; ++i) {
        if (sol.assignment[i] >= 0) {
            total += cost_matrix[i * m + sol.assignment[i]];
        }
    }
    sol.total_cost = total;

    free(work_matrix);
    free(u); free(v); free(p); free(way); free(minv); free(used);
    return sol;
}

int main(void) {
    const int32_t N = 3, M = 3;
    const int64_t costs[9] = {
        10, 19, 8,
        10, 18, 7,
        13, 16, 9
    };

    HungarianSolution sol = hungarian_solve_dense(costs, N, M, HUNGARIAN_MINIMIZE);
    printf("Total min cost: %lld\n", (long long)sol.total_cost);
    for (int32_t i = 0; i < N; ++i) {
        printf("Row %d -> Col %d (cost %lld)\n", i, sol.assignment[i],
               (long long)costs[i * M + sol.assignment[i]]);
    }
    hungarian_solution_free(&sol);
    return 0;
}
