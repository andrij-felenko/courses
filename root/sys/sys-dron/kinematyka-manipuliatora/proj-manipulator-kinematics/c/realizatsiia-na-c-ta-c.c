#include <stdio.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define MAX_JOINTS 8
#define EPSILON 1e-6f

typedef struct {
    float x, y, z;
} vec3_t;

typedef struct {
    float data[4][4];
} mat4_t;

typedef struct {
    float theta;  /* кут повороту навколо Z_(i-1) (рад) */
    float d;      /* зміщення вздовж Z_(i-1) (м) */
    float a;      /* довжина спільного перпендикуляра X_i (м) */
    float alpha;  /* кут скручування навколо X_i (рад) */
    bool is_revolute;
    float q_min;  /* нижня межа руху суглоба */
    float q_max;  /* верхня межа руху суглоба */
} dh_joint_t;

typedef struct {
    dh_joint_t joints[MAX_JOINTS];
    int num_joints;
} manipulator_chain_t;

typedef struct {
    /* 6 рядків (3 лінійні швидкості, 3 кутові швидкості), n стовпців */
    float data[6][MAX_JOINTS];
    int rows;
    int cols;
} jacobian_t;

static inline vec3_t vec3_add(vec3_t a, vec3_t b) {
    return (vec3_t){a.x + b.x, a.y + b.y, a.z + b.z};
}

static inline vec3_t vec3_sub(vec3_t a, vec3_t b) {
    return (vec3_t){a.x - b.x, a.y - b.y, a.z - b.z};
}

static inline vec3_t vec3_cross(vec3_t a, vec3_t b) {
    return (vec3_t){
        a.y * b.z - a.z * b.y,
        a.z * b.x - a.x * b.z,
        a.x * b.y - a.y * b.x
    };
}

