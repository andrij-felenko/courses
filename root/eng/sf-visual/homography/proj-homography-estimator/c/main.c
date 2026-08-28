#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

#define HOMOGRAPHY_MAX_POINTS 1024
#define HOMOGRAPHY_EPSILON 1e-12
#define JACOBI_MAX_ITERATIONS 60

typedef struct {
    double x;
    double y;
} HomographyPoint2D;

typedef struct {
    double m[3][3];
} HomographyMat3x3;

typedef struct {
    double max_reprojection_error;
    int max_iterations;
    double confidence;
} HomographyRansacParams;

typedef struct {
    HomographyMat3x3 H;
    int inlier_count;
    bool inliers[HOMOGRAPHY_MAX_POINTS];
    double mean_error;
} HomographyResult;

/* Обчислення визначника матриці 3x3 */
static double mat3_determinant(const HomographyMat3x3* A) {
    return A->m[0][0] * (A->m[1][1] * A->m[2][2] - A->m[1][2] * A->m[2][1]) -
           A->m[0][1] * (A->m[1][0] * A->m[2][2] - A->m[1][2] * A->m[2][0]) +
           A->m[0][2] * (A->m[1][0] * A->m[2][1] - A->m[1][1] * A->m[2][0]);
}

/* Аналітичне обчислення оберненої матриці 3x3 */
static bool mat3_inverse(const HomographyMat3x3* in, HomographyMat3x3* out) {
    double det = mat3_determinant(in);
    if (fabs(det) < HOMOGRAPHY_EPSILON) {
        return false;
    }
    double inv_det = 1.0 / det;

    out->m[0][0] = (in->m[1][1] * in->m[2][2] - in->m[1][2] * in->m[2][1]) * inv_det;
    out->m[0][1] = (in->m[0][2] * in->m[2][1] - in->m[0][1] * in->m[2][2]) * inv_det;
    out->m[0][2] = (in->m[0][1] * in->m[1][2] - in->m[0][2] * in->m[1][1]) * inv_det;

    out->m[1][0] = (in->m[1][2] * in->m[2][0] - in->m[1][0] * in->m[2][2]) * inv_det;
    out->m[1][1] = (in->m[0][0] * in->m[2][2] - in->m[0][2] * in->m[2][0]) * inv_det;
    out->m[1][2] = (in->m[0][2] * in->m[1][0] - in->m[0][0] * in->m[1][2]) * inv_det;

    out->m[2][0] = (in->m[1][0] * in->m[2][1] - in->m[1][1] * in->m[2][0]) * inv_det;
    out->m[2][1] = (in->m[0][1] * in->m[2][0] - in->m[0][0] * in->m[2][1]) * inv_det;
    out->m[2][2] = (in->m[0][0] * in->m[1][1] - in->m[0][1] * in->m[1][0]) * inv_det;

    return true;
}

/* Множення двох матриць 3x3: C = A * B */
static HomographyMat3x3 mat3_multiply(const HomographyMat3x3* a, const HomographyMat3x3* b) {
    HomographyMat3x3 c;
    for (int r = 0; r < 3; ++r) {
        for (int col = 0; col < 3; ++col) {
            c.m[r][col] = a->m[r][0] * b->m[0][col] +
                          a->m[r][1] * b->m[1][col] +
                          a->m[r][2] * b->m[2][col];
        }
    }
    return c;
}

/* Пряме проектування 2D точки через матрицю H */
static bool project_point(const HomographyMat3x3* H, const HomographyPoint2D* in, HomographyPoint2D* out) {
    double z = H->m[2][0] * in->x + H->m[2][1] * in->y + H->m[2][2];
    if (fabs(z) < HOMOGRAPHY_EPSILON) {
        return false;
    }
    double inv_z = 1.0 / z;
    out->x = (H->m[0][0] * in->x + H->m[0][1] * in->y + H->m[0][2]) * inv_z;
    out->y = (H->m[1][0] * in->x + H->m[1][1] * in->y + H->m[1][2]) * inv_z;
    return true;
}

/* Обчислення матриці попередньої нормалізації Гартлі */
static HomographyMat3x3 compute_hartley_normalization(const HomographyPoint2D* pts, int n) {
    HomographyMat3x3 T;
    double sum_x = 0.0, sum_y = 0.0;
    for (int i = 0; i < n; ++i) {
        sum_x += pts[i].x;
        sum_y += pts[i].y;
    }
    double mean_x = sum_x / (double)n;
    double mean_y = sum_y / (double)n;

    double dist_sum = 0.0;
    for (int i = 0; i < n; ++i) {
        double dx = pts[i].x - mean_x;
        double dy = pts[i].y - mean_y;
        dist_sum += sqrt(dx * dx + dy * dy);
    }
    double mean_dist = dist_sum / (double)n;
    double scale = (mean_dist > HOMOGRAPHY_EPSILON) ? (sqrt(2.0) / mean_dist) : 1.0;

    T.m[0][0] = scale; T.m[0][1] = 0.0;   T.m[0][2] = -scale * mean_x;
    T.m[1][0] = 0.0;   T.m[1][1] = scale; T.m[1][2] = -scale * mean_y;
    T.m[2][0] = 0.0;   T.m[2][1] = 0.0;   T.m[2][2] = 1.0;

    return T;
}

