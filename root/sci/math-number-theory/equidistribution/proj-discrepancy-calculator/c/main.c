#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Компаратор для порівняння чисел плаваючої крапки у qsort */
static int compare_doubles(const void *a, const void *b) {
    double da = *(const double *)a;
    double db = *(const double *)b;
    if (da < db) return -1;
    if (da > db) return 1;
    return 0;
}

/* Точне обчислення зіркової дискрепантності D*N за O(N log N) */
double compute_star_discrepancy(const double *pts, size_t n) {
    if (n == 0) return 0.0;
    
    /* Виділення пам'яті під копію для сортування */
    double *sorted = (double *)malloc(n * sizeof(double));
    if (!sorted) return -1.0;
    
    /* Заганяємо значення у напівінтервал [0, 1) */
    for (size_t i = 0; i < n; i++) {
        double val = fmod(pts[i], 1.0);
        if (val < 0.0) val += 1.0;
        sorted[i] = val;
    }
    
    /* Сортування точок за зростанням O(N log N) */
    qsort(sorted, n, sizeof(double), compare_doubles);
    
    double max_diff = 0.0;
    double inv_n = 1.0 / (double)n;
    
    /* Обчислення максимальної вертикальної відстані */
    for (size_t i = 0; i < n; i++) {
        double current_i = (double)(i + 1) * inv_n;
        double previous_i = (double)i * inv_n;
        
        double diff1 = fabs(current_i - sorted[i]);
        double diff2 = fabs(previous_i - sorted[i]);
        
        if (diff1 > max_diff) max_diff = diff1;
        if (diff2 > max_diff) max_diff = diff2;
    }
    
    free(sorted);
    return max_diff;
}

/* Модуль нормованої тригонометричної суми Вейля (1/N) * |sum e^(2pi i h x_n)| */
double compute_weyl_sum(const double *pts, size_t n, int h) {
    if (n == 0) return 0.0;
    
    double re_sum = 0.0;
    double im_sum = 0.0;
    
    for (size_t i = 0; i < n; i++) {
        double angle = 2.0 * M_PI * (double)h * pts[i];
        re_sum += cos(angle);
        im_sum += sin(angle);
    }
    
    double mod = sqrt(re_sum * re_sum + im_sum * im_sum);
    return mod / (double)n;
}

/* Функція радикальної інверсії для послідовності Ван дер Корпута */
double van_der_corput(size_t n, size_t base) {
    double q = 0.0;
    double bk = 1.0 / (double)base;
    while (n > 0) {
        q += (double)(n % base) * bk;
        n /= base;
        bk /= (double)base;
    }
    return q;
}

int main(void) {
    size_t N = 1000;
    double phi = (sqrt(5.0) - 1.0) / 2.0; /* Золотий перетин */
    
    double *golden_seq = (double *)malloc(N * sizeof(double));
    double *vdc_seq = (double *)malloc(N * sizeof(double));
    
    for (size_t i = 0; i < N; i++) {
        golden_seq[i] = fmod((i + 1) * phi, 1.0);
        vdc_seq[i] = van_der_corput(i + 1, 2);
    }
    
    double d_golden = compute_star_discrepancy(golden_seq, N);
    double d_vdc = compute_star_discrepancy(vdc_seq, N);
    double w_golden = compute_weyl_sum(golden_seq, N, 1);
    
    printf("Дискрепантність {n*phi} (N=%zu): %.6f\n", N, d_golden);
    printf("Дискрепантність Ван дер Корпута (N=%zu): %.6f\n", N, d_vdc);
    printf("Сума Вейля |S_N(1)|/N для {n*phi}: %.6f\n", w_golden);
    
    free(golden_seq);
    free(vdc_seq);
    return 0;
}