static inline float vec3_dot(vec3_t a, vec3_t b) {
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

static inline float vec3_norm(vec3_t a) {
    return sqrtf(vec3_dot(a, a));
}

static mat4_t mat4_identity(void) {
    mat4_t m;
    memset(&m, 0, sizeof(m));
    for (int i = 0; i < 4; i++) m.data[i][i] = 1.0f;
    return m;
}

static mat4_t mat4_multiply(mat4_t a, mat4_t b) {
    mat4_t res;
    for (int r = 0; r < 4; r++) {
        for (int c = 0; c < 4; c++) {
            res.data[r][c] = a.data[r][0] * b.data[0][c] +
                             a.data[r][1] * b.data[1][c] +
                             a.data[r][2] * b.data[2][c] +
                             a.data[r][3] * b.data[3][c];
        }
    }
    return res;
}

/* Однорідна матриця стандартного перетворення Денавіта-Гартенберга */
static mat4_t dh_matrix(float theta, float d, float a, float alpha) {
    float ct = cosf(theta), st = sinf(theta);
    float ca = cosf(alpha), sa = sinf(alpha);

    mat4_t m = {{
        { ct,  -st * ca,   st * sa,  a * ct },
        { st,   ct * ca,  -ct * sa,  a * st },
        { 0.0f,      sa,        ca,       d },
        { 0.0f,    0.0f,      0.0f,    1.0f }
    }};
    return m;
}

/* Пряма кінематика (Forward Kinematics) */
bool fk_solve(const manipulator_chain_t *arm, const float *q,
              mat4_t *t_cumulative, mat4_t *t_end_effector) {
    if (!arm || !q || !t_end_effector) return false;

    mat4_t current = mat4_identity();
    if (t_cumulative) t_cumulative[0] = current;

    for (int i = 0; i < arm->num_joints; i++) {
        float theta = arm->joints[i].theta;
        float d = arm->joints[i].d;

        if (arm->joints[i].is_revolute) {
            theta += q[i];
        } else {
            d += q[i];
        }

        mat4_t t_i = dh_matrix(theta, d, arm->joints[i].a, arm->joints[i].alpha);
        current = mat4_multiply(current, t_i);

        if (t_cumulative) {
            t_cumulative[i + 1] = current;
        }
    }

    *t_end_effector = current;
    return true;
}

/* Обчислення геометричного Якобіана J(q) */
bool jacobian_compute(const manipulator_chain_t *arm, const float *q, jacobian_t *jac) {
    if (!arm || !q || !jac) return false;

    mat4_t t_cum[MAX_JOINTS + 1];
    mat4_t t_ee;
    if (!fk_solve(arm, q, t_cum, &t_ee)) return false;

    vec3_t p_ee = {t_ee.data[0][3], t_ee.data[1][3], t_ee.data[2][3]};

    jac->rows = 6;
    jac->cols = arm->num_joints;
    memset(jac->data, 0, sizeof(jac->data));

    for (int i = 0; i < arm->num_joints; i++) {
        /* Одиничний вектор осі Z_(i-1) у світовій системі */
        vec3_t z_i = {t_cum[i].data[0][2], t_cum[i].data[1][2], t_cum[i].data[2][2]};
        /* Позиція початку координат системи i-1 */
        vec3_t p_i = {t_cum[i].data[0][3], t_cum[i].data[1][3], t_cum[i].data[2][3]};

        if (arm->joints[i].is_revolute) {
            vec3_t r = vec3_sub(p_ee, p_i);
            vec3_t j_v = vec3_cross(z_i, r);
            vec3_t j_w = z_i;

            jac->data[0][i] = j_v.x;
            jac->data[1][i] = j_v.y;
            jac->data[2][i] = j_v.z;
            jac->data[3][i] = j_w.x;
            jac->data[4][i] = j_w.y;
            jac->data[5][i] = j_w.z;
        } else {
            /* Поступальне зчленування */
            jac->data[0][i] = z_i.x;
            jac->data[1][i] = z_i.y;
            jac->data[2][i] = z_i.z;
            jac->data[3][i] = 0.0f;
            jac->data[4][i] = 0.0f;
            jac->data[5][i] = 0.0f;
        }
    }
    return true;
}

/* Обернена кінематика: Damped Least Squares (DLS) для 3D-позиціонування */
bool ik_solve_dls_position(const manipulator_chain_t *arm, vec3_t target_pos,
                           const float *q_init, float *q_out,
                           int max_iters, float tol, float lambda) {
    if (!arm || !q_init || !q_out) return false;

    int n = arm->num_joints;
    for (int i = 0; i < n; i++) q_out[i] = q_init[i];

    float lambda_sq = lambda * lambda;

    for (int iter = 0; iter < max_iters; iter++) {
        mat4_t t_ee;
        fk_solve(arm, q_out, NULL, &t_ee);

        vec3_t current_pos = {t_ee.data[0][3], t_ee.data[1][3], t_ee.data[2][3]};
        vec3_t error = vec3_sub(target_pos, current_pos);

        if (vec3_norm(error) < tol) {
            return true; /* Досягнуто заданої точності */
        }

        jacobian_t full_jac;
        jacobian_compute(arm, q_out, &full_jac);

        /* J_pos: розмірність 3xN */
        /* Обчислюємо A = (J * J^T + lambda^2 * I) розмірністю 3x3 */
        float a_mat[3][3] = {0};
        for (int r = 0; r < 3; r++) {
            for (int c = 0; c < 3; c++) {
                float sum = 0.0f;
                for (int k = 0; k < n; k++) {
                    sum += full_jac.data[r][k] * full_jac.data[c][k];
                }
                a_mat[r][c] = sum + (r == c ? lambda_sq : 0.0f);
            }
        }

        /* Пряме аналітичне обернення симетричної матриці 3x3 через мінори */
        float det = a_mat[0][0] * (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) -
                    a_mat[0][1] * (a_mat[1][0] * a_mat[2][2] - a_mat[1][2] * a_mat[2][0]) +
                    a_mat[0][2] * (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]);

        if (fabsf(det) < EPSILON) return false;
        float inv_det = 1.0f / det;

        float a_inv[3][3];
        a_inv[0][0] = (a_mat[1][1] * a_mat[2][2] - a_mat[1][2] * a_mat[2][1]) * inv_det;
        a_inv[0][1] = (a_mat[0][2] * a_mat[2][1] - a_mat[0][1] * a_mat[2][2]) * inv_det;
        a_inv[0][2] = (a_mat[0][1] * a_mat[1][2] - a_mat[0][2] * a_mat[1][1]) * inv_det;

        a_inv[1][0] = (a_mat[1][2] * a_mat[2][0] - a_mat[1][0] * a_mat[2][2]) * inv_det;
        a_inv[1][1] = (a_mat[0][0] * a_mat[2][2] - a_mat[0][2] * a_mat[2][0]) * inv_det;
        a_inv[1][2] = (a_mat[0][2] * a_mat[1][0] - a_mat[0][0] * a_mat[1][2]) * inv_det;

        a_inv[2][0] = (a_mat[1][0] * a_mat[2][1] - a_mat[1][1] * a_mat[2][0]) * inv_det;
        a_inv[2][1] = (a_mat[0][1] * a_mat[2][0] - a_mat[0][0] * a_mat[2][1]) * inv_det;
        a_inv[2][2] = (a_mat[0][0] * a_mat[1][1] - a_mat[0][1] * a_mat[1][0]) * inv_det;

        /* v_temp = A_inv * error */
        float err_arr[3] = {error.x, error.y, error.z};
        float v_temp[3] = {0};
        for (int r = 0; r < 3; r++) {
            v_temp[r] = a_inv[r][0] * err_arr[0] +
                        a_inv[r][1] * err_arr[1] +
                        a_inv[r][2] * err_arr[2];
        }

        /* delta_q = J^T * v_temp */
        for (int i = 0; i < n; i++) {
            float dq = full_jac.data[0][i] * v_temp[0] +
                       full_jac.data[1][i] * v_temp[1] +
                       full_jac.data[2][i] * v_temp[2];

            q_out[i] += dq;

            /* Затискання в апаратні ліміти */
            if (q_out[i] < arm->joints[i].q_min) q_out[i] = arm->joints[i].q_min;
            if (q_out[i] > arm->joints[i].q_max) q_out[i] = arm->joints[i].q_max;
        }
    }

    return false; /* Перевищено ліміт ітерацій */
}
