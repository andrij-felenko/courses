/*
 * kin_solver.c - Чисельний кінематичний розв'язувач багатоланкових систем на C99.
 * Повна реалізація прямої кінематики, геометричного Якобіана, SVD-аналізу та DLS.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define MAX_JOINTS 12
#define TASK_DIM 6
#define SVD_MAX_ITER 100
#define EPS_TOL 1e-12

typedef enum {
    JOINT_REVOLUTE,
    JOINT_PRISMATIC
} JointType;

typedef struct {
    double x, y, z;
} Vec3;

typedef struct {
    double m[3][3];
} Mat3;

typedef struct {
    double m[4][4];
} Mat4;

typedef struct {
    JointType type;
    Vec3 axis;
    Mat4 offset;
    double q_min;
    double q_max;
    double q_rest;
} Joint;

typedef struct {
    int num_joints;
    Joint joints[MAX_JOINTS];
} KinematicChain;

typedef struct {
    double U[TASK_DIM][TASK_DIM];
    double S[TASK_DIM];
    double V[MAX_JOINTS][MAX_JOINTS];
    int rank;
    double manipulability;
    double condition_number;
} SvdAnalysis;

/* --- Векторна та матрична алгебра --- */

static inline Vec3 vec3_create(double x, double y, double z) {
    Vec3 v = {x, y, z};
    return v;
}

static inline Vec3 vec3_add(Vec3 a, Vec3 b) {
    return vec3_create(a.x + b.x, a.y + b.y, a.z + b.z);
}

static inline Vec3 vec3_sub(Vec3 a, Vec3 b) {
    return vec3_create(a.x - b.x, a.y - b.y, a.z - b.z);
}

static inline Vec3 vec3_scale(Vec3 v, double s) {
    return vec3_create(v.x * s, v.y * s, v.z * s);
}

static inline double vec3_dot(Vec3 a, Vec3 b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return vec3_create(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    );
}

static inline double vec3_norm(Vec3 v) {
    return sqrt(vec3_dot(v, v));
}

static inline Mat4 mat4_identity(void) {
    Mat4 res;
    memset(&res, 0, sizeof(Mat4));
    for (int i = 0; i < 4; ++i) res.m[i][i] = 1.0;
    return res;
}

static Mat4 mat4_multiply(const Mat4* a, const Mat4* b) {
    Mat4 res;
    for (int r = 0; r < 4; ++r) {
        for (int c = 0; c < 4; ++c) {
            double sum = 0.0;
            for (int k = 0; k < 4; ++k) {
                sum += a->m[r][k] * b->m[k][c];
            }
            res.m[r][c] = sum;
        }
    }
    return res;
}

static Vec3 mat4_transform_point(const Mat4* m, Vec3 p) {
    return vec3_create(
        m->m[0][0] * p.x + m->m[0][1] * p.y + m->m[0][2] * p.z + m->m[0][3],
        m->m[1][0] * p.x + m->m[1][1] * p.y + m->m[1][2] * p.z + m->m[1][3],
        m->m[2][0] * p.x + m->m[2][1] * p.y + m->m[2][2] * p.z + m->m[2][3]
    );
}

static Vec3 mat4_transform_vector(const Mat4* m, Vec3 v) {
    return vec3_create(
        m->m[0][0] * v.x + m->m[0][1] * v.y + m->m[0][2] * v.z,
        m->m[1][0] * v.x + m->m[1][1] * v.y + m->m[1][2] * v.z,
        m->m[2][0] * v.x + m->m[2][1] * v.y + m->m[2][2] * v.z
    );
}

static Mat4 mat4_joint_transform(JointType type, Vec3 axis, double q) {
    Mat4 res = mat4_identity();
    if (type == JOINT_REVOLUTE) {
        double c = cos(q);
        double s = sin(q);
        double v = 1.0 - c;
        double kx = axis.x, ky = axis.y, kz = axis.z;

        res.m[0][0] = kx * kx * v + c;
        res.m[0][1] = kx * ky * v - kz * s;
        res.m[0][2] = kx * kz * v + ky * s;

        res.m[1][0] = kx * ky * v + kz * s;
        res.m[1][1] = ky * ky * v + c;
        res.m[1][2] = ky * kz * v - kx * s;

        res.m[2][0] = kx * kz * v - ky * s;
        res.m[2][1] = ky * kz * v + kx * s;
        res.m[2][2] = kz * kz * v + c;
    } else if (type == JOINT_PRISMATIC) {
        res.m[0][3] = axis.x * q;
        res.m[1][3] = axis.y * q;
        res.m[2][3] = axis.z * q;
    }
    return res;
}

/* --- Пряма кінематика та геометричний Якобіан --- */

