#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define N 128
#define DT 0.02
#define DX 1.0
#define KAPPA 1.0
#define MOBILITY 1.0
#define STEPS 5000

/* Одновимірні масиви для 2D сітки N x N */
static double c[N * N];
static double mu[N * N];
static double c_next[N * N];

/* Отримання індексу за періодичними межами */
static inline int pidx(int i, int j) {
    int ni = (i + N) % N;
    int nj = (j + N) % N;
    return ni * N + nj;
}

/* Обчислення оператора Лапласа для масиву in у точці (i, j) */
static double laplacian(const double *in, int i, int j) {
    double center = in[pidx(i, j)];
    double left   = in[pidx(i - 1, j)];
    double right  = in[pidx(i + 1, j)];
    double up     = in[pidx(i, j - 1)];
    double down   = in[pidx(i, j + 1)];
    return (left + right + up + down - 4.0 * center) / (DX * DX);
}

/* Ініціалізація концентрації з випадковими флуктуаціями [-0.05, 0.05] */
void init_system(double c_mean) {
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            double rnd = ((double)rand() / RAND_MAX - 0.5) * 0.1;
            c[pidx(i, j)] = c_mean + rnd;
        }
    }
}

/* Обчислення повної вільної енергії F[c] */
double compute_total_free_energy(void) {
    double total_energy = 0.0;
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            double val = c[pidx(i, j)];
            double f_bulk = 0.25 * val * val * val * val - 0.5 * val * val;
            
            double dc_dx = (c[pidx(i + 1, j)] - c[pidx(i - 1, j)]) / (2.0 * DX);
            double dc_dy = (c[pidx(i, j + 1)] - c[pidx(i, j - 1)]) / (2.0 * DX);
            double grad_sq = dc_dx * dc_dx + dc_dy * dc_dy;
            
            total_energy += f_bulk + 0.5 * KAPPA * grad_sq;
        }
    }
    return total_energy * (DX * DX);
}

/* Один крок часової інтеграції */
void simulation_step(void) {
    /* 1. Обчислення хімічного потенціалу mu = c^3 - c - KAPPA * laplacian(c) */
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            int idx = pidx(i, j);
            double val = c[idx];
            double df_dc = val * val * val - val;
            double lap_c = laplacian(c, i, j);
            mu[idx] = df_dc - KAPPA * lap_c;
        }
    }

    /* 2. Оновлення концентрації c_next = c + DT * MOBILITY * laplacian(mu) */
    for (int i = 0; i < N; ++i) {
        for (int j = 0; j < N; ++j) {
            int idx = pidx(i, j);
            double lap_mu = laplacian(mu, i, j);
            c_next[idx] = c[idx] + DT * MOBILITY * lap_mu;
        }
    }

    /* 3. Копіювання c_next у c */
    for (int i = 0; i < N * N; ++i) {
        c[i] = c_next[i];
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    init_system(0.0);

    printf("Початкова вільна енергія F: %.4f\n", compute_total_free_energy());

    for (int step = 1; step <= STEPS; ++step) {
        simulation_step();
        if (step % 1000 == 0) {
            printf("Крок %5d | Повна вільна енергія F: %.4f\n", 
                   step, compute_total_free_energy());
        }
    }

    printf("Симуляцію 2D спінодального розпаду на C завершено успішно.\n");
    return 0;
}
