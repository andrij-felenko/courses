/* Чисельний аналіз кругових відображень та теореми Данжуа (C). */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double omega;
    double k;
} circle_map_t;

/* Підйом синус-кругового відображення F(x) */
static inline double circle_map_lift(const circle_map_t *map, double x) {
    return x + map->omega - (map->k / (2.0 * M_PI)) * sin(2.0 * M_PI * x);
}

/* Похідна підйому F'(x) */
static inline double circle_map_prime(const circle_map_t *map, double x) {
    return 1.0 - map->k * cos(2.0 * M_PI * x);
}

/* Обчислення числа обертання Пуанкаре */
double compute_rotation_number(const circle_map_t *map, long iterations) {
    double x = 0.0;
    for (long i = 0; i < iterations; ++i) {
        x = circle_map_lift(map, x);
    }
    double rho = fmod(x / (double)iterations, 1.0);
    if (rho < 0.0) rho += 1.0;
    return rho;
}

/* Обчислення накопиченого добутку похідних (f^{q_k}')(x0) */
double compute_derivative_product(const circle_map_t *map, double x0, long q_steps) {
    double prod = 1.0;
    double curr_x = x0;
    for (long i = 0; i < q_steps; ++i) {
        double mod_x = fmod(curr_x, 1.0);
        if (mod_x < 0.0) mod_x += 1.0;
        prod *= circle_map_prime(map, mod_x);
        curr_x = circle_map_lift(map, curr_x);
    }
    return prod;
}

int main(void) {
    double golden_ratio = (sqrt(5.0) - 1.0) / 2.0;
    circle_map_t map = { .omega = golden_ratio, .k = 0.5 };

    printf("=== Аналіз кругового відображення (C) ===\n");
    printf("Omega = %.8f, K = %.2f\n", map.omega, map.k);

    double rho = compute_rotation_number(&map, 1000000L);
    printf("Число обертання rho(f) = %.8f\n\n", rho);

    long test_q[] = { 13, 34, 89, 233, 610, 1597 };
    size_t num_q = sizeof(test_q) / sizeof(test_q[0]);

    double x1 = 0.123, x2 = 0.789;
    printf("q_k   | log(f^{q_k}')(x1) | log(f^{q_k}')(x2) | |log_d1 - log_d2|\n");
    printf("----------------------------------------------------------------\n");

    for (size_t i = 0; i < num_q; ++i) {
        long q = test_q[i];
        double d1 = compute_derivative_product(&map, x1, q);
        double d2 = compute_derivative_product(&map, x2, q);
        double log_d1 = log(fabs(d1));
        double log_d2 = log(fabs(d2));
        double diff = fabs(log_d1 - log_d2);

        printf("%-5ld | %-17.6f | %-17.6f | %.6f\n", q, log_d1, log_d2, diff);
    }

    return 0;
}
