#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

/* Потоковий статистичний акумулятор 1-4 моментів */
typedef struct {
    uint64_t count;      /* Кількість спостережень (n) */
    double mean;         /* Поточне вибіркове середнє (M1) */
    double M2;           /* Сума квадратів відхилень: ∑(x - μ)² */
    double M3;           /* Сума кубів відхилень: ∑(x - μ)³ */
    double M4;           /* Сума четвертих степенів: ∑(x - μ)⁴ */
    double min_val;      /* Мінімальне значення у вибірці */
    double max_val;      /* Максимальне значення у вибірці */
} welford_acc_t;

/* Ініціалізація або скидання акумулятора */
void welford_init(welford_acc_t *acc) {
    if (!acc) return;
    acc->count = 0;
    acc->mean = 0.0;
    acc->M2 = 0.0;
    acc->M3 = 0.0;
    acc->M4 = 0.0;
    acc->min_val = INFINITY;
    acc->max_val = -INFINITY;
}

/* Додавання одного спостереження за алгоритмом Велфорда-Пебея */
void welford_push(welford_acc_t *acc, double x) {
    if (!acc || isnan(x)) return;

    acc->count++;
    uint64_t n = acc->count;

    if (x < acc->min_val) acc->min_val = x;
    if (x > acc->max_val) acc->max_val = x;

    if (n == 1) {
        acc->mean = x;
        acc->M2 = 0.0;
        acc->M3 = 0.0;
        acc->M4 = 0.0;
        return;
    }

    double delta = x - acc->mean;
    double delta_n = delta / (double)n;
    double delta_n2 = delta_n * delta_n;
    double term1 = delta * delta_n * (double)(n - 1);

    /* Оновлення середнього */
    acc->mean += delta_n;

    /* Оновлення вищих моментів (від старших до молодших) */
    acc->M4 += term1 * delta_n2 * (double)(n * n - 3 * n + 3) +
               6.0 * delta_n2 * acc->M2 - 4.0 * delta_n * acc->M3;
    acc->M3 += term1 * delta_n * (double)(n - 2) - 3.0 * delta_n * acc->M2;
    acc->M2 += term1;

    /* Захист від машинного нуля нижче порогу точності */
    if (acc->M2 < 0.0) acc->M2 = 0.0;
    if (acc->M4 < 0.0) acc->M4 = 0.0;
}

/* Пакетне додавання масиву значень */
void welford_push_batch(welford_acc_t *acc, const double *data, size_t length) {
    if (!acc || !data) return;
    for (size_t i = 0; i < length; ++i) {
        welford_push(acc, data[i]);
    }
}

/* Паралельне об'єднання двох акумуляторів (формули Чена-Пебея) */
void welford_merge(welford_acc_t *dst, const welford_acc_t *src) {
    if (!dst || !src || src->count == 0) return;
    if (dst->count == 0) {
        *dst = *src;
        return;
    }

    uint64_t n_a = dst->count;
    uint64_t n_b = src->count;
    uint64_t n_ab = n_a + n_b;
    double delta = src->mean - dst->mean;
    double delta2 = delta * delta;
    double delta3 = delta2 * delta;
    double delta4 = delta3 * delta;

    double n_a_f = (double)n_a;
    double n_b_f = (double)n_b;
    double n_ab_f = (double)n_ab;

    /* Нове об'єднане середнє */
    dst->mean += delta * (n_b_f / n_ab_f);

    /* Нові об'єднані моменти */
    double new_m4 = dst->M4 + src->M4 +
                    delta4 * (n_a_f * n_b_f * (n_a_f * n_a_f - n_a_f * n_b_f + n_b_f * n_b_f)) / (n_ab_f * n_ab_f * n_ab_f) +
                    6.0 * delta2 * (n_a_f * n_a_f * src->M2 + n_b_f * n_b_f * dst->M2) / (n_ab_f * n_ab_f) +
                    4.0 * delta * (n_a_f * src->M3 - n_b_f * dst->M3) / n_ab_f;

    double new_m3 = dst->M3 + src->M3 +
                    delta3 * (n_a_f * n_b_f * (n_a_f - n_b_f)) / (n_ab_f * n_ab_f) +
                    3.0 * delta * (n_a_f * src->M2 - n_b_f * dst->M2) / n_ab_f;

    double new_m2 = dst->M2 + src->M2 +
                    delta2 * (n_a_f * n_b_f / n_ab_f);

    dst->M4 = fmax(0.0, new_m4);
    dst->M3 = new_m3;
    dst->M2 = fmax(0.0, new_m2);
    dst->count = n_ab;

    if (src->min_val < dst->min_val) dst->min_val = src->min_val;
    if (src->max_val > dst->max_val) dst->max_val = src->max_val;
}

/* Отримання вибіркової дисперсії (s², незміщена оцінка з k-1) */
double welford_sample_variance(const welford_acc_t *acc) {
    if (!acc || acc->count < 2) return 0.0;
    return acc->M2 / (double)(acc->count - 1);
}

/* Отримання генеральної дисперсії (σ², ділення на k) */
double welford_population_variance(const welford_acc_t *acc) {
    if (!acc || acc->count == 0) return 0.0;
    return acc->M2 / (double)acc->count;
}

/* Отримання середньоквадратичного відхилення (s) */
double welford_stddev(const welford_acc_t *acc) {
    return sqrt(welford_sample_variance(acc));
}

/* Отримання коефіцієнта асиметрії (g1) */
double welford_skewness(const welford_acc_t *acc) {
    if (!acc || acc->count < 3 || acc->M2 <= 1e-15) return 0.0;
    double n = (double)acc->count;
    double var = acc->M2 / n;
    return (acc->M3 / n) / pow(var, 1.5);
}

/* Отримання коефіцієнта ексцесу (g2, excess kurtosis, для норми = 0) */
double welford_kurtosis(const welford_acc_t *acc) {
    if (!acc || acc->count < 4 || acc->M2 <= 1e-15) return 0.0;
    double n = (double)acc->count;
    double var = acc->M2 / n;
    return (acc->M4 / n) / (var * var) - 3.0;
}