void forward_kinematics_and_jacobian(
    const KinematicChain* chain,
    const double* q,
    Mat4* out_T_end,
    double J[TASK_DIM][MAX_JOINTS])
{
    int n = chain->num_joints;
    Mat4 T_curr = mat4_identity();
    Mat4 T_frames[MAX_JOINTS + 1];
    T_frames[0] = T_curr;

    Vec3 z_axes[MAX_JOINTS];
    Vec3 p_origins[MAX_JOINTS];

    for (int i = 0; i < n; ++i) {
        Mat4 T_j = mat4_joint_transform(chain->joints[i].type, chain->joints[i].axis, q[i]);
        Mat4 T_step = mat4_multiply(&chain->joints[i].offset, &T_j);
        T_curr = mat4_multiply(&T_curr, &T_step);
        T_frames[i + 1] = T_curr;

        z_axes[i] = mat4_transform_vector(&T_frames[i], chain->joints[i].axis);
        p_origins[i] = mat4_transform_point(&T_frames[i], vec3_create(0, 0, 0));
    }

    *out_T_end = T_curr;
    Vec3 p_end = mat4_transform_point(&T_curr, vec3_create(0, 0, 0));

    for (int i = 0; i < n; ++i) {
        if (chain->joints[i].type == JOINT_REVOLUTE) {
            Vec3 rot_axis = z_axes[i];
            Vec3 r = vec3_sub(p_end, p_origins[i]);
            Vec3 lin_vel = vec3_cross(rot_axis, r);

            J[0][i] = rot_axis.x;
            J[1][i] = rot_axis.y;
            J[2][i] = rot_axis.z;
            J[3][i] = lin_vel.x;
            J[4][i] = lin_vel.y;
            J[5][i] = lin_vel.z;
        } else {
            Vec3 trans_axis = z_axes[i];
            J[0][i] = 0.0;
            J[1][i] = 0.0;
            J[2][i] = 0.0;
            J[3][i] = trans_axis.x;
            J[4][i] = trans_axis.y;
            J[5][i] = trans_axis.z;
        }
    }
}

/* --- Двосторонній SVD Якобі --- */

static void svd_decompose_jacobian(
    int m, int n,
    const double A[TASK_DIM][MAX_JOINTS],
    SvdAnalysis* out_svd)
{
    double V[MAX_JOINTS][MAX_JOINTS];
    double work_A[TASK_DIM][MAX_JOINTS];
    memcpy(work_A, A, sizeof(double) * TASK_DIM * MAX_JOINTS);

    memset(V, 0, sizeof(V));
    for (int i = 0; i < n; ++i) V[i][i] = 1.0;

    memset(out_svd->U, 0, sizeof(out_svd->U));
    for (int i = 0; i < m; ++i) out_svd->U[i][i] = 1.0;

    for (int iter = 0; iter < SVD_MAX_ITER; ++iter) {
        double max_err = 0.0;
        for (int i = 0; i < n - 1; ++i) {
            for (int j = i + 1; j < n; ++j) {
                double a = 0.0, b = 0.0, c = 0.0;
                for (int k = 0; k < m; ++k) {
                    a += work_A[k][i] * work_A[k][i];
                    b += work_A[k][j] * work_A[k][j];
                    c += work_A[k][i] * work_A[k][j];
                }
                if (fabs(c) > max_err) max_err = fabs(c);

                if (fabs(c) > 1e-15) {
                    double zeta = (b - a) / (2.0 * c);
                    double t = (zeta >= 0.0 ? 1.0 : -1.0) / (fabs(zeta) + sqrt(1.0 + zeta * zeta));
                    double cos_v = 1.0 / sqrt(1.0 + t * t);
                    double sin_v = t * cos_v;

                    for (int k = 0; k < m; ++k) {
                        double temp_i = work_A[k][i];
                        double temp_j = work_A[k][j];
                        work_A[k][i] = cos_v * temp_i - sin_v * temp_j;
                        work_A[k][j] = sin_v * temp_i + cos_v * temp_j;
                    }

                    for (int k = 0; k < n; ++k) {
                        double temp_i = V[k][i];
                        double temp_j = V[k][j];
                        V[k][i] = cos_v * temp_i - sin_v * temp_j;
                        V[k][j] = sin_v * temp_i + cos_v * temp_j;
                    }
                }
            }
        }
        if (max_err < 1e-13) break;
    }

    int min_dim = m < n ? m : n;
    for (int i = 0; i < min_dim; ++i) {
        double norm = 0.0;
        for (int k = 0; k < m; ++k) {
            norm += work_A[k][i] * work_A[k][i];
        }
        double s = sqrt(norm);
        out_svd->S[i] = s;
        if (s > 1e-14) {
            for (int k = 0; k < m; ++k) out_svd->U[k][i] = work_A[k][i] / s;
        } else {
            for (int k = 0; k < m; ++k) out_svd->U[k][i] = 0.0;
        }
    }

    for (int i = 0; i < min_dim - 1; ++i) {
        for (int j = i + 1; j < min_dim; ++j) {
            if (out_svd->S[j] > out_svd->S[i]) {
                double temp_s = out_svd->S[i];
                out_svd->S[i] = out_svd->S[j];
                out_svd->S[j] = temp_s;

                for (int k = 0; k < m; ++k) {
                    double temp_u = out_svd->U[k][i];
                    out_svd->U[k][i] = out_svd->U[k][j];
                    out_svd->U[k][j] = temp_u;
                }
                for (int k = 0; k < n; ++k) {
                    double temp_v = V[k][i];
                    V[k][i] = V[k][j];
                    V[k][j] = temp_v;
                }
            }
        }
    }

    memcpy(out_svd->V, V, sizeof(V));

    double s_max = out_svd->S[0];
    double s_min = out_svd->S[min_dim - 1];
    double tol = (double)(m > n ? m : n) * s_max * 2.22e-16;
    if (tol < 1e-12) tol = 1e-12;

    int rk = 0;
    double manip_prod = 1.0;
    for (int i = 0; i < min_dim; ++i) {
        if (out_svd->S[i] > tol) {
            rk++;
            manip_prod *= out_svd->S[i];
        }
    }
    out_svd->rank = rk;
    out_svd->manipulability = (rk == min_dim) ? manip_prod : 0.0;
    out_svd->condition_number = (s_min > 1e-12) ? (s_max / s_min) : 1e12;
}

