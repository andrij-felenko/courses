#include <stdio.h>
#include <math.h>
#include <stdint.h>

typedef struct {
    int32_t num;
    int32_t den;
} Fraction;

/* Пошук найкращого раціонального наближення target_val із знаменником <= max_den */
Fraction farey_approximate(double target_val, int32_t max_den) {
    Fraction left = {0, 1};
    Fraction right = {1, 1};

    while (1) {
        int32_t med_num = left.num + right.num;
        int32_t med_den = left.den + right.den;

        /* Перевищено допустимий знаменник — зупиняємо пошук */
        if (med_den > max_den) {
            break;
        }

        double med_val = (double)med_num / med_den;

        /* Перевірка на точне влучання з урахуванням машинної точності */
        if (fabs(target_val - med_val) < 1e-15) {
            return (Fraction){med_num, med_den};
        }

        if (target_val > med_val) {
            left.num = med_num;
            left.den = med_den;
        } else {
            right.num = med_num;
            right.den = med_den;
        }
    }

    /* Обираємо межу із найменшою абсолютною похибкою */
    double err_left = fabs(target_val - (double)left.num / left.den);
    double err_right = fabs(target_val - (double)right.num / right.den);

    return (err_left <= err_right) ? left : right;
}
