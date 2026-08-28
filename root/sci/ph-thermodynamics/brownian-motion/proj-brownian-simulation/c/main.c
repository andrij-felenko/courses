#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Фізичні параметри системи */
typedef struct {
    double temp;      /* Температура, К (напр. 300.0) */
    double gamma;     /* Коефіцієнт в'язкого тертя, кг/с */
    double mass;      /* Маса частинки, кг */
    double dt;        /* Крок симуляції за часом, с */
    size_t num_steps; /* Кількість кроків у траєкторії */
    size_t num_trials;/* Кількість частинок в ансамблі */
} SimulationParams;

/* Результати аналізу MSD */
typedef struct {
    double *time_array;
    double *msd_array;
    double estimated_D;
    size_t num_steps;
} SimulationResult;

/* Генератор випадкових чисел Ґаусса (перетворення Бокса—Мюллера) */
static double generate_gaussian(void) {
    double u1 = (double)rand() / (double)RAND_MAX;
    double u2 = (double)rand() / (double)RAND_MAX;
    if (u1 < 1e-12) u1 = 1e-12;
    return sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2);
}

/* Вільна пам'ять для результатів */
void free_simulation_result(SimulationResult *res) {
    if (res) {
        free(res->time_array);
        free(res->msd_array);
        res->time_array = NULL;
        res->msd_array = NULL;
    }
}

/* Симуляція ансамблю частинок та розрахунок MSD */
int run_brownian_simulation(const SimulationParams *p, SimulationResult *res) {
    const double kB = 1.380649e-23; /* Стала Больцмана, Дж/К */
    const double noise_amp = sqrt(2.0 * p->gamma * kB * p->temp * p->dt) / p->mass;
    const double damping = 1.0 - (p->gamma / p->mass) * p->dt;

    res->num_steps = p->num_steps;
    res->time_array = (double *)calloc(p->num_steps, sizeof(double));
    res->msd_array = (double *)calloc(p->num_steps, sizeof(double));

    if (!res->time_array || !res->msd_array) {
        free_simulation_result(res);
        return -1;
    }

    for (size_t i = 0; i < p->num_steps; ++i) {
        res->time_array[i] = (double)i * p->dt;
    }

    /* Накопичення квадрата зсуву по ансамблю */
    for (size_t trial = 0; trial < p->num_trials; ++trial) {
        double x = 0.0, y = 0.0;
        /* Початкова теплова швидкість v ~ N(0, sqrt(kB T / m)) */
        double v_scale = sqrt(kB * p->temp / p->mass);
        double vx = generate_gaussian() * v_scale;
        double vy = generate_gaussian() * v_scale;

        res->msd_array[0] += (x * x + y * y);

        for (size_t step = 1; step < p->num_steps; ++step) {
            vx = vx * damping + noise_amp * generate_gaussian();
            vy = vy * damping + noise_amp * generate_gaussian();

            x += vx * p->dt;
            y += vy * p->dt;

            res->msd_array[step] += (x * x + y * y);
        }
    }

    /* Усереднення по ансамблю */
    for (size_t step = 0; step < p->num_steps; ++step) {
        res->msd_array[step] /= (double)p->num_trials;
    }

    /* Оцінка коефіцієнта дифузії в 2D: D = MSD / (4 * t) на лінійній ділянці */
    size_t last_idx = p->num_steps - 1;
    if (res->time_array[last_idx] > 0.0) {
        res->estimated_D = res->msd_array[last_idx] / (4.0 * res->time_array[last_idx]);
    } else {
        res->estimated_D = 0.0;
    }

    return 0;
}

int main(void) {
    srand((unsigned int)time(NULL));

    SimulationParams params = {
        .temp = 300.0,
        .gamma = 1e-8,
        .mass = 1e-14,
        .dt = 1e-7,
        .num_steps = 1000,
        .num_trials = 500
    };

    SimulationResult result = {0};
    if (run_brownian_simulation(&params, &result) == 0) {
        double theory_D = (1.380649e-23 * params.temp) / params.gamma;
        printf("Теоретичний D = %.4e м²/с\n", theory_D);
        printf("Оцінений D    = %.4e м²/с\n", result.estimated_D);
        printf("MSD на кроці 100 (t = %.2e с): %.4e м²\n",
               result.time_array[100], result.msd_array[100]);
        printf("MSD на кроці 999 (t = %.2e с): %.4e м²\n",
               result.time_array[999], result.msd_array[999]);
        free_simulation_result(&result);
    } else {
        fprintf(stderr, "Помилка виділення пам'яті під час симуляції\n");
        return 1;
    }

    return 0;
}
