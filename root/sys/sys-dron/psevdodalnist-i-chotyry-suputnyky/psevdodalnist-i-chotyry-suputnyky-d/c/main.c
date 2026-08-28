#include <stdio.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

#define GNSS_SPEED_OF_LIGHT 299792458.0      /* м/с */
#define GNSS_EARTH_ROT_RATE 7.2921151467e-5  /* рад/с (WGS-84) */
#define GNSS_MAX_SATS       32
#define GNSS_MAX_ITER       10
#define GNSS_CONV_TOL       1e-4             /* поріг збіжності в метрах */

/* Спостереження одного супутника в дану епоху */
typedef struct {
    double x_sat;       /* ECEF координата X (м) */
    double y_sat;       /* ECEF координата Y (м) */
    double z_sat;       /* ECEF координата Z (м) */
    double pseudorange; /* виміряна псевдодальність (м) */
    double dt_sat;      /* поправка супутникового годинника (с) */
    double elevation;   /* кут піднесення над горизонтом (рад) */
} GnssSatObs;

/* Результат розрахунку навігаційного фіксу */
typedef struct {
    double x, y, z;     /* розраховані координати ECEF (м) */
    double c_dt;        /* зсув годинника приймача (м) */
    double gdop, pdop, hdop, vdop, tdop;
    int iterations_used;
    bool converged;
} GnssNavSolution;

/* Інверсія симетричної матриці 4x4 методом Гаусса-Жордана */
static bool mat4_invert(const double A[4][4], double inv[4][4]) {
    double aug[4][8];
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            aug[i][j] = A[i][j];
            aug[i][j + 4] = (i == j) ? 1.0 : 0.0;
        }
    }

    for (int col = 0; col < 4; col++) {
        int pivot = col;
        double max_val = fabs(aug[col][col]);
        for (int row = col + 1; row < 4; row++) {
            double v = fabs(aug[row][col]);
            if (v > max_val) {
                max_val = v;
                pivot = row;
            }
        }
        if (max_val < 1e-15) return false; /* вироджена матриця */

        if (pivot != col) {
            for (int k = 0; k < 8; k++) {
                double tmp = aug[col][k];
                aug[col][k] = aug[pivot][k];
                aug[pivot][k] = tmp;
            }
        }

        double scale = aug[col][col];
        for (int k = 0; k < 8; k++) aug[col][k] /= scale;

        for (int row = 0; row < 4; row++) {
            if (row != col) {
                double factor = aug[row][col];
                for (int k = 0; k < 8; k++) {
                    aug[row][k] -= factor * aug[col][k];
                }
            }
        }
    }

    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            inv[i][j] = aug[i][j + 4];
        }
    }
    return true;
}

/* Розрахунок геодезичних DOP-метрик через поворот до локальної системи ENU */
static void compute_dop_metrics(const double invN[4][4], double x, double y, double z,
                                GnssNavSolution *sol) {
    /* Геоцентрична широта та довжина для матриці повороту */
    double p = sqrt(x * x + y * y);
    double lat = atan2(z, p);
    double lon = atan2(y, x);

    double s_lat = sin(lat), c_lat = cos(lat);
    double s_lon = sin(lon), c_lon = cos(lon);

    /* Матриця обертання ECEF -> ENU (3x3) */
    double R[3][3] = {
        { -s_lon,          c_lon,         0.0    },
        { -s_lat * c_lon, -s_lat * s_lon, c_lat  },
        {  c_lat * c_lon,  c_lat * s_lon, s_lat  }
    };

    /* Q_enu = R * invN[0..2][0..2] * R^T */
    double Q_xyz[3][3];
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            Q_xyz[i][j] = invN[i][j];

    double temp[3][3] = {0};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            for (int k = 0; k < 3; k++)
                temp[i][j] += R[i][k] * Q_xyz[k][j];

    double Q_enu[3][3] = {0};
    for (int i = 0; i < 3; i++)
        for (int j = 0; j < 3; j++)
            for (int k = 0; k < 3; k++)
                Q_enu[i][j] += temp[i][k] * R[j][k];

    double qE = Q_enu[0][0];
    double qN = Q_enu[1][1];
    double qU = Q_enu[2][2];
    double qT = invN[3][3];

    sol->hdop = sqrt(fmax(0.0, qE + qN));
    sol->vdop = sqrt(fmax(0.0, qU));
    sol->pdop = sqrt(fmax(0.0, qE + qN + qU));
    sol->tdop = sqrt(fmax(0.0, qT));
    sol->gdop = sqrt(fmax(0.0, qE + qN + qU + qT));
}

