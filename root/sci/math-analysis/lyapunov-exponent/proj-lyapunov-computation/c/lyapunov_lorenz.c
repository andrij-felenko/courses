/* lyapunov_lorenz.c - Чисельний розрахунок спектра Ляпунова мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define DIM 3

/* Параметри системи Лоренца 63 */
typedef struct {
    double sigma;
    double rho;
    double beta;
} LorenzParams;

/* Обчислення правої частини системи Лоренца f(x) */
static void lorenz_rhs(const double x[DIM], double dxdt[DIM], const LorenzParams *p) {
    dxdt[0] = p->sigma * (x[1] - x[0]);
    dxdt[1] = x[0] * (p->rho - x[2]) - x[1];
    dxdt[2] = x[0] * x[1] - p->beta * x[2];
}

/* Обчислення матриці Якобі J(x) для системи Лоренца */
static void lorenz_jacobian(const double x[DIM], double J[DIM][DIM], const LorenzParams *p) {
    J[0][0] = -p->sigma;  J[0][1] = p->sigma;   J[0][2] = 0.0;
    J[1][0] = p->rho - x[2]; J[1][1] = -1.0;     J[1][2] = -x[0];
    J[2][0] = x[1];        J[2][1] = x[0];      J[2][2] = -p->beta;
}

/* Множення матриці Якобі на вектор: dy = J · y */
static void mat_vec_mult(const double J[DIM][DIM], const double y[DIM], double dydt[DIM]) {
    for (int i = 0; i < DIM; ++i) {
        dydt[i] = 0.0;
        for (int j = 0; j < DIM; ++j) {
            dydt[i] += J[i][j] * y[j];
        }
    }
}

