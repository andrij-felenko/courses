#include <stddef.h>

/* Олімпійське середнє N=5, k=1 без циклів і розгалужень */
static inline double trimmed_mean_5_k1(double a, double b, double c, double d, double e) {
    /* Сума всіх елементів */
    double total_sum = a + b + c + d + e;

    /* Пошук мінімуму за 4 порівняння */
    double min1 = (a < b) ? a : b;
    double min2 = (c < d) ? c : d;
    double min12 = (min1 < min2) ? min1 : min2;
    double global_min = (min12 < e) ? min12 : e;

    /* Пошук максимуму за 4 порівняння */
    double max1 = (a > b) ? a : b;
    double max2 = (c > d) ? c : d;
    double max12 = (max1 > max2) ? max1 : max2;
    double global_max = (max12 > e) ? max12 : e;

    /* Віднімаємо два екстремуми й ділимо на 3 */
    return (total_sum - global_min - global_max) / 3.0;
}
