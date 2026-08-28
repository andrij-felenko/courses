#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>

// Структура для збереження результатів порівняльного аналізу
typedef struct {
    double markov_bound;
    double chebyshev_bound;
    double chernoff_bound_approx;
    double chernoff_bound_exact;
    double empirical_probability;
} BoundResult;

// Обчислення теоретичних меж та Монте-Карло симуляція
BoundResult calculate_bounds(int n, double p, double delta, int trials) {
    BoundResult res;
    double mu = n * p;
    double variance = n * p * (1.0 - p);
    double threshold = (1.0 + delta) * mu;

    // 1. Межа Маркова: Pr[X >= T] <= mu / T
    res.markov_bound = mu / threshold;
    if (res.markov_bound > 1.0) res.markov_bound = 1.0;

    // 2. Межа Чебишова: Pr[|X - mu| >= dev] <= Var[X] / dev^2
    double dev = threshold - mu;
    res.chebyshev_bound = variance / (dev * dev);
    if (res.chebyshev_bound > 1.0) res.chebyshev_bound = 1.0;

    // 3. Межа Чернова (квадратична аппроксимація): exp(-mu * delta^2 / 3)
    res.chernoff_bound_approx = exp(-mu * delta * delta / 3.0);
    if (res.chernoff_bound_approx > 1.0) res.chernoff_bound_approx = 1.0;

    // 4. Межа Чернова (точна MGF через логарифмічний простір для уникнення переповнення)
    double log_exact = mu * (delta - (1.0 + delta) * log(1.0 + delta));
    res.chernoff_bound_exact = exp(log_exact);
    if (res.chernoff_bound_exact > 1.0) res.chernoff_bound_exact = 1.0;

    // Симуляція методом Монте-Карло
    int violation_count = 0;
    for (int t = 0; t < trials; ++t) {
        int sum = 0;
        for (int i = 0; i < n; ++i) {
            double r = (double)rand() / ((double)RAND_MAX + 1.0);
            if (r < p) {
                sum++;
            }
        }
        if (sum >= threshold) {
            violation_count++;
        }
    }
    res.empirical_probability = (double)violation_count / (double)trials;

    return res;
}

int main(void) {
    srand((unsigned int)time(NULL));

    int n = 300;
    double p = 0.3;
    double delta = 0.4;
    int trials = 200000;

    printf("=== Симуляція нерівності Чернова (C99) ===\n");
    printf("Параметри: n = %d, p = %.2f, delta = %.2f, trials = %d\n", n, p, delta, trials);
    printf("Очікуване значення mu = %.2f\n", n * p);
    printf("Поріг відхилення T = (1 + delta)*mu = %.2f\n\n", (1.0 + delta) * n * p);

    BoundResult res = calculate_bounds(n, p, delta, trials);

    printf("Емпірична ймовірність Pr[X >= T] : %.6f\n", res.empirical_probability);
    printf("----------------------------------------\n");
    printf("Межа Маркова                     : %.6f\n", res.markov_bound);
    printf("Межа Чебишова                    : %.6f\n", res.chebyshev_bound);
    printf("Межа Чернова (квадратична)       : %.6f\n", res.chernoff_bound_approx);
    printf("Межа Чернова (точна MGF)         : %.6f\n", res.chernoff_bound_exact);

    return 0;
}