/* Головний розв'язувач навігаційної задачі методом Gauss-Newton WLS */
bool gnss_solve_pseudoranges(const GnssSatObs *sats, int num_sats,
                             GnssNavSolution *sol) {
    if (num_sats < 4 || !sats || !sol) return false;

    /* Початкове наближення: центр Землі і нульовий зсув годинника */
    double state[4] = { 0.0, 0.0, 0.0, 0.0 };
    sol->converged = false;
    sol->iterations_used = 0;

    for (int iter = 0; iter < GNSS_MAX_ITER; iter++) {
        double N[4][4] = {0};   /* Нормальна матриця: G^T * W * G */
        double b[4]    = {0};   /* Правий вектор: G^T * W * delta_rho */

        for (int i = 0; i < num_sats; i++) {
            /* 1. Корекція обертання Землі під час польоту сигналу (Sagnac effect) */
            double dx = sats[i].x_sat - state[0];
            double dy = sats[i].y_sat - state[1];
            double dz = sats[i].z_sat - state[2];
            double approx_range = sqrt(dx * dx + dy * dy + dz * dz);
            double tau = approx_range / GNSS_SPEED_OF_LIGHT;
            double alpha = GNSS_EARTH_ROT_RATE * tau;

            /* Поворот супутника навколо осі Z */
            double x_sat_rot =  cos(alpha) * sats[i].x_sat + sin(alpha) * sats[i].y_sat;
            double y_sat_rot = -sin(alpha) * sats[i].x_sat + cos(alpha) * sats[i].y_sat;
            double z_sat_rot = sats[i].z_sat;

            /* 2. Геометрична дальність до скоригованого супутника */
            double rx = state[0] - x_sat_rot;
            double ry = state[1] - y_sat_rot;
            double rz = state[2] - z_sat_rot;
            double geom_range = sqrt(rx * rx + ry * ry + rz * rz);
            if (geom_range < 1.0) geom_range = 1.0;

            /* 3. Одиничний вектор прямої видимості (рядок матриці G) */
            double u[4] = { rx / geom_range, ry / geom_range, rz / geom_range, 1.0 };

            /* 4. Виправлена виміряна псевдодальність (мінус годинник супутника) */
            double corr_pr = sats[i].pseudorange + GNSS_SPEED_OF_LIGHT * sats[i].dt_sat;

            /* Нев'язка псевдодальності */
            double expected_pr = geom_range + state[3];
            double delta_rho = corr_pr - expected_pr;

            /* 5. Ваговий коефіцієнт за кутом піднесення w = sin^2(elevation) */
            double s_el = sin(fmax(sats[i].elevation, 0.0872)); /* мінімум 5 градусів */
            double weight = s_el * s_el;

            /* Накопичення нормальних рівнянь: N += G_i^T * w_i * G_i, b += G_i^T * w_i * dr */
            for (int r = 0; r < 4; r++) {
                for (int c = 0; c < 4; c++) {
                    N[r][c] += u[r] * u[c] * weight;
                }
                b[r] += u[r] * weight * delta_rho;
            }
        }

        /* 6. Розв'язання лінійної системи N * dx = b */
        double invN[4][4];
        if (!mat4_invert(N, invN)) return false;

        double delta_x[4] = {0};
        for (int r = 0; r < 4; r++) {
            for (int c = 0; c < 4; c++) {
                delta_x[r] += invN[r][c] * b[c];
            }
        }

        /* 7. Оновлення стану */
        state[0] += delta_x[0];
        state[1] += delta_x[1];
        state[2] += delta_x[2];
        state[3] += delta_x[3];

        sol->iterations_used = iter + 1;
        double pos_step = sqrt(delta_x[0] * delta_x[0] +
                               delta_x[1] * delta_x[1] +
                               delta_x[2] * delta_x[2]);

        /* Перевірка збіжності */
        if (pos_step < GNSS_CONV_TOL) {
            sol->x = state[0];
            sol->y = state[1];
            sol->z = state[2];
            sol->c_dt = state[3];
            sol->converged = true;

            /* Оцінка DOP-метрик */
            compute_dop_metrics(invN, state[0], state[1], state[2], sol);
            return true;
        }
    }

    return false;
}