/* --- Регуляризоване обернене кінематичне перетворення DLS --- */

void solve_ik_dls(
    const KinematicChain* chain,
    const double J[TASK_DIM][MAX_JOINTS],
    const double twist_cmd[TASK_DIM],
    const double* q_curr,
    double lambda_max,
    double w_threshold,
    const SvdAnalysis* svd,
    double* out_q_dot)
{
    int n = chain->num_joints;
    int m = TASK_DIM;

    double lambda = 0.0;
    if (svd->manipulability < w_threshold) {
        double ratio = 1.0 - (svd->manipulability / w_threshold);
        lambda = lambda_max * ratio * ratio;
    }
    double lambda_sq = lambda * lambda;

    double A[TASK_DIM][TASK_DIM];
    memset(A, 0, sizeof(A));
    for (int r = 0; r < m; ++r) {
        for (int c = 0; c < m; ++c) {
            double sum = 0.0;
            for (int k = 0; k < n; ++k) {
                sum += J[r][k] * J[c][k];
            }
            A[r][c] = sum;
        }
        A[r][r] += lambda_sq;
    }

    double f[TASK_DIM];
    double aug[TASK_DIM][TASK_DIM + 1];
    for (int r = 0; r < m; ++r) {
        for (int c = 0; c < m; ++c) aug[r][c] = A[r][c];
        aug[r][m] = twist_cmd[r];
    }

    for (int k = 0; k < m; ++k) {
        int max_row = k;
        double max_val = fabs(aug[k][k]);
        for (int r = k + 1; r < m; ++r) {
            if (fabs(aug[r][k]) > max_val) {
                max_val = fabs(aug[r][k]);
                max_row = r;
            }
        }
        if (max_row != k) {
            for (int c = k; c <= m; ++c) {
                double temp = aug[k][c];
                aug[k][c] = aug[max_row][c];
                aug[max_row][c] = temp;
            }
        }
        double pivot = aug[k][k];
        if (fabs(pivot) < 1e-14) pivot = (pivot >= 0.0 ? 1e-14 : -1e-14);

        for (int r = k + 1; r < m; ++r) {
            double factor = aug[r][k] / pivot;
            for (int c = k; c <= m; ++c) {
                aug[r][c] -= factor * aug[k][c];
            }
        }
    }

    for (int r = m - 1; r >= 0; --r) {
        double sum = aug[r][m];
        for (int c = r + 1; c < m; ++c) {
            sum -= aug[r][c] * f[c];
        }
        f[r] = sum / aug[r][r];
    }

    double q_dot_main[MAX_JOINTS];
    for (int i = 0; i < n; ++i) {
        double sum = 0.0;
        for (int r = 0; r < m; ++r) {
            sum += J[r][i] * f[r];
        }
        q_dot_main[i] = sum;
    }

    double q_null_desired[MAX_JOINTS];
    double k_null = 2.0;
    for (int i = 0; i < n; ++i) {
        q_null_desired[i] = -k_null * (q_curr[i] - chain->joints[i].q_rest);
    }

    double J_qnull[TASK_DIM];
    for (int r = 0; r < m; ++r) {
        double sum = 0.0;
        for (int c = 0; c < n; ++c) {
            sum += J[r][c] * q_null_desired[c];
        }
        J_qnull[r] = sum;
    }

    double f_null[TASK_DIM];
    for (int r = 0; r < m; ++r) {
        for (int c = 0; c < m; ++c) aug[r][c] = A[r][c];
        aug[r][m] = J_qnull[r];
    }
    for (int k = 0; k < m; ++k) {
        double pivot = aug[k][k];
        if (fabs(pivot) < 1e-14) pivot = (pivot >= 0.0 ? 1e-14 : -1e-14);
        for (int r = k + 1; r < m; ++r) {
            double factor = aug[r][k] / pivot;
            for (int c = k; c <= m; ++c) aug[r][c] -= factor * aug[k][c];
        }
    }
    for (int r = m - 1; r >= 0; --r) {
        double sum = aug[r][m];
        for (int c = r + 1; c < m; ++c) sum -= aug[r][c] * f_null[c];
        f_null[r] = sum / aug[r][r];
    }

    for (int i = 0; i < n; ++i) {
        double Jt_fnull = 0.0;
        for (int r = 0; r < m; ++r) {
            Jt_fnull += J[r][i] * f_null[r];
        }
        out_q_dot[i] = q_dot_main[i] + (q_null_desired[i] - Jt_fnull);
    }
}

