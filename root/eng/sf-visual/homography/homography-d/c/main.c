#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double x;
    double y;
} Point2D;

typedef struct {
    double m[3][3];
} Mat3x3;

/* Обчислення матриці нормалізації Гартлі */
static Mat3x3 compute_hartley_transform(const Point2D* pts, int n) {
    Mat3x3 T;
    double sum_x = 0.0, sum_y = 0.0;
    for (int i = 0; i < n; ++i) {
        sum_x += pts[i].x;
        sum_y += pts[i].y;
    }
    double mean_x = sum_x / n;
    double mean_y = sum_y / n;

    double dist_sum = 0.0;
    for (int i = 0; i < n; ++i) {
        double dx = pts[i].x - mean_x;
        double dy = pts[i].y - mean_y;
        dist_sum += sqrt(dx * dx + dy * dy);
    }
    double mean_dist = dist_sum / n;
    double scale = (mean_dist > 1e-12) ? (sqrt(2.0) / mean_dist) : 1.0;

    T.m[0][0] = scale; T.m[0][1] = 0.0;   T.m[0][2] = -scale * mean_x;
    T.m[1][0] = 0.0;   T.m[1][1] = scale; T.m[1][2] = -scale * mean_y;
    T.m[2][0] = 0.0;   T.m[2][1] = 0.0;   T.m[2][2] = 1.0;

    return T;
}

/* Множення двох матриць 3x3: C = A * B */
static Mat3x3 mat3_mul(const Mat3x3* a, const Mat3x3* b) {
    Mat3x3 c;
    for (int r = 0; r < 3; ++r) {
        for (int col = 0; col < 3; ++col) {
            c.m[r][col] = a->m[r][0] * b->m[0][col] +
                          a->m[r][1] * b->m[1][col] +
                          a->m[r][2] * b->m[2][col];
        }
    }
    return c;
}

/* Аналітичне обернення матриці нормалізації T */
static Mat3x3 hartley_inverse(const Mat3x3* T) {
    Mat3x3 inv;
    double scale = T->m[0][0];
    double mean_x = -T->m[0][2] / scale;
    double mean_y = -T->m[1][2] / scale;

    inv.m[0][0] = 1.0 / scale; inv.m[0][1] = 0.0;         inv.m[0][2] = mean_x;
    inv.m[1][0] = 0.0;         inv.m[1][1] = 1.0 / scale; inv.m[1][2] = mean_y;
    inv.m[2][0] = 0.0;         inv.m[2][1] = 0.0;         inv.m[2][2] = 1.0;

    return inv;
}

/* Ітеративний метод Якобі для знаходження власних векторів симетричної матриці 9x9 */
static void jacobi_eigensystem_9x9(const double A_in[9][9], double V_out[9][9]) {
    double A[9][9];
    for (int i = 0; i < 9; ++i) {
        for (int j = 0; j < 9; ++j) {
            A[i][j] = A_in[i][j];
            V_out[i][j] = (i == j) ? 1.0 : 0.0;
        }
    }

    const int max_iter = 50;
    for (int iter = 0; iter < max_iter; ++iter) {
        double max_off = 0.0;
        int p = 0, q = 1;
        for (int i = 0; i < 9; ++i) {
            for (int j = i + 1; j < 9; ++j) {
                double val = fabs(A[i][j]);
                if (val > max_off) {
                    max_off = val;
                    p = i;
                    q = j;
                }
            }
        }
        if (max_off < 1e-15) break;

        double theta = 0.5 * (A[q][q] - A[p][p]) / A[p][q];
        double t = 1.0 / (fabs(theta) + sqrt(theta * theta + 1.0));
        if (theta < 0.0) t = -t;

        double c = 1.0 / sqrt(t * t + 1.0);
        double s = t * c;
        double tau = s / (1.0 + c);

        double app = A[p][p];
        double aqq = A[q][q];
        double apq = A[p][q];

        A[p][p] = app - t * apq;
        A[q][q] = aqq + t * apq;
        A[p][q] = 0.0;
        A[q][p] = 0.0;

        for (int k = 0; k < 9; ++k) {
            if (k != p && k != q) {
                double akp = A[k][p];
                double akq = A[k][q];
                A[k][p] = akp - s * (akq + tau * akp);
                A[p][k] = A[k][p];
                A[k][q] = akq + s * (akp - tau * akq);
                A[q][k] = A[k][q];
            }
        }

        for (int k = 0; k < 9; ++k) {
            double vkp = V_out[k][p];
            double vkq = V_out[k][q];
            V_out[k][p] = vkp - s * (vkq + tau * vkp);
            V_out[k][q] = vkq + s * (vkp - tau * vkq);
        }
    }
}