/* Ітеративний метод Якобі для знаходження власних векторів симетричної матриці 9x9 */
static void jacobi_eigensolver_9x9(const double A_in[9][9], double V_out[9][9]) {
    double A[9][9];
    for (int i = 0; i < 9; ++i) {
        for (int j = 0; j < 9; ++j) {
            A[i][j] = A_in[i][j];
            V_out[i][j] = (i == j) ? 1.0 : 0.0;
        }
    }

    for (int iter = 0; iter < JACOBI_MAX_ITERATIONS; ++iter) {
        double max_offdiag = 0.0;
        int p = 0, q = 1;
        for (int i = 0; i < 9; ++i) {
            for (int j = i + 1; j < 9; ++j) {
                double val = fabs(A[i][j]);
                if (val > max_offdiag) {
                    max_offdiag = val;
                    p = i;
                    q = j;
                }
            }
        }
        if (max_offdiag < 1e-15) break;

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

/* Оцінка гомографії алгоритмом DLT за нормалізованими точками */
bool homography_estimate_dlt(const HomographyPoint2D* src, const HomographyPoint2D* dst, int n, HomographyMat3x3* out_H) {
    if (n < 4) return false;

    HomographyMat3x3 T_src = compute_hartley_normalization(src, n);
    HomographyMat3x3 T_dst = compute_hartley_normalization(dst, n);

    double M[9][9];
    memset(M, 0, sizeof(M));

    for (int i = 0; i < n; ++i) {
        double x = T_src.m[0][0] * src[i].x + T_src.m[0][2];
        double y = T_src.m[1][1] * src[i].y + T_src.m[1][2];
        double u = T_dst.m[0][0] * dst[i].x + T_dst.m[0][2];
        double v = T_dst.m[1][1] * dst[i].y + T_dst.m[1][2];

        double r1[9] = { 0.0, 0.0, 0.0, -x, -y, -1.0, v * x, v * y, v };
        double r2[9] = { x, y, 1.0, 0.0, 0.0, 0.0, -u * x, -u * y, -u };

        for (int r = 0; r < 9; ++r) {
            for (int c = 0; c < 9; ++c) {
                M[r][c] += r1[r] * r1[c] + r2[r] * r2[c];
            }
        }
    }

    double V[9][9];
    jacobi_eigensolver_9x9(M, V);

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

    HomographyMat3x3 H_norm;
    H_norm.m[0][0] = V[0][min_col]; H_norm.m[0][1] = V[1][min_col]; H_norm.m[0][2] = V[2][min_col];
    H_norm.m[1][0] = V[3][min_col]; H_norm.m[1][1] = V[4][min_col]; H_norm.m[1][2] = V[5][min_col];
    H_norm.m[2][0] = V[6][min_col]; H_norm.m[2][1] = V[7][min_col]; H_norm.m[2][2] = V[8][min_col];

    HomographyMat3x3 inv_T_dst;
    if (!mat3_inverse(&T_dst, &inv_T_dst)) return false;

    HomographyMat3x3 temp = mat3_multiply(&inv_T_dst, &H_norm);
    *out_H = mat3_multiply(&temp, &T_src);

    if (fabs(out_H->m[2][2]) > HOMOGRAPHY_EPSILON) {
        double inv_scale = 1.0 / out_H->m[2][2];
        for (int r = 0; r < 3; ++r) {
            for (int c = 0; c < 3; ++c) {
                out_H->m[r][c] *= inv_scale;
            }
        }
    }
    return true;
}

/* Лінійний конгруентний генератор псевдовипадкових чисел */
static uint32_t lcg_rand(uint32_t* state) {
    *state = (*state * 1664525u + 1013904223u);
    return *state;
}

/* Робастна оцінка гомографії RANSAC */
bool homography_estimate_ransac(
    const HomographyPoint2D* src,
    const HomographyPoint2D* dst,
    int n,
    const HomographyRansacParams* params,
    HomographyResult* result)
{
    if (n < 4 || n > HOMOGRAPHY_MAX_POINTS) return false;

    double thresh_sq = params->max_reprojection_error * params->max_reprojection_error;
    uint32_t rng_state = 0x12345678;

    int best_inlier_count = 0;
    HomographyMat3x3 best_H;
    memset(&best_H, 0, sizeof(best_H));

    int required_iterations = params->max_iterations;

    for (int iter = 0; iter < required_iterations; ++iter) {
        int idx[4];
        for (int i = 0; i < 4; ++i) {
            bool unique;
            do {
                unique = true;
                idx[i] = (int)(lcg_rand(&rng_state) % (uint32_t)n);
                for (int j = 0; j < i; ++j) {
                    if (idx[i] == idx[j]) { unique = false; break; }
                }
            } while (!unique);
        }

        HomographyPoint2D sample_src[4], sample_dst[4];
        for (int i = 0; i < 4; ++i) {
            sample_src[i] = src[idx[i]];
            sample_dst[i] = dst[idx[i]];
        }

        HomographyMat3x3 H_cand;
        if (!homography_estimate_dlt(sample_src, sample_dst, 4, &H_cand)) continue;

        HomographyMat3x3 inv_H_cand;
        if (!mat3_inverse(&H_cand, &inv_H_cand)) continue;

        int current_inliers = 0;
        for (int i = 0; i < n; ++i) {
            HomographyPoint2D proj_dst, proj_src;
            if (!project_point(&H_cand, &src[i], &proj_dst)) continue;
            if (!project_point(&inv_H_cand, &dst[i], &proj_src)) continue;

            double dx1 = dst[i].x - proj_dst.x;
            double dy1 = dst[i].y - proj_dst.y;
            double dx2 = src[i].x - proj_src.x;
            double dy2 = src[i].y - proj_src.y;

            double sym_err = (dx1 * dx1 + dy1 * dy1) + (dx2 * dx2 + dy2 * dy2);
            if (sym_err < thresh_sq) {
                current_inliers++;
            }
        }

        if (current_inliers > best_inlier_count) {
            best_inlier_count = current_inliers;
            best_H = H_cand;

            double w = (double)current_inliers / (double)n;
            double w4 = w * w * w * w;
            if (w4 > 1e-6) {
                double num = log(1.0 - params->confidence);
                double den = log(1.0 - w4);
                int k = (int)(num / den) + 1;
                if (k < required_iterations) {
                    required_iterations = k;
                }
            }
        }
    }

    if (best_inlier_count < 4) return false;

    HomographyMat3x3 inv_best_H;
    mat3_inverse(&best_H, &inv_best_H);

    HomographyPoint2D inlier_src[HOMOGRAPHY_MAX_POINTS];
    HomographyPoint2D inlier_dst[HOMOGRAPHY_MAX_POINTS];
    int count = 0;
    double total_err = 0.0;

    memset(result->inliers, 0, sizeof(result->inliers));

    for (int i = 0; i < n; ++i) {
        HomographyPoint2D proj_dst, proj_src;
        if (!project_point(&best_H, &src[i], &proj_dst) ||
            !project_point(&inv_best_H, &dst[i], &proj_src)) {
            continue;
        }

        double dx1 = dst[i].x - proj_dst.x;
        double dy1 = dst[i].y - proj_dst.y;
        double dx2 = src[i].x - proj_src.x;
        double dy2 = src[i].y - proj_src.y;
        double sym_err = (dx1 * dx1 + dy1 * dy1) + (dx2 * dx2 + dy2 * dy2);

        if (sym_err < thresh_sq) {
            result->inliers[i] = true;
            inlier_src[count] = src[i];
            inlier_dst[count] = dst[i];
            total_err += sqrt(sym_err * 0.5);
            count++;
        }
    }

    result->inlier_count = count;
    result->mean_error = (count > 0) ? (total_err / count) : 0.0;

    return homography_estimate_dlt(inlier_src, inlier_dst, count, &result->H);
}

/* Зворотне перспективне відображення (IPM) з білінійною інтерполяцією */
void homography_warp_perspective_bilinear(
    const uint8_t* src_image, int src_w, int src_h,
    uint8_t* dst_image, int dst_w, int dst_h,
    const HomographyMat3x3* H_dst_to_src)
{
    for (int dst_y = 0; dst_y < dst_h; ++dst_y) {
        for (int dst_x = 0; dst_x < dst_w; ++dst_x) {
            HomographyPoint2D pt_dst = { (double)dst_x, (double)dst_y };
            HomographyPoint2D pt_src;

            if (!project_point(H_dst_to_src, &pt_dst, &pt_src)) {
                dst_image[dst_y * dst_w + dst_x] = 0;
                continue;
            }

            if (pt_src.x < 0.0 || pt_src.x >= (double)(src_w - 1) ||
                pt_src.y < 0.0 || pt_src.y >= (double)(src_h - 1)) {
                dst_image[dst_y * dst_w + dst_x] = 0;
                continue;
            }

            int x0 = (int)floor(pt_src.x);
            int y0 = (int)floor(pt_src.y);
            int x1 = x0 + 1;
            int y1 = y0 + 1;

            double wx1 = pt_src.x - (double)x0;
            double wy1 = pt_src.y - (double)y0;
            double wx0 = 1.0 - wx1;
            double wy0 = 1.0 - wy1;

            uint8_t p00 = src_image[y0 * src_w + x0];
            uint8_t p01 = src_image[y0 * src_w + x1];
            uint8_t p10 = src_image[y1 * src_w + x0];
            uint8_t p11 = src_image[y1 * src_w + x1];

            double val = wx0 * wy0 * p00 +
                         wx1 * wy0 * p01 +
                         wx0 * wy1 * p10 +
                         wx1 * wy1 * p11;

            dst_image[dst_y * dst_w + dst_x] = (uint8_t)(val + 0.5);
        }
    }
}