/* Один крок інтегрування методом Рунге-Кутти 4-го порядку (RK4) */
static void rk4_step(double x[DIM], double Q[DIM][DIM], double dt, const LorenzParams *p) {
    double k1_x[DIM], k2_x[DIM], k3_x[DIM], k4_x[DIM];
    double temp_x[DIM];
    
    double k1_Q[DIM][DIM], k2_Q[DIM][DIM], k3_Q[DIM][DIM], k4_Q[DIM][DIM];
    double temp_Q[DIM][DIM];
    double J[DIM][DIM];

    /* Крок 1 */
    lorenz_rhs(x, k1_x, p);
    lorenz_jacobian(x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { Q[0][col], Q[1][col], Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k1_Q[r][col] = res[r];
    }

    /* Крок 2 */
    for (int i = 0; i < DIM; ++i) temp_x[i] = x[i] + 0.5 * dt * k1_x[i];
    for (int r = 0; r < DIM; ++r)
        for (int c = 0; c < DIM; ++c)
            temp_Q[r][c] = Q[r][c] + 0.5 * dt * k1_Q[r][c];

    lorenz_rhs(temp_x, k2_x, p);
    lorenz_jacobian(temp_x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { temp_Q[0][col], temp_Q[1][col], temp_Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k2_Q[r][col] = res[r];
    }

    /* Крок 3 */
    for (int i = 0; i < DIM; ++i) temp_x[i] = x[i] + 0.5 * dt * k2_x[i];
    for (int r = 0; r < DIM; ++r)
        for (int c = 0; c < DIM; ++c)
            temp_Q[r][c] = Q[r][c] + 0.5 * dt * k2_Q[r][c];

    lorenz_rhs(temp_x, k3_x, p);
    lorenz_jacobian(temp_x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { temp_Q[0][col], temp_Q[1][col], temp_Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k3_Q[r][col] = res[r];
    }

    /* Крок 4 */
    for (int i = 0; i < DIM; ++i) temp_x[i] = x[i] + dt * k3_x[i];
    for (int r = 0; r < DIM; ++r)
        for (int c = 0; c < DIM; ++c)
            temp_Q[r][c] = Q[r][c] + dt * k3_Q[r][c];

    lorenz_rhs(temp_x, k4_x, p);
    lorenz_jacobian(temp_x, J, p);
    for (int col = 0; col < DIM; ++col) {
        double col_vec[DIM] = { temp_Q[0][col], temp_Q[1][col], temp_Q[2][col] };
        double res[DIM];
        mat_vec_mult(J, col_vec, res);
        for (int r = 0; r < DIM; ++r) k4_Q[r][col] = res[r];
    }

    /* Оновлення стану x та матриці Q */
    for (int i = 0; i < DIM; ++i) {
        x[i] += (dt / 6.0) * (k1_x[i] + 2.0 * k2_x[i] + 2.0 * k3_x[i] + k4_x[i]);
    }
    for (int r = 0; r < DIM; ++r) {
        for (int c = 0; c < DIM; ++c) {
            Q[r][c] += (dt / 6.0) * (k1_Q[r][c] + 2.0 * k2_Q[r][c] + 2.0 * k3_Q[r][c] + k4_Q[r][c]);
        }
    }
}

/* Ортогоналізація Грама-Шмідта стовпчиків матриці Q з поверненням норм */
static void gram_schmidt(double Q[DIM][DIM], double r_diag[DIM]) {
    for (int j = 0; j < DIM; ++j) {
        /* Вектор v = j-й стовпчик Q */
        double v[DIM];
        for (int i = 0; i < DIM; ++i) v[i] = Q[i][j];

        /* Ортогоналізація відносно попередніх стовпчиків */
        for (int k = 0; k < j; ++k) {
            double dot = 0.0;
            for (int i = 0; i < DIM; ++i) dot += v[i] * Q[i][k];
            for (int i = 0; i < DIM; ++i) v[i] -= dot * Q[i][k];
        }

        /* Обчислення норми */
        double norm = 0.0;
        for (int i = 0; i < DIM; ++i) norm += v[i] * v[i];
        norm = sqrt(norm);
        r_diag[j] = norm;

        /* Нормування вектора */
        for (int i = 0; i < DIM; ++i) {
            Q[i][j] = (norm > 1e-14) ? (v[i] / norm) : 0.0;
        }
    }
}

int main(void) {
    LorenzParams params = { 10.0, 28.0, 8.0 / 3.0 };
    double x[DIM] = { 1.0, 1.0, 1.0 };
    double Q[DIM][DIM] = {
        { 1.0, 0.0, 0.0 },
        { 0.0, 1.0, 0.0 },
        { 0.0, 0.0, 1.0 }
    };

    double dt = 0.01;
    long total_steps = 100000;
    long transient_steps = 10000;
    double lyap_sum[DIM] = { 0.0, 0.0, 0.0 };

    /* Пропуск перехідного процесу (вихід на атрактор) */
    for (long step = 0; step < transient_steps; ++step) {
        rk4_step(x, Q, dt, &params);
        double dummy_r[DIM];
        gram_schmidt(Q, dummy_r);
    }

    /* Основний цикл накопичення показників Ляпунова */
    for (long step = 0; step < total_steps; ++step) {
        rk4_step(x, Q, dt, &params);
        double r_diag[DIM];
        gram_schmidt(Q, r_diag);

        for (int i = 0; i < DIM; ++i) {
            lyap_sum[i] += log(r_diag[i]);
        }
    }

    double total_time = total_steps * dt;
    printf("Спектр показників Ляпунова для системи Лоренца:\n");
    for (int i = 0; i < DIM; ++i) {
        double lyap = lyap_sum[i] / total_time;
        printf("  λ_%d = %+.5f\n", i + 1, lyap);
    }

    /* Розмірність Каплана-Йорке */
    double l1 = lyap_sum[0] / total_time;
    double l2 = lyap_sum[1] / total_time;
    double l3 = lyap_sum[2] / total_time;
    if (l1 > 0.0 && (l1 + l2) > 0.0 && l3 < 0.0) {
        double d_L = 2.0 + (l1 + l2) / fabs(l3);
        printf("Розмірність Каплана–Йорке D_L = %.4f\n", d_L);
    }

    return 0;
}
