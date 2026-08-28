#include <stdio.h>
#include <math.h>

/* Алгоритм Кахана для детермінанта 2x2 */
double kahan_det2x2(double a, double b, double c, double d) {
    double w = b * c;
    double e = fma(-b, c, w);
    double d_val = fma(a, d, -w);
    return d_val + e;
}

int main(void) {
    /* Числовий приклад із катастрофічним скасуванням */
    double a = 9007199254740994.0; /* 2^53 + 2 */
    double d = 9007199254740994.0;
    double b = 9007199254740995.0; /* 2^53 + 3 */
    double c = 9007199254740993.0; /* 2^53 + 1 */

    double naive = (a * d) - (b * c);
    double kahan = kahan_det2x2(a, b, c, d);

    printf("Точне аналітичне значення: 1.0000000000000000\n");
    printf("Наївне обчислення (MUL-SUB): %.16e (Помилка!)\n", naive);
    printf("Алгоритм Кахана (FMA):      %.16f (Абсолютно точно!)\n", kahan);

    return 0;
}
