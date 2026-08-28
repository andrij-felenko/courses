#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>
#include <stdbool.h>

typedef struct {
    double x;
    double y;
    double z;
    double t;
} Point3D;

typedef struct {
    double xte_rms;
    double xte_max;
    double frechet_dist;
    double dtw_normalized;
    bool passed;
} RegressionReport;

/* Евклідова відстань у 3D просторі */
static inline double euclidean_dist(Point3D a, Point3D b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    double dz = a.z - b.z;
    return sqrt(dx * dx + dy * dy + dz * dz);
}

/* Розрахунок метрик Cross-Track Error відносно планового сегмента AB */
void compute_xte_statistics(const Point3D* test_track, size_t n_points,
                            Point3D seg_a, Point3D seg_b,
                            double* out_rms, double* out_max) {
    if (n_points == 0) {
        *out_rms = 0.0;
        *out_max = 0.0;
        return;
    }

    double vx = seg_b.x - seg_a.x;
    double vy = seg_b.y - seg_a.y;
    double vz = seg_b.z - seg_a.z;
    double seg_len_sq = vx * vx + vy * vy + vz * vz;

    double sum_sq_err = 0.0;
    double max_err = 0.0;

    for (size_t i = 0; i < n_points; ++i) {
        Point3D p = test_track[i];
        double wx = p.x - seg_a.x;
        double wy = p.y - seg_a.y;
        double wz = p.z - seg_a.z;

        double t = (seg_len_sq > 1e-9) ? (wx * vx + wy * vy + wz * vz) / seg_len_sq : 0.0;
        if (t < 0.0) t = 0.0;
        if (t > 1.0) t = 1.0;

        Point3D proj = {
            .x = seg_a.x + t * vx,
            .y = seg_a.y + t * vy,
            .z = seg_a.z + t * vz,
            .t = p.t
        };

        double err = euclidean_dist(p, proj);
        sum_sq_err += err * err;
        if (err > max_err) {
            max_err = err;
        }
    }

    *out_rms = sqrt(sum_sq_err / (double)n_points);
    *out_max = max_err;
}

/* Дискретна відстань Фреше з оптимізацією пам'яті O(M) */
double compute_discrete_frechet(const Point3D* p, size_t n,
                                const Point3D* q, size_t m) {
    if (n == 0 || m == 0) return DBL_MAX;

    double* prev_row = (double*)malloc(m * sizeof(double));
    double* curr_row = (double*)malloc(m * sizeof(double));
    if (!prev_row || !curr_row) {
        free(prev_row);
        free(curr_row);
        return DBL_MAX;
    }

    /* Базовий стан L(0, 0) */
    prev_row[0] = euclidean_dist(p[0], q[0]);

    /* Ініціалізація першого рядка L(0, j) */
    for (size_t j = 1; j < m; ++j) {
        double d = euclidean_dist(p[0], q[j]);
        prev_row[j] = (d > prev_row[j - 1]) ? d : prev_row[j - 1];
    }

    /* Заповнення матриці рядок за рядком */
    for (size_t i = 1; i < n; ++i) {
        double d0 = euclidean_dist(p[i], q[0]);
        curr_row[0] = (d0 > prev_row[0]) ? d0 : prev_row[0];

        for (size_t j = 1; j < m; ++j) {
            double d = euclidean_dist(p[i], q[j]);
            double min_prev = prev_row[j - 1];
            if (prev_row[j] < min_prev) min_prev = prev_row[j];
            if (curr_row[j - 1] < min_prev) min_prev = curr_row[j - 1];

            curr_row[j] = (d > min_prev) ? d : min_prev;
        }

        /* Заміна рядків */
        double* tmp = prev_row;
        prev_row = curr_row;
        curr_row = tmp;
    }

    double result = prev_row[m - 1];
    free(prev_row);
    free(curr_row);
    return result;
}

/* DTW з вікном Сакое-Чіба (радіус window_r) */
double compute_dtw_constrained(const Point3D* p, size_t n,
                               const Point3D* q, size_t m,
                               size_t window_r) {
    if (n == 0 || m == 0) return DBL_MAX;

    double* dtw_matrix = (double*)malloc(n * m * sizeof(double));
    if (!dtw_matrix) return DBL_MAX;

    for (size_t i = 0; i < n * m; ++i) {
        dtw_matrix[i] = DBL_MAX;
    }

    #define DTW(i, j) dtw_matrix[(i) * m + (j)]

    DTW(0, 0) = euclidean_dist(p[0], q[0]);

    for (size_t i = 0; i < n; ++i) {
        size_t j_start = (i > window_r) ? (i - window_r) : 0;
        size_t j_end = (i + window_r + 1 < m) ? (i + window_r + 1) : m;

        for (size_t j = j_start; j < j_end; ++j) {
            if (i == 0 && j == 0) continue;

            double cost = euclidean_dist(p[i], q[j]);
            double min_prev = DBL_MAX;

            if (i > 0 && DTW(i - 1, j) < min_prev) min_prev = DTW(i - 1, j);
            if (j > 0 && DTW(i, j - 1) < min_prev) min_prev = DTW(i, j - 1);
            if (i > 0 && j > 0 && DTW(i - 1, j - 1) < min_prev) min_prev = DTW(i - 1, j - 1);

            if (min_prev < DBL_MAX) {
                DTW(i, j) = cost + min_prev;
            }
        }
    }

    double total_cost = DTW(n - 1, m - 1);
    free(dtw_matrix);
    #undef DTW

    return (total_cost < DBL_MAX) ? (total_cost / (double)(n + m)) : DBL_MAX;
}
