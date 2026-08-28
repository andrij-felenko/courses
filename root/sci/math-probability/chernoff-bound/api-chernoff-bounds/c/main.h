#ifndef CHERNOFF_BOUNDS_H
#define CHERNOFF_BOUNDS_H

#include <stdbool.h>
#include <math.h>

// Структура конфігурації параметрів випадкової суми
typedef struct {
    int n;             // загальна кількість незалежних випробувань (n > 0)
    double p;          // ймовірність успіху в кожному випробуванні (0 < p < 1)
    double delta;      // відносне відхилення delta > 0
    double target_err; // цільова гранична ймовірність помилки (0 < err < 1)
} ChernoffParams;

// Обчислення точної верхньої межі MGF: Pr[X >= (1 + delta) * mu]
static inline double chernoff_upper_bound_exact(double mu, double delta) {
    if (mu <= 0.0 || delta <= 0.0) return 1.0;
    // Обчислення через логарифмічний простір для захисту від чисельного underflow
    double log_b = mu * (delta - (1.0 + delta) * log(1.0 + delta));
    double bound = exp(log_b);
    return (bound > 1.0) ? 1.0 : bound;
}

// Обчислення квадратичної аппроксимації верхнього хвоста: exp(-mu * delta^2 / 3)
static inline double chernoff_upper_bound_approx(double mu, double delta) {
    if (mu <= 0.0 || delta <= 0.0) return 1.0;
    double bound = exp(-mu * delta * delta / 3.0);
    return (bound > 1.0) ? 1.0 : bound;
}

// Обчислення квадратичної аппроксимації нижнього хвоста: exp(-mu * delta^2 / 2)
static inline double chernoff_lower_bound_approx(double mu, double delta) {
    if (mu <= 0.0 || delta <= 0.0 || delta >= 1.0) return 1.0;
    double bound = exp(-mu * delta * delta / 2.0);
    return (bound > 1.0) ? 1.0 : bound;
}

// Обчислення двосторонньої межі: 2 * exp(-mu * delta^2 / 3)
static inline double chernoff_twosided_bound(double mu, double delta) {
    if (mu <= 0.0 || delta <= 0.0 || delta >= 1.0) return 1.0;
    double bound = 2.0 * exp(-mu * delta * delta / 3.0);
    return (bound > 1.0) ? 1.0 : bound;
}

// Обчислення необхідної кількості випробувань k для більшості голосів (Majority Voting)
static inline int chernoff_required_trials(double gamma, double target_error) {
    if (gamma <= 0.0 || target_error <= 0.0 || target_error >= 1.0) return -1;
    double k = (3.0 / (2.0 * gamma * gamma)) * log(1.0 / target_error);
    return (int)ceil(k);
}

#endif // CHERNOFF_BOUNDS_H
