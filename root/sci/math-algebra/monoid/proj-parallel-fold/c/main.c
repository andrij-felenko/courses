#include <stdio.h>
#include <stdlib.h>
#include <float.h>
#include <math.h>

/* Структура моноїда статистичних метрик */
typedef struct {
    long long count;
    double sum;
    double min_val;
    double max_val;
    double m2; /* сума квадратів відхилень для дисперсії */
} Metrics;

/* Нейтральний елемент моноїда e */
Metrics metrics_empty(void) {
    Metrics m;
    m.count = 0;
    m.sum = 0.0;
    m.min_val = DBL_MAX;
    m.max_val = -DBL_MAX;
    m.m2 = 0.0;
    return m;
}

/* Ініціалізація акумулятора з одного числового вимірювання */
Metrics metrics_from_value(double x) {
    Metrics m;
    m.count = 1;
    m.sum = x;
    m.min_val = x;
    m.max_val = x;
    m.m2 = 0.0;
    return m;
}

/* Асоціативна бінарна операція моноїда: combine(a, b) */
Metrics metrics_combine(Metrics a, Metrics b) {
    if (a.count == 0) return b;
    if (b.count == 0) return a;

    Metrics res;
    res.count = a.count + b.count;
    res.sum = a.sum + b.sum;
    res.min_val = (a.min_val < b.min_val) ? a.min_val : b.min_val;
    res.max_val = (a.max_val > b.max_val) ? a.max_val : b.max_val;

    double mean_a = a.sum / (double)a.count;
    double mean_b = b.sum / (double)b.count;
    double delta = mean_b - mean_a;

    double term = delta * delta * ((double)a.count * (double)b.count / (double)res.count);
    res.m2 = a.m2 + b.m2 + term;

    return res;
}

/* Рекурсивне бінарне дерево редукції (Divide and Conquer) */
Metrics reduce_range(const double* data, size_t left, size_t right) {
    if (left >= right) {
        return metrics_empty();
    }
    if (right - left == 1) {
        return metrics_from_value(data[left]);
    }
    size_t mid = left + (right - left) / 2;
    Metrics left_res = reduce_range(data, left, mid);
    Metrics right_res = reduce_range(data, mid, right);
    return metrics_combine(left_res, right_res);
}