/* Обчислення матриці гомографії через нормалізований DLT */
bool estimate_homography_dlt(const Point2D* src, const Point2D* dst, int n, Mat3x3* out_H) {
    if (n < 4) return false;

    Mat3x3 T_src = compute_hartley_transform(src, n);
    Mat3x3 T_dst = compute_hartley_transform(dst, n);

    /* Формування нормальних рівнянь M = A^T * A (розмір 9x9) */
    double M[9][9] = {0};

    for (int i = 0; i < n; ++i) {
        /* Нормалізація точок */
        double x = T_src.m[0][0] * src[i].x + T_src.m[0][2];
        double y = T_src.m[1][1] * src[i].y + T_src.m[1][2];
        double u = T_dst.m[0][0] * dst[i].x + T_dst.m[0][2];
        double v = T_dst.m[1][1] * dst[i].y + T_dst.m[1][2];

        /* Рядок 1: [0, 0, 0, -x, -y, -1, v*x, v*y, v] */
        double r1[9] = { 0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v };
        /* Рядок 2: [x, y, 1, 0, 0, 0, -u*x, -u*y, -u] */
        double r2[9] = { x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y, -u };

        for (int r = 0; r < 9; ++r) {
            for (int c = 0; c < 9; ++c) {
                M[r][c] += r1[r] * r1[c] + r2[r] * r2[c];
            }
        }
    }

    double V[9][9];
    jacobi_eigensystem_9x9(M, V);

    /* Пошук стовпця з мінімальним діагональним значенням (найменшим власним числом) */
    int min_col = 0;
    double min_eval = 1e30;
    for (int col = 0; col < 9; ++col) {
        double eval = 0.0;
        for (int r = 0; r < 9; ++r) {
            double sum = 0.0;
            for (int k = 0; k < 9; ++k) sum += M[r][k] * V[k][col];
            eval += V[r][col] * sum;
        }
        if (eval < min_eval) {
            min_eval = eval;
            min_col = col;
        }
    }

    Mat3x3 H_norm;
    H_norm.m[0][0] = V[0][min_col]; H_norm.m[0][1] = V[1][min_col]; H_norm.m[0][2] = V[2][min_col];
    H_norm.m[1][0] = V[3][min_col]; H_norm.m[1][1] = V[4][min_col]; H_norm.m[1][2] = V[5][min_col];
    H_norm.m[2][0] = V[6][min_col]; H_norm.m[2][1] = V[7][min_col]; H_norm.m[2][2] = V[8][min_col];

    /* Денормалізація: H = inv(T_dst) * H_norm * T_src */
    Mat3x3 inv_T_dst = hartley_inverse(&T_dst);
    Mat3x3 temp = mat3_mul(&inv_T_dst, &H_norm);
    *out_H = mat3_mul(&temp, &T_src);

    /* Нормалізація елемента h33 до 1.0 */
    if (fabs(out_H->m[2][2]) > 1e-12) {
        double inv_h33 = 1.0 / out_H->m[2][2];
        for (int r = 0; r < 3; ++r) {
            for (int c = 0; c < 3; ++c) {
                out_H->m[r][c] *= inv_h33;
            }
        }
    }

    return true;
}
