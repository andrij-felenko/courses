#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

typedef struct {
    int x;
    int y;
} Particle;

typedef struct {
    int lx;
    int ly;
    int num_particles;
    Particle *particles;
} LatticeGas;

/* Створення та ініціалізація газу у лівій половині ґратки */
LatticeGas* lattice_gas_create(int lx, int ly, int n) {
    LatticeGas *gas = (LatticeGas*)malloc(sizeof(LatticeGas));
    if (!gas) return NULL;

    gas->lx = lx;
    gas->ly = ly;
    gas->num_particles = n;
    gas->particles = (Particle*)malloc(sizeof(Particle) * n);
    if (!gas->particles) {
        free(gas);
        return NULL;
    }

    /* Розміщення частинок у лівій половині: x in [0, lx/2 - 1] */
    int half_x = lx / 2;
    for (int i = 0; i < n; ++i) {
        gas->particles[i].x = rand() % half_x;
        gas->particles[i].y = rand() % ly;
    }

    return gas;
}

void lattice_gas_free(LatticeGas *gas) {
    if (gas) {
        free(gas->particles);
        free(gas);
    }
}

/* Крок симуляції: випадкове блукання кожної частинки */
void lattice_gas_step(LatticeGas *gas) {
    for (int i = 0; i < gas->num_particles; ++i) {
        int dir = rand() % 4;
        int nx = gas->particles[i].x;
        int ny = gas->particles[i].y;

        if (dir == 0) nx++;      /* праворуч */
        else if (dir == 1) nx--; /* ліворуч */
        else if (dir == 2) ny++; /* вгору */
        else if (dir == 3) ny--; /* вниз */

        /* Відбиваючі межі ґратки */
        if (nx >= 0 && nx < gas->lx) gas->particles[i].x = nx;
        if (ny >= 0 && ny < gas->ly) gas->particles[i].y = ny;
    }
}

/* Підрахунок частинок у ліві половині */
int lattice_gas_count_left(const LatticeGas *gas) {
    int count = 0;
    int half_x = gas->lx / 2;
    for (int i = 0; i < gas->num_particles; ++i) {
        if (gas->particles[i].x < half_x) {
            count++;
        }
    }
    return count;
}

/* Точне обчислення S / k_B = ln W через lgamma */
double calculate_entropy(int n, int n_left) {
    int n_right = n - n_left;
    double log_n_fact = lgamma(n + 1.0);
    double log_nl_fact = lgamma(n_left + 1.0);
    double log_nr_fact = lgamma(n_right + 1.0);

    return log_n_fact - log_nl_fact - log_nr_fact;
}

int main(void) {
    srand((unsigned int)time(NULL));

    const int LX = 100;
    const int LY = 100;
    const int N = 1000;
    const int STEPS = 200;

    LatticeGas *gas = lattice_gas_create(LX, LY, N);
    if (!gas) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    printf("Крок\tN_L\tN_R\tS/k_B\t\tS_max/k_B\n");
    double s_max = N * log(2.0); /* Рівноважна ентропія для рівних частин */

    for (int step = 0; step <= STEPS; step += 10) {
        int n_left = lattice_gas_count_left(gas);
        int n_right = N - n_left;
        double s_boltzmann = calculate_entropy(N, n_left);

        printf("%d\t%d\t%d\t%.4f\t%.4f\n", step, n_left, n_right, s_boltzmann, s_max);

        for (int k = 0; k < 10; ++k) {
            lattice_gas_step(gas);
        }
    }

    lattice_gas_free(gas);
    return 0;
}
