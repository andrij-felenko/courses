#include <math.h>
#include <stdbool.h>
#include <stddef.h>

#define DOF 6
#define CARTESIAN_DIM 6

typedef struct {
    double q[DOF];             /* Кути шарнірів (рад) */
} JointState;

typedef struct {
    double v[3];               /* Лінійна швидкість (м/с) */
    double omega[3];           /* Кутова швидкість (рад/с) */
} Twist;

typedef struct {
    double lambda_max;         /* Максимальний коефіцієнт демпфування */
    double w_threshold;        /* Поріг маніпулятивності активації DLS */
    double max_joint_vel;      /* Гранична швидкість приводу (рад/с) */
} DlsConfig;

/* Обчислення добутку A * B для квадратних матриць 6x6 */
static void mat_mul6(const double a[6][6], const double b[6][6], double out[6][6]) {
    for (int r = 0; r < 6; ++r) {
        for (int c = 0; c < 6; ++c) {
            double sum = 0.0;
            for (int k = 0; k < 6; ++k) {
                sum += a[r][k] * b[k][c];
            }
            out[r][c] = sum;
        }
    }
}

/* Обчислення матриці Грама G = J * J^T (розмір 6x6) */
static void compute_gram_matrix(const double J[6][6], double G[6][6]) {
    for (int r = 0; r < 6; ++r) {
        for (int c = 0; c < 6; ++c) {
            double sum = 0.0;
            for (int k = 0; k < 6; ++k) {
                sum += J[r][k] * J[c][k];
            }
            G[r][c] = sum;
        }
    }
}

/* Обернення матриці 6x6 методом Гауса-Жордана з частковим вибором головного елемента */
static bool invert_matrix6(const double in[6][6], double inv[6][6], double *det_out) {
    double aug[6][12];
    for (int r = 0; r < 6; ++r) {
        for (int c = 0; c < 6; ++c) {
            aug[r][c] = in[r][c];
            aug[r][c + 6] = (r == c) ? 1.0 : 0.0;
        }
    }

    double det = 1.0;

    for (int i = 0; i < 6; ++i) {
        int pivot = i;
        double max_val = fabs(aug[i][i]);
        for (int r = i + 1; r < 6; ++r) {
            double val = fabs(aug[r][i]);
            if (val > max_val) {
                max_val = val;
                pivot = r;
            }
        }

        if (max_val < 1e-12) {
            if (det_out) *det_out = 0.0;
            return false; /* Матриця вироджена */
        }

        if (pivot != i) {
            for (int c = 0; c < 12; ++c) {
                double tmp = aug[i][c];
                aug[i][c] = aug[pivot][c];
                aug[pivot][c] = tmp;
            }
            det = -det;
        }

        double diag = aug[i][i];
        det *= diag;

        for (int c = 0; c < 12; ++c) {
            aug[i][c] /= diag;
        }

        for (int r = 0; r < 6; ++r) {
            if (r != i) {
                double factor = aug[r][i];
                for (int c = 0; c < 12; ++c) {
                    aug[r][c] -= factor * aug[i][c];
                }
            }
        }
    }

    if (det_out) *det_out = det;

    for (int r = 0; r < 6; ++r) {
        for (int c = 0; c < 6; ++c) {
            inv[r][c] = aug[r][c + 6];
        }
    }
    return true;
}

/* Оцінка показника маніпулятивності Йошікави w = sqrt(det(J * J^T)) */
double compute_yoshikawa_manipulability(const double J[6][6]) {
    double G[6][6];
    compute_gram_matrix(J, G);

    double invG[6][6];
    double det_G = 0.0;
    if (!invert_matrix6(G, invG, &det_G) || det_G <= 0.0) {
        return 0.0;
    }
    return sqrt(det_G);
}

/* Розв'язання оберненої швидкості методом адаптивного DLS */
bool solve_ik_dls(const double J[6][6], const Twist *twist,
                  const DlsConfig *cfg, double qdot_out[DOF], double *manipulability) {
    if (!twist || !cfg || !qdot_out) return false;

    double G[6][6];
    compute_gram_matrix(J, G);

    /* Обчислення маніпулятивності */
    double invG_dummy[6][6];
    double det_G = 0.0;
    invert_matrix6(G, invG_dummy, &det_G);
    double w = (det_G > 0.0) ? sqrt(det_G) : 0.0;
    if (manipulability) *manipulability = w;

    /* Розрахунок адаптивного демпфування lambda^2 */
    double lambda_sq = 0.0;
    if (w < cfg->w_threshold) {
        double ratio = 1.0 - (w / cfg->w_threshold);
        lambda_sq = cfg->lambda_max * cfg->lambda_max * ratio * ratio;
    }

    /* Додавання регуляризації: G_damped = J * J^T + lambda^2 * I */
    for (int i = 0; i < 6; ++i) {
        G[i][i] += lambda_sq;
    }

    /* Обернення регуляризованої матриці */
    double G_inv[6][6];
    double det_damped = 0.0;
    if (!invert_matrix6(G, G_inv, &det_damped)) {
        return false;
    }

    /* Вектор декартової швидкості x_dot */
    double x_dot[6] = {
        twist->v[0], twist->v[1], twist->v[2],
        twist->omega[0], twist->omega[1], twist->omega[2]
    };

    /* v_temp = G_inv * x_dot */
    double v_temp[6];
    for (int r = 0; r < 6; ++r) {
        double sum = 0.0;
        for (int c = 0; c < 6; ++c) {
            sum += G_inv[r][c] * x_dot[c];
        }
        v_temp[r] = sum;
    }

    /* q_dot = J^T * v_temp */
    double max_qdot = 0.0;
    for (int j = 0; j < DOF; ++j) {
        double sum = 0.0;
        for (int r = 0; r < 6; ++r) {
            sum += J[r][j] * v_temp[r];
        }
        qdot_out[j] = sum;
        if (fabs(sum) > max_qdot) {
            max_qdot = fabs(sum);
        }
    }

    /* Масштабування швидкостей у разі перевищення ліміту приводів */
    if (max_qdot > cfg->max_joint_vel && max_qdot > 1e-6) {
        double scale = cfg->max_joint_vel / max_qdot;
        for (int j = 0; j < DOF; ++j) {
            qdot_out[j] *= scale;
        }
    }

    return true;
}
