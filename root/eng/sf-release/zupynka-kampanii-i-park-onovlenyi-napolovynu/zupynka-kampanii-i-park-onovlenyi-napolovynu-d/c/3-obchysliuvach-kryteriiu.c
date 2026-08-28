#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    if (da < db) return -1;
    if (da > db) return 1;
    return 0;
}

/* Обчислення максимальної відстані D Колмогорова-Смирнова */
bool calculate_kolmogorov_smirnov(const double *sample1, size_t n1,
                                 const double *sample2, size_t n2,
                                 double *out_d_stat, bool *out_is_rejected,
                                 double alpha_critical) {
    if (!sample1 || !sample2 || n1 == 0 || n2 == 0 || !out_d_stat || !out_is_rejected) {
        return false;
    }

    double *s1 = (double *)malloc(n1 * sizeof(double));
    double *s2 = (double *)malloc(n2 * sizeof(double));
    if (!s1 || !s2) {
        free(s1);
        free(s2);
        return false;
    }

    memcpy(s1, sample1, n1 * sizeof(double));
    memcpy(s2, sample2, n2 * sizeof(double));

    qsort(s1, n1, sizeof(double), compare_doubles);
    qsort(s2, n2, sizeof(double), compare_doubles);

    size_t i = 0, j = 0;
    double d_max = 0.0;
    double fn1 = 0.0, fn2 = 0.0;

    while (i < n1 && j < n2) {
        double val1 = s1[i];
        double val2 = s2[j];

        if (val1 <= val2) {
            i++;
            fn1 = (double)i / (double)n1;
        }
        if (val2 <= val1) {
            j++;
            fn2 = (double)j / (double)n2;
        }

        double diff = fabs(fn1 - fn2);
        if (diff > d_max) {
            d_max = diff;
        }
    }

    *out_d_stat = d_max;

    /* Критичне значення для alpha = 0.01: c(alpha) = 1.63 */
    double c_alpha = (alpha_critical > 0.0) ? alpha_critical : 1.63;
    double threshold = c_alpha * sqrt(((double)(n1 + n2)) / ((double)(n1 * n2)));

    *out_is_rejected = (d_max > threshold);

    free(s1);
    free(s2);
    return true;
}
