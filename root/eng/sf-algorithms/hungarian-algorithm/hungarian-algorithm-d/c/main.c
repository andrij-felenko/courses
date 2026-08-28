#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define HUNGARIAN_INF INT64_MAX / 4

typedef struct {
    int64_t total_cost;
    int32_t* assignment; /* assignment[i] містить індекс стовпця для рядка i */
    int32_t n;
} HungarianResult;

HungarianResult hungarian_solve(const int64_t* matrix, int32_t n) {
    HungarianResult res;
    res.n = n;
    res.total_cost = 0;
    res.assignment = (int32_t*)malloc((size_t)n * sizeof(int32_t));

    int64_t* u = (int64_t*)calloc((size_t)(n + 1), sizeof(int64_t));
    int64_t* v = (int64_t*)calloc((size_t)(n + 1), sizeof(int64_t));
    int32_t* p = (int32_t*)calloc((size_t)(n + 1), sizeof(int32_t));
    int32_t* way = (int32_t*)calloc((size_t)(n + 1), sizeof(int32_t));
    int64_t* minv = (int64_t*)malloc((size_t)(n + 1) * sizeof(int64_t));
    bool* used = (bool*)malloc((size_t)(n + 1) * sizeof(bool));

    for (int32_t i = 1; i <= n; ++i) {
        p[0] = i;
        int32_t j0 = 0;
        for (int32_t j = 0; j <= n; ++j) {
            minv[j] = HUNGARIAN_INF;
            used[j] = false;
        }

        do {
            used[j0] = true;
            int32_t i0 = p[j0];
            int64_t delta = HUNGARIAN_INF;
            int32_t j1 = 0;

            for (int32_t j = 1; j <= n; ++j) {
                if (!used[j]) {
                    int64_t cur = matrix[(i0 - 1) * n + (j - 1)] - u[i0] - v[j];
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

            for (int32_t j = 0; j <= n; ++j) {
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

    for (int32_t j = 1; j <= n; ++j) {
        if (p[j] > 0) {
            res.assignment[p[j] - 1] = j - 1;
        }
    }
    res.total_cost = -v[0];

    free(u); free(v); free(p); free(way); free(minv); free(used);
    return res;
}
