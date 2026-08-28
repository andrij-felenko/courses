/* electrostatic_energy.c — Обчислення енергії системи зарядів мовою C (C99)
   Компіляція: gcc -O3 -std=c99 electrostatic_energy.c -lm -o electrostatic_energy */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define VACUUM_EPS0 8.8541878128e-12
#define COULOMB_K   8.9875517923e9  /* 1 / (4 * pi * eps0) */

typedef struct {
    double x;
    double y;
    double z;
    double q;
} Charge3D;

/* Обчислення повної кулонівської енергії взаємодії N зарядів */
double compute_system_energy(const Charge3D *charges, size_t n, double r_soft) {
    if (!charges || n < 2) {
        return 0.0;
    }
    
    double total_energy = 0.0;
    const double r_soft_sq = r_soft * r_soft;

    /* Обхід лише верхнього трикутника (i < j) для виключення дублювання пар */
    for (size_t i = 0; i < n; ++i) {
        const double xi = charges[i].x;
        const double yi = charges[i].y;
        const double zi = charges[i].z;
        const double qi = charges[i].q;

        for (size_t j = i + 1; j < n; ++j) {
            const double dx = xi - charges[j].x;
            const double dy = yi - charges[j].y;
            const double dz = zi - charges[j].z;

            const double dist_sq = dx * dx + dy * dy + dz * dz + r_soft_sq;
            const double dist = sqrt(dist_sq);

            total_energy += (qi * charges[j].q) / dist;
        }
    }

    return COULOMB_K * total_energy;
}

/* Генерація тестової системи N зарядів у кубі 1x1x1 м */
Charge3D* generate_random_system(size_t n) {
    Charge3D *arr = (Charge3D*)malloc(n * sizeof(Charge3D));
    if (!arr) return NULL;

    srand(12345); /* Фіксоване зерно для відтворюваності */
    for (size_t i = 0; i < n; ++i) {
        arr[i].x = (double)rand() / RAND_MAX;
        arr[i].y = (double)rand() / RAND_MAX;
        arr[i].z = (double)rand() / RAND_MAX;
        /* Чергування позитивних та негативних зарядів +-1 мкКл */
        arr[i].q = (i % 2 == 0) ? 1e-6 : -1e-6;
    }
    return arr;
}

int main(void) {
    const size_t n_charges = 1000;
    const double r_soft = 1e-9; /* 1 нм регуляризація */

    Charge3D *system = generate_random_system(n_charges);
    if (!system) {
        fprintf(stderr, "Помилка виділення пам'яті!\n");
        return 1;
    }

    clock_t start = clock();
    const double W = compute_system_energy(system, n_charges, r_soft);
    clock_t end = clock();

    double elapsed_ms = (double)(end - start) * 1000.0 / CLOCKS_PER_SEC;

    printf("Розмір системи: N = %zu зарядів\n", n_charges);
    printf("Повна потенціальна енергія системи: W = %.6f Дж (%.3f мДж)\n", W, W * 1000.0);
    printf("Час обчислення (C99): %.3f мс\n", elapsed_ms);

    free(system);
    return 0;
}
