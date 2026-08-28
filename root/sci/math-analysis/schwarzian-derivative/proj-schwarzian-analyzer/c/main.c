#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Обчислення похідної Шварца за точними аналітичними похідними */
double schwarzian_exact(double df1, double df2, double df3) {
    if (fabs(df1) < 1e-12) {
        return -1e15; /* Прямує до мінус нескінченності в критичній точці */
    }
    double term1 = df3 / df1;
    double ratio = df2 / df1;
    double term2 = 1.5 * ratio * ratio;
    return term1 - term2;
}

/* Чисельне обчислення похідної Шварца через центральні різниці 4-го порядку */
double schwarzian_numeric(double (*f)(double), double x, double h) {
    double f_p2 = f(x + 2.0 * h);
    double f_p1 = f(x + h);
    double f_m1 = f(x - h);
    double f_m2 = f(x - 2.0 * h);

    /* Скінченно-різницеві оцінки похідних 4-го порядку */
    double df1 = (f_m2 - 8.0 * f_m1 + 8.0 * f_p1 - f_p2) / (12.0 * h);
    double df2 = (-f_m2 + 16.0 * f_m1 - 30.0 * f(x) + 16.0 * f_p1 - f_p2) / (12.0 * h * h);
    double df3 = (-f_p2 + 2.0 * f_p1 - 2.0 * f_m1 + f_m2) / (2.0 * h * h * h);

    return schwarzian_exact(df1, df2, df3);
}

/* Тестове логістичне відображення f(x) = r * x * (1 - x) */
static double g_r = 3.83;

static double logistic_map(double x) {
    return g_r * x * (1.0 - x);
}

int main(void) {
    g_r = 3.83; /* Параметр у зоні 3-циклу */
    double x_step = 0.05;

    printf("=== Аналіз похідної Шварца для логістичного відображення (r = %.2f) ===\n", g_r);
    printf("  x     df1       df2       S(f) exact    S(f) numeric\n");
    printf("----------------------------------------------------------\n");

    for (double x = 0.1; x <= 0.9; x += x_step) {
        if (fabs(x - 0.5) < 1e-4) continue; /* Пропускаємо критичну точку */

        double df1 = g_r * (1.0 - 2.0 * x);
        double df2 = -2.0 * g_r;
        double df3 = 0.0;

        double S_exact = schwarzian_exact(df1, df2, df3);
        double S_num = schwarzian_numeric(logistic_map, x, 1e-4);

        printf("%4.2f  %8.4f  %8.4f  %12.4f  %12.4f\n", x, df1, df2, S_exact, S_num);
    }

    return 0;
}
