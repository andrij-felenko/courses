/*
 * dof_kinematics.c - Обчислення кінематики та Якобіана 6-DoF маніпулятора на C99.
 */

#include <stdio.h>
#include <math.h>
#include <string.h>

#define DOF 6

typedef struct {
    double m[4][4];
} Mat4;

typedef struct {
    double x, y, z;
} Vec3;

static inline Vec3 vec3_create(double x, double y, double z) {
    Vec3 v = {x, y, z};
    return v;
}

static inline Vec3 vec3_cross(Vec3 a, Vec3 b) {
    return vec3_create(
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    );
}

static inline Mat4 mat4_identity(void) {
    Mat4 res;
    memset(&res, 0, sizeof(Mat4));
    for (int i = 0; i < 4; ++i) res.m[i][i] = 1.0;
    return res;
}

static Mat4 mat4_mul(const Mat4* a, const Mat4* b) {
    Mat4 res;
    for (int r = 0; r < 4; ++r) {
        for (int c = 0; c < 4; ++c) {
            double s = 0.0;
            for (int k = 0; k < 4; ++k) s += a->m[r][k] * b->m[k][c];
            res.m[r][c] = s;
        }
    }
    return res;
}

/* Формування матриці перетворення за параметрами Денавіта-Хартенберга (DH) */
static Mat4 dh_matrix(double alpha, double a, double d, double theta) {
    Mat4 res = mat4_identity();
    double ct = cos(theta), st = sin(theta);
    double ca = cos(alpha), sa = sin(alpha);

    res.m[0][0] = ct;       res.m[0][1] = -st * ca;  res.m[0][2] = st * sa;   res.m[0][3] = a * ct;
    res.m[1][0] = st;       res.m[1][1] = ct * ca;   res.m[1][2] = -ct * sa;  res.m[1][3] = a * st;
    res.m[2][0] = 0.0;      res.m[2][1] = sa;        res.m[2][2] = ca;        res.m[2][3] = d;
    res.m[3][0] = 0.0;      res.m[3][1] = 0.0;       res.m[3][2] = 0.0;       res.m[3][3] = 1.0;

    return res;
}

void compute_fk_and_jacobian(
    const double q[DOF],
    Mat4* out_T_end,
    double J[6][DOF])
{
    /* Параметри DH для моделі маніпулятора (PUMA-подібна геометрія) */
    const double alpha[DOF] = { M_PI / 2.0, 0.0, M_PI / 2.0, -M_PI / 2.0, M_PI / 2.0, 0.0 };
    const double a[DOF]     = { 0.0, 0.432, 0.020, 0.0, 0.0, 0.0 };
    const double d[DOF]     = { 0.150, 0.0, 0.0, 0.432, 0.0, 0.050 };

    Mat4 T[DOF + 1];
    T[0] = mat4_identity();

    Vec3 z_axes[DOF];
    Vec3 p_origins[DOF];

    for (int i = 0; i < DOF; ++i) {
        Mat4 A_i = dh_matrix(alpha[i], a[i], d[i], q[i]);
        T[i + 1] = mat4_mul(&T[i], &A_i);

        z_axes[i] = vec3_create(T[i].m[0][2], T[i].m[1][2], T[i].m[2][2]);
        p_origins[i] = vec3_create(T[i].m[0][3], T[i].m[1][3], T[i].m[2][3]);
    }

    *out_T_end = T[DOF];
    Vec3 p_end = vec3_create(T[DOF].m[0][3], T[DOF].m[1][3], T[DOF].m[2][3]);

    for (int i = 0; i < DOF; ++i) {
        Vec3 r = vec3_create(p_end.x - p_origins[i].x, p_end.y - p_origins[i].y, p_end.z - p_origins[i].z);
        Vec3 lin = vec3_cross(z_axes[i], r);

        J[0][i] = z_axes[i].x;
        J[1][i] = z_axes[i].y;
        J[2][i] = z_axes[i].z;
        J[3][i] = lin.x;
        J[4][i] = lin.y;
        J[5][i] = lin.z;
    }
}

int main(void) {
    double q[DOF] = {0.1, 0.3, -0.5, 0.2, 0.4, -0.1};
    Mat4 T_end;
    double J[6][DOF];

    compute_fk_and_jacobian(q, &T_end, J);

    printf("=== Пряма кінематика 6-DoF маніпулятора (C99) ===\n");
    printf("Положення схоплювача: x = %.3f м, y = %.3f м, z = %.3f м\n\n",
           T_end.m[0][3], T_end.m[1][3], T_end.m[2][3]);

    printf("Матриця Якобі J(q) розмірності 6x6:\n");
    for (int r = 0; r < 6; ++r) {
        for (int c = 0; c < DOF; ++c) {
            printf("%8.3f ", J[r][c]);
        }
        printf("\n");
    }

    return 0;
}