int main(void) {
    KinematicChain robot;
    robot.num_joints = 6;

    for (int i = 0; i < 6; ++i) {
        robot.joints[i].type = JOINT_REVOLUTE;
        robot.joints[i].axis = vec3_create(0, 0, 1);
        robot.joints[i].q_min = -M_PI;
        robot.joints[i].q_max = M_PI;
        robot.joints[i].q_rest = 0.0;
        robot.joints[i].offset = mat4_identity();
    }

    robot.joints[0].offset.m[2][3] = 0.3;
    robot.joints[1].axis = vec3_create(0, 1, 0);
    robot.joints[2].axis = vec3_create(0, 1, 0);
    robot.joints[2].offset.m[2][3] = 0.4;
    robot.joints[3].axis = vec3_create(1, 0, 0);
    robot.joints[3].offset.m[2][3] = 0.4;
    robot.joints[4].axis = vec3_create(0, 1, 0);
    robot.joints[5].axis = vec3_create(0, 0, 1);
    robot.joints[5].offset.m[2][3] = 0.15;

    double q_normal[6] = {0.2, 0.5, -0.8, 0.1, 0.4, -0.2};
    double q_singular[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.0};

    Mat4 T_end;
    double J[TASK_DIM][MAX_JOINTS];
    SvdAnalysis svd;

    printf("=== Демонстрація кінематичного розв'язувача (C99) ===\n\n");

    forward_kinematics_and_jacobian(&robot, q_normal, &T_end, J);
    svd_decompose_jacobian(TASK_DIM, robot.num_joints, J, &svd);

    printf("1. Звичайна конфігурація:\n");
    printf("   Положення: (%.3f, %.3f, %.3f) м\n", T_end.m[0][3], T_end.m[1][3], T_end.m[2][3]);
    printf("   Сингулярні числа: ");
    for (int i = 0; i < 6; ++i) printf("%.3f ", svd.S[i]);
    printf("\n   Ранг: %d / 6, Маніпулятивність: %.6e, kappa(J): %.2f\n\n",
           svd.rank, svd.manipulability, svd.condition_number);

    forward_kinematics_and_jacobian(&robot, q_singular, &T_end, J);
    svd_decompose_jacobian(TASK_DIM, robot.num_joints, J, &svd);

    printf("2. Сингулярна конфігурація:\n");
    printf("   Положення: (%.3f, %.3f, %.3f) м\n", T_end.m[0][3], T_end.m[1][3], T_end.m[2][3]);
    printf("   Сингулярні числа: ");
    for (int i = 0; i < 6; ++i) printf("%.3e ", svd.S[i]);
    printf("\n   Ранг: %d / 6, Маніпулятивність: %.6e, kappa(J): %.2e\n\n",
           svd.rank, svd.manipulability, svd.condition_number);

    double twist_target[6] = {0.0, 0.0, 0.0, 0.0, 0.0, 0.2};
    double q_dot[MAX_JOINTS];
    solve_ik_dls(&robot, J, twist_target, q_singular, 0.1, 0.05, &svd, q_dot);

    printf("3. Швидкості шарнірів DLS (рад/с): ");
    for (int i = 0; i < 6; ++i) printf("%.4f ", q_dot[i]);
    printf("\n");

    return 0;
}
